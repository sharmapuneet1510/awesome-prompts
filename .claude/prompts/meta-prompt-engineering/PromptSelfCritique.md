# Prompt Self-Critique

## Context
You've drafted a prompt (agent instruction, skill, or template) and want to check it for ambiguity, missing constraints, or unverifiable success criteria before it goes into use.

## Requirements
- Check for underspecified terms — any word a reasonable reader could interpret two different ways.
- Check that success criteria are checkable from the output alone, not requiring the author's intent.
- Check that constraints (format, scope, what NOT to do) are as explicit as the positive instructions.
- Check for missing context a fresh reader would need (what system is this for, what's out of scope).

## Approach
1. Read the prompt as if you've never seen the task it's for.
2. For each instruction, ask: "could two competent people follow this and produce meaningfully different results?" If yes, tighten it.
3. For each success criterion, ask: "could I verify this was met just by looking at the output?" If no, rewrite it to be checkable.
4. List every ambiguity found, with the specific fix, rather than a vague "could be clearer."

## Skills Referenced
- `agent_skill_design_skill.md` (when a prompt should become a reusable skill instead)

## Expected Output
A list of concrete ambiguities/gaps, each with: the problematic phrase, why it's ambiguous, and the specific rewrite.

## Success Criteria
- Every flagged issue names the exact phrase, not a general area.
- Every fix is a concrete rewrite, not "add more detail."
- Re-reading the revised prompt, a fresh reader could execute it without needing to ask a clarifying question that the original prompt should have answered.
