"""Tests for core data models: Node, Edge, Graph, ExecutionContext."""

import pytest
from typing import Dict, List
from datetime import datetime

from context_builder.models import (
    Node,
    Edge,
    Graph,
    ExecutionContext,
    NodeType,
    EdgeType,
)


class TestNodeType:
    """Tests for NodeType enum."""

    def test_all_node_types_exist(self):
        """Test that all required node types are defined."""
        required_types = [
            "WORKSPACE", "REPOSITORY", "MODULE", "PACKAGE", "CLASS", "INTERFACE",
            "METHOD", "ENDPOINT", "CONSUMER", "PRODUCER", "SCHEDULER", "BATCH_JOB",
            "DATABASE", "DATABASE_TABLE", "MIDDLEWARE", "MIDDLEWARE_TOPIC",
            "EXTERNAL_API", "CONFIG_FILE", "CONFIG_PROPERTY", "EXCEPTION",
            "BUSINESS_FLOW", "TEST_CLASS", "TEST_METHOD", "COVERAGE_REPORT",
            "TECHNICAL_DEBT", "RISK",
        ]
        for node_type in required_types:
            assert hasattr(NodeType, node_type), f"NodeType.{node_type} not found"

    def test_node_type_string_serialization(self):
        """Test that NodeType enums serialize to strings."""
        assert isinstance(NodeType.WORKSPACE.value, str)
        assert NodeType.CLASS.value == "CLASS"


class TestEdgeType:
    """Tests for EdgeType enum."""

    def test_all_edge_types_exist(self):
        """Test that all required edge types are defined."""
        required_types = [
            "CONTAINS", "IMPLEMENTS", "EXTENDS", "CALLS", "READS_FROM", "WRITES_TO",
            "PUBLISHES_TO", "CONSUMES_FROM", "THROWS", "HANDLES", "USES_CONFIG",
            "PART_OF_FLOW", "DEPENDS_ON", "TESTS", "COVERS", "LACKS_TEST_FOR",
            "HAS_RISK", "HAS_TECH_DEBT",
        ]
        for edge_type in required_types:
            assert hasattr(EdgeType, edge_type), f"EdgeType.{edge_type} not found"

    def test_edge_type_string_serialization(self):
        """Test that EdgeType enums serialize to strings."""
        assert isinstance(EdgeType.CONTAINS.value, str)
        assert EdgeType.CALLS.value == "CALLS"


class TestNode:
    """Tests for Node class."""

    def test_node_creation_minimal(self):
        """Test creating a node with minimal attributes."""
        node = Node(
            id="node1",
            type=NodeType.CLASS,
            name="UserService",
        )
        assert node.id == "node1"
        assert node.type == NodeType.CLASS
        assert node.name == "UserService"

    def test_node_creation_full(self):
        """Test creating a node with all attributes."""
        attributes = {"language": "java", "visibility": "public"}
        node = Node(
            id="node1",
            type=NodeType.CLASS,
            name="UserService",
            repository="awesome-prompts",
            module="services",
            path="src/main/java/com/example/UserService.java",
            language="java",
            framework_role="service",
            attributes=attributes,
        )
        assert node.id == "node1"
        assert node.type == NodeType.CLASS
        assert node.name == "UserService"
        assert node.repository == "awesome-prompts"
        assert node.module == "services"
        assert node.path == "src/main/java/com/example/UserService.java"
        assert node.language == "java"
        assert node.framework_role == "service"
        assert node.attributes == attributes

    def test_node_to_dict_minimal(self):
        """Test Node serialization to dict with minimal data."""
        node = Node(
            id="node1",
            type=NodeType.CLASS,
            name="UserService",
        )
        node_dict = node.to_dict()
        assert node_dict["id"] == "node1"
        assert node_dict["type"] == "CLASS"
        assert node_dict["name"] == "UserService"

    def test_node_to_dict_full(self):
        """Test Node serialization to dict with all attributes."""
        attributes = {"language": "java", "visibility": "public"}
        node = Node(
            id="node1",
            type=NodeType.CLASS,
            name="UserService",
            repository="awesome-prompts",
            module="services",
            path="src/main/java/com/example/UserService.java",
            language="java",
            framework_role="service",
            attributes=attributes,
        )
        node_dict = node.to_dict()
        assert node_dict["id"] == "node1"
        assert node_dict["type"] == "CLASS"
        assert node_dict["name"] == "UserService"
        assert node_dict["repository"] == "awesome-prompts"
        assert node_dict["module"] == "services"
        assert node_dict["path"] == "src/main/java/com/example/UserService.java"
        assert node_dict["language"] == "java"
        assert node_dict["framework_role"] == "service"
        assert node_dict["attributes"] == attributes


