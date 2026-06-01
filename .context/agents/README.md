# Super Agent Orchestrator: 11 Sub-Agents

## Overview

The Super Agent Orchestrator is a 14-step pipeline coordinated by 11 specialized agents that analyze multi-repository projects to generate comprehensive engineering intelligence.

**Architecture**: Each agent is independently testable, uses shared models, and produces outputs consumed by subsequent agents.

**Total Steps**: 14 (Steps 1-11 agent execution, Step 12 maturity gate, Step 13-14 reporting)

---

## Agent Execution Pipeline

### Step 1: ProjectDefinitionAgent ✓
**Workspace analysis, technology stack extraction, architecture discovery**

- Discovers repositories and analyzes metadata
- Identifies programming languages, frameworks, databases
- Infers architectural patterns (microservices, monolith, event-driven)
- Outputs: `project_definition.json`, `tech-stack.md`, `architecture.md`

[Full Details →](project-definition-agent.md)

---

### Step 2: RepoScannerAgent ✓
**Deterministic fact extraction, symbol catalog, dependency graph**

- Parses all source files using language-specific analyzers
- Extracts symbols: classes, methods, endpoints, configuration
- Builds inventory of code elements with source references
- Outputs: `inventory.json`, `dependencies.json`, `config.json`

[Full Details →](repo-scanner-agent.md)

---

### Step 3: CodeGraphAgent ✓
**Technical graph construction, semantic relationships, algorithms**

- Converts inventory to traversable graph (nodes + edges)
- Adds semantic edges: inheritance, composition, dependency injection
- Computes graph algorithms: topological sort, circular dependencies
- Outputs: `graph.json`, `graph.graphml`, in-memory NetworkX DiGraph

[Full Details →](code-graph-agent.md)

---

### Step 4: FlowAnalysisAgent ✓
**Business flow discovery, entry points, critical paths**

- Traces execution flows through callgraph
- Identifies entry points (endpoints, consumers, jobs, events)
- Maps data transformations and side effects
- Outputs: `flows.json`, Mermaid flowcharts

[Full Details →](flow-analysis-agent.md)

---

### Step 5: C4DiagramAgent ✓
**C4 context, container, component, code diagrams**

- Generates Level 1-4 C4 architecture diagrams
- Creates technology matrix and deployment topology
- Outputs: Mermaid/PlantUML diagrams, `c4-context.md`

[Full Details →](c4-diagram-agent.md)

---

### Step 6: HTMLSiteAgent ✓
**Interactive documentation portal (4 tabs)**

- Architecture tab: C4 diagrams, narrative, technology
- Tech Stack tab: Versions, dependencies, frameworks
- File Tree tab: Hierarchical file browser with search
- API Endpoints tab: RESTful endpoint catalog

Features: Interactive, responsive, dark mode, export, search

Outputs: `index.html`, assets, embedded data

[Full Details →](html-site-agent.md)

---

### Step 7: RAGAgent ✓
**Searchable code index for semantic queries**

- Indexes source code and documentation
- Creates vector embeddings and full-text indices
- Enables code search, semantic search, faceted queries
- Outputs: `rag-index.json`, embedding vectors

[Full Details →](rag-agent.md)

---

### Step 8: TestIntelligenceAgent ✓
**Test coverage analysis and quality assessment**

- Discovers and analyzes all test files
- Calculates coverage (line, branch, method)
- Assesses test quality (naming, structure, assertions)
- Maps tests to business requirements
- Outputs: `test-report.json`, `test-gaps.md`, recommendations

[Full Details →](test-intelligence-agent.md)

---

### Step 9: TechnicalDebtAgent ✓
**Code quality issues, architecture debt, security vulnerabilities**

- Identifies complexity, duplication, unused code
- Detects circular dependencies, god objects, feature envy
- Finds framework misuse and best practice violations
- Detects security issues: hardcoded secrets, input validation gaps
- Outputs: `technical-debt.json`, `debt-remediation.md`, prioritized issue list

