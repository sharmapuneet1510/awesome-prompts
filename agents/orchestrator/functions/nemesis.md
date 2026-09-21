---
name: orchestrator:nemesis Function
version: 1.0
description: Attack an existing conclusion before it is trusted — compose a specialist persona with NEMESIS, investigate independently, return a verdict with ranked hypotheses of why it failed
prefix: orchestrator:nemesis
---

# Function: orchestrator:nemesis

**Prefix:** `orchestrator:nemesis` (alias `/nemesis <id>`)

**Purpose:** Assume a finished conclusion may be wrong and try to prove it wrong with evidence.
NEMESIS is an **execution mode**, not an agent: it turns the specialist that fits the target into an
opposing specialist (`Architect + NEMESIS = NEMESIS Architect`). It may just as well conclude that the
conclusion **survived**, and it never invents a defect.

**Skill:** [`nemesis_skill`](../../../skills/nemesis_skill.md) holds the behaviour, the enumerations and
the report format. This file holds the lifecycle, the persona table and the isolation contract.

## Input Specification

```yaml
# Required
target: string             # JIRA-4821 | PR-1839 | CR-839 | ADR-104 | API-TEST-2291 | RELEASE-RC-32 | a path

# Optional
persona: string?           # override the persona chosen from the domain table, e.g. quality:security
trigger: enum?             # manual (default) | workflow | policy | agent
parent: string?            # NMS id when this run challenges an earlier NEMESIS verdict
```

Invocations:

```text
orchestrator:nemesis target=PR-1839
/nemesis ADR-104
/nemesis RELEASE-RC-32 persona=quality:security
```

## Configuration

Read `docs/nemesis/nemesis.yml` in the project under review, if it exists. Without it NEMESIS is
manual-only, read-only, depth 2, and nothing activates automatically. Keys and defaults:
`enabled: true`, `default_trigger: manual`, `auto_activate` (all rules default off),
`context_isolation: true`, `independent_source_validation: true`, `default_access: read_only`,
`maximum_depth: 2`. An optional `policy_match` block (Jira priorities, labels, path globs) tells the
policy gates what "critical", "payment" or "regulatory" means for the project. If `enabled: false`,
refuse and say so.

## Process

Print `NEMESIS ACTIVATED`, then run the steps in this order.

### Step 1 — Resolve the target

Resolve `target` to five things and nothing more: the **artefact**, the **original conclusion**, the
**original verdict**, the **evidence references** and the **identifiers**. Recognise the type from the
id prefix or the file. If the target is ambiguous, ask once. If it has no conclusion to challenge
(a raw artefact nobody has judged), say so and stop.

### Step 2 — Select the persona

Determine the target's domain and pick the persona and skills from this table. Use only these
existing functions. A `persona=` override wins.

| Target | Persona (`agent:function`) | Skills to attach |
|---|---|---|
| Requirements analysis, Jira acceptance | `ba:trace`, `ba:clarify` | `traceability_skill` |
| Architecture, ADR, technical, API and data design | `architect:design`, `architect:adr`, `architect:api`, `architect:schema` | `adr_skill`, `oop_skill` |
| Code, PR approval, code review, security review | `quality:review`, `quality:security` | `code_review_skill`, `security_audit_skill` |
| API, UI and automation test results, test strategy, regression, evidence pack | `quality:qa`, `quality:observe` | `test_skill`, `traceability_skill` |
| Release approval, deployment readiness | `implementer:pipeline` | `debugging_skill`, `opentelemetry_skill` |
| RCA, production incident conclusions | `quality:debug`, `quality:diagnose` | `debugging_skill` |
| Documentation | `implementer:doc` | `code_documentation_skill` |
| Compliance, risk, performance assessment | `quality:security`, `quality:perf` | `security_audit_skill` |
| Agent- or human-generated recommendation or decision | `orchestrator:review`, `orchestrator:tradeoff`, `orchestrator:risk` | `adr_skill` |

Add the language skill that fits the code (`java_advanced_skill`, `python_advanced_skill`, …). The
effective persona is:

```text
Base persona + domain skills + nemesis_skill + target context + available evidence
+ MCP roles + challenge plan + platform guardrails = NEMESIS <SPECIALIST>
```

### Step 3 — Isolate

**Spawn a fresh sub-agent** for the challenge and give it only the five inputs of step 1, the
persona and skills of step 2, and the challenge instructions below. Never pass the original agent's
reasoning, drafts or scratch analysis. Give it read-only tools, plus permission to write only its
report file.

Sub-agent instruction:

