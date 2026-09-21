# NEMESIS — Adversarial Validation Mode (Prompt Layer) — Design Specification

**Date:** September 21, 2026
**Status:** Approved 2026-09-21 (the user's "looks good" on the written spec). Implemented on branch `feat/nemesis`. Refinements made while implementing (ordered verdict rules, a refusal writes nothing, the `change` header key and target-type list, the release persona) were ruled by the controller and await the user's confirmation; D4 and D8-D10 in the Decisions table record them.
**Version:** 1.0
**Source requirement:** [`nemisis_requirement.md`](../../../nemisis_requirement.md) (36 sections, supplied by the user)

Claims carry the RULE 12 labels: **FACT** (verified, sourced), **INFERENCE** (reasoned, not measured), **PROPOSAL** (awaiting approval), **DECISION** (approved by the user).

---

## Executive Summary

Add **NEMESIS**, an *adversarial execution mode*, to this prompt-layer library. Given any derived conclusion (a PR approval, an ADR, a test result, a release decision, an RCA, …) NEMESIS assumes the conclusion may be wrong and tries to prove it wrong with evidence: it writes the opposite hypothesis first, investigates independently of the original agent, hunts for counterexamples, grades the evidence, and returns a structured verdict. It may equally conclude that the original **survived**, and it must never invent a defect to justify being activated.

Delivered as: one shared behaviour skill (`nemesis_skill.md`), one dispatchable function (`orchestrator:nemesis`) that composes an existing specialist persona with that skill, a report and audit-record format, an optional `nemesis.yml` policy file, three opt-in policy-gate steps in existing functions, worked examples, docs, and contract tests.

NEMESIS is a **mode**, not a new agent: `Architect + NEMESIS = NEMESIS Architect`.

---

## Problem Statement

- Agents in this repo produce conclusions (`quality:review` PASS, `architect:adr`, `quality:qa` results) that downstream steps trust. **FACT:** none of the 42 existing functions is tasked with attacking a finished conclusion; `quality:observe` compares artefacts and "never scores" (`docs/02-reference/functions.md`).
- A second reviewer of the same kind tends to confirm the first (shared framing, shared evidence, shared summary). The Tenth Man idea is to give one party the explicit job of disagreeing. **INFERENCE** (the requirement's premise; not measured here).
- The requirement also asks for platform pieces (UI button, progress view, workforce-floor card, MCP servers). **FACT:** this repository contains prompts, skills, agent definitions and Python tools, and no UI or MCP runtime. Those pieces are out of scope here and are documented as contracts.

---

## What the source requirement asks for, and where it lands

| Source § | Topic | Covered by |
|---|---|---|
| 1–2, 22, 33, 36 | purpose, philosophy, never fabricate, base persona, product line | skill (persona text, no-fabrication rule) — N1, N7, N9 |
| 3, 6, 7, 34, 35 | execution mode, dynamic persona composition | function + domain table — N1, N3 |
| 4, 23 | invocation, lifecycle | function — N2, N4 |
| 5 | supported targets | domain table — N3 |
| 8 | independent context | function isolation contract — N5 |
| 9, 10 | reverse hypothesis, challenge plan | skill + function — N4 |
| 11, 12 | independent evidence, MCP, read-only | function — N6 |
| 13–16 | requirement attack, counterexamples, evidence challenge, false confidence | skill — N7, N8 |
| 17–20 | categories, severity, confidence, verdicts | skill + contract test — N7, N9 |
| 21, 22 | example verdicts | worked examples — N14 |
| 24, 28 | workflow integration, return to work | function routing — N13 |
| 25, 26 | triggers, agent-to-agent | config + policy gates — N12 |
| 27 | NEMESIS against NEMESIS, depth limit | function — N13 |
| 29 | audit trail | report header — N11 |
| 30–32 | UI, workforce floor, status vocabulary | **out of scope**; the vocabulary strings are defined in the skill for platforms to reuse — N2 |
| new (user, 2026-09-21) | verdict carries hypotheses of failure cause | skill + report — N10 |

---

## Requirements

| ID | Requirement |
|---|---|
| **N1** | **A mode, not an agent.** NEMESIS adds no new agent. The effective persona is composed as *base specialist persona + domain skills + the NEMESIS behaviour skill + target context + evidence*. |
| **N2** | **Entry points.** `orchestrator:nemesis target=<id\|path>` and the alias `/nemesis <id>`. On activation it prints `NEMESIS ACTIVATED`. The skill defines the status vocabulary of §32 (`NEMESIS IS CHALLENGING THE CONCLUSION`, `COUNTEREXAMPLE DETECTED`, `CONCLUSION COMPROMISED`, `NEMESIS SURVIVED`, `NEMESIS DEFEATED THE CONCLUSION`) for platform UIs to reuse. |
| **N3** | **Target and persona resolution.** The function resolves the target to five things (artefact, original conclusion, original verdict, evidence references, identifiers), determines its domain, and selects the persona and skills from a table that names only existing agents and functions. An ambiguous target is asked about once. |
| **N4** | **Reverse hypothesis first.** Before any investigation NEMESIS writes the opposing hypothesis and a domain-specific challenge plan. The reverse hypothesis is a starting point, not a verdict. |
| **N5** | **Independence.** The challenge runs in a fresh sub-agent that receives only the five inputs of N3, never the original agent's reasoning. Where the host cannot spawn one, a clean-room pass runs in the same context. Either way the report records `context_isolated` truthfully. |
| **N6** | **Read-only and source-first.** Access is read-only by default. The only file NEMESIS writes is its own report. It inspects source systems (git, Jira export, CI output, test results) directly rather than trusting another agent's summary, requests the MCP roles it needs, and falls back to git and files when a role is unavailable. |
| **N7** | **Findings.** Every finding traces to a requirement, acceptance criterion, design constraint, risk, expected behaviour, evidence item or system invariant. Each has a category (17, §17), a severity (5) and a confidence (5) recorded as **separate** fields. A `SPECULATIVE` finding can never by itself raise the verdict above SURVIVED WITH CONDITIONS. |
| **N8** | **Evidence and confidence.** NEMESIS challenges the evidence used to approve, grading each item STRONG, PARTIAL, WEAK, MISSING, IRRELEVANT or CONTRADICTORY, and treats absolute claims ("no issues", "fully tested", "safe to release") as triggers for a higher evidence bar. |
| **N9** | **Verdict.** Exactly one of SURVIVED, SURVIVED WITH CONDITIONS, CHALLENGED, DEFEATED, INSUFFICIENT EVIDENCE, chosen by the rules in *Design §4*. A SURVIVED report states the challenge paths executed and does not invent findings. |
| **N10** | **Failure-cause hypotheses.** The verdict carries ranked hypotheses of *why* — the defect cause and the miss cause (why the original conclusion did not catch it) — each with a cause class, mechanism, the findings it explains, a confidence, and a **discriminating check** (*Design §5*). They are labelled INFERENCE, never fact. |
| **N11** | **Report and audit record.** Every activation writes `docs/nemesis/NMS-<year>-<seq>.md` in the downstream project, with the machine-readable header of *Design §6* (which contains the §29 audit fields). |
| **N12** | **Config and triggers.** `docs/nemesis/nemesis.yml` holds `enabled`, `default_trigger`, `auto_activate`, `context_isolation`, `independent_source_validation`, `default_access`, `maximum_depth`. Triggers: manual (default), workflow, policy, agent. With no `nemesis.yml`, NEMESIS is manual-only and nothing activates automatically. Policy activation is an opt-in step in `quality:review`, `architect:adr` and `orchestrator:pr`. |
| **N13** | **Routing and recursion.** DEFEATED or CHALLENGED routes back to the specialist that owns the work, with the whole report (hypotheses first) as task context; SURVIVED lets the workflow continue. A NEMESIS verdict may itself be challenged; `maximum_depth` (default 2) bounds it and a further activation is refused. |
| **N14** | **Docs, examples, tests.** Registration in the reference docs, README and `CLAUDE.md` counts, `agents/README.md`, the orchestrator function table, the CHANGELOG; a workflow doc; two worked example reports; a contract test that pins the enumerations and validates the examples against the verdict rules. |

**Non-goals.** The ACTIVATE button, progress UI and workforce-floor rendering; real MCP servers; technical enforcement of read-only access or isolation (a prompt cannot enforce either; see N5, N6 and *Risks*); changing any existing verdict scale.

---

## Design

### 1. Artifacts (all in this repo)

| File | Purpose |
|---|---|
| `skills/nemesis_skill.md` | The shared behaviour: reverse hypothesis, challenge plans by domain, requirement-by-requirement attack, counterexamples, evidence classes, false-confidence triggers, the 17 categories, severity and confidence, verdict rules, cause classes, no-fabrication rule, base persona text, status vocabulary. |
| `agents/orchestrator/functions/nemesis.md` | `orchestrator:nemesis`: input spec, the lifecycle of §2, the domain→persona table of §3, the isolation contract, routing and recursion. |
| `docs/04-examples/nemesis-config.example.yml` (the template for a project's `docs/nemesis/nemesis.yml`) | The N12 keys with their defaults. |
| Report template (inside the skill) | The header and section layout of §6. |
| `docs/04-examples/nemesis-*.md` (two) | A DEFEATED and a SURVIVED worked report. |
| `docs/01-workflows/15-challenge-a-conclusion.md` | The user-facing workflow. |
| `tests/nemesis/` (six modules: skill, function, gates, examples, registration, traceability) | The contract tests of *Testing and Traceability*. |

### 2. Lifecycle (`orchestrator:nemesis`)

1. **Resolve the target** (N3).
2. **Select the persona** from the domain table.
3. **Isolate** (N5): spawn a fresh sub-agent with the five inputs, or fall back and record it.
4. **Reverse hypothesis and challenge plan** (N4).
5. **Collect independent evidence** from the sources (N6).
6. **Attack requirement by requirement; generate counterexamples** (N7).
7. **Challenge the evidence** (N8).
8. **Form failure-cause hypotheses** (N10) and **choose the verdict** (§4).
9. **Write the report** (N11) and **route** (N13).
10. **Terminate**: the NEMESIS specialist exists only for the challenge.

### 3. Domain → persona (PROPOSAL; only existing agents and functions)

| Target | Persona (agent:function) |
|---|---|
| Requirements analysis, Jira acceptance | `business_analyst` (`ba:trace`, `ba:clarify`) |
| Architecture, ADR, technical, API and data design | `architect` (`design`, `adr`, `api`, `schema`) |
| Code, PR approval, code review, security review | `quality` (`review`, `security`) |
| API, UI and automation test results, test strategy, regression, evidence pack | `quality` (`qa`, `observe`) |
| Release approval, deployment readiness | `quality` (`observe`), `orchestrator` (`risk`) |
| RCA, production incident conclusions | `quality` (`debug`, `diagnose`) |
| Documentation | `implementer` (`doc`) |
| Compliance, risk, performance assessment | `quality` (`security`, `perf`) |
| Agent- or human-generated recommendation or decision | `orchestrator` (`review`, `tradeoff`, `risk`) |

### 4. Verdict rules (PROPOSAL — the requirement leaves them to judgement; tune on real reports)

The rules are **ordered: the first that matches decides**, so every set of findings has exactly one verdict. *Counting findings* are those whose confidence is not `DISPROVEN` (a disproven finding is a challenge path that was tried and failed; it is recorded but does not count).

| Order | Verdict | When |
|---|---|---|
| 1 | **DEFEATED** | A counting finding at HIGH or CRITICAL severity with CONFIRMED or HIGH_CONFIDENCE confidence that is *backed*: it carries a counterexample, or its category is `CONTRADICTORY_EVIDENCE`. |
| 2 | **INSUFFICIENT EVIDENCE** | Not defeated, and every counting non-`SPECULATIVE` HIGH or CRITICAL finding has category `EVIDENCE_GAP`: the conclusion cannot be verified either way. (If nothing could be verified, that is recorded as a HIGH `EVIDENCE_GAP` finding.) |
| 3 | **CHALLENGED** | A counting non-`SPECULATIVE` HIGH or CRITICAL finding (for example CONFIRMED without a counterexample, or PLAUSIBLE), or two or more counting non-`SPECULATIVE` MEDIUM findings. |
| 4 | **SURVIVED WITH CONDITIONS** | Any other counting finding (LOW or INFORMATIONAL findings, at most one non-speculative MEDIUM, any `SPECULATIVE` finding), plus stated assumptions. |
| 5 | **SURVIVED** | No counting findings; the challenge paths executed are listed. |

A `SPECULATIVE` finding never counts toward rules 2 and 3, which is how it is kept from raising the verdict above SURVIVED WITH CONDITIONS (N7). *Refinement of 2026-09-21:* the first draft of this table was not total (a CRITICAL finding without a counterexample, or a single MEDIUM finding, had no verdict) and contradicted the speculative cap; the final task review found it and the ordered form above replaces it.

### 5. Failure-cause hypotheses (N10)

A finding says *what* is wrong; a hypothesis says *why*. Two layers: **defect cause** (why the defect exists) and **miss cause** (why the original conclusion did not catch it).

Each hypothesis has: `id`, `layer` (defect | miss), `statement`, `mechanism` (a short causal chain), `explains` (finding ids), `cause_class`, `confidence` (same scale as findings), `rank`, and `discriminating_check` (the cheapest test, query or read that would confirm or refute it).

`cause_class` is one of: `REQUIREMENT_MISUNDERSTOOD`, `ASSUMPTION_UNTESTED`, `EVIDENCE_INADEQUATE`, `CHECK_SCOPE_TOO_NARROW`, `DESIGN_FLAW`, `IMPLEMENTATION_SLIP`, `INTEGRATION_MISMATCH`, `ENVIRONMENT_DIFFERENCE`, `PROCESS_GAP`, `FALSE_CONFIDENCE`.

By verdict: **DEFEATED / CHALLENGED** — required and ranked; the owning specialist starts from the top hypothesis and runs its discriminating check. **INSUFFICIENT EVIDENCE** — why the evidence is missing. **SURVIVED / SURVIVED WITH CONDITIONS** — the conditions under which the conclusion would fail; may be empty and is never padded.

### 6. Report and audit record (N11)

`docs/nemesis/NMS-<year>-<seq>.md`, sequence = highest existing for that year + 1, five digits, restarting each year. YAML header (`target.type` is one of `requirement`, `architecture`, `adr`, `pull_request`, `code_review`, `security_review`, `test_result`, `release`, `rca`, `documentation`, `assessment`, `recommendation`; the `findings` counts count only findings that are not `DISPROVEN`):

```yaml
nemesis_id: NMS-2026-00982
created: 2026-09-21
target: {type: pull_request, id: PR-1839}
change: JIRA-4821          # the stable work item; stays the same across re-reviews
original_agent: CodeReviewer-04
original_verdict: PASS
nemesis_persona: NEMESIS_CODE_REVIEWER
verdict: DEFEATED
findings: {critical: 1, high: 1, medium: 2, low: 0, informational: 0}
hypotheses: 3
sources: [JIRA-4821, PR-1839, TEST-RUN-774]
context_isolated: true
access: read_only
trigger: manual            # manual | workflow | policy | agent
depth: 1
parent_nemesis: null
```

Body, in order: **Verdict** → **Failure-cause hypotheses** → Original conclusion → Reverse hypothesis → Challenge paths executed → Findings (id, category, severity, confidence, traces-to, counterexample, impact, required action) → Evidence assessment → Required actions (ending "repeat the review, then re-run NEMESIS").

### 7. Config and triggers (N12)

`docs/nemesis/nemesis.yml`, defaults from §25 of the source: `enabled: true`, `default_trigger: manual`, `auto_activate` (critical_change, production_release, architecture_change, security_change, regulatory_change, payment_change — all default `false` in the template), `context_isolation: true`, `independent_source_validation: true`, `default_access: read_only`, `maximum_depth: 2`. **PROPOSAL:** an optional `policy_match` block (Jira priorities, labels, path globs) tells the gate steps what "critical" or "payment" means for this project, because a prompt layer has no event bus.

Policy gates: after a PASS, `quality:review` (critical, security or payment change), `architect:adr` (before an ADR becomes Accepted) and `orchestrator:pr` (production release) read `nemesis.yml`; if it exists, is enabled, and a rule matches, they invoke `orchestrator:nemesis` and act on the verdict. Without the file they do nothing.

### 8. Isolation, read-only and their limits (N5, N6)

The function instructs the calling agent to hand the sub-agent only the five inputs, to give it read-only tools, and to write only the report. **INFERENCE:** none of this is technically enforced by a prompt; a sub-agent could still be given the wrong context. The report therefore records what actually happened (`context_isolated`, `access`, `sources`) so a reader can judge the challenge, and the fallback path is labelled in the verdict text.

### 9. Recursion (N13)

Depth counts nesting: the original challenge is depth 1, a challenge of that verdict is depth 2. `maximum_depth` defaults to 2; a request beyond it is refused: the response says which limit was hit and which parent, and nothing is written (a refusal is not an activation, so it has no audit record, and the report stays the only write). Depth is the parent's `depth` plus 1, or 1 with no parent; a re-run after a fix is a new depth-1 challenge of the fixed artefact.

---

## Testing and Traceability

The tests check the contract text against the repository, since a prompt layer has no runtime to unit-test.

| Test | Proves | Reqs |
|---|---|---|
| Enumerations | the skill lists exactly the 17 categories, 5 severities, 5 confidence levels, 5 verdicts, 6 evidence classes and the cause classes of §5 | N7 N8 N9 N10 |
| Lifecycle | the function's steps appear in the order of §2 and it states read-only, depth 2 and the isolation fallback | N4 N5 N6 N13 |
| Domain table | every persona names an agent and function file that exists | N3 |
| Config | the example `nemesis.yml` parses and has the N12 keys and defaults | N12 |
| Policy gates | the three functions each contain the gate step and mention `nemesis.yml` | N12 |
| Worked examples | each parses; header keys and sections present in order; the verdict is consistent with the §4 rules (DEFEATED has a HIGH+ finding at CONFIRMED/HIGH_CONFIDENCE with a counterexample; SURVIVED has no findings); every hypothesis has a discriminating check | N9 N10 N11 |
| Registration | the counts in README, `CLAUDE.md` and the reference docs agree and the exporter lists the new skill | N14 |

Each test module declares `COVERS = ["N…"]`, and a traceability test fails if a requirement loses coverage (the pattern used by Prompt Preflight).

---

## Decisions (RULE 11a — contract, dependency, failure mode)

| ID | Decision | Alternatives rejected | Status |
|---|---|---|---|
| D1 | Prompt layer only; no Python runtime, no UI. | + a reference runtime; spec-only | approved in chat, 2026-09-21 |
| D2 | One `orchestrator:nemesis` function plus a shared skill. | `mode=nemesis` on every function (touches all five agents); `quality:nemesis` only (second-class for non-QA targets) | approved in chat, 2026-09-21 |
| D3 | Isolate when the host can, record the truth, fall back visibly. | require isolation (unusable without sub-agents); never isolate | approved in chat, 2026-09-21 |
| D4 | Verdict rules of §4, implemented as ordered rules (first match wins) so exactly one verdict applies to any finding set; lower findings always stay in the report. | none proposed by the source; unordered rules (found not to be exclusive) | **Accepted** (approved in chat, refined during implementation — controller ruling, pending the user's confirmation) |
| D5 | Failure-cause hypotheses, two layers, with discriminating checks. | findings only | approved in chat, 2026-09-21 |
| D8 | A refusal (depth limit, disabled config) writes nothing; the report is the only write. | a refusal note file | controller ruling, pending the user's confirmation |
| D9 | Reports carry a stable `change` header key (Jira key, else the first target's id; a re-review inherits it) and a pinned `target.type` list; gates count blocking results by `change`. | counting by `target` (changes every re-review, so the guard never fires) | controller ruling, pending the user's confirmation |
| D10 | The release persona is `quality:observe` plus `orchestrator:risk`. | `implementer:pipeline` (builds pipelines, does not assess readiness) | controller ruling, pending the user's confirmation |
| D6 | Reports live downstream in `docs/nemesis/`, never in this repo. | store in this repo | **Accepted** (approved with the plan, 2026-09-21) |
| D7 | Policy activation as opt-in steps in three existing functions, driven by `nemesis.yml`. | a new event mechanism (none exists); no automation | approved in chat, 2026-09-21 |

---

## Risks and Open Questions

| ID | Item | Mitigation |
|---|---|---|
| R1 | Isolation and read-only cannot be enforced by a prompt. | Record what happened; label fallback runs; say so in the docs. |
| R2 | The adversarial framing can manufacture defects. | The no-fabrication rule, evidence and counterexample requirements, the SURVIVED verdict, the speculative-finding cap, worked SURVIVED example. |
| R3 | Cost: a sub-agent per activation; automatic triggers multiply it. | Manual by default; automation only via an explicit `nemesis.yml`. |
| R4 | The §4 verdict thresholds may be miscalibrated. | PROPOSAL; revisit after real reports. |
| R5 | The three gate steps edit files governed by RULE 11 (agent functions). | Each is a one-paragraph, opt-in step; `nemesis.yml` absent means no behaviour change; reviewed as part of the plan. |
| O1 | Which hosts can spawn a sub-agent. Claude Code can; other exported platforms may not. | The fallback path (D3). |
| O2 | What counts as a "critical", "payment" or "regulatory" change for a given project. | The optional `policy_match` block (§7); default all `auto_activate` rules off. |

---

## Task Outline (the plan will detail each)

0. Commit the source requirement (`nemisis_requirement.md`) with this spec.
1. `nemesis_skill.md` and the enumeration and lifecycle contract tests.
2. `orchestrator:nemesis`, the domain table, `nemesis.yml` template, report template, config and domain-table tests.
3. The three opt-in policy-gate steps and their tests.
4. Worked examples, workflow doc, registration, counts, exporter check, registration tests.
5. Full verification and a final review.

---

## Governance and Scope

- **RULE 11.** This spec and the plan that follows are this repository's own design records, in `docs/superpowers/`, following the precedent of the Prompt Preflight spec. No feature file is written until the user approves this spec and the plan.
- **RULE 11a / 12.** D1–D3, D5 and D7 were agreed in chat on 2026-09-21; D4 and D6 are proposals awaiting approval with this spec.
- **Branching.** Work happens on a new branch from `main` (or the user's chosen base), never on `main`.
- **Out of scope, tracked separately:** the platform UI, MCP servers and workforce-floor rendering.

---

## Sources

- `nemisis_requirement.md` — the user's requirement, 36 sections.
- This repository: `agents/*/functions/`, `docs/02-reference/functions.md`, `skills/`, and the Prompt Preflight spec at `docs/superpowers/specs/2026-09-20-prompt-preflight-hook-design.md` for structure and conventions.
