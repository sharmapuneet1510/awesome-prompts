# Workflows

**Start here. Find what you are trying to do, run that workflow.**

Every workflow below is a complete path: prerequisites, the command chain,
the gates you must pass, and the artifacts you end up with. They all draw on
the same 16-stage spine — see [sdlc-playbook.md](sdlc-playbook.md) — but you
rarely need all 16 stages at once.

---

## I want to…

| I want to… | Workflow |
|---|---|
| …start a project that does not exist yet | [01 — Start a new project](01-start-new-project.md) |
| …build a feature, starting from a conversation | [02 — Feature from a conversation](02-feature-from-conversation.md) |
| …build a feature, starting from a written requirement | [03 — Feature from a requirement](03-feature-from-requirement.md) |
| …get my bearings in a codebase I do not know | [04 — Understand a codebase](04-understand-a-codebase.md) |
| …record why we decided something | [05 — Record a decision](05-record-a-decision.md) |
| …review a pull request | [06 — Review a pull request](06-review-a-pull-request.md) |
| …fix something that is broken in production | [07 — Fix a production incident](07-fix-production-incident.md) |
| …find security holes | [08 — Audit security](08-audit-security.md) |
| …make it faster | [09 — Optimise performance](09-optimise-performance.md) |
| …modernise something old and large | [10 — Modernise a legacy system](10-modernise-legacy-system.md) |
| …get it deployed | [11 — Set up CI/CD](11-set-up-cicd.md) |
| …turn a backlog into something readable | [12 — Manage a backlog](12-manage-backlog.md) |
| …ship a release | [13 — Ship a release](13-ship-a-release.md) |
| …use these agents in Cursor, Copilot, or elsewhere | [14 — Export to platforms](14-export-to-platforms.md) |

---

## Choosing between the three "build" workflows

The most common confusion. All three end in working code; they differ in where
you start.

```
Do you have a written, agreed requirement?
│
├─ No, only a conversation or a vague idea
│  │
│  ├─ …and the project does not exist yet    → 01 Start a new project
│  └─ …and the codebase already exists       → 02 Feature from a conversation
│
└─ Yes, a requirement document or ticket     → 03 Feature from a requirement
```

Workflow 02 is the long form: it spends stages 1–5 turning a conversation into
requirements, analysis, and recorded decisions before any planning happens.
Workflow 03 skips straight to stage 6 because that work is already done.

**Do not skip 02 just because it is longer.** Its early stages exist to stop you
implementing the wrong thing precisely, which is the most expensive failure mode
in the catalogue.

---

## The gates

Four gates interrupt these workflows. They are refusals, not warnings — an agent
stops rather than proceeding with a caveat.

| Gate | Rule | What it blocks | Released by |
|---|---|---|---|
| Requirements approved | RULE 11 | `architect:design` | You approve `requirements.md` |
| Design approved | RULE 11 | Task generation | You approve `design.md` |
| Tasks approved | RULE 11 | `implementer:build` / `:full` | You approve `tasks.md` |
| ADR accepted | RULE 11a | Implementing a decision-bearing change | You approve the ADR |

**Trivial work is exempt from RULE 11** — one-line fixes, config tweaks, small
documentation edits. Substantive changes to agent, skill, or instruction files
are not trivial.

Full detail: [../02-reference/rules.md](../02-reference/rules.md).

---

## Conventions used in every workflow document

**Prerequisites** — what must already exist. If it does not, the workflow names
which other workflow produces it.

**The chain** — commands in order. `→` means "then"; a command in *(parentheses)*
is conditional.

**Gates** — where you will be stopped and asked to approve something.

**Artifacts** — every file produced, and where it lands. Unless stated otherwise,
artifacts land in the **project being worked on**, not in this repository.

**Worked example** — a link into [../04-examples/](../04-examples/), where one
exists. Some workflows are newer than the example library; those say so rather
than linking to nothing.

---

## Reference

- [sdlc-playbook.md](sdlc-playbook.md) — the 16-stage spine, with every command mapped to its stage
- [../02-reference/functions.md](../02-reference/functions.md) — all 42 functions
- [../02-reference/artifacts.md](../02-reference/artifacts.md) — every artifact and the stage that produces it
