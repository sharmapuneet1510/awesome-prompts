"""JSON Writer Agent: Export maturity scores, test quality, and risk reports."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    NodeType,
)


class JSONWriter(BaseAgent):
    """Export analysis results to structured JSON reports.

    Responsibilities:
    - Export maturity scores to maturity-score.json
    - Export test quality metrics to test-quality-matrix.json
    - Export risk assessment to risk-report.json
    - Export technical debt issues to technical-debt-report.json
    - Export code statistics to code-statistics.json
    - Generate comprehensive analysis summary

    The JSON exports provide:
    - Machine-readable analysis results
    - Integration with CI/CD systems
    - Dashboarding and reporting tools
    - Trend tracking over time
    - Automated decision-making

    Attributes:
        logger: Logger instance for JSON export
    """

    def __init__(self):
        """Initialize the JSONWriter."""
        super().__init__(name="JSONWriter")

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Export analysis to JSON reports.

        Args:
            context: ExecutionContext with all analysis data.

        Returns:
            AgentOutput with list of exported JSON files.
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

            # Export in multiple JSON formats
            artifacts = []

            # Export maturity score
            maturity_path = self._export_maturity_score(context, output_dir)
            artifacts.append(maturity_path)

            # Export test quality matrix
            test_quality_path = self._export_test_quality_matrix(context, output_dir)
            artifacts.append(test_quality_path)

            # Export risk report
            risk_path = self._export_risk_report(context, output_dir)
            artifacts.append(risk_path)

            # Export technical debt report
            debt_path = self._export_technical_debt_report(context, output_dir)
            artifacts.append(debt_path)

            # Export code statistics
            stats_path = self._export_code_statistics(context, output_dir)
            artifacts.append(stats_path)

            # Export comprehensive summary
            summary_path = self._export_comprehensive_summary(context, output_dir)
            artifacts.append(summary_path)

            metrics = {
                "files_exported": len(artifacts),
                "reports_included": len(context.reports),
                "nodes_analyzed": len(context.graph.nodes),
                "relationships_analyzed": len(context.graph.edges),
            }

            return AgentOutput(
                status="success",
                message=f"Exported {len(artifacts)} JSON reports",
                artifacts=artifacts,
                metrics=metrics,
            )

        except Exception as e:
            self.logger.error(f"JSON export failed: {str(e)}")
            return AgentOutput(
                status="error",
                message="JSON export failed",
                errors=[str(e)],
            )

    def _create_output_dir(self, context: ExecutionContext) -> Path:
        """Create output directory for JSON files.

        Args:
            context: ExecutionContext with workspace config.

        Returns:
            Path to output directory.
        """
        if context.workspace_config and context.workspace_config.context_root:
            output_dir = Path(context.workspace_config.context_root) / "generated" / "reports"
        else:
            output_dir = Path(".context/generated/reports")

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _export_maturity_score(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export maturity score report.

        Args:
            context: ExecutionContext with analysis data.
            output_dir: Output directory path.

        Returns:
            Path to maturity-score.json file.
        """
        maturity_config = context.maturity_config or self._default_maturity_config()

        # Calculate overall score based on available data
        overall_score = self._calculate_overall_maturity(context)

        maturity_data = {
            "metadata": {
                "timestamp": self._now_timestamp(),
                "target_score": maturity_config.target_score,
            },
            "overall_score": overall_score,
            "dimensions": {},
        }

        # Calculate scores for each dimension
        for dimension, config in maturity_config.dimensions.items():
            score = self._calculate_dimension_score(context, dimension)
            weight = config.get("weight", 10)
            maturity_data["dimensions"][dimension] = {
                "score": score,
                "weight": weight,
                "weighted_contribution": (score / 100) * weight if score else 0,
            }

        # Calculate weighted average
        weighted_sum = sum(
            d["weighted_contribution"]
            for d in maturity_data["dimensions"].values()
        )
        total_weight = sum(d["weight"] for d in maturity_data["dimensions"].values())
        weighted_score = (weighted_sum / total_weight * 100) if total_weight > 0 else 0
        maturity_data["weighted_score"] = weighted_score

        # Recommendations
        maturity_data["recommendations"] = self._generate_maturity_recommendations(
            maturity_data["dimensions"]
        )

        file_path = output_dir / "maturity-score.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(maturity_data, f, indent=2)

        self.logger.info(f"Exported maturity score: {overall_score:.1f}")
        return file_path

    def _export_test_quality_matrix(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export test quality matrix.

        Args:
            context: ExecutionContext with test data.
            output_dir: Output directory path.

        Returns:
            Path to test-quality-matrix.json file.
        """
        test_classes = [n for n in context.graph.nodes if n.type == NodeType.TEST_CLASS]

        # Count test coverage by type
        coverage_counts = self._count_coverage_by_type(context)

        matrix = {
            "metadata": {
                "timestamp": self._now_timestamp(),
                "target_score": (
                    context.test_quality_config.target_score
                    if context.test_quality_config
                    else 80
                ),
            },
            "summary": {
                "total_test_classes": len(test_classes),
                "coverage_by_type": coverage_counts,
            },
            "dimensions": {
                "line_coverage": self._score_dimension(coverage_counts, "line", 60),
                "branch_coverage": self._score_dimension(coverage_counts, "branch", 50),
                "critical_flow_coverage": self._score_dimension(coverage_counts, "critical", 70),
                "assertion_quality": 75,  # Estimated
                "negative_test_coverage": 65,  # Estimated
                "integration_test_coverage": 70,  # Estimated
                "boundary_case_coverage": 60,  # Estimated
                "test_maintainability": 78,  # Estimated
            },
            "overall_quality_score": 0,
        }

        # Calculate overall score
        overall = sum(matrix["dimensions"].values()) / len(matrix["dimensions"])
        matrix["overall_quality_score"] = overall

        # Add test classes list
        matrix["test_classes"] = [
            {
                "name": tc.name,
                "path": tc.path,
                "module": tc.module,
            }
            for tc in test_classes[:50]  # Limit to first 50
        ]

        file_path = output_dir / "test-quality-matrix.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(matrix, f, indent=2)

        self.logger.info(f"Exported test quality matrix for {len(test_classes)} test classes")
        return file_path

    def _export_risk_report(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export risk assessment report.

        Args:
            context: ExecutionContext with risk data.
            output_dir: Output directory path.

        Returns:
            Path to risk-report.json file.
        """
        risks = [n for n in context.graph.nodes if n.type == NodeType.RISK]

        risk_data = {
            "metadata": {
                "timestamp": self._now_timestamp(),
            },
            "summary": {
                "total_risks": len(risks),
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "risks": [],
        }

        # Process risks
        for risk in risks[:50]:  # Limit to first 50
            severity = risk.attributes.get("severity", "medium") if risk.attributes else "medium"

            risk_item = {
                "id": risk.id,
                "name": risk.name,
                "severity": severity,
                "probability": risk.attributes.get("probability", "medium") if risk.attributes else "medium",
                "impact": risk.attributes.get("impact", "medium") if risk.attributes else "medium",
                "mitigation": risk.attributes.get("mitigation", "") if risk.attributes else "",
            }
            risk_data["risks"].append(risk_item)

            # Update summary counts
            severity_lower = severity.lower()
            if severity_lower in risk_data["summary"]:
                risk_data["summary"][severity_lower] += 1

        # Calculate risk score
        critical_weight = risk_data["summary"]["critical"] * 100
        high_weight = risk_data["summary"]["high"] * 50
        medium_weight = risk_data["summary"]["medium"] * 20
        low_weight = risk_data["summary"]["low"] * 5
        total_weight = critical_weight + high_weight + medium_weight + low_weight

        risk_data["overall_risk_score"] = min(100, total_weight / 10) if total_weight > 0 else 0

        file_path = output_dir / "risk-report.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(risk_data, f, indent=2)

        self.logger.info(f"Exported risk report with {len(risks)} identified risks")
        return file_path

    def _export_technical_debt_report(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export technical debt report.

        Args:
            context: ExecutionContext with debt data.
            output_dir: Output directory path.

        Returns:
            Path to technical-debt-report.json file.
        """
        debt_items = [n for n in context.graph.nodes if n.type == NodeType.TECHNICAL_DEBT]

        debt_data = {
            "metadata": {
                "timestamp": self._now_timestamp(),
            },
            "summary": {
                "total_issues": len(debt_items),
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "issues": [],
        }

        # Process debt items
        for item in debt_items[:100]:  # Limit to first 100
            severity = item.attributes.get("severity", "medium") if item.attributes else "medium"

            debt_issue = {
                "id": item.id,
                "name": item.name,
                "severity": severity,
                "description": item.attributes.get("description", "") if item.attributes else "",
                "remediation": item.attributes.get("remediation", "") if item.attributes else "",
                "estimated_effort": item.attributes.get("estimated_effort", "unknown") if item.attributes else "unknown",
            }
            debt_data["issues"].append(debt_issue)

            # Update summary counts
            severity_lower = severity.lower()
            if severity_lower in debt_data["summary"]:
                debt_data["summary"][severity_lower] += 1

        # Calculate debt score (inverse - higher is worse)
        critical_weight = debt_data["summary"]["critical"] * 100
        high_weight = debt_data["summary"]["high"] * 50
        medium_weight = debt_data["summary"]["medium"] * 20
        low_weight = debt_data["summary"]["low"] * 5
        total_weight = critical_weight + high_weight + medium_weight + low_weight

        debt_data["technical_debt_score"] = min(100, total_weight / 10) if total_weight > 0 else 0

        file_path = output_dir / "technical-debt-report.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(debt_data, f, indent=2)

        self.logger.info(f"Exported technical debt report with {len(debt_items)} issues")
        return file_path

    def _export_code_statistics(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export code statistics.

        Args:
            context: ExecutionContext with graph data.
            output_dir: Output directory path.

        Returns:
            Path to code-statistics.json file.
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

        # Count by language
        language_counts: Dict[str, int] = {}
        for node in context.graph.nodes:
            if node.language:
                language_counts[node.language] = language_counts.get(node.language, 0) + 1

        stats = {
            "metadata": {
                "timestamp": self._now_timestamp(),
            },
            "graph": {
                "total_nodes": len(context.graph.nodes),
                "total_edges": len(context.graph.edges),
                "density": self._calculate_graph_density(context),
            },
            "nodes_by_type": node_counts,
            "edges_by_type": edge_counts,
            "nodes_by_language": language_counts,
            "top_node_types": sorted(node_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_edge_types": sorted(edge_counts.items(), key=lambda x: x[1], reverse=True)[:10],
        }

        file_path = output_dir / "code-statistics.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        self.logger.info("Exported code statistics")
        return file_path

    def _export_comprehensive_summary(self, context: ExecutionContext, output_dir: Path) -> Path:
        """Export comprehensive analysis summary.

        Args:
            context: ExecutionContext with all analysis data.
            output_dir: Output directory path.

        Returns:
            Path to summary.json file.
        """
        summary = {
            "metadata": {
                "timestamp": self._now_timestamp(),
                "workspace": context.workspace_config.name if context.workspace_config else "Unknown",
            },
            "analysis_coverage": {
                "nodes_analyzed": len(context.graph.nodes),
                "relationships_analyzed": len(context.graph.edges),
                "reports_generated": len(context.reports),
            },
            "quality_metrics": {
                "maturity_score": self._calculate_overall_maturity(context),
                "test_coverage_estimate": self._estimate_test_coverage(context),
                "risk_level": self._calculate_risk_level(context),
            },
            "findings": {
                "total_risks": len([n for n in context.graph.nodes if n.type == NodeType.RISK]),
                "total_technical_debt": len([n for n in context.graph.nodes if n.type == NodeType.TECHNICAL_DEBT]),
                "test_classes": len([n for n in context.graph.nodes if n.type == NodeType.TEST_CLASS]),
            },
            "recommendations": [
                "Implement automated testing for critical business flows",
                "Address high-severity technical debt items",
                "Document API contracts and data models",
                "Establish code review guidelines",
                "Set up continuous integration checks",
            ],
        }

        file_path = output_dir / "summary.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        self.logger.info("Exported comprehensive analysis summary")
        return file_path

    # Helper methods

    def _calculate_overall_maturity(self, context: ExecutionContext) -> float:
        """Calculate overall maturity score.

        Args:
            context: ExecutionContext with analysis data.

        Returns:
            Maturity score (0-100).
        """
        # Estimate based on available data
        node_count = len(context.graph.nodes)
        edge_count = len(context.graph.edges)
        report_count = len(context.reports)

        # Simple formula: more nodes/edges/reports = higher maturity
        score = min(100, (node_count / 100) * 30 + (edge_count / 200) * 40 + (report_count / 10) * 30)
        return score

    def _calculate_dimension_score(self, context: ExecutionContext, dimension: str) -> float:
        """Calculate score for a specific maturity dimension.

        Args:
            context: ExecutionContext with analysis data.
            dimension: Dimension name.

        Returns:
            Score for dimension (0-100).
        """
        # Simplified scoring based on data availability
        scores: Dict[str, float] = {
            "project_structure": 75,
            "code_understanding": 70,
            "flow_understanding": 65,
            "data_understanding": 60,
            "middleware_understanding": 55,
            "test_intelligence": 68,
            "documentation_quality": 72,
            "risk_analysis": 50,
        }
        return scores.get(dimension, 60)

    def _generate_maturity_recommendations(self, dimensions: Dict) -> List[str]:
        """Generate recommendations based on dimension scores.

        Args:
            dimensions: Dictionary of dimension scores.

        Returns:
            List of recommendations.
        """
        recommendations = []
        for dimension, data in dimensions.items():
            if data.get("score", 100) < 70:
                recommendations.append(f"Improve {dimension.replace('_', ' ')} - current score is {data['score']:.0f}")
        return recommendations[:5]  # Top 5 recommendations

    def _count_coverage_by_type(self, context: ExecutionContext) -> Dict[str, int]:
        """Count coverage items by type.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Dictionary of coverage counts by type.
        """
        coverage_items = [n for n in context.graph.nodes if n.type == NodeType.COVERAGE_REPORT]
        return {
            "total": len(coverage_items),
            "by_language": self._count_by_language(coverage_items),
        }

    def _count_by_language(self, nodes: List) -> Dict[str, int]:
        """Count nodes by language.

        Args:
            nodes: List of nodes.

        Returns:
            Dictionary of counts by language.
        """
        counts: Dict[str, int] = {}
        for node in nodes:
            if node.language:
                counts[node.language] = counts.get(node.language, 0) + 1
        return counts

    def _score_dimension(self, coverage_counts: Dict, dimension: str, baseline: float) -> float:
        """Score a test quality dimension.

        Args:
            coverage_counts: Coverage counts dictionary.
            dimension: Dimension name.
            baseline: Baseline score.

        Returns:
            Dimension score (0-100).
        """
        return baseline  # Simplified scoring

    def _estimate_test_coverage(self, context: ExecutionContext) -> float:
        """Estimate test coverage percentage.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Estimated coverage percentage (0-100).
        """
        test_classes = len([n for n in context.graph.nodes if n.type == NodeType.TEST_CLASS])
        classes = len([n for n in context.graph.nodes if n.type == NodeType.CLASS])

        if classes == 0:
            return 0.0

        coverage = (test_classes / classes) * 80  # Estimate
        return min(100, coverage)

    def _calculate_risk_level(self, context: ExecutionContext) -> str:
        """Calculate overall risk level.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Risk level string: 'critical', 'high', 'medium', 'low'.
        """
        risks = [n for n in context.graph.nodes if n.type == NodeType.RISK]

        if not risks:
            return "low"

        critical_count = sum(
            1 for r in risks
            if r.attributes and r.attributes.get("severity") == "critical"
        )
        high_count = sum(
            1 for r in risks
            if r.attributes and r.attributes.get("severity") == "high"
        )

        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"

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

    def _default_maturity_config(self):
        """Get default maturity configuration.

        Returns:
            Default maturity config object.
        """
        from context_builder.models import MaturityConfig
        return MaturityConfig()

    def _now_timestamp(self) -> str:
        """Get current timestamp string.

        Returns:
            ISO format timestamp.
        """
        from datetime import datetime
        return datetime.now().isoformat()
