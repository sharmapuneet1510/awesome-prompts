---
name: MCP Server Builder Skill
version: 1.0
description: >
  Use when creating, scaffolding, testing, or registering a new Model Context
  Protocol (MCP) server. Covers SDK and transport choice, a working server in
  Python and TypeScript, three test layers, and Claude Code registration.
  Tool-schema design rules live in mcp_server_skill.
applies_to: [mcp, python, typescript, java, agent-tools]
tags: [mcp, mcp-server, stdio, streamable-http, sdk, testing]
---

# MCP Server Builder Skill — v1.0

> **Scope.** How to *build* an MCP server: pick SDK and transport, write it, test it, register it. *Which* tools to expose and how to shape their schemas is `mcp_server_skill.md` — apply both.
>
> **Verified 2026-09-20** by running every example below against Python `mcp` 2.2.0 and npm `@modelcontextprotocol/server` 2.0.0 (spec 2026-07-28). SDK APIs change between majors — redo §1 before trusting any snippet, these included.

## 1. Step 0 — Pin the SDK major version

| Language | Package | Trap |
|---|---|---|
| Python | `mcp` 2.x — `from mcp.server import MCPServer` | `pip install mcp` now installs 2.x. The v1 import `from mcp.server.fastmcp import FastMCP` raises `ModuleNotFoundError`. To stay on v1, pin `mcp<2`. |
| TypeScript | `@modelcontextprotocol/server` 2.x + `zod` | `@modelcontextprotocol/sdk` is the legacy v1 package with a different API. In v2, `inputSchema` must be `z.object({...})` and stdio is served with `serveStdio`. |
| Java | `io.modelcontextprotocol.sdk:mcp`, or Spring Boot `org.springframework.ai:spring-ai-starter-mcp-server` | Coordinates only — no Java example here was compiled. Follow the SDK's own docs. |

Check the current major on PyPI / npm and read the SDK's quickstart **before** writing code. Never write MCP code from memory.

## 2. Choose primitives and transport

| Primitive | Triggered by | Use for |
|---|---|---|
| **Tool** | the model | actions and queries — the default choice |
| **Resource** | the application / user attaches it | read-only content addressed by URI |
| **Prompt** | the user | reusable prompt templates |

| Transport | Shape | Choose when |
|---|---|---|
| **stdio** | client spawns your server as a subprocess; one client; runs with the user's own permissions | local, single-user, development — **start here** |
| **Streamable HTTP** | long-running server, many clients, needs auth | remote or shared servers |

SSE is legacy: the TypeScript SDK keeps it only in a frozen migration package. Use Streamable HTTP for anything remote.

## 3. A working server — Python

```python
"""Support-ticket MCP server: read-only lookups plus one guarded destructive tool."""
import logging
import sys
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

# Under stdio, stdout IS the protocol channel. Log to stderr only.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("tickets")

mcp = MCPServer("tickets", instructions="Look up support tickets. Deleting one needs confirm=true.")


class Ticket(BaseModel):
    id: str
    title: str
    status: Literal["open", "closed"]


_DB: dict[str, Ticket] = {
    "T-1": Ticket(id="T-1", title="Login fails on Safari", status="open"),
    "T-2": Ticket(id="T-2", title="Invoice PDF is blank", status="closed"),
}

READ_ONLY = ToolAnnotations(read_only_hint=True)


@mcp.tool(annotations=READ_ONLY)
def get_ticket(ticket_id: str) -> Ticket:
    """Fetch one ticket by ID. Read-only. If the ID is unknown, use search_tickets."""
    ticket = _DB.get(ticket_id)
    if ticket is None:
        raise ToolError(f"NOT_FOUND: no ticket {ticket_id!r}. Call search_tickets for valid IDs.")
    return ticket


@mcp.tool(annotations=READ_ONLY)
def search_tickets(
    status: Literal["open", "closed"] | None = None,
    limit: Annotated[int, Field(ge=1, le=50)] = 10,
) -> list[Ticket]:
    """List tickets, optionally filtered by status. Read-only; returns at most `limit`."""
    log.info("search status=%s limit=%s", status, limit)
    hits = [t for t in _DB.values() if status is None or t.status == status]
    return hits[:limit]


@mcp.tool(annotations=ToolAnnotations(destructive_hint=True, idempotent_hint=True))
def delete_ticket(ticket_id: str, confirm: bool = False) -> str:
    """Permanently delete a ticket. Without confirm=true this only previews the deletion."""
    if ticket_id not in _DB:
        raise ToolError(f"NOT_FOUND: no ticket {ticket_id!r}.")
    if not confirm:
        return f"PREVIEW: would delete {ticket_id} ({_DB[ticket_id].title}). Re-call with confirm=true."
    del _DB[ticket_id]
    return f"Deleted {ticket_id}."


if __name__ == "__main__":
    mcp.run()  # stdio by default
```

