# 06 — Review a Pull Request

**Two questions, deliberately separated:** does the code match what was agreed,
and is the code any good?

Covers [SDLC](sdlc-playbook.md) stage 11.

---

## When to use this

- A PR is open.
- Before merging anything substantial.

## Prerequisites

- A PR or a diff.
- For conformance checking: `specs/<feature>/requirements.md`, `docs/adr/`, and
  `docs/current-technical-specification.md`. Without them `quality:observe`
  can still run, but it can only report what it can compare.

---

## The chain

```
quality:observe pr=123      → conformance: 4 comparisons, observations only
    ↓
quality:review pr=123       → quality: scoring, may propose fixes
    ↓
(quality:security path=./src)   ← if the PR touches auth, input handling, or secrets
(quality:perf path=./src)       ← if it touches a hot path
    ↓
(quality:report pr=123)     → single executive synthesis of all of the above
```

**Run `quality:observe` first. Conformance before opinion.**

---

## Why two functions, not one

They answer different questions and blur badly when merged.

|  | `quality:observe` | `quality:review` |
|---|---|---|
| Asks | Does this match what was agreed? | Is this good code? |
| Output | Gaps, both directions | Score, findings, fix proposals |
| May edit code | Never | May propose |
| May write an ADR | Never — may only propose one | No |
| Assigns a score | No | Yes |

A reviewer that both diagnoses and fixes tends to fix what is easy rather than
report what matters.

---

## The four comparisons

`quality:observe` checks each in both directions.

### 1. Requirement ↔ Code
| Direction | Gap |
|---|---|
| Requirement with no code | Unimplemented requirement |
| Code with no requirement | Scope creep |

### 2. ADR ↔ Code
| Direction | Gap |
|---|---|
| ADR decision not reflected in code | Decision not honoured |
| Code contradicting an Accepted ADR | **Undocumented reversal — the most serious finding** |
| Decision-bearing code with no ADR | RULE 11a violation |

### 3. Specification ↔ Code
| Direction | Gap |
|---|---|
| Spec section with no implementation | Spec ahead of code |
| Behaviour absent from the spec | Spec stale — regenerate |

### 4. Tests ↔ Acceptance Criteria
| Direction | Gap |
|---|---|
| Criterion with no test | Unverified criterion |
| Test asserting behaviour no criterion requires | Over-specified test, or a missing criterion |

---

## Handling an undocumented reversal

The sharpest finding: code that contradicts an Accepted ADR. Two legitimate
responses, and one that is not:

1. **Implement per the ADR** — the decision stands.
2. **Supersede the ADR** via [05](05-record-a-decision.md) — the decision has
   genuinely changed, so record why.
3. ~~Quietly edit the ADR to match the code~~ — this destroys the record and is
   never correct.

---

## Reading a finding

Findings carry RULE 12 labels: a FACT about what is there, plus a PROPOSAL about
what to do. Never both diagnosis and unilateral fix.

```
### ADR ↔ Code — decision not honoured
FACT: ADR-0012 requires an Idempotency-Key header; src/order/api.py:44
accepts the request without reading one.
PROPOSAL: implement per ADR-0012, or supersede it via architect:adr.
```

---

## Reviewing several PRs

```
quality:batch-review from=./reviews.json
```

One HTML report with sidebar tabs and a summary dashboard, rather than n
separate reviews you then have to hold in your head at once.

---

## Artifacts

| Path | From |
|---|---|
| `docs/observations/<PR>-observations.md` | `quality:observe` |
| Review report with score | `quality:review` |
| Batch HTML report | `quality:batch-review` |
| `docs/project-context/open-questions.md` | Unresolved gaps, appended |

---

## Exit condition

No High findings open. High findings block the RULE 11 gate — they are not
advisory.

---

## Worked example

[../04-examples/quality.md](../04-examples/quality.md) — PR review scenario.

---

## Next

- `quality:qa` to fold any Tests ↔ AC gaps into the standing suites — see
  [08](08-audit-security.md) and [09](09-optimise-performance.md)
- [13 — Ship a release](13-ship-a-release.md)
