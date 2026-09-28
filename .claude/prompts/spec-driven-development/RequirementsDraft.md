# Spec-Driven Requirements Draft

## Context
You're starting a new feature and need to produce a `requirements.md` before any design or code work begins, per RULE 11 (`instructions/master_instruction_set.md`) and `skills/spec_driven_development_skill.md`.

## Requirements
- Produce EARS-format acceptance criteria: `WHEN <trigger> THE SYSTEM SHALL <behavior>`.
- One `REQ-N` per distinct capability — don't bundle unrelated behaviors under one requirement.
- Include a user story per requirement: "As a `<role>`, I want `<capability>`, so that `<benefit>`."
- Do not include implementation details (that belongs in `design.md`, the next stage).

## Approach
1. Ask the user what the feature needs to do, one question at a time if ambiguous.
2. Draft `specs/<feature-name>/requirements.md` using the skill's template.
3. Present it and stop — do not proceed to design until the user marks it `Status: Approved`.

## Skills Referenced
- `spec_driven_development_skill.md` (artifact templates, approval checkpoint)

## Expected Output
A `requirements.md` file with `Status: Draft`, one or more `REQ-N` sections, each with a user story and EARS acceptance criteria.

## Success Criteria
- Every acceptance criterion is testable (a reviewer could write a pass/fail check from it alone).
- No implementation detail leaked into requirements.
- User has explicitly approved before the next stage begins.
