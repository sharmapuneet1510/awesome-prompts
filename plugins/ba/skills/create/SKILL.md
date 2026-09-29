---
name: create
description: Parse a plain-text requirements file into Jira issues with BDD acceptance criteria, plus HTML requirement cards
argument-hint: path=./requirements.txt
disable-model-invocation: true
---

Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md for the sections this function needs.

# ba:create

Turns a plain-text requirements file into structured Jira issues with
Given/When/Then acceptance criteria, and renders them as HTML requirement cards.

## Inputs

```
ba:create path=./requirements.txt
```

- `path` (string, required) — the requirements file (plain text, Markdown, or one requirement per line)

## Outputs

```
✓ requirements.json            — Jira-ready issues with BDD acceptance criteria
✓ requirements-cards.html      — one card per requirement
```

## Workflow

Follow ba_create_skill (`engineering-skills:ba-create` skill): detect the input
format, extract requirements, write acceptance criteria that a test can assert,
and render the cards. Ask about any requirement that has no testable outcome
instead of inventing one.
