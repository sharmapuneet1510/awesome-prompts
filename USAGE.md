# Usage Guide: Super Agent Orchestrator

## Overview

The Super Agent Orchestrator analyzes multi-repository projects to generate comprehensive engineering intelligence including architecture diagrams, code graphs, test coverage reports, and technical debt assessments.

---

## Quick Start

### 1. Basic Usage

```bash
# Navigate to your project
cd my-project

# Initialize orchestrator (creates .context directory)
python3 -m context_builder.cli init

# Run analysis
python3 -m context_builder.cli build-context

# View results in browser
open .context/generated/index.html
```

### 2. With Maturity Iteration

```bash
# Analyze until target maturity is reached
python3 -m context_builder.cli build-context --until-mature

# Limit iterations
python3 -m context_builder.cli build-context --until-mature --max-iterations 3
```

---

## Command-Line Interface

### Main Commands

#### `build-context`
Build complete project context with optional maturity iteration.

```bash
python3 -m context_builder.cli build-context [OPTIONS]

Options:
  --until-mature              Iterate until maturity target is reached
  --max-iterations INT        Maximum iterations (default: 5)
  --target-maturity INT       Target maturity score 0-100 (default: 80)
  --verbose                   Enable verbose output
  --debug                     Enable debug logging
  --output-dir PATH           Output directory (default: .context/generated)
```

**Examples:**
```bash
# Basic analysis
python3 -m context_builder.cli build-context

# Analyze until mature (max 3 iterations)
python3 -m context_builder.cli build-context --until-mature --max-iterations 3

# Set custom target
python3 -m context_builder.cli build-context --target-maturity 75 --until-mature

# Debug mode
python3 -m context_builder.cli build-context --debug
```

#### `check-config`
Validate configuration files.

```bash
python3 -m context_builder.cli check-config

# Output:
# ✓ Workspace config valid
# ✓ Scan config valid
# ✓ Maturity config valid
# ✓ All repositories found
# ✓ Include patterns: 5 patterns
# ✓ Exclude patterns: 8 patterns
```

#### `validate`
Validate generated outputs.

```bash
python3 -m context_builder.cli validate

# Output:
# ✓ graph.json is valid
# ✓ inventory.json is valid
# ✓ flows.json is valid
# ✓ technical-debt.json is valid
# ✓ maturity-report.json is valid
```

#### `export-agents`
Export agent definitions to platform-specific files.

```bash
python3 -m context_builder.cli export-agents [OPTIONS]

Options:
  --target PLATFORM           Target platform (claude, copilot, cursor, etc.)
  --format FORMAT            Output format (markdown, json, yaml)
  --output-dir PATH          Output directory
```

**Examples:**
```bash
# Export to Claude
python3 -m context_builder.cli export-agents --target claude

# Export to multiple platforms
python3 -m context_builder.cli export-agents --target claude copilot cursor

# Export with format
python3 -m context_builder.cli export-agents --target claude --format markdown
```

---

## Configuration

### Workspace Definition

**.context/workspace-definition.d.yaml**

Defines the workspace and repositories to analyze.

```yaml
version: "1.0"

workspace:
  id: my-workspace
  name: My Multi-Repo Project
  description: Analysis of our microservices architecture
  context_root: .context

repositories:
  - id: auth-service
    name: Authentication Service
    description: User authentication and JWT management
    local_path: ./services/auth
    git_url: https://github.com/myorg/auth-service.git
    type: service                    # service, api, web, library, tool
    language: java                   # java, python, typescript, go, etc.
    framework: spring-boot           # spring-boot, fastapi, express, etc.

  - id: user-service
    name: User Service
    description: User profile management
    local_path: ./services/user
    type: service
    language: python
    framework: fastapi

  - id: frontend
    name: Frontend Application
    description: React web application
    local_path: ./apps/frontend
    type: web
    language: typescript
    framework: react

  - id: shared-libs
    name: Shared Libraries
    description: Shared code and utilities
    local_path: ./shared
    type: library
```

### Scan Configuration

**.context/scan-config.yaml**

Controls what files to analyze and depth of analysis.

