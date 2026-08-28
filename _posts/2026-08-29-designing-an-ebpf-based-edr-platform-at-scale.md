---
layout: post
title: "Designing an eBPF-Based EDR Platform at Scale"
date: 2026-08-29 00:00:00 +0800
categories: [tech]
tags: [ebpf, security, edr, kubernetes, rust, kafka, architecture]
description: "A reference architecture for large-scale host security: in-kernel filtering with libbpf, a Rust agent as the single enforcement point, versioned policy distribution, and a Kafka/Flink data plane built for 100k-node fleets."
---

Endpoint detection and response (EDR) has a fundamental tension. To catch an attacker you need visibility into *everything* — every process spawn, file touch, and socket connect on the machine — but shipping everything to a central platform at fleet scale is a data-delivery problem that quietly eats your budget and your latency. The design space for solving it has narrowed considerably in the last few years: eBPF is now the standard way to get kernel-level visibility without kernel modules or userland instrumentation, and the interesting engineering questions have moved from "can we see it" to "how do we filter it in-kernel, enforce on it locally, and keep the pipeline honest at 100k nodes".

This article walks through a reference architecture for exactly that: an eBPF-based EDR platform targeting super-large-scale host security — bare-metal hosts and Kubernetes nodes alike — where every layer is built in-house around open-source components (libbpf, Kafka, Elasticsearch, Flink). The goal is not to re-explain what eBPF is; it is to lay out the hard design decisions: where enforcement actually happens, how policy gets from a central server into kernel maps atomically, and why the data plane — not the collector — is usually where these systems die.

## Why eBPF for host security

The traditional options each fail in a specific way at scale:

- **Kernel modules** give full power but require per-kernel-version maintenance, can panic the host on a bug, and are slow to ship.
- **Userland agents** (ptrace-based or syscall-intercepting) are gameable by the very attackers they target, add measurable overhead, and miss events that happen before/after their hooks.
- **Static LSM frameworks** (AppArmor, SELinux) enforce well but express poorly: fleet-wide policy management for thousands of workloads with dynamic behavior is a constant fight against label sprawl.

eBPF removes the main objections to each. The verifier sandboxes programs so a bug cannot panic the kernel; CO-RE (Compile Once, Run Everywhere) plus BTF means one binary runs across a wide kernel matrix without per-kernel rebuilds; and since 5.7, `bpf_lsm` hooks let eBPF programs *enforce*, not just observe — returning an error code from a security hook is enough to deny the operation in-kernel.

This design sits deliberately on top of prior art rather than beside it. Falco (CNCF graduated) established detection-first runtime security with a rich rule DSL; Tetragon demonstrated aggressive in-kernel filtering plus real-time blocking at very low overhead; Tracee pushed deep tracing for forensic completeness; KubeArmor proved LSM-based policy enforcement is operationally viable. The reference architecture here combines those threads — detection, in-kernel enforcement, and forensics-grade event fidelity — with a control plane and data plane explicitly engineered for 10k–100k node fleets, which most of the single-cluster tools are not.

The one-line motivation: **image scanning tells you a vulnerability exists; eBPF runtime security tells you it is being exploited right now.** Everything below serves that promise at scale.

## Architecture overview

<figure class="figure">
<img src="/assets/images/fig-ebpf-edr-architecture.svg" alt="Reference architecture for an eBPF-based EDR platform: BPF programs and Rust agent on each node, policy server over gRPC, Kafka feeding Elasticsearch and Flink" loading="lazy">
<figcaption class="figcaption"><b>Fig. 1 | Reference architecture.</b> Each host/K8s node runs C+libbpf BPF programs (collection + in-kernel enforcement) and a Rust EDR agent that normalizes events, compiles policy into BPF maps, and produces to Kafka. The policy server distributes compiled rules over gRPC; downstream, Elasticsearch serves the traceability platform and Flink feeds the alert center.</figcaption>
</figure>

The system has three planes:

1. **Kernel plane (per node):** C + libbpf programs hooking process lifecycle (`execve`/`fork`/`exit`), file operations (`openat`/`rename`/`unlink`), and network connects (`connect4`/`connect6`). They capture cgroup/netns context, apply in-kernel policy filters, and emit surviving events into a ring buffer. The same map set also carries enforcement state (block lists) for `bpf_lsm` hooks.
2. **Agent plane (per node):** a Rust daemon that loads the BPF objects, normalizes raw kernel events into typed records, enriches them with container metadata, compiles policy from the server into BPF maps, produces to Kafka, and reports health/metrics.
3. **Control + data plane (central):** a policy server that owns rule authoring, compilation, versioned distribution, and fleet consistency auditing; Kafka as the event backbone (`edr.events.process`, `edr.events.file`, `edr.events.network`, `edr.events.policy`, `edr.events.agent`); Elasticsearch for traceability; Flink for real-time behavior-chain correlation into an alert center.

