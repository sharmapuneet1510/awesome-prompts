---
name: trivial
description: Let one small change past the spec gate until the user's next message — typed by the user, with a reason
argument-hint: <reason>
disable-model-invocation: true
---

The spec-gate hook has opened a bypass for this turn only and logged the
reason; its result is in your context, in a line that starts with `spec-gate:`.
Make only the small change the user described. The bypass closes with the
user's next message. If there is no such line, spec-gate is not active in this project (no
`.spec-gate.json`): tell the user that, and do nothing else.
