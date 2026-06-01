# Architecture: Super Agent Orchestrator

## System Overview

The Super Agent Orchestrator is a Python-based system that analyzes multi-repository projects to generate comprehensive engineering intelligence. It uses a layered architecture with clear separation between coordination, specialization, and implementation.

```
User/CLI
    ↓
Orchestrator (Coordination)
    ↓
11 Sub-Agents (Specialization)
    ├── ProjectDefinitionAgent
    ├── RepoScannerAgent
    ├── CodeGraphAgent
    ├── FlowAnalysisAgent
    ├── C4DiagramAgent
    ├── HTMLSiteAgent
    ├── RAGAgent
    ├── TestIntelligenceAgent
    ├── TechnicalDebtAgent
    └── MaturityAgent
    ↓
Services (Reusable Utilities)
    ├── CacheService
    ├── GitService
    ├── GraphService
    ├── ScannerService
    ├── DiagramService
    ├── MarkdownService
    └── LoggerService
    ↓
Analyzers (Language-Specific)
    ├── JavaAnalyzer
    ├── PythonAnalyzer
    ├── TypeScriptAnalyzer
    └── ... (more)
    ↓
Data Layer
    ├── ExecutionContext
    ├── Graph
    ├── Models
    └── Configuration
```

---

## Core Components

### 1. Orchestrator (context_builder/orchestrator.py)

**Responsibility**: Coordinate 11 agents through a 14-step pipeline.

**Key Methods**:
- `build_context(until_mature)`: Main entry point
- `_load_configs()`: Load configuration files
- `_initialize_context()`: Create ExecutionContext
- `_register_agents()`: Register all sub-agents
- `_execute_agents()`: Run agents in sequence
- `_check_maturity_gate()`: Evaluate maturity score
- `_generate_final_report()`: Create output reports

**Flow**:
```
STEP 0: Load configs & Initialize
STEP 1-11: Execute agents
STEP 12: Check maturity gate
    ├─ PASS → STEP 13-14
    ├─ RETRY → Back to STEP 4
    └─ WARN → STEP 13-14 with warnings
STEP 13-14: Generate reports & export agents
```

**Maturity Iteration**:
- First run: Steps 1-3 (foundation)
- Maturity check: Step 10 produces score
- If score < target: Rerun Steps 4-10 (refinement)
- Max iterations: 5 (configurable)

### 2. Execution Context (context_builder/models.py)

**Responsibility**: Shared state across all agents.

**Structure**:
```python
class ExecutionContext:
    workspace_config: Optional[WorkspaceConfig]
    project_config: Optional[ProjectConfig]
    tech_aliases: Optional[TechAliases]
    scan_config: ScanConfig
    maturity_config: MaturityConfig
    test_quality_config: TestQualityConfig
    
    graph: Graph                    # Technical graph
    reports: Dict[str, Report]      # Agent outputs
    iteration: int                  # Current iteration
    generated_files: List[Path]     # Output artifacts
    
    cache: Optional[Any]            # CacheService
    logger: Optional[Any]           # Logger
```

**Usage**: Every agent receives context, reads inputs, writes outputs.

### 3. Sub-Agents (context_builder/agents/)

**Base Class**: BaseAgent

```python
class BaseAgent:
    name: str
    description: str
    
    def execute(self, context: ExecutionContext) -> AgentOutput:
        # Implement specific analysis
        return AgentOutput(
            status="success" or "failure",
            message="Summary",
            artifacts=[Path, ...],        # Generated files
            metrics={"count": 123, ...},  # Measurements
            errors=["error1", ...]        # Issues
        )
```

**Agent Order** (dependency-based):
```
1. ProjectDefinitionAgent (discovers repos, tech stacks)
2. RepoScannerAgent (extracts symbols from code)
3. CodeGraphAgent (builds traversable graph)
4. FlowAnalysisAgent (identifies business flows) ← Iteration re-entry
5. C4DiagramAgent (generates architecture diagrams)
6. HTMLSiteAgent (creates interactive portal)
7. RAGAgent (builds searchable index)
8. TestIntelligenceAgent (analyzes test coverage)
9. TechnicalDebtAgent (identifies issues)
10. MaturityAgent (scores overall maturity)
```

### 4. Services (context_builder/services/)

Reusable utility modules:

| Service | Purpose | Key Methods |
|---------|---------|-------------|
| CacheService | Incremental analysis | save_repo_hash, is_repo_unchanged |
| GitService | Repository ops | clone_repo, list_files |
| GraphService | Graph operations | export_to_json, export_to_graphml |
| ScannerService | File scanning | scan_directory, count_files, get_file_stats |
| DiagramService | Diagram generation | generate_architecture_diagram, generate_flow_diagram |
| MarkdownService | Markdown utils | create_document, create_table, create_code_block |
| LoggerService | Logging | setup_console_handler, setup_file_handler |

---

## Data Flow

### Step 1-3: Foundation (No Iteration)

```
ProjectDefinitionAgent
├─ Input: workspace_config, project_config
├─ Process: Discover repos, detect languages/frameworks
└─ Output: project_definition.json, tech-stack.md
    ↓
RepoScannerAgent
├─ Input: project_definition.json
├─ Process: Parse all source files, extract symbols
└─ Output: inventory.json, dependencies.json
    ↓
CodeGraphAgent
├─ Input: inventory.json, dependencies.json
├─ Process: Build graph, compute algorithms
└─ Output: graph.json, graph.graphml
    ↓
[ExecutionContext has: graph, reports, generated_files]
```

### Step 4-10: Analysis (Can Iterate)

```
FlowAnalysisAgent
├─ Input: context.graph
├─ Process: Trace execution paths, identify flows
└─ Output: flows.json
    ↓
C4DiagramAgent
├─ Input: context.graph, flows
├─ Process: Generate C4 diagrams
└─ Output: c4-context.md
    ↓
HTMLSiteAgent
├─ Input: All previous reports
├─ Process: Create interactive HTML portal
└─ Output: index.html, assets/
    ↓
RAGAgent
├─ Input: context.graph, source code
├─ Process: Build search index
└─ Output: rag-index.json
    ↓
TestIntelligenceAgent
├─ Input: inventory.json (test refs)
├─ Process: Analyze coverage, quality
└─ Output: test-report.json
    ↓
TechnicalDebtAgent
├─ Input: context.graph, code patterns
├─ Process: Identify issues, security, perf
└─ Output: technical-debt.json
    ↓
MaturityAgent
├─ Input: All reports
├─ Process: Score maturity by dimension
└─ Output: maturity-report.json, overall_score
    ↓
[Maturity Gate Check]
```

### Step 12: Maturity Gate

```
MaturityAgent produces score (0-100)
    ↓
if score >= target_score:
    → PASS (Step 13-14)
elif iteration < max_iterations:
    → RETRY (Back to Step 4)
else:
    → WARN (Step 13-14 with warnings)
```

### Step 13-14: Report Generation

```
Orchestrator._generate_final_report()
├─ Collect all reports
├─ Write final_report.md
├─ Export agent definitions to .context/agents/
└─ List all generated artifacts
```

---

## Configuration System

Located in `.context/` directory with YAML files:

```
.context/
├── workspace-definition.d.yaml     # Workspace & repos
├── project-definition.d.yaml       # Project metadata
├── scan-config.yaml                # Include/exclude patterns
├── maturity-config.yaml            # Scoring & iterations
├── test-quality-config.yaml        # Test metrics
└── [generated outputs]
    ├── project_definition.json
    ├── inventory.json
    ├── graph.json
    ├── flows.json
    ├── c4-context.md
    ├── index.html
    ├── rag-index.json
    ├── test-report.json
    ├── technical-debt.json
    ├── maturity-report.json
    └── final_report.md
```

**Configuration Loading** (config/loader.py):
1. Check if file exists
2. Parse YAML
3. Validate schema
4. Return config or defaults

---

## Graph Data Structure

### Nodes

Represent code elements with metadata:

```python
@dataclass
class Node:
    id: str                           # Unique ID
    type: NodeType                    # CLASS, METHOD, ENDPOINT, etc.
    name: str                         # Human-readable name
    repository: Optional[str]         # Which repo
    module: Optional[str]             # Package/module
    path: Optional[str]               # File path
    language: Optional[str]           # java, python, typescript, etc.
    framework_role: Optional[str]     # spring, fastapi, react, etc.
    attributes: Dict[str, Any]        # Custom metadata
```