One structural decision deserves emphasis because it is easy to get wrong: **the policy server never writes BPF maps directly.** A BPF map is a kernel object owned by the node's userspace loader — only the local agent can update it, via libbpf. So the real path is `policy server →(gRPC)→ Rust agent →(libbpf map update)→ BPF maps`. This looks like an extra hop but is actually a feature: the agent becomes the single enforcement point where policy can be validated locally, applied atomically, versioned per node, and kept effective even when the network to the control plane is down.

## The kernel layer: hooks and the enforcement problem

### Hook selection

The hook set follows what an EDR must answer: *what ran, what did it touch, where did it talk to?*

| Concern | Hooks | Notes |
|---|---|---|
| Process lifecycle | `execve`, `fork`/`clone`, `exit` | Reconstructs the process tree; `exit` events are as important as `execve` for attribution windows |
| File activity | `openat`, `rename`, `unlink` | Covers read/write intent plus destructive ops (ransomware renames, log deletion) |
| Network egress | `connect4`, `connect6` | C2 beaconing detection; capture remote addr/port + netns id |
| Context | cgroup id at fork time, netns id per socket | The stable keys for container attribution — see agent layer |

Two implementation notes matter in practice. First, prefer tracepoints/fentry over raw kprobes where the kernel offers them: they are ABI-stable across versions, which is what keeps a 100k-node fleet from fragmenting into per-kernel builds. Second, capture context *at fork time*, not lazily: reading the current task's cgroup id when `execve` fires is cheap and race-free; trying to attribute a process after it has already exec'd is where attribution bugs live.

### Audit vs. enforce — the real fork in the road

Observation and enforcement are different kernel problems, and conflating them is the most common design mistake.

**Audit (observe)** needs only tracepoints/kprobes: low overhead, stable across versions, no special config. **Enforce (block/kill)** requires `bpf_lsm` programs attached to security hooks — `bprm_check_security` for execve blocking, `socket_connect` for network blocking, `path_*` hooks for file operations. The catch is the deployment matrix: you need kernel ≥ 5.7 with `CONFIG_BPF_LSM=y`, and on many distributions you must additionally add `lsm=...,bpf` to the boot command line — a change that requires a reboot and touches every node in the fleet. A heterogeneous production environment will always contain nodes where enforcement is unavailable, so the agent must detect this at startup (`/sys/kernel/security/lsm`) and **degrade gracefully to audit-only mode** rather than fail.

The second subtlety is process killing. If your policy says "kill any process running X", a userspace SIGKILL from the Rust agent has an inherent race: by the time the event traverses ring buffer → agent → `kill(2)`, the process may have finished its damage. The in-kernel alternative — `bpf_send_signal(SIGKILL)` (5.3+) fired from the hook itself — kills on the next matching event with no userspace round trip, but only for processes that keep hitting your hooks. A robust design uses both: **LSM blocking as primary** (deny the operation before it happens) and **userspace kill as fallback** for long-running malicious processes already in memory.

### In-kernel filtering is non-negotiable at scale

On a busy node, `openat` and `connect` fire tens of thousands of times per second. Shipping them all to userspace first means the ring buffer overflows before Kafka ever becomes the bottleneck. The fix is to push policy *into* the kernel: the agent compiles allowlists/denylists into BPF hash maps, and each hook checks the map **before** emitting an event.

```c
// Allowlist compiled into a BPF hash map; checked in-kernel before emit.
static __always_inline void maybe_emit_file_event(struct file *f)
{
    u64 path_hash = 0;
    // ...hash dentry path (bounded, verifier-friendly)...
    if (bpf_map_lookup_elem(&allow_open, &path_hash))
        return;                       // known-benign: drop in kernel
    struct file_event ev = { /* pid, cgroup id, path hash, flags */ };
    bpf_ringbuf_output(&events, &ev, sizeof(ev), 0);
}
```

This is the single biggest lever on both overhead and data volume — it is also why Tetragon-style designs report near-zero cost in production. Two refinements complete the picture:

