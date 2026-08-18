---
name: implementer:build Function
description: Code generation from specifications, architecture, or requirements
prefix: implementer:build
version: 3.0
---

# implementer:build

**Generate production-ready code** from specifications, architecture documents, or requirements.

## Inputs

```
implementer:build path="..." [tech_stack="..."]
```

- `path` (string, required) — Path to spec, design, or requirements file
- `tech_stack` (string, optional) — Target tech (Java, Python, React, Node.js, etc.)
- `style` (string, optional) — Code style (conventional, google, airbnb)

## Outputs

```
✓ src/                        — Generated source code
✓ ARCHITECTURE.md             — Code structure documentation
✓ BUILD.md                    — Build and deployment guide
```

## Example

```bash
implementer:build path=./api-spec.yaml [tech_stack="Python, FastAPI"]
```

**Output:**
- FastAPI routes with type hints
- Pydantic models
- Docstrings
- Error handling

## Gate — Approved Spec Only (RULE 11 / 11a)

Run these checks **before** generating any code. Each failure is a refusal
with a named next step, not a warning to proceed past.

| Check | Refuse when | Next step |
|---|---|---|
| Spec chain | `specs/<feature>/tasks.md` is missing or not `Status: Approved` | `orchestrator:plan` → `architect:design` |
| ADR gate | The change alters a contract, data shape, dependency, or failure mode and no Accepted ADR cites its Parent Jira | `architect:adr` |
| Traceability | `ba:trace` reports a High finding on T-1, T-2, T-10, or T-13 | Resolve the finding |
| Scope | A task has no `REQ-n` citation | `orchestrator:plan` |

Implement **only** what the approved tasks and Accepted ADRs describe. Work
not traceable to a requirement is scope creep, and `quality:observe` will
report it as such.

Trivial work — one-line fixes, config tweaks, small doc edits — is exempt per
RULE 11.

## Workflow

0. Run the gate above. Refuse if any check fails.
1. Parse specification/design
2. Read `docs/adr/` for Accepted decisions constraining this area, and
   `docs/project-context/` for invariants and known behaviours
3. Detect or use specified tech stack
4. Generate code structure
5. Implement functions/classes — honouring every Accepted ADR; contradicting
   one requires `architect:adr` to supersede it first
6. Add error handling
7. Generate documentation
8. Create build configuration
9. Update `docs/project-context/dependencies.md` if dependencies changed

## Related Functions

- `implementer:full` — Build + test + doc in one pass
- `implementer:test` — Test generation
- `implementer:doc` — Documentation generation
- `architect:design` — System design (input)
- `architect:adr` — Required before decision-bearing changes
- `ba:trace` — Gate checks

## Related Skills

- `skills/spec_driven_development_skill.md` · `skills/adr_skill.md`
- `skills/traceability_skill.md` · `skills/project_context_skill.md`