class TestEdge:
    """Tests for Edge class."""

    def test_edge_creation_minimal(self):
        """Test creating an edge with minimal attributes."""
        edge = Edge(
            source="node1",
            target="node2",
            type=EdgeType.CALLS,
        )
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.type == EdgeType.CALLS

    def test_edge_creation_full(self):
        """Test creating an edge with all attributes."""
        attributes = {"method": "getUserById", "line": 42}
        edge = Edge(
            source="node1",
            target="node2",
            type=EdgeType.CALLS,
            confidence=0.95,
            source_reference="UserService.java:42",
            attributes=attributes,
        )
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.type == EdgeType.CALLS
        assert edge.confidence == 0.95
        assert edge.source_reference == "UserService.java:42"
        assert edge.attributes == attributes

    def test_edge_to_dict_minimal(self):
        """Test Edge serialization to dict with minimal data."""
        edge = Edge(
            source="node1",
            target="node2",
            type=EdgeType.CALLS,
        )
        edge_dict = edge.to_dict()
        assert edge_dict["source"] == "node1"
        assert edge_dict["target"] == "node2"
        assert edge_dict["type"] == "CALLS"

    def test_edge_to_dict_full(self):
        """Test Edge serialization to dict with all attributes."""
        attributes = {"method": "getUserById", "line": 42}
        edge = Edge(
            source="node1",
            target="node2",
            type=EdgeType.CALLS,
            confidence=0.95,
            source_reference="UserService.java:42",
            attributes=attributes,
        )
        edge_dict = edge.to_dict()
        assert edge_dict["source"] == "node1"
        assert edge_dict["target"] == "node2"
        assert edge_dict["type"] == "CALLS"
        assert edge_dict["confidence"] == 0.95
        assert edge_dict["source_reference"] == "UserService.java:42"
        assert edge_dict["attributes"] == attributes


class TestGraph:
    """Tests for Graph class."""

    def test_graph_creation(self):
        """Test creating an empty graph."""
        graph = Graph()
        assert graph.nodes == []
        assert graph.edges == []

    def test_graph_add_node(self):
        """Test adding a node to the graph."""
        graph = Graph()
        node = Node(id="node1", type=NodeType.CLASS, name="UserService")
        graph.add_node(node)
        assert len(graph.nodes) == 1
        assert graph.nodes[0].id == "node1"

    def test_graph_add_multiple_nodes(self):
        """Test adding multiple nodes to the graph."""
        graph = Graph()
        node1 = Node(id="node1", type=NodeType.CLASS, name="UserService")
        node2 = Node(id="node2", type=NodeType.CLASS, name="OrderService")
        graph.add_node(node1)
        graph.add_node(node2)
        assert len(graph.nodes) == 2

    def test_graph_no_duplicate_nodes(self):
        """Test that duplicate nodes are skipped."""
        graph = Graph()
        node = Node(id="node1", type=NodeType.CLASS, name="UserService")
        graph.add_node(node)
        graph.add_node(node)
        assert len(graph.nodes) == 1

    def test_graph_find_node(self):
        """Test finding a node by id."""
        graph = Graph()
        node = Node(id="node1", type=NodeType.CLASS, name="UserService")
        graph.add_node(node)
        found = graph.find_node("node1")
        assert found is not None
        assert found.id == "node1"

    def test_graph_find_node_not_found(self):
        """Test finding a non-existent node returns None."""
        graph = Graph()
        found = graph.find_node("nonexistent")
        assert found is None

    def test_graph_add_edge(self):
        """Test adding an edge to the graph."""
        graph = Graph()
        node1 = Node(id="node1", type=NodeType.CLASS, name="UserService")
        node2 = Node(id="node2", type=NodeType.CLASS, name="OrderService")
        graph.add_node(node1)
        graph.add_node(node2)
        edge = Edge(source="node1", target="node2", type=EdgeType.CALLS)
        graph.add_edge(edge)
        assert len(graph.edges) == 1
        assert graph.edges[0].source == "node1"

    def test_graph_add_multiple_edges(self):
        """Test adding multiple edges to the graph."""
        graph = Graph()
        node1 = Node(id="node1", type=NodeType.CLASS, name="UserService")
        node2 = Node(id="node2", type=NodeType.CLASS, name="OrderService")
        node3 = Node(id="node3", type=NodeType.CLASS, name="PaymentService")
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        edge1 = Edge(source="node1", target="node2", type=EdgeType.CALLS)
        edge2 = Edge(source="node2", target="node3", type=EdgeType.CALLS)
        graph.add_edge(edge1)
        graph.add_edge(edge2)
        assert len(graph.edges) == 2

    def test_graph_no_duplicate_edges(self):
        """Test that duplicate edges are skipped."""
        graph = Graph()
        node1 = Node(id="node1", type=NodeType.CLASS, name="UserService")
        node2 = Node(id="node2", type=NodeType.CLASS, name="OrderService")
        graph.add_node(node1)
        graph.add_node(node2)
        edge = Edge(source="node1", target="node2", type=EdgeType.CALLS)
        graph.add_edge(edge)
        graph.add_edge(edge)
        assert len(graph.edges) == 1

    def test_graph_to_dict(self):
        """Test Graph serialization to dict."""
        graph = Graph()
        node1 = Node(id="node1", type=NodeType.CLASS, name="UserService")
        node2 = Node(id="node2", type=NodeType.CLASS, name="OrderService")
        edge = Edge(source="node1", target="node2", type=EdgeType.CALLS)
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(edge)

        graph_dict = graph.to_dict()
        assert "nodes" in graph_dict
        assert "edges" in graph_dict
        assert len(graph_dict["nodes"]) == 2
        assert len(graph_dict["edges"]) == 1
        assert graph_dict["nodes"][0]["id"] == "node1"
        assert graph_dict["edges"][0]["source"] == "node1"


