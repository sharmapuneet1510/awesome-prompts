"""Flow Analysis Agent: Trace API->DB->middleware flows and identify behavior patterns."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

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


class FlowAnalysisAgent(BaseAgent):
    """Trace and analyze execution flows through the system.

    Responsibilities:
    - Identify API endpoints as flow entry points
    - Trace flows from endpoints through services to DB/middleware
    - Detect retry, rollback, timeout, and error handling behavior
    - Generate flow diagrams as Mermaid syntax
    - Export flow-analysis.md, exception-flow.md, and flow-*.mmd files

    The flow analysis provides insights into system behavior under normal and
    exceptional conditions, supporting production debugging and optimization.

    Attributes:
        logger: Logger instance for flow analysis operations
    """

    def __init__(self):
        """Initialize the FlowAnalysisAgent."""
        super().__init__(name="FlowAnalysisAgent")
        self.flows: List[Dict[str, Any]] = []
        self.exception_flows: List[Dict[str, Any]] = []
        self.retry_patterns: Dict[str, Any] = {}
        self.timeout_patterns: Dict[str, Any] = {}

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Analyze execution flows in the codebase.

        Args:
            context: ExecutionContext containing the graph and reports.

        Returns:
            AgentOutput with flow analysis results and artifacts.
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

        try:
            # Identify flow entry points (endpoints)
            endpoints = self._find_endpoints(context)
            self.logger.info(f"Found {len(endpoints)} endpoint(s)")

            # Trace flows from each endpoint
            flow_count = 0
            for endpoint in endpoints:
                flows = self._trace_flows_from_endpoint(endpoint, context)
                self.flows.extend(flows)
                flow_count += len(flows)

            # Analyze exception handling flows
            exception_flow_count = self._analyze_exception_flows(context)

            # Detect retry patterns
            retry_count = self._detect_retry_patterns(context)

            # Detect timeout patterns
            timeout_count = self._detect_timeout_patterns(context)

            # Generate flow diagrams
            artifacts = self._generate_artifacts(context)

            # Create reports
            self._create_reports(context, flow_count, exception_flow_count)

            metrics = {
                "endpoints_found": len(endpoints),
                "flows_traced": flow_count,
                "exception_flows": exception_flow_count,
                "retry_patterns": retry_count,
                "timeout_patterns": timeout_count,
                "diagrams_generated": len(artifacts),
            }

            return AgentOutput(
                status="success",
                message=f"Analyzed {flow_count} flows from {len(endpoints)} endpoints",
                artifacts=artifacts,
                metrics=metrics,
            )

        except Exception as e:
            self.logger.error(f"Flow analysis failed: {str(e)}")
            return AgentOutput(
                status="error",
                message="Flow analysis failed",
                errors=[str(e)],
            )

    def _find_endpoints(self, context: ExecutionContext) -> List[Node]:
        """Find all API endpoints in the graph.

        Args:
            context: ExecutionContext with graph.

        Returns:
            List of endpoint nodes.
        """
        endpoints = []
        for node in context.graph.nodes:
            if node.type == NodeType.ENDPOINT:
                endpoints.append(node)
        return endpoints

    def _trace_flows_from_endpoint(
        self, endpoint: Node, context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """Trace the flow path from an endpoint.

        Args:
            endpoint: Starting endpoint node.
            context: ExecutionContext with graph.

        Returns:
            List of flow objects describing the paths.
        """
        flows = []
        visited: Set[str] = set()

        # Use BFS to trace paths from endpoint
        queue = [(endpoint.id, [endpoint.id])]
        path_count = 0

        while queue and path_count < 10:  # Limit paths per endpoint
            current_id, path = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            current_node = context.graph.find_node(current_id)
            if not current_node:
                continue

            # Find outgoing edges
            outgoing = [
                e for e in context.graph.edges
                if e.source == current_id
            ]

            if not outgoing or len(path) > 10:  # Limit path depth
                # Reached a leaf or depth limit - this is a complete flow
                flow = {
                    "id": f"flow_{path_count}",
                    "entry_point": endpoint.name,
                    "path": path,
                    "length": len(path),
                    "endpoints": [context.graph.find_node(n).name for n in path],
                }
                flows.append(flow)
                path_count += 1
            else:
                # Continue tracing
                for edge in outgoing:
                    if edge.target not in visited:
                        queue.append((edge.target, path + [edge.target]))

        return flows

    def _analyze_exception_flows(self, context: ExecutionContext) -> int:
        """Analyze exception handling flows.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Count of exception flows found.
        """
        exception_flows = 0

        # Find exception nodes
        exception_nodes = [
            n for n in context.graph.nodes
            if n.type == NodeType.EXCEPTION
        ]

        # Find edges that handle exceptions
        for exception_node in exception_nodes:
            handling_edges = [
                e for e in context.graph.edges
                if e.target == exception_node.id and e.type == EdgeType.HANDLES
            ]

            for edge in handling_edges:
                handler_node = context.graph.find_node(edge.source)
                if handler_node:
                    flow = {
                        "exception": exception_node.name,
                        "handler": handler_node.name,
                        "handler_type": handler_node.type.value,
                    }
                    self.exception_flows.append(flow)
                    exception_flows += 1

        return exception_flows

    def _detect_retry_patterns(self, context: ExecutionContext) -> int:
        """Detect retry/resilience patterns in code.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Count of retry patterns found.
        """
        retry_count = 0

        # Look for methods/services with retry-related attributes
        for node in context.graph.nodes:
            if node.type in [NodeType.METHOD, NodeType.CLASS]:
                if node.attributes:
                    attributes_str = str(node.attributes).lower()
                    if any(
                        keyword in attributes_str
                        for keyword in ["retry", "resilient", "backoff", "circuit"]
                    ):
                        self.retry_patterns[node.id] = {
                            "name": node.name,
                            "type": node.type.value,
                            "confidence": 0.75,
                        }
                        retry_count += 1

        return retry_count

    def _detect_timeout_patterns(self, context: ExecutionContext) -> int:
        """Detect timeout patterns in code.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Count of timeout patterns found.
        """
        timeout_count = 0

        # Look for timeout-related attributes
        for node in context.graph.nodes:
            if node.type in [NodeType.METHOD, NodeType.CLASS]:
                if node.attributes:
                    attributes_str = str(node.attributes).lower()
                    if any(
                        keyword in attributes_str
                        for keyword in ["timeout", "deadline", "ttl", "duration"]
                    ):
                        self.timeout_patterns[node.id] = {
                            "name": node.name,
                            "type": node.type.value,
                            "confidence": 0.75,
                        }
                        timeout_count += 1

        return timeout_count

    def _generate_artifacts(self, context: ExecutionContext) -> List[Path]:
        """Generate flow diagram artifacts.

        Args:
            context: ExecutionContext with graph.

        Returns:
            List of artifact file paths.
        """
        artifacts = []

        # Generate main flow diagram
        flow_mermaid = self._generate_flow_mermaid()
        if context.workspace_config and context.workspace_config.context_root:
            flow_path = context.workspace_config.context_root / "flow-diagram.mmd"
            flow_path.write_text(flow_mermaid)
            artifacts.append(flow_path)
            context.generated_files.append(flow_path)

        # Generate exception flow diagram
        exception_mermaid = self._generate_exception_flow_mermaid()
        if context.workspace_config and context.workspace_config.context_root:
            exception_path = (
                context.workspace_config.context_root / "exception-flow.mmd"
            )
            exception_path.write_text(exception_mermaid)
            artifacts.append(exception_path)
            context.generated_files.append(exception_path)

        return artifacts

    def _generate_flow_mermaid(self) -> str:
        """Generate Mermaid diagram for flows.

        Returns:
            Mermaid syntax string for flow diagram.
        """
        lines = ["graph TD"]

        # Add flow nodes
        for i, flow in enumerate(self.flows):
            if i >= 5:  # Limit to first 5 flows in diagram
                break
            endpoints = flow["endpoints"]
            flow_label = " -> ".join(
                [e.replace(" ", "\n") for e in endpoints[:5]]
            )
            lines.append(f'    F{i}["{flow_label}"]')

        # Add edges between flows if they share nodes
        for i in range(len(self.flows) - 1):
            if i < 4:  # Limit connections
                lines.append(f"    F{i} --> F{i+1}")

        return "\n".join(lines)

    def _generate_exception_flow_mermaid(self) -> str:
        """Generate Mermaid diagram for exception flows.

        Returns:
            Mermaid syntax string for exception flow diagram.
        """
        lines = ["graph TD"]

        # Add exception flow nodes
        for i, exc_flow in enumerate(self.exception_flows):
            exception = exc_flow["exception"].replace(" ", "_")
            handler = exc_flow["handler"].replace(" ", "_")
            lines.append(f'    {exception}["{exc_flow["exception"]}"]')
            lines.append(f'    {handler}["{exc_flow["handler"]}"]')
            lines.append(f"    {exception} -->|handled by| {handler}")

        if not lines:
            lines.append('    A["No exception flows detected"]')

        return "\n".join(lines)

    def _create_reports(
        self,
        context: ExecutionContext,
        flow_count: int,
        exception_flow_count: int,
    ) -> None:
        """Create flow analysis reports.

        Args:
            context: ExecutionContext to add reports to.
            flow_count: Number of flows traced.
            exception_flow_count: Number of exception flows found.
        """
        # Create flow analysis report
        flow_report_content = self._generate_flow_report(flow_count)
        context.reports["flow_analysis_report"] = Report(
            name="flow-analysis",
            content=flow_report_content,
            metrics={
                "flows_traced": flow_count,
                "flows_with_retry": len(self.retry_patterns),
                "flows_with_timeout": len(self.timeout_patterns),
            },
        )

        # Create exception flow report
        exception_report_content = self._generate_exception_report(
            exception_flow_count
        )
        context.reports["exception_flow_report"] = Report(
            name="exception-flow",
            content=exception_report_content,
            metrics={
                "exception_flows": exception_flow_count,
            },
        )

    def _generate_flow_report(self, flow_count: int) -> str:
        """Generate flow analysis report content.

        Args:
            flow_count: Number of flows traced.

        Returns:
            Markdown report content.
        """
        report = f"""# Flow Analysis Report

