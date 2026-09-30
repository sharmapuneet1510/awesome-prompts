---
type: regex
target: { source: file, path: specs/checkout/tasks.md }
pattern: 'Status\W*Approved'
flags: i
match: not_contains
---
