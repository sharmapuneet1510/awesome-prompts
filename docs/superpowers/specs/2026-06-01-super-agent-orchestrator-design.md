---
title: Super Agent Orchestrator — Complete Design Spec
date: 2026-06-01
version: 1.0
status: approved
scope: Full implementation (11 sub-agents, 14-step pipeline, multi-platform export)
---

# Super Agent Orchestrator — Design Specification

## Executive Summary

The **Super Agent Orchestrator** is a Python-based system that analyzes multi-repository software projects and generates complete engineering intelligence (architecture docs, maturity scores, test quality analysis, technical debt reports, interactive graphs, and HTML portal).

**Key Design Decisions:**
- Separate Python modules for each sub-agent (export-friendly)
- Both CLI tool and importable library
- 14-step pipeline with maturity iteration
- Multi-platform support (Claude, Copilot, Cursor, GitHub, Gemini, etc.)
- Full implementation of all 11 sub-agents in Phase 1

---

## Architecture Overview

### Layered Design

```
┌─────────────────────────────────────────────────┐
│  CLI Layer (context-builder command)            │
├─────────────────────────────────────────────────┤
│  Orchestrator (orchestrator.py)                 │
│  - Coordinates 11 sub-agents in sequence        │
│  - Manages state & .context folder              │
│  - Detects iteration/maturity gates             │
├─────────────────────────────────────────────────┤
│  Sub-Agent Layer (agents/*)                     │
│  - 11 independent agents with clear boundaries  │
│  - Standard interface: execute(context)         │
│  - Reusable across platforms                    │
├─────────────────────────────────────────────────┤
│  Core Services Layer                            │
│  - Config management                            │
│  - Graph building & operations                  │
│  - File scanning & parsing                      │
│  - Cache & state management                     │
├─────────────────────────────────────────────────┤
│  External Integration                           │
│  - token_optimizer (query analysis, optional)   │
│  - parser (Java/Maven field derivation)         │
│  - exporter (export to 8 LLM platforms)         │
└─────────────────────────────────────────────────┘
```

**Design Principle:** Separate data gathering (parsing, graph building) from AI explanation (LLM annotation). This makes the system platform-agnostic — any LLM can wrap it.

---

## Package Structure

### Directory Layout

```
context_builder/
├── __init__.py
├── cli.py                          # Entry point (context-builder command)
├── orchestrator.py                 # Main coordinator (14-step pipeline)
├── models.py                       # Shared data models
├── config/
│   ├── __init__.py
│   ├── workspace_config.py         # Workspace definition (repos, GitLab)
│   ├── project_config.py           # Project definition (tech stack, entry points)
│   ├── tech_aliases.py             # Tech mapping (e.g., DataFabric → Pulsar)
│   ├── scan_config.py              # File scanning rules
│   ├── output_config.py            # Output formats (HTML, Markdown, Graph)
│   ├── c4_config.py                # C4 diagram rules
│   ├── maturity_config.py          # Maturity scoring weights
│   ├── test_quality_config.py      # Test evaluation rules
│   └── loader.py                   # Config initialization
├── agents/
│   ├── __init__.py
│   ├── base_agent.py               # Base class for all sub-agents
│   ├── project_definition_agent.py # Agent 1
│   ├── repo_scanner_agent.py       # Agent 2
│   ├── code_graph_agent.py         # Agent 3
│   ├── flow_analysis_agent.py      # Agent 4
│   ├── c4_diagram_agent.py         # Agent 5
│   ├── html_site_agent.py          # Agent 6
│   ├── rag_agent.py                # Agent 7
│   ├── test_intelligence_agent.py  # Agent 8
│   ├── technical_debt_agent.py     # Agent 9
│   ├── maturity_agent.py           # Agent 10
│   └── super_agent_orchestrator.py # Agent 11 (also exportable)
├── services/
│   ├── __init__.py
│   ├── git_service.py              # GitPython wrapper
│   ├── scanner_service.py          # File scanning & parsing
│   ├── graph_service.py            # Graph operations
│   ├── cache_service.py            # Cache management
│   ├── diagram_service.py          # Diagram generation
│   └── markdown_service.py         # Markdown generation for RAG
├── analyzers/
│   ├── __init__.py
│   ├── java_analyzer.py            # Java/Spring Boot parsing
│   ├── python_analyzer.py          # Python analysis
│   ├── typescript_analyzer.py      # TypeScript/JavaScript
│   ├── config_analyzer.py          # YAML/XML/properties
│   ├── db_analyzer.py              # SQL schema detection
│   └── middleware_analyzer.py      # Pulsar/messaging detection
├── output/
│   ├── __init__.py
│   ├── markdown_writer.py          # Markdown book generation
│   ├── html_writer.py              # Single-page HTML portal
│   ├── graph_writer.py             # Graph export (JSON, GraphML)
│   └── json_writer.py              # Report JSON (maturity, tests, risk)
├── utils/
│   ├── __init__.py
│   ├── logger.py                   # Progress logging
│   ├── file_utils.py               # Path & directory handling
│   └── validator.py                # Input validation
└── tests/
    ├── conftest.py
    ├── test_orchestrator.py
    ├── test_agents/                # One test file per agent
    ├── test_services/
    ├── test_analyzers/
    ├── test_output/
    └── fixtures/                   # Sample projects, configs
```