What the SDK does for you: **type hints become the JSON Schema**, the **docstring becomes the tool description** (the model reads it — say what the tool does *not* do), and a `BaseModel` return type becomes structured output with an output schema.

## 4. The same shape — TypeScript (v2)

```ts
import { McpServer } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { z } from 'zod';

const Ticket = z.object({ id: z.string(), title: z.string(), status: z.enum(['open', 'closed']) });
type Ticket = z.infer<typeof Ticket>;

const db = new Map<string, Ticket>([
    ['T-1', { id: 'T-1', title: 'Login fails on Safari', status: 'open' }],
    ['T-2', { id: 'T-2', title: 'Invoice PDF is blank', status: 'closed' }]
]);

// Errors the agent can read and act on: isError:true, not a thrown exception.
const fail = (text: string) => ({ isError: true as const, content: [{ type: 'text' as const, text }] });

// Under stdio, stdout IS the protocol channel. Log with console.error (stderr) only.
serveStdio(() => {
    const server = new McpServer({ name: 'tickets', version: '1.0.0' });

    server.registerTool(
        'get_ticket',
        {
            description: 'Fetch one ticket by ID. Read-only. If the ID is unknown, use search_tickets.',
            inputSchema: z.object({ ticketId: z.string() }),
            outputSchema: Ticket,
            annotations: { readOnlyHint: true }
        },
        async ({ ticketId }) => {
            const ticket = db.get(ticketId);
            if (!ticket) return fail(`NOT_FOUND: no ticket '${ticketId}'. Call search_tickets for valid IDs.`);
            return { content: [{ type: 'text', text: JSON.stringify(ticket) }], structuredContent: ticket };
        }
    );

    server.registerTool(
        'delete_ticket',
        {
            description: 'Permanently delete a ticket. Without confirm=true this only previews the deletion.',
            inputSchema: z.object({ ticketId: z.string(), confirm: z.boolean().default(false) }),
            annotations: { destructiveHint: true, idempotentHint: true }
        },
        async ({ ticketId, confirm }) => {
            const ticket = db.get(ticketId);
            if (!ticket) return fail(`NOT_FOUND: no ticket '${ticketId}'.`);
            if (!confirm) {
                return { content: [{ type: 'text', text: `PREVIEW: would delete ${ticketId} (${ticket.title}). Re-call with confirm=true.` }] };
            }
            db.delete(ticketId);
            return { content: [{ type: 'text', text: `Deleted ${ticketId}.` }] };
        }
    );

    return server;
});
```

Typechecks under `strict`; needs `"types": ["node"]` in `tsconfig.json` on TypeScript ≥ 6.

## 5. Rules that bite at build time

1. **Never write to stdout under stdio.** It carries JSON-RPC; a stray `print()` / `console.log()` is not a valid message. The symptom depends on the client: the Python SDK client logs `Failed to parse JSONRPC message from server` and skips the line; a stricter client may fail the handshake or drop the connection. Log to stderr.
2. **Failures the agent should act on → `ToolError` (Python) or `isError: true` (TS).** The message reaches the model, so make it actionable (`NOT_FOUND: … Call search_tickets`) and keep secrets and filesystem paths out of it. Any *other* exception raised in Python is masked as `Error executing tool <name>` (verified: an internal path was not leaked; the traceback goes to stderr). That is safe, but the agent cannot self-correct from it — so anticipated failures need `ToolError`.
3. **Let the schema validate.** Constrain with types (`Literal`, `Field(ge=1, le=50)`, `z.enum`). An out-of-range `limit` comes back as an error result.
4. **Cap output.** Every returned byte costs the agent tokens: default `limit`, hard maximum, paginate.
5. **Secrets come from the environment.** Never as tool arguments, tool results, or log lines.
6. **Returned data is untrusted input to the model.** A ticket title can carry instructions. A tool that reads third-party text must not also be able to take destructive action without the preview/confirm gate.
7. **HTTP: keep the SDK's safe defaults until you add auth.** Python's `mcp.run(transport="streamable-http")` binds `127.0.0.1:8000/mcp`, validates Host/Origin, and caps request bodies at 4 MiB. Before binding to any other interface, add authentication and leave those checks on.

