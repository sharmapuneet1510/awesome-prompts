# 15 — Challenge a Conclusion

**Attack a finished conclusion before anyone trusts it.** NEMESIS assumes the result may be wrong,
investigates independently, and either proves it wrong or says it survived.

Covers the review and verification stages of the [SDLC](sdlc-playbook.md).

---

## When to use this

- A review said `PASS` and the change is critical, security-relevant, payment-related or going to
  production.
- An ADR is about to become Accepted and getting it wrong is expensive.
- A test result, RCA or release approval is being relied on and nobody else has tried to break it.
- You want a second opinion that is **not** another reviewer agreeing with the first.

Not for: a first review (use [06](06-review-a-pull-request.md)), or anything with no conclusion yet.

## Prerequisites

- A conclusion to challenge, with an id or a path (`PR-1839`, `CR-839`, `ADR-104`, `API-TEST-2291`,
  `RELEASE-RC-32`).
- Read access to the sources: requirements, git, test results.
- Optional: `docs/nemesis/nemesis.yml` (start from
  [`nemesis-config.example.yml`](../04-examples/nemesis-config.example.yml)). Without it NEMESIS is
  manual-only.

---

## The chain

```
quality:review pr=1839            → PASS
    ↓
orchestrator:nemesis target=PR-1839     (or /nemesis PR-1839)
    ↓  NEMESIS ACTIVATED
    ↓  fresh sub-agent, read-only, five inputs only
    ↓
docs/nemesis/NMS-2026-00982.md    → verdict + ranked hypotheses of why
    │
    ├─ DEFEATED / CHALLENGED      → back to the owning specialist, hypotheses first
    │                               fix → re-review → NEMESIS again
    ├─ INSUFFICIENT EVIDENCE      → back to the owner with the evidence to obtain
    └─ SURVIVED (WITH CONDITIONS) → continue the workflow
```

## What you get

A report with, in order: the **verdict**, the **failure-cause hypotheses** (why it failed, and the
cheapest check for each), the original conclusion, the reverse hypothesis, the challenge paths
executed, the findings (category, severity and confidence kept separate), the evidence assessment and
the required actions. Worked examples:
[defeated](../04-examples/nemesis-defeated.md) and [survived](../04-examples/nemesis-survived.md).

## The verdicts

| Verdict | Meaning |
|---|---|
| `SURVIVED` | No findings. The conclusion held up. |
| `SURVIVED WITH CONDITIONS` | Only minor or speculative findings (at most one non-speculative medium one), plus stated assumptions. |
| `CHALLENGED` | A significant finding that is not backed by a counterexample, or several medium ones: reconsider the conclusion. |
| `DEFEATED` | A high-impact, high-confidence finding backed by a counterexample or by contradictory evidence. |
| `INSUFFICIENT EVIDENCE` | Neither the conclusion nor its opposite can be supported. |

NEMESIS never has to find a defect, and does not invent one.

## Automatic activation (optional)

With a `docs/nemesis/nemesis.yml` (not `enabled: false`) whose `auto_activate` rules are on, three
functions run NEMESIS when a rule matches, each at its own point:

| Function | When | What the verdict does |
|---|---|---|
| `quality:review` | after a `PASS` (critical, security or payment change) | `DEFEATED`, `CHALLENGED` or `INSUFFICIENT EVIDENCE` overrides the `PASS`; `SURVIVED WITH CONDITIONS` keeps it and copies the conditions |
| `architect:adr` | between `Status: Proposed` and the approval request (architecture change) | advice to the approver; a human still approves |
| `orchestrator:pr` | before the release PR (production release) | `DEFEATED`, `CHALLENGED` or `INSUFFICIENT EVIDENCE` stops it |

Without the file nothing runs by itself.

## Limits

A prompt cannot technically enforce isolation or read-only access. The function instructs both and the
report records what actually happened (`context_isolated`, `access`, `sources`); a run that could not
spawn a fresh sub-agent says so in its verdict.

Two guards keep it from looping. After **two consecutive** `DEFEATED` or `CHALLENGED` results for the
same target the gates stop and hand the decision to a human, and a challenge of a NEMESIS verdict
stops at `maximum_depth` (default 2; a third is refused, and writes nothing). A challenger never
evaluates a gate itself, and `enabled: false` refuses every trigger, even a manual `/nemesis`.

## Related

- Skill: [`nemesis_skill`](../../skills/nemesis_skill.md)
- Function: [`orchestrator:nemesis`](../../agents/orchestrator/functions/nemesis.md)
- Requirement: [`nemisis_requirement.md`](../../nemisis_requirement.md)