### Generated Output Structure

```
.context/                           # User's project folder
├── instruction.md
├── workspace-definition.d.yaml
├── project-definition.d.yaml
├── tech-aliases.yaml
├── scan-config.yaml
├── output-config.yaml
├── c4-config.yaml
├── maturity-config.yaml
├── test-quality-config.yaml
├── agents/                         # Generated agent definitions (exportable)
│   ├── 00-super-agent-orchestrator.md
│   ├── 01-project-definition-agent.md
│   └── ... (11 total)
├── cache/
│   ├── repo-hashes.json
│   └── scan-state.json
└── generated/
    ├── book-md/                    # Markdown book (15+ files)
    ├── site-html/                  # Single-page HTML portal
    ├── diagrams/                   # Mermaid & C4 diagrams
    ├── graph/                      # nodes.json, edges.json, graphml
    ├── rag/                        # RAG chunks + metadata
    └── reports/                    # Maturity, test quality, risk reports
```

---

## The 14-Step Pipeline

### Execution Sequence

```
Step 1:  Initialize .context folder
         └─ Create directories, load/generate default configs

Step 2:  Detect repositories
         └─ Parse workspace-definition.yaml, clone/pull repos

Step 3:  Generate workspace & project definitions
         └─ ProjectDefinitionAgent detects modules, tech stack, entry points

Step 4:  Scan source code and config files
         └─ RepoScannerAgent extracts facts (classes, endpoints, topics, tables)
         └─ Output: scan-report.md, raw-symbols.json

Step 5:  Build raw symbol map
         └─ Parse Java, Python, TypeScript, SQL, YAML, XML files

Step 6:  Build graph nodes and edges
         └─ CodeGraphAgent creates traversable technical graph
         └─ Output: nodes.json, edges.json, graph.graphml

Step 7:  Analyze flows (API, message, batch)
         └─ FlowAnalysisAgent traces end-to-end flows
         └─ Output: flow-analysis.md, exception-flow.md, flow-*.mmd

Step 8:  Analyze DB and middleware
         └─ Extract DB schemas, middleware topics, tech aliases

Step 9:  Analyze exception handling & error flows
         └─ Detect retry, rollback, timeout, failure behavior

Step 10: Analyze tests & test maturity
         └─ TestIntelligenceAgent evaluates test quality (not just %)
         └─ Output: test-quality-matrix.md, test-quality-matrix.json

Step 11: Analyze technical debt & bottlenecks
         └─ TechnicalDebtAgent detects risks, large classes, circular deps
         └─ Output: technical-debt.md, bottlenecks.md, risk-report.md

Step 12: Generate C4 & Mermaid diagrams
         └─ C4DiagramAgent creates C4 context/container/component diagrams
         └─ Output: c4-context.mmd, c4-container.mmd, c4-component-*.mmd

Step 13: Generate Markdown book
         └─ MarkdownService creates 15+ AI-optimized Markdown files
         └─ Output: book-md/ (index.md, architecture.md, flow-analysis.md, etc.)

Step 14: Generate single-page HTML portal
         └─ HTMLSiteAgent creates interactive dashboard
         └─ Output: index.html (Mermaid.js + Cytoscape.js + embedded data)

Step 15: Generate RAG chunks
         └─ RAGAgent chunks Markdown for vector DB indexing
         └─ Output: chunks.jsonl, index-metadata.json

Step 16: Calculate maturity score
         └─ MaturityAgent scores 8 dimensions, generates next actions
         └─ Output: maturity-score.json, maturity-report.md, next-actions.md

Step 17: Check maturity gate
         └─ If score < target AND iterations < max:
            └─ Goto Step 7 (focused re-analysis)
         └─ Else: DONE
```

### Key Behaviors

