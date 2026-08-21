# Documentation

**Ordered so that browsing order matches reading order.** Numbered directories,
not alphabetical scatter.

---

## Map

| Directory | Answers | Start with |
|---|---|---|
| [00-getting-started/](00-getting-started/) | How do I set this up, and what are the pieces? | [concepts.md](00-getting-started/concepts.md) |
| [01-workflows/](01-workflows/) | **What do I do?** 14 use cases, each a complete path | [README.md](01-workflows/README.md) |
| [02-reference/](02-reference/) | What exists? Agents, functions, skills, tools, rules, artifacts | [README.md](02-reference/README.md) |
| [03-guides/](03-guides/) | How do I do this specific task? | [README.md](03-guides/README.md) |
| [04-examples/](04-examples/) | Show me a real one | [README.md](04-examples/README.md) |
| [99-archive/](99-archive/) | Where did the old document go? | [README.md](99-archive/README.md) |
| [superpowers/](superpowers/) | This repository's own design records | — |

---

## Which do I want?

```
Do you know what you are trying to do?
│
├─ No, I am new here          → 00-getting-started/
│
├─ Yes, it is a task          → 01-workflows/   ← most of the time
│
├─ I need a specific fact     → 02-reference/
│
└─ I want to see one done     → 04-examples/
```

**When in doubt, [01-workflows/](01-workflows/).** Nearly every question that
starts "how do I…" is answered by a workflow, and each one names its
prerequisites, gates, and artifacts.

---

## The 14 workflows

| | | | |
|---|---|---|---|
| [01 New project](01-workflows/01-start-new-project.md) | [02 From a conversation](01-workflows/02-feature-from-conversation.md) | [03 From a requirement](01-workflows/03-feature-from-requirement.md) | [04 Understand a codebase](01-workflows/04-understand-a-codebase.md) |
| [05 Record a decision](01-workflows/05-record-a-decision.md) | [06 Review a PR](01-workflows/06-review-a-pull-request.md) | [07 Production incident](01-workflows/07-fix-production-incident.md) | [08 Audit security](01-workflows/08-audit-security.md) |
| [09 Optimise performance](01-workflows/09-optimise-performance.md) | [10 Modernise legacy](01-workflows/10-modernise-legacy-system.md) | [11 Set up CI/CD](01-workflows/11-set-up-cicd.md) | [12 Manage a backlog](01-workflows/12-manage-backlog.md) |
| [13 Ship a release](01-workflows/13-ship-a-release.md) | [14 Export to platforms](01-workflows/14-export-to-platforms.md) | | |

Plus [sdlc-playbook.md](01-workflows/sdlc-playbook.md) — the 16-stage spine they
all draw from.

---

## Outside docs/

| Path | Holds |
|---|---|
| [../README.md](../README.md) | Repository entry point |
| [../CHANGELOG.md](../CHANGELOG.md) | Version history, v1.0.0 → today |
| [../CLAUDE.md](../CLAUDE.md) | Instructions Claude Code loads automatically |
| `../agents/` | The 5 agent definitions and their function files |
| `../skills/` | The 35 skills |
| `../prompts/` | 18 prompt templates in 11 categories |
| `../instructions/` | `master_instruction_set.md` — RULES 0–12 |
| `../tools/` | Python utilities |

---

## Conventions

**Artifacts land in the project being worked on**, not in this repository —
unless a document says otherwise. `docs/superpowers/` is the exception: it holds
this repository's own design records.

**Counts are verified.** 5 agents, 42 functions, 35 skills, as of 2026-08-21.
Documents that disagree are in [99-archive/](99-archive/) and are marked
superseded.

**Numbered prefixes are reading order**, not priority. `99-archive` sorts last
because it is consulted least.
