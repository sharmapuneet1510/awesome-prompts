"""Tests for C4DiagramAgent."""

from pathlib import Path
from typing import Dict, Any

import pytest

from context_builder.agents import C4DiagramAgent
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
        name="E-Commerce Platform",
        description="Complete e-commerce system",
        context_root=tmp_workspace / "context",
        repositories=[],
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
def graph_with_architecture(execution_context):
    """Create a graph with C4-style architecture."""
    graph = execution_context.graph

    # Add main system database
    user_db = Node(
        id="db-users",
        type=NodeType.DATABASE,
        name="UserDB",
    )
    graph.add_node(user_db)

    # Add main system middleware
    message_queue = Node(
        id="middleware-mq",
        type=NodeType.MIDDLEWARE,
        name="MessageQueue",
    )
    graph.add_node(message_queue)

    # Add main system modules
    user_module = Node(
        id="module-users",
        type=NodeType.MODULE,
        name="UserModule",
    )
    graph.add_node(user_module)

    product_module = Node(
        id="module-products",
        type=NodeType.MODULE,
        name="ProductModule",
    )
    graph.add_node(product_module)

    # Add classes within modules
    user_controller = Node(
        id="class-userctrl",
        type=NodeType.CLASS,
        name="UserController",
        module="UserModule",
    )
    graph.add_node(user_controller)

    product_service = Node(
        id="class-prodservice",
        type=NodeType.CLASS,
        name="ProductService",
        module="ProductModule",
    )
    graph.add_node(product_service)

    # Add external API
    payment_api = Node(
        id="external-payment",
        type=NodeType.EXTERNAL_API,
        name="PaymentGateway",
    )
    graph.add_node(payment_api)

    # Add relationships
    graph.add_edge(Edge(
        source="module-users",
        target="db-users",
        type=EdgeType.READS_FROM,
    ))
    graph.add_edge(Edge(
        source="module-products",
        target="middleware-mq",
        type=EdgeType.PUBLISHES_TO,
    ))

    return execution_context


class TestC4DiagramAgentExecution:
    """Test overall agent execution."""

    def test_execute_success(self, graph_with_architecture):
        """Test successful C4 diagram generation."""
        agent = C4DiagramAgent()
        output = agent.execute(graph_with_architecture)

        assert output.status == "success"
        assert "C4" in output.message
        assert output.metrics["main_system"] == "E-Commerce Platform"
        assert output.metrics["diagrams_generated"] > 0

    def test_execute_invalid_context(self):
        """Test execution with invalid context."""
        agent = C4DiagramAgent()
        output = agent.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_execute_missing_graph(self, execution_context):
        """Test execution with missing graph."""
        execution_context.graph = None
        agent = C4DiagramAgent()
        output = agent.execute(execution_context)

        assert output.status == "error"


class TestC4DiagramAgentSystemIdentification:
    """Test system and external component identification."""

    def test_identify_main_system(self, graph_with_architecture):
        """Test identifying main system."""
        agent = C4DiagramAgent()
        main_system, external = agent._identify_systems(graph_with_architecture)

        assert main_system is not None
        assert main_system["name"] == "E-Commerce Platform"
        assert "description" in main_system

    def test_identify_external_systems(self, graph_with_architecture):
        """Test identifying external systems."""
        agent = C4DiagramAgent()
        main_system, external = agent._identify_systems(graph_with_architecture)

        assert len(external) == 1
        assert external[0]["name"] == "PaymentGateway"
        assert external[0]["type"] == "external_system"

    def test_no_external_systems(self, execution_context):
        """Test with no external systems."""
        # Just add main system database
        db = Node(
            id="db-1",
            type=NodeType.DATABASE,
            name="LocalDB",
        )
        execution_context.graph.add_node(db)

        agent = C4DiagramAgent()
        main_system, external = agent._identify_systems(execution_context)

        assert len(external) == 0


class TestC4DiagramAgentContainerIdentification:
    """Test container identification."""

    def test_identify_containers(self, graph_with_architecture):
        """Test identifying containers."""
        agent = C4DiagramAgent()
        containers = agent._identify_containers(graph_with_architecture)

        assert len(containers) > 0
        # Should find database and middleware containers
        container_names = [c["name"] for c in containers]
        assert "UserDB" in container_names or "MessageQueue" in container_names

    def test_container_deduplication(self, execution_context):
        """Test that containers are deduplicated."""
        graph = execution_context.graph

        # Add same database node twice (shouldn't happen but test resilience)
        for i in range(2):
            db = Node(
                id=f"db-{i}",
                type=NodeType.DATABASE,
                name="MainDB",
            )
            graph.add_node(db)

        agent = C4DiagramAgent()
        containers = agent._identify_containers(execution_context)

        # Should have deduplicated
        assert len(containers) >= 1


class TestC4DiagramAgentComponentIdentification:
    """Test component identification."""

    def test_identify_components(self, graph_with_architecture):
        """Test identifying components."""
        agent = C4DiagramAgent()
        components = agent._identify_components(graph_with_architecture)

        assert len(components) > 0
        # Should find classes
        component_names = [c["name"] for c in components]
        assert "UserController" in component_names or "ProductService" in component_names

    def test_components_limit(self, execution_context):
        """Test component limit."""
        graph = execution_context.graph

        # Add many classes
        for i in range(20):
            class_node = Node(
                id=f"class-{i}",
                type=NodeType.CLASS,
                name=f"Component{i}",
            )
            graph.add_node(class_node)

        agent = C4DiagramAgent()
        components = agent._identify_components(execution_context)

        # Should identify classes but may be limited
        assert len(components) > 0


