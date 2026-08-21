# awesome-prompts

**A spec-driven engineering system for AI coding assistants.** Five role-based
agents, 42 callable functions, 35 reusable skills — with gates that stop an
assistant from building the wrong thing confidently.

Exports to Claude, Copilot, Cursor, Windsurf, Gemini, Continue, OpenAI, and
Aider.

---

## What do you want to do?

| | Go to |
|---|---|
| **Set it up** | [docs/00-getting-started/](docs/00-getting-started/) |
| **Do a task** | [docs/01-workflows/](docs/01-workflows/) ← most of the time |
| **Look something up** | [docs/02-reference/](docs/02-reference/) |
| **See a worked example** | [docs/04-examples/](docs/04-examples/) |
| **Understand the design** | [docs/00-getting-started/concepts.md](docs/00-getting-started/concepts.md) |

---

## The 14 workflows

Every one names its prerequisites, the command chain, the gates you will hit,
and the artifacts you end up with.

| Workflow | For |
|---|---|
| [01 Start a new project](docs/01-workflows/01-start-new-project.md) | Greenfield, nothing exists yet |
| [02 Feature from a conversation](docs/01-workflows/02-feature-from-conversation.md) | A stakeholder described a problem |
| [03 Feature from a requirement](docs/01-workflows/03-feature-from-requirement.md) | You have a ticket |
| [04 Understand a codebase](docs/01-workflows/04-understand-a-codebase.md) | You inherited something |
| [05 Record a decision](docs/01-workflows/05-record-a-decision.md) | Writing an ADR |
| [06 Review a pull request](docs/01-workflows/06-review-a-pull-request.md) | A PR is open |
| [07 Fix a production incident](docs/01-workflows/07-fix-production-incident.md) | Something is broken now |
| [08 Audit security](docs/01-workflows/08-audit-security.md) | Finding abuse paths |
| [09 Optimise performance](docs/01-workflows/09-optimise-performance.md) | Making it faster |
| [10 Modernise a legacy system](docs/01-workflows/10-modernise-legacy-system.md) | Structural change to something running |
| [11 Set up CI/CD](docs/01-workflows/11-set-up-cicd.md) | Getting it deployed |
| [12 Manage a backlog](docs/01-workflows/12-manage-backlog.md) | Jira in, readable out |
| [13 Ship a release](docs/01-workflows/13-ship-a-release.md) | Proving the chain holds |
| [14 Export to platforms](docs/01-workflows/14-export-to-platforms.md) | Using this in Cursor, Copilot, elsewhere |

Plus the [SDLC playbook](docs/01-workflows/sdlc-playbook.md): 16 stages, every
command mapped to its stage and gate.

---

## Quick start

```bash
git clone https://github.com/sharmapuneet1510/awesome-prompts.git
cd awesome-prompts

python3 tools/exporter.py --list       # see what is available
python3 tools/exporter.py --dry-run    # preview
python3 tools/exporter.py              # export to all 8 platforms
```

Then invoke a function in your assistant:

```
architect:analyse jira=PROJ-123        # how does this work today?
architect:adr jira=PROJ-123            # record the decision
implementer:full path=./specs/checkout # build it
quality:observe pr=123                 # does it match what we agreed?
```

Full setup: [docs/00-getting-started/](docs/00-getting-started/).

---

## The idea

**What is true now** and **why it became true** are separate documents.

| Question | Document | Property |
|---|---|---|
| How does this work today? | Current Technical Specification | Regenerated from decisions. Only current truth |
| Why is it like this? | ADR log | Immutable. Includes the paths not taken |

The specification is a **projection** of accepted decisions, rebuilt from
scratch each time — so it never carries a claim no decision supports. ADRs are
never edited or deleted, even when superseded, because a superseded decision was
correct when it was made and that record is what stops someone re-introducing
the design it replaced.

Ordinary documentation fails exactly here: it accumulates until no reader can
tell which sentences are still true.

Two mechanisms enforce it:

**Gates** — six of them, all refusals rather than warnings. A change that alters
a contract, a data shape, a dependency, or a failure mode needs an accepted
decision record before the code is written.

**Labels** — every substantive claim is tagged FACT (cited), INFERENCE
(reasoned), PROPOSAL (awaiting you), or DECISION (you approved). Only a DECISION
changes the specification. This stops a plausible guess becoming the foundation
for three more.

More: [docs/00-getting-started/concepts.md](docs/00-getting-started/concepts.md).

---

## What is in here

| | Count | Where |
|---|---|---|
| Agents | 5 | [`agents/`](agents/) · [reference](docs/02-reference/agents.md) |
| Callable functions | 42 | [reference](docs/02-reference/functions.md) |
| Skills | 35 | [`skills/`](skills/) · [reference](docs/02-reference/skills.md) |
| Prompt templates | 18 in 11 categories | [`prompts/`](prompts/) |
| Export platforms | 8 | [workflow 14](docs/01-workflows/14-export-to-platforms.md) |
| Rules | RULES 0–12 + 4 principles | [`instructions/`](instructions/) · [reference](docs/02-reference/rules.md) |
| Python tools | 22 | [`tools/`](tools/) · [reference](docs/02-reference/tools.md) |

### The five agents

| Agent | Owns |
|---|---|
| **Orchestrator** | Planning, orchestration, trade-offs, risk, shipping |
| **Architect** | Design, technical analysis, decision records, the specification |
| **Implementer** | Code, tests, docs, CI/CD, infrastructure |
| **Quality** | Conformance, review, security, performance, debugging, QA suites |
| **Business Analyst** | Discovery, requirements, backlog, traceability |

Agents orchestrate and dispatch; [skills](docs/02-reference/skills.md) hold the
implementation knowledge. Adding a language means adding a skill, not an agent.

---

## Repository layout

```
├── README.md · CHANGELOG.md · CLAUDE.md · CREDITS.md
├── agents/          5 agent definitions + function files
├── skills/          35 reusable skills
├── prompts/         18 templates, 11 categories
├── instructions/    master_instruction_set.md — RULES 0–12
├── tools/           Python utilities, incl. the 8-platform exporter
├── hooks/           automation hooks
├── token_optimizer/ query analysis library
├── parser/          Java field-derivation analysis
└── docs/
    ├── 00-getting-started/
    ├── 01-workflows/      ← 14 use cases
    ├── 02-reference/      ← agents, functions, skills, tools, rules, artifacts
    ├── 03-guides/
    ├── 04-examples/
    ├── 99-archive/
    └── superpowers/       this repo's own design records
```

---

## History

[CHANGELOG.md](CHANGELOG.md) — v1.0.0 (December 2025) through today,
reconstructed from 280 commits.

The shape of it: a prompt collection became a skill library (v1.0.0), gained a
multi-platform exporter (v2.0.0) and an autonomous developer system (v3.0.0),
grew to thirteen agents (v3.5.0), consolidated back to five (v4.0.0), added the
spec-driven gate (v4.2.0), then decision records and traceability (v5.0.0).

---

## Contributing

New skill? Read `skills/agent_skill_design_skill.md` first, then register it in
`skills/README.md`.

Substantive changes to agent, skill, or instruction files are feature work under
RULE 11 — they need the requirements → design → tasks chain. Only trivial edits
are exempt.

---

## Credits

Prompt templates and several skills draw on
[ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts).
The four behavioural principles follow Andrej Karpathy's observations on LLM
coding pitfalls. See [CREDITS.md](CREDITS.md).
