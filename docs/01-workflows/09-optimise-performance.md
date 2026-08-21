# 09 — Optimise Performance

**Measure, decide, change, then guard the number.** The guarding step is what
makes the improvement permanent.

Covers [SDLC](sdlc-playbook.md) stages 11–12.

---

## When to use this

- A path is measurably too slow.
- Load is projected to grow past what the current design handles.
- An incident traced back to saturation rather than a logic bug.

**Not this workflow** if you have no measurement. Optimising without a baseline
produces changes you cannot defend and cannot verify.

## Prerequisites

- A target: which path, and what "fast enough" means as a number.

---

## The chain

```
quality:perf path=./src             → profiling, bottlenecks, scalability projection
    ↓
architect:adr                       → the optimisation is a decision  ◆ GATE
    ↓
implementer:full                    → change + tests
    ↓
quality:qa suite=performance        → ◆ threshold row that guards the gain
```

---

## Start with a number

Before running anything, write down the target: *p95 checkout under 800 ms at
200 requests per second*.

Without it you cannot tell success from motion, and the ADR's Rationale field
has nothing to appeal to.

`quality:perf` gives you profiling, bottleneck identification, optimisation
strategies, and a scalability projection. The projection matters as much as the
current reading — it tells you whether you are fixing today's problem or next
quarter's.

---

## Optimisations are always ADR-worthy

They alter a failure mode by construction. Decision Type: `Performance`.

Performance ADRs have unusually honest consequences, because the trade is always
explicit:

| Optimisation | Accepted cost |
|---|---|
| Caching | Staleness window, invalidation complexity |
| Denormalisation | Write amplification, consistency risk |
| Batching | Latency floor for small requests |
| Connection pooling | Resource ceiling under burst |
| Async processing | Eventual consistency, harder debugging |

An ADR that lists a speedup and no cost has not finished thinking.

---

## Guard the gain

Every performance ADR gets a `PERF-n` row carrying **a numeric threshold and a
load profile** — not "should be fast":

```
| PERF-3 | p95 checkout latency under 800ms at 200 rps sustained for 5 min
         | REQ-4, ADR-0018 | yes | tests/performance/test_checkout_load.py
         | 2026-08-21 |
```

Without the threshold row, the next refactor silently gives the improvement back
and nobody notices until a customer does.

---

## Artifacts

| Path | From |
|---|---|
| Performance report — bottlenecks, strategies, scalability projection | `quality:perf` |
| `docs/adr/` — Decision Type `Performance` | `architect:adr` |
| `docs/project-context/quality/performance.md` — `PERF-n` rows | `quality:qa` |
| `docs/current-technical-specification.md` §7 Performance | `architect:spec` |

---

## Worked example

[../04-examples/quality.md](../04-examples/quality.md) — performance analysis
scenario.

---

## Next

- [10 — Modernise a legacy system](10-modernise-legacy-system.md) if the ceiling is structural
