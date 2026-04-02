General rules for this repository:

- Only write files inside the current workspace.
- Use .agent-handoff/current.json as the shared handoff state between agents.
- Store per-Jira work under .agent-sessions/jira/<KEY>/.
- When Jira work is completed, store a reusable template under .agent-sessions/templates/jira/.

Project context:
- Business code lives in gateway-* modules.
- Prefer existing patterns in the gateway-* modules; do not invent new frameworks.
- Keep changes minimal, add safe logging and error handling consistent with existing code style.    