- **Incremental:** Skip completed steps if configs/outputs already exist
- **Iterative maturity:** Re-analyze flows & technical debt until maturity target or max iterations
- **Caching:** Cache repo hashes; skip unchanged repos
- **All outputs under `.context/generated/`**

---

## The 11 Sub-Agents

### Standard Agent Interface

```python
class BaseAgent:
    def execute(self, context: ExecutionContext) -> AgentOutput:
        """
        Execute the agent and return structured results.
        
        Args:
            context: ExecutionContext with configs, graph, reports
        
        Returns:
            AgentOutput with status, artifacts, metrics
        """
        pass
```

### Agent Responsibilities

| # | Agent | Input | Output | Key Responsibility |
|---|-------|-------|--------|-------------------|
| 1 | **ProjectDefinitionAgent** | Repos detected | project-definition.d.yaml | Detect modules, tech stack, entry points, business purpose |
| 2 | **RepoScannerAgent** | workspace-definition.yaml | scan-report.md, raw-symbols.json | Deterministic fact extraction: classes, endpoints, configs, DB |
| 3 | **CodeGraphAgent** | raw-symbols.json | nodes.json, edges.json, graph.graphml | Build traversable technical graph with relationships |
| 4 | **FlowAnalysisAgent** | nodes.json, edges.json | flow-analysis.md, exception-flow.md, flow-*.mmd | Trace API→DB→middleware flows, exception handling |
| 5 | **C4DiagramAgent** | nodes.json, project-definition.yaml | c4-context.mmd, c4-container.mmd, c4-component-*.mmd | Generate C4-style architecture diagrams (Mermaid) |
| 6 | **HTMLSiteAgent** | All generated files (MD, graphs, diagrams) | index.html | Single-page interactive portal (Mermaid.js + Cytoscape.js) |
| 7 | **RAGAgent** | book-md/*.md, graph data | chunks.jsonl, index-metadata.json | Chunk & prepare Markdown for RAG/vector DB indexing |
| 8 | **TestIntelligenceAgent** | Source code, tests, coverage reports | test-quality-matrix.md/.json, test-intelligence.md | Evaluate test maturity (coverage %, assertion quality, negative tests) |
| 9 | **TechnicalDebtAgent** | nodes.json, source code | technical-debt.md, bottlenecks.md, risk-report.md | Detect large classes, circular deps, weak exception handling |
| 10 | **MaturityAgent** | All reports, graph data | maturity-score.json, maturity-report.md, next-actions.md | Score 8 dimensions; generate actionable next steps |
| 11 | **SuperAgentOrchestrator** | All sub-agent outputs | (coordinates, validates, iterates) | Master coordinator; also exportable as agent definition |

### Shared ExecutionContext

```python
class ExecutionContext:
    workspace_config: WorkspaceConfig         # .context/workspace-definition.d.yaml
    project_config: ProjectConfig            # .context/project-definition.d.yaml
    tech_aliases: TechAliases                # .context/tech-aliases.yaml
    scan_config: ScanConfig                  # .context/scan-config.yaml
    maturity_config: MaturityConfig          # .context/maturity-config.yaml
    test_quality_config: TestQualityConfig   # .context/test-quality-config.yaml
    
    graph: Graph                             # Accumulated nodes/edges
    reports: Dict[str, Report]               # Accumulated findings
    iteration: int                           # Current maturity iteration
    generated_files: List[Path]              # All output file paths
    
    cache: CacheManager                      # Repo hashes, scan state
    logger: Logger                           # Progress logging
```

---

## Data Flow

### Pipeline Dataflow Diagram

```
Git Repos (clone/pull via GitService)
    ↓
[ProjectDefinitionAgent]
    ↓ project-definition.d.yaml
    ↓
[RepoScannerAgent] → raw-symbols.json (classes, endpoints, topics, tables)
    ↓
[CodeGraphAgent] → nodes.json, edges.json, graph.graphml
    ↓
[FlowAnalysisAgent] → flow-analysis.md, exception-flow.md, flow-*.mmd
    ↓
[C4DiagramAgent] → c4-*.mmd (context, container, component)
    ↓
[TestIntelligenceAgent] → test-quality-matrix.json, test-intelligence.md
    ↓
[TechnicalDebtAgent] → technical-debt.md, bottlenecks.md, risk-report.md
    ↓
[MarkdownService] → book-md/ (15+ files, AI-optimized)
    ↓
[HTMLSiteAgent] → index.html (Mermaid.js + Cytoscape.js, all data embedded)
    ↓
[RAGAgent] → chunks.jsonl, index-metadata.json
    ↓
[MaturityAgent] → maturity-score.json, maturity-report.md, next-actions.md
    ↓
Decision: maturity < target AND iterations < max?
    ├─ YES: Loop back to [FlowAnalysisAgent] (Step 7)
    └─ NO: DONE
```

### Config Hierarchy

```
.context/
├── workspace-definition.d.yaml     ✏️ User-defined: repos, GitLab config
├── project-definition.d.yaml       ✏️ Auto-generated first pass, user refines
├── tech-aliases.yaml               ✏️ User maps internal terminology
├── scan-config.yaml                ✏️ What files to scan
├── output-config.yaml              ✏️ HTML/Markdown/Graph output settings
├── c4-config.yaml                  ✏️ C4 diagram rules (what to show)
├── maturity-config.yaml            ✏️ Scoring weights & target score
├── test-quality-config.yaml        ✏️ Test evaluation rules
└── [generated outputs]
```

---

## CLI Interface

### Commands

```bash
# Initialize .context in current directory
context-builder init

# Initialize multi-repo workspace
context-builder init-workspace

# Add a repository
context-builder add-repo <git-url-or-local-path>

# Run full analysis pipeline
context-builder build-context

# Run + iterate until maturity target
context-builder build-context --until-mature

# Run specific steps (for debugging)
context-builder scan
context-builder analyze
context-builder generate-diagrams
context-builder generate-html

# Ask questions about the project (LLM-powered)
context-builder ask "What are the main entry points?"

# Check status
context-builder status
```

### Console Output

```
Context Build Started

Step 1: Loading configuration ✓
Step 2: Detecting repositories ✓
Step 3: Generating project definition ✓
Step 4: Scanning source code ✓
Step 5: Building graph ✓
Step 6: Analyzing flows ✓
Step 7: Analyzing DB & middleware ✓
Step 8: Analyzing tests ✓
Step 9: Analyzing technical debt ✓
Step 10: Generating diagrams ✓
Step 11: Generating Markdown ✓
Step 12: Generating HTML portal ✓
Step 13: Building RAG chunks ✓
Step 14: Calculating maturity ✓

Context Build Completed ✓

Results:
  📊 Project Understanding: 72%
  🧪 Test Intelligence: 65%
  ⚡ Overall Status: NOT_READY

Next Actions:
  • Add DB schema paths to project-definition.yaml
  • Map 5 missing Pulsar topics
  • Add integration tests for payment flow
  • Run `context-builder build-context --until-mature` to iterate

Generated files:
  ✓ .context/generated/site-html/index.html (open in browser)
  ✓ .context/generated/book-md/ (Markdown book)
  ✓ .context/generated/graph/ (graph data)
  ✓ .context/agents/ (exportable agent definitions)
```

---

## Multi-Platform Export Strategy

### Generated Agent Definitions

The orchestrator generates **exportable agent definitions** in `.context/agents/`:

```
.context/agents/
├── 00-super-agent-orchestrator.md      ← Master coordinator
├── 01-project-definition-agent.md
├── 02-repo-scanner-agent.md
├── 03-code-graph-agent.md
├── 04-flow-analysis-agent.md
├── 05-c4-diagram-agent.md
├── 06-html-site-agent.md
├── 07-rag-agent.md
├── 08-test-intelligence-agent.md
├── 09-technical-debt-agent.md
└── 10-maturity-agent.md               ← 11 total
```

Each agent definition:
- Describes the agent's role and responsibilities
- References the Python implementation: `Call context_builder.agents.ProjectDefinitionAgent()`
- Can be exported to **8 platforms** via the existing exporter tool

### Export Workflow

```bash
# List all agents and skills
python tools/exporter.py --list

# Export context-builder to specific platforms
python tools/exporter.py \
  --target claude copilot cursor \
  --agents context_builder

# Generates:
# - instructions/claude/context-builder-agents.md
# - instructions/copilot/context-builder-agents.md
# - instructions/cursor/context-builder-agents.md
```

Each platform-specific file includes:
> "To use this agent system, install context_builder:
> ```bash
> pip install context-builder
> ```
> Then import and call agents:
> ```python
> from context_builder.agents import ProjectDefinitionAgent
> result = ProjectDefinitionAgent().execute(context)
> ```"

### Supported Export Targets

- Claude (claude.ai, Claude API)
- GitHub Copilot (VS Code, GitHub.com)
- Cursor (IDE)
- Windsurf
- VS Code
- Google Gemini
- Continue (JetBrains, VSCode)
- OpenAI (ChatGPT, API)

---

## Testing Strategy

### Test Structure

```
tests/
├── conftest.py                      # pytest fixtures
├── test_orchestrator.py
│   ├── test_full_pipeline_end_to_end()
│   ├── test_iteration_on_low_maturity()
│   ├── test_caching_skips_unchanged_repos()
│   └── test_config_initialization()
├── test_agents/
│   ├── test_project_definition_agent.py
│   ├── test_repo_scanner_agent.py
│   ├── test_code_graph_agent.py
│   ├── test_flow_analysis_agent.py
│   ├── test_c4_diagram_agent.py
│   ├── test_html_site_agent.py
│   ├── test_rag_agent.py
│   ├── test_test_intelligence_agent.py
│   ├── test_technical_debt_agent.py
│   └── test_maturity_agent.py
├── test_services/
│   ├── test_git_service.py
│   ├── test_scanner_service.py
│   ├── test_graph_service.py
│   ├── test_cache_service.py
│   ├── test_diagram_service.py
│   └── test_markdown_service.py
├── test_analyzers/
│   ├── test_java_analyzer.py
│   ├── test_python_analyzer.py
│   ├── test_typescript_analyzer.py
│   ├── test_config_analyzer.py
│   ├── test_db_analyzer.py
│   └── test_middleware_analyzer.py
├── test_output/
│   ├── test_markdown_writer.py
│   ├── test_html_writer.py
│   ├── test_graph_writer.py
│   └── test_json_writer.py
└── fixtures/
    ├── sample-java-project/         # Spring Boot test project
    ├── sample-python-project/       # FastAPI test project
    ├── sample-multi-repo/           # Multi-repo workspace
    └── sample-configs/              # Config YAML templates
```

### Coverage Targets

- Agents: 85%+
- Services: 90%+
- Analyzers: 85%+
- Overall: 80%+

### Test Types

- **Unit tests:** Individual agents, services, analyzers
- **Integration tests:** Agent interactions, end-to-end pipeline
- **Fixture tests:** Sample projects, configs, repos
- **Regression tests:** Known bug fixes
- **Performance tests:** Caching, incremental analysis

---

## Integration Points

### With Existing Tools

**token_optimizer:**
- Optional query optimization before LLM dispatch
- Use case: Optimize questions asked in `context-builder ask`

**parser:**
- Java/Maven field derivation analysis
- Use case: Enhance CodeGraphAgent for Java projects

**exporter:**
- Export generated agent definitions to 8 platforms
- Use case: `exporter.py --agents context_builder`

### Dependencies

**Required:**
- Python 3.9+
- GitPython (git operations)
- Typer (CLI framework)
- Pydantic (data models)
- PyYAML (config parsing)
- Jinja2 (HTML/Markdown templates)

**Optional:**
- tree-sitter (advanced code parsing)
- networkx (graph analysis)
- lxml (XML parsing)
- javalang (Java AST parsing)

---

## Implementation Dependencies

### Phase 1 (Full Implementation)

All 11 sub-agents must be implemented in Phase 1 to complete the system.

**Critical path:**
1. Core models & ExecutionContext
2. Config system
3. Services (git, scanner, graph, cache)
4. Analyzers (Java, Python, TypeScript, config, DB, middleware)
5. Agents (in dependency order)
6. Output writers (Markdown, HTML, Graph, JSON)
7. Orchestrator
8. CLI

---

## Success Criteria

- ✅ CLI works: `context-builder build-context` runs end-to-end
- ✅ `.context` folder is generated with all configs
- ✅ All 11 sub-agents execute and produce outputs
- ✅ Sample projects (Java, Python, multi-repo) work
- ✅ Graph (nodes.json, edges.json) is generated
- ✅ Mermaid diagrams are generated
- ✅ C4 diagrams are generated
- ✅ Markdown book is generated (15+ files)
- ✅ Single-page HTML portal is generated
- ✅ Test quality matrix is generated
- ✅ Maturity report is generated
- ✅ RAG chunks are generated
- ✅ Maturity iteration works (`--until-mature`)
- ✅ Agent definitions are exportable to 8 platforms
- ✅ 80%+ test coverage

---

## Not In Scope (Phase 1)

- Neo4j integration (generate data only)
- Live Q&A with RAG vector DB (generate chunks only)
- Real-time monitoring/CI integration
- GitHub/GitLab webhook integration

---

## Document Review Checklist

- ✅ All 11 sub-agents documented
- ✅ 14-step pipeline fully specified
- ✅ Package structure is clear
- ✅ CLI interface is complete
- ✅ Multi-platform export strategy defined
- ✅ Testing strategy documented
- ✅ Integration points clear
- ✅ No contradictions or ambiguities
- ✅ Scope is focused (full Phase 1 implementation)
