# Archify: Diagram-as-Code Skill

Generate interactive architecture, workflow, sequence, data flow, and lifecycle diagrams as self-contained HTML with verified evidence grounding.

## How to Use

### 1. Pick Your Diagram Type
- **Architecture** — System components, zones, dependencies (e.g., microservices)
- **Workflow** — Step-by-step processes with decisions (e.g., order fulfillment)
- **Sequence** — Timed message exchanges (e.g., OAuth2, API calls)
- **DataFlow** — Data transformations and pipelines (e.g., analytics)
- **Lifecycle** — Project phases and transitions (e.g., release stages)

### 2. Read the Schema
Before writing, read the relevant schema definition in `schema/schema.ts` to understand required fields.

### 3. Study an Example
Look at the corresponding example in `examples/` to see the exact structure and conventions:
- `architecture-example.json`
- `workflow-example.json`
- `sequence-example.json`
- `dataflow-example.json`
- `lifecycle-example.json`

### 4. Author Your Diagram
Follow the authoring guide (`docs/authoring-guide.md`) and create a JSON diagram:

**Key Principles:**
- Use stable, semantic IDs (e.g., `auth-service`, not `node-42`)
- Map nodes to evidence (file paths, commits, URLs)
- Use semantic colors (frontend, backend, database, security, cloud, messaging, external)
- Write clear labels and descriptions

**Example Minimal Diagram:**
```json
{
  "type": "architecture",
  "version": "1.0.0",
  "title": "My System",
  "nodes": [
    { "id": "web", "label": "Web App", "color": "frontend" },
    { "id": "api", "label": "API", "color": "backend" },
    { "id": "db", "label": "Database", "color": "database" }
  ],
  "edges": [
    { "id": "e1", "from": "web", "to": "api", "label": "HTTP" },
    { "id": "e2", "from": "api", "to": "db", "label": "SQL" }
  ]
}
```

### 5. Validate
Validate your diagram using the CLI:
```bash
cat your-diagram.json | node bin/archify.mjs validate
```

**Output:**
```
✓ Validation passed
  Nodes: 3
  Edges: 2
  Warnings: 1
    ⚠ Node 'web' lacks evidence tie
```

### 6. Fix Errors & Warnings
Read the diagnostic output and repair your diagram:
- **Errors** (block delivery) — must fix
- **Warnings** (recommended) — should fix
- **Info** (feedback) — nice-to-have

Common fixes:
- Missing required field → add it
- Unknown node reference → check spelling or add node
- Workflow missing start/end → add start/end nodes
- Sequence out of order → fix `order` field

### 7. Deliver
Once validation passes:
```bash
cat your-diagram.json | node bin/archify.mjs deliver
```

**Output:**
```json
{
  "delivered": true,
  "sha256": "a1b2c3d4...",
  "size": 2847,
  "type": "architecture",
  "title": "My System",
  "version": "1.0.0",
  "nodeCount": 3,
  "edgeCount": 2
}
```

The checksum proves deterministic, bit-perfect output.

### 8. View & Export
The delivered diagram is a self-contained HTML file. Use it to:
- Download SVG (for presentations)
- Download PNG (for documents)
- Share via link (no server required)
- Inspect interactive details (hover, zoom, toggle theme)

---

## CLI Reference

### validate
Check diagram against schema and all validation rules.
```bash
cat diagram.json | node bin/archify.mjs validate
```

**Exit codes:**
- 0 = valid (0 errors)
- 1 = invalid (errors present)

### deliver
Validate, freeze spec, and generate checksums.
```bash
cat diagram.json | node bin/archify.mjs deliver
```

**Output:** JSON with SHA-256 and metadata.

### preview
Generate HTML preview for browser inspection.
```bash
cat diagram.json | node bin/archify.mjs preview
```

**Output:** Path to temporary HTML file.

---

## Validation Rules

### Errors (Block Delivery)

| Rule | When | Fix |
|------|------|-----|
| Missing type | No `type` field | Add: `"type": "architecture"` (or workflow, etc.) |
| Invalid type | `type` not in [architecture, workflow, ...] | Use a valid type |
| Missing version | No `version` field | Add: `"version": "1.0.0"` |
| Missing title | No `title` field | Add: `"title": "My Diagram"` |
| Empty nodes | `nodes` array is empty | Add at least 1 node |
| Unknown node ref | Edge references non-existent node | Check node IDs or add missing node |
| Workflow no start | No node with `type: "start"` | Add start node |
| Workflow no end | No node with `type: "end"` | Add end node |
| Sequence bad order | Messages not in order (1, 2, 3, ...) | Fix `order` field to be monotonic |
| Sequence < 2 participants | Less than 2 participants | Add participants |