```text
You are NEMESIS acting as <NEMESIS specialist>. Follow nemesis_skill.md.
Target: <id>.  Original conclusion: <conclusion>.  Original verdict: <verdict>.
Evidence references: <refs>.  Identifiers: <ids>.
Retrieve the source evidence yourself; do not trust summaries. You have read-only access.
Write only the report file <path>. Return the verdict and the report path.
```

**If the host cannot spawn a sub-agent**, run a *clean-room pass* in the calling context: set the
original agent's reasoning aside, work only from the five inputs and the sources, and state at the top
of the report and in the verdict text that isolation was not available. Either way record
`context_isolated: true|false` truthfully. Do not claim isolation that did not happen.

### Step 4 — Reverse hypothesis and challenge plan

Write the reverse hypothesis first, then the challenge plan for the domain (see the skill, §3–§4).

### Step 5 — Collect independent evidence

Inspect the source systems directly, read-only. Request these MCP roles when the target needs them
and fall back to git and files when a role is unavailable: `jira`, `git`, `ci_cd`, `test_management`,
`evidence_store`, `confluence`, `architecture_repository`, `observability`. Record the sources used.
A source that could not be reached is stated in the report, and anything that depends on it loses
confidence.

### Step 6 — Attack requirement by requirement; generate counterexamples

One finding per issue, each traced to a requirement, acceptance criterion, design constraint, risk,
expected behaviour, evidence item or invariant. Give every finding a category, a severity and a
confidence (separate fields). Write counterexamples as steps and say whether each was executed or
derived.

### Step 7 — Challenge the evidence

Grade each evidence item STRONG, PARTIAL, WEAK, MISSING, IRRELEVANT or CONTRADICTORY, and apply the
false-confidence signals.

### Step 8 — Failure-cause hypotheses and verdict

Form ranked hypotheses of why (defect layer and miss layer), each with a cause class, mechanism,
explained findings, confidence and a **discriminating check**. Then choose the verdict by the rules in
the skill (§10). Print the matching status string (`NEMESIS SURVIVED`, `NEMESIS DEFEATED THE
CONCLUSION`, …).

### Step 9 — Write the report and route

Write `docs/nemesis/NMS-<year>-<seq>.md` (create `docs/nemesis/` if needed; sequence = highest
existing plus one, five digits). This is the only write.

| Verdict | Route |
|---|---|
| `DEFEATED`, `CHALLENGED` | Return to the specialist that owns the work, with the **whole report as task context**, hypotheses first. That specialist starts from rank 1 and runs its discriminating check, fixes, is re-reviewed, and NEMESIS runs again. |
| `SURVIVED WITH CONDITIONS` | Continue the workflow; the conditions travel with it. |
| `SURVIVED` | Continue the workflow. |
| `INSUFFICIENT EVIDENCE` | Return to the owner with the list of evidence to obtain. |

### Step 10 — Terminate

The NEMESIS specialist exists only for the challenge. End the sub-agent and return control.

## Recursion

A NEMESIS verdict may itself be challenged (`parent=<NMS id>`). The original challenge is depth 1, a
challenge of it is depth 2. `maximum_depth` defaults to 2. A request beyond it is **refused**: write a
short refusal note naming the limit and the parent, and do not run.

## Triggers

| Trigger | How |
|---|---|
| `manual` | The user runs `orchestrator:nemesis` or `/nemesis`. Default. |
| `workflow` | A workflow step names it. |
| `policy` | `quality:review`, `architect:adr` and `orchestrator:pr` each contain an opt-in gate that reads `docs/nemesis/nemesis.yml` and invokes this function when a rule matches. |
| `agent` | Any function may request it; the depth limit still applies. |

## Refusals

- `enabled: false` in `docs/nemesis/nemesis.yml`.
- A request beyond `maximum_depth`.
- A target with no conclusion to challenge.
- A request to write anywhere but the NEMESIS report (NEMESIS is read-only).

## Example

```bash
orchestrator:nemesis target=CR-839
```

Result: `NEMESIS DEFEATED THE CONCLUSION` — the duplicate check ignores PROCESSING transactions, so two
concurrent requests can both pass. Ranked hypotheses point at the missing concurrent test (miss layer)
and the read-then-write check (defect layer); the report goes back to the developer. See the worked
examples in [`docs/04-examples/nemesis-defeated.md`](../../../docs/04-examples/nemesis-defeated.md) and
[`nemesis-survived.md`](../../../docs/04-examples/nemesis-survived.md).

## Related

- Skill: `nemesis_skill`
- Workflow: [15 — Challenge a conclusion](../../../docs/01-workflows/15-challenge-a-conclusion.md)
- Functions: `quality:review`, `architect:adr`, `orchestrator:pr` (policy gates)
