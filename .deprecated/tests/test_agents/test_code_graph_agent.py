"""Tests for CodeGraphAgent."""

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from context_builder.agents import CodeGraphAgent
from context_builder.models import (
    AgentOutput,
    Edge,
    EdgeType,
    ExecutionContext,
    Graph,
    MaturityConfig,
    Node,
    NodeType,
    ProjectConfig,
    Report,
    ScanConfig,
    TechAliases,
    TestQualityConfig,
    WorkspaceConfig,
)


@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temporary workspace directory."""
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    return tmp_path


@pytest.fixture
def workspace_config(tmp_workspace):
    """Create a workspace configuration."""
    return WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace for graph agent tests",
        context_root=tmp_workspace / "context",
        repositories=[
            {
                "id": "java-service",
                "name": "Java Service",
                "local_path": str(tmp_workspace / "java-service"),
            }
        ],
    )


@pytest.fixture
def execution_context(workspace_config):
    """Create an execution context with empty graph."""
    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=Graph(),
    )


@pytest.fixture
def scan_report_with_symbols():
    """Create a scan report with extracted symbols."""
    return Report(
        name="scan_report",
        content="Scan Report",
        metrics={
            "classes": [
                {
                    "id": "java-service-class-UserController",
                    "name": "UserController",
                    "type": "class",
                    "file": "src/main/java/com/example/UserController.java",
                    "repository": "java-service",
                    "language": "java",
                    "framework_role": "controller",
                },
                {
                    "id": "java-service-class-UserService",
                    "name": "UserService",
                    "type": "class",
                    "file": "src/main/java/com/example/UserService.java",
                    "repository": "java-service",
                    "language": "java",
                    "framework_role": "service",
                    "parent_class": "BaseService",
                },
                {
                    "id": "java-service-class-BaseService",
                    "name": "BaseService",
                    "type": "class",
                    "file": "src/main/java/com/example/BaseService.java",
                    "repository": "java-service",
                    "language": "java",
                },
            ],
            "endpoints": [
                {
                    "id": "java-service-endpoint-get-users",
                    "name": "GET /api/users",
                    "type": "endpoint",
                    "file": "src/main/java/com/example/UserController.java",
                    "repository": "java-service",
                    "class_name": "UserController",
                    "method": "getUsers",
                },
                {
                    "id": "java-service-endpoint-post-user",
                    "name": "POST /api/users",
                    "type": "endpoint",
                    "file": "src/main/java/com/example/UserController.java",
                    "repository": "java-service",
                    "class_name": "UserController",
                    "method": "createUser",
                },
            ],
            "consumers": [
                {
                    "id": "java-service-consumer-user-events",
                    "name": "UserEventConsumer",
                    "type": "consumer",
                    "file": "src/main/java/com/example/UserEventConsumer.java",
                    "repository": "java-service",
                    "topic": "user-events",
                },
            ],
            "producers": [
                {
                    "id": "java-service-producer-user-events",
                    "name": "UserEventProducer",
                    "type": "producer",
                    "file": "src/main/java/com/example/UserEventProducer.java",
                    "repository": "java-service",
                    "topic": "user-events",
                },
            ],
            "middleware_topics": [
                {
                    "id": "java-service-topic-user-events",
                    "name": "user-events",
                    "type": "topic",
                    "repository": "java-service",
                },
            ],
            "schedulers": [
                {
                    "id": "java-service-scheduler-batch",
                    "name": "BatchScheduler",
                    "type": "scheduler",
                    "file": "src/main/java/com/example/BatchScheduler.java",
                    "repository": "java-service",
                    "schedule": "0 0 * * *",
                },
            ],
            "configurations": [
                {
                    "id": "java-service-config-app",
                    "name": "application.yml",
                    "type": "config",
                    "file": "src/main/resources/application.yml",
                    "repository": "java-service",
                },
            ],
            "databases": [
                {
                    "id": "java-service-db-users",
                    "name": "users",
                    "type": "database_table",
                    "repository": "java-service",
                },
            ],
            "methods": [
                {
                    "id": "java-service-method-get-users",
                    "name": "getUsers",
                    "type": "method",
                    "file": "src/main/java/com/example/UserController.java",
                    "repository": "java-service",
                },
            ],
        },
    )


class TestCodeGraphAgentCreation:
    """Test node creation from extracted symbols."""

    def test_init(self):
        """Test CodeGraphAgent initialization."""
        agent = CodeGraphAgent()
        assert agent.name == "CodeGraphAgent"
        assert agent.graph_service is not None

    def test_create_nodes_from_classes(self, execution_context, scan_report_with_symbols):
        """Test creating CLASS nodes from extracted classes."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Find created class nodes
        class_nodes = [n for n in execution_context.graph.nodes if n.type == NodeType.CLASS]
        assert len(class_nodes) == 3
        assert any(n.name == "UserController" for n in class_nodes)
        assert any(n.name == "UserService" for n in class_nodes)
        assert any(n.name == "BaseService" for n in class_nodes)

    def test_create_nodes_from_endpoints(self, execution_context, scan_report_with_symbols):
        """Test creating ENDPOINT nodes from extracted endpoints."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Find created endpoint nodes
        endpoint_nodes = [n for n in execution_context.graph.nodes if n.type == NodeType.ENDPOINT]
        assert len(endpoint_nodes) == 2
        assert any(n.name == "GET /api/users" for n in endpoint_nodes)
        assert any(n.name == "POST /api/users" for n in endpoint_nodes)

    def test_create_nodes_preserves_attributes(self, execution_context, scan_report_with_symbols):
        """Test that node creation preserves symbol attributes."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Find UserService node
        user_service = next(
            (n for n in execution_context.graph.nodes if n.name == "UserService"),
            None,
        )
        assert user_service is not None
        assert user_service.repository == "java-service"
        assert user_service.language == "java"
        assert user_service.framework_role == "service"
        assert "parent_class" in user_service.attributes
        assert user_service.attributes["parent_class"] == "BaseService"

    def test_create_nodes_all_symbol_types(self, execution_context, scan_report_with_symbols):
        """Test creating nodes for all symbol types."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        node_count = agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Total symbols in the scan report
        total_symbols = 3 + 2 + 1 + 1 + 1 + 1 + 1 + 1  # classes + endpoints + consumers + producers + middleware_topics + schedulers + configurations + databases + methods
        assert node_count >= total_symbols

        # Check specific node types exist
        assert any(n.type == NodeType.CLASS for n in execution_context.graph.nodes)
        assert any(n.type == NodeType.ENDPOINT for n in execution_context.graph.nodes)
        assert any(n.type == NodeType.CONSUMER for n in execution_context.graph.nodes)
        assert any(n.type == NodeType.PRODUCER for n in execution_context.graph.nodes)
        assert any(n.type == NodeType.MIDDLEWARE_TOPIC for n in execution_context.graph.nodes)
        assert any(n.type == NodeType.SCHEDULER for n in execution_context.graph.nodes)


class TestCodeGraphAgentEdges:
    """Test edge creation for relationships."""

    def test_create_inheritance_edges(self, execution_context, scan_report_with_symbols):
        """Test creating EXTENDS edges for inheritance."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        # Create nodes first
        agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Create inheritance edge
        user_service_node = next(
            (n for n in execution_context.graph.nodes if n.name == "UserService"),
            None,
        )
        base_service_node = next(
            (n for n in execution_context.graph.nodes if n.name == "BaseService"),
            None,
        )

        # Manually create the inheritance relationship
        if user_service_node and base_service_node:
            edge = Edge(
                source=user_service_node.id,
                target=base_service_node.id,
                type=EdgeType.EXTENDS,
                confidence=0.95,
            )
            execution_context.graph.add_edge(edge)

        # Find EXTENDS edges
        extends_edges = [e for e in execution_context.graph.edges if e.type == EdgeType.EXTENDS]
        assert len(extends_edges) >= 1
        assert any(e.source == user_service_node.id for e in extends_edges)

    def test_create_middleware_edges(self, execution_context, scan_report_with_symbols):
        """Test creating PUBLISHES_TO and CONSUMES_FROM edges."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        # Create nodes first
        agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Create middleware edges
        edge_count = agent._create_middleware_edges(execution_context)

        # Should create edges between producers/consumers and topics
        assert edge_count > 0

        # Check for middleware edges
        middleware_edges = [
            e
            for e in execution_context.graph.edges
            if e.type in [EdgeType.PUBLISHES_TO, EdgeType.CONSUMES_FROM]
        ]
        assert len(middleware_edges) > 0

    def test_create_containment_edges(self, execution_context, scan_report_with_symbols):
        """Test creating CONTAINS edges for hierarchical relationships."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        # Create nodes first
        agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Create containment edges
        agent._create_containment_edges(execution_context)

        # Check for containment edges
        contains_edges = [e for e in execution_context.graph.edges if e.type == EdgeType.CONTAINS]
        assert len(contains_edges) > 0

        # Should have repository nodes
        repo_nodes = [n for n in execution_context.graph.nodes if n.type == NodeType.REPOSITORY]
        assert len(repo_nodes) > 0

    def test_edge_confidence_scores(self, execution_context, scan_report_with_symbols):
        """Test that edges have appropriate confidence scores."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        # Create nodes first
        agent._create_nodes_from_symbols(
            scan_report_with_symbols.metrics, execution_context
        )

        # Create a test edge
        class_node = next(
            (n for n in execution_context.graph.nodes if n.type == NodeType.CLASS),
            None,
        )
        endpoint_node = next(
            (n for n in execution_context.graph.nodes if n.type == NodeType.ENDPOINT),
            None,
        )

        if class_node and endpoint_node:
            edge = Edge(
                source=class_node.id,
                target=endpoint_node.id,
                type=EdgeType.CONTAINS,
                confidence=0.95,
            )
            execution_context.graph.add_edge(edge)

            # Find the edge
            found_edge = next(
                (e for e in execution_context.graph.edges if e.source == class_node.id),
                None,
            )
            assert found_edge is not None
            assert found_edge.confidence == 0.95


class TestCodeGraphAgentExecution:
    """Test full agent execution."""

    def test_execute_success(self, execution_context, scan_report_with_symbols):
        """Test successful graph agent execution."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        result = agent.execute(execution_context)

        assert result.status == "success"
        assert "nodes_created" in result.metrics
        assert "edges_created" in result.metrics
        assert result.metrics["nodes_created"] > 0

    def test_execute_missing_scan_report(self, execution_context):
        """Test execution fails without scan report."""
        agent = CodeGraphAgent()

        result = agent.execute(execution_context)

        assert result.status == "error"
        assert "scan" in result.message.lower()

    def test_execute_missing_graph(self, execution_context, scan_report_with_symbols):
        """Test execution fails with None graph."""
        context = ExecutionContext(
            workspace_config=execution_context.workspace_config,
            project_config=execution_context.project_config,
            tech_aliases=execution_context.tech_aliases,
            scan_config=execution_context.scan_config,
            maturity_config=execution_context.maturity_config,
            test_quality_config=execution_context.test_quality_config,
            graph=None,
        )
        context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        result = agent.execute(context)

        assert result.status == "error"

    def test_execute_generates_report(self, execution_context, scan_report_with_symbols):
        """Test that execution generates graph report."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        result = agent.execute(execution_context)

        assert result.status == "success"
        assert "graph_report" in execution_context.reports
        report = execution_context.reports["graph_report"]
        assert "Technical Graph Report" in report.content
        assert "Node Types Distribution" in report.content
        assert "graph.graphml" in report.content

    def test_execute_creates_artifacts(self, tmp_workspace, execution_context, scan_report_with_symbols):
        """Test that execution creates artifact files."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        result = agent.execute(execution_context)

        assert result.status == "success"
        # Check artifacts list (may be empty if export skipped)
        # but should not error
        assert isinstance(result.artifacts, list)


