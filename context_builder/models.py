"""Core data models for context builder: Graph, Node, Edge, ExecutionContext."""

import logging
from dataclasses import dataclass, field
from enum import Enum
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
class ExecutionContext:
    """Holds all state during pipeline execution.

    Attributes:
        graph: The context graph being built
        configs: Configuration dictionary for the execution
        reports: Dictionary of reports generated during execution
        iteration: Current iteration number in multi-step processing
        generated_files: List of files generated during execution
        cache: Dictionary for caching intermediate results
        logger: Logger instance for execution logging
    """

    graph: Graph
    configs: Dict[str, Any] = field(default_factory=dict)
    reports: Dict[str, Any] = field(default_factory=dict)
    iteration: int = 0
    generated_files: List[str] = field(default_factory=list)
    cache: Dict[str, Any] = field(default_factory=dict)
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("context_builder"))

    def __post_init__(self):
        """Initialize logger if not already configured."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
