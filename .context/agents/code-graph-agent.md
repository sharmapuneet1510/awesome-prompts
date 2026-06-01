# Code Graph Agent

## Role
Code Graph Agent constructs a traversable technical graph from inventory and dependency data, adding semantic relationships and confidence metrics.

## Responsibilities

### Graph Construction
- Convert inventory symbols to graph nodes
- Map dependency edges with confidence scores
- Add node attributes: repository, module, language, framework role
- Infer implicit edges: inheritance, composition, dependency injection

### Node Types
- **Workspace**: Top-level container
- **Repository**: Source repository
- **Module**: Logical module/package
- **Package**: Language package
- **Class/Interface**: Class and interface definitions
- **Method**: Method or function
- **Endpoint**: HTTP endpoint, consumer, producer
- **Database**: Data store
- **Config**: Configuration file
- **Exception**: Exception/error type

### Edge Types
- **CONTAINS**: Structural containment
- **IMPLEMENTS/EXTENDS**: Inheritance hierarchy
- **CALLS**: Function/method invocation
- **READS_FROM/WRITES_TO**: Data flow
- **PUBLISHES_TO/CONSUMES_FROM**: Event flow (Kafka, RabbitMQ, etc.)
- **USES_CONFIG**: Configuration usage
- **DEPENDS_ON**: Transitive dependency
- **TESTS**: Test coverage relationship

### Graph Algorithms
- Topological sort: determine execution order
- Strongly connected components: identify circular dependencies
- Reachability analysis: trace execution paths
- Centrality metrics: identify critical nodes

## Input
- **context.generated/inventory.json**: Symbol catalog
- **context.generated/dependencies.json**: Dependency edges
- **workspace_config**: Repository layout

## Output
- **context.graph**: In-memory NetworkX DiGraph
- **context.generated/graph.json**: Serialized nodes and edges
- **context.generated/graph.graphml**: GraphML for Neo4j import

## AgentOutput Metrics
- `nodes_created`: Count of nodes in graph
- `edges_created`: Count of edges
- `circular_dependencies`: Count of strongly connected components
- `graph_density`: Edge density metric
- `elapsed_seconds`: Execution time

## Quality Gates
- No nodes without source reference
- No unresolved edges (orphaned targets)
- Confidence scores all in [0, 1.0]
- Graph is acyclic (or cycles properly marked)

## Success Criteria
- [ ] All nodes created from inventory
- [ ] All edges properly typed and confidence-scored
- [ ] Graph exported to JSON, GraphML, and in-memory
- [ ] Circular dependencies identified and logged
- [ ] Reachability queries functional
- [ ] No unresolved references

## Next Step
→ FlowAnalysisAgent (Step 4): Analyze business flows and interactions
