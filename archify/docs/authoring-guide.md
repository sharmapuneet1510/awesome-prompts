# Diagram Authoring Guide for LLMs

This guide teaches Claude (or similar LLMs) how to author high-quality, evidence-grounded diagrams using the Archify schema.

## Core Principles

### 1. Read Schema & Examples Before Writing
Always read the schema boundaries first. Never hallucinate JSON structures.

**Workflow:**
1. Read `schema.ts` for your diagram type
2. Study one example from `examples/`
3. Identify the exact fields you must populate
4. Identify optional vs. required fields
5. Then write your diagram

### 2. Choose the Right Diagram Type
Each type serves a specific purpose:

| Type | Purpose | Best For |
|------|---------|----------|
| **Architecture** | Show system topology and data flow | System design, infrastructure |
| **Workflow** | Show process steps and decisions | Business processes, user flows |
| **Sequence** | Show message order and timing | API interactions, protocols |
| **DataFlow** | Show data transformations | ETL, analytics pipelines |
| **Lifecycle** | Show phases and transitions | Feature releases, project stages |

**Decision Tree:**
- **Are you showing how components communicate?** → Architecture
- **Are you showing step-by-step process with decisions?** → Workflow
- **Are you showing timed message exchange?** → Sequence
- **Are you showing data transformation?** → DataFlow
- **Are you showing phases of a project/product?** → Lifecycle

### 3. Create Stable, Semantic IDs
IDs are the anchor point for evidence and traceability. They must be:
- **Stable** — never change, even if the label or description changes
- **Semantic** — reflect what the thing is (e.g., `auth-service`, not `node-42`)
- **Deterministic** — same ID always refers to same entity

**Examples:**
✓ `auth-service`, `postgres-main`, `order-handler`, `event-queue`
✗ `node-1`, `service-abc123`, `temp-x`, `🔐-svc` (not alphanumeric)

**How to Create IDs:**
1. Take the label (e.g., "Authentication Service")
2. Lowercase and hyphenate (e.g., "authentication-service")
3. Shorten if it gets too long, but keep it recognizable (e.g., "auth-service")
4. Never use UUIDs or random suffixes

### 4. Ground Everything in Evidence
Every node should trace back to code, commits, or external references.

**Evidence Types:**
- `file`: Relative path to source file (e.g., `src/services/auth/service.ts`)
- `lines`: Line range where this component is defined (e.g., `42-120`)
- `commit`: Git commit SHA (first 7+ chars) (e.g., `abc1234`)
- `url`: External reference (e.g., `https://stripe.com/docs/api`)

**What Needs Evidence:**
- High-value nodes (architecture, security, external services) — almost always
- Low-value nodes (local caches, temporary states) — optional
- Edges showing API calls or data flow — should have evidence if they're important
- Business logic nodes — should tie to implementation

**Examples:**

```json
{
  "id": "auth-service",
  "label": "Auth Service",
  "evidence": {
    "file": "src/services/auth/service.ts",
    "lines": "1-150",
    "commit": "abc1234"
  }
}
```

### 5. Use Semantic Colors Correctly
7 colors, each with specific meaning. Never use color for aesthetics; use it for clarity.

| Color | Meaning | Examples |
|-------|---------|----------|
| **frontend** | User-facing | React components, HTML, browser JavaScript |
| **backend** | Server-side logic | APIs, services, business logic |
| **database** | Data storage | PostgreSQL, Redis, S3 buckets |
| **security** | Auth & protection | OAuth, JWT, firewalls, encryption |
| **cloud** | Infrastructure | AWS, GCP, Kubernetes, load balancers |
| **messaging** | Async comms | RabbitMQ, Kafka, event buses |
| **external** | Third-party | Stripe, Auth0, GitHub API |

**Rule:** If you're unsure, default to `backend` for your own code, `external` for outside services.

### 6. Write Clear Labels & Descriptions
- **Label** — noun, 2-4 words (e.g., "Auth Service", "PostgreSQL", "Stripe API")
- **Description** — brief explanation of purpose or behavior (1-2 sentences, max 256 chars)

**Examples:**