- **Per-cgroup rate limiting** for high-churn workloads (a batch job opening 10k files should not drown a node's event stream).
- **Event prioritization on overflow.** When the ring buffer is full, you must choose what to drop — and the choice is dictated by downstream needs. `execve`/`exit` events are *structurally required*: without them the process tree in Elasticsearch cannot be reconstructed, and every later file/network event becomes unattributable. File-open noise can be sampled; process lifecycle cannot be lost. Encode this as per-event-class drop policy rather than a single global one.

## The agent layer: why Rust, and what it actually does

The agent is the most load-bearing component in the system — it owns BPF loading, event normalization, metadata enrichment, policy compilation, Kafka production, and self-healing. For a fleet-scale deployment I would choose Rust for three concrete reasons rather than ideology:

1. **One static binary.** A musl-linked single file with no runtime dependencies deploys identically across distros — critical when your nodes span CentOS 7-era hosts to the latest Ubuntu.
2. **Bounded behavior under event storms.** No GC pauses, and queue backpressure is explicit in the type system: a full internal channel drops or spools by design instead of growing memory until OOM. An EDR agent that dies during an attack (when event volume peaks) is worse than useless — it is blind exactly when you need it.
3. **Safe concurrency around map updates.** The policy compiler writes BPF maps while the producer thread reads ring-buffer events; Rust's ownership model makes these interactions auditable without a team of reviewers hunting data races in C++.

### Container attribution: cgroup id is the key

In Kubernetes, the stable identity of a workload is **not** its name or PID — it is the cgroup. The BPF side captures only cheap integers (cgroup inode id at fork time, netns id per socket); the agent maintains a local cache mapping `cgroup_id → (pod, namespace, container, image)`, populated from CRI/kubelet and refreshed with TTLs to survive pod churn. Two practical traps:

- **cgroup v1 vs v2** expose different paths and hierarchies; the agent must normalize both, because a mixed fleet is the norm for years after any migration.
- **The node's own noise.** kubelet, containerd, CNI daemons, and log shippers generate enormous event volume that is never interesting to an EDR. Default allowlists for system components are not optional polish — they are what keeps your per-node event rate in the tens of events/second instead of thousands.

### The local policy compiler: atomic map updates

The agent receives compiled policy from the server and translates it into BPF map entries. The hard requirement is **atomicity**: a half-updated block list can either let an attack through or, worse, break legitimate traffic for the duration of the update. The standard technique is double buffering — two pre-allocated maps plus a one-element "active slot" pointer:

```rust
// Fill the next map completely, then flip one u32 — atomic from the kernel's view.
fn apply_policy(next_slot: u32, policy: &CompiledPolicy) -> Result<()> {
    let target = maps.policy_map(next_slot)?;      // pre-allocated BPF hash map
    for rule in policy.rules() {
        target.put(rule.key(), rule.value())?;     // fill completely first
    }
    maps.active_slot().put(SLOT_KEY, next_slot)?;  // single-entry flip
    Ok(())
}
```

Every kernel hook reads the active slot first, so it sees either the old complete policy or the new complete one — never a mix. Pair this with **policy versioning**: every rule set carries a monotonically increasing version, and each agent reports its *effective* version in heartbeats. The control plane can then answer "which nodes are not running v1284?" as a simple audit query — fleet-wide policy consistency becomes measurable instead of assumed.

### Resilience: the network is not part of the security path

Two failure modes define agent reliability design:

- **Kafka unreachable.** Events must spool to local disk in a bounded ring (drop-oldest when full) and replay on reconnect. Dropping events silently during an outage would create exactly the forensic gap an attacker wants.
- **Policy server unreachable.** Already-loaded policy stays effective — enforcement lives in kernel maps, not in network calls. The agent only needs to detect *drift* (its version falling behind the fleet's) and alert on it.

## Control plane: distributing policy to 100k nodes

The policy server owns rule authoring, compilation, distribution, and auditing. At scale, three design points matter more than the transport protocol:

**Versioned deltas, not full pushes.** A full policy snapshot per node per sync is wasteful; agents request "give me everything newer than v1284" and apply a delta. Heartbeats stay cheap (version + health), so 100k agents cost the control plane almost nothing at steady state — all traffic concentrates on actual policy changes, which are rare by design.

**Wave-based rollout.** A bad rule pushed to 100k nodes simultaneously is an incident you cannot roll back fast enough. Rollouts proceed in waves (canary node group → percentage ramp → full fleet) with automatic halt conditions: if canary agents report elevated error rates, enforcement denials on allowlisted traffic, or agent crashes, the wave stops and the rule is quarantined. This is the same discipline as any large-scale config system — but for security policy, a bad rule has two failure modes at once (false positives *and* new attack surface).

**Consistency auditing.** Because agents report effective versions, "policy state of the fleet" is a query, not an assumption: coverage percentage per version, nodes stuck on old versions (usually offline or degraded), and enforcement-capable vs audit-only node counts. That last number — how many nodes can actually *block* versus only *observe* — should be a first-class dashboard metric, because it defines your real protection boundary.

## Data pipeline: where these systems actually die

### Kafka topology

Five topics split the stream by event class (`process`, `file`, `network`, `policy`, `agent`), which lets downstream consumers scale and retain independently. The critical partitioning decision: **partition by node_id.** Per-node ordering is what makes process-tree reconstruction possible in Elasticsearch — a child's `execve` must land after its parent's, with `(pid, start_time)` as the join key. A hash on pid or content would interleave events from one machine and silently corrupt every forensic query you ever run.

### Volume math (the number that sizes everything)

| Stage | Assumption | Rate |
|---|---|---|
| Raw kernel events, busy node | pre-filter | ~10⁴–10⁵ /s |
| Post in-kernel filter, per node | allowlists + rate limits | ~20 /s |
| Fleet: 100k nodes | × 100k | **~2M events/s** |
| Wire size @ ~400 B/event | JSON/Avro | **~70 GB/day** |

Kafka handles this comfortably — it is not the bottleneck. The cost center is **Elasticsearch**, and specifically its cardinality: file paths, remote IPs, and command lines are unbounded fields that explode index size. The standard mitigations, in order of importance: ILM hot/warm/cold tiering with aggressive retention on cold; downsampling low-value event classes (file opens) while keeping `execve`/`exit` and alert-linked events at full fidelity for longer; and pre-hashing high-cardinality fields in the agent so ES stores hashes plus a lookup table rather than raw strings.

### Flink: where EDR becomes detection, not logging

Single-event signatures ("this binary is on a blocklist") are only the floor of an EDR. The real value is **behavior-chain correlation**: `execve` of a downloaded binary → `openat` on `/etc/shadow` or mass file renames → outbound `connect` to a rare remote IP, all within N seconds — that *sequence* is ransomware or exfiltration, and no single event in it is suspicious alone. Flink session windows keyed by `(node_id, process_tree_root)` compute these chains; the engineering challenge is bounding window state (process trees on chatty nodes can be large), which argues for keying on tree root rather than per-process and expiring aggressively. Alerts flow to a separate topic consumed by the alert center, carrying the full event chain as evidence — not just "rule X fired".

## Engineering for stability at scale

The difference between an eBPF demo and a fleet product is unglamorous:

- **Verifier CI matrix.** The BPF verifier rejects programs that are legal on one kernel version/config and illegal on another. Every release must load-test against the supported matrix (5.10 / 5.15 / 6.x × major distros), including BTF availability checks — CO-RE needs `/sys/kernel/btf/vmlinux`, and its absence means graceful fallback, not a crash loop.
- **Right-size your maps.** A production lesson from Netflix's Cilium rollout: default-sized BPF maps caused recurring overflow incidents until they were sized for real workload counts (128 MB → 512 MB eliminated the failures). Map fill rate belongs in per-agent metrics; a map that fills is a silent data-loss event.
- **Idempotent loading.** The agent must survive restarts, node reboots, and policy-server reconnects by converging to the same state: load BPF objects → fetch current policy version → apply delta → report. Any step can be retried without side effects.
- **Rollout discipline for enforcement itself.** Ship in audit-only mode first (observe what *would* be blocked), review false-positive rates per rule class, then enable enforcement incrementally. A blocklist that kills a production deploy pipeline loses trust faster than any missed attack.

## Trade-offs and open questions

Honest limits of this architecture:

- **The kernel floor is a product constraint.** `bpf_lsm` + CO-RE pushes the practical minimum to ~5.8–5.10 for full capability; anything older gets audit-only coverage. In a mixed fleet, "we block X" must always be qualified by "on N% of nodes".
- **eBPF sees syscalls, not payloads.** You know *that* 2 MB went to `c2.example:443`, not what was in it. Deep inspection (file content hashing at read time, network payload) costs real CPU and is where the overhead budget gets spent — scope it per rule class, not globally.
- **Flink state cost scales with fleet chatty-ness**, and ES retention is a direct line item. The data plane, not the collector, determines your steady-state bill; model both before promising "forever traceability".
- **Policy expressiveness vs in-kernel checkability.** Every rule you want enforced must compile to something a BPF program can evaluate cheaply at hook time. Complex behavioral rules belong in Flink (post-hoc correlation); only stateless, local predicates belong in kernel maps. Keeping that boundary clean is what keeps both sides fast.

The through-line of the whole design: **enforcement lives in the kernel where it cannot be bypassed or starved; intelligence lives in the pipeline where it can scale.** The agent is the hinge between them — small enough to run on every node for years, disciplined enough that a 100k-node fleet behaves like one machine.
