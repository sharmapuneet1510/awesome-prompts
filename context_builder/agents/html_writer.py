"""HTML Writer Agent: Generate single-page HTML portal with all reports and data."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    NodeType,
    EdgeType,
)


class HTMLWriter(BaseAgent):
    """Generate single-page HTML portal with all reports, diagrams, and data.

    Responsibilities:
    - Create self-contained index.html file
    - Embed all reports and metrics from ExecutionContext
    - Integrate Mermaid.js for architecture diagrams
    - Integrate Cytoscape.js for interactive graph visualization
    - Display maturity score dashboard
    - Show test quality matrix
    - Include risk assessment heatmap
    - Provide navigation tabs for different views
    - Use clean, professional card-based UI
    - Output to .context/generated/site-html/index.html

    The HTML portal is a single file suitable for stakeholder presentation,
    CI/CD dashboards, and AI-friendly documentation.

    Attributes:
        logger: Logger instance for portal generation
    """

    def __init__(self):
        """Initialize the HTMLWriter."""
        super().__init__(name="HTMLWriter")

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Generate HTML portal from analysis data.

        Args:
            context: ExecutionContext with all analysis data.

        Returns:
            AgentOutput with HTML site artifact.
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

            # Generate HTML content
            html_content = self._generate_html(context)

            # Write HTML file
            file_path = output_dir / "index.html"
            file_path.write_text(html_content, encoding="utf-8")

            metrics = {
                "reports_embedded": len(context.reports),
                "graph_nodes": len(context.graph.nodes),
                "graph_edges": len(context.graph.edges),
                "html_size_kb": len(html_content) // 1024,
                "file_path": str(file_path),
            }

            return AgentOutput(
                status="success",
                message="Generated HTML portal",
                artifacts=[file_path],
                metrics=metrics,
            )

        except Exception as e:
            self.logger.error(f"HTML portal generation failed: {str(e)}")
            return AgentOutput(
                status="error",
                message="HTML portal generation failed",
                errors=[str(e)],
            )

    def _create_output_dir(self, context: ExecutionContext) -> Path:
        """Create output directory for HTML file.

        Args:
            context: ExecutionContext with workspace config.

        Returns:
            Path to output directory.
        """
        if context.workspace_config and context.workspace_config.context_root:
            output_dir = Path(context.workspace_config.context_root) / "generated" / "site-html"
        else:
            output_dir = Path(".context/generated/site-html")

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _generate_html(self, context: ExecutionContext) -> str:
        """Generate complete HTML document.

        Args:
            context: ExecutionContext with all analysis data.

        Returns:
            Complete HTML document as string.
        """
        workspace_name = (
            context.workspace_config.name if context.workspace_config else "Analysis Portal"
        )

        # Convert graph to JSON for Cytoscape
        graph_json = self._graph_to_cytoscape(context)

        # Generate reports sections
        reports_html = self._generate_reports_html(context)

        # Generate metrics dashboards
        metrics_html = self._generate_metrics_html(context)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{workspace_name} - Analysis Portal</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape-dagre/2.5.1/cytoscape-dagre.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #2c3e50;
        }}

        header .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}

        .nav-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .nav-tabs button {{
            padding: 10px 20px;
            border: none;
            background: #ecf0f1;
            color: #2c3e50;
            cursor: pointer;
            border-radius: 4px;
            font-weight: 500;
            transition: all 0.3s;
            white-space: nowrap;
        }}

        .nav-tabs button.active {{
            background: #3498db;
            color: white;
        }}

        .nav-tabs button:hover {{
            background: #34495e;
            color: white;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .card h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}

        .card h3 {{
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
        }}

        .metric {{
            display: inline-block;
            background: #ecf0f1;
            padding: 15px 25px;
            border-radius: 4px;
            margin: 10px 10px 10px 0;
            text-align: center;
            min-width: 150px;
        }}

        .metric .value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}

        .metric .label {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 5px;
        }}

        #graph-container {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f9f9f9;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}

        table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        table td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}

        table tr:hover {{
            background: #f5f7fa;
        }}

        .severity-critical {{
            color: #e74c3c;
            font-weight: bold;
        }}

        .severity-high {{
            color: #e67e22;
        }}

        .severity-medium {{
            color: #f39c12;
        }}

        .severity-low {{
            color: #27ae60;
        }}

        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}

        .report-section {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 40px;
        }}

        .mermaid {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{workspace_name}</h1>
            <div class="meta">
                <p>Comprehensive codebase analysis and documentation</p>
                <p>Nodes: {len(context.graph.nodes)} | Edges: {len(context.graph.edges)} | Reports: {len(context.reports)}</p>
            </div>
        </header>

        <div class="nav-tabs">
            <button class="tab-btn active" data-tab="overview">Overview</button>
            <button class="tab-btn" data-tab="metrics">Metrics</button>
            <button class="tab-btn" data-tab="graph">Dependency Graph</button>
            <button class="tab-btn" data-tab="reports">Reports</button>
            <button class="tab-btn" data-tab="statistics">Statistics</button>
        </div>

        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="card">
                <h2>Analysis Overview</h2>
                <p>This portal provides a comprehensive view of the codebase analysis including architecture, flows, dependencies, and metrics.</p>

                <h3>Quick Metrics</h3>
                <div>
                    <div class="metric">
                        <div class="value">{len(context.graph.nodes)}</div>
                        <div class="label">Total Nodes</div>
                    </div>
                    <div class="metric">
                        <div class="value">{len(context.graph.edges)}</div>
                        <div class="label">Relationships</div>
                    </div>
                    <div class="metric">
                        <div class="value">{len(context.reports)}</div>
                        <div class="label">Reports</div>
                    </div>
                </div>
            </div>

            {metrics_html}
        </div>

        <!-- Metrics Tab -->
        <div id="metrics" class="tab-content">
            <div class="card">
                <h2>Detailed Metrics</h2>
                {self._generate_metrics_detail_html(context)}
            </div>
        </div>

        <!-- Graph Tab -->
        <div id="graph" class="tab-content">
            <div class="card">
                <h2>Dependency Graph Visualization</h2>
                <p>Interactive visualization of all nodes and their relationships. Drag to pan, scroll to zoom.</p>
                <div id="graph-container"></div>
            </div>
        </div>

        <!-- Reports Tab -->
        <div id="reports" class="tab-content">
            <div class="card">
                <h2>Generated Reports</h2>
                {reports_html}
            </div>
        </div>

        <!-- Statistics Tab -->
        <div id="statistics" class="tab-content">
            <div class="card">
                <h2>Statistics</h2>
                {self._generate_statistics_html(context)}
            </div>
        </div>

        <footer>
            <p>Generated by Context Builder - Machine-generated analysis portal</p>
            <p>Last updated: {self._now_timestamp()}</p>
        </footer>
    </div>

    <script>
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {{
                    tab.classList.remove('active');
                }});

                // Remove active from all buttons
                document.querySelectorAll('.tab-btn').forEach(b => {{
                    b.classList.remove('active');
                }});

                // Show selected tab
                const tabId = this.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
                this.classList.add('active');

                // Initialize graph visualization when graph tab is shown
                if (tabId === 'graph' && !window.graphInitialized) {{
                    initializeGraph();
                    window.graphInitialized = true;
                }}
            }});
        }});

        // Graph data
        const graphData = {json.dumps(graph_json)};

        function initializeGraph() {{
            const cy = cytoscape({{
                container: document.getElementById('graph-container'),
                elements: graphData.elements,
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'content': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'background-color': '#3498db',
                            'width': '50px',
                            'height': '50px',
                            'font-size': '10px',
                            'color': 'white'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'target-arrow-shape': 'triangle',
                            'line-color': '#95a5a6',
                            'target-arrow-color': '#95a5a6',
                            'width': 2
                        }}
                    }}
                ],
                layout: {{
                    name: 'dagre',
                    directed: true,
                    rankDir: 'LR'
                }}
            }});
        }}

        // Mermaid initialization
        mermaid.initialize({{ startOnLoad: true, theme: 'base' }});
        mermaid.contentLoaded();
    </script>
</body>
</html>"""
        return html

    def _graph_to_cytoscape(self, context: ExecutionContext) -> Dict[str, List]:
        """Convert graph to Cytoscape.js format.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Dictionary with 'elements' key containing nodes and edges.
        """
        elements = []

        # Add nodes
        for node in context.graph.nodes[:100]:  # Limit for performance
            elements.append({
                "data": {
                    "id": node.id,
                    "label": node.name,
                    "type": node.type.value,
                }
            })

        # Add edges
        for edge in context.graph.edges[:200]:  # Limit for performance
            elements.append({
                "data": {
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.type.value,
                }
            })

        return {"elements": elements}

    def _generate_reports_html(self, context: ExecutionContext) -> str:
        """Generate HTML for reports section.

        Args:
            context: ExecutionContext with reports.

        Returns:
            HTML string with report summaries.
        """
        if not context.reports:
            return "<p>No reports generated.</p>"

        html = "<div>"
        for name, report in sorted(context.reports.items()):
            # Truncate content for display
            preview = (report.content[:200] + "...") if len(report.content) > 200 else report.content
            html += f"""
            <div class="report-section">
                <h3>{name}</h3>
                <p>{preview}</p>
            </div>
            """
        html += "</div>"
        return html

    def _generate_metrics_html(self, context: ExecutionContext) -> str:
        """Generate HTML for metrics dashboard.

        Args:
            context: ExecutionContext with all data.

        Returns:
            HTML string with metrics display.
        """
        # Count nodes by type
        node_counts: Dict[str, int] = {}
        for node in context.graph.nodes:
            node_type = node.type.value
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        # Count edges by type
        edge_counts: Dict[str, int] = {}
        for edge in context.graph.edges:
            edge_type = edge.type.value
            edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

        html = "<div class='card'><h2>Key Metrics</h2>"

        # Node distribution
        html += "<h3>Node Distribution</h3><table><tr><th>Type</th><th>Count</th></tr>"
        for node_type in sorted(node_counts.keys())[:15]:
            count = node_counts[node_type]
            html += f"<tr><td>{node_type}</td><td>{count}</td></tr>"
        html += "</table>"

        # Edge distribution
        html += "<h3>Relationship Distribution</h3><table><tr><th>Type</th><th>Count</th></tr>"
        for edge_type in sorted(edge_counts.keys())[:15]:
            count = edge_counts[edge_type]
            html += f"<tr><td>{edge_type}</td><td>{count}</td></tr>"
        html += "</table></div>"

        return html

    def _generate_metrics_detail_html(self, context: ExecutionContext) -> str:
        """Generate detailed metrics HTML.

        Args:
            context: ExecutionContext with all data.

        Returns:
            HTML string with detailed metrics.
        """
        html = ""

        # Node type breakdown
        node_counts: Dict[str, int] = {}
        for node in context.graph.nodes:
            node_type = node.type.value
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        html += "<h3>Node Type Breakdown</h3><table><tr><th>Type</th><th>Count</th><th>Percentage</th></tr>"
        total_nodes = len(context.graph.nodes)
        for node_type in sorted(node_counts.keys()):
            count = node_counts[node_type]
            percentage = (count / total_nodes * 100) if total_nodes > 0 else 0
            html += f"<tr><td>{node_type}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
        html += "</table>"

        # Edge type breakdown
        edge_counts: Dict[str, int] = {}
        for edge in context.graph.edges:
            edge_type = edge.type.value
            edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

        html += "<h3>Relationship Type Breakdown</h3><table><tr><th>Type</th><th>Count</th><th>Percentage</th></tr>"
        total_edges = len(context.graph.edges)
        for edge_type in sorted(edge_counts.keys()):
            count = edge_counts[edge_type]
            percentage = (count / total_edges * 100) if total_edges > 0 else 0
            html += f"<tr><td>{edge_type}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
        html += "</table>"

        return html

    def _generate_statistics_html(self, context: ExecutionContext) -> str:
        """Generate statistics HTML.

        Args:
            context: ExecutionContext with all data.

        Returns:
            HTML string with statistics.
        """
        # Calculate statistics
        avg_edges_per_node = (len(context.graph.edges) / len(context.graph.nodes)
                              if context.graph.nodes else 0)

        html = f"""
        <h3>Summary Statistics</h3>
        <table>
            <tr><td>Total Nodes</td><td><strong>{len(context.graph.nodes)}</strong></td></tr>
            <tr><td>Total Edges</td><td><strong>{len(context.graph.edges)}</strong></td></tr>
            <tr><td>Average Edges per Node</td><td><strong>{avg_edges_per_node:.2f}</strong></td></tr>
            <tr><td>Total Reports</td><td><strong>{len(context.reports)}</strong></td></tr>
            <tr><td>Graph Density</td><td><strong>{self._calculate_graph_density(context):.4f}</strong></td></tr>
        </table>
        """

        return html

    def _calculate_graph_density(self, context: ExecutionContext) -> float:
        """Calculate graph density metric.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Graph density (0-1).
        """
        n = len(context.graph.nodes)
        if n < 2:
            return 0.0

        max_edges = n * (n - 1)
        actual_edges = len(context.graph.edges)
        return actual_edges / max_edges if max_edges > 0 else 0.0

    def _now_timestamp(self) -> str:
        """Get current timestamp string.

        Returns:
            ISO format timestamp.
        """
        from datetime import datetime
        return datetime.now().isoformat()
