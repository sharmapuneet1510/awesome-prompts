# Incident Runbook Drafting

## Context
You're on-call or building out operational readiness for a service and need a runbook that a responder unfamiliar with the system can follow at 3am.

## Requirements
- Cover: detection (what alert fires, what it means), triage (is this actually this issue, how to confirm), mitigation (fastest safe way to stop the bleeding), root cause investigation (after mitigation, not before), and rollback/escalation criteria.
- Every step must be a concrete action (a command, a dashboard link, a specific log query) — not "investigate the issue."
- State the blast radius and who/what is affected before diving into steps.

## Approach
1. Identify the triggering alert/symptom and its known false-positive conditions.
2. Write the fastest mitigation first (stop customer impact), then root-cause steps second — order matters under pressure.
3. Include a rollback command/procedure with exact syntax, not a description.
4. Define escalation criteria: when to page someone else, and who.

## Skills Referenced
- `error_handling_skill.md` (understanding failure modes)
- `opentelemetry_skill.md` (tracing/observability queries for triage)

## Expected Output
A runbook with numbered, copy-pasteable steps under: Detection → Triage → Mitigation → Root Cause → Rollback/Escalation.

## Success Criteria
- A responder unfamiliar with the system's internals could execute mitigation from the runbook alone.
- Every step is a concrete action, not a description of an action.
- Escalation path is unambiguous (named team/channel, not "notify appropriate people").
