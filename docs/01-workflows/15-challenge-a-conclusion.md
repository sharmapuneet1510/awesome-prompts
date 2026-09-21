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
orchestrator:nemesis target=CR-839      (or /nemesis CR-839)
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
| `SURVIVED WITH CONDITIONS` | Only minor or speculative findings, plus stated assumptions. |
| `CHALLENGED` | Significant issues; reconsider the conclusion. |
| `DEFEATED` | A high-impact, high-confidence finding backed by a counterexample. |
| `INSUFFICIENT EVIDENCE` | Neither the conclusion nor its opposite can be supported. |

NEMESIS never has to find a defect, and does not invent one.

## Automatic activation (optional)

With a `docs/nemesis/nemesis.yml` whose `auto_activate` rules are on, `quality:review`,
`architect:adr` and `orchestrator:pr` invoke NEMESIS after a PASS when a rule matches. Without the
file nothing runs by itself.

## Limits

A prompt cannot technically enforce isolation or read-only access. The function instructs both and the
report records what actually happened (`context_isolated`, `access`, `sources`); a run that could not
spawn a fresh sub-agent says so in its verdict.

## Related

- Skill: [`nemesis_skill`](../../skills/nemesis_skill.md)
- Function: [`orchestrator:nemesis`](../../agents/orchestrator/functions/nemesis.md)
- Requirement: [`nemisis_requirement.md`](../../nemisis_requirement.md)
