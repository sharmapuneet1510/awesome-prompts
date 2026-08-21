# Reference

**One document per topic. No overlap.**

Reference answers *what exists*. For *what to do*, start at
[../01-workflows/](../01-workflows/).

| Document | Covers |
|---|---|
| [agents.md](agents.md) | The 5 agents, their roles, and the 9 specialist modes that map onto them |
| [functions.md](functions.md) | All 42 callable functions, with inputs and the workflow each belongs to |
| [skills.md](skills.md) | The 35 skills agents dispatch to |
| [tools.md](tools.md) | Python tools in `tools/`, plus `token_optimizer` and `parser` |
| [rules.md](rules.md) | 4 principles, RULES 0–12, and every gate |
| [artifacts.md](artifacts.md) | Every file the system produces, who writes it, and which must never be hand-edited |

Also here: `architecture-reference.html` and `architecture-system.mmd` — system
diagrams.

---

## Counts

| | |
|---|---|
| Agents | 5 |
| Callable functions | 42 |
| Skills | 35 |
| Prompt templates | 18 across 11 categories |
| Export platforms | 8 |
| Instruction rules | RULES 0–12, plus 4 principles |

Verified 2026-08-21. Five earlier documents disagreed on these numbers; the ones
above are counted from the filesystem and the agent dispatch tables.

---

## Quick answers

**Which agent do I use?** → [agents.md](agents.md), or go straight to
[../01-workflows/README.md](../01-workflows/README.md) and pick your task.

**What does `quality:observe` do differently from `quality:review`?** →
[functions.md](functions.md#quality). Observe reports conformance and never
edits; review scores and may propose fixes.

**Why did my command refuse to run?** → [rules.md](rules.md). Almost always
RULE 11 (unapproved spec) or RULE 11a (missing ADR).

**Can I edit this generated file?** → [artifacts.md](artifacts.md#never-hand-edit-these).

**Where did the old documentation go?** → [../99-archive/](../99-archive/).
