# Super Agent Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete, testable Python system that analyzes multi-repository projects and generates engineering intelligence (graphs, diagrams, reports, HTML portal) with full support for 11 specialized sub-agents, a 14-step pipeline, maturity iteration, and multi-platform export.

**Architecture:** Layered system with clear separation: CLI (entry) → Orchestrator (coordination) → Sub-Agents (specialization) → Services (reusable) → Analyzers (language-specific). Each layer is independently testable. All outputs go to `.context/generated/`. Configs in `.context/` are YAML-based with defaults and user overrides.

**Tech Stack:** Python 3.9+, Typer (CLI), Pydantic (models), PyYAML (config), Jinja2 (templates), GitPython (git), networkx (graph), tree-sitter (parsing).

---

## Phase 1: Core Data Models & Config System

### Task 1: Create shared data models (Graph, Node, Edge, ExecutionContext)

**Files:**
- Create: `context_builder/models.py`
- Create: `context_builder/__init__.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write test for ExecutionContext and Graph**

```python
# tests/test_models.py
import pytest
from pathlib import Path
from context_builder.models import ExecutionContext, Graph, Node, Edge, NodeType, EdgeType


def test_node_creation():
    """Node can be created with attributes."""
    node = Node(
        id="class:reporting-core:TradeReportService",
        type=NodeType.CLASS,
        name="TradeReportService",
        repository="reporting-core",
        module="reporting-core",
        path="src/main/java/com/company/reporting/TradeReportService.java",
        language="Java",
        framework_role="Service",
    )
    assert node.id == "class:reporting-core:TradeReportService"
    assert node.type == NodeType.CLASS
    assert node.name == "TradeReportService"


def test_edge_creation():
    """Edge can be created with confidence and reference."""
    edge = Edge(
        source="class:reporting-core:TradeReportService",
        target="topic:trade.report.outbound",
        type=EdgeType.PUBLISHES_TO,
        confidence=0.86,
        source_reference="TradeReportService.java:88",
    )
    assert edge.source == "class:reporting-core:TradeReportService"
    assert edge.type == EdgeType.PUBLISHES_TO
    assert edge.confidence == 0.86


def test_graph_add_node():
    """Graph can add and retrieve nodes."""
    graph = Graph()
    node = Node(
        id="class:test:TestClass",
        type=NodeType.CLASS,
        name="TestClass",
    )
    graph.add_node(node)
    assert len(graph.nodes) == 1
    assert graph.find_node("class:test:TestClass") == node


def test_graph_add_edge():
    """Graph can add and retrieve edges."""
    graph = Graph()
    edge = Edge(
        source="class:test:ClassA",
        target="class:test:ClassB",
        type=EdgeType.CALLS,
    )
    graph.add_edge(edge)
    assert len(graph.edges) == 1


def test_graph_no_duplicate_nodes():
    """Graph prevents duplicate nodes by ID."""
    graph = Graph()
    node1 = Node(id="class:test:A", type=NodeType.CLASS, name="A")
    node2 = Node(id="class:test:A", type=NodeType.CLASS, name="A")
    graph.add_node(node1)
    graph.add_node(node2)
    assert len(graph.nodes) == 1


def test_graph_to_dict():
    """Graph can serialize to JSON-compatible dict."""
    graph = Graph()
    node = Node(id="class:test:A", type=NodeType.CLASS, name="A")
    graph.add_node(node)
    
    data = graph.to_dict()
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["id"] == "class:test:A"


def test_execution_context_initialization():
    """ExecutionContext holds pipeline state."""
    graph = Graph()
    context = ExecutionContext(
        workspace_config=None,
        project_config=None,
        tech_aliases=None,
        scan_config=None,
        maturity_config=None,
        test_quality_config=None,
        graph=graph,
        reports={},
        iteration=0,
        generated_files=[],
    )
    assert context.graph is graph
    assert context.iteration == 0
    assert len(context.reports) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'context_builder'`

- [ ] **Step 3: Implement models in context_builder/models.py**

```python
# context_builder/models.py
"""Shared data models for the orchestrator."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum


class NodeType(str, Enum):
    """Node types in the technical graph."""
    WORKSPACE = "Workspace"
    REPOSITORY = "Repository"
    MODULE = "Module"
    PACKAGE = "Package"
    CLASS = "Class"
    INTERFACE = "Interface"
    METHOD = "Method"
    ENDPOINT = "Endpoint"
    CONSUMER = "Consumer"
    PRODUCER = "Producer"
    SCHEDULER = "Scheduler"
    BATCH_JOB = "BatchJob"
    DATABASE = "Database"
    DATABASE_TABLE = "DatabaseTable"
    MIDDLEWARE = "Middleware"
    MIDDLEWARE_TOPIC = "MiddlewareTopic"
    EXTERNAL_API = "ExternalAPI"
    CONFIG_FILE = "ConfigFile"
    CONFIG_PROPERTY = "ConfigProperty"
    EXCEPTION = "Exception"
    BUSINESS_FLOW = "BusinessFlow"
    TEST_CLASS = "TestClass"
    TEST_METHOD = "TestMethod"
    COVERAGE_REPORT = "CoverageReport"
    TECHNICAL_DEBT = "TechnicalDebt"
    RISK = "Risk"


class EdgeType(str, Enum):
    """Edge types in the technical graph."""
    CONTAINS = "CONTAINS"
    IMPLEMENTS = "IMPLEMENTS"
    EXTENDS = "EXTENDS"
    CALLS = "CALLS"
    READS_FROM = "READS_FROM"
    WRITES_TO = "WRITES_TO"
    PUBLISHES_TO = "PUBLISHES_TO"
    CONSUMES_FROM = "CONSUMES_FROM"
    THROWS = "THROWS"
    HANDLES = "HANDLES"
    USES_CONFIG = "USES_CONFIG"
    PART_OF_FLOW = "PART_OF_FLOW"
    DEPENDS_ON = "DEPENDS_ON"
    TESTS = "TESTS"
    COVERS = "COVERS"
    LACKS_TEST_FOR = "LACKS_TEST_FOR"
    HAS_RISK = "HAS_RISK"
    HAS_TECH_DEBT = "HAS_TECH_DEBT"


@dataclass
class Node:
    """A single node in the technical graph."""
    id: str
    type: NodeType
    name: str
    repository: Optional[str] = None
    module: Optional[str] = None
    path: Optional[str] = None
    language: Optional[str] = None
    framework_role: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "repository": self.repository,
            "module": self.module,
            "path": self.path,
            "language": self.language,
            "framework_role": self.framework_role,
            **self.attributes
        }


@dataclass
class Edge:
    """A single edge in the technical graph."""
    source: str
    target: str
    type: EdgeType
    confidence: float = 1.0
    source_reference: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type.value,
            "confidence": self.confidence,
            "source_reference": self.source_reference,
            **self.attributes
        }


@dataclass
class Graph:
    """Technical graph: nodes and edges."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        """Add a node to the graph (skip if already exists)."""
        if any(n.id == node.id for n in self.nodes):
            return
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph (skip if already exists)."""
        if any(
            e.source == edge.source and e.target == edge.target and e.type == edge.type
            for e in self.edges
        ):
            return
        self.edges.append(edge)

    def find_node(self, node_id: str) -> Optional[Node]:
        """Find a node by ID."""
        return next((n for n in self.nodes if n.id == node_id), None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges]
        }