## 6. Test in three layers

**6.1 In-process — fast, runs in CI.** `Client(mcp)` connects to the server object directly.

```python
import pytest
from mcp import Client
from tickets_server import mcp

pytestmark = pytest.mark.anyio


async def test_lists_tools_with_annotations():
    async with Client(mcp) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == {"get_ticket", "search_tickets", "delete_ticket"}
    assert tools["delete_ticket"].annotations.destructive_hint is True


async def test_unknown_id_is_a_tool_error_the_agent_can_read():
    async with Client(mcp) as client:
        result = await client.call_tool("get_ticket", {"ticket_id": "nope"})
    assert result.is_error
    assert "NOT_FOUND" in result.content[0].text


async def test_delete_previews_until_confirmed():
    async with Client(mcp) as client:
        preview = await client.call_tool("delete_ticket", {"ticket_id": "T-2"})
        assert "PREVIEW" in preview.content[0].text
        assert not (await client.call_tool("get_ticket", {"ticket_id": "T-2"})).is_error
```

**6.2 Real stdio subprocess — catches stdout pollution, import errors, path bugs.** Launch the server exactly as a host would:

```python
import sys
from mcp import Client, StdioServerParameters

params = StdioServerParameters(command=sys.executable, args=["tickets_server.py"])
async with Client(params, read_timeout_seconds=8) as client:
    print([t.name for t in (await client.list_tools()).tools])
```

Any MCP client can drive any server: the TypeScript server above was tested with this Python client.

**6.3 Inspector — interactive or scripted.**

```bash
uv run mcp dev tickets_server.py        # interactive UI (Python; needs the mcp[cli] extra)
npx @modelcontextprotocol/inspector --cli python tickets_server.py --method tools/list
```

Inspector 2.x declares Node ≥ 22.19. The `--cli` form ran on Node 20.15 with engine warnings.

## 7. Register with Claude Code

```bash
claude mcp add tickets -- /abs/path/python /abs/path/tickets_server.py    # stdio
claude mcp add --transport http tickets https://host.example/mcp          # remote
claude mcp list                                                            # health check
```

- Use **absolute paths** for the interpreter and script so startup does not depend on the client's working directory.
- **Scope** (`-s`): `local` (default), `user` (all your projects), `project` (writes `.mcp.json` in the current directory, meant to be committed).
- A `project`-scoped server shows `⏸ Pending approval` in `claude mcp list` until someone runs `claude` and approves it.
- **`-e KEY=value` is stored in plain text in the config file.** At `project` scope that file is committed — pass secrets at `local` or `user` scope only.

## 8. Checklist

✅ Checked the SDK's current major version and read its quickstart (no code from memory)
✅ Started with stdio; chose Streamable HTTP only for remote/shared use
✅ Tool descriptions state what the tool does *and* does not do; tool set reviewed against `mcp_server_skill.md`
✅ Read-only tools carry `read_only_hint`; destructive tools carry `destructive_hint` and a preview/confirm step
✅ Nothing writes to stdout under stdio; logging goes to stderr
✅ Anticipated failures use `ToolError` / `isError` with actionable, secret-free messages
✅ Inputs are constrained by types; list-returning tools have a default and a hard `limit`
✅ Secrets come from the environment, never from arguments, results, or logs
✅ Tested in-process **and** as a real stdio subprocess
✅ Registered with absolute paths; secrets not passed via `-e` at project scope
