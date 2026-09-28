# Archify Schema & Authoring Guide

Production-grade diagram-as-code system supporting 5 diagram types with typed JSON IR, validation, and evidence grounding.

## Contents

- **`schema/schema.ts`** — TypeScript/Zod definitions for all diagram types
  - Architecture, Workflow, Sequence, DataFlow, Lifecycle
  - Validation schema and TypeScript types
  - Evidence grounding structures

- **`examples/`** — Reference implementations for each diagram type
  - `architecture-example.json` — E-commerce platform
  - `workflow-example.json` — Order fulfillment process
  - `sequence-example.json` — OAuth2 authentication
  - `dataflow-example.json` — Analytics pipeline
  - `lifecycle-example.json` — Feature release cycle

- **`docs/`** — Guidance for diagram creation and validation
  - `authoring-guide.md` — How to author diagrams (LLM-focused)
  - `validation-rules.md` — All validation rules and severity levels

## Quick Start

### 1. Choose Diagram Type

| Type | Use Case |
|------|----------|
| Architecture | System topology, infrastructure, components |
| Workflow | Process steps, business flows, decisions |
| Sequence | Message ordering, API interactions, protocols |
| DataFlow | Data transformation, ETL, pipelines |
| Lifecycle | Project phases, release stages, timelines |

### 2. Read Schema & Example

```bash
# Read the schema definitions
cat schema/schema.ts

# Study an example for your type
cat examples/architecture-example.json
```

### 3. Create Your Diagram

Use the authoring guide to create a JSON diagram following the schema.

```bash
cat docs/authoring-guide.md
```

### 4. Validate

Validate your diagram before delivery:

```bash
node bin/archify.mjs validate < your-diagram.json
```

The validator will return:
- ✓ 0 errors → ready for delivery
- ✗ N errors → fix and revalidate
- ⚠ N warnings → optional improvements

### 5. Deliver

Once validation passes:

```bash
node bin/archify.mjs deliver < your-diagram.json
```

Returns SHA-256 checksum and byte count (deterministic proof).

## Key Design Principles

### 1. Evidence Grounding
Every high-value node should trace back to source code, commits, or external references.

```json
{
  "id": "auth-service",
  "evidence": {
    "file": "src/services/auth/service.ts",
    "lines": "42-120",
    "commit": "abc1234"
  }
}
```

### 2. Semantic Colors (Not Aesthetic)
7 colors with fixed meaning:
- **frontend** — UI, client, browser
- **backend** — servers, services, APIs
- **database** — storage, cache, queues
- **security** — auth, encryption, guards
- **cloud** — infrastructure, cloud services
- **messaging** — async communication
- **external** — third-party services

### 3. Stable, Semantic IDs
IDs must be deterministic and reflect what they represent:
- ✓ `auth-service`, `postgres-main`, `event-queue`
- ✗ `node-42`, `service-abc123`, `uuid-randomized`

### 4. Type-Specific Rules

**Architecture:** Zones must not be empty; nodes belong to zones.

**Workflow:** Must have 1 start node, 1+ end nodes; decision nodes have 2+ branches.

**Sequence:** Messages must be ordered (1, 2, 3, ...); 2+ participants.

**DataFlow:** Show source → transform → sink; mark data formats.

**Lifecycle:** Stages in order; transitions define progression.

### 5. Deterministic Output
Same input always produces identical output (checksums match).

## Directory Structure

```
archify/
├── schema/
│   └── schema.ts                 # Zod schemas (source of truth)
├── examples/
│   ├── architecture-example.json # E-commerce system
│   ├── workflow-example.json     # Order fulfillment
│   ├── sequence-example.json     # OAuth2 flow
│   ├── dataflow-example.json     # Analytics pipeline
│   └── lifecycle-example.json    # Release lifecycle
├── docs/
│   ├── authoring-guide.md        # How to author diagrams
│   └── validation-rules.md       # All validation rules
├── bin/
│   └── archify.mjs               # CLI tool (validate, preview, deliver)
└── README.md                     # This file
```

## Validation Rules

### Errors (Block Delivery)
- Schema conformance (required fields, types)
- Stable ID format (alphanumeric + hyphens)
- Referenced nodes must exist
- Workflow missing start/end nodes
- Sequence messages out of order

### Warnings (Recommended, Non-Blocking)
- Missing evidence ties
- Orphaned nodes
- Circular dependencies
- Empty zones/swimlanes
- Data type inconsistencies

### Info (Nice-to-Have)
- Performance suggestions
- Color recommendations

## LLM Authoring Workflow

1. **Read** schema & examples
2. **Write** diagram JSON
3. **Validate** with CLI
4. **Read** diagnostics
5. **Repair** errors/warnings
6. **Revalidate** until 0 errors
7. **Deliver** with checksum

See `docs/authoring-guide.md` for detailed LLM instructions.

## Dependencies

### Production
- `zod@^1.0.0` — Runtime schema validation
- `simple-icons@^16.28.0` — Icon library

### Development
- `ajv@^8.17.1` — JSON schema validation
- `parse5@^7.3.0` — HTML parsing
- `saxes@^6.0.0` — XML/SAX parsing
- `typescript@^5.0.0` — TypeScript compiler

## Next Steps

- [ ] **#36** Implement SVG renderer with automatic layout
- [ ] **#37** Build validation pipeline (diagnostic formatter)
- [ ] **#38** Create CLI tool (validate, preview, deliver)
- [ ] **#39** Build browser viewer (interactivity, themes)
- [ ] **#42** Create LLM skill integration
- [ ] **#43** Write tests and finalize documentation

## References

- Original inspiration: [archify](https://github.com/tt-a1i/archify)
- Related issues: #44 (Epic), #35 (This issue)
