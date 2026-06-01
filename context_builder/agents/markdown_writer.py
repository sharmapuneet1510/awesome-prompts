"""Markdown Writer Agent: Generate comprehensive markdown documentation book."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    NodeType,
    EdgeType,
)


class MarkdownWriter(BaseAgent):
    """Generate comprehensive markdown documentation book from analysis.

    Responsibilities:
    - Generate 15+ markdown files for comprehensive documentation
    - Create index.md with navigation and table of contents
    - Generate architecture.md with design documentation
    - Generate flow-analysis.md with business flow diagrams
    - Generate code-structure.md with class hierarchies
    - Generate test-intelligence.md with test coverage analysis
    - Generate technical-debt.md with issues and recommendations
    - Generate risk-assessment.md with risk analysis
    - Generate endpoints.md with API documentation
    - Generate databases.md with data model documentation
    - Generate middleware.md with messaging and integration details
    - Generate exceptions.md with error handling documentation
    - Generate configuration.md with config properties
    - Generate glossary.md with terminology
    - Optimize for AI/RAG with summaries, details, and source references
    - Output to .context/generated/book-md/

    The markdown book provides searchable, version-controllable documentation
    suitable for CI/CD pipelines, AI training, and stakeholder reference.

    Attributes:
        logger: Logger instance for book generation
    """

    # Standard markdown files to generate
    BOOK_FILES = [
        "index.md",
        "architecture.md",
        "flow-analysis.md",
        "code-structure.md",
        "test-intelligence.md",
        "technical-debt.md",
        "risk-assessment.md",
        "endpoints.md",
        "databases.md",
        "middleware.md",
        "exceptions.md",
        "configuration.md",
        "glossary.md",
        "appendix-nodes.md",
        "appendix-edges.md",
    ]

    def __init__(self):
        """Initialize the MarkdownWriter."""
        super().__init__(name="MarkdownWriter")

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Generate markdown documentation book from analysis context.

        Args:
            context: ExecutionContext with all analysis data.

        Returns:
            AgentOutput with list of generated markdown files.
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

            # Generate all markdown files
            artifacts = []
            for filename in self.BOOK_FILES:
                method_name = f"_generate_{filename[:-3]}"  # Remove .md extension
                if hasattr(self, method_name):
                    file_path = self._generate_markdown_file(
                        context, output_dir, filename, getattr(self, method_name)
                    )
                    artifacts.append(file_path)

            metrics = {
                "files_generated": len(artifacts),
                "total_nodes": len(context.graph.nodes),
                "total_edges": len(context.graph.edges),
                "total_reports": len(context.reports),
            }

            return AgentOutput(
                status="success",
                message=f"Generated markdown book with {len(artifacts)} files",
                artifacts=artifacts,
                metrics=metrics,
            )

        except Exception as e:
            self.logger.error(f"Markdown book generation failed: {str(e)}")
            return AgentOutput(
                status="error",
                message="Markdown book generation failed",
                errors=[str(e)],
            )

    def _create_output_dir(self, context: ExecutionContext) -> Path:
        """Create output directory for markdown files.

        Args:
            context: ExecutionContext with workspace config.

        Returns:
            Path to output directory.
        """
        if context.workspace_config and context.workspace_config.context_root:
            output_dir = Path(context.workspace_config.context_root) / "generated" / "book-md"
        else:
            output_dir = Path(".context/generated/book-md")

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _generate_markdown_file(
        self,
        context: ExecutionContext,
        output_dir: Path,
        filename: str,
        generator_func,
    ) -> Path:
        """Generate a single markdown file.

        Args:
            context: ExecutionContext with all data.
            output_dir: Output directory path.
            filename: Name of file to generate.
            generator_func: Function to generate content.

        Returns:
            Path to generated file.
        """
        content = generator_func(context)
        file_path = output_dir / filename
        file_path.write_text(content, encoding="utf-8")
        self.logger.info(f"Generated {filename}")
        return file_path

    def _generate_index(self, context: ExecutionContext) -> str:
        """Generate index.md with navigation and table of contents.

        Args:
            context: ExecutionContext with all data.

        Returns:
            Markdown content for index.md.
        """
        workspace_name = (
            context.workspace_config.name
            if context.workspace_config
            else "Unknown Workspace"
        )
        workspace_desc = (
            context.workspace_config.description
            if context.workspace_config
            else ""
        )

        return f"""# {workspace_name} - Architecture Documentation

