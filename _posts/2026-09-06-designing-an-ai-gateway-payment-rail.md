---
layout: post
title: "An AI Gateway Is a Payment Rail: Routing, Metering, and Control, Key by Key"
date: 2026-09-06 00:00:00 +0800
categories: [tech]
tags: [ai-gateway, llm, architecture, routing, byok, metering, litellm, key-management]
description: "The design of an AI capability gateway for multiple business systems: five ways to supply model keys, two levels of routing decisions, a metering layer built like a bank ledger, a hard boundary drawn around the third-party engine — and the PoC measurements that caught a concurrency cliff before it ever shipped."
---

Every product team that ships LLM features ends up hand-writing the same five things: a place to store API keys, a retry policy, a rate limiter, a usage counter, and a monthly spreadsheet of what it all cost. Then the second team in the company writes them again, slightly worse. This is the era of model abundance — OpenAI, Anthropic, Gemini, DeepSeek, self-hosted vLLM — and yet each integration is still bolted onto one provider like a dependency, not an infrastructure layer.

The picture changes the moment you treat AI capabilities the way a bank treats payments. A call to a language model is a transaction: it has a *spender* (whose budget pays), an *amount* (tokens in, tokens out), a *counterparty* (which provider and which key), and a *receipt* (an audit row). Seen that way, the missing piece of infrastructure is an **AI gateway** — not an API proxy, but a payment rail: routing, metering, and control, key by key.

This essay is the design of exactly that system, which we've been working on under the codename *airoute*. It is a design document in essay form: the problem, the architecture, the one engineering decision that cost the most thought, and the measurements from a proof of concept that reshaped at least one assumption before a line of production code existed.

## 1. Whose money is this call?

The core of the gateway is a single question asked on every request: **whose key pays for this call?** Everything else — throughput, latency, provider translation — is a solved problem compared to this one, because the answer involves money, entitlements, and trust, and it must be decided in milliseconds.

Supply comes in five modes, and the gateway must host all five at once, because real organizations mix them:

