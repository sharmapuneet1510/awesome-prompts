---
type: regex
target: last_message
pattern: 'all (\d+ )?(tests )?pass|all passed'
flags: i
match: not_contains
---
