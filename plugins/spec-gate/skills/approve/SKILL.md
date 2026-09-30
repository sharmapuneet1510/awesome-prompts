---
name: approve
description: Approve a spec file or ADR so spec-gate records it — typed by the user after reviewing the file
argument-hint: <specs/<feature>/requirements.md|design.md|tasks.md | docs/adr/ADR-NNNN-*.md>
disable-model-invocation: true
---

The spec-gate hook handled this command before you saw it and added its result
to your context, in a line that starts with `spec-gate:`. Tell the user that
result in one sentence. Do not edit the file and do not write an approval
marker yourself: only the hook records approvals. If there is no such line, spec-gate is not active in this project (no
`.spec-gate.json`): tell the user that, and do nothing else.