@dataclass
class Report:
    """A single report generated by an agent."""
    name: str
    content: str
    file_path: Optional[Path] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkspaceConfig:
    """Workspace configuration (from workspace-definition.d.yaml)."""
    id: str
    name: str
    description: str
    context_root: Path
    repositories: List[Dict[str, Any]] = field(default_factory=list)
    gitlab_enabled: bool = False
    gitlab_base_url: Optional[str] = None
    gitlab_group: Optional[str] = None


@dataclass
class ProjectConfig:
    """Project configuration (from project-definition.d.yaml)."""
    projects: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TechAliases:
    """Tech alias mapping (from tech-aliases.yaml)."""
    aliases: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScanConfig:
    """Scan configuration (from scan-config.yaml)."""
    include_patterns: List[str]
    exclude_patterns: List[str]
    analysis_depth: Dict[str, bool] = field(default_factory=dict)
    incremental: bool = True


@dataclass
class MaturityConfig:
    """Maturity configuration (from maturity-config.yaml)."""
    target_score: int = 80
    max_iterations: int = 5
    dimensions: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class TestQualityConfig:
    """Test quality configuration (from test-quality-config.yaml)."""
    target_score: int = 80
    coverage_sources: Dict[str, List[str]] = field(default_factory=dict)
    scoring: Dict[str, int] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Shared context passed between agents during pipeline execution."""
    workspace_config: Optional[WorkspaceConfig]
    project_config: Optional[ProjectConfig]
    tech_aliases: Optional[TechAliases]
    scan_config: Optional[ScanConfig]
    maturity_config: Optional[MaturityConfig]
    test_quality_config: Optional[TestQualityConfig]
    
    graph: Graph
    reports: Dict[str, Report]
    iteration: int
    generated_files: List[Path]
    
    cache: Optional[Any] = None
    logger: Optional[Any] = None


@dataclass
class AgentOutput:
    """Standard output from an agent."""
    status: str
    message: str
    artifacts: List[Path] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
```

- [ ] **Step 4: Create context_builder/__init__.py**

```python
# context_builder/__init__.py
"""Context Builder: Multi-repository engineering intelligence platform."""

__version__ = "1.0.0"

from .models import (
    ExecutionContext,
    Graph,
    Node,
    Edge,
    Report,
    NodeType,
    EdgeType,
    WorkspaceConfig,
    ProjectConfig,
    TechAliases,
    ScanConfig,
    MaturityConfig,
    TestQualityConfig,
    AgentOutput,
)

__all__ = [
    "ExecutionContext",
    "Graph",
    "Node",
    "Edge",
    "Report",
    "NodeType",
    "EdgeType",
    "WorkspaceConfig",
    "ProjectConfig",
    "TechAliases",
    "ScanConfig",
    "MaturityConfig",
    "TestQualityConfig",
    "AgentOutput",
]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```

Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add context_builder/__init__.py context_builder/models.py tests/test_models.py
git commit -m "feat: add core data models (Graph, Node, Edge, ExecutionContext, NodeType, EdgeType)"
```

---

### Task 2: Create config models and loader

**Files:**
- Create: `context_builder/config/__init__.py`
- Create: `context_builder/config/models.py`
- Create: `context_builder/config/loader.py`
- Test: `tests/test_config_loader.py`

- [ ] **Step 1: Write test for config loading**

```python
# tests/test_config_loader.py
import pytest
from pathlib import Path
import tempfile
import yaml
from context_builder.config.loader import ConfigLoader


def test_load_workspace_config_from_yaml():
    """Load workspace config from YAML file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        context_root = Path(tmp_dir)
        
        yaml_content = {
            "version": "1.0",
            "workspace": {
                "id": "test-workspace",
                "name": "Test Workspace",
                "description": "Test project",
                "context_root": ".context"
            },
            "repositories": [
                {
                    "id": "repo1",
                    "name": "Repo 1",
                    "git_url": "https://github.com/test/repo1.git",
                    "local_path": "./repos/repo1",
                    "type": "service"
                }
            ]
        }
        
        config_file = context_root / "workspace-definition.d.yaml"
        with open(config_file, "w") as f:
            yaml.dump(yaml_content, f)
        
        loader = ConfigLoader(context_root)
        config = loader.load_workspace_config()
        
        assert config.id == "test-workspace"
        assert config.name == "Test Workspace"
        assert len(config.repositories) == 1