- **BYOK** — the end user brings their own upstream key (think: an API reseller's customer, or an internal team with its own enterprise contract).
- **Platform-operated pool** — keys the gateway operator buys and meters internally.
- **Authorized bring-in** — a user contributes their key to the shared pool under a usage-and-revenue-share agreement, with per-key traceability and the right to be evicted for abuse.
- **Partner pool** — a partner's keys with an agreed flat token price; usage × price settles monthly, backed by audit rows.
- **Self-hosted** — local OpenAI-compatible endpoints (vLLM, LM Studio), which the gateway treats as just another provider.

Out in the business systems, none of this is visible. They hold only a **virtual key** (`sk-air-*`) minted by the gateway, scoped to a tenant, with its own expiry, rate limits, model allowlist, and budget. The real upstream keys are envelope-encrypted at rest, never appear in logs, and never leave the gateway process. A business system that switches from BYOK to the platform pool, or from OpenAI to a local model, changes nothing in its code — the routing layer absorbs it.

Routing itself is two decisions stacked. **First, the source decision:** whose money. A healthy BYOK key belonging to the calling user routes to the user's own key; otherwise the call falls through a configurable priority chain into the platform pools. The chain is policy, not code, so a tenant can reorder it without a deploy. **Second, the pool-internal pick:** given a pool, which concrete key carries this request? Each pool declares its own strategy:

**Table 1.** Pool-internal key selection algorithms.

| Algorithm | Idea | Best for |
|---|---|---|
| round-robin | take turns | pools of homogeneous keys |
| least-busy | fewest in-flight requests | self-hosted, capacity-sensitive |
| quota-aware | weight by remaining RPM/TPM | keys with unequal upstream limits |
| cost-first | cheapest unit price first | platform-operated pools, cost control |
| latency-based | weight by historical p50/p95 | latency-sensitive tenants |

Underneath sits a health system per key: consecutive 429/5xx counts put a key into cooldown, then automatic removal and — when it recovers — restoration. A failed call walks a ladder: retry on the next key, then down a model fallback chain, then an honest error, every rung marked in the ledger (`degraded: true`). One boundary is deliberate: a BYOK failure does *not* silently fall back to the platform pool, because that would be spending someone else's money without consent. It is opt-in policy, never a default.

The whole decision chain, compressed:

![The route of one call as six configurable gates: tier gate, cache lookup, source decision, key pick, quota gate, then call and meter — with three metered exits: cache hit, over quota, and upstream failure](/assets/images/fig-airoute-call-route.svg)

Every gate above reads live state — plans, routing rules, pool strategy, key health — so the path is pure policy. That is the design goal: **the request path stays boring and fast; all the interesting business rules live in data.**

## 2. The whole system in one picture

The architecture that carries this routing is deliberately conventional on the outside — FastAPI + asyncio, stateless gateway nodes, Redis and PostgreSQL underneath — and unusual on the inside in exactly one place, the engine boundary. Here is the system, drawn to show who owns what:

![The airoute gateway architecture: business systems call an OpenAI-compatible endpoint with virtual keys; inside the self-built scope, a data plane (ingress, router, dispatcher, metering) and a control plane (tenants, key pools, billing, policies, webhooks, reconciliation) sit beside the in-process litellm engine and shared Redis/PostgreSQL stores; upstream providers — OpenAI, Anthropic, Gemini, DeepSeek, local AI — all connect through the same path](/assets/images/fig-airoute-architecture.svg)

The picture encodes three structural decisions worth stating out loud.

**Control plane and data plane are separated.** The request path does five things — authenticate, decide, dispatch, translate, meter — and nothing else. Every business rule (who may use which tier, what overage does, how pools settle) lives in the control plane beside the request path, free to evolve without touching it. This is what lets the gateway serve several business systems with different plans and policies from one codebase.

**Stateless nodes, stateful stores.** Rate counters, semantic cache, and the metering queue live in Redis; metadata, the accounting ledger, and audit live in PostgreSQL. A gateway node holds nothing, so scaling is adding replicas — from a single docker-compose host to a small fleet, without a rewrite.

**The engine is a box with a hard border.** Litellm, the open-source translation engine, runs *in-process* — but it is a dependency with a contract, not a platform we extend. The next section is about that border, because it was the most expensive decision in the design.

## 3. Where the engine ends and we begin

The standard way to build an AI gateway is to fork a proxy — LiteLLM Proxy and its siblings ship with routing, budgets, and keys already inside. The standard instinct is therefore: take the proxy, tweak it, ship. We rejected that, and the reasoning is the heart of the design.

A proxy is a monolith with opinions. LiteLLM Proxy couples authentication, team management, budgeting, and routing into one codebase; the features this gateway needs — per-request BYOK routing, authorized key pooling with revenue share, subscription billing with overage policies — sit *outside* its model. Fitting them in means deep surgery on a codebase that rebases against upstream weekly. Every upgrade becomes a merge-conflict lottery; you eventually stop upgrading, and then you own a fork forever.

The opposite extreme is writing all provider adapters ourselves. That is a decade of accumulated work — 100+ provider protocol quirks, streaming semantics, retry behavior, cost tables. Rewriting it to save the trouble of integrating it is how engineers burn quarters.

The middle path, and our choice: **write the gateway ourselves and use litellm as an engine library, never as a proxy.** The gateway calls `acompletion` in-process and passes `api_key`, `api_base`, and `model` *per request*. That single capability — the gateway, not the proxy config, decides which key each request carries — is what makes BYOK routing and pool-level scheduling fully ours. Litellm keeps the job it is unmatched at: translating one request into 100+ provider dialects, streaming included.

**Table 2.** Keeping a fast-moving dependency from becoming a liability.

| Layer | Strategy |
|---|---|
| Dependency | version-locked (litellm==x.y.z); upgrades are PRs with contract tests |
| Isolation | all engine calls go through one `adapters/` layer; business code never imports litellm |
| Contract tests | full mock-provider suite — streaming, errors, rate limits, usage fields — run on every upgrade |
| Upstreaming | generic features PR'd back upstream, so the next upgrade delivers them for free |
| Fallback | if upstream refuses a critical feature: fork the *library* (small surface) or vendor it — never the proxy |
| Bypass | the full proxy still exists for internal lightweight use, deliberately outside commercial billing |

The boundary rule is worth stating in one sentence: **the engine never sees user identity or billing logic — only a chosen key and a request to translate.** Any capability litellm lacks for the money logic (routing decisions, metering, policies) is ours by construction, not by patch. And if a better engine ever appears, we change one layer, not the system.

## 4. Metering like a bank, not like a log file

If routing is the brain of the gateway, metering is its nervous system — and it has the same non-negotiable property as a bank ledger: it must be complete, attributable, and impossible to lose. Every call, cache hit included, produces one atomic row: tenant, user, virtual key, pool, upstream key, model, input tokens, output tokens, cost, latency, status, whether it was cached or degraded. The `request_id` makes the row idempotent — retries cannot double-count, which matters more than it sounds once you have a client that retries.

Two implementation details are worth copying. First, token counts come from the model's own `usage` response — the gateway never counts tokens itself — and streaming requests capture usage at the **stream tail**, so the response is never buffered for the sake of accounting. When an upstream omits usage, the gateway injects an estimate and marks the row `usage_source: estimated`, because an honest estimate beats a silent hole in the ledger. Second, the request path never blocks on storage: usage rows go to a Redis Stream and a worker batch-inserts them into PostgreSQL, partitioned monthly. The gateway trades a few seconds of accounting latency for zero added request latency — and billing systems do not need real-time, they need *complete*.

On top of the ledger sit the settlement modes: subscriptions for users (monthly token/request quotas, allowed tiers, an overage policy that can block, prompt an upgrade, or degrade to a cheaper tier), usage statements for BYOK users, monthly settlement sheets for partner pools, and revenue-share statements for authorized bring-in keys (share proceeds can offset the contributor's own subscription). Cache hits and shadow-mode calls bill at their own special rates. None of this touches the request path; it all reads the same ledger.

## 5. The levers that make pooled keys cheaper than single keys

A gateway justifies its existence twice over once it starts saving tokens, not just organizing them. Five value-adds are designed in from day one rather than bolted on later:

**Table 3.** Value-add layer, all policy-driven, all metered.

| Lever | What it does | Note |
|---|---|---|
| Semantic cache | non-streaming, cacheable calls hit a tenant-isolated cache | estimate: 70–90% token savings on repetitive workloads |
| Fallback chain | per-model alias: primary → alt1 → alt2 on 5xx/429/timeout | response marked `degraded`, optionally surfaced via header |
| Task-tiered routing | business declares task class via `X-Task-Type` or alias (`summary-fast` vs `summary-ultra`) | plan decides which tiers are reachable |
| Usage webhooks | signed, retried, idempotent callbacks at 80%/100% thresholds and anomalies | lets the business system gate its own paywall |
| Canary & shadow | weighted canary rollout of new models with one-command rollback; shadow mode compares responses without billing | shadow traffic logged under a separate cost code |

The cache is the sleeper hit. A homework-explanation service — the kind of repetitive, high-similarity workload a gateway operator's first tenant tends to run — can serve most of its traffic from a cache without the user noticing anything but the bill shrinking. V1 ships exact-match caching (request hash); semantic similarity (embeddings + threshold, cosine ≥ 0.95) comes in V2. Privacy rules are strict: BYOK calls and sensitive-marked tasks are never cached, tenants are isolated, TTLs are configurable, and any request can force a bypass. The design treats the cache as a billing product, not a performance trick: hits are metered at a cache price, and the ledger can show exactly what caching saved.

## 6. What the PoC proved — and the cliff it found

Before M1, we built a proof of concept: a real gateway process, a mock upstream that records which key each request arrived under, and a test suite. It cost a weekend and changed the risk list. Seven integration tests passed: per-request key injection genuinely routes BYOK traffic to the user's own key (verified at the mock); pool round-robin with 429 failover works and marks `degraded`; a BYOK failure does *not* leak into the public pool by default; streaming usage is captured at the stream tail; missing usage gets the estimated-injection treatment; auth, alias mapping, and idempotent metering hold up.

The performance runs were more interesting. Two numbers did not surprise us: a warm gateway handles a serial call in ~2.7 ms, and cold-start initialization costs 236–500 ms on the first few requests (litellm's client construction — hence a mandatory startup warm-up in V1). The third number surprised us a lot.

![Measured gateway throughput against concurrency: climbing to 2276 QPS at 100 connections, then a cliff past ~120 where uvicorn's h11 latency explodes — 417 QPS at 250 connections; a per-key semaphore capped at 100 holds a flat 2021 QPS instead](/assets/images/fig-airoute-concurrency-cliff.svg)

Naively, more concurrent connections should mean more throughput until the CPU gives out. Instead, uvicorn's h11 protocol server falls off a cliff around ~120+ concurrent connections: 100 connections delivered 2276 QPS, and 250 connections delivered 417 QPS — a fivefold collapse, not a plateau. Client-side connection-pool over-subscription made it pathological, with requests queueing inside the client library. This is exactly the failure mode a real gateway would hit first, because real business systems do not arrive one request at a time.

The fix was already in the design, but the measurement promoted it from nice-to-have to law: **a concurrency semaphore per upstream key.** Each key gets a queue with a cap; the gateway restrains itself before the upstream ever sees a 429. With the semaphore capped at 100, a 300-request burst ran at 2021 QPS with p50 latency of 44 ms — flat, predictable, no cliff. The lesson generalizes: for a component that fronts other people's rate limits, self-restraint is not a performance detail, it is the correctness model.

The PoC also caught three traps worth recording. Litellm's underlying OpenAI client retries by itself (`max_retries=2`), which stacked on our retry layer and tripled the pressure on a failing key — retry policy must be converged in one place. Litellm tries to fetch model cost tables from the network at import time, which stalls startup for 30+ seconds on restricted networks — a local cost map flag fixes it. And litellm constructs a fresh `AsyncOpenAI` client per request, so connection reuse must be explicitly engineered. These four items — connection reuse, startup warm-up, retry convergence, per-key semaphores — are the M1 checklist.

## 7. From design to production

The roadmap runs in three stages. **M1** ships the spine: the OpenAI-compatible endpoint, virtual keys, self-operated pool plus BYOK routing, the atomic metering ledger, basic subscription quotas, and the management API — enough for a first business system to run real traffic on and see every call in its statements. **M2** adds the value layer: semantic cache, fallback chains, task-tiered routing, usage webhooks, local vLLM, and the admin UI. **M3** turns it commercial: authorized bring-in pooling, partner settlement, reconciliation reports, canary and shadow mode, and a high-availability deployment. The PoC has already retired the biggest architectural risk; what remains is mostly scope and discipline.

**Table 4.** Milestones.

| Stage | Content | Acceptance |
|---|---|---|
| M0 · Design | this document | done |
| M1 · MVP | endpoint · virtual keys · self-operated + BYOK routing · ledger · quota basics · mgmt API | a real business system on real traffic, usage queryable |
| M2 · Value | semantic cache · fallback · task tiers · webhooks · local vLLM · admin UI | cost reports usable |
| M3 · Commercial | authorized pooling · partner settlement · reconciliation · canary/shadow · HA | closed loop, externally operable |

None of this is exotic. The gateway's components are a stateless API service, two stores, and a borrowed translation engine. What the design process kept revealing is that the hard problems are all **boundary problems**: whose money is this call, which logic may live in the third-party engine, where caching is allowed, what may never be metered silently. Those boundaries are what make a pile of keys into a payment rail — and they are exactly the part no proxy vendor will ever sell you, because they are your business model, not theirs.
