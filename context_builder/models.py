"""Core data models for context builder: Graph, Node, Edge, ExecutionContext."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class NodeType(str, Enum):
    """Enumeration of all node types in the context graph."""

    WORKSPACE = "WORKSPACE"
    REPOSITORY = "REPOSITORY"
    MODULE = "MODULE"
    PACKAGE = "PACKAGE"
    CLASS = "CLASS"
    INTERFACE = "INTERFACE"
    METHOD = "METHOD"
    ENDPOINT = "ENDPOINT"
    CONSUMER = "CONSUMER"
    PRODUCER = "PRODUCER"
    SCHEDULER = "SCHEDULER"
    BATCH_JOB = "BATCH_JOB"
    DATABASE = "DATABASE"
    DATABASE_TABLE = "DATABASE_TABLE"
    MIDDLEWARE = "MIDDLEWARE"
    MIDDLEWARE_TOPIC = "MIDDLEWARE_TOPIC"
    EXTERNAL_API = "EXTERNAL_API"
    CONFIG_FILE = "CONFIG_FILE"
    CONFIG_PROPERTY = "CONFIG_PROPERTY"
    EXCEPTION = "EXCEPTION"
    BUSINESS_FLOW = "BUSINESS_FLOW"
    TEST_CLASS = "TEST_CLASS"
    TEST_METHOD = "TEST_METHOD"
    COVERAGE_REPORT = "COVERAGE_REPORT"
    TECHNICAL_DEBT = "TECHNICAL_DEBT"
    RISK = "RISK"


class EdgeType(str, Enum):
    """Enumeration of all edge types in the context graph."""

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
    """Represents a node in the context graph.

    Attributes:
        id: Unique identifier for the node
        type: NodeType enum value indicating the node's role
        name: Human-readable name for the node
        repository: Optional repository name where node is defined
        module: Optional module/package where node is located
        path: Optional file path to the node definition
        language: Optional programming language (e.g., 'java', 'python')
        framework_role: Optional role within a framework (e.g., 'service', 'controller')
        attributes: Optional dictionary of custom attributes
    """

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
        """Serialize node to dictionary.

        Returns:
            Dictionary representation of the node with enum values as strings.
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "repository": self.repository,
            "module": self.module,
            "path": self.path,
            "language": self.language,
            "framework_role": self.framework_role,
            "attributes": self.attributes,
        }