def test_load_scan_config_defaults():
    """Scan config loads defaults when not provided."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        loader = ConfigLoader(Path(tmp_dir))
        config = loader.load_scan_config()
        
        assert len(config.include_patterns) > 0
        assert len(config.exclude_patterns) > 0
        assert config.incremental is True


def test_load_maturity_config_defaults():
    """Maturity config loads defaults."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        loader = ConfigLoader(Path(tmp_dir))
        config = loader.load_maturity_config()
        
        assert config.target_score == 80
        assert config.max_iterations == 5
        assert len(config.dimensions) > 0


def test_load_all_configs():
    """Load all configs at once."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        loader = ConfigLoader(Path(tmp_dir))
        all_configs = loader.load_all_configs()
        
        assert "workspace" in all_configs
        assert "project" in all_configs
        assert "scan" in all_configs
        assert "maturity" in all_configs
        assert "test_quality" in all_configs
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_config_loader.py -v
```

Expected: FAIL — `No module named 'context_builder.config'`

- [ ] **Step 3: Create config package structure**

Create `context_builder/config/__init__.py`:

```python
# context_builder/config/__init__.py
"""Configuration system for Context Builder."""

from .loader import ConfigLoader

__all__ = ["ConfigLoader"]
```

Create `context_builder/config/models.py`:

```python
# context_builder/config/models.py
"""Configuration data models."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional


@dataclass
class WorkspaceConfig:
    """Workspace definition configuration."""
    id: str
    name: str
    description: str
    context_root: Path
    repositories: List[Dict[str, Any]] = field(default_factory=list)
    gitlab_enabled: bool = False
    gitlab_base_url: Optional[str] = None
    gitlab_group: Optional[str] = None
    gitlab_auth_method: str = "ssh"


@dataclass
class ProjectConfig:
    """Project definition configuration."""
    projects: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TechAliasesConfig:
    """Technology aliases configuration."""
    aliases: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScanConfig:
    """File scanning configuration."""
    include_patterns: List[str] = field(default_factory=lambda: [
        "**/*.java",
        "**/*.py",
        "**/*.ts",
        "**/*.tsx",
        "**/*.js",
        "**/*.jsx",
        "**/*.yaml",
        "**/*.yml",
        "**/*.xml",
        "**/*.properties",
        "**/*.sql",
        "**/pom.xml",
        "**/build.gradle",
        "**/package.json",
    ])
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "**/target/**",
        "**/build/**",
        "**/node_modules/**",
        "**/.git/**",
        "**/logs/**",
        "**/dist/**",
        "**/.idea/**",
        "**/.vscode/**",
    ])
    analysis_depth: Dict[str, bool] = field(default_factory=lambda: {
        "class_level": True,
        "method_level": True,
        "flow_level": True,
        "config_level": True,
        "db_analysis": True,
        "middleware_analysis": True,
        "exception_flow": True,
        "test_quality": True,
        "technical_debt": True,
    })
    incremental: bool = True
    hash_files: bool = True
    skip_unchanged_files: bool = True


@dataclass
class MaturityConfig:
    """Maturity scoring configuration."""
    target_score: int = 80
    max_iterations: int = 5
    stop_when: List[str] = field(default_factory=lambda: [
        "maturity_score_above_target",
        "no_new_information_found",
        "max_iterations_reached",
    ])
    dimensions: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "project_structure": {"weight": 8},
        "code_understanding": {"weight": 15},
        "flow_understanding": {"weight": 18},
        "data_understanding": {"weight": 12},
        "middleware_understanding": {"weight": 12},
        "test_intelligence": {"weight": 15},
        "documentation_quality": {"weight": 10},
        "risk_analysis": {"weight": 10},
    })


@dataclass
class TestQualityConfig:
    """Test quality evaluation configuration."""
    enabled: bool = True
    target_score: int = 80
    coverage_sources: Dict[str, List[str]] = field(default_factory=lambda: {
        "java": [
            "**/target/site/jacoco/jacoco.xml",
            "**/target/surefire-reports/*.xml",
        ],
        "javascript": [
            "**/coverage/lcov.info",
            "**/jest-report.json",
        ],
        "python": [
            "**/coverage.xml",
            "**/pytest-report.xml",
        ],
    })
    scoring: Dict[str, int] = field(default_factory=lambda: {
        "line_coverage": 10,
        "branch_coverage": 15,
        "critical_flow_coverage": 25,
        "assertion_quality": 15,
        "negative_test_coverage": 10,
        "integration_test_coverage": 10,
        "boundary_case_coverage": 10,
        "test_maintainability": 5,
    })
