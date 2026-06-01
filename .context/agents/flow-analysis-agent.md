# Flow Analysis Agent

## Role
Flow Analysis Agent traces business processes, user journeys, and critical flows through the codebase, identifying entry points, decision trees, and data flows.

## Responsibilities

### Flow Discovery
- Identify entry points (HTTP endpoints, consumers, scheduled jobs, event handlers)
- Trace execution paths through callgraph
- Detect decision points (if/switch statements, branching logic)
- Map data transformations
- Identify side effects (I/O, database, external calls)

### Flow Types
- **Request/Response**: HTTP request → response cycle
- **Event-Driven**: Event publication → consumption chain
- **Batch**: Scheduled job execution
- **Data Pipeline**: ETL flow with transformations
- **User Journey**: Multi-step user interaction sequence

### Analysis Depth
- Critical paths: high-traffic, business-critical flows
- Error paths: exception handling and recovery
- Optimization hotspots: loops, recursive calls, complex logic
- Security boundaries: authentication, authorization checks

## Input
- **context.graph**: Technical graph from CodeGraphAgent
- **context.generated/inventory.json**: Symbol catalog
- **scan_config**: Analysis depth settings

## Output
- **context.generated/flows.json**: Discovered flows with entry/exit points
- **context.flows**: In-memory flow objects
- **Mermaid flowcharts**: Generated for critical paths

## AgentOutput Metrics
- `flows_discovered`: Count of unique business flows
- `entry_points_found`: Count of identified entry points
- `critical_paths`: Count of high-criticality flows
- `flow_complexity`: Average path length
- `elapsed_seconds`: Execution time

## Flow Representation
```json
{
  "name": "User Registration",
  "type": "Request/Response",
  "entry": "POST /api/auth/register",
  "steps": [
    {"action": "ValidateInput", "confidence": 0.95},
    {"action": "CheckEmailUnique", "confidence": 0.90},
    {"action": "HashPassword", "confidence": 0.99},
    {"action": "CreateUser", "confidence": 0.95}
  ],
  "exit": "201 Created",
  "criticality": "high"
}
```

## Success Criteria
- [ ] All endpoint entry points identified
- [ ] Critical flows traced end-to-end
- [ ] Flow complexity within acceptable bounds
- [ ] No orphaned flow segments
- [ ] Mermaid diagrams generate successfully
- [ ] Flow metrics computed

## Next Step
→ C4DiagramAgent (Step 5): Generate architecture diagrams
