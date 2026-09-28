# Super Skills

**What makes a skill a "super skill" in this repository, and what changed to
get all 38 there.** Updated 2026-09-28.

> **Correction.** An earlier version of this page (commit `214803b`) claimed
> per-skill token savings of 18–32% and marked all 37 skills enhanced. None of
> that had been measured or done. This page replaces it; the numbers below are
> measured, and the method is stated.

---

## The standard

A super skill has four properties. Each is checkable by reading the file.

| Property | What it means | Where it is defined |
|---|---|---|
| **Quick Card** | A table directly under the H1: use when, skip when, inputs, produces, steps, done when, load on demand, run report, pairs with | `agent_skill_design_skill` §3a |
| **Senior defaults** | For coding skills: the 4–6 advanced rules that matter most for that stack, each consistent with the body | same |
| **Progressive disclosure** | The card names section numbers, so an agent loads one section, not the file | same |
| **Run report** | A run that changes files writes one self-contained HTML report: what was asked, what was done step by step, every artifact, labelled claims, gates, open items | `html_report_skill` |

Plus hygiene the validator enforces: frontmatter with `name`, `version`,
`description`, `applies_to`; code fences that actually close.

```bash
python3 tools/skill_validator.py      # 38 valid; README.md is not a skill
```

---

## Token budget — measured

Estimated as characters ÷ 4 over `skills/*_skill.md`.

| | Tokens (≈) |
|---|---|
| All 38 skill files, in full | 143,800 |
| All 38 Quick Cards | 11,700 — 8.2% of the full set |
| Median skill file | 4,150 |
| Median Quick Card | 290 |
| Largest file — `code_review_skill` | 9,540; its card 250 |

**What this does and does not show.** An agent that reads only the cards of
the skills it might need, then loads one section, reads a fraction of the file.
An agent that loads whole files anyway pays about 290 tokens *more* per skill
for the card. The saving comes from following the card's **Load on demand** row;
it is not automatic, and agent behaviour was not measured here.

---

## The HTML run report

One contract, defined once in `html_report_skill`, instead of a report format
per skill. Each skill's card names only the sections it adds.

| # | Section | Rule |
|---|---|---|
| 1 | Header | Skill + version, invocation, date, outcome: `Done` · `Partial` · `Blocked` |
| 2 | Summary | ≤ 4 sentences |
| 3 | What was done | Ordered steps, each `done` / `skipped` / `failed` with one line of detail |
| 4 | Artifacts | Every touched path, linked, with action and purpose |
| 5 | Decisions & claims | RULE 12 labels; every `FACT` cites file:line |
| — | Skill-specific | e.g. `test_skill` adds AC → test map, coverage, mutation score |
| 6 | Gates & checks | Only checks that actually ran, each with evidence |
| 7 | Open items | Follow-ups, risks, questions for a human |

The page is self-contained — inline CSS, no scripts, no external requests —
with light and dark themes, a sticky section nav, collapsible sections built on
`<details>`, and print styles. Every interpolated value is HTML-escaped. It is
written only when a run changes files, or on `report=html`.

---

## What changed in v5.1

### Added

- `html_report_skill` — the shared run-report contract (skill 38).
- A Quick Card on all 38 skills; senior defaults on the 18 coding skills.
- `applies_to` frontmatter on the 14 skills that lacked it — the validator now passes all 38.
- `agent_skill_design_skill` §3a — the Quick Card specification.
- [Skills playbook](../01-workflows/skills-playbook.md) — which skills each of the 16 SDLC stages loads.

### Fixed — defects in the skills themselves

| Skill | Defect | Fix | Evidence |
|---|---|---|---|
| 11 skills | 115 closing code fences carried a language tag (` ```java `). In CommonMark such a line does not close the block, so everything after the first example rendered as code | Bare closing fences | Parser pass; nested four-backtick block in `project_context_skill` left intact |
| `tools/fix_code_blocks.py` | Tagged every bare fence, closers included — the cause of the above | Tags opening fences only | 0 closers touched on re-run |
| `tools/skill_validator.py` | Counted every fence as an opener, so it reported correct closers as warnings | Tracks open/close; warns on tagged closers instead | Warnings 424 → 55 (the 55 are real untagged openers) |
| `backend_skill` | `async def` routes on a synchronous SQLAlchemy session blocked the event loop | Plain `def` routes | Example run under FastAPI TestClient: 201 / 409 / 400 / 200 / 401 / 401 |
| `backend_skill` | Login returned early for unknown emails, so timing revealed which accounts exist | Verify against a dummy hash either way | Median 33.2 ms known email vs 33.1 ms unknown |
| `backend_skill` | `python-jose` and `passlib` (last release 2020); Pydantic v1 `class Config` | PyJWT, pwdlib (Argon2id), `model_config` | Same run, deprecation warnings as errors |
| `opentelemetry_skill` | Depended on `opentelemetry-exporter-jaeger-thrift` at 1.35.0 — the artifact ended at 1.34.1, so the build could not resolve | Instrumentation BOM 2.31.1; OTLP to Jaeger | Maven Central metadata |
| `lombok_skill` | "Best practice" put `@Data` on a JPA entity and `@Enumerated` on a `String` | `@Getter`/`@Setter`, id-based `equals`, constant `hashCode`, enum field | Compiled with Lombok 1.18.34 + Hibernate 6.5.3: hash stable after id assignment |
| `lombok_skill` | `@Wither` (deprecated) described as a setter | `@With`, which returns a copy | Same compile |
| `test_skill` | `userEvent` imported from `@testing-library/react`, which does not export it; thin on technique | Rewritten: AAA, given/when/then, fakes vs mocks, Testcontainers, property-based, contract, mutation, determinism | pytest + Hypothesis examples pass in random order |
| `multi_review_html_skill`, `ba_create_skill` | Review and requirement text injected without escaping — a snippet with `</script>` or `List<String>` broke the page | JSON data blocks with `<` escaped; render via `textContent` | — |
| `spring_advanced_skill` | Comment said `publishEvent` fires after commit | It fires immediately; the listener's `AFTER_COMMIT` defers delivery | — |
| `context_builder_skill` | Named callers removed in v4 and an API `tools/context_builder.py` does not have | Real callers; real `ContextBuilder(...).build()` example | Example run |

### Not done

- Skill bodies were not shortened. The saving is from reading cards, not from rewriting 16,000 lines.
- 55 opening code fences still have no language tag. They render correctly.
- `orchestrator_agent.md` refers to an `architecture_skill` that does not exist.
- `CHANGELOG.md` has two `[5.0.0]` sections and a `[1.0.0]` dated 2026-09-28 above `[Unreleased]`.

---

## See also

- [skills.md](skills.md) — every skill, grouped
- [../01-workflows/skills-playbook.md](../01-workflows/skills-playbook.md) — skills by SDLC stage
- `skills/agent_skill_design_skill.md` · `skills/html_report_skill.md`
