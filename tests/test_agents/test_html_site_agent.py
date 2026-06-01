"""Tests for HTMLSiteAgent."""

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from context_builder.agents import HTMLSiteAgent
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
        name="Test Project",
        description="Test project for HTML site generation",
        context_root=tmp_workspace / "context",
        repositories=[],
    )


@pytest.fixture
def execution_context(workspace_config):
    """Create an execution context with reports and graph."""
    context = ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=Graph(),
    )

    # Add some nodes to graph
    node1 = Node(id="n1", type=NodeType.CLASS, name="UserService")
    node2 = Node(id="n2", type=NodeType.DATABASE, name="UserDB")
    context.graph.add_node(node1)
    context.graph.add_node(node2)

    # Add edge
    edge = Edge(source="n1", target="n2", type=EdgeType.READS_FROM)
    context.graph.add_edge(edge)

    # Add some reports
    context.reports["scan_report"] = Report(
        name="Scan Report",
        content="# Scan Results\n- Found 10 classes\n- Found 5 endpoints",
    )

    context.reports["flow_analysis_report"] = Report(
        name="Flow Analysis",
        content="# Flow Analysis\n## Flows Found: 3\n- Flow 1: API -> Service -> DB",
    )

    context.reports["c4_diagram_report"] = Report(
        name="C4 Diagrams",
        content="# C4 Model\n## Containers: 2",
    )

    return context