class TestExecutionContext:
    """Tests for ExecutionContext class."""

    def test_execution_context_creation(self):
        """Test creating an ExecutionContext."""
        graph = Graph()
        context = ExecutionContext(graph=graph)
        assert context.graph is graph
        assert context.configs == {}
        assert context.reports == {}
        assert context.iteration == 0
        assert context.generated_files == []
        assert context.cache == {}
        assert context.logger is not None

    def test_execution_context_with_configs(self):
        """Test ExecutionContext with configurations."""
        graph = Graph()
        configs = {"timeout": 30, "debug": True}
        context = ExecutionContext(graph=graph, configs=configs)
        assert context.configs == configs

    def test_execution_context_with_reports(self):
        """Test ExecutionContext with reports."""
        graph = Graph()
        reports = {"analysis": "summary", "metrics": "data"}
        context = ExecutionContext(graph=graph, reports=reports)
        assert context.reports == reports

    def test_execution_context_iteration_tracking(self):
        """Test ExecutionContext iteration tracking."""
        graph = Graph()
        context = ExecutionContext(graph=graph)
        assert context.iteration == 0
        context.iteration += 1
        assert context.iteration == 1

    def test_execution_context_generated_files_tracking(self):
        """Test ExecutionContext generated files tracking."""
        graph = Graph()
        context = ExecutionContext(graph=graph)
        assert context.generated_files == []
        context.generated_files.append("models.py")
        context.generated_files.append("__init__.py")
        assert len(context.generated_files) == 2
        assert "models.py" in context.generated_files

    def test_execution_context_cache(self):
        """Test ExecutionContext cache functionality."""
        graph = Graph()
        context = ExecutionContext(graph=graph)
        assert context.cache == {}
        context.cache["key1"] = "value1"
        assert context.cache["key1"] == "value1"

    def test_execution_context_holds_pipeline_state(self):
        """Test ExecutionContext holds all pipeline state."""
        graph = Graph()
        node = Node(id="node1", type=NodeType.CLASS, name="UserService")
        graph.add_node(node)

        configs = {"timeout": 30}
        reports = {"status": "running"}
        generated_files = ["file1.py"]

        context = ExecutionContext(
            graph=graph,
            configs=configs,
            reports=reports,
            iteration=1,
            generated_files=generated_files,
        )

        assert len(context.graph.nodes) == 1
        assert context.configs["timeout"] == 30
        assert context.reports["status"] == "running"
        assert context.iteration == 1
        assert len(context.generated_files) == 1
        assert context.logger is not None

    def test_execution_context_logger_exists(self):
        """Test ExecutionContext has a logger."""
        graph = Graph()
        context = ExecutionContext(graph=graph)
        assert context.logger is not None
        assert hasattr(context.logger, "info") or hasattr(context.logger, "debug")