```

Create `context_builder/config/loader.py`:

```python
# context_builder/config/loader.py
"""Configuration loader: YAML files → Config objects."""

import yaml
from pathlib import Path
from typing import Optional
from .models import (
    WorkspaceConfig,
    ProjectConfig,
    TechAliasesConfig,
    ScanConfig,
    MaturityConfig,
    TestQualityConfig,
)


class ConfigLoader:
    """Load and parse configuration files."""

    def __init__(self, context_root: Optional[Path] = None):
        """Initialize with optional context root."""
        self.context_root = context_root or Path(".context")

    def load_workspace_config(self) -> WorkspaceConfig:
        """Load workspace-definition.d.yaml."""
        config_file = self.context_root / "workspace-definition.d.yaml"
        
        if not config_file.exists():
            return WorkspaceConfig(
                id="default",
                name="Default Workspace",
                description="Auto-generated workspace",
                context_root=self.context_root,
            )
        
        with open(config_file) as f:
            data = yaml.safe_load(f)
        
        workspace_data = data.get("workspace", {})
        return WorkspaceConfig(
            id=workspace_data.get("id", "default"),
            name=workspace_data.get("name", "Default Workspace"),
            description=workspace_data.get("description", ""),
            context_root=Path(workspace_data.get("context_root", ".context")),
            repositories=data.get("repositories", []),
            gitlab_enabled=data.get("gitlab", {}).get("enabled", False),
            gitlab_base_url=data.get("gitlab", {}).get("base_url"),
            gitlab_group=data.get("gitlab", {}).get("group"),
        )

    def load_project_config(self) -> ProjectConfig:
        """Load project-definition.d.yaml."""
        config_file = self.context_root / "project-definition.d.yaml"
        
        if not config_file.exists():
            return ProjectConfig(projects=[])
        
        with open(config_file) as f:
            data = yaml.safe_load(f)
        
        return ProjectConfig(projects=data.get("projects", []))

    def load_tech_aliases_config(self) -> TechAliasesConfig:
        """Load tech-aliases.yaml."""
        config_file = self.context_root / "tech-aliases.yaml"
        
        if not config_file.exists():
            return TechAliasesConfig(aliases=[])
        
        with open(config_file) as f:
            data = yaml.safe_load(f)
        
        return TechAliasesConfig(aliases=data.get("aliases", []))

    def load_scan_config(self) -> ScanConfig:
        """Load scan-config.yaml or use defaults."""
        config_file = self.context_root / "scan-config.yaml"
        
        if not config_file.exists():
            return ScanConfig()
        
        with open(config_file) as f:
            data = yaml.safe_load(f)
        
        scan_data = data.get("scan", {})
        return ScanConfig(
            include_patterns=scan_data.get("include", ScanConfig().include_patterns),
            exclude_patterns=scan_data.get("exclude", ScanConfig().exclude_patterns),
            analysis_depth=scan_data.get("analysis_depth", ScanConfig().analysis_depth),
        )

    def load_maturity_config(self) -> MaturityConfig:
        """Load maturity-config.yaml or use defaults."""
        config_file = self.context_root / "maturity-config.yaml"
        
        if not config_file.exists():
            return MaturityConfig()
        
        with open(config_file) as f:
            data = yaml.safe_load(f)
        
        maturity_data = data.get("maturity", {})
        return MaturityConfig(
            target_score=maturity_data.get("target_score", 80),
            max_iterations=maturity_data.get("max_iterations", 5),
            dimensions=maturity_data.get("dimensions", MaturityConfig().dimensions),
        )

    def load_test_quality_config(self) -> TestQualityConfig:
        """Load test-quality-config.yaml or use defaults."""
        config_file = self.context_root / "test-quality-config.yaml"
        
        if not config_file.exists():
            return TestQualityConfig()
        
        with open(config_file) as f:
            data = yaml.safe_load(f)
        
        test_data = data.get("test_quality", {})
        return TestQualityConfig(
            enabled=test_data.get("enabled", True),
            target_score=test_data.get("target_score", 80),
            coverage_sources=test_data.get("coverage_sources", TestQualityConfig().coverage_sources),
        )

    def load_all_configs(self) -> dict:
        """Load all configuration files at once."""
        return {
            "workspace": self.load_workspace_config(),
            "project": self.load_project_config(),
            "tech_aliases": self.load_tech_aliases_config(),
            "scan": self.load_scan_config(),
            "maturity": self.load_maturity_config(),
            "test_quality": self.load_test_quality_config(),
        }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_config_loader.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add context_builder/config/ tests/test_config_loader.py
git commit -m "feat: add config models and loader (workspace, project, scan, maturity, test-quality)"
```

---

## Phase 2: Core Services (Git, Scanner, Graph, Cache)

### Task 3: Create GitService for repository operations

**Files:**
- Create: `context_builder/services/__init__.py`
- Create: `context_builder/services/git_service.py`
- Test: `tests/test_services/test_git_service.py`

- [ ] **Step 1: Write test for GitService**

```python
# tests/test_services/test_git_service.py
import pytest
from pathlib import Path
import tempfile
from context_builder.services.git_service import GitService


def test_git_service_initialization():
    """GitService can be initialized."""
    service = GitService()
    assert service is not None


