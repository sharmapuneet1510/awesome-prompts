"""Tests for writer agents: MarkdownWriter, HTMLWriter, GraphWriter, JSONWriter."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from context_builder.agents.markdown_writer import MarkdownWriter
from context_builder.agents.html_writer import HTMLWriter
from context_builder.agents.graph_writer import GraphWriter
from context_builder.agents.json_writer import JSONWriter
from context_builder.models import (
    ExecutionContext,
    Graph,
    Node,
    Edge,
    NodeType,
    EdgeType,
    WorkspaceConfig,
    Report,
)


# Fixtures


@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    graph = Graph()

    # Add nodes
    nodes = [
        Node(id="repo-1", type=NodeType.REPOSITORY, name="MainRepo", path="/main"),
        Node(id="module-1", type=NodeType.MODULE, name="CoreModule", path="/core"),
        Node(id="class-1", type=NodeType.CLASS, name="UserService", path="/core/UserService.java"),
        Node(id="method-1", type=NodeType.METHOD, name="createUser", path="/core/UserService.java#createUser"),
        Node(id="endpoint-1", type=NodeType.ENDPOINT, name="POST /users", path="/api/users", framework_role="POST"),
        Node(id="db-1", type=NodeType.DATABASE, name="PostgreSQL", path="postgres://localhost"),
        Node(id="table-1", type=NodeType.DATABASE_TABLE, name="users_table", path="public.users"),
        Node(id="test-1", type=NodeType.TEST_CLASS, name="UserServiceTest", path="/test/UserServiceTest.java"),
        Node(id="debt-1", type=NodeType.TECHNICAL_DEBT, name="Missing null checks",
             attributes={"severity": "high", "description": "Service lacks validation"}),
        Node(id="risk-1", type=NodeType.RISK, name="SQL injection risk",
             attributes={"probability": "low", "impact": "critical", "mitigation": "Use parameterized queries"}),
    ]
    for node in nodes:
        graph.add_node(node)

    # Add edges
    edges = [
        Edge(source="repo-1", target="module-1", type=EdgeType.CONTAINS),
        Edge(source="module-1", target="class-1", type=EdgeType.CONTAINS),
        Edge(source="class-1", target="method-1", type=EdgeType.CONTAINS),
        Edge(source="endpoint-1", target="method-1", type=EdgeType.CALLS),
        Edge(source="class-1", target="table-1", type=EdgeType.READS_FROM),
        Edge(source="test-1", target="class-1", type=EdgeType.TESTS),
    ]
    for edge in edges:
        graph.add_edge(edge)

    return graph


@pytest.fixture
def execution_context(sample_graph):
    """Create an execution context for testing."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace for analysis",
        context_root=Path("/tmp/.context"),
    )

    context = ExecutionContext(
        workspace_config=workspace_config,
        project_config=None,
        tech_aliases=None,
        scan_config=None,
        maturity_config=None,
        test_quality_config=None,
        graph=sample_graph,
    )

    # Add some reports
    context.reports["overview"] = Report(
        name="Overview",
        content="This is the overview report",
    )
    context.reports["architecture"] = Report(
        name="Architecture",
        content="System architecture details",
    )

    return context


# Tests for MarkdownWriter