```yaml
# Include patterns (glob format)
include:
  - "**/*.java"              # Java files
  - "**/*.py"                # Python files
  - "**/*.ts"                # TypeScript files
  - "**/*.tsx"               # React files
  - "**/*.go"                # Go files
  - "**/*.xml"               # Spring XML config
  - "**/*.yaml"              # YAML config
  - "**/*.properties"        # Java properties
  - "**/*.json"              # JSON config

# Exclude patterns
exclude:
  - "**/node_modules/**"     # NPM packages
  - "**/dist/**"             # Build output
  - "**/build/**"            # Gradle output
  - "**/target/**"           # Maven output
  - "**/.git/**"             # Git files
  - "**/__pycache__/**"       # Python cache
  - "**/.pytest_cache/**"     # Pytest cache
  - "**/venv/**"             # Python venv
  - "**/.venv/**"            # Alt venv

# Analysis depth settings
analysis_depth:
  classes: true              # Parse class definitions
  methods: true              # Parse method/function definitions
  endpoints: true            # Parse HTTP endpoints
  consumers: true            # Parse message consumers
  producers: true            # Parse message producers
  tests: true                # Analyze test files

# Incremental analysis
incremental: true            # Skip unchanged repos on retry
```

### Maturity Configuration

**.context/maturity-config.yaml**

Controls maturity scoring and iteration.

```yaml
# Target maturity score (0-100)
target_score: 80

# Maximum iterations for maturity improvement
max_iterations: 5

# Dimension weights and targets
dimensions:
  architecture:              # Clear architecture, design
    weight: 0.20
    target: 80

  documentation:             # API docs, architecture docs
    weight: 0.20
    target: 85

  tests:                      # Test coverage and quality
    weight: 0.20
    target: 80

  code_quality:              # Complexity, duplication, naming
    weight: 0.15
    target: 75

  technical_debt:            # Security, performance, debt
    weight: 0.15
    target: 75

  framework:                 # Framework consistency, best practices
    weight: 0.10
    target: 85
```

### Test Quality Configuration

**.context/test-quality-config.yaml**

Defines test quality metrics and coverage targets.

```yaml
# Target test coverage percentage
target_score: 80

# Coverage source locations
coverage_sources:
  java:
    - "**/target/site/jacoco/index.html"
    - "**/build/reports/jacoco/test/html/index.html"
  python:
    - ".coverage"
    - "htmlcov/index.html"
  javascript:
    - "coverage/lcov-report/index.html"

# Scoring criteria
scoring:
  line_coverage_weight: 0.40
  branch_coverage_weight: 0.30
  test_count_weight: 0.20
  test_quality_weight: 0.10
```

---

## Programmatic Usage

### Basic Example

```python
from context_builder.orchestrator import Orchestrator
from pathlib import Path

# Initialize orchestrator
context_root = Path(".context")
orch = Orchestrator(context_root)

# Build context
success = orch.build_context(until_mature=False)

if success:
    # Get results
    context = orch.get_context()
    files = orch.get_generated_files()
    score = orch.get_maturity_score()

    print(f"Success: {success}")
    print(f"Maturity: {score}/100")
    print(f"Generated files: {len(files)}")
    for f in files:
        print(f"  - {f}")
```

### With Maturity Iteration

```python
from context_builder.orchestrator import Orchestrator
from pathlib import Path

orch = Orchestrator(Path(".context"))
success = orch.build_context(until_mature=True)

if success:
    score = orch.get_maturity_score()
    target = orch.target_maturity
    
    print(f"Final maturity: {score}/{target}")
    if score >= target:
        print("✓ Target maturity reached")
    else:
        print("✗ Could not reach target maturity in max iterations")
```

### Accessing Generated Data

```python
from context_builder.orchestrator import Orchestrator
import json

orch = Orchestrator(Path(".context"))
orch.build_context()
context = orch.get_context()

# Access graph
print(f"Nodes: {len(context.graph.nodes)}")
print(f"Edges: {len(context.graph.edges)}")

# Access reports
for report_name, report in context.reports.items():
    print(f"\n{report_name}:")
    print(f"  Metrics: {report.metrics}")
    print(f"  Content: {report.content[:200]}...")

# Read generated JSON files
import json
graph_data = json.loads(
    open(".context/generated/graph.json").read()
)
print(f"Graph nodes: {len(graph_data['nodes'])}")
print(f"Graph edges: {len(graph_data['edges'])}")
```

---

## Output Artifacts

All outputs are generated in `.context/generated/`:

### JSON Artifacts