{workspace_desc}

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Business Flows](#business-flows)
3. [Code Structure](#code-structure)
4. [Test Intelligence](#test-intelligence)
5. [Technical Debt](#technical-debt)
6. [Risk Assessment](#risk-assessment)
7. [API Endpoints](#api-endpoints)
8. [Data Models](#data-models)
9. [Middleware & Integration](#middleware--integration)
10. [Exception Handling](#exception-handling)
11. [Configuration](#configuration)
12. [Glossary](#glossary)

## Architecture Overview

See [architecture.md](./architecture.md) for detailed system design and component relationships.

## Business Flows

See [flow-analysis.md](./flow-analysis.md) for business process flows and data movement patterns.

## Code Structure

See [code-structure.md](./code-structure.md) for package hierarchies, classes, and methods.

## Test Intelligence

See [test-intelligence.md](./test-intelligence.md) for test coverage analysis and quality metrics.

## Technical Debt

See [technical-debt.md](./technical-debt.md) for issues, code smells, and remediation recommendations.

## Risk Assessment

See [risk-assessment.md](./risk-assessment.md) for risk analysis and mitigation strategies.

## API Endpoints

See [endpoints.md](./endpoints.md) for REST API documentation and integration points.

## Data Models

See [databases.md](./databases.md) for database schemas and data relationships.

## Middleware & Integration

See [middleware.md](./middleware.md) for messaging systems, event streams, and integration patterns.

## Exception Handling

See [exceptions.md](./exceptions.md) for error types, handling strategies, and recovery patterns.

## Configuration

See [configuration.md](./configuration.md) for application configuration properties and environment setup.

## Glossary

See [glossary.md](./glossary.md) for terminology and domain-specific definitions.

---

**Generated:** {self._now_timestamp()}
**Nodes:** {len(context.graph.nodes)}
**Edges:** {len(context.graph.edges)}
**Reports:** {len(context.reports)}

*This documentation is machine-generated from codebase analysis. For updates, re-run the context builder.*
"""

    def _generate_architecture(self, context: ExecutionContext) -> str:
        """Generate architecture.md with design documentation.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for architecture.md.
        """
        repositories = self._get_repositories(context)
        modules = self._get_nodes_by_type(context, NodeType.MODULE)

        content = "# System Architecture\n\n"
        content += "## Overview\n\n"
        content += "System architecture describing components, layers, and key dependencies.\n\n"

        if repositories:
            content += "## Repositories\n\n"
            for repo in repositories:
                content += f"### {repo.name}\n\n"
                content += f"- **ID:** {repo.id}\n"
                content += f"- **Path:** {repo.path}\n\n"

        if modules:
            content += "## Modules\n\n"
            for module in modules:
                content += f"### {module.name}\n\n"
                if module.path:
                    content += f"- **Path:** {module.path}\n"
                if module.framework_role:
                    content += f"- **Role:** {module.framework_role}\n"
                content += "\n"

        content += "## Component Relationships\n\n"
        content += self._generate_relationship_table(context)

        return content

    def _generate_flow_analysis(self, context: ExecutionContext) -> str:
        """Generate flow-analysis.md with business flows and data movement.

        Args:
            context: ExecutionContext with graph and reports.

        Returns:
            Markdown content for flow-analysis.md.
        """
        flows = self._get_nodes_by_type(context, NodeType.BUSINESS_FLOW)

        content = "# Business Flow Analysis\n\n"
        content += "## Overview\n\n"
        content += "Business process flows, data movement patterns, and sequence diagrams.\n\n"

        if flows:
            content += "## Identified Flows\n\n"
            for flow in flows:
                content += f"### {flow.name}\n\n"
                if flow.path:
                    content += f"- **Source:** {flow.path}\n"

                # Find related nodes
                related = self._get_related_nodes(context, flow.id, EdgeType.PART_OF_FLOW)
                if related:
                    content += "- **Components:**\n"
                    for node in related:
                        content += f"  - {node.name} ({node.type.value})\n"
                content += "\n"

        content += "## Data Flow Patterns\n\n"
        content += "- Request/Response patterns\n"
        content += "- Event streaming patterns\n"
        content += "- Batch processing patterns\n"
        content += "- Database interaction patterns\n\n"

        return content

    def _generate_code_structure(self, context: ExecutionContext) -> str:
        """Generate code-structure.md with package hierarchies and classes.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for code-structure.md.
        """
        packages = self._get_nodes_by_type(context, NodeType.PACKAGE)
        classes = self._get_nodes_by_type(context, NodeType.CLASS)
        interfaces = self._get_nodes_by_type(context, NodeType.INTERFACE)

        content = "# Code Structure\n\n"
        content += "## Overview\n\n"
        content += f"- **Packages:** {len(packages)}\n"
        content += f"- **Classes:** {len(classes)}\n"
        content += f"- **Interfaces:** {len(interfaces)}\n\n"

        if packages:
            content += "## Package Hierarchy\n\n"
            for pkg in packages[:20]:  # Limit to first 20
                content += f"### {pkg.name}\n\n"
                if pkg.path:
                    content += f"Location: `{pkg.path}`\n\n"

        content += "## Key Classes\n\n"
        for cls in classes[:20]:  # Limit to first 20
            content += f"### {cls.name}\n\n"
            if cls.module:
                content += f"Module: {cls.module}\n\n"
            if cls.framework_role:
                content += f"Role: {cls.framework_role}\n\n"

        return content

    def _generate_test_intelligence(self, context: ExecutionContext) -> str:
        """Generate test-intelligence.md with test coverage analysis.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for test-intelligence.md.
        """
        test_classes = self._get_nodes_by_type(context, NodeType.TEST_CLASS)
        coverage = self._get_nodes_by_type(context, NodeType.COVERAGE_REPORT)

        content = "# Test Intelligence\n\n"
        content += "## Overview\n\n"
        content += f"- **Test Classes:** {len(test_classes)}\n"
        content += f"- **Coverage Reports:** {len(coverage)}\n\n"

        if test_classes:
            content += "## Test Classes\n\n"
            for test_cls in test_classes[:15]:
                content += f"### {test_cls.name}\n\n"
                if test_cls.path:
                    content += f"Location: `{test_cls.path}`\n\n"

        if coverage:
            content += "## Coverage Reports\n\n"
            for report in coverage[:10]:
                content += f"- {report.name}\n"

        content += "\n## Recommendations\n\n"
        content += "- Increase branch coverage for critical flows\n"
        content += "- Add integration tests for component interactions\n"
        content += "- Improve assertion quality in existing tests\n"

        return content

    def _generate_technical_debt(self, context: ExecutionContext) -> str:
        """Generate technical-debt.md with issues and recommendations.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for technical-debt.md.
        """
        debt = self._get_nodes_by_type(context, NodeType.TECHNICAL_DEBT)

        content = "# Technical Debt Analysis\n\n"
        content += "## Overview\n\n"
        content += f"- **Issues Identified:** {len(debt)}\n\n"

        if debt:
            content += "## Issues by Category\n\n"
            for issue in debt[:20]:
                content += f"### {issue.name}\n\n"
                if issue.attributes:
                    severity = issue.attributes.get("severity", "Unknown")
                    content += f"- **Severity:** {severity}\n"
                    if "description" in issue.attributes:
                        content += f"- **Description:** {issue.attributes['description']}\n"
                    if "remediation" in issue.attributes:
                        content += f"- **Remediation:** {issue.attributes['remediation']}\n"
                content += "\n"

        content += "## Remediation Strategy\n\n"
        content += "1. Prioritize by severity and impact\n"
        content += "2. Schedule incremental fixes\n"
        content += "3. Add regression tests\n"
        content += "4. Monitor metrics over time\n"

        return content

    def _generate_risk_assessment(self, context: ExecutionContext) -> str:
        """Generate risk-assessment.md with risk analysis.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for risk-assessment.md.
        """
        risks = self._get_nodes_by_type(context, NodeType.RISK)

        content = "# Risk Assessment\n\n"
        content += "## Overview\n\n"
        content += f"- **Risks Identified:** {len(risks)}\n\n"

        if risks:
            content += "## Risk Register\n\n"
            for risk in risks[:15]:
                content += f"### {risk.name}\n\n"
                if risk.attributes:
                    probability = risk.attributes.get("probability", "Unknown")
                    impact = risk.attributes.get("impact", "Unknown")
                    mitigation = risk.attributes.get("mitigation", "")
                    content += f"- **Probability:** {probability}\n"
                    content += f"- **Impact:** {impact}\n"
                    if mitigation:
                        content += f"- **Mitigation:** {mitigation}\n"
                content += "\n"

        content += "## Mitigation Strategies\n\n"
        content += "- Implement defensive programming patterns\n"
        content += "- Add comprehensive error handling\n"
        content += "- Establish monitoring and alerting\n"
        content += "- Conduct security reviews\n"

        return content

    def _generate_endpoints(self, context: ExecutionContext) -> str:
        """Generate endpoints.md with API documentation.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for endpoints.md.
        """
        endpoints = self._get_nodes_by_type(context, NodeType.ENDPOINT)

        content = "# API Endpoints\n\n"
        content += "## Overview\n\n"
        content += f"- **Total Endpoints:** {len(endpoints)}\n\n"

        if endpoints:
            content += "## Endpoint Reference\n\n"
            for endpoint in endpoints[:30]:
                content += f"### {endpoint.name}\n\n"
                if endpoint.path:
                    content += f"**Path:** `{endpoint.path}`\n\n"
                if endpoint.framework_role:
                    content += f"**Method:** {endpoint.framework_role}\n\n"
                if endpoint.attributes:
                    if "description" in endpoint.attributes:
                        content += f"**Description:** {endpoint.attributes['description']}\n\n"

        return content

    def _generate_databases(self, context: ExecutionContext) -> str:
        """Generate databases.md with data model documentation.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for databases.md.
        """
        databases = self._get_nodes_by_type(context, NodeType.DATABASE)
        tables = self._get_nodes_by_type(context, NodeType.DATABASE_TABLE)

        content = "# Data Models\n\n"
        content += "## Overview\n\n"
        content += f"- **Databases:** {len(databases)}\n"
        content += f"- **Tables:** {len(tables)}\n\n"

        if databases:
            content += "## Database Schemas\n\n"
            for db in databases:
                content += f"### {db.name}\n\n"
                if db.path:
                    content += f"Location: `{db.path}`\n\n"
                # Find related tables
                related_tables = self._get_related_nodes(context, db.id, EdgeType.CONTAINS)
                if related_tables:
                    content += "**Tables:**\n"
                    for table in related_tables:
                        content += f"- {table.name}\n"
                content += "\n"

        return content

    def _generate_middleware(self, context: ExecutionContext) -> str:
        """Generate middleware.md with messaging and integration details.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for middleware.md.
        """
        middleware = self._get_nodes_by_type(context, NodeType.MIDDLEWARE)
        topics = self._get_nodes_by_type(context, NodeType.MIDDLEWARE_TOPIC)

        content = "# Middleware & Integration\n\n"
        content += "## Overview\n\n"
        content += f"- **Middleware Systems:** {len(middleware)}\n"
        content += f"- **Topics/Queues:** {len(topics)}\n\n"

        if middleware:
            content += "## Middleware Systems\n\n"
            for mw in middleware:
                content += f"### {mw.name}\n\n"
                if mw.path:
                    content += f"Location: `{mw.path}`\n\n"

        if topics:
            content += "## Topics and Queues\n\n"
            for topic in topics[:20]:
                content += f"- {topic.name}\n"

        return content

    def _generate_exceptions(self, context: ExecutionContext) -> str:
        """Generate exceptions.md with error handling documentation.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for exceptions.md.
        """
        exceptions = self._get_nodes_by_type(context, NodeType.EXCEPTION)

        content = "# Exception Handling\n\n"
        content += "## Overview\n\n"
        content += f"- **Exception Types:** {len(exceptions)}\n\n"

        if exceptions:
            content += "## Exception Types\n\n"
            for exc in exceptions[:25]:
                content += f"### {exc.name}\n\n"
                if exc.attributes:
                    if "description" in exc.attributes:
                        content += f"{exc.attributes['description']}\n\n"
                    if "handling" in exc.attributes:
                        content += f"**Handling:** {exc.attributes['handling']}\n\n"

        content += "## Error Handling Patterns\n\n"
        content += "- Try-catch-finally patterns\n"
        content += "- Fallback strategies\n"
        content += "- Logging and monitoring\n"
        content += "- User-facing error messages\n"

        return content

    def _generate_configuration(self, context: ExecutionContext) -> str:
        """Generate configuration.md with config properties.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for configuration.md.
        """
        configs = self._get_nodes_by_type(context, NodeType.CONFIG_PROPERTY)

        content = "# Configuration\n\n"
        content += "## Overview\n\n"
        content += f"- **Configuration Properties:** {len(configs)}\n\n"

        if configs:
            content += "## Properties\n\n"
            for prop in configs[:30]:
                content += f"### {prop.name}\n\n"
                if prop.attributes:
                    if "default_value" in prop.attributes:
                        content += f"- **Default:** `{prop.attributes['default_value']}`\n"
                    if "description" in prop.attributes:
                        content += f"- **Description:** {prop.attributes['description']}\n"
                content += "\n"

        return content

    def _generate_glossary(self, context: ExecutionContext) -> str:
        """Generate glossary.md with terminology and definitions.

        Args:
            context: ExecutionContext with all data.

        Returns:
            Markdown content for glossary.md.
        """
        content = "# Glossary\n\n"
        content += "## Common Terms\n\n"

        terms = {
            "API": "Application Programming Interface - a set of rules for communication between components",
            "Component": "A self-contained, reusable piece of functionality",
            "Endpoint": "A specific URL or service entry point for API calls",
            "Flow": "A sequence of steps or operations in a business process",
            "Middleware": "Software that enables communication between applications",
            "Module": "A self-contained unit of code with specific functionality",
            "Node": "A vertex in the dependency graph representing a code entity",
            "Edge": "A relationship or dependency between two nodes",
            "Repository": "A collection of code and related artifacts",
            "Schema": "The structure of a database or data model",
            "Service": "A component providing specific business functionality",
            "Topic": "A message queue or event stream in middleware systems",
        }

        for term, definition in sorted(terms.items()):
            content += f"### {term}\n\n{definition}\n\n"

        return content

    def _generate_appendix_nodes(self, context: ExecutionContext) -> str:
        """Generate appendix-nodes.md with complete node reference.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for appendix-nodes.md.
        """
        content = "# Appendix A: Node Reference\n\n"
        content += f"## All Nodes ({len(context.graph.nodes)} total)\n\n"

        # Group by type
        by_type: Dict[str, List] = {}
        for node in context.graph.nodes:
            node_type = node.type.value
            if node_type not in by_type:
                by_type[node_type] = []
            by_type[node_type].append(node)

        for node_type in sorted(by_type.keys()):
            nodes = by_type[node_type]
            content += f"### {node_type} ({len(nodes)})\n\n"
            for node in nodes[:20]:  # Limit per type
                content += f"- **{node.name}**"
                if node.path:
                    content += f" (`{node.path}`)"
                content += "\n"
            if len(nodes) > 20:
                content += f"- ... and {len(nodes) - 20} more\n"
            content += "\n"

        return content

    def _generate_appendix_edges(self, context: ExecutionContext) -> str:
        """Generate appendix-edges.md with complete edge reference.

        Args:
            context: ExecutionContext with graph data.

        Returns:
            Markdown content for appendix-edges.md.
        """
        content = "# Appendix B: Relationship Reference\n\n"
        content += f"## All Relationships ({len(context.graph.edges)} total)\n\n"

        # Group by type
        by_type: Dict[str, int] = {}
        for edge in context.graph.edges:
            edge_type = edge.type.value
            by_type[edge_type] = by_type.get(edge_type, 0) + 1

        content += "### Relationship Types\n\n"
        for edge_type in sorted(by_type.keys()):
            count = by_type[edge_type]
            content += f"- {edge_type}: {count}\n"

        content += "\n### Sample Relationships\n\n"
        for i, edge in enumerate(context.graph.edges[:50]):
            source_node = context.graph.find_node(edge.source)
            target_node = context.graph.find_node(edge.target)
            source_name = source_node.name if source_node else edge.source
            target_name = target_node.name if target_node else edge.target
            content += f"- {source_name} {edge.type.value} {target_name}\n"

        return content

    # Helper methods

    def _get_repositories(self, context: ExecutionContext) -> List:
        """Get all REPOSITORY nodes from graph."""
        return self._get_nodes_by_type(context, NodeType.REPOSITORY)

    def _get_nodes_by_type(self, context: ExecutionContext, node_type: NodeType) -> List:
        """Get all nodes of a specific type.

        Args:
            context: ExecutionContext with graph.
            node_type: NodeType to filter by.

        Returns:
            List of nodes matching the type.
        """
        return [node for node in context.graph.nodes if node.type == node_type]

    def _get_related_nodes(
        self, context: ExecutionContext, node_id: str, edge_type: Optional[EdgeType] = None
    ) -> List:
        """Get all nodes related to a node via edges.

        Args:
            context: ExecutionContext with graph.
            node_id: ID of source node.
            edge_type: Optional EdgeType to filter by.

        Returns:
            List of related nodes.
        """
        related_ids = []
        for edge in context.graph.edges:
            if edge.source == node_id:
                if edge_type is None or edge.type == edge_type:
                    related_ids.append(edge.target)

        return [context.graph.find_node(nid) for nid in related_ids if context.graph.find_node(nid)]

    def _generate_relationship_table(self, context: ExecutionContext) -> str:
        """Generate a table of key relationships.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Markdown table of relationships.
        """
        # Group edges by type
        edges_by_type: Dict[str, int] = {}
        for edge in context.graph.edges:
            edge_type = edge.type.value
            edges_by_type[edge_type] = edges_by_type.get(edge_type, 0) + 1

        table = "| Relationship Type | Count |\n"
        table += "|---|---|\n"
        for edge_type in sorted(edges_by_type.keys()):
            count = edges_by_type[edge_type]
            table += f"| {edge_type} | {count} |\n"

        return table

    def _now_timestamp(self) -> str:
        """Get current timestamp string.

        Returns:
            ISO format timestamp.
        """
        from datetime import datetime
        return datetime.now().isoformat()