class TestMarkdownWriter:
    """Test suite for MarkdownWriter agent."""

    def test_markdown_writer_initialization(self):
        """Test MarkdownWriter initializes with correct name."""
        writer = MarkdownWriter()
        assert writer.name == "MarkdownWriter"

    def test_markdown_writer_execute_success(self, execution_context, tmp_path):
        """Test successful markdown generation."""
        writer = MarkdownWriter()

        # Mock the output directory
        with patch.object(writer, "_create_output_dir", return_value=tmp_path):
            output = writer.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) > 0
        assert output.metrics["total_nodes"] == len(execution_context.graph.nodes)

    def test_markdown_writer_execute_invalid_context(self):
        """Test MarkdownWriter handles invalid context."""
        writer = MarkdownWriter()
        output = writer.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_markdown_generate_index(self, execution_context):
        """Test index.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_index(execution_context)

        assert "Test Workspace" in content
        assert "Table of Contents" in content
        assert "architecture.md" in content
        assert len(content) > 200

    def test_markdown_generate_architecture(self, execution_context):
        """Test architecture.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_architecture(execution_context)

        assert "System Architecture" in content
        assert "Repositories" in content
        assert len(content) > 100

    def test_markdown_generate_flow_analysis(self, execution_context):
        """Test flow-analysis.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_flow_analysis(execution_context)

        assert "Business Flow" in content
        assert "Data Flow" in content
        assert len(content) > 100

    def test_markdown_generate_code_structure(self, execution_context):
        """Test code-structure.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_code_structure(execution_context)

        assert "Code Structure" in content
        assert "Packages" in content
        assert len(content) > 100

    def test_markdown_generate_test_intelligence(self, execution_context):
        """Test test-intelligence.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_test_intelligence(execution_context)

        assert "Test Intelligence" in content
        assert "Test Classes" in content
        assert len(content) > 100

    def test_markdown_generate_technical_debt(self, execution_context):
        """Test technical-debt.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_technical_debt(execution_context)

        assert "Technical Debt" in content
        assert "Issues" in content
        assert len(content) > 100

    def test_markdown_generate_risk_assessment(self, execution_context):
        """Test risk-assessment.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_risk_assessment(execution_context)

        assert "Risk Assessment" in content
        assert "Risk Register" in content
        assert len(content) > 100

    def test_markdown_generate_endpoints(self, execution_context):
        """Test endpoints.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_endpoints(execution_context)

        assert "API Endpoints" in content
        assert "POST /users" in content
        assert len(content) > 100

    def test_markdown_generate_databases(self, execution_context):
        """Test databases.md generation."""
        writer = MarkdownWriter()
        content = writer._generate_databases(execution_context)

        assert "Data Models" in content
        assert "PostgreSQL" in content
        assert len(content) > 100

    def test_markdown_get_nodes_by_type(self, execution_context):
        """Test node filtering by type."""
        writer = MarkdownWriter()
        classes = writer._get_nodes_by_type(execution_context, NodeType.CLASS)

        assert len(classes) == 1
        assert classes[0].name == "UserService"

    def test_markdown_get_related_nodes(self, execution_context):
        """Test finding related nodes."""
        writer = MarkdownWriter()
        related = writer._get_related_nodes(execution_context, "module-1", EdgeType.CONTAINS)

        assert len(related) == 1
        assert related[0].name == "UserService"


# Tests for HTMLWriter


class TestHTMLWriter:
    """Test suite for HTMLWriter agent."""

    def test_html_writer_initialization(self):
        """Test HTMLWriter initializes with correct name."""
        writer = HTMLWriter()
        assert writer.name == "HTMLWriter"

    def test_html_writer_execute_success(self, execution_context, tmp_path):
        """Test successful HTML generation."""
        writer = HTMLWriter()

        # Mock the output directory
        with patch.object(writer, "_create_output_dir", return_value=tmp_path):
            output = writer.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) == 1
        assert output.metrics["graph_nodes"] == len(execution_context.graph.nodes)

    def test_html_writer_execute_invalid_context(self):
        """Test HTMLWriter handles invalid context."""
        writer = HTMLWriter()
        output = writer.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_html_generate_html_structure(self, execution_context):
        """Test generated HTML contains required structure."""
        writer = HTMLWriter()
        html = writer._generate_html(execution_context)

        assert "<!DOCTYPE html>" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "Test Workspace" in html
        assert "mermaid" in html
        assert "cytoscape" in html

    def test_html_generate_html_tabs(self, execution_context):
        """Test HTML contains navigation tabs."""
        writer = HTMLWriter()
        html = writer._generate_html(execution_context)

        assert "Overview" in html
        assert "Metrics" in html
        assert "Dependency Graph" in html
        assert "Reports" in html
        assert "Statistics" in html

    def test_html_graph_to_cytoscape(self, execution_context):
        """Test graph to Cytoscape conversion."""
        writer = HTMLWriter()
        cytoscape_data = writer._graph_to_cytoscape(execution_context)

        assert "elements" in cytoscape_data
        assert len(cytoscape_data["elements"]) > 0

    def test_html_generate_reports(self, execution_context):
        """Test reports section generation."""
        writer = HTMLWriter()
        html = writer._generate_reports_html(execution_context)

        assert "overview" in html.lower() or "Overview" in html
        assert len(html) > 50

    def test_html_generate_metrics(self, execution_context):
        """Test metrics section generation."""
        writer = HTMLWriter()
        html = writer._generate_metrics_html(execution_context)

        assert "Node Distribution" in html
        assert "Relationship Distribution" in html

    def test_html_calculate_graph_density(self, execution_context):
        """Test graph density calculation."""
        writer = HTMLWriter()
        density = writer._calculate_graph_density(execution_context)

        assert 0 <= density <= 1


