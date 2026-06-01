# C4 Diagram Agent

## Role
C4 Diagram Agent generates C4 context, container, component, and code-level architecture diagrams for visualization of system structure at multiple abstraction levels.

## Responsibilities

### C4 Level Generation

#### Level 1: Context Diagram
- System as single box
- External systems and actors
- High-level interactions
- Technology-agnostic view

#### Level 2: Container Diagram
- Internal containers (microservices, applications, databases, message brokers)
- Container-to-container relationships
- Technology choices (Spring Boot, React, PostgreSQL, Kafka)
- Deployment unit boundaries

#### Level 3: Component Diagram
- Internal components within containers
- Key responsibilities
- Component interactions
- Technology-specific (e.g., Spring @Service, @Repository)

#### Level 4: Code Diagram (optional)
- Class hierarchies
- Method-level interactions
- Package structure
- For complex components only

### Diagram Generation
- Generate PlantUML and Mermaid formats
- Create context.md document with all 4 levels
- Include technology matrix (language, framework, database per container)
- Add deployment topology diagram

## Input
- **context.graph**: Technical graph with node/edge metadata
- **context.generated/project_definition.json**: Project and tech stack info
- **context.flows**: Identified business flows

## Output
- **context.generated/c4-context.md**: Level 1-4 diagrams
- **context.generated/c4-context.mmd**: Mermaid format
- **context.generated/deployment-topology.mmd**: Deployment diagram
- **context.diagrams**: In-memory diagram objects

## AgentOutput Metrics
- `contexts_generated`: Count of C4 diagrams created
- `containers_identified`: Count of deployment units
- `components_mapped`: Count of internal components
- `diagram_complexity`: Total nodes/edges in all diagrams
- `elapsed_seconds`: Execution time

## Diagram Quality
- No isolated components (all must connect to something)
- Clear containment hierarchy (no orphaned nodes)
- Consistent naming conventions
- Technology labels on all edges
- Legend and metadata for each diagram

## Success Criteria
- [ ] All 4 C4 levels generated
- [ ] Diagrams are acyclic and consistent
- [ ] Every container has clear responsibility
- [ ] Technology choices clearly documented
- [ ] Deployment topology shows infrastructure
- [ ] Diagrams render without errors in Mermaid/PlantUML

## Next Step
→ HTMLSiteAgent (Step 6): Create interactive HTML portal