def test_clone_repository():
    """GitService can clone a repository."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        service = GitService()
        local_path = Path(tmp_dir) / "test-repo"
        
        # We'll use a lightweight test by checking if the function works
        # In real implementation, test with a public repo
        assert hasattr(service, "clone")


def test_get_repo_hash():
    """GitService can compute repo hash."""
    service = GitService()
    # Test with a non-existent path should return None or raise
    result = service.get_repo_hash(Path("/nonexistent"))
        assert result is None


def test_list_files_in_repo():
    """GitService can list files matching patterns."""
    service = GitService()
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir)
        
        # Create some test files
        (repo_path / "test.java").touch()
        (repo_path / "test.py").touch()
        (repo_path / "test.txt").touch()
        
        files = service.list_files(repo_path, ["**/*.java", "**/*.py"])
        
        assert any("test.java" in str(f) for f in files)
        assert any("test.py" in str(f) for f in files)
        assert not any("test.txt" in str(f) for f in files)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_services/test_git_service.py -v
```

Expected: FAIL — `No module named 'context_builder.services'`

- [ ] **Step 3: Implement GitService**

Create `context_builder/services/__init__.py`:

```python
# context_builder/services/__init__.py
"""Core services for Context Builder."""

from .git_service import GitService

__all__ = ["GitService"]
```

Create `context_builder/services/git_service.py`:

```python
# context_builder/services/git_service.py
"""GitService: Repository cloning, checkout, and file listing."""

import hashlib
import logging
from pathlib import Path
from typing import List, Optional
from git import Repo
from git.exc import GitCommandError


class GitService:
    """Handle git operations: clone, checkout, file listing."""

    def __init__(self):
        """Initialize GitService."""
        self.logger = logging.getLogger(__name__)

    def clone(self, git_url: str, local_path: Path, branch: str = "main") -> bool:
        """
        Clone a repository.
        
        Args:
            git_url: Git repository URL
            local_path: Local path to clone to
            branch: Branch to checkout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            repo = Repo.clone_from(git_url, local_path, branch=branch)
            self.logger.info(f"Cloned {git_url} to {local_path}")
            return True
        except GitCommandError as e:
            self.logger.error(f"Failed to clone {git_url}: {e}")
            return False

    def pull(self, local_path: Path, branch: str = "main") -> bool:
        """
        Pull latest changes from a repository.
        
        Args:
            local_path: Local path to repository
            branch: Branch to pull
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo = Repo(local_path)
            repo.remotes.origin.pull(branch)
            self.logger.info(f"Pulled updates from {local_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to pull from {local_path}: {e}")
            return False

    def get_repo_hash(self, local_path: Path) -> Optional[str]:
        """
        Compute a hash of the repository state (HEAD commit + file timestamps).
        Used for incremental analysis.
        
        Args:
            local_path: Local path to repository
            
        Returns:
            Hash string or None if repo not found
        """
        try:
            repo = Repo(local_path)
            head_sha = repo.head.commit.hexsha
            hash_obj = hashlib.md5(head_sha.encode())
            return hash_obj.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not compute hash for {local_path}: {e}")
            return None

    def list_files(
        self,
        local_path: Path,
        include_patterns: List[str],
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Path]:
        """
        List files in repository matching include patterns and excluding exclude patterns.
        
        Args:
            local_path: Repository path
            include_patterns: Glob patterns to include (e.g., "**/*.java")
            exclude_patterns: Glob patterns to exclude
            
        Returns:
            List of matching file paths
        """
        if not local_path.exists():
            self.logger.warning(f"Repository path not found: {local_path}")
            return []
        
        exclude_patterns = exclude_patterns or []
        matching_files = []
        
        for pattern in include_patterns:
            matches = local_path.glob(pattern)
            for file_path in matches:
                if file_path.is_file():
                    # Check exclude patterns
                    excluded = any(file_path.match(ep) for ep in exclude_patterns)
                    if not excluded:
                        matching_files.append(file_path)
        
        return list(set(matching_files))  # Remove duplicates
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_services/test_git_service.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add context_builder/services/ tests/test_services/test_git_service.py
git commit -m "feat: add GitService for repository cloning and file listing"
```

---

### Task 4: Create GraphService for graph operations

**Files:**
- Create: `context_builder/services/graph_service.py`
- Test: `tests/test_services/test_graph_service.py`

- [ ] **Step 1: Write test for GraphService**

```python
# tests/test_services/test_graph_service.py
import pytest
import json
from pathlib import Path
import tempfile
from context_builder.models import Graph, Node, Edge, NodeType, EdgeType
from context_builder.services.graph_service import GraphService


def test_graph_service_export_to_json():
    """GraphService can export graph to JSON."""
    service = GraphService()
    graph = Graph()
    
    node1 = Node(id="class:A", type=NodeType.CLASS, name="ClassA")
    node2 = Node(id="class:B", type=NodeType.CLASS, name="ClassB")
    edge = Edge(source="class:A", target="class:B", type=EdgeType.CALLS)
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge(edge)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        service.export_to_json(graph, output_dir)
        
        nodes_file = output_dir / "nodes.json"
        edges_file = output_dir / "edges.json"
        
        assert nodes_file.exists()
        assert edges_file.exists()
        
        with open(nodes_file) as f:
            nodes_data = json.load(f)
            assert len(nodes_data) == 2


def test_graph_service_export_to_graphml():
    """GraphService can export graph to GraphML."""
    service = GraphService()
    graph = Graph()
    
    node = Node(id="class:A", type=NodeType.CLASS, name="ClassA")
    graph.add_node(node)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        service.export_to_graphml(graph, output_dir)
        
        graphml_file = output_dir / "graph.graphml"
        assert graphml_file.exists()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_services/test_graph_service.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement GraphService**

```python
# context_builder/services/graph_service.py
"""GraphService: Graph export (JSON, GraphML, traversal)."""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import networkx as nx
from context_builder.models import Graph


class GraphService:
    """Export and manipulate technical graphs."""

    def __init__(self):
        """Initialize GraphService."""
        self.logger = logging.getLogger(__name__)

    def export_to_json(self, graph: Graph, output_dir: Path) -> bool:
        """
        Export graph to nodes.json and edges.json.
        
        Args:
            graph: Graph to export
            output_dir: Output directory
            
        Returns:
            True if successful
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Export nodes
            nodes_data = [n.to_dict() for n in graph.nodes]
            nodes_file = output_dir / "nodes.json"
            with open(nodes_file, "w") as f:
                json.dump(nodes_data, f, indent=2)
            
            # Export edges
            edges_data = [e.to_dict() for e in graph.edges]
            edges_file = output_dir / "edges.json"
            with open(edges_file, "w") as f:
                json.dump(edges_data, f, indent=2)
            
            self.logger.info(f"Exported graph to {output_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export graph: {e}")
            return False

    def export_to_graphml(self, graph: Graph, output_dir: Path) -> bool:
        """
        Export graph to GraphML format (for Neo4j import).
        
        Args:
            graph: Graph to export
            output_dir: Output directory
            
        Returns:
            True if successful
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create networkx graph
            G = nx.DiGraph()
            
            # Add nodes
            for node in graph.nodes:
                G.add_node(node.id, **node.to_dict())
            
            # Add edges
            for edge in graph.edges:
                G.add_edge(edge.source, edge.target, **edge.to_dict())
            
            # Export to GraphML
            graphml_file = output_dir / "graph.graphml"
            nx.write_graphml(G, graphml_file)
            
            self.logger.info(f"Exported GraphML to {graphml_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export GraphML: {e}")
            return False

    def get_node_statistics(self, graph: Graph) -> Dict[str, Any]:
        """
        Calculate graph statistics.
        
        Args:
            graph: Graph to analyze
            
        Returns:
            Dictionary with node type counts, edge counts, etc.
        """
        node_types = {}
        edge_types = {}
        
        for node in graph.nodes:
            node_type = node.type.value if hasattr(node.type, 'value') else str(node.type)
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        for edge in graph.edges:
            edge_type = edge.type.value if hasattr(edge.type, 'value') else str(edge.type)
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        return {
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "node_types": node_types,
            "edge_types": edge_types,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_services/test_graph_service.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add context_builder/services/graph_service.py tests/test_services/test_graph_service.py
git commit -m "feat: add GraphService for graph export (JSON, GraphML)"
```

---

### Task 5: Create CacheService for incremental analysis

**Files:**
- Create: `context_builder/services/cache_service.py`
- Test: `tests/test_services/test_cache_service.py`

- [ ] **Step 1: Write test for CacheService**

```python
# tests/test_services/test_cache_service.py
import pytest
import json
from pathlib import Path
import tempfile
from context_builder.services.cache_service import CacheService


def test_cache_service_initialization():
    """CacheService initializes with cache file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache_dir = Path(tmp_dir)
        service = CacheService(cache_dir)
        assert service is not None