[Full Details →](technical-debt-agent.md)

---

### Step 10: MaturityAgent ✓
**Maturity scoring across 6 dimensions**

- Scores architecture clarity (0-100)
- Scores documentation completeness (0-100)
- Scores test coverage and quality (0-100)
- Scores code quality (0-100)
- Scores technical debt (0-100)
- Scores framework adoption (0-100)
- Calculates weighted overall score

Outputs: `maturity-report.json`, `maturity.md`, overall_score

[Full Details →](maturity-agent.md)

---

### Step 12: Maturity Gate ✓
**Pipeline control: Pass, Fail, or Iterate**

- If maturity_score ≥ target: **PASS** → Proceed to reporting
- If maturity_score < target AND iterations < max: **RETRY** → Resume from Step 4
- If maturity_score < target AND iterations ≥ max: **WARN** → Proceed with warning

---

### Step 13-14: Report Generation & Agent Export
**Final reports, agent definitions, cleanup**

- Generate executive summary (`final_report.md`)
- Export agent definitions to `.context/agents/` (this directory)
- Create deployment guide
- Bundle all outputs for delivery

---

## Execution Model

### Sequential Execution
```
ProjectDefinitionAgent (Step 1)
    ↓
RepoScannerAgent (Step 2)
    ↓
CodeGraphAgent (Step 3)
    ↓
FlowAnalysisAgent (Step 4) ← Iteration re-entry point
    ↓
C4DiagramAgent (Step 5)
    ↓
HTMLSiteAgent (Step 6)
    ↓
RAGAgent (Step 7)
    ↓
TestIntelligenceAgent (Step 8)
    ↓
TechnicalDebtAgent (Step 9)
    ↓
MaturityAgent (Step 10)
    ↓
[Maturity Gate Check]
    ├─ PASS → Reports & Export (Step 13-14)
    ├─ RETRY → Back to Step 4
    └─ WARN → Reports & Export with Warnings
```

### Iteration Strategy
- First iteration: Steps 1-3 run once (foundation)
- Maturity check: Step 10 produces score
- If score < target: **Rerun Steps 4-10** with refined analysis
- Max iterations: 5 (configurable)
- Each iteration adds depth to existing analysis

### Incremental Analysis
- CacheService caches repository state
- Unchanged repos skipped on retry
- Only changed code re-analyzed
- Results merged with previous iteration

---

## Shared Models & Services

### Models (context_builder/models.py)
- `ExecutionContext`: Shared state across agents
- `Graph`: Technical graph (nodes + edges)
- `Node`, `Edge`: Graph elements with metadata
- `Report`: Agent output reports
- Config models: Workspace, Project, Scan, Maturity, TestQuality

### Services (context_builder/services/)
- `CacheService`: Incremental analysis cache
- `GitService`: Repository cloning and file listing
- `GraphService`: Graph export (JSON, GraphML)
- `ScannerService`: File scanning with patterns
- `DiagramService`: Mermaid diagram generation
- `MarkdownService`: Markdown utilities for documentation
- `LoggerService`: Structured logging and formatting

---

## Configuration

### Workspace Definition (.context/workspace-definition.d.yaml)
```yaml
version: "1.0"
workspace:
  id: my-workspace
  name: My Multi-Repo Project
  description: Description
context_root: .context
repositories:
  - id: repo1
    name: Backend Service
    git_url: https://github.com/myorg/repo1.git
    local_path: ./repos/repo1
    type: service
```

### Scan Configuration (.context/scan-config.yaml)
```yaml
include:
  - "**/*.java"
  - "**/*.py"
  - "**/*.ts"
exclude:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/dist/**"
analysis_depth:
  classes: true
  methods: true
  endpoints: true
incremental: true
```