# Tests for GraphWriter


class TestGraphWriter:
    """Test suite for GraphWriter agent."""

    def test_graph_writer_initialization(self):
        """Test GraphWriter initializes with correct name."""
        writer = GraphWriter()
        assert writer.name == "GraphWriter"

    def test_graph_writer_execute_success(self, execution_context, tmp_path):
        """Test successful graph export."""
        writer = GraphWriter()

        # Mock the output directory
        with patch.object(writer, "_create_output_dir", return_value=tmp_path):
            output = writer.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) >= 4  # nodes, edges, graphml, summary

    def test_graph_writer_execute_invalid_context(self):
        """Test GraphWriter handles invalid context."""
        writer = GraphWriter()
        output = writer.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_graph_export_nodes(self, execution_context, tmp_path):
        """Test nodes.json export."""
        writer = GraphWriter()
        nodes_path = writer._export_nodes(execution_context, tmp_path)

        assert nodes_path.exists()
        with open(nodes_path) as f:
            data = json.load(f)

        assert data["total_count"] == len(execution_context.graph.nodes)
        assert len(data["nodes"]) > 0

    def test_graph_export_edges(self, execution_context, tmp_path):
        """Test edges.json export."""
        writer = GraphWriter()
        edges_path = writer._export_edges(execution_context, tmp_path)

        assert edges_path.exists()
        with open(edges_path) as f:
            data = json.load(f)

        assert data["total_count"] == len(execution_context.graph.edges)
        assert len(data["edges"]) > 0

    def test_graph_export_graphml(self, execution_context, tmp_path):
        """Test GraphML export."""
        writer = GraphWriter()
        graphml_path = writer._export_graphml(execution_context, tmp_path)

        assert graphml_path.exists()
        content = graphml_path.read_text()

        assert "<?xml version" in content
        assert "<graphml" in content
        assert "<node" in content
        assert "<edge" in content

    def test_graph_generate_graphml_content(self, execution_context):
        """Test GraphML content generation."""
        writer = GraphWriter()
        graphml = writer._generate_graphml(execution_context.graph)

        assert "<?xml version" in graphml
        assert "graphml" in graphml
        assert len(execution_context.graph.nodes) <= graphml.count("<node")

    def test_graph_export_summary(self, execution_context, tmp_path):
        """Test summary.json export."""
        writer = GraphWriter()
        summary_path = writer._export_summary(execution_context, tmp_path)

        assert summary_path.exists()
        with open(summary_path) as f:
            data = json.load(f)

        assert "nodes" in data
        assert "edges" in data
        assert "degree_statistics" in data

    def test_graph_calculate_summary(self, execution_context):
        """Test summary calculation."""
        writer = GraphWriter()
        summary = writer._calculate_summary(execution_context.graph)

        assert summary["nodes"]["total"] == len(execution_context.graph.nodes)
        assert summary["edges"]["total"] == len(execution_context.graph.edges)
        assert "degree_statistics" in summary

    def test_graph_escape_xml(self):
        """Test XML escaping."""
        writer = GraphWriter()

        test_str = '<node name="test&value" />'
        escaped = writer._escape_xml(test_str)

        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&amp;" in escaped


# Tests for JSONWriter


