---
name: architect:frontend Function
description: Frontend architecture - component hierarchy, state management, UI patterns
prefix: architect:frontend
version: 3.0
---

# architect:frontend

**Design frontend architecture** with component hierarchies, state management, and UI patterns.

## Inputs

```
architect:frontend requirements="..." [framework="react"]
```

- `requirements` (string, required) — UI/UX requirements
- `framework` (string, optional) — Framework (react, vue, angular)
- `state_management` (string, optional) — State lib (redux, zustand, context)

## Outputs

```
✓ component-hierarchy.md      — Component tree and relationships
✓ state-management.md         — State flow and patterns
✓ routing.md                  — Page/route structure
✓ ui-patterns.md              — Reusable UI patterns
```

## Example

```bash
architect:frontend requirements="E-commerce: product catalog, shopping cart, checkout, user profile"
```

## Workflow

1. Analyze UI requirements
2. Design component hierarchy
3. Plan state management
4. Define routing structure
5. Identify reusable patterns
6. Plan responsive design
7. Document interaction flows

## Related Functions

- `architect:design` — Full system architecture
- `architect:a11y` — Accessibility planning
- `implementer:build` — Frontend implementation
