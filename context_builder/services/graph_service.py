"""GraphService: Export and manipulate technical graphs."""

import json
import logging
from pathlib import Path
from typing import Dict, Any

import networkx as nx

from context_builder.models import Graph


class GraphService:
    """Export and manipulate technical graphs to various formats."""

    def __init__(self):
        """Initialize GraphService with logger."""
        self.logger = logging.getLogger(__name__)

    def export_to_json(self, graph: Graph, output_dir: Path) -> bool:
        """
        Export graph to JSON format (nodes.json and edges.json).

        Args:
            graph: Graph object to export
            output_dir: Directory to write JSON files to

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to Path if needed
            output_dir = Path(output_dir)

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            # Export nodes
            nodes_data = [node.to_dict() for node in graph.nodes]
            nodes_file = output_dir / "nodes.json"
            with open(nodes_file, "w") as f:
                json.dump(nodes_data, f, indent=2)

            # Export edges
            edges_data = [edge.to_dict() for edge in graph.edges]
            edges_file = output_dir / "edges.json"
            with open(edges_file, "w") as f:
                json.dump(edges_data, f, indent=2)

            self.logger.info(
                f"Exported graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges to {output_dir}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to export graph to JSON: {e}")
            return False

    def export_to_graphml(self, graph: Graph, output_dir: Path) -> bool:
        """
        Export graph to GraphML format (for Neo4j import).

        Args:
            graph: Graph object to export
            output_dir: Directory to write GraphML file to

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to Path if needed
            output_dir = Path(output_dir)

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create NetworkX directed graph
            G = nx.DiGraph()

            # Add nodes with all attributes (filter out None values and complex types)
            for node in graph.nodes:
                node_data = node.to_dict()
                # Filter out None values and complex types (dicts, lists) for GraphML compatibility
                filtered_data = {
                    k: v
                    for k, v in node_data.items()
                    if v is not None and not isinstance(v, (dict, list))
                }
                G.add_node(node.id, **filtered_data)

            # Add edges with all attributes (filter out None values and complex types)
            for edge in graph.edges:
                edge_data = edge.to_dict()
                # Remove source and target from attributes dict as they're implicit
                edge_data_copy = edge_data.copy()
                source = edge_data_copy.pop("source")
                target = edge_data_copy.pop("target")
                # Filter out None values and complex types for GraphML compatibility
                filtered_data = {
                    k: v
                    for k, v in edge_data_copy.items()
                    if v is not None and not isinstance(v, (dict, list))
                }
                G.add_edge(source, target, **filtered_data)

            # Write to GraphML
            graphml_file = output_dir / "graph.graphml"
            nx.write_graphml(G, str(graphml_file))

            self.logger.info(
                f"Exported GraphML: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges to {graphml_file}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to export graph to GraphML: {e}")
            return False

    def get_node_statistics(self, graph: Graph) -> Dict[str, Any]:
        """
        Calculate graph statistics: node/edge counts by type.

        Args:
            graph: Graph object to analyze

        Returns:
            Dictionary with statistics:
                - total_nodes: Total number of nodes
                - total_edges: Total number of edges
                - node_types: Count of nodes by type
                - edge_types: Count of edges by type
        """
        node_types: Dict[str, int] = {}
        edge_types: Dict[str, int] = {}

        # Count nodes by type
        for node in graph.nodes:
            # Get string value from enum
            node_type_str = node.type.value if hasattr(node.type, "value") else str(node.type)
            node_types[node_type_str] = node_types.get(node_type_str, 0) + 1

        # Count edges by type
        for edge in graph.edges:
            # Get string value from enum
            edge_type_str = edge.type.value if hasattr(edge.type, "value") else str(edge.type)
            edge_types[edge_type_str] = edge_types.get(edge_type_str, 0) + 1

        return {
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "node_types": node_types,
            "edge_types": edge_types,
        }