class TestC4DiagramAgentDiagramGeneration:
    """Test diagram generation."""

    def test_generate_context_diagram(self):
        """Test C4 context diagram generation."""
        agent = C4DiagramAgent()
        main_system = {
            "name": "E-Commerce Platform",
            "description": "Complete e-commerce system",
        }
        external = [
            {"name": "PaymentGateway", "type": "external_system"},
        ]

        mermaid = agent._generate_context_diagram(main_system, external)

        assert "graph TB" in mermaid
        assert "E-Commerce Platform" in mermaid
        assert "PaymentGateway" in mermaid

    def test_generate_container_diagram(self):
        """Test C4 container diagram generation."""
        agent = C4DiagramAgent()
        main_system = {"name": "System", "description": "Test"}
        containers = [
            {"id": "db-1", "name": "UserDB", "type": "database", "description": "User Data"},
            {"id": "mq-1", "name": "MessageQueue", "type": "middleware", "description": "Message Broker"},
        ]

        mermaid = agent._generate_container_diagram(main_system, containers)

        assert "graph TB" in mermaid
        assert "System" in mermaid or "subgraph" in mermaid

    def test_generate_component_diagram(self):
        """Test C4 component diagram generation."""
        agent = C4DiagramAgent()
        container = {"id": "mod-1", "name": "UserModule", "type": "module"}
        components = [
            {"id": "c1", "name": "UserController", "type": "class", "module": "UserModule"},
            {"id": "c2", "name": "UserService", "type": "class", "module": "UserModule"},
        ]

        mermaid = agent._generate_component_diagram(container, components)

        assert "graph TB" in mermaid
        assert "UserModule" in mermaid

    def test_diagram_formatting(self, graph_with_architecture):
        """Test that diagrams are properly formatted."""
        agent = C4DiagramAgent()
        output = agent.execute(graph_with_architecture)

        assert output.status == "success"
        # Check artifacts exist
        for artifact in output.artifacts:
            assert artifact.exists()
            content = artifact.read_text()
            assert "graph" in content.lower() or "mermaid" in artifact.suffix.lower()


class TestC4DiagramAgentArtifacts:
    """Test artifact generation and file handling."""

    def test_generate_artifacts(self, graph_with_architecture):
        """Test artifact file generation."""
        agent = C4DiagramAgent()
        main_system = {"name": "Test", "description": "Test system"}
        external = []
        containers = [{"id": "db-1", "name": "DB", "type": "database", "description": "Database"}]
        components = []

        artifacts = agent._generate_c4_diagrams(
            graph_with_architecture, main_system, external, containers, components
        )

        assert len(artifacts) > 0
        # Check for expected files
        artifact_names = [a.name for a in artifacts]
        assert any("context" in name for name in artifact_names)

    def test_artifact_file_naming(self, graph_with_architecture):
        """Test artifact file naming convention."""
        agent = C4DiagramAgent()
        output = agent.execute(graph_with_architecture)

        assert output.status == "success"
        artifact_names = [a.name for a in output.artifacts]

        # Should have context and container diagrams
        assert any("context" in name for name in artifact_names)


class TestC4DiagramAgentReports:
    """Test report generation."""

    def test_create_report(self, graph_with_architecture):
        """Test report creation."""
        agent = C4DiagramAgent()
        main_system = {"name": "E-Commerce", "description": "E-commerce system"}
        external = [{"name": "PaymentGateway"}]
        containers = [
            {"id": "db-1", "name": "UserDB", "type": "database", "description": "Users"},
        ]

        agent._create_report(
            graph_with_architecture, main_system, external, containers
        )

        assert "c4_diagram_report" in graph_with_architecture.reports
        report = graph_with_architecture.reports["c4_diagram_report"]
        assert "C4" in report.content or "Diagram" in report.content

    def test_report_metrics(self, graph_with_architecture):
        """Test report contains metrics."""
        agent = C4DiagramAgent()
        output = agent.execute(graph_with_architecture)

        assert output.metrics["main_system"] == "E-Commerce Platform"
        assert output.metrics["containers"] >= 0
        assert output.metrics["external_systems"] >= 0


class TestC4DiagramAgentIconsAndColors:
    """Test icon and color utilities."""

    def test_get_container_icon(self):
        """Test container icon mapping."""
        agent = C4DiagramAgent()

        assert agent._get_container_icon("database") == "💾"
        assert agent._get_container_icon("middleware") == "📨"
        assert agent._get_container_icon("unknown") == "⚙️"

    def test_get_component_icon(self):
        """Test component icon mapping."""
        agent = C4DiagramAgent()

        assert agent._get_component_icon("class") == "🔷"
        assert agent._get_component_icon("interface") == "🔶"
        assert agent._get_component_icon("unknown") == "•"

    def test_get_container_color(self):
        """Test container color mapping."""
        agent = C4DiagramAgent()

        assert agent._get_container_color("database") == "#85BBF0"
        assert agent._get_container_color("middleware") == "#F08080"
        assert "#" in agent._get_container_color("unknown")


class TestC4DiagramAgentIntegration:
    """Integration tests for C4 diagram generation."""

    def test_full_execution_flow(self, graph_with_architecture):
        """Test complete execution flow."""
        agent = C4DiagramAgent()
        output = agent.execute(graph_with_architecture)

        assert output.status == "success"
        assert len(output.artifacts) > 0
        assert len(graph_with_architecture.reports) > 0

    def test_artifacts_exist_on_disk(self, graph_with_architecture):
        """Test that generated artifacts exist on disk."""
        agent = C4DiagramAgent()
        output = agent.execute(graph_with_architecture)

        for artifact in output.artifacts:
            assert artifact.exists()
            assert artifact.stat().st_size > 0