@dataclass
class Edge:
    """Represents an edge (relationship) between two nodes.

    Attributes:
        source: ID of the source node
        target: ID of the target node
        type: EdgeType enum value indicating the relationship type
        confidence: Optional confidence score (0.0-1.0) for the edge
        source_reference: Optional reference to where the edge was discovered
        attributes: Optional dictionary of custom attributes
    """

    source: str
    target: str
    type: EdgeType
    confidence: Optional[float] = None
    source_reference: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize edge to dictionary.

        Returns:
            Dictionary representation of the edge with enum values as strings.
        """
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type.value,
            "confidence": self.confidence,
            "source_reference": self.source_reference,
            "attributes": self.attributes,
        }


@dataclass
class Graph:
    """Represents a directed graph of nodes and edges.

    Attributes:
        nodes: List of Node objects in the graph
        edges: List of Edge objects in the graph
    """

    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        """Add a node to the graph, skipping duplicates.

        Args:
            node: Node to add to the graph
        """
        # Skip if node with same ID already exists
        if any(existing.id == node.id for existing in self.nodes):
            return
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph, skipping duplicates.

        Args:
            edge: Edge to add to the graph
        """
        # Skip if edge with same source, target, and type already exists
        if any(
            existing.source == edge.source
            and existing.target == edge.target
            and existing.type == edge.type
            for existing in self.edges
        ):
            return
        self.edges.append(edge)

    def find_node(self, node_id: str) -> Optional[Node]:
        """Find a node by its ID.

        Args:
            node_id: ID of the node to find

        Returns:
            Node if found, None otherwise
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary.

        Returns:
            Dictionary representation of the graph with all nodes and edges.
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


@dataclass
class Report:
    """A single report generated by an agent.

    Attributes:
        name: Name of the report
        content: Report content/body
        file_path: Optional path where report is saved
        metrics: Optional metrics dictionary for report metadata
    """

    name: str
    content: str
    file_path: Optional[Path] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkspaceConfig:
    """Workspace configuration (from workspace-definition.d.yaml).

    Attributes:
        id: Unique workspace identifier
        name: Workspace name
        description: Workspace description
        context_root: Root path for workspace context
        repositories: List of repository configurations
        gitlab_enabled: Whether GitLab is enabled
        gitlab_base_url: GitLab base URL if enabled
        gitlab_group: GitLab group name if enabled
    """

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
    """Project configuration (from project-definition.d.yaml).

    Attributes:
        projects: List of project configurations
    """

    projects: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TechAliases:
    """Tech alias mapping (from tech-aliases.yaml).

    Attributes:
        aliases: List of technology alias mappings
    """

    aliases: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScanConfig:
    """Scan configuration (from scan-config.yaml).

    Attributes:
        include_patterns: File patterns to include in scan
        exclude_patterns: File patterns to exclude from scan
        analysis_depth: Flags for different analysis levels
        incremental: Whether to use incremental scanning
    """

    include_patterns: List[str] = field(
        default_factory=lambda: [
            "**/*.java", "**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx",
            "**/*.yaml", "**/*.yml", "**/*.xml", "**/*.properties", "**/*.sql",
            "**/pom.xml", "**/build.gradle", "**/package.json",
        ]
    )
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "**/target/**", "**/build/**", "**/node_modules/**", "**/.git/**",
            "**/logs/**", "**/dist/**", "**/.idea/**", "**/.vscode/**",
        ]
    )
    analysis_depth: Dict[str, bool] = field(
        default_factory=lambda: {
            "class_level": True,
            "method_level": True,
            "flow_level": True,
            "config_level": True,
            "db_analysis": True,
            "middleware_analysis": True,
            "exception_flow": True,
            "test_quality": True,
            "technical_debt": True,
        }
    )
    incremental: bool = True


@dataclass
class MaturityConfig:
    """Maturity configuration (from maturity-config.yaml).

    Attributes:
        target_score: Target maturity score (0-100)
        max_iterations: Maximum iterations for maturity analysis
        dimensions: Maturity dimensions with weights
    """

    target_score: int = 80
    max_iterations: int = 5
    dimensions: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "project_structure": {"weight": 8},
            "code_understanding": {"weight": 15},
            "flow_understanding": {"weight": 18},
            "data_understanding": {"weight": 12},
            "middleware_understanding": {"weight": 12},
            "test_intelligence": {"weight": 15},
            "documentation_quality": {"weight": 10},
            "risk_analysis": {"weight": 10},
        }
    )


@dataclass
class TestQualityConfig:
    """Test quality configuration (from test-quality-config.yaml).

    Attributes:
        target_score: Target test quality score (0-100)
        coverage_sources: Coverage report locations per language
        scoring: Scoring weights for different test quality dimensions
    """

    target_score: int = 80
    coverage_sources: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "java": ["**/target/site/jacoco/jacoco.xml", "**/target/surefire-reports/*.xml"],
            "javascript": ["**/coverage/lcov.info", "**/jest-report.json"],
            "python": ["**/coverage.xml", "**/pytest-report.xml"],
        }
    )
    scoring: Dict[str, int] = field(
        default_factory=lambda: {
            "line_coverage": 10,
            "branch_coverage": 15,
            "critical_flow_coverage": 25,
            "assertion_quality": 15,
            "negative_test_coverage": 10,
            "integration_test_coverage": 10,
            "boundary_case_coverage": 10,
            "test_maintainability": 5,
        }
    )


@dataclass
class AgentOutput:
    """Standard output from an agent.

    Attributes:
        status: Status of agent execution (e.g., 'success', 'failed')
        message: Status message or description
        artifacts: Generated artifacts (file paths)
        metrics: Execution metrics
        errors: List of error messages if any
    """

    status: str
    message: str
    artifacts: List[Path] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ExecutionContext:
    """Holds all state during pipeline execution.

    Attributes:
        workspace_config: Workspace configuration
        project_config: Project configuration
        tech_aliases: Technology aliases mapping
        scan_config: Scan configuration
        maturity_config: Maturity analysis configuration
        test_quality_config: Test quality configuration
        graph: The context graph being built
        reports: Dictionary of reports generated during execution
        iteration: Current iteration number in multi-step processing
        generated_files: List of files generated during execution
        cache: Dictionary for caching intermediate results
        logger: Logger instance for execution logging
    """

    workspace_config: Optional[WorkspaceConfig]
    project_config: Optional[ProjectConfig]
    tech_aliases: Optional[TechAliases]
    scan_config: Optional[ScanConfig]
    maturity_config: Optional[MaturityConfig]
    test_quality_config: Optional[TestQualityConfig]
    graph: Graph
    reports: Dict[str, Report] = field(default_factory=dict)
    iteration: int = 0
    generated_files: List[Path] = field(default_factory=list)
    cache: Optional[Any] = None
    logger: Optional[Any] = None

    def __post_init__(self):
        """Initialize logger if not already configured."""
        if self.logger is None:
            self.logger = logging.getLogger("context_builder")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