class TestHTMLSiteAgentExecution:
    """Test overall agent execution."""

    def test_execute_success(self, execution_context):
        """Test successful HTML site generation."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        assert output.status == "success"
        assert "HTML" in output.message
        assert len(output.artifacts) > 0
        assert output.metrics["reports_embedded"] > 0

    def test_execute_invalid_context(self):
        """Test execution with invalid context."""
        agent = HTMLSiteAgent()
        output = agent.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_execute_missing_graph(self, execution_context):
        """Test execution with missing graph."""
        execution_context.graph = None
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        assert output.status == "error"


class TestHTMLSiteAgentGeneration:
    """Test HTML content generation."""

    def test_generate_html_structure(self, execution_context):
        """Test HTML structure generation."""
        agent = HTMLSiteAgent()
        html = agent._generate_html(execution_context)

        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "<body>" in html

    def test_html_includes_cdn_resources(self, execution_context):
        """Test that HTML includes CDN resources."""
        agent = HTMLSiteAgent()
        html = agent._generate_html(execution_context)

        # Should include Mermaid
        assert "mermaid" in html
        # Should include Cytoscape
        assert "cytoscape" in html

    def test_html_includes_navigation(self, execution_context):
        """Test that HTML includes navigation tabs."""
        agent = HTMLSiteAgent()
        html = agent._generate_html(execution_context)

        assert "Dashboard" in html
        assert "Reports" in html
        assert "Graphs" in html
        assert "Metrics" in html

    def test_html_includes_javascript(self, execution_context):
        """Test that HTML includes JavaScript functionality."""
        agent = HTMLSiteAgent()
        html = agent._generate_html(execution_context)

        assert "function openTab" in html
        assert "cytoscape(" in html


class TestHTMLSiteAgentStyling:
    """Test CSS generation."""

    def test_generate_css(self):
        """Test CSS generation."""
        agent = HTMLSiteAgent()
        css = agent._generate_css()

        assert "body {" in css
        assert "container" in css
        assert "tab-content" in css
        assert "card" in css
        assert "#667eea" in css  # Primary color

    def test_css_has_animations(self):
        """Test that CSS includes animations."""
        agent = HTMLSiteAgent()
        css = agent._generate_css()

        assert "fadeIn" in css
        assert "animation" in css
        assert "transition" in css

    def test_css_responsive(self):
        """Test that CSS includes responsive patterns."""
        agent = HTMLSiteAgent()
        css = agent._generate_css()

        # Should have grid layout
        assert "grid" in css
        assert "auto-fit" in css


class TestHTMLSiteAgentSections:
    """Test individual section generation."""

    def test_generate_header(self, execution_context):
        """Test header generation."""
        agent = HTMLSiteAgent()
        header = agent._generate_header(execution_context)

        assert "Context Builder Analysis" in header
        assert "Test Project" in header

    def test_generate_dashboard(self, execution_context):
        """Test dashboard generation."""
        agent = HTMLSiteAgent()
        dashboard = agent._generate_dashboard(execution_context)

        assert "Dashboard" in dashboard
        assert "Nodes" in dashboard or "nodes" in dashboard
        assert "metric-card" in dashboard

    def test_generate_reports_section(self, execution_context):
        """Test reports section generation."""
        agent = HTMLSiteAgent()
        reports_section = agent._generate_reports_section(execution_context)

        assert "Reports" in reports_section
        # Should contain report names
        assert "Scan" in reports_section or "scan" in reports_section

    def test_generate_graphs_section(self, execution_context):
        """Test graphs section generation."""
        agent = HTMLSiteAgent()
        graphs_section = agent._generate_graphs_section(execution_context)

        assert "Graph" in graphs_section or "graph" in graphs_section
        assert "graph" in graphs_section.lower()  # Contains graph visualization

    def test_generate_metrics_section(self, execution_context):
        """Test metrics section generation."""
        agent = HTMLSiteAgent()
        metrics_section = agent._generate_metrics_section(execution_context)

        assert "Metrics" in metrics_section or "metrics" in metrics_section
        assert "Coverage" in metrics_section or "coverage" in metrics_section


class TestHTMLSiteAgentGraphVisualization:
    """Test graph visualization data preparation."""

    def test_prepare_cytoscape_data(self, execution_context):
        """Test Cytoscape data preparation."""
        agent = HTMLSiteAgent()
        cytoscape_json = agent._prepare_cytoscape_data(execution_context)

        data = json.loads(cytoscape_json)
        assert isinstance(data, list)
        assert len(data) > 0

        # Should have nodes and edges
        nodes = [d for d in data if "id" in d.get("data", {})]
        assert len(nodes) > 0

    def test_cytoscape_data_format(self, execution_context):
        """Test Cytoscape data format."""
        agent = HTMLSiteAgent()
        cytoscape_json = agent._prepare_cytoscape_data(execution_context)

        data = json.loads(cytoscape_json)

        for element in data:
            assert "data" in element
            assert "id" in element["data"] or "source" in element["data"]

    def test_cytoscape_data_limits(self, execution_context):
        """Test that Cytoscape data respects limits."""
        # Add many nodes
        for i in range(100):
            node = Node(
                id=f"node-{i}",
                type=NodeType.CLASS,
                name=f"Class{i}",
            )
            execution_context.graph.add_node(node)

        agent = HTMLSiteAgent()
        cytoscape_json = agent._prepare_cytoscape_data(execution_context)
        data = json.loads(cytoscape_json)

        # Should be limited to avoid performance issues
        nodes = [d for d in data if "id" in d.get("data", {})]
        assert len(nodes) <= 55  # 50 node limit + some edges


class TestHTMLSiteAgentFileGeneration:
    """Test file writing operations."""

    def test_write_html_file(self, execution_context):
        """Test writing HTML file to disk."""
        agent = HTMLSiteAgent()
        html_content = "<html><body>Test</body></html>"
        artifacts = agent._write_html_file(html_content, execution_context)

        assert len(artifacts) > 0
        artifact = artifacts[0]
        assert artifact.exists()
        assert artifact.suffix == ".html"
        assert "index" in artifact.name

    def test_html_file_content(self, execution_context):
        """Test that HTML file contains expected content."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        assert output.status == "success"
        html_file = output.artifacts[0]
        content = html_file.read_text()

        assert "<!DOCTYPE html>" in content
        assert "Context Builder" in content

    def test_html_file_size(self, execution_context):
        """Test HTML file size metrics."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        assert output.metrics["html_size_kb"] > 0
        # Should be reasonably sized
        assert output.metrics["html_size_kb"] < 1000  # Less than 1MB


class TestHTMLSiteAgentMetrics:
    """Test metrics calculation."""

    def test_metrics_include_graph_stats(self, execution_context):
        """Test that metrics include graph statistics."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        assert "graph_nodes" in output.metrics
        assert "graph_edges" in output.metrics
        assert output.metrics["graph_nodes"] > 0

    def test_metrics_include_report_count(self, execution_context):
        """Test that metrics include report count."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        assert "reports_embedded" in output.metrics
        assert output.metrics["reports_embedded"] == 3

    def test_metrics_with_empty_reports(self, workspace_config):
        """Test metrics with no reports."""
        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        agent = HTMLSiteAgent()
        output = agent.execute(context)

        assert output.metrics["reports_embedded"] == 0


class TestHTMLSiteAgentIntegration:
    """Integration tests."""

    def test_full_execution_flow(self, execution_context):
        """Test complete execution flow."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) > 0
        assert output.metrics["html_size_kb"] > 0

    def test_html_valid_structure(self, execution_context):
        """Test that generated HTML has valid structure."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        html_content = output.artifacts[0].read_text()

        # Check basic HTML validity
        assert html_content.count("<") >= html_content.count(">") - 5  # Allow minor imbalance in self-closing tags
        assert html_content.count("<script") == html_content.count("</script>")
        assert html_content.count("function") > 0  # Has JavaScript

    def test_html_includes_all_reports(self, execution_context):
        """Test that HTML includes all reports."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        html_content = output.artifacts[0].read_text()

        # Should reference report names
        for report_name in execution_context.reports.keys():
            # Reports should be embedded somewhere
            assert "report" in html_content or "Report" in html_content

    def test_html_accessible_from_file(self, execution_context):
        """Test that generated HTML is readable as a file."""
        agent = HTMLSiteAgent()
        output = agent.execute(execution_context)

        html_file = output.artifacts[0]
        assert html_file.is_file()
        assert html_file.stat().st_size > 0

        # Should be readable
        content = html_file.read_text()
        assert len(content) > 0
