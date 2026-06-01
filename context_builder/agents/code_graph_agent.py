"""Code Graph Agent: Build traversable technical graph from extracted symbols."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Node,
    NodeType,
    Edge,
    EdgeType,
    Report,
)
from context_builder.services.graph_service import GraphService


class CodeGraphAgent(BaseAgent):
    """Build a traversable technical graph from extracted symbols.

    Responsibilities:
    - Create nodes from extracted symbols (classes, endpoints, consumers, etc.)
    - Create edges for relationships (calls, implements, publishes, consumes, etc.)
    - Preserve source references in nodes and edges
    - Export nodes.json, edges.json, and graph.graphml

    The graph serves as a queryable representation of the codebase architecture,
    suitable for visualization and further analysis by downstream agents.

    Attributes:
        graph_service: GraphService instance for graph export operations
    """

    def __init__(self):
        """Initialize the CodeGraphAgent."""
        super().__init__(name="CodeGraphAgent")
        self.graph_service = GraphService()

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Build graph from extracted symbols.

        Args:
            context: ExecutionContext containing scan results and graph.

        Returns:
            AgentOutput with graph construction results and export artifacts.
        """
        if not self.validate_context(context):
            return AgentOutput(
                status="error",
                message="Invalid execution context",
                errors=["ExecutionContext is None"],
            )

        if not context.graph:
            return AgentOutput(
                status="error",
                message="Missing graph in context",
                errors=["Graph not initialized"],
            )

        # Check for scan report with extracted symbols
        scan_report = context.reports.get("scan_report")
        if not scan_report or not scan_report.metrics:
            return AgentOutput(
                status="error",
                message="Missing scan results",
                errors=["No scan-report found with symbol metrics"],
            )

        try:
            # Create nodes from extracted symbols
            node_count = self._create_nodes_from_symbols(scan_report.metrics, context)
            self.logger.info(f"Created {node_count} nodes from symbols")

            # Create edges for relationships
            edge_count = self._create_edges_from_relationships(context)
            self.logger.info(f"Created {edge_count} edges for relationships")

            # Get graph statistics
            stats = self.graph_service.get_node_statistics(context.graph)

            # Generate graph report
            report_content = self._generate_graph_report(stats)
            context.reports["graph_report"] = Report(
                name="graph-report",
                content=report_content,
                metrics=stats,
            )

            # Export graph to various formats
            artifacts = self._export_graph(context)

            return AgentOutput(
                status="success",
                message=f"Built graph with {node_count} nodes and {edge_count} edges",
                artifacts=artifacts,
                metrics={
                    "nodes_created": node_count,
                    "edges_created": edge_count,
                    **stats,
                },
            )
        except Exception as e:
            self.logger.error(f"Error in CodeGraphAgent: {e}", exc_info=True)
            return AgentOutput(
                status="error",
                message=str(e),
                errors=[str(e)],
            )

    def _create_nodes_from_symbols(
        self, metrics: Dict[str, Any], context: ExecutionContext
    ) -> int:
        """Create graph nodes from extracted symbols.

        Args:
            metrics: Dictionary of symbol metrics from scan report.
            context: ExecutionContext with the graph to populate.

        Returns:
            Count of nodes created.
        """
        node_count = 0

        # Symbol type to NodeType mapping
        type_mapping = {
            "classes": NodeType.CLASS,
            "endpoints": NodeType.ENDPOINT,
            "consumers": NodeType.CONSUMER,
            "producers": NodeType.PRODUCER,
            "schedulers": NodeType.SCHEDULER,
            "configurations": NodeType.CONFIG_FILE,
            "databases": NodeType.DATABASE,
            "middleware_topics": NodeType.MIDDLEWARE_TOPIC,
            "methods": NodeType.METHOD,
            "external_apis": NodeType.EXTERNAL_API,
        }

        for symbol_type, node_type in type_mapping.items():
            symbols = metrics.get(symbol_type, [])
            if not isinstance(symbols, list):
                continue

            for symbol in symbols:
                if not isinstance(symbol, dict):
                    continue

                symbol_id = symbol.get("id", "")
                symbol_name = symbol.get("name", "unknown")

                if not symbol_id:
                    continue

                # Create node with all available metadata
                node = Node(
                    id=symbol_id,
                    type=node_type,
                    name=symbol_name,
                    repository=symbol.get("repository"),
                    path=symbol.get("file") or symbol.get("path"),
                    language=symbol.get("language"),
                    framework_role=symbol.get("framework_role"),
                    attributes={
                        k: v
                        for k, v in symbol.items()
                        if k not in ["id", "name", "repository", "file", "path", "language", "framework_role"]
                    },
                )

                context.graph.add_node(node)
                node_count += 1

        return node_count

    def _create_edges_from_relationships(self, context: ExecutionContext) -> int:
        """Create edges representing relationships between symbols.

        Args:
            context: ExecutionContext with the graph to populate.

        Returns:
            Count of edges created.
        """
        edge_count = 0

        # Strategy 1: Extract relationships from symbol attributes
        for node in context.graph.nodes:
            # Handle inheritance relationships (extends/implements)
            if "parent_class" in node.attributes and node.attributes["parent_class"]:
                parent_name = node.attributes["parent_class"]
                parent_id = self._find_node_id_by_name(context.graph, parent_name)
                if parent_id:
                    edge = Edge(
                        source=node.id,
                        target=parent_id,
                        type=EdgeType.EXTENDS,
                        confidence=0.95,
                        source_reference=f"Class definition: {node.path}",
                    )
                    context.graph.add_edge(edge)
                    edge_count += 1

            # Handle interface implementations
            if "interfaces" in node.attributes and node.attributes["interfaces"]:
                interfaces = node.attributes["interfaces"]
                if isinstance(interfaces, str):
                    interface_list = [i.strip() for i in interfaces.split(",")]
                else:
                    interface_list = interfaces if isinstance(interfaces, list) else []

                for interface_name in interface_list:
                    interface_id = self._find_node_id_by_name(context.graph, interface_name)
                    if interface_id:
                        edge = Edge(
                            source=node.id,
                            target=interface_id,
                            type=EdgeType.IMPLEMENTS,
                            confidence=0.90,
                            source_reference=f"Interface implementation: {node.path}",
                        )
                        context.graph.add_edge(edge)
                        edge_count += 1

        # Strategy 2: Container relationships (module contains class, class contains method)
        self._create_containment_edges(context)
        edge_count = len(context.graph.edges)

        # Strategy 3: Middleware relationships (producers/consumers to topics)
        edge_count += self._create_middleware_edges(context)

        # Strategy 4: Endpoint relationships
        edge_count += self._create_endpoint_edges(context)

        return edge_count

    def _create_containment_edges(self, context: ExecutionContext) -> None:
        """Create CONTAINS edges for hierarchical relationships.

        Args:
            context: ExecutionContext with the graph to populate.
        """
        # Group nodes by type and location to infer containment
        repositories = {}
        modules = {}

        for node in context.graph.nodes:
            if node.repository:
                if node.repository not in repositories:
                    repositories[node.repository] = []
                repositories[node.repository].append(node)

            if node.module:
                if node.module not in modules:
                    modules[node.module] = []
                modules[node.module].append(node)

        # Create repository->child relationships
        for repo_id, nodes in repositories.items():
            # Create repository node if it doesn't exist
            repo_node_id = f"repo:{repo_id}"
            if not context.graph.find_node(repo_node_id):
                repo_node = Node(
                    id=repo_node_id,
                    type=NodeType.REPOSITORY,
                    name=repo_id,
                    repository=repo_id,
                )
                context.graph.add_node(repo_node)

            # Create containment edges
            for node in nodes:
                if node.type in [NodeType.CLASS, NodeType.CONFIG_FILE, NodeType.DATABASE]:
                    edge = Edge(
                        source=repo_node_id,
                        target=node.id,
                        type=EdgeType.CONTAINS,
                        confidence=1.0,
                        source_reference=f"Repository structure: {repo_id}",
                    )
                    context.graph.add_edge(edge)

    def _create_middleware_edges(self, context: ExecutionContext) -> int:
        """Create edges between producers/consumers and middleware topics.

        Args:
            context: ExecutionContext with the graph to populate.

        Returns:
            Count of edges created.
        """
        edge_count = 0

        # Find all topics
        topics = [n for n in context.graph.nodes if n.type == NodeType.MIDDLEWARE_TOPIC]
        # Find all producers and consumers
        producers = [n for n in context.graph.nodes if n.type == NodeType.PRODUCER]
        consumers = [n for n in context.graph.nodes if n.type == NodeType.CONSUMER]

        # Create producer -> topic edges
        for producer in producers:
            # Find published topic by name similarity or from attributes
            topic_name = producer.attributes.get("topic", "")
            if topic_name:
                matching_topic = next(
                    (t for t in topics if topic_name in t.name),
                    None,
                )
                if matching_topic:
                    edge = Edge(
                        source=producer.id,
                        target=matching_topic.id,
                        type=EdgeType.PUBLISHES_TO,
                        confidence=0.85,
                        source_reference=producer.path,
                    )
                    context.graph.add_edge(edge)
                    edge_count += 1

        # Create consumer -> topic edges
        for consumer in consumers:
            # Find subscribed topic by name similarity or from attributes
            topic_name = consumer.attributes.get("topic", "")
            if topic_name:
                matching_topic = next(
                    (t for t in topics if topic_name in t.name),
                    None,
                )
                if matching_topic:
                    edge = Edge(
                        source=matching_topic.id,
                        target=consumer.id,
                        type=EdgeType.CONSUMES_FROM,
                        confidence=0.85,
                        source_reference=consumer.path,
                    )
                    context.graph.add_edge(edge)
                    edge_count += 1

        return edge_count

    def _create_endpoint_edges(self, context: ExecutionContext) -> int:
        """Create edges from endpoints to their handler classes.

        Args:
            context: ExecutionContext with the graph to populate.

        Returns:
            Count of edges created.
        """
        edge_count = 0

        endpoints = [n for n in context.graph.nodes if n.type == NodeType.ENDPOINT]

        for endpoint in endpoints:
            # Find the class that defines this endpoint
            handler_class = endpoint.attributes.get("class_name", "")
            if handler_class:
                matching_class = next(
                    (n for n in context.graph.nodes
                     if n.type == NodeType.CLASS and handler_class in n.name),
                    None,
                )
                if matching_class:
                    edge = Edge(
                        source=matching_class.id,
                        target=endpoint.id,
                        type=EdgeType.CONTAINS,
                        confidence=0.95,
                        source_reference=f"Endpoint definition: {endpoint.path}",
                    )
                    context.graph.add_edge(edge)
                    edge_count += 1

        return edge_count

    def _find_node_id_by_name(self, graph, name: str) -> Optional[str]:
        """Find a node ID by class/interface name (simple name matching).

        Args:
            graph: Graph to search.
            name: Name to match.

        Returns:
            Node ID if found, None otherwise.
        """
        for node in graph.nodes:
            if node.name == name or node.name.endswith("." + name):
                return node.id
        return None

    def _export_graph(self, context: ExecutionContext) -> List[Path]:
        """Export graph to JSON and GraphML formats.

        Args:
            context: ExecutionContext containing workspace config and graph.

        Returns:
            List of artifact file paths.
        """
        artifacts = []

        # Determine output directory
        if context.workspace_config and context.workspace_config.context_root:
            output_dir = context.workspace_config.context_root / "graph"
        else:
            output_dir = Path.cwd() / "context" / "graph"

        try:
            # Export to JSON
            if self.graph_service.export_to_json(context.graph, output_dir):
                artifacts.append(output_dir / "nodes.json")
                artifacts.append(output_dir / "edges.json")

            # Export to GraphML
            if self.graph_service.export_to_graphml(context.graph, output_dir):
                artifacts.append(output_dir / "graph.graphml")

            self.logger.info(f"Exported graph artifacts to {output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to export graph: {e}")

        return artifacts

    def _generate_graph_report(self, stats: Dict[str, Any]) -> str:
        """Generate a markdown report of graph statistics.

        Args:
            stats: Graph statistics dictionary.

        Returns:
            Markdown-formatted report.
        """
        report = "# Technical Graph Report\n\n"

        report += "## Graph Statistics\n\n"
        report += f"- **Total Nodes**: {stats.get('total_nodes', 0)}\n"
        report += f"- **Total Edges**: {stats.get('total_edges', 0)}\n\n"

        node_types = stats.get("node_types", {})
        if node_types:
            report += "### Node Types Distribution\n\n"
            for node_type, count in sorted(node_types.items()):
                report += f"- {node_type}: {count}\n"
            report += "\n"

        edge_types = stats.get("edge_types", {})
        if edge_types:
            report += "### Edge Types Distribution\n\n"
            for edge_type, count in sorted(edge_types.items()):
                report += f"- {edge_type}: {count}\n"
            report += "\n"

        report += "## Graph Artifacts\n\n"
        report += "- `nodes.json` - All nodes with attributes\n"
        report += "- `edges.json` - All edges with relationships\n"
        report += "- `graph.graphml` - Graph in GraphML format (for Neo4j/visualization)\n"

        return report
