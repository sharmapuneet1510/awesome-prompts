---
name: status
description: Show which specs and ADRs spec-gate has recorded as approved, and whether gated edits are allowed
disable-model-invocation: true
---

The spec-gate hook added a status report to your context, starting with
`spec-gate status`. Show it to the user as it is. If there is no such report,
spec-gate is not active in this project (no `.spec-gate.json`): tell the user that.