class TestJSONWriter:
    """Test suite for JSONWriter agent."""

    def test_json_writer_initialization(self):
        """Test JSONWriter initializes with correct name."""
        writer = JSONWriter()
        assert writer.name == "JSONWriter"

    def test_json_writer_execute_success(self, execution_context, tmp_path):
        """Test successful JSON export."""
        writer = JSONWriter()

        # Mock the output directory
        with patch.object(writer, "_create_output_dir", return_value=tmp_path):
            output = writer.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) >= 6  # maturity, test quality, risk, debt, stats, summary

    def test_json_writer_execute_invalid_context(self):
        """Test JSONWriter handles invalid context."""
        writer = JSONWriter()
        output = writer.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_json_export_maturity_score(self, execution_context, tmp_path):
        """Test maturity score export."""
        writer = JSONWriter()
        maturity_path = writer._export_maturity_score(execution_context, tmp_path)

        assert maturity_path.exists()
        with open(maturity_path) as f:
            data = json.load(f)

        assert "overall_score" in data
        assert "dimensions" in data
        assert "recommendations" in data

    def test_json_export_test_quality_matrix(self, execution_context, tmp_path):
        """Test quality matrix export."""
        writer = JSONWriter()
        quality_path = writer._export_test_quality_matrix(execution_context, tmp_path)

        assert quality_path.exists()
        with open(quality_path) as f:
            data = json.load(f)

        assert "summary" in data
        assert "dimensions" in data
        assert "overall_quality_score" in data

    def test_json_export_risk_report(self, execution_context, tmp_path):
        """Test risk report export."""
        writer = JSONWriter()
        risk_path = writer._export_risk_report(execution_context, tmp_path)

        assert risk_path.exists()
        with open(risk_path) as f:
            data = json.load(f)

        assert "summary" in data
        assert "risks" in data
        assert "overall_risk_score" in data

    def test_json_export_technical_debt_report(self, execution_context, tmp_path):
        """Test technical debt report export."""
        writer = JSONWriter()
        debt_path = writer._export_technical_debt_report(execution_context, tmp_path)

        assert debt_path.exists()
        with open(debt_path) as f:
            data = json.load(f)

        assert "summary" in data
        assert "issues" in data
        assert "technical_debt_score" in data

    def test_json_export_code_statistics(self, execution_context, tmp_path):
        """Test code statistics export."""
        writer = JSONWriter()
        stats_path = writer._export_code_statistics(execution_context, tmp_path)

        assert stats_path.exists()
        with open(stats_path) as f:
            data = json.load(f)

        assert "graph" in data
        assert "nodes_by_type" in data
        assert "edges_by_type" in data

    def test_json_export_comprehensive_summary(self, execution_context, tmp_path):
        """Test comprehensive summary export."""
        writer = JSONWriter()
        summary_path = writer._export_comprehensive_summary(execution_context, tmp_path)

        assert summary_path.exists()
        with open(summary_path) as f:
            data = json.load(f)

        assert "metadata" in data
        assert "analysis_coverage" in data
        assert "quality_metrics" in data

    def test_json_calculate_overall_maturity(self, execution_context):
        """Test overall maturity calculation."""
        writer = JSONWriter()
        score = writer._calculate_overall_maturity(execution_context)

        assert 0 <= score <= 100

    def test_json_estimate_test_coverage(self, execution_context):
        """Test test coverage estimation."""
        writer = JSONWriter()
        coverage = writer._estimate_test_coverage(execution_context)

        assert 0 <= coverage <= 100

    def test_json_calculate_risk_level(self, execution_context):
        """Test risk level calculation."""
        writer = JSONWriter()
        level = writer._calculate_risk_level(execution_context)

        assert level in ["critical", "high", "medium", "low"]


# Integration tests


class TestWritersIntegration:
    """Integration tests for all writers together."""

    def test_all_writers_execute_successfully(self, execution_context, tmp_path):
        """Test all writers can execute with same context."""
        writers = [
            MarkdownWriter(),
            HTMLWriter(),
            GraphWriter(),
            JSONWriter(),
        ]

        with patch("context_builder.agents.markdown_writer.Path") as mock_path, \
             patch("context_builder.agents.html_writer.Path") as mock_path2, \
             patch("context_builder.agents.graph_writer.Path") as mock_path3, \
             patch("context_builder.agents.json_writer.Path") as mock_path4:

            for writer in writers:
                # Create a unique temp dir for each writer
                writer_tmp = tmp_path / writer.name
                writer_tmp.mkdir(exist_ok=True)

                with patch.object(writer, "_create_output_dir", return_value=writer_tmp):
                    output = writer.execute(execution_context)

                assert output.status == "success"
                assert len(output.artifacts) > 0

    def test_writers_with_empty_graph(self, tmp_path):
        """Test writers handle empty graph gracefully."""
        empty_context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=Graph(),
        )

        writers = [
            MarkdownWriter(),
            HTMLWriter(),
            GraphWriter(),
            JSONWriter(),
        ]

        for writer in writers:
            writer_tmp = tmp_path / writer.name
            writer_tmp.mkdir(exist_ok=True)

            with patch.object(writer, "_create_output_dir", return_value=writer_tmp):
                output = writer.execute(empty_context)

            # Should still succeed but with metrics showing empty graph
            assert output.status == "success"