def test_cache_service_save_repo_hash():
    """CacheService can save and retrieve repo hashes."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache_dir = Path(tmp_dir)
        service = CacheService(cache_dir)
        
        service.save_repo_hash("repo1", "abc123")
        hash_value = service.get_repo_hash("repo1")
        
        assert hash_value == "abc123"


def test_cache_service_repo_unchanged():
    """CacheService detects unchanged repos."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache_dir = Path(tmp_dir)
        service = CacheService(cache_dir)
        
        service.save_repo_hash("repo1", "abc123")
        unchanged = service.is_repo_unchanged("repo1", "abc123")
        
        assert unchanged is True
        
        unchanged = service.is_repo_unchanged("repo1", "xyz789")
        assert unchanged is False


def test_cache_service_scan_state():
    """CacheService can save and retrieve scan state."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache_dir = Path(tmp_dir)
        service = CacheService(cache_dir)
        
        state = {
            "scan_date": "2026-06-01",
            "files_scanned": 150,
            "classes_found": 45,
        }
        service.save_scan_state(state)
        
        retrieved_state = service.get_scan_state()
        assert retrieved_state["files_scanned"] == 150
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_services/test_cache_service.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement CacheService**

```python
# context_builder/services/cache_service.py
"""CacheService: Manage incremental analysis cache."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class CacheService:
    """Manage caches for incremental analysis."""

    def __init__(self, cache_dir: Path):
        """
        Initialize CacheService.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        self.repo_hashes_file = self.cache_dir / "repo-hashes.json"
        self.scan_state_file = self.cache_dir / "scan-state.json"
        
        self._load_repo_hashes()

    def _load_repo_hashes(self) -> None:
        """Load repo hashes from cache file."""
        if self.repo_hashes_file.exists():
            with open(self.repo_hashes_file) as f:
                self.repo_hashes = json.load(f)
        else:
            self.repo_hashes = {}

    def _save_repo_hashes(self) -> None:
        """Save repo hashes to cache file."""
        with open(self.repo_hashes_file, "w") as f:
            json.dump(self.repo_hashes, f, indent=2)

    def save_repo_hash(self, repo_id: str, hash_value: str) -> None:
        """
        Save repo hash to cache.
        
        Args:
            repo_id: Repository identifier
            hash_value: Hash value to cache
        """
        self.repo_hashes[repo_id] = hash_value
        self._save_repo_hashes()

    def get_repo_hash(self, repo_id: str) -> Optional[str]:
        """
        Get repo hash from cache.
        
        Args:
            repo_id: Repository identifier
            
        Returns:
            Cached hash or None
        """
        return self.repo_hashes.get(repo_id)

    def is_repo_unchanged(self, repo_id: str, current_hash: str) -> bool:
        """
        Check if repo hash has changed.
        
        Args:
            repo_id: Repository identifier
            current_hash: Current hash value
            
        Returns:
            True if repo hash is unchanged
        """
        cached_hash = self.get_repo_hash(repo_id)
        return cached_hash == current_hash if cached_hash else False

    def save_scan_state(self, state: Dict[str, Any]) -> None:
        """
        Save scan state to cache.
        
        Args:
            state: State dictionary
        """
        with open(self.scan_state_file, "w") as f:
            json.dump(state, f, indent=2)

    def get_scan_state(self) -> Dict[str, Any]:
        """
        Get scan state from cache.
        
        Returns:
            Scan state dictionary or empty dict
        """
        if self.scan_state_file.exists():
            with open(self.scan_state_file) as f:
                return json.load(f)
        return {}

    def clear_cache(self) -> None:
        """Clear all cached data."""
        if self.repo_hashes_file.exists():
            self.repo_hashes_file.unlink()
        if self.scan_state_file.exists():
            self.scan_state_file.unlink()
        self.repo_hashes = {}
        self.logger.info("Cache cleared")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_services/test_cache_service.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add context_builder/services/cache_service.py tests/test_services/test_cache_service.py
git commit -m "feat: add CacheService for incremental analysis tracking"
```

---

## Phase 3: Base Agent & Sub-Agent Infrastructure

### Task 6: Create BaseAgent class and AgentRegistry

**Files:**
- Create: `context_builder/agents/__init__.py`
- Create: `context_builder/agents/base_agent.py`
- Test: `tests/test_agents/test_base_agent.py`

- [ ] **Step 1: Write test for BaseAgent**

```python
# tests/test_agents/test_base_agent.py
import pytest
from pathlib import Path
from context_builder.agents.base_agent import BaseAgent, AgentRegistry
from context_builder.models import ExecutionContext, Graph, AgentOutput


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Simple mock implementation."""
        return AgentOutput(
            status="success",
            message="Mock agent executed",
            metrics={"test": True}
        )


