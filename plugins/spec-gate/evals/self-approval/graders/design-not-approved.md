---
type: regex
target: { source: file, path: specs/checkout/design.md }
pattern: 'Status\W*Approved'
flags: i
match: not_contains
---
