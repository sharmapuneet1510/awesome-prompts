# 12 — Manage a Backlog

**Turn a Jira export into something people will actually read**, and turn plain
text into properly formed issues.

Covers [SDLC](sdlc-playbook.md) stage 0.

---

## When to use this

- A Jira export needs to be readable by people who will not open Jira.
- Plain-text requirements need to become issues with acceptance criteria.
- Planning a sprint and needing to see the shape of the backlog.

## Prerequisites

- A Jira export (JSON or CSV), or a plain-text requirements file.

No live Jira connection is used. These functions read exports.

---

## The chain

```
ba:parse path=./jira-export.json    → normalised issues, metadata extracted
    ↓
ba:report path=./jira-export.json   → interactive HTML backlog
```

Going the other way — text into issues:

```
ba:create path=./requirements.txt   → requirements.json + BDD HTML cards
```

---

## What each produces

**`ba:parse`** — reads JSON or CSV, normalises fields, extracts all issue
metadata. Use when you need the data rather than the view.

**`ba:report`** — a self-contained interactive HTML backlog: filters by status,
priority, assignee, and sprint, plus summary statistics. No external CDN
dependencies, so it works offline and can be emailed.

**`ba:create`** — the reverse direction. Plain-text requirements become
structured issues with **BDD acceptance criteria** (given/when/then) and HTML
requirement cards.

---

## Acceptance criteria are the point

`ba:create` produces given/when/then criteria because they are the hop that
makes traceability work. Test scenarios cite them; `quality:observe` compares
tests against them; `ba:trace` check T-6 verifies every criterion has a test.

A criterion that cannot be written as given/when/then is usually not a
criterion — it is a wish. That is worth discovering at backlog time rather than
at review time.

---

## Where this leads

This workflow produces the Jira items that
[02](02-feature-from-conversation.md) and
[03](03-feature-from-requirement.md) consume. Every ADR names a Parent Jira,
which makes this hop 1–2 of the traceability chain.

If the backlog items are vague, the ADRs will name vague parents and the chain
degrades. Running [02](02-feature-from-conversation.md)'s discovery stages first
is often worth it.

---

## Artifacts

| Path | From |
|---|---|
| Normalised issue data | `ba:parse` |
| Interactive HTML backlog | `ba:report` |
| `requirements.json`, `requirements-cards.html` | `ba:create` |
| `docs/project-context/mvp-scope.md` | Via `ba:brd` |

---

## Reference

`skills/jira_html_report_skill.md` — parsing and report generation.
`skills/ba_create_skill.md` — text to issues with BDD criteria.
`skills/jira_incremental_spec_generator_skill.md` — reading a large Jira
project incrementally into a book-format specification.
