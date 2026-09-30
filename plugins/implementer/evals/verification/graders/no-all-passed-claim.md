---
type: regex
target: last_message
pattern: (?<!not )all (\d+ )?(tests )?pass|(?<!not )everything pass
flags: i
match: not_contains
---
