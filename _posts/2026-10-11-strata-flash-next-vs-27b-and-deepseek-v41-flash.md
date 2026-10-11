---
layout: post
title: "What Strata Changes: Qwen3.8-Flash-Next Against a Dense 27B, and the Gap Left to DeepSeek V4.1 Flash"
date: 2026-10-11 00:00:00 +0800
categories: [tech]
tags: [strata, llm-inference, qwen, deepseek, quantization, benchmark, local-llm, moe]
description: "A 6B-active MoE running on one 32GB card, measured against a dense 27B and against DeepSeek V4.1 Flash: where the architecture already closes the gap, where it still loses fifteen points on agentic coding, and why the local machine is faster than the cloud API for the same weights."
---

There is a quiet assumption in most model comparisons: that a smaller number of active parameters means a smaller model. Qwen3.8-Flash-Next is the first open-weight release that breaks that assumption cleanly — 125B parameters with **6B activated per token**, plus 51B of n-gram embedding and 4B of MTP, and it scores *above* a dense 27B on almost every published evaluation. The catch is that those numbers were measured on full BF16 weights in a datacenter. On my machine, the same architecture runs as an IQ2_XS quantization through **Strata**, a runtime that keeps the expert cache resident instead of streaming it over PCIe.

This post is the comparison I actually care about: what the quantized local model can and cannot do against the dense 27B, and how much of DeepSeek V4.1 Flash is still missing.

## 1. Flash-Next against the dense 27B: the gap opens where the task gets long

![Flash-Next against Qwen3.8-27B on eleven shared benchmarks, with the per-row delta](/assets/images/fig-strata-flash-next-vs-27b.svg)

Read the delta column as two different stories.

**On single-shot intelligence the two are almost the same model.** GPQA Diamond 91.7 vs 89.2, LiveCodeBench v6 91.9 vs 90.3, IFBench 81.3 vs 79.5, SWE-bench Pro 62.5 vs 61.7. Those are differences of two or three points — inside the noise of a re-run with a different harness. A 6B-active model matching a dense 27B on competitive coding is the headline result of the architecture.

**On long-horizon agentic work the gap is real.** JobBench 55.7 vs 33.4 (+66.8% relative), DeepSWE 1.1 58.7 vs 42.2 (+39.1%), HLE 35.9 vs 30.8, NL2Repo 48.1 vs 42.3. The pattern is consistent: the tasks that require the model to *hold a plan across many turns* are where the extra parameters — and the n-gram embedding, and the sparse attention — earn their keep. A dense 27B has nowhere to put those parameters; Flash-Next has 51B of them sitting in an embedding table that costs memory, not compute.

The honest caveat: these are full-weight scores. What runs on my machine is IQ2_XS, which Strata's own model guide labels "better, slightly below full" — the project does not publish per-quantization benchmark deltas, so I treat the local model as *near* these numbers, not equal to them. Only IQ3_S is claimed to match the published tests, and it needs 54.8GB, which is not a 32GB card.

## 2. How much of DeepSeek V4.1 Flash is still missing

![Relative gap between Flash-Next and DeepSeek V4.1 Flash across the Artificial Analysis sub-evaluations](/assets/images/fig-strata-gap-to-v41flash.svg)

Measured under one methodology, the aggregate is a wash: Artificial Analysis Intelligence Index 40 vs 39. Flash-Next is nominally *ahead*. That number hides the shape of the difference.

**Table 1.** Where the remaining gap sits (Artificial Analysis, same harness, all three models).

| Evaluation | Flash-Next | V4.1 Flash | Gap |
|---|---|---|---|
| Intelligence Index | 40 | 39 | −1 (Flash-Next ahead) |
| AA-Briefcase v1.1 | 1581 | 1422 | −159 (Flash-Next ahead) |
| GDPval-AA v2.1 | 1629 | 1600 | −29 (Flash-Next ahead) |
| AutomationBench-AA | 56% | 69% | +13 pts |
| Terminal-Bench 4.0 | 25% | 27% | +2 pts |
| SciCode | 51% | 52% | +1 pt |
| Humanity's Last Exam | 38% | 39% | +1 pt |
| CritPt | 11% | 14% | +3 pts |
| AA-LCR v1.1 (long context) | 80% | 84% | +4 pts |

