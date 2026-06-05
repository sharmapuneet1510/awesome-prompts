---
name: architect:design Function
description: Greenfield system design - topology, API contracts, DB schema, UI architecture
prefix: architect:design
version: 3.0
---

# architect:design

**Design new systems from scratch** with complete architecture, API contracts, and database schemas.

## Inputs

```
architect:design requirements="..."
```

- `requirements` (string, required) — System requirements or feature description
- `context` (string, optional) — Existing architecture context
- `tech_stack` (string, optional) — Preferred technologies (e.g., "Python, FastAPI, PostgreSQL, React")

## Outputs

```
✓ system-architecture.md      — System topology, components, data flow
✓ api-contract.md             — OpenAPI/REST specifications
✓ database-schema.md          — DDL, relationships, indices
✓ ui-architecture.md          — Frontend component hierarchy
✓ deployment-diagram.md       — Infrastructure topology
```

## Example

```bash
architect:design requirements="Build e-commerce platform with product catalog, shopping cart, and checkout"
```

**Output:**
- System topology (microservices vs monolith)
- API design (products, orders, payments)
- Database schema (products, orders, inventory)
- UI structure (catalog, cart, checkout flows)
- Deployment architecture (load balancers, databases, caches)

## Workflow

1. Parse requirements and constraints
2. Determine system topology (monolith, microservices, serverless)
3. Design API contracts (REST, GraphQL, gRPC)
4. Create database schema with relationships
5. Plan UI component hierarchy
6. Define deployment strategy
7. Document all decisions with rationale

## Related Functions

- `architect:schema` — Database schema generation only
- `architect:api` — REST API contract design only
- `architect:refactor` — Brownfield migration planning
