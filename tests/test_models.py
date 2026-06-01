"""Tests for core data models: Node, Edge, Graph, ExecutionContext."""

import pytest
from typing import Dict, List
from datetime import datetime
from pathlib import Path

from context_builder.models import (
    Node,
    Edge,
    Graph,
    ExecutionContext,
    NodeType,
    EdgeType,
    Report,
    WorkspaceConfig,
    ProjectConfig,
    TechAliases,
    ScanConfig,
    MaturityConfig,
    TestQualityConfig,
    AgentOutput,
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
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
        )
        assert context.graph is graph
        assert context.reports == {}
        assert context.iteration == 0
        assert context.generated_files == []
        assert context.logger is not None

    def test_execution_context_with_workspace_config(self):
        """Test ExecutionContext with WorkspaceConfig."""
        graph = Graph()
        workspace = WorkspaceConfig(
            id="ws-1",
            name="TestWorkspace",
            description="Test",
            context_root=Path("/tmp"),
        )
        context = ExecutionContext(
            workspace_config=workspace,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
        )
        assert context.workspace_config == workspace

    def test_execution_context_with_reports(self):
        """Test ExecutionContext with reports."""
        graph = Graph()
        report = Report(name="test_report", content="Test content")
        reports = {"analysis": report}
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
            reports=reports,
        )
        assert context.reports == reports

    def test_execution_context_iteration_tracking(self):
        """Test ExecutionContext iteration tracking."""
        graph = Graph()
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
        )
        assert context.iteration == 0
        context.iteration += 1
        assert context.iteration == 1

    def test_execution_context_generated_files_tracking(self):
        """Test ExecutionContext generated files tracking."""
        graph = Graph()
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
        )
        assert context.generated_files == []
        context.generated_files.append(Path("models.py"))
        context.generated_files.append(Path("__init__.py"))
        assert len(context.generated_files) == 2
        assert Path("models.py") in context.generated_files

    def test_execution_context_cache(self):
        """Test ExecutionContext cache functionality."""
        graph = Graph()
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
            cache={"initial": "value"},
        )
        assert context.cache == {"initial": "value"}
        context.cache["key1"] = "value1"
        assert context.cache["key1"] == "value1"

    def test_execution_context_holds_pipeline_state(self):
        """Test ExecutionContext holds all pipeline state."""
        graph = Graph()
        node = Node(id="node1", type=NodeType.CLASS, name="UserService")
        graph.add_node(node)

        generated_files = [Path("file1.py")]
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
            iteration=1,
            generated_files=generated_files,
        )

        assert len(context.graph.nodes) == 1
        assert context.iteration == 1
        assert len(context.generated_files) == 1
        assert context.logger is not None

    def test_execution_context_logger_exists(self):
        """Test ExecutionContext has a logger."""
        graph = Graph()
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=graph,
        )
        assert context.logger is not None
        assert hasattr(context.logger, "info") or hasattr(context.logger, "debug")


class TestReport:
    """Tests for Report class."""

    def test_report_creation_minimal(self):
        """Test creating a Report with minimal attributes."""
        report = Report(
            name="analysis_report",
            content="Sample analysis content",
        )
        assert report.name == "analysis_report"
        assert report.content == "Sample analysis content"
        assert report.file_path is None
        assert report.metrics == {}

    def test_report_creation_full(self):
        """Test creating a Report with all attributes."""
        file_path = Path("/tmp/report.md")
        metrics = {"accuracy": 0.95, "coverage": 0.85}
        report = Report(
            name="analysis_report",
            content="Sample analysis content",
            file_path=file_path,
            metrics=metrics,
        )
        assert report.name == "analysis_report"
        assert report.content == "Sample analysis content"
        assert report.file_path == file_path
        assert report.metrics == metrics


class TestWorkspaceConfig:
    """Tests for WorkspaceConfig class."""

    def test_workspace_config_creation_minimal(self):
        """Test creating a WorkspaceConfig with minimal attributes."""
        config = WorkspaceConfig(
            id="ws-001",
            name="MyWorkspace",
            description="Test workspace",
            context_root=Path("/workspace"),
        )
        assert config.id == "ws-001"
        assert config.name == "MyWorkspace"
        assert config.description == "Test workspace"
        assert config.context_root == Path("/workspace")
        assert config.repositories == []
        assert config.gitlab_enabled is False
        assert config.gitlab_base_url is None
        assert config.gitlab_group is None

    def test_workspace_config_creation_full(self):
        """Test creating a WorkspaceConfig with all attributes."""
        repositories = [{"name": "repo1", "url": "https://github.com/user/repo1"}]
        config = WorkspaceConfig(
            id="ws-001",
            name="MyWorkspace",
            description="Test workspace",
            context_root=Path("/workspace"),
            repositories=repositories,
            gitlab_enabled=True,
            gitlab_base_url="https://gitlab.com",
            gitlab_group="my-group",
        )
        assert config.id == "ws-001"
        assert config.repositories == repositories
        assert config.gitlab_enabled is True
        assert config.gitlab_base_url == "https://gitlab.com"
        assert config.gitlab_group == "my-group"


class TestProjectConfig:
    """Tests for ProjectConfig class."""

    def test_project_config_creation_minimal(self):
        """Test creating a ProjectConfig with minimal attributes."""
        config = ProjectConfig()
        assert config.projects == []

    def test_project_config_creation_with_projects(self):
        """Test creating a ProjectConfig with projects."""
        projects = [
            {"name": "project1", "path": "/path/to/project1"},
            {"name": "project2", "path": "/path/to/project2"},
        ]
        config = ProjectConfig(projects=projects)
        assert config.projects == projects
        assert len(config.projects) == 2


