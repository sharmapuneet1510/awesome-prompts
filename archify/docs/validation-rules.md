# Diagram Validation Rules

This document defines all validation rules that must pass before a diagram can be delivered. The validator checks these rules and returns actionable diagnostics for repair.

## Core Validation Rules

### Schema Conformance
**Rule:** All diagrams must conform to their TypeScript schema (Zod-validated).
- ✓ Required fields present and non-empty
- ✓ Enum values valid (e.g., `color` must be one of 7 semantic colors)
- ✓ String lengths within bounds (IDs: 1-64, labels: 1-128, descriptions: 1-256)
- ✗ Diagnostic: "Field 'color' must be one of: frontend, backend, database, security, cloud, messaging, external"

### Stable IDs
**Rule:** Node and edge IDs must be stable, deterministic, and immutable.
- ✓ Alphanumeric + hyphens only (no spaces, underscores, or punctuation)
- ✓ Between 1-64 characters
- ✓ Same ID always refers to the same entity
- ✗ Diagnostic: "ID 'auth service-01' contains invalid character (space). Use 'auth-service-01' instead."

### Evidence Grounding
**Rule:** High-value nodes/edges should have evidence ties. Optional but recommended.
- ✓ If evidence provided:
  - `file` must be a relative path (no leading `/`)
  - `lines` must be valid range or single number (e.g., "42-88" or "42")
  - `commit` should be 7+ character SHA prefix
  - `url` must be valid HTTP/HTTPS URL
- ✗ Warning: "Node 'auth-service' lacks evidence tie. Consider adding file/lines/commit."

### Semantic Colors
**Rule:** Each node must use one of 7 semantic colors; colors must reflect node type.
- ✓ `frontend` — UI, browser, client libraries
- ✓ `backend` — servers, services, APIs, business logic
- ✓ `database` — storage (SQL, NoSQL, cache, queue)
- ✓ `security` — auth, encryption, guards, compliance
- ✓ `cloud` — cloud services, infrastructure, CDN
- ✓ `messaging` — queues, pub/sub, event systems
- ✓ `external` — third-party services, partners
- ✗ Warning: "Node 'PostgreSQL' uses 'database' color (correct). Node 'Payment API' uses 'backend'; consider 'external' if third-party."

### Connectivity & Reachability
**Rule:** Edges must reference valid nodes; graphs must detect orphaned nodes and cycles.
- ✓ Edge `from` and `to` must reference existing node IDs
- ✓ No self-loops (edge from node to itself, except in sequence diagrams)
- ✗ Error: "Edge 'edge-42' references missing node 'unknown-service'. Available: auth-service, product-service, ..."
- ✗ Warning: "Node 'temp-cache' has no incoming or outgoing edges. Is it unused?"
- ✗ Warning: "Cycle detected: api-gateway → service-a → service-b → api-gateway. Intentional? Confirm."

### Type-Specific Rules

#### Architecture Diagrams
- ✓ Zones must not be empty (if declared, at least 1 node belongs to zone)
- ✓ Nodes in same zone should be related logically
- ✗ Warning: "Zone 'database' has no nodes. Remove or add nodes to this zone."

#### Workflow Diagrams
- ✓ Must have exactly 1 start node (type: 'start')
- ✓ Must have at least 1 end node (type: 'end')
- ✓ Swimlanes must not be empty
- ✓ Decision nodes must have at least 2 outgoing edges
- ✗ Error: "Workflow missing 'start' node. Add a node with type: 'start'."
- ✗ Warning: "Decision node 'check-inventory' has only 1 outgoing edge. Decisions require 2+ branches."

#### Sequence Diagrams
- ✓ Messages must be ordered (order field must increase monotonically)
- ✓ Participants must have unique IDs
- ✓ Messages must reference valid participants
- ✓ At least 2 participants required
- ✗ Error: "Message order is not monotonic: msg-1 (order: 2), msg-2 (order: 1). Fix ordering."