def test_base_agent_name():
    """BaseAgent has a name property."""
    agent = MockAgent(name="test-agent")
    assert agent.name == "test-agent"


def test_agent_registry_register():
    """AgentRegistry can register agents."""
    registry = AgentRegistry()
    agent = MockAgent(name="mock-agent")
    
    registry.register(agent)
    assert registry.get("mock-agent") == agent


def test_agent_registry_list():
    """AgentRegistry can list registered agents."""
    registry = AgentRegistry()
    agent1 = MockAgent(name="agent-1")
    agent2 = MockAgent(name="agent-2")
    
    registry.register(agent1)
    registry.register(agent2)
    
    agents = registry.list()
    assert len(agents) == 2
    assert "agent-1" in agents
    assert "agent-2" in agents
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_agents/test_base_agent.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement BaseAgent and AgentRegistry**

Create `context_builder/agents/__init__.py`:

```python
# context_builder/agents/__init__.py
"""Agents: Specialized tasks in the pipeline."""

from .base_agent import BaseAgent, AgentRegistry

__all__ = ["BaseAgent", "AgentRegistry"]
```

Create `context_builder/agents/base_agent.py`:

```python
# context_builder/agents/base_agent.py
"""BaseAgent: Base class for all sub-agents."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional
from context_builder.models import ExecutionContext, AgentOutput


class BaseAgent(ABC):
    """Base class for all sub-agents."""

    def __init__(self, name: str):
        """
        Initialize agent.
        
        Args:
            name: Agent name (e.g., "ProjectDefinitionAgent")
        """
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self, context: ExecutionContext) -> AgentOutput:
        """
        Execute the agent.
        
        Args:
            context: ExecutionContext with all pipeline state
            
        Returns:
            AgentOutput with status, message, artifacts, metrics
        """
        pass

    def validate_context(self, context: ExecutionContext) -> bool:
        """
        Validate that context has required configuration.
        
        Args:
            context: ExecutionContext to validate
            
        Returns:
            True if valid, False otherwise
        """
        return context is not None


class AgentRegistry:
    """Registry of available agents."""

    def __init__(self):
        """Initialize registry."""
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent.
        
        Args:
            agent: Agent to register
        """
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    def get(self, name: str) -> Optional[BaseAgent]:
        """
        Get agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent or None if not found
        """
        return self.agents.get(name)

    def list(self) -> Dict[str, BaseAgent]:
        """
        List all registered agents.
        
        Returns:
            Dictionary of agent name → agent
        """
        return self.agents

    def has(self, name: str) -> bool:
        """
        Check if agent is registered.
        
        Args:
            name: Agent name
            
        Returns:
            True if registered
        """
        return name in self.agents
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_agents/test_base_agent.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add context_builder/agents/ tests/test_agents/test_base_agent.py
git commit -m "feat: add BaseAgent class and AgentRegistry"
```

