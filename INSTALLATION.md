# Installation Guide: Super Agent Orchestrator

## Prerequisites

- **Python 3.9+** (tested on 3.11)
- **pip** or **poetry** for package management
- **Git** for repository cloning
- **Virtual environment tool** (venv, conda, or similar)

---

## Quick Start

### 1. Clone and Set Up Environment

```bash
# Clone the repository
git clone https://github.com/yourdomain/awesome-prompts.git
cd awesome-prompts

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# For development (includes test dependencies)
pip install -r requirements-dev.txt
```

### 3. Verify Installation

```bash
# Check imports
python3 -c "from context_builder.orchestrator import Orchestrator; print('Installation OK')"

# Run tests
python3 -m pytest tests/ -v --tb=short
```

---

## Installation Options

### Option A: Standard Installation

```bash
pip install -r requirements.txt
```

**Installs:**
- FastAPI, Uvicorn (if using CLI)
- PyYAML (configuration)
- Pydantic (data models)
- NetworkX (graph algorithms)
- GitPython (repository operations)
- tree-sitter (language parsing)

### Option B: Development Installation

```bash
pip install -r requirements-dev.txt
```

**Adds:**
- pytest, pytest-cov (testing)
- black, flake8, mypy (code quality)
- sphinx (documentation generation)

### Option C: Minimal Installation (Core Only)

```bash
pip install pydantic pyyaml networkx gitpython
```

---

## Project Structure After Installation

```
awesome-prompts/
├── context_builder/              # Main package
│   ├── __init__.py
│   ├── models.py                 # Data models
│   ├── orchestrator.py           # Main orchestrator
│   ├── cli.py                    # CLI interface
│   ├── config/                   # Configuration system
│   │   ├── loader.py
│   │   └── models.py
│   ├── services/                 # Utility services
│   │   ├── cache_service.py
│   │   ├── git_service.py
│   │   ├── graph_service.py
│   │   ├── scanner_service.py
│   │   ├── diagram_service.py
│   │   ├── markdown_service.py
│   │   └── logger_service.py
│   ├── agents/                   # 11 sub-agents
│   │   ├── base_agent.py
│   │   ├── project_definition_agent.py
│   │   ├── repo_scanner_agent.py
│   │   └── ... (9 more agents)
│   └── analyzers/                # Language-specific analyzers
│       ├── java_analyzer.py
│       ├── python_analyzer.py
│       └── ... (more analyzers)
│
├── .context/                     # Configuration directory
│   ├── workspace-definition.d.yaml
│   ├── project-definition.d.yaml
│   ├── scan-config.yaml
│   ├── maturity-config.yaml
│   ├── test-quality-config.yaml
│   └── agents/                   # Agent definitions (generated)
│
├── tests/                        # Test suite
│   ├── test_models.py
│   ├── test_services/
│   ├── test_agents/
│   ├── test_integration/
│   └── fixtures/
│
├── docs/                         # Documentation
│   └── architecture.md
│
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── README.md
├── INSTALLATION.md               # This file
└── ARCHITECTURE.md
```

---

## Configuration

### Create .context Directory

```bash
# Create configuration directory
mkdir -p .context

# Copy default configurations
cp context_builder/config/defaults/*.yaml .context/
```

### Minimal Configuration Example

**.context/workspace-definition.d.yaml**
```yaml
version: "1.0"
workspace:
  id: my-workspace
  name: My Project
  description: Multi-repository analysis
context_root: .context
repositories:
  - id: backend
    name: Backend Service
    local_path: ./repos/backend
    type: service
  - id: frontend
    name: Frontend App
    local_path: ./repos/frontend
    type: web
```

**.context/scan-config.yaml**
```yaml
include:
  - "**/*.java"
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
exclude:
  - "**/node_modules/**"
  - "**/dist/**"
  - "**/.git/**"
analysis_depth:
  classes: true
  methods: true
  endpoints: true
incremental: true
```

**.context/maturity-config.yaml**
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

