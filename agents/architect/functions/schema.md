---
name: architect:schema Function
description: Database schema generation and optimization
prefix: architect:schema
version: 3.0
---

# architect:schema

**Design and optimize database schemas** with relationships, indices, constraints, and migrations.

## Inputs

```
architect:schema requirements="..." [db_type="postgresql"]
```

- `requirements` (string, required) — Data model requirements
- `db_type` (string, optional) — Database type (postgresql, mysql, mssql)
- `scale` (string, optional) — Expected scale (small, medium, enterprise)

## Outputs

```
✓ schema.sql                  — Complete DDL with relationships
✓ migrations/                 — Versioned migration scripts
✓ indices.sql                 — Performance indices
✓ relationships-diagram.md    — ER diagram and descriptions
```

## Example

```bash
architect:schema requirements="E-commerce: products, orders, inventory, customers"
```

## Workflow

1. Parse data requirements
2. Design entities and relationships
3. Normalize schema (3NF+)
4. Add indices for common queries
5. Plan migration strategy
6. Document relationships
7. Consider scaling and partitioning

## Related Functions

- `architect:design` — Full system architecture
- `implementer:full` — Implementation with schema