#### Data Flow Diagrams
- ✓ Flows (if declared) must have valid node paths
- ✓ Data types should be consistent across related edges
- ✓ No circular data flows (unless explicitly intentional)
- ✗ Warning: "Flow 'analytics' mixes data types: json → parquet → json. Confirm intentional."

#### Lifecycle Diagrams
- ✓ Stages must be in order (transitions respect stage sequence)
- ✓ Must have at least 1 stage
- ✓ Transitions must reference valid stages
- ✗ Error: "Transition from 'design' to 'ideation' violates stage order. Stages must progress forward."

---

## Diagnostic Severity Levels

### Errors (Block Delivery)
- Schema conformance failures
- Missing required fields
- Invalid node/edge references
- Workflow missing start/end nodes
- Invalid stability constraints (non-deterministic IDs)

**Action:** Repair required before delivery.

### Warnings (Non-Blocking, Recommended Fix)
- Missing evidence ties on key nodes
- Orphaned nodes
- Cycles (unless intentional)
- Empty zones/swimlanes
- Data type inconsistencies

**Action:** Should fix to improve quality, but not required for delivery.

### Info (Feedback Only)
- Unused references
- Semantic color recommendations
- Performance suggestions

**Action:** Nice-to-have improvements.

---

## LLM Authoring Guidance

When the validator returns errors or warnings, Claude must:

1. **Read the diagnostic message carefully** — it says exactly what's wrong and suggests a fix.
2. **Identify the offending subject** — node ID, edge ID, zone name, etc.
3. **Apply the fix** — e.g., rename ID, add missing field, reorder messages.
4. **Revalidate immediately** — use `node bin/archify.mjs validate < diagram.json` and read the new results.
5. **Repeat until zero errors** — warnings are OK, errors are not.

### Example Repair Loop

**Initial Diagram (Invalid)**
```json
{
  "type": "architecture",
  "nodes": [
    { "id": "auth service", "label": "Auth Service", "color": "security" }
  ]
}
```

**Diagnostic Output**
```
Error: ID 'auth service' contains invalid character (space).
Suggestion: Use 'auth-service' instead.

Error: Missing required field 'version'.
Suggestion: Add "version": "1.0.0"
```

**Repaired Diagram**
```json
{
  "type": "architecture",
  "version": "1.0.0",
  "nodes": [
    { "id": "auth-service", "label": "Auth Service", "color": "security" }
  ]
}
```

**Revalidation Result**
```
✓ Validation passed (0 errors, 0 warnings)
```

---

## Determinism & Bit-Perfect Reproducibility

The validator ensures that **same input → same output**.

### Rules Enforcing Determinism
- IDs must be stable (no randomization, UUIDs, or timestamps)
- Edge ordering (for sequence diagrams) must be explicit and monotonic
- Color assignments must not change based on context
- Layout must be deterministic (no floating-point randomness)

### Verification
```bash
node bin/archify.mjs validate < diagram.json
# SHA-256: a1b2c3d4...
# Size: 2847 bytes

# Later, same diagram:
node bin/archify.mjs validate < diagram.json
# SHA-256: a1b2c3d4... ✓ IDENTICAL
# Size: 2847 bytes ✓ IDENTICAL
```

If checksums differ, the diagram is non-deterministic.

---

## Checklist for LLM Before Delivery

Before running `deliver`, ensure:

- [ ] Schema validation passes (0 errors)
- [ ] All node/edge IDs are stable (no UUIDs, no runtime values)
- [ ] Evidence ties present on 80%+ of high-value nodes
- [ ] No orphaned nodes (all nodes referenced or intentionally isolated)
- [ ] Semantic colors reflect node types
- [ ] Type-specific rules pass (start/end for workflows, order for sequences)
- [ ] Revalidation checksums match (deterministic)

---

## References
- `schema.ts` — TypeScript definitions and Zod schemas
- Examples — See `examples/` for valid diagram specimens
- `bin/archify.mjs` — CLI validator and delivery tool