## Summary
- **Flows Traced**: {flow_count}
- **Retry Patterns**: {len(self.retry_patterns)}
- **Timeout Patterns**: {len(self.timeout_patterns)}

## Flow Paths

"""
        for flow in self.flows[:5]:
            report += f"### Flow {flow['id']}\n"
            report += f"- **Entry**: {flow['entry_point']}\n"
            report += f"- **Length**: {flow['length']} hops\n"
            report += f"- **Path**: {' → '.join(flow['endpoints'][:5])}\n\n"

        if self.retry_patterns:
            report += "## Retry Patterns\n\n"
            for node_id, pattern in self.retry_patterns.items():
                report += (
                    f"- {pattern['name']} ({pattern['type']}) - "
                    f"confidence: {pattern['confidence']}\n"
                )

        if self.timeout_patterns:
            report += "\n## Timeout Patterns\n\n"
            for node_id, pattern in self.timeout_patterns.items():
                report += (
                    f"- {pattern['name']} ({pattern['type']}) - "
                    f"confidence: {pattern['confidence']}\n"
                )

        return report

    def _generate_exception_report(self, exception_flow_count: int) -> str:
        """Generate exception flow report content.

        Args:
            exception_flow_count: Number of exception flows found.

        Returns:
            Markdown report content.
        """
        report = f"""# Exception Flow Report

## Summary
- **Exception Flows**: {exception_flow_count}

## Exception Handlers

"""
        for exc_flow in self.exception_flows:
            report += f"### {exc_flow['exception']}\n"
            report += f"- **Handler**: {exc_flow['handler']}\n"
            report += f"- **Handler Type**: {exc_flow['handler_type']}\n\n"

        return report
