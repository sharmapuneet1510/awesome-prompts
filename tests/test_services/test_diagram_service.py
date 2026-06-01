"""Tests for DiagramService."""

import pytest
from pathlib import Path
import tempfile

from context_builder.models import Graph, Node, Edge, NodeType, EdgeType
from context_builder.services.diagram_service import DiagramService


class TestDiagramServiceInitialization:
    """Tests for DiagramService initialization."""

    def test_init(self):
        """DiagramService initializes successfully."""
        service = DiagramService()
        assert service is not None
        assert service.logger is not None


class TestGenerateArchitectureDiagram:
    """Tests for generate_architecture_diagram method."""

    def test_generate_architecture_diagram(self):
        """Generate architecture diagram from graph."""
        service = DiagramService()

        graph = Graph()
        node1 = Node(id="class:A", type=NodeType.CLASS, name="ClassA")
        node2 = Node(id="class:B", type=NodeType.CLASS, name="ClassB")
        edge = Edge(source="class:A", target="class:B", type=EdgeType.CALLS)

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(edge)

        diagram = service.generate_architecture_diagram(graph)

        assert "graph TD" in diagram
        assert "ClassA" in diagram
        assert "ClassB" in diagram
        assert "CALLS" in diagram

    def test_generate_architecture_diagram_writes_file(self):
        """Generate architecture diagram can write to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagramService()

            graph = Graph()
            node = Node(id="class:A", type=NodeType.CLASS, name="ClassA")
            graph.add_node(node)

            output_file = Path(tmpdir) / "diagram.md"
            diagram = service.generate_architecture_diagram(graph, output_file)

            assert output_file.exists()
            assert output_file.read_text() == diagram

    def test_generate_architecture_diagram_empty_graph(self):
        """Generate architecture diagram handles empty graph."""
        service = DiagramService()
        graph = Graph()

        diagram = service.generate_architecture_diagram(graph)

        assert "graph TD" in diagram


class TestGenerateFlowDiagram:
    """Tests for generate_flow_diagram method."""

    def test_generate_flow_diagram(self):
        """Generate flow diagram from steps."""
        service = DiagramService()

        steps = [
            {"name": "Initialize", "action": "setup"},
            {"name": "Analyze", "action": "parse"},
            {"name": "Generate", "action": "output"},
        ]

        diagram = service.generate_flow_diagram("Test Flow", steps)

        assert "graph TD" in diagram
        assert "Start: Test Flow" in diagram
        assert "Initialize" in diagram
        assert "Analyze" in diagram
        assert "Generate" in diagram

    def test_generate_flow_diagram_writes_file(self):
        """Generate flow diagram can write to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagramService()

            steps = [{"name": "Step1"}]
            output_file = Path(tmpdir) / "flow.md"

            diagram = service.generate_flow_diagram("Flow", steps, output_file)

            assert output_file.exists()


class TestGenerateDependencyDiagram:
    """Tests for generate_dependency_diagram method."""

    def test_generate_dependency_diagram(self):
        """Generate dependency diagram from dependencies."""
        service = DiagramService()

        dependencies = {
            "ServiceA": ["ServiceB", "ServiceC"],
            "ServiceB": ["Database"],
        }

        diagram = service.generate_dependency_diagram(dependencies)

        assert "graph LR" in diagram
        assert "ServiceA" in diagram
        assert "ServiceB" in diagram
        assert "Database" in diagram


class TestGenerateClassDiagram:
    """Tests for generate_class_diagram method."""

    def test_generate_class_diagram(self):
        """Generate class diagram from class definitions."""
        service = DiagramService()

        classes = [
            {
                "name": "Animal",
                "attributes": ["name: str", "age: int"],
                "methods": ["speak", "move"],
            },
            {
                "name": "Dog",
                "attributes": ["breed: str"],
                "methods": ["bark"],
            },
        ]

        diagram = service.generate_class_diagram(classes)

        assert "classDiagram" in diagram
        assert "class Animal" in diagram
        assert "class Dog" in diagram
        assert "name: str" in diagram

    def test_generate_class_diagram_empty_methods(self):
        """Generate class diagram handles empty methods."""
        service = DiagramService()

        classes = [{"name": "Empty"}]

        diagram = service.generate_class_diagram(classes)

        assert "classDiagram" in diagram
        assert "class Empty" in diagram


class TestGenerateStateDiagram:
    """Tests for generate_state_diagram method."""

    def test_generate_state_diagram(self):
        """Generate state diagram from states and transitions."""
        service = DiagramService()

        states = ["Idle", "Processing", "Done"]
        transitions = [
            {"from": "Idle", "to": "Processing", "event": "start"},
            {"from": "Processing", "to": "Done", "event": "complete"},
        ]

        diagram = service.generate_state_diagram(states, transitions)

        assert "stateDiagram-v2" in diagram
        assert "Idle" in diagram
        assert "Processing" in diagram
        assert "Done" in diagram
        assert "start" in diagram
        assert "complete" in diagram

    def test_generate_state_diagram_writes_file(self):
        """Generate state diagram can write to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagramService()

            states = ["A", "B"]
            transitions = [{"from": "A", "to": "B", "event": "go"}]
            output_file = Path(tmpdir) / "state.md"

            diagram = service.generate_state_diagram(
                states, transitions, output_file
            )

            assert output_file.exists()