class TestTechAliases:
    """Tests for TechAliases class."""

    def test_tech_aliases_creation_minimal(self):
        """Test creating a TechAliases with minimal attributes."""
        aliases = TechAliases()
        assert aliases.aliases == []

    def test_tech_aliases_creation_with_aliases(self):
        """Test creating a TechAliases with alias mappings."""
        alias_list = [
            {"tech": "java", "aliases": ["Java", "JAVA"]},
            {"tech": "python", "aliases": ["Python", "py"]},
        ]
        aliases = TechAliases(aliases=alias_list)
        assert aliases.aliases == alias_list
        assert len(aliases.aliases) == 2


class TestScanConfig:
    """Tests for ScanConfig class."""

    def test_scan_config_creation_minimal(self):
        """Test creating a ScanConfig with defaults."""
        config = ScanConfig()
        assert len(config.include_patterns) > 0
        assert len(config.exclude_patterns) > 0
        assert isinstance(config.analysis_depth, dict)
        assert config.incremental is True

    def test_scan_config_include_patterns(self):
        """Test that ScanConfig has required include patterns."""
        config = ScanConfig()
        assert "**/*.java" in config.include_patterns
        assert "**/*.py" in config.include_patterns
        assert "**/pom.xml" in config.include_patterns

    def test_scan_config_exclude_patterns(self):
        """Test that ScanConfig has required exclude patterns."""
        config = ScanConfig()
        assert "**/target/**" in config.exclude_patterns
        assert "**/node_modules/**" in config.exclude_patterns
        assert "**/.git/**" in config.exclude_patterns

    def test_scan_config_analysis_depth_defaults(self):
        """Test that ScanConfig has all required analysis depth flags."""
        config = ScanConfig()
        required_keys = [
            "class_level", "method_level", "flow_level", "config_level",
            "db_analysis", "middleware_analysis", "exception_flow",
            "test_quality", "technical_debt",
        ]
        for key in required_keys:
            assert key in config.analysis_depth
            assert isinstance(config.analysis_depth[key], bool)


class TestMaturityConfig:
    """Tests for MaturityConfig class."""

    def test_maturity_config_creation_minimal(self):
        """Test creating a MaturityConfig with defaults."""
        config = MaturityConfig()
        assert config.target_score == 80
        assert config.max_iterations == 5
        assert isinstance(config.dimensions, dict)

    def test_maturity_config_dimensions(self):
        """Test that MaturityConfig has all required dimensions."""
        config = MaturityConfig()
        required_dims = [
            "project_structure", "code_understanding", "flow_understanding",
            "data_understanding", "middleware_understanding", "test_intelligence",
            "documentation_quality", "risk_analysis",
        ]
        for dim in required_dims:
            assert dim in config.dimensions
            assert "weight" in config.dimensions[dim]

    def test_maturity_config_custom_target(self):
        """Test creating a MaturityConfig with custom target score."""
        config = MaturityConfig(target_score=90, max_iterations=10)
        assert config.target_score == 90
        assert config.max_iterations == 10


class TestTestQualityConfig:
    """Tests for TestQualityConfig class."""

    def test_test_quality_config_creation_minimal(self):
        """Test creating a TestQualityConfig with defaults."""
        config = TestQualityConfig()
        assert config.target_score == 80
        assert isinstance(config.coverage_sources, dict)
        assert isinstance(config.scoring, dict)

    def test_test_quality_config_coverage_sources(self):
        """Test that TestQualityConfig has required coverage sources."""
        config = TestQualityConfig()
        assert "java" in config.coverage_sources
        assert "javascript" in config.coverage_sources
        assert "python" in config.coverage_sources

    def test_test_quality_config_scoring_dimensions(self):
        """Test that TestQualityConfig has all required scoring dimensions."""
        config = TestQualityConfig()
        required_scoring = [
            "line_coverage", "branch_coverage", "critical_flow_coverage",
            "assertion_quality", "negative_test_coverage", "integration_test_coverage",
            "boundary_case_coverage", "test_maintainability",
        ]
        for scoring_key in required_scoring:
            assert scoring_key in config.scoring
            assert isinstance(config.scoring[scoring_key], int)

    def test_test_quality_config_custom_target(self):
        """Test creating a TestQualityConfig with custom target score."""
        config = TestQualityConfig(target_score=90)
        assert config.target_score == 90


class TestAgentOutput:
    """Tests for AgentOutput class."""

    def test_agent_output_creation_minimal(self):
        """Test creating an AgentOutput with minimal attributes."""
        output = AgentOutput(
            status="success",
            message="Task completed",
        )
        assert output.status == "success"
        assert output.message == "Task completed"
        assert output.artifacts == []
        assert output.metrics == {}
        assert output.errors == []

    def test_agent_output_creation_full(self):
        """Test creating an AgentOutput with all attributes."""
        artifacts = [Path("/tmp/file1.py"), Path("/tmp/file2.py")]
        metrics = {"execution_time": 2.5, "files_generated": 2}
        errors = ["Warning: deprecated API used"]
        output = AgentOutput(
            status="success",
            message="Task completed",
            artifacts=artifacts,
            metrics=metrics,
            errors=errors,
        )
        assert output.status == "success"
        assert output.message == "Task completed"
        assert output.artifacts == artifacts
        assert output.metrics == metrics
        assert output.errors == errors

    def test_agent_output_with_errors(self):
        """Test creating an AgentOutput with error status."""
        output = AgentOutput(
            status="failed",
            message="Task failed",
            errors=["File not found", "Invalid configuration"],
        )
        assert output.status == "failed"
        assert len(output.errors) == 2
        assert "File not found" in output.errors