- **project_definition.json**: Project metadata, tech stack
- **inventory.json**: Symbol catalog (classes, methods, endpoints)
- **dependencies.json**: Dependency graph
- **graph.json**: Complete technical graph (nodes + edges)
- **flows.json**: Business flows and entry points
- **test-report.json**: Test coverage and quality metrics
- **technical-debt.json**: Issues and debt assessment
- **maturity-report.json**: Maturity scores by dimension
- **rag-index.json**: Search index metadata

### Markdown Artifacts

- **architecture.md**: Architecture narrative with diagrams
- **tech-stack.md**: Technology reference table
- **test-gaps.md**: Test coverage gaps and recommendations
- **debt-remediation.md**: Technical debt remediation plan
- **maturity.md**: Executive maturity summary

### Diagrams

- **c4-context.md**: C4 architecture diagrams
- **c4-context.mmd**: Mermaid format
- **deployment-topology.mmd**: Deployment architecture

### HTML Portal

- **index.html**: Interactive documentation portal (4 tabs)
- **assets/**: CSS, JavaScript, images
- **data.json**: Embedded data for portal

### Other

- **final_report.md**: Executive summary
- **graph.graphml**: GraphML for Neo4j import
- **nodes.json**, **edges.json**: Separated graph data

---

## Interpreting Results

### Maturity Report

The maturity report provides scores across 6 dimensions:

```json
{
  "overall_score": 72,           # Weighted average 0-100
  "target_score": 80,
  "status": "needs_iteration",   # pass, fail, needs_iteration
  "dimensions": {
    "architecture": 85,          # Clear, well-documented
    "documentation": 70,         # Gaps in API docs
    "tests": 65,                 # Below target
    "code_quality": 75,
    "technical_debt": 68,
    "framework": 80
  },
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendations": ["..."]
}
```

### Technical Debt Report

Identifies issues by severity and category:

```json
{
  "id": "DEBT-001",
  "severity": "high",            # critical, high, medium, low
  "category": "complexity",      # complexity, duplication, security, etc.
  "location": "UserService.validatePassword()",
  "description": "Cyclomatic complexity of 15 (target: <10)",
  "remediation": "Extract conditional logic",
  "effort_points": 3,
  "priority": "high"
}
```

### Test Coverage Report

Shows coverage gaps and quality metrics:

```json
{
  "total_tests": 450,
  "average_coverage": 75.5,      # %
  "untested_classes": 12,
  "untested_methods": 45,
  "quality_score": 78,           # 0-100
  "recommendations": [
    "Add tests for UserService (coverage: 45%)",
    "Break up PaymentProcessor method (complexity: 18)"
  ]
}
```

---

## Troubleshooting

### No repositories found

```bash
# Check workspace config
python3 -m context_builder.cli check-config

# Verify repository paths exist
ls -la ./repos/
```

### Analysis stuck or slow

```bash
# Enable debug logging
export LOGLEVEL=DEBUG
python3 -m context_builder.cli build-context

# Check .context/logs/ for details
tail -f .context/logs/context-builder.log
```

### Maturity not reaching target

```bash
# Try with more iterations
python3 -m context_builder.cli build-context --until-mature --max-iterations 7

# Lower target
python3 -m context_builder.cli build-context --until-mature --target-maturity 70
```

### Invalid configuration

```bash
# Validate config
python3 -m context_builder.cli check-config

# Fix YAML syntax errors
cat .context/workspace-definition.d.yaml

# Check file permissions
ls -la .context/
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Architecture Analysis

on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run orchestrator
        run: python3 -m context_builder.cli build-context
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: architecture-analysis
          path: .context/generated/
```

### GitLab CI Example

```yaml
analyze-architecture:
  stage: analysis
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python3 -m context_builder.cli build-context --debug
  artifacts:
    paths:
      - .context/generated/
    expire_in: 30 days
```

---

## Performance Tips

1. **Use Incremental Analysis**: Set `incremental: true` in scan config
2. **Exclude Build Artifacts**: Add `/build/**`, `/dist/**` to exclude patterns
3. **Parallel Agents** (future): Some agents can run in parallel
4. **Cache Repositories**: GitService caches cloned repos

---

## Next Steps

1. **View Agent Definitions**: See [.context/agents/](../.context/agents/README.md)
2. **Understand Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. **See Examples**: Check [examples/](../examples/) directory
4. **Run Tests**: `pytest tests/ -v`
5. **Integrate with your CI/CD**: See CI/CD examples above

---

## Support & Feedback

- **Documentation**: See [docs/](../docs/) directory
- **Issues**: Check GitHub issues
- **Logs**: Check `.context/logs/` for debug info

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-01