### Warnings (Recommended)

| Rule | When | Fix |
|------|------|-----|
| Missing evidence | High-value node (security, database, etc.) has no evidence tie | Add `evidence`: { file, lines, commit, url } |
| Orphaned node | Node has no incoming or outgoing edges | Connect it or remove it |
| Empty zone | Zone declared but has no nodes | Add nodes to zone or remove it |
| Color mismatch | Node color doesn't reflect its type | Consider different color |

---

## Schema Overview

Each diagram type has a specific schema. All share:
- `type` (required) — diagram type
- `version` (required) — semver (e.g., "1.0.0")
- `title` (required) — human-readable name
- `description` (optional) — longer explanation
- `nodes` (required) — array of components
- `edges` (optional) — array of relationships
- `metadata` (optional) — author, created, updated

### Node Properties
- `id` (required) — stable, semantic ID (alphanumeric + hyphens)
- `label` (required) — display name
- `color` (required) — semantic color (frontend, backend, database, security, cloud, messaging, external)
- `evidence` (optional) — proof: `{ file, lines, commit, url }`
- `description` (optional) — explain purpose

### Edge Properties
- `id` (required) — stable edge ID
- `from` (required) — source node ID
- `to` (required) — target node ID
- `label` (optional) — relationship description
- `evidence` (optional) — proof of connection

---

## Common Patterns

### Architecture with Zones
```json
{
  "type": "architecture",
  "nodes": [...],
  "zones": [
    { "id": "client", "label": "Client Layer" },
    { "id": "api", "label": "API Layer" }
  ]
}
```

### Workflow with Decisions
```json
{
  "type": "workflow",
  "nodes": [
    { "id": "start", "type": "start", ... },
    { "id": "check", "type": "decision", ... },
    { "id": "end", "type": "end", ... }
  ]
}
```

### Sequence with Message Types
```json
{
  "type": "sequence",
  "messages": [
    { "id": "m1", "type": "sync", "order": 1, ... },
    { "id": "m2", "type": "async", "order": 2, ... },
    { "id": "m3", "type": "return", "order": 3, ... }
  ]
}
```

---

## Authoring Workflow

```
1. Choose type (architecture, workflow, etc.)
2. Read schema/schema.ts
3. Study examples/[type]-example.json
4. Author diagram.json (start with required fields)
5. Validate: cat diagram.json | node bin/archify.mjs validate
6. Read errors/warnings
7. Repair diagram
8. Revalidate (go to step 5)
9. Deliver: cat diagram.json | node bin/archify.mjs deliver
10. Get SHA-256 checksum (proof of bit-perfect output)
```

---

## Evidence Grounding

The most powerful feature: every node/edge can tie to source code.

**Example:**
```json
{
  "id": "auth-service",
  "label": "Auth Service",
  "evidence": {
    "file": "src/services/auth/service.ts",
    "lines": "42-120",
    "commit": "abc1234"
  }
}
```

This means: "The Auth Service is defined in src/services/auth/service.ts, lines 42-120, commit abc1234."

**Why it matters:**
- Diagrams stay synchronized with code
- Future readers can find the implementation
- Reviewers verify against source
- Enables automated consistency checks

---

## Best Practices

1. **Read before writing** — Never guess the schema; read the example
2. **Stable IDs** — Use semantic, immutable IDs (`auth-service`, not `node-42`)
3. **Evidence on high-value nodes** — Security, database, external services should have evidence
4. **Clear labels** — 2-4 words, descriptive (not abbreviated)
5. **Semantic colors** — Match color to node type (blue for frontend, green for backend)
6. **Validate early** — Check after each meaningful edit
7. **Fix errors first** — Errors block delivery; warnings are optional

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| "Unknown node 'x-service'" | Typo in node ID | Check spelling in schema example; copy-paste if needed |
| "Workflow missing start" | No node with `type: "start"` | Add `{ "id": "start", "label": "Start", "type": "start", ... }` |
| "Message order not monotonic" | Order field not increasing (1, 2, 3...) | Renumber messages in order |
| "Zone 'x' has no nodes" | Zone declared but empty | Add nodes with `zone: "x"` or remove zone |
| "Checksum mismatch" | Diagram changed between validates | Input must be byte-identical for reproducibility |

---

## Files & References

- `schema/schema.ts` — TypeScript/Zod definitions (source of truth)
- `examples/` — 5 complete, validated examples
- `docs/authoring-guide.md` — Detailed LLM authoring instruction
- `docs/validation-rules.md` — All validation rules
- `bin/archify.mjs` — CLI tool (validate, deliver, preview)
- `validator/` — Validation implementation
- `renderer/` — SVG generation and layout