### Maturity Configuration (.context/maturity-config.yaml)
```yaml
target_score: 80
max_iterations: 5
dimensions:
  architecture: 0.20
  documentation: 0.20
  tests: 0.20
  code_quality: 0.15
  technical_debt: 0.15
  framework: 0.10
```

---

## Output Artifacts

### Generated Files (context.generated/)
- `project_definition.json`: Metadata
- `tech-stack.md`: Technology reference
- `architecture.md`: Architecture narrative
- `inventory.json`: Symbol catalog
- `dependencies.json`: Dependency edges
- `graph.json`: Technical graph
- `flows.json`: Business flows
- `c4-context.md`: C4 diagrams
- `index.html`: Interactive portal
- `rag-index.json`: Search index
- `test-report.json`: Coverage and quality
- `technical-debt.json`: Issues and debt
- `maturity-report.json`: Maturity scoring
- `final_report.md`: Executive summary

### Agent Definitions (context/agents/)
- `project-definition-agent.md`: Agent 1 definition (this directory)
- `repo-scanner-agent.md`: Agent 2 definition
- `code-graph-agent.md`: Agent 3 definition
- [... 7 more agent definitions ...]
- `maturity-agent.md`: Agent 10 definition
- `README.md`: This file

---

## Usage

### Basic Execution
```bash
cd my-project
python3 -m context_builder.cli build-context
```

### With Maturity Iteration
```bash
python3 -m context_builder.cli build-context --until-mature
```

### Programmatic Usage
```python
from context_builder.orchestrator import Orchestrator
from pathlib import Path

orch = Orchestrator(Path(".context"))
success = orch.build_context(until_mature=True)
if success:
    context = orch.get_context()
    print(f"Maturity: {orch.get_maturity_score()}/100")
    print(f"Files: {len(orch.get_generated_files())}")
```

---

## Testing

Each agent is independently testable:
```bash
# Test specific agent
pytest tests/test_agents/test_project_definition_agent.py -v

# Test all agents
pytest tests/test_agents/ -v

# Test with coverage
pytest tests/ --cov=context_builder --cov-report=html
```

---

## Agent Interface

All agents implement `BaseAgent`:

```python
class MyAgent(BaseAgent):
    def __init__(self):
        self.name = "MyAgent"
        self.description = "Description"
    
    def execute(self, context: ExecutionContext) -> AgentOutput:
        # Process context
        # Generate artifacts
        return AgentOutput(
            status="success",
            message="Summary",
            artifacts=[Path(...), ...],
            metrics={"count": 123, ...},
            errors=[]
        )
```

---

## Customization

### Add Custom Analyzer
```python
# Create context_builder/analyzers/custom_analyzer.py
from context_builder.analyzers.base_analyzer import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: Path) -> List[Symbol]:
        # Parse file, return symbols
        pass
```

### Add Custom Service
```python
# Create context_builder/services/custom_service.py
class CustomService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def operation(self):
        # Implementation
        pass
```

---

## Performance & Scaling

- **Incremental Analysis**: Unchanged repos skip re-scan
- **Caching**: Repository state cached, used for delta analysis
- **Lazy Loading**: Graph queries on-demand
- **Streaming**: Large file lists streamed, not loaded to memory
- **Parallelization** (future): Independent agents can run in parallel

---

## Support & Troubleshooting

### Enable Debug Logging
```bash
LOGLEVEL=DEBUG python3 -m context_builder.cli build-context
```

### Check Configuration
```bash
python3 -m context_builder.cli check-config
```

### Validate Outputs
```bash
python3 -m context_builder.cli validate
```

---

## References

- [Orchestrator Implementation](../orchestrator.py)
- [Base Agent](../agents/base_agent.py)
- [Data Models](../models.py)
- [Configuration System](../config/loader.py)
- [CLI](../cli.py)

---

## License

Part of the awesome-prompts project. See root LICENSE file.

---

**Generated**: 2026-06-01
**Version**: 1.0.0