**NodeTypes**: WORKSPACE, REPOSITORY, MODULE, PACKAGE, CLASS, INTERFACE, METHOD, ENDPOINT, CONSUMER, PRODUCER, DATABASE, MIDDLEWARE, CONFIG_FILE, EXCEPTION, BUSINESS_FLOW, TEST_CLASS, TECHNICAL_DEBT, RISK, etc.

### Edges

Represent relationships with confidence:

```python
@dataclass
class Edge:
    source: str                       # Source node ID
    target: str                       # Target node ID
    type: EdgeType                    # CALLS, CONTAINS, IMPLEMENTS, etc.
    confidence: float                 # 0.0-1.0 confidence score
    source_reference: Optional[str]   # File:line reference
    attributes: Dict[str, Any]        # Custom metadata
```

**EdgeTypes**: CONTAINS, IMPLEMENTS, EXTENDS, CALLS, READS_FROM, WRITES_TO, PUBLISHES_TO, CONSUMES_FROM, THROWS, HANDLES, USES_CONFIG, PART_OF_FLOW, DEPENDS_ON, TESTS, COVERS, LACKS_TEST_FOR, HAS_RISK, HAS_TECH_DEBT

### Graph Operations

```python
graph.add_node(node)                  # Add node (skip if exists)
graph.add_edge(edge)                  # Add edge (skip if exists)
graph.find_node(node_id)              # Find node by ID
graph.to_dict()                       # JSON-serialize
```

---

## Analyzers (Language-Specific)

### Base Analyzer Pattern

```python
from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, file_path: Path) -> List[Symbol]:
        """Parse file, return symbols with source refs."""
        pass
```

### Supported Analyzers

| Language | Analyzer | Parser | Key Symbols |
|----------|----------|--------|------------|
| Java | JavaAnalyzer | javalang AST | Classes, methods, annotations |
| Python | PythonAnalyzer | ast module | Classes, functions, decorators |
| TypeScript | TSAnalyzer | tree-sitter | Classes, interfaces, decorators |
| YAML | YAMLAnalyzer | yaml parser | Keys, sections |
| JSON | JSONAnalyzer | json parser | Objects, arrays |

### Symbol Types

```python
@dataclass
class Symbol:
    id: str                     # Unique ID
    type: SymbolType            # CLASS, METHOD, FUNCTION, etc.
    name: str
    file: Path
    line: int                   # Starting line
    language: str
    attributes: Dict[str, Any]  # Framework-specific data
    confidence: float = 1.0     # 0.0-1.0
```

---

## Testing Architecture

### Test Organization

```
tests/
├── test_models.py              # Data models
├── test_services/              # Services
│   ├── test_scanner_service.py
│   ├── test_diagram_service.py
│   ├── test_markdown_service.py
│   └── test_logger_service.py
├── test_agents/                # Individual agents
│   ├── test_project_definition_agent.py
│   ├── test_repo_scanner_agent.py
│   └── ... (more)
├── test_integration/           # End-to-end
│   └── test_full_pipeline.py
└── fixtures/                   # Test data
    ├── java_spring_boot_sample.py
    └── python_fastapi_sample.py
```

### Test Coverage

**Total Tests**: 1000+ (1004 as of current implementation)

**By Category**:
- Models: 50 tests
- Services: 63 tests
  - ScannerService: 11 tests
  - DiagramService: 11 tests
  - MarkdownService: 22 tests
  - LoggerService: 19 tests
- Agents: 800+ tests (10 agents × 80+ tests each)
- Integration: 20+ tests
- Config: 50+ tests

### Test Fixtures

**Sample Projects**:
- JavaSpringBootSample: Full Java/Spring project
- PythonFastAPISample: Full Python/FastAPI project

**Features**:
- Controller, Service, Repository, Entity classes
- Test files (JUnit, Pytest)
- Configuration files (POM, requirements.txt)
- Ready for full pipeline analysis

---

## Output Formats

### JSON Artifacts

**graph.json**: Complete technical graph
```json
{
  "nodes": [
    {"id": "class:A", "type": "Class", "name": "A", ...},
    {"id": "method:A.foo", "type": "Method", "name": "foo", ...}
  ],
  "edges": [
    {"source": "class:A", "target": "method:A.foo", "type": "CONTAINS", ...}
  ]
}
```