✓ `label: "Auth Service"`, `description: "Handles JWT token generation and validation"`
✗ `label: "svc"`, `description: "Does auth stuff"`
✗ `label: "Microservice for Authentication and Authorization including OAuth2"` (too long)

---

## Type-Specific Authoring Patterns

### Architecture Diagrams

**Pattern: Zones → Nodes → Edges**

1. Identify logical zones (e.g., "Client Layer", "API Layer", "Data Layer")
2. Place nodes in zones
3. Draw edges showing dependencies

**Example Workflow:**

```json
{
  "type": "architecture",
  "version": "1.0.0",
  "title": "My System Architecture",
  "zones": [
    { "id": "client", "label": "Client" },
    { "id": "api", "label": "API" },
    { "id": "data", "label": "Data" }
  ],
  "nodes": [
    { "id": "web-client", "label": "Web Client", "color": "frontend", "zone": "client" },
    { "id": "api-server", "label": "API Server", "color": "backend", "zone": "api" },
    { "id": "db", "label": "PostgreSQL", "color": "database", "zone": "data" }
  ],
  "edges": [
    { "id": "edge-1", "from": "web-client", "to": "api-server", "label": "HTTP" },
    { "id": "edge-2", "from": "api-server", "to": "db", "label": "SQL" }
  ]
}
```

**Tips:**
- Arrange zones left-to-right or top-to-bottom (request flow direction)
- Use zones to prevent visual clutter
- Every node should belong to a zone

### Workflow Diagrams

**Pattern: Start → Process/Decision → End**

1. Identify start point
2. List process steps and decision branches
3. Converge to end

**Example Workflow:**

```json
{
  "type": "workflow",
  "nodes": [
    { "id": "start", "label": "Order Received", "type": "start" },
    { "id": "validate", "label": "Validate Payment", "type": "process" },
    { "id": "check", "label": "Check Inventory", "type": "decision" },
    { "id": "ship", "label": "Ship Order", "type": "process" },
    { "id": "end", "label": "Order Complete", "type": "end" }
  ],
  "edges": [
    { "id": "e1", "from": "start", "to": "validate", "order": 1 },
    { "id": "e2", "from": "validate", "to": "check", "order": 2 },
    { "id": "e3", "from": "check", "to": "ship", "condition": "In Stock", "order": 3 },
    { "id": "e4", "from": "ship", "to": "end", "order": 4 }
  ]
}
```

**Tips:**
- Exactly 1 start node (type: 'start')
- At least 1 end node (type: 'end')
- Decision nodes → 2+ outgoing edges (if/else branches)
- Orders must be monotonic (1, 2, 3, ...)

### Sequence Diagrams

**Pattern: Participants → Messages (ordered)**

1. List all participants (actors, systems)
2. Enumerate messages in order
3. Mark message types (sync, async, return)

**Example:**

```json
{
  "type": "sequence",
  "participants": [
    { "id": "user", "label": "User", "role": "actor" },
    { "id": "api", "label": "API", "role": "participant" },
    { "id": "db", "label": "Database", "role": "system" }
  ],
  "messages": [
    { "id": "m1", "from": "user", "to": "api", "label": "POST /login", "type": "sync", "order": 1 },
    { "id": "m2", "from": "api", "to": "db", "label": "Query user", "type": "sync", "order": 2 },
    { "id": "m3", "from": "db", "to": "api", "label": "User record", "type": "return", "order": 3 },
    { "id": "m4", "from": "api", "to": "user", "label": "200 OK", "type": "return", "order": 4 }
  ]
}
```

**Tips:**
- Messages must be ordered (1, 2, 3, ..., never jump or repeat)
- 2+ participants required
- Types: 'sync' (wait for response), 'async' (fire and forget), 'return' (response)

### Data Flow Diagrams

**Pattern: Source → Transform → Sink**

1. Identify data sources
2. Show transformations
3. Show sinks (storage, output)

**Example:**

