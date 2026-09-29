---
name: mcp-server
description: Designing which tools an MCP server or agent exposes, and their schemas
---

# MCP Server & Tool Design Skill — v1.1

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | Designing which tools an MCP server or agent exposes, and their schemas |
| **Skip when** | Building and wiring the server — `mcp_server_builder_skill` |
| **Inputs** | The workflows the agent must perform |
| **Produces** | Tool list with names, descriptions, parameter schemas, error shapes |
| **Steps** | 1. Minimise the tool set → 2. Scope each to least privilege → 3. Write schema + description (does / does not) → 4. Design structured, retryable-aware errors |
| **Done when** | §5 checklist passes |
| **Load on demand** | §1 minimisation · §2 least privilege · §3 schema clarity · §4 errors |
| **Run report** | `html_report_skill` — adds: Tool inventory (read-only / mutating / destructive) |
| **Pairs with** | `mcp_server_builder_skill` |

---

## 1. Tool Minimization

Every tool exposed to an agent is a decision surface — more tools means more chances for the agent to pick the wrong one. Before adding a tool, ask: can an existing tool's parameters cover this, or does it genuinely need a new capability?

- Prefer a few well-scoped tools over many overlapping ones (one `search` tool with filters beats `search_by_name` + `search_by_date` + `search_by_tag`).
- Don't expose raw CRUD if the workflow only ever needs 2 of the 4 operations — narrower tools reduce misuse.

## 2. Least-Privilege Scoping

- Scope each tool's effective permissions to exactly what its stated purpose needs. A "read customer record" tool should not also be able to write.
- Separate read-only tools from mutating tools clearly in naming (`get_*`/`list_*` vs `create_*`/`update_*`/`delete_*`) so an agent's own reasoning about risk lines up with the tool name.
- For destructive or hard-to-reverse operations, require an explicit confirmation parameter or a preceding read/preview call — don't let a single tool call both compute and commit an irreversible change.

## 3. Schema Clarity

The tool's JSON schema is the only contract the agent sees — treat it like a public API:
- **Name**: verb + object, unambiguous (`create_invoice`, not `process`).
- **Description**: state what it does, when to use it, and what it explicitly does NOT do (e.g., "does not send the invoice — call `send_invoice` separately").
- **Parameters**: required vs optional clearly marked; use enums instead of free-text where the valid values are known; avoid overloaded parameters that change meaning based on another parameter's value.
- **Return shape**: consistent, predictable — same shape on success and on the documented error cases, so the agent doesn't need to branch on undocumented structure.

## 4. Error Design

- Return structured errors the agent can reason about (`{"error": "NOT_FOUND", "message": "..."}`), not raw stack traces or generic 500s.
- Distinguish retryable errors (rate limit, transient network) from non-retryable ones (invalid input, not found) — an agent that retries a non-retryable error wastes turns and can loop.

## 5. Checklist

✅ Each tool has one clear purpose; no overlapping near-duplicates
✅ Read-only vs mutating tools are distinguishable by name
✅ Destructive operations require explicit confirmation or a preview step
✅ Descriptions state both what the tool does and what it doesn't
✅ Parameters use enums/types over free-text where possible
✅ Errors are structured and distinguish retryable from non-retryable

---
> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied. See `docs/reference/credits.md`.