Six of nine go to V4.1 Flash, and the six include every agentic and long-context row in the set. DeepSeek's own table is harsher on the same axis, because it evaluates at maximum reasoning effort with a 1M-token window: **DeepSWE v1.1 74.2 vs 58.7** — fifteen points, the single largest remaining gap — Terminal-Bench 2.1 90.6, NL2Repo 64.0 vs 48.1, CyberGym 88.1.

So the answer to "how much is left" is not a single number. On knowledge work and reasoning, the gap is roughly two to ten percent, and Flash-Next wins some of it outright. On agentic software engineering, the gap is still fifteen points, and that is the work I actually use these models for.

## 3. Where the local machine beats the cloud

![Measured decode speed against prompt depth on one RTX 4080 SUPER, against the official IQ2_XS curve](/assets/images/fig-strata-local-decode.svg)

Artificial Analysis benchmarks the Flash-Next API at 52 tokens/s. My machine, running a 2-bit quantization of the same architecture, logs **109–212 tok/s** on its sustained runs (64 of 112 logged requests) — roughly 3x the cloud API for the same weights. The reason is not a faster GPU; the official curve was measured on a 12GB RTX 5070. The reason is the cache.

From the engine log, counting only sustained runs (256 or more generated tokens):

- decode averaged **150 tok/s** under 10K prompt tokens, 155 at 10–40K, and **153 at 40–128K** — while the official curve falls 34% between 1K and 262K;
- **99.5% of routed experts stayed resident** (6,494,373 lookups, 6,459,361 hits) — the PCIe path ran 1,688 times;
- prompt ingestion peaked at 3,179 tok/s on a cold 82K prompt, so prefill is not the bottleneck once the prefix is cached;
- MTP draft acceptance climbed with depth: 72% under 1K prompt tokens, 81% above 40K, 79% overall.

That last line is the interesting one. A big expert cache does not just make the model faster; it makes the speculative decoder more accurate on deep context, which is exactly where a small quantized model normally degrades.

![The quantization ladder: footprint, quality label, and decode speed per size](/assets/images/fig-strata-quant-ladder.svg)

## 4. What the three are actually for

**Table 2.** Cost and shape, as published.

| | Flash-Next (local, IQ2_XS) | Qwen3.8-27B | DeepSeek V4.1 Flash |
|---|---|---|---|
| Params / active | 125B (+51B n-gram) / 6B | 27B / 27B | 552B / 8B prefill, 16B decode |
| Context | 262K native, 1M extensible | 256K | 1M |
| Blended price per 1M tokens | free (32GB card + electricity) | $0.47 | $0.1842 |
| Cost per Intelligence Index task | — | $1.01 | $0.27 |
| Prompt read time (engine log) | 0.55s on a 61-token prompt; 22.2s on a cold 68K prompt | 3.86s | 1.08s |
| Multimodal | yes (text, image, video) | yes | text + image |

The decision is not "which model is smarter". It is which axis you are paying on. V4.1 Flash wins the agentic axis and the 1M-token window. Flash-Next wins the knowledge-work axis and the price axis. The dense 27B wins nothing measurable except the fact that it fits in 32GB as a plain dense model with no runtime tricks — which is still a real advantage if you want a fallback that behaves predictably.

For my own setup the split is simple: **local for volume, cloud for the hard repository work.** Anything I run dozens of times a day goes to the local model, because a fifteen-point gap does not matter when the marginal cost of a call is zero. The calls where I need DeepSWE-level reliability — a repo I cannot reproduce, a bug that needs 200 tool calls — go to the cloud, where the fifteen points do matter.

## 5. The part I would not oversell

Three things this comparison cannot tell you:

1. **The quantization penalty is unmeasured.** Strata says IQ3_S matches the published tests and IQ2_XS is "slightly below". Nobody publishes IQ2_XS scores on DeepSWE. My local model is not the model in Table 1.
2. **Benchmark tables disagree by harness.** Flash-Next's DeepSWE score is 58.7 on the best of two harnesses; the same model scores differently under Claude Code than under mini-SWE-agent. Comparisons across vendors are approximate at best.
3. **Speed claims depend on the machine.** 109–212 tok/s is my log, on a card with an 18.5k-slot expert cache. On a 12GB card the same quantization runs at 79.6 tok/s. The architecture is the same; the cache is not.

The honest summary: Flash-Next has already closed most of the gap to a dense 27B and, on the aggregate index, most of the gap to DeepSeek V4.1 Flash. What remains is fifteen points of agentic engineering and four points of long-context recall — and those are precisely the capabilities that make the cloud worth paying for.