```json
{
  "type": "dataflow",
  "nodes": [
    { "id": "events", "label": "User Events", "color": "frontend", "dataType": "event" },
    { "id": "ingest", "label": "Event Ingest", "color": "backend", "transformation": "Validate & enrich" },
    { "id": "warehouse", "label": "Data Warehouse", "color": "database", "dataType": "parquet" }
  ],
  "edges": [
    { "id": "e1", "from": "events", "to": "ingest", "format": "json" },
    { "id": "e2", "from": "ingest", "to": "warehouse", "format": "parquet" }
  ]
}
```

**Tips:**
- Mark data types (json, xml, csv, protobuf, avro)
- Show transformations (enrich, filter, aggregate)
- Name flows if there are multiple paths

### Lifecycle Diagrams

**Pattern: Stages → Transitions**

1. List stages in order
2. Define transitions (when you move to next stage)
3. Add activities/tasks per stage

**Example:**

```json
{
  "type": "lifecycle",
  "stages": [
    { "id": "plan", "label": "Planning", "duration": "1 week" },
    { "id": "dev", "label": "Development", "duration": "4 weeks" },
    { "id": "test", "label": "Testing", "duration": "1 week" },
    { "id": "release", "label": "Release", "duration": "1 day" }
  ],
  "transitions": [
    { "from": "plan", "to": "dev", "trigger": "Plan approved" },
    { "from": "dev", "to": "test", "trigger": "Code complete" },
    { "from": "test", "to": "release", "trigger": "All tests pass" }
  ]
}
```

**Tips:**
- Stages must be in chronological order
- Transitions define progression rules
- Add conditions if needed (e.g., "gate: no critical bugs")

---

## The Read-Validate-Repair Loop

**Never assume your diagram is correct.** Always validate:

1. **Write** your diagram JSON
2. **Validate** with `node bin/archify.mjs validate < diagram.json`
3. **Read** the diagnostic output
4. **Repair** any errors or warnings
5. **Revalidate** until zero errors
6. **Deliver** with `node bin/archify.mjs deliver < diagram.json`

**Example Repair:**

```bash
# Write diagram
cat diagram.json | node bin/archify.mjs validate
# Output:
# Error: Edge 'e42' references unknown node 'foo-service'
# Available nodes: auth-service, product-service

# Fix: Rename 'foo-service' to 'product-service' in edge
# Revalidate
cat diagram.json | node bin/archify.mjs validate
# Output:
# ✓ Valid (0 errors, 1 warning)
# Warning: Node 'temp-cache' has no edges

# Optional: Fix warning
# Or accept and deliver
cat diagram.json | node bin/archify.mjs deliver
# Output:
# SHA-256: a1b2c3d4...
# Size: 2847 bytes
```

---

## Quality Checklist

Before delivery, verify:

- [ ] Schema: Valid JSON matching diagram type
- [ ] IDs: All stable, semantic, alphanumeric + hyphens
- [ ] Colors: Semantic (not aesthetic); reflect node types
- [ ] Evidence: 80%+ coverage on high-value nodes
- [ ] Labels: Clear, concise (2-4 words)
- [ ] Descriptions: Explain purpose or behavior
- [ ] Connectivity: No broken references, no orphaned nodes
- [ ] Type-Specific: Start/end for workflows, order for sequences, etc.
- [ ] Validation: 0 errors (warnings acceptable)
- [ ] Determinism: Revalidation checksums match

---

## Common Mistakes & Fixes

| Mistake | Fix |
|---------|-----|
| Using UUIDs for IDs | Use semantic IDs based on entity name |
| No evidence ties | Add file/lines/commit for high-value nodes |
| Wrong color (aesthetic not semantic) | Pick color that reflects node type |
| Orphaned nodes | Remove or connect to graph |
| Broken edge references | Verify 'from' and 'to' reference existing nodes |
| Workflow without start/end | Add nodes with type: 'start' and type: 'end' |
| Sequence messages out of order | Ensure order field is monotonic (1, 2, 3, ...) |
| Missing 'version' or 'type' | Add required top-level fields |

---

## References
- `schema.ts` — Zod schema definitions (source of truth)
- `examples/` — Valid specimens for each diagram type
- `validation-rules.md` — Validation rule reference
- `bin/archify.mjs validate` — Validator CLI
- `bin/archify.mjs deliver` — Delivery tool with checksums