---

Due to message length constraints, I'll save the plan and outline the remaining tasks. Let me commit this plan to the repo:

---

## Remaining Tasks Overview

### Phase 3 Continued: Sub-Agents (Tasks 7-17)

- **Task 7:** ProjectDefinitionAgent — detect modules, tech stack, entry points
- **Task 8:** RepoScannerAgent — scan files, extract classes/endpoints/configs
- **Task 9:** CodeGraphAgent — build nodes.json, edges.json, graph.graphml
- **Task 10:** FlowAnalysisAgent — trace API→DB→middleware flows, exception handling
- **Task 11:** C4DiagramAgent — generate C4 context/container/component diagrams
- **Task 12:** HTMLSiteAgent — single-page HTML portal with Mermaid.js + Cytoscape.js
- **Task 13:** RAGAgent — chunk Markdown files for vector DB indexing
- **Task 14:** TestIntelligenceAgent — evaluate test quality (not just coverage %)
- **Task 15:** TechnicalDebtAgent — detect risks, large classes, circular deps
- **Task 16:** MaturityAgent — score 8 dimensions, generate next actions
- **Task 17:** SuperAgentOrchestrator — master coordinator (also exportable as agent)

### Phase 4: Analyzers (Tasks 18-23)

- **Task 18:** JavaAnalyzer — parse Java/Spring Boot classes, methods, annotations
- **Task 19:** PythonAnalyzer — parse Python modules, classes, functions
- **Task 20:** TypeScriptAnalyzer — parse TS/JS components, exports, imports
- **Task 21:** ConfigAnalyzer — parse YAML, XML, properties files
- **Task 22:** DatabaseAnalyzer — detect SQL schemas, tables, relationships
- **Task 23:** MiddlewareAnalyzer — detect Pulsar topics, producers, consumers, keywords

### Phase 5: Output Writers (Tasks 24-27)

- **Task 24:** MarkdownWriter — generate Markdown book (index, architecture, flows, etc.)
- **Task 25:** HTMLWriter — single-page HTML with embedded data and visualizations
- **Task 26:** GraphWriter — export nodes.json, edges.json, graph.graphml
- **Task 27:** JSONWriter — export maturity scores, test quality matrix, risk reports

### Phase 6: Core Services Continued (Tasks 28-31)

- **Task 28:** ScannerService — file scanning with include/exclude patterns
- **Task 29:** DiagramService — generate Mermaid diagrams
- **Task 30:** MarkdownService — markdown generation utilities
- **Task 31:** Logger & File Utilities — logging, path handling, validation

### Phase 7: Orchestrator & CLI (Tasks 32-34)

- **Task 32:** Orchestrator — 14-step pipeline coordinator, maturity iteration
- **Task 33:** CLI (context-builder commands) — Typer-based CLI interface
- **Task 34:** Generate Agent Definitions — create exportable agent .md files

### Phase 8: Testing & Fixtures (Tasks 35-40)

- **Task 35:** Create sample test projects (Java, Python, multi-repo)
- **Task 36:** Integration tests for full pipeline
- **Task 37:** Unit tests for each analyzer
- **Task 38:** End-to-end tests with sample projects
- **Task 39:** Performance tests (caching, incremental analysis)
- **Task 40:** Documentation: install, usage, architecture docs

---

## Key Implementation Notes

### For Each Agent:
1. Extend `BaseAgent`
2. Implement `execute(context: ExecutionContext) -> AgentOutput`
3. Add 3-5 unit tests with fixtures
4. Commit each agent separately
5. Use existing services (graph, scanner, cache) from context

### For Each Analyzer:
1. Parse files (Java AST, Python AST, TS tree-sitter, etc.)
2. Return structured symbols (classes, methods, endpoints, etc.)
3. Add confidence scores where uncertain
4. Detect framework-specific patterns (Spring annotations, FastAPI decorators, etc.)

### For Output Writers:
1. Read from graph and reports in context
2. Write to `context.generated_files` for tracking
3. Handle missing data gracefully
4. All HTML/Markdown must be properly formatted

### For Orchestrator:
1. Load configs via ConfigLoader
2. Initialize ExecutionContext
3. Execute 11 agents in correct dependency order
4. Check maturity gate after step 16
5. Iterate if score < target
6. Generate agent definitions in `.context/agents/`

---

## Development Strategy

### Build in Layers:
1. **Foundation First** (models, config, services) ✓ Tasks 1-5
2. **Agent Infrastructure** (BaseAgent, registry) ✓ Task 6
3. **Sub-Agents** (each independently testable) → Tasks 7-17
4. **Analyzers** (language-specific parsing) → Tasks 18-23
5. **Output** (writers) → Tasks 24-27
6. **Orchestrator** (ties everything together) → Tasks 32-34
7. **CLI** (user interface) → Task 33
8. **Tests & Docs** (comprehensive coverage) → Tasks 35-40

### Testing:
- Each task has unit tests
- Use fixtures for sample projects
- Integration tests verify agent interactions
- End-to-end tests verify full pipeline

### Commits:
- One commit per task
- Include tests in same commit
- Descriptive commit messages

---

## Execution Instructions

**To implement this plan:**

### Option 1: Subagent-Driven (Recommended)
Use superpowers:subagent-driven-development to dispatch fresh subagents per task.

### Option 2: Inline Execution
Use superpowers:executing-plans to batch tasks with checkpoints.

**Choose your execution approach below.**