**inventory.json**: Symbol catalog
```json
[
  {"id": "class:Service", "type": "Class", "file": "src/Service.java", ...},
  {"id": "method:Service.process", "type": "Method", ...}
]
```

### Markdown Artifacts

**architecture.md**: Narrative with diagrams
```markdown
# Architecture

## Overview
System consists of X services...

## C4 Diagram Level 1
[Mermaid diagram]

## Technology Stack
| Component | Technology |
```

### HTML Portal

**index.html**: 4-tab interactive interface
- Tab 1: Architecture (C4 diagrams, narrative)
- Tab 2: Tech Stack (versions, frameworks)
- Tab 3: File Tree (hierarchical browser)
- Tab 4: API Endpoints (catalog, examples)

---

## Performance Characteristics

### Time Complexity

| Step | Complexity | Notes |
|------|-----------|-------|
| ProjectDefinitionAgent | O(R) | Linear in repos |
| RepoScannerAgent | O(F × L) | Files × average lines |
| CodeGraphAgent | O(N + E) | Nodes + edges |
| FlowAnalysisAgent | O(E × P) | Edges × path length |
| C4DiagramAgent | O(N) | Number of nodes |
| HTMLSiteAgent | O(N + E) | Linear |
| RAGAgent | O(D × E) | Documents × embedding |
| MaturityAgent | O(1) | Constant (aggregation) |

### Space Complexity

- Graph: O(N + E) nodes and edges
- Cache: O(R) repository hashes
- Index: O(D) documents
- Reports: O(R + D) data

### Optimization Strategies

1. **Incremental Analysis**: Cache repo state, skip unchanged
2. **Lazy Evaluation**: Compute metrics on-demand
3. **Streaming**: Process large files line-by-line
4. **Caching**: LRU cache for graph queries
5. **Parallelization** (future): Run independent agents in parallel

---

## Error Handling

### Error Categories

| Category | Severity | Action |
|----------|----------|--------|
| Critical | High | Halt orchestration |
| Warning | Medium | Log and continue |
| Info | Low | Log only |

### Critical Errors

- ProjectDefinitionAgent failure (repos not found)
- RepoScannerAgent failure (parsing errors on all files)
- Config loading failure

### Non-Critical Errors

- Missing test files (log and continue)
- Unsupported language (skip files)
- Ambiguous framework detection (log with confidence)

---

## Extension Points

### Add Custom Analyzer

```python
# Create context_builder/analyzers/custom_analyzer.py
from context_builder.analyzers.base_analyzer import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: Path) -> List[Symbol]:
        # Implement custom parsing
        return [Symbol(...), ...]
```

### Add Custom Service

```python
# Create context_builder/services/custom_service.py
class CustomService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def operation(self):
        # Implement operation
        pass
```

### Add Custom Agent

```python
# Create context_builder/agents/custom_agent.py
from context_builder.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        self.name = "CustomAgent"
        self.description = "Custom agent description"
    
    def execute(self, context: ExecutionContext) -> AgentOutput:
        # Implement agent logic
        return AgentOutput(...)
```

---

## Technology Stack

- **Python 3.9+**: Core language
- **Pydantic**: Data models and validation
- **PyYAML**: Configuration files
- **NetworkX**: Graph algorithms
- **GitPython**: Git operations
- **tree-sitter**: Language parsing
- **javalang**: Java AST parsing
- **Jinja2**: Template rendering
- **FastAPI**: CLI framework (Typer)
- **pytest**: Testing framework

---

## Future Enhancements

1. **Parallel Execution**: Run independent agents simultaneously
2. **ML-Powered Analysis**: Use ML for pattern detection
3. **Custom Rules**: Allow user-defined analysis rules
4. **Real-time Updates**: Stream results as they're generated
5. **Graph Database**: Export to Neo4j for interactive exploration
6. **API Server**: RESTful API for remote analysis
7. **Multi-language Support**: More language analyzers
8. **Performance Profiling**: Identify bottlenecks

---

## References

- **Design Pattern**: Orchestrator + Specialist + Decorator pattern
- **Graph Theory**: Topological sort, strongly connected components
- **Software Architecture**: C4 model for architecture visualization
- **Clean Code**: SOLID principles, separation of concerns

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-01  
**Total Lines of Code**: 15,000+  
**Total Test Coverage**: 1000+ tests
