"""Graph Writer Agent: Export graph to multiple formats for downstream tools."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Graph,
)


class GraphWriter(BaseAgent):
    """Export graph to multiple formats for Neo4j, visualization, and analysis tools.

    Responsibilities:
    - Export graph to nodes.json (all nodes with attributes)
    - Export graph to edges.json (all edges with metadata)
    - Export graph to GraphML format for Neo4j/Gephi import
    - Generate graph statistics and summary
    - Output to .context/generated/graph/

    The graph exports enable:
    - Neo4j database import for querying relationships
    - Cytoscape/Gephi visualization and analysis
    - Machine learning on graph structure
    - Knowledge graph construction
    - Relationship analysis at scale

    Attributes:
        logger: Logger instance for graph export
    """

    def __init__(self):
        """Initialize the GraphWriter."""
        super().__init__(name="GraphWriter")

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Export graph to multiple formats.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            AgentOutput with list of exported files.
        """
        if not self.validate_context(context):
            return AgentOutput(
                status="error",
                message="Invalid execution context",
                errors=["ExecutionContext is None"],
            )

        try:
            # Create output directory
            output_dir = self._create_output_dir(context)

            # Export in multiple formats
            artifacts = []

            # Export nodes.json
            nodes_path = self._export_nodes(context, output_dir)
            artifacts.append(nodes_path)

            # Export edges.json
            edges_path = self._export_edges(context, output_dir)
            artifacts.append(edges_path)

            # Export GraphML for Neo4j
            graphml_path = self._export_graphml(context, output_dir)
            artifacts.append(graphml_path)

            # Export graph summary
            summary_path = self._export_summary(context, output_dir)
            artifacts.append(summary_path)

            metrics = {
                "files_exported": len(artifacts),
                "total_nodes": len(context.graph.nodes),
                "total_edges": len(context.graph.edges),
            }

            return AgentOutput(
                status="success",
                message=f"Exported graph in {len(artifacts)} formats",
                artifacts=artifacts,
                metrics=metrics,
            )

        except Exception as e:
            self.logger.error(f"Graph export failed: {str(e)}")
            return AgentOutput(
                status="error",
                message="Graph export failed",
                errors=[str(e)],
            )

    def _create_output_dir(self, context: ExecutionContext) -> Path:
        """Create output directory for graph files.

        Args:
            context: ExecutionContext with workspace config.

        Returns:
            Path to output directory.
        """
        if context.workspace_config and context.workspace_config.context_root:
            output_dir = Path(context.workspace_config.context_root) / "generated" / "graph"
        else:
            output_dir = Path(".context/generated/graph")

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _export_nodes(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export all nodes to nodes.json.

        Args:
            context: ExecutionContext with graph.
            output_dir: Output directory path.

        Returns:
            Path to nodes.json file.
        """
        nodes_data = {
            "total_count": len(context.graph.nodes),
            "nodes": [node.to_dict() for node in context.graph.nodes],
        }

        file_path = output_dir / "nodes.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(nodes_data, f, indent=2)

        self.logger.info(f"Exported {len(context.graph.nodes)} nodes to nodes.json")
        return file_path

    def _export_edges(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export all edges to edges.json.

        Args:
            context: ExecutionContext with graph.
            output_dir: Output directory path.

        Returns:
            Path to edges.json file.
        """
        edges_data = {
            "total_count": len(context.graph.edges),
            "edges": [edge.to_dict() for edge in context.graph.edges],
        }

        file_path = output_dir / "edges.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(edges_data, f, indent=2)

        self.logger.info(f"Exported {len(context.graph.edges)} edges to edges.json")
        return file_path

    def _export_graphml(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export graph to GraphML format for Neo4j/Gephi import.

        Args:
            context: ExecutionContext with graph.
            output_dir: Output directory path.

        Returns:
            Path to graph.graphml file.
        """
        graphml_content = self._generate_graphml(context.graph)

        file_path = output_dir / "graph.graphml"
        file_path.write_text(graphml_content, encoding="utf-8")

        self.logger.info("Exported graph to GraphML format")
        return file_path

    def _generate_graphml(self, graph: Graph) -> str:
        """Generate GraphML XML content.

        Args:
            graph: Graph to export.

        Returns:
            GraphML XML string.
        """
        graphml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="type" for="node" attr.name="type" attr.type="string"/>
  <key id="name" for="node" attr.name="name" attr.type="string"/>
  <key id="language" for="node" attr.name="language" attr.type="string"/>
  <key id="path" for="node" attr.name="path" attr.type="string"/>
  <key id="framework_role" for="node" attr.name="framework_role" attr.type="string"/>
  <key id="edge_type" for="edge" attr.name="type" attr.type="string"/>
  <key id="confidence" for="edge" attr.name="confidence" attr.type="double"/>

  <graph id="G" edgedefault="directed">
"""

        # Add nodes
        for node in graph.nodes:
            graphml += f'    <node id="{node.id}">\n'
            graphml += f'      <data key="type">{self._escape_xml(node.type.value)}</data>\n'
            graphml += f'      <data key="name">{self._escape_xml(node.name)}</data>\n'
            if node.language:
                graphml += f'      <data key="language">{self._escape_xml(node.language)}</data>\n'
            if node.path:
                graphml += f'      <data key="path">{self._escape_xml(node.path)}</data>\n'
            if node.framework_role:
                graphml += f'      <data key="framework_role">{self._escape_xml(node.framework_role)}</data>\n'
            graphml += '    </node>\n'

        # Add edges
        for i, edge in enumerate(graph.edges):
            graphml += f'    <edge id="e{i}" source="{edge.source}" target="{edge.target}">\n'
            graphml += f'      <data key="edge_type">{self._escape_xml(edge.type.value)}</data>\n'
            if edge.confidence is not None:
                graphml += f'      <data key="confidence">{edge.confidence}</data>\n'
            graphml += '    </edge>\n'

        graphml += """  </graph>
</graphml>"""

        return graphml

    def _export_summary(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export graph summary statistics to JSON.

        Args:
            context: ExecutionContext with graph.
            output_dir: Output directory path.

        Returns:
            Path to summary.json file.
        """
        summary = self._calculate_summary(context.graph)

        file_path = output_dir / "summary.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        self.logger.info("Exported graph summary statistics")
        return file_path

    def _calculate_summary(self, graph: Graph) -> Dict[str, Any]:
        """Calculate graph summary statistics.

        Args:
            graph: Graph to analyze.

        Returns:
            Dictionary with summary statistics.
        """
        # Count nodes by type
        node_counts: Dict[str, int] = {}
        for node in graph.nodes:
            node_type = node.type.value
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        # Count edges by type
        edge_counts: Dict[str, int] = {}
        for edge in graph.edges:
            edge_type = edge.type.value
            edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

        # Calculate degree distribution
        in_degree: Dict[str, int] = {}
        out_degree: Dict[str, int] = {}

        for node in graph.nodes:
            in_degree[node.id] = 0
            out_degree[node.id] = 0

        for edge in graph.edges:
            out_degree[edge.source] = out_degree.get(edge.source, 0) + 1
            in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

        max_in_degree = max(in_degree.values()) if in_degree else 0
        max_out_degree = max(out_degree.values()) if out_degree else 0
        avg_degree = (2 * len(graph.edges) / len(graph.nodes)) if graph.nodes else 0

        # Find nodes with highest degree
        degree_map = {
            nid: in_degree.get(nid, 0) + out_degree.get(nid, 0)
            for nid in out_degree.keys()
        }
        top_nodes = sorted(degree_map.items(), key=lambda x: x[1], reverse=True)[:10]
        top_node_names = [
            {
                "id": nid,
                "name": (graph.find_node(nid).name if graph.find_node(nid) else nid),
                "degree": degree,
            }
            for nid, degree in top_nodes
        ]

        # Calculate graph density
        n = len(graph.nodes)
        max_edges = n * (n - 1) if n > 1 else 1
        density = len(graph.edges) / max_edges if max_edges > 0 else 0

        return {
            "nodes": {
                "total": len(graph.nodes),
                "by_type": node_counts,
            },
            "edges": {
                "total": len(graph.edges),
                "by_type": edge_counts,
            },
            "degree_statistics": {
                "average": avg_degree,
                "max_in_degree": max_in_degree,
                "max_out_degree": max_out_degree,
            },
            "top_nodes_by_degree": top_node_names,
            "graph_metrics": {
                "density": density,
                "avg_edges_per_node": avg_degree,
                "is_directed": True,
            },
        }

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters.

        Args:
            text: Text to escape.

        Returns:
            Escaped text.
        """
        if not text:
            return ""
        text = str(text)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        return text
