"""Tests for GraphService: graph export to JSON and GraphML formats."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from context_builder.models import Graph, Node, NodeType, Edge, EdgeType
from context_builder.services.graph_service import GraphService


class TestGraphService:
    """Test GraphService class."""

    def test_graph_service_init(self):
        """Test GraphService initialization."""
        service = GraphService()
        assert service is not None
        assert service.logger is not None

    def test_export_to_json_with_nodes_and_edges(self):
        """Test exporting graph with nodes and edges to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            # Create test graph
            graph = Graph()
            node1 = Node(
                id="workspace-1",
                type=NodeType.WORKSPACE,
                name="Test Workspace",
                repository="test-repo"
            )
            node2 = Node(
                id="class-1",
                type=NodeType.CLASS,
                name="TestClass",
                repository="test-repo",
                path="src/TestClass.java"
            )
            graph.add_node(node1)
            graph.add_node(node2)

            edge = Edge(
                source="workspace-1",
                target="class-1",
                type=EdgeType.CONTAINS,
                confidence=0.95
            )
            graph.add_edge(edge)

            service = GraphService()
            result = service.export_to_json(graph, output_dir)

            assert result is True
            assert (output_dir / "nodes.json").exists()
            assert (output_dir / "edges.json").exists()

            # Verify nodes.json content
            with open(output_dir / "nodes.json") as f:
                nodes_data = json.load(f)
            assert len(nodes_data) == 2
            assert nodes_data[0]["id"] == "workspace-1"
            assert nodes_data[0]["type"] == "WORKSPACE"
            assert nodes_data[1]["id"] == "class-1"
            assert nodes_data[1]["type"] == "CLASS"

            # Verify edges.json content
            with open(output_dir / "edges.json") as f:
                edges_data = json.load(f)
            assert len(edges_data) == 1
            assert edges_data[0]["source"] == "workspace-1"
            assert edges_data[0]["target"] == "class-1"
            assert edges_data[0]["type"] == "CONTAINS"
            assert edges_data[0]["confidence"] == 0.95

    def test_export_to_json_empty_graph(self):
        """Test exporting an empty graph to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            graph = Graph()  # Empty graph

            service = GraphService()
            result = service.export_to_json(graph, output_dir)

            assert result is True
            assert (output_dir / "nodes.json").exists()
            assert (output_dir / "edges.json").exists()

            with open(output_dir / "nodes.json") as f:
                nodes_data = json.load(f)
            with open(output_dir / "edges.json") as f:
                edges_data = json.load(f)

            assert nodes_data == []
            assert edges_data == []

    def test_export_to_json_creates_directory(self):
        """Test export_to_json creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "deep" / "directory"
            graph = Graph()

            service = GraphService()
            result = service.export_to_json(graph, output_dir)

            assert result is True
            assert output_dir.exists()
            assert (output_dir / "nodes.json").exists()
            assert (output_dir / "edges.json").exists()

    def test_export_to_json_preserves_attributes(self):
        """Test that export_to_json preserves node and edge attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            graph = Graph()
            node = Node(
                id="test-1",
                type=NodeType.CLASS,
                name="TestClass",
                attributes={"complexity": "high", "lines_of_code": 150}
            )
            graph.add_node(node)

            edge = Edge(
                source="test-1",
                target="test-2",
                type=EdgeType.CALLS,
                attributes={"call_count": 5, "is_recursive": True}
            )
            graph.add_edge(edge)

            service = GraphService()
            service.export_to_json(graph, output_dir)

            with open(output_dir / "nodes.json") as f:
                nodes_data = json.load(f)
            with open(output_dir / "edges.json") as f:
                edges_data = json.load(f)

            assert nodes_data[0]["attributes"]["complexity"] == "high"
            assert nodes_data[0]["attributes"]["lines_of_code"] == 150
            assert edges_data[0]["attributes"]["call_count"] == 5
            assert edges_data[0]["attributes"]["is_recursive"] is True

    def test_export_to_graphml_success(self):
        """Test exporting graph to GraphML format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            graph = Graph()
            node1 = Node(
                id="workspace-1",
                type=NodeType.WORKSPACE,
                name="Test Workspace"
            )
            node2 = Node(
                id="class-1",
                type=NodeType.CLASS,
                name="TestClass"
            )
            graph.add_node(node1)
            graph.add_node(node2)

            edge = Edge(
                source="workspace-1",
                target="class-1",
                type=EdgeType.CONTAINS
            )
            graph.add_edge(edge)

            service = GraphService()
            result = service.export_to_graphml(graph, output_dir)

            assert result is True
            assert (output_dir / "graph.graphml").exists()

            # Verify it's a valid GraphML file
            graphml_content = (output_dir / "graph.graphml").read_text()
            assert "<?xml" in graphml_content
            assert "<graph" in graphml_content
            assert "workspace-1" in graphml_content
            assert "class-1" in graphml_content

    def test_export_to_graphml_empty_graph(self):
        """Test exporting an empty graph to GraphML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            graph = Graph()

            service = GraphService()
            result = service.export_to_graphml(graph, output_dir)

            assert result is True
            assert (output_dir / "graph.graphml").exists()

    def test_export_to_graphml_creates_directory(self):
        """Test export_to_graphml creates output directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "directory"
            graph = Graph()

            service = GraphService()
            result = service.export_to_graphml(graph, output_dir)

            assert result is True
            assert output_dir.exists()
            assert (output_dir / "graph.graphml").exists()

    def test_export_to_graphml_with_attributes(self):
        """Test exporting graph with node/edge attributes to GraphML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            graph = Graph()
            node1 = Node(
                id="class-1",
                type=NodeType.CLASS,
                name="ServiceClass",
                language="java",
                attributes={"public_methods": 5}
            )
            node2 = Node(
                id="class-2",
                type=NodeType.CLASS,
                name="ControllerClass",
                language="java"
            )
            graph.add_node(node1)
            graph.add_node(node2)

            edge = Edge(
                source="class-1",
                target="class-2",
                type=EdgeType.CALLS,
                confidence=0.9
            )
            graph.add_edge(edge)

            service = GraphService()
            service.export_to_graphml(graph, output_dir)

            graphml_content = (output_dir / "graph.graphml").read_text()
            assert "ServiceClass" in graphml_content
            assert "ControllerClass" in graphml_content

    def test_get_node_statistics(self):
        """Test calculating node statistics from graph."""
        graph = Graph()

        # Add nodes of different types
        graph.add_node(Node(id="workspace-1", type=NodeType.WORKSPACE, name="WS"))
        graph.add_node(Node(id="workspace-2", type=NodeType.WORKSPACE, name="WS2"))
        graph.add_node(Node(id="class-1", type=NodeType.CLASS, name="C1"))
        graph.add_node(Node(id="class-2", type=NodeType.CLASS, name="C2"))
        graph.add_node(Node(id="class-3", type=NodeType.CLASS, name="C3"))
        graph.add_node(Node(id="method-1", type=NodeType.METHOD, name="M1"))

        # Add edges of different types
        graph.add_edge(Edge(source="workspace-1", target="class-1", type=EdgeType.CONTAINS))
        graph.add_edge(Edge(source="workspace-1", target="class-2", type=EdgeType.CONTAINS))
        graph.add_edge(Edge(source="class-1", target="method-1", type=EdgeType.CONTAINS))
        graph.add_edge(Edge(source="class-1", target="class-2", type=EdgeType.CALLS))
        graph.add_edge(Edge(source="class-2", target="class-3", type=EdgeType.CALLS))

        service = GraphService()
        stats = service.get_node_statistics(graph)

        assert stats["total_nodes"] == 6
        assert stats["total_edges"] == 5
        assert stats["node_types"]["WORKSPACE"] == 2
        assert stats["node_types"]["CLASS"] == 3
        assert stats["node_types"]["METHOD"] == 1
        assert stats["edge_types"]["CONTAINS"] == 3
        assert stats["edge_types"]["CALLS"] == 2

    def test_get_node_statistics_empty_graph(self):
        """Test statistics for an empty graph."""
        graph = Graph()
        service = GraphService()
        stats = service.get_node_statistics(graph)

        assert stats["total_nodes"] == 0
        assert stats["total_edges"] == 0
        assert stats["node_types"] == {}
        assert stats["edge_types"] == {}

    def test_get_node_statistics_nodes_only(self):
        """Test statistics for a graph with only nodes (no edges)."""
        graph = Graph()
        graph.add_node(Node(id="n1", type=NodeType.CLASS, name="C1"))
        graph.add_node(Node(id="n2", type=NodeType.CLASS, name="C2"))

        service = GraphService()
        stats = service.get_node_statistics(graph)

        assert stats["total_nodes"] == 2
        assert stats["total_edges"] == 0
        assert stats["node_types"]["CLASS"] == 2
        assert stats["edge_types"] == {}

    def test_export_to_json_handles_write_error(self):
        """Test export_to_json handles write errors gracefully."""
        graph = Graph()
        graph.add_node(Node(id="n1", type=NodeType.CLASS, name="C1"))

        service = GraphService()

        # Mock Path to raise an exception on mkdir
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("No permission")):
            result = service.export_to_json(graph, Path("/invalid/path"))
            assert result is False

    def test_export_to_graphml_handles_write_error(self):
        """Test export_to_graphml handles write errors gracefully."""
        graph = Graph()
        graph.add_node(Node(id="n1", type=NodeType.CLASS, name="C1"))

        service = GraphService()

        # Use an invalid path
        with patch('networkx.write_graphml', side_effect=OSError("Write failed")):
            result = service.export_to_graphml(graph, Path("/invalid/path"))
            assert result is False

    def test_export_json_special_characters_in_attributes(self):
        """Test export handles special characters in attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            graph = Graph()
            node = Node(
                id="node-1",
                type=NodeType.CLASS,
                name="TestClass",
                attributes={
                    "description": 'Test with "quotes" and \\ backslash',
                    "unicode": "emoji 🎉"
                }
            )
            graph.add_node(node)

            service = GraphService()
            result = service.export_to_json(graph, output_dir)

            assert result is True
            with open(output_dir / "nodes.json") as f:
                nodes_data = json.load(f)

            assert nodes_data[0]["attributes"]["description"] == 'Test with "quotes" and \\ backslash'
            assert "🎉" in nodes_data[0]["attributes"]["unicode"]

    def test_export_to_json_multiple_calls_overwrites(self):
        """Test that multiple export calls overwrite previous files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            # First export
            graph1 = Graph()
            graph1.add_node(Node(id="n1", type=NodeType.CLASS, name="C1"))

            service = GraphService()
            service.export_to_json(graph1, output_dir)

            with open(output_dir / "nodes.json") as f:
                first_data = json.load(f)
            assert len(first_data) == 1

            # Second export with different data
            graph2 = Graph()
            graph2.add_node(Node(id="n1", type=NodeType.CLASS, name="C1"))
            graph2.add_node(Node(id="n2", type=NodeType.CLASS, name="C2"))

            service.export_to_json(graph2, output_dir)

            with open(output_dir / "nodes.json") as f:
                second_data = json.load(f)
            assert len(second_data) == 2

    def test_export_to_graphml_directed_graph(self):
        """Test that GraphML export creates a directed graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            graph = Graph()
            graph.add_node(Node(id="a", type=NodeType.CLASS, name="A"))
            graph.add_node(Node(id="b", type=NodeType.CLASS, name="B"))
            graph.add_edge(Edge(source="a", target="b", type=EdgeType.CALLS))

            service = GraphService()
            service.export_to_graphml(graph, output_dir)

            graphml_content = (output_dir / "graph.graphml").read_text()
            # Check for directed graph declaration
            assert 'edgedefault="directed"' in graphml_content or '<graph' in graphml_content

    def test_get_statistics_all_node_types(self):
        """Test statistics includes all node types present in graph."""
        graph = Graph()

        # Add one node of each type
        for node_type in [NodeType.WORKSPACE, NodeType.REPOSITORY, NodeType.CLASS,
                          NodeType.METHOD, NodeType.INTERFACE]:
            graph.add_node(Node(id=f"n-{node_type.value}", type=node_type, name=node_type.value))

        service = GraphService()
        stats = service.get_node_statistics(graph)

        assert len(stats["node_types"]) == 5
        for node_type in [NodeType.WORKSPACE, NodeType.REPOSITORY, NodeType.CLASS,
                          NodeType.METHOD, NodeType.INTERFACE]:
            assert stats["node_types"][node_type.value] == 1
