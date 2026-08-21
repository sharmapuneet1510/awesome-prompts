# Changelog

All notable changes to this project, newest first.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/).

> **On version numbers.** This repository ran two overlapping version schemes
> for most of its life: a repo release number that reached `v4.2.0` in May 2026,
> and an agent-architecture number that ran `v1.0` → `v3.2`. Nothing was ever
> git-tagged. This changelog reconciles them into a single line, keeping the
> dates and content that actually shipped and noting the architecture version
> inside each release. Releases before `v5.0.0` are reconstructed from commit
> history and are dated by the work, not by a tag.

---

## [5.1.0] — 2026-08-21

Documentation restructure. No behavioural change to any agent, skill, or tool.

### Added
- `CHANGELOG.md` — this file.
- `docs/01-workflows/` — 14 use-case workflows, each with prerequisites, the
  command chain, gates, and artifacts produced.
- `docs/02-reference/` — one document per topic: agents, functions, skills,
  tools, rules, artifacts.
- `docs/00-getting-started/` — installation, quick start, and a concepts page
  explaining agent vs. skill vs. function vs. gate.
- `docs/99-archive/` — superseded documents, preserved with a header naming
  what replaced them.

### Changed
- Documentation reorganised from 21 unordered root-level files into an ordered
  `docs/` hierarchy. Browsing order now matches reading order.