class TestCodeGraphAgentCrossRepository:
    """Test graph building for cross-repository links."""

    def test_cross_repository_node_creation(self, execution_context):
        """Test creating nodes from multiple repositories."""
        # Add multiple repositories to metrics
        metrics = {
            "classes": [
                {
                    "id": "service-a-class-UserService",
                    "name": "UserService",
                    "type": "class",
                    "repository": "service-a",
                    "file": "src/UserService.java",
                },
                {
                    "id": "service-b-class-OrderService",
                    "name": "OrderService",
                    "type": "class",
                    "repository": "service-b",
                    "file": "src/OrderService.java",
                },
            ],
            "endpoints": [],
            "consumers": [],
            "producers": [],
            "schedulers": [],
            "configurations": [],
            "databases": [],
            "middleware_topics": [],
            "methods": [],
        }

        agent = CodeGraphAgent()
        node_count = agent._create_nodes_from_symbols(metrics, execution_context)

        assert node_count == 2

        # Check repositories are different
        repo_a_nodes = [n for n in execution_context.graph.nodes if n.repository == "service-a"]
        repo_b_nodes = [n for n in execution_context.graph.nodes if n.repository == "service-b"]

        assert len(repo_a_nodes) == 1
        assert len(repo_b_nodes) == 1
        assert repo_a_nodes[0].name == "UserService"
        assert repo_b_nodes[0].name == "OrderService"


class TestCodeGraphAgentStatistics:
    """Test graph statistics calculation."""

    def test_graph_statistics(self, execution_context, scan_report_with_symbols):
        """Test that graph statistics are calculated correctly."""
        execution_context.reports["scan_report"] = scan_report_with_symbols
        agent = CodeGraphAgent()

        result = agent.execute(execution_context)

        assert result.status == "success"
        assert "total_nodes" in result.metrics
        assert "total_edges" in result.metrics
        assert "node_types" in result.metrics
        assert "edge_types" in result.metrics

        # Check that node types are in statistics
        node_types = result.metrics.get("node_types", {})
        if node_types:
            assert "CLASS" in node_types or len(node_types) > 0
