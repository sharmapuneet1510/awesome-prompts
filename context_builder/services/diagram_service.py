"""DiagramService: Generate Mermaid diagrams for architecture and flow visualization."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from context_builder.models import Graph, Node, Edge, NodeType, EdgeType


class DiagramService:
    """Generate Mermaid diagrams from graphs and flow data."""

    def __init__(self):
        """Initialize DiagramService."""
        self.logger = logging.getLogger(__name__)

    def generate_architecture_diagram(
        self, graph: Graph, output_file: Optional[Path] = None
    ) -> str:
        """
        Generate Mermaid graph diagram for architecture.

        Args:
            graph: Technical graph to visualize
            output_file: Optional file to write diagram

        Returns:
            Mermaid diagram as string
        """
        diagram_lines = ["graph TD"]

        # Add nodes
        node_map: Dict[str, str] = {}
        for i, node in enumerate(graph.nodes):
            node_id = f"N{i}"
            node_map[node.id] = node_id
            label = f"{node.name} ({node.type.value})"
            diagram_lines.append(f'    {node_id}["{label}"]')

        # Add edges
        for edge in graph.edges:
            source_id = node_map.get(edge.source)
            target_id = node_map.get(edge.target)
            if source_id and target_id:
                edge_label = edge.type.value.replace("_", " ")
                diagram_lines.append(
                    f'    {source_id} -->|{edge_label}| {target_id}'
                )

        diagram = "\n".join(diagram_lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(diagram)
            self.logger.info(f"Generated architecture diagram at {output_file}")

        return diagram

    def generate_flow_diagram(
        self,
        flow_name: str,
        steps: List[Dict[str, Any]],
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Generate Mermaid sequence or flowchart diagram for a process flow.

        Args:
            flow_name: Name of the flow
            steps: List of step dictionaries with 'name' and optional 'action', 'actor'
            output_file: Optional file to write diagram

        Returns:
            Mermaid diagram as string
        """
        diagram_lines = [f"graph TD", f'    Start["Start: {flow_name}"]']

        prev_node = "Start"
        for i, step in enumerate(steps):
            node_id = f"S{i}"
            step_name = step.get("name", f"Step {i}")
            diagram_lines.append(f'    {node_id}["{step_name}"]')
            diagram_lines.append(f"    {prev_node} --> {node_id}")
            prev_node = node_id

        diagram_lines.append(f'    {prev_node} --> End["End: {flow_name}"]')

        diagram = "\n".join(diagram_lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(diagram)
            self.logger.info(f"Generated flow diagram at {output_file}")

        return diagram

    def generate_dependency_diagram(
        self, dependencies: Dict[str, List[str]], output_file: Optional[Path] = None
    ) -> str:
        """
        Generate Mermaid diagram for dependency graph.

        Args:
            dependencies: Dictionary mapping component to list of dependencies
            output_file: Optional file to write diagram

        Returns:
            Mermaid diagram as string
        """
        diagram_lines = ["graph LR"]

        for component, deps in dependencies.items():
            for dep in deps:
                diagram_lines.append(f'    "{dep}" --> "{component}"')

        diagram = "\n".join(diagram_lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(diagram)
            self.logger.info(f"Generated dependency diagram at {output_file}")

        return diagram

    def generate_class_diagram(
        self, classes: List[Dict[str, Any]], output_file: Optional[Path] = None
    ) -> str:
        """
        Generate Mermaid class diagram.

        Args:
            classes: List of class definitions with 'name', 'methods', 'attributes'
            output_file: Optional file to write diagram

        Returns:
            Mermaid diagram as string
        """
        diagram_lines = ["classDiagram"]

        for cls in classes:
            class_name = cls.get("name", "UnknownClass")
            diagram_lines.append(f"    class {class_name} {{")

            attributes = cls.get("attributes", [])
            for attr in attributes:
                diagram_lines.append(f"        {attr}")

            methods = cls.get("methods", [])
            for method in methods:
                diagram_lines.append(f"        {method}()")

            diagram_lines.append("    }")

        diagram = "\n".join(diagram_lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(diagram)
            self.logger.info(f"Generated class diagram at {output_file}")

        return diagram

    def generate_state_diagram(
        self, states: List[str], transitions: List[Dict[str, str]], output_file: Optional[Path] = None
    ) -> str:
        """
        Generate Mermaid state diagram.

        Args:
            states: List of state names
            transitions: List of transition dicts with 'from', 'to', 'event'
            output_file: Optional file to write diagram

        Returns:
            Mermaid diagram as string
        """
        diagram_lines = ["stateDiagram-v2"]

        for state in states:
            diagram_lines.append(f"    state {state}")

        for transition in transitions:
            from_state = transition.get("from", "")
            to_state = transition.get("to", "")
            event = transition.get("event", "")
            diagram_lines.append(f'    {from_state} --> {to_state}: {event}')

        diagram = "\n".join(diagram_lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(diagram)
            self.logger.info(f"Generated state diagram at {output_file}")

        return diagram
