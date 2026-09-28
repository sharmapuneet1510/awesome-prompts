# Plain-Language Technical Rewrite

## Context
You have technical documentation (API docs, a runbook, an architecture doc) written in dense jargon or passive voice, and need it rewritten for a reader who is technical but unfamiliar with this specific system.

## Requirements
- Active voice, short sentences (aim for one idea per sentence).
- Define any domain-specific term or acronym on first use.
- Preserve every technical fact and constraint exactly — this is a clarity rewrite, not a content change or a simplification that drops detail.
- Keep code samples, commands, and exact values unchanged verbatim.

## Approach
1. Read the source once fully before rewriting anything — a rewrite that starts sentence-by-sentence tends to lose the document's overall structure.
2. Rewrite passive constructions ("the request is processed by the handler") into active ones ("the handler processes the request").
3. Break up sentences with more than one clause carrying independent information.
4. Flag (don't silently drop) any sentence whose meaning was ambiguous even in the source — that's a content gap, not a writing-style issue, and needs the original author's input.

## Skills Referenced
- `code_documentation_skill.md` (docstring/comment conventions if the doc includes code)

## Expected Output
A rewritten document with the same structure and technical content, in active voice and shorter sentences, with a short list of any ambiguous source passages flagged separately.

## Success Criteria
- No technical fact, constraint, or exact value changed from the source.
- Passive voice eliminated except where genuinely clearer (rare — justify if kept).
- A reader unfamiliar with the system's jargon can follow it without external lookup, aside from terms explicitly defined inline.