- Root reduced to `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `CREDITS.md`.
- `README.md` rewritten as a use-case entry point rather than a feature list.
- Function documentation consolidated from five overlapping files into
  `docs/02-reference/functions.md`.
- Skill documentation consolidated from two files into
  `docs/02-reference/skills.md`.
- SDLC documentation consolidated from six files into `docs/01-workflows/`.
- Specialist mode documentation folded into `docs/02-reference/agents.md`.

### Removed
- `README.html` — a generated copy of `README.md` last regenerated 2026-05-25
  and three months out of date.

### Fixed
- Contradictory counts across documentation. Five files claimed different
  numbers of functions (28, 30, 31) and skills (22, 26, 31). All now report the
  verified counts: **5 agents, 42 functions, 35 skills**.

---

## [5.0.0] — 2026-08-18

The spec-driven development platform. Implements `requirements-18082026.md`
as prompt-layer artifacts. Architecture v3.2, instruction set v2.2.

### Added
- **`skills/adr_skill.md`** — Engineering Decision Records: a 13-field record,
  a seven-state lifecycle with a legal-transition table, ten decision types as
  a closed enum, ID allocation, a supersede chain requiring reciprocal edits,
  and a trigger rule for what actually earns an ADR.
- **`skills/project_context_skill.md`** — the 14-node shared knowledge tree,
  a template per node, and an ownership matrix naming which companion writes
  each node and on what event.
- **`skills/current_tech_spec_skill.md`** — the Current Technical Specification
  as a projection of Accepted-or-later ADRs, regenerated rather than edited,
  plus the Final Implementation Record.
- **`skills/traceability_skill.md`** — the eight-hop chain from requirement to
  release, with 18 validation checks split forward, backward, and integrity.
- **`RULE 11a` — ADR Gate.** A change to a contract, data shape, dependency, or
  failure mode requires an Accepted ADR before the code is written.
- **`RULE 12` — Epistemic Labelling.** Every substantive claim is a FACT
  (cited), INFERENCE (reasoned), PROPOSAL (awaiting a human), or DECISION
  (approved). Only a human-approved DECISION mutates the technical
  specification.
- **Nine companion functions**, mapped onto the existing five agents rather
  than adding new ones:
  - `ba:discover`, `ba:clarify`, `ba:brd`, `ba:trace` — BA Companion
  - `architect:analyse`, `architect:adr`, `architect:spec` — Developer Companion
  - `quality:observe` — Review Companion, observations only
  - `quality:qa` — QA Companion, five reusable suites
- **`docs/01-workflows/sdlc-playbook.md`** — the complete 16-stage lifecycle
  with the commands available at each stage and the gate that must pass before
  the next one starts.

### Changed
- `implementer:build` now runs a four-check gate and refuses rather than warns:
  approved `tasks.md`, an Accepted ADR for decision-bearing changes, no High
  traceability findings, and every task citing a requirement ID.
- Master Instruction Set v2.1 → v2.2.
- Skills 31 → 35. Callable functions 31 → 42.

### Fixed
- `orchestrator:ideate` and `orchestrator:solve` had function files and were
  documented in `agents/orchestrator/README.md` but were never listed in the
  agent's dispatch table. Added. The true function count was 42, not 40.

---

## [4.2.0] — 2026-08-06 → 2026-08-08

The spec-driven gate, and the return of `prompts/`.

### Added
- **`RULE 11` — Spec-Driven Gate.** No feature code without an approved
  requirements → design → tasks chain.
- **`RULE 10`** — surgical precision and token efficiency: surgical
  modification, diff-only outputs, graph-style context curation, token and
  memory efficiency, execution workflow.
- `skills/spec_driven_development_skill.md` — artifact templates and the
  approval-checkpoint workflow for the RULE 11 gate.
- Five skills inspired by [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts):
  debugging, refactoring, security audit, MCP server design, agent skill design.
- Four prompt categories: devops-sre, meta-prompt-engineering,
  technical-writing, spec-driven-development.
- `prompts/` discovery and export across all eight platforms in `exporter.py`.

### Changed
- `orchestrator:plan`, `architect:design`, `implementer:build`/`:full`, and
  `quality:review` all wired into the spec-driven gate.

### Fixed
- Restored `prompts/`, which a deliberate reorganisation had dropped while
  `CLAUDE.md` still documented it as live.
- Stale skill, agent, and prompt counts across `README.md`,
  `agents/README.md`, and `tools/README.md`.

---

## [4.1.0] — 2026-06-09 → 2026-06-10

Documentation depth pass.

### Added
- Comprehensive function documentation with examples, guardrails, and error
  handling for all functions across agents, tools, and skills.
- MCP-style documentation format and a platform-specific masters strategy.
- Exporter analysis against DeployHQ best practices.

### Notes
The reference documents produced in this release
(`AGENTS_FUNCTIONS_VERIFIED.md`, `SKILLS_REFERENCE_VERIFIED.md`,
`TOOLS_FUNCTIONS_VERIFIED.md`) were superseded in `5.1.0` and now live under
`docs/99-archive/superseded/`.

---

## [4.0.0] — 2026-06-01 → 2026-06-04

The consolidation. Thirteen agents became five.

### Added
- **Function dispatch** — `agent:function` syntax, replacing whole-agent
  invocation with fine-grained calls.
- `orchestrator:ideate` and `orchestrator:solve`, with three reusable modules:
  `ideation_engine`, `design_solver`, `expert_panel_generator`.
- `quality:batch-review` — multi-PR review with a tabbed HTML report.
- `quality:diagnose` — conversational problem solving.
- `ba:create` — plain-text requirements to JIRA issues with BDD acceptance
  criteria.
- Export manifest tracking, for automatic cleanup of superseded exports.
- A repository analysis system: graph services, code analysers, C4 diagram and
  HTML site generation, incremental caching.

### Changed
- **Architecture v2.0 → v3.0.** Thirteen specialised agents consolidated into
  four role-based agents plus one utility agent, eliminating role overlap.
  `implementer:full` introduced to run build → test → doc in a single context
  window, removing state-transfer loss.
- Repository restructured to a three-tier layout.
- `token-optimizer` renamed `token_optimizer` for importability.
- `AP:` vendor prefix added to agent names for multi-vendor distinction.

### Removed
- Generated IDE export folders from git tracking; only `.claude` retained.

---

## [3.5.0] — 2026-05-25 → 2026-05-27

Specialist agents, hooks, and the instruction framework.

### Added
- **Code Review Agent v3** — requirement-driven, six-phase analysis pipeline,
  HTML report generator, MR comment formatter.
- **Hook exporter** — hook discovery, `HookFile` parsing, per-platform hook
  output directories, auto-generated platform configs with hook registration,
  and a `--hooks` CLI filter. Sample hooks: promptshield, test-runner,
  format-check.
- **Nine specialist agents**: codebase auditor, production debugger,
  performance optimizer, architecture refactorer, backend systems architect,
  senior frontend engineer, technical lead, security auditor, and an
  engineering team coordinator.
- **`token_optimizer`** — a Python library for intelligent query analysis:
  multi-dimensional scoring, web-search detection, intent classification,
  token estimation, and routing recommendations.
- **Centralised instructions framework** — YAML+Markdown hybrid parser,
  hierarchical loader, middleware pipeline (validation, dependency resolution
  with topological sort, conflict detection, precedence, provider filtering),
  and a plugin system.

---

## [3.0.0] — 2026-05-20

The autonomous developer system.

### Added
- Requirement parser with markdown generation, accepting free text, JIRA, or
  files.
- Project detector distinguishing new from existing projects.
- Context builder producing `context.json`, `architecture.md`, `tech-stack.md`,
  and an interactive `design.html`.
- Task generator for bite-sized task specifications.
- Generation skills for database schema, backend API, frontend UI, and testing.
- Autonomous developer agent orchestrating the full pipeline.
- Test case generator agent and the code documentation skill.
- Technical documentation agent.
- Graphify knowledge-graph integrator, GitHub sync for PR creation, and a task
  completion tracker.

### Changed
- Exporter now creates folders and copies files into a target project
  directory; cross-platform Python detection; interactive skill selection.

---

## [2.0.0] — 2026-04-14 → 2026-04-15

The unified exporter.

### Added
- `BaseFile` parser, `SkillFile` and `AgentFile` data models, `ExportResult`,
  and the `PlatformExporter` abstract base.
- Export to eight platforms: Claude, Copilot, Cursor, Windsurf, Gemini,
  Continue, OpenAI, Aider.

### Changed
- Replaced `skill_exporter` with the unified exporter, covering skills and
  agents in one tool. 79 tests passing.

---

## [1.0.0] — 2025-12-11 → 2026-04-03

Origins. A collection of prompt templates that grew into a skill library.

### Added
- Prompt templates for user stories, email writing, code review, testing,
  codebase analysis, incident management, and reporting.
- Eight foundational skills covering Apache Camel, Spring, Java, logging, and
  observability.
- The first `master_instruction_set.md`.

---

## Version Map

For anyone cross-referencing older documents, which may cite either scheme:

| This changelog | Repo version claimed at the time | Architecture version | Instruction set |
|---|---|---|---|
| 5.1.0 | — | v3.2 | v2.2 |
| 5.0.0 | — | v3.2 | v2.2 |
| 4.2.0 | — | v3.1 | v2.1 |
| 4.1.0 | — | v3.1 | v2.0 |
| 4.0.0 | — | v3.0 | v2.0 |
| 3.5.0 | v4.2.0 | v1.0 | v1.0 |
| 3.0.0 | v4.0.0 – v4.1.0 | v1.0 | v1.0 |
| 2.0.0 | v3.0.0 | — | v1.0 |
| 1.0.0 | — | — | — |
