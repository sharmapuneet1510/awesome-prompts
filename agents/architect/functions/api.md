---
name: architect:api Function
description: REST/GraphQL API contract design and OpenAPI specification
prefix: architect:api
version: 3.0
---

# architect:api

**Design API contracts** with OpenAPI specifications, request/response schemas, and authentication.

## Inputs

```
architect:api requirements="..." [style="rest|graphql"]
```

- `requirements` (string, required) — API requirements
- `style` (string, optional) — REST or GraphQL
- `auth` (string, optional) — Authentication method (jwt, oauth2, api-key)

## Outputs

```
✓ openapi.yaml                — OpenAPI 3.0 specification
✓ endpoints.md                — Endpoint documentation
✓ schemas.md                  — Request/response schemas
✓ authentication.md           — Auth implementation guide
```

## Example

```bash
architect:api requirements="Product catalog API: list, get, search, create, update, delete"
```

## Workflow

1. Define endpoints and operations
2. Design request/response schemas
3. Plan authentication and authorization
4. Document error handling
5. Generate OpenAPI spec
6. Plan API versioning
7. Create usage examples

## Related Functions

- `architect:design` — Full system architecture
- `implementer:build` — API implementation