## Verify Configuration

```bash
# Check configuration validity
python3 -m context_builder.cli check-config

# Expected output:
# ✓ Workspace config valid
# ✓ Scan config valid
# ✓ Maturity config valid
# ✓ All repositories found
```

---

## Troubleshooting Installation

### Issue: ImportError: No module named 'context_builder'

**Solution:**
```bash
# Add current directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in development mode
pip install -e .
```

### Issue: ModuleNotFoundError: No module named 'yaml'

**Solution:**
```bash
pip install pyyaml
```

### Issue: ModuleNotFoundError: No module named 'networkx'

**Solution:**
```bash
pip install networkx
```

### Issue: Tree-sitter parser not found

**Solution:**
```bash
# Install tree-sitter and build parsers
pip install tree-sitter
python3 -m context_builder.setup_parsers  # Not yet implemented
```

### Issue: Git command not found

**Solution:**
```bash
# Install Git or GitPython
pip install gitpython
```

---

## Running Tests

### Run All Tests

```bash
# Basic test run
python3 -m pytest

# Verbose output
python3 -m pytest -v

# Show print statements
python3 -m pytest -v -s

# Stop on first failure
python3 -m pytest -x

# Run specific test file
python3 -m pytest tests/test_models.py -v

# Run specific test class
python3 -m pytest tests/test_models.py::TestNode -v

# Run specific test method
python3 -m pytest tests/test_models.py::TestNode::test_creation -v
```

### Test Coverage

```bash
# Generate coverage report
python3 -m pytest tests/ --cov=context_builder --cov-report=html

# View report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

### Test Fixtures

```bash
# Create Java Spring Boot sample project
python3 -c "from tests.fixtures.java_spring_boot_sample import JavaSpringBootSample; \
            p = JavaSpringBootSample.create_sample_project(); \
            print(f'Created at: {p}')"

# Create Python FastAPI sample project
python3 -c "from tests.fixtures.python_fastapi_sample import PythonFastAPISample; \
            p = PythonFastAPISample.create_sample_project(); \
            print(f'Created at: {p}')"
```

---

## First Run

### 1. Initialize Configuration

```bash
mkdir -p .context/generated
```

### 2. Create Workspace Definition

```bash
cat > .context/workspace-definition.d.yaml << 'EOF'
version: "1.0"
workspace:
  id: my-workspace
  name: My Project
context_root: .context
repositories:
  - id: repo1
    name: Repository 1
    local_path: ./sample-repos/repo1
    type: service
EOF
```

### 3. Run First Analysis

```bash
# Check configuration
python3 -m context_builder.cli check-config

# Run analysis
python3 -m context_builder.cli build-context

# Check results
ls -la .context/generated/
```

### 4. View Results

The generated artifacts will be in `.context/generated/`:
- `index.html`: Interactive portal
- `architecture.md`: Architecture documentation
- `project_definition.json`: Project metadata
- `graph.json`: Technical graph
- And many more...

Open `index.html` in a browser to see the interactive documentation portal.

---

## Environment Variables

```bash
# Set log level
export LOGLEVEL=DEBUG

# Set config directory
export CONTEXT_ROOT=.context

# Set output directory
export OUTPUT_DIR=.context/generated
```

---

## Next Steps

After installation:

1. **Read [USAGE.md](USAGE.md)** - Learn how to use the orchestrator
2. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** - Understand system design
3. **Check [.context/agents/](../.context/agents/README.md)** - Learn about agents
4. **Run sample analysis** - Try on a small project first
5. **Integrate with CI/CD** - Add to your build pipeline

---

## Support

- **Documentation**: See [docs/](../docs/) directory
- **Issues**: Check GitHub issues for known problems
- **Tests**: Run `pytest -v` to verify installation
- **Logs**: Check `.context/logs/` for debug information

---

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Remove package
pip uninstall context-builder
```

---

## Next: [USAGE.md](USAGE.md)

Ready to use? Head to the **[Usage Guide](USAGE.md)**.
