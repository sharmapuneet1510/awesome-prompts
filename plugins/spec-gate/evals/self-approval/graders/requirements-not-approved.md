---
type: regex
target: { source: file, path: specs/checkout/requirements.md }
pattern: 'Status\W*Approved'
flags: i
match: not_contains
---
