"""Maturity Agent for calculating overall codebase maturity score."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Report,
)


class MaturityAgent(BaseAgent):
    """Calculate overall codebase maturity across 8 dimensions.

    Responsibilities:
    - Score 8 dimensions: structure, code, flows, data, middleware, tests, docs, risk
    - Calculate overall maturity percentage (0-100)
    - Generate maturity-score.json, maturity-report.md, next-actions.md
    - Determine if score >= target_score
    - Return metrics: maturity_score, dimension_scores, status (READY/NOT_READY)

    Attributes:
        target_score: Target maturity score (default 80)
    """

    DIMENSIONS = [
        "project_structure",
        "code_understanding",
        "flow_understanding",
        "data_understanding",
        "middleware_understanding",
        "test_intelligence",
        "documentation_quality",
        "risk_analysis",
    ]

    def __init__(self, target_score: int = 80):
        """Initialize the MaturityAgent.

        Args:
            target_score: Target maturity score (0-100)
        """
        super().__init__(name="MaturityAgent")
        self.target_score = target_score

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Calculate maturity score and generate reports.

        Args:
            context: ExecutionContext containing all reports and metrics.

        Returns:
            AgentOutput with maturity score and status.
        """
        if not self.validate_context(context):
            return AgentOutput(
                status="error",
                message="Invalid execution context",
                errors=["ExecutionContext is None"],
            )

        if not context.workspace_config:
            return AgentOutput(
                status="error",
                message="Missing workspace config",
                errors=["WorkspaceConfig not loaded"],
            )

        try:
            workspace_path = context.workspace_config.context_root

            # Score each dimension
            dimension_scores = self._score_dimensions(context)

            # Calculate overall maturity
            overall_score = self._calculate_overall_score(dimension_scores)

            # Determine status
            status = "READY" if overall_score >= self.target_score else "NOT_READY"

            # Generate reports
            maturity_data = {
                "overall_score": overall_score,
                "target_score": self.target_score,
                "status": status,
                "dimension_scores": dimension_scores,
                "timestamp": str(Path.cwd()),
            }

            # Save maturity score
            score_file = workspace_path / "maturity-score.json"
            with open(score_file, "w") as f:
                json.dump(maturity_data, f, indent=2)

            context.generated_files.append(score_file)

            # Generate markdown reports
            report_content = self._generate_maturity_report(maturity_data)
            report = Report(
                name="Maturity Report",
                content=report_content,
                file_path=workspace_path / "maturity-report.md",
                metrics={
                    "maturity_score": overall_score,
                    "status": status,
                },
            )
            context.reports["maturity"] = report

            # Generate next actions
            next_actions = self._generate_next_actions(dimension_scores, overall_score, context)
            actions_file = workspace_path / "next-actions.md"
            with open(actions_file, "w") as f:
                f.write(next_actions)
            context.generated_files.append(actions_file)

            return AgentOutput(
                status="success",
                message=f"Maturity score: {overall_score}% ({status})",
                artifacts=[score_file, actions_file],
                metrics={
                    "maturity_score": overall_score,
                    "target_score": self.target_score,
                    "status": status,
                    "dimension_scores": dimension_scores,
                },
            )
        except Exception as e:
            return AgentOutput(
                status="error",
                message=f"Maturity agent failed: {str(e)}",
                errors=[str(e)],
            )

    def _score_dimensions(self, context: ExecutionContext) -> Dict[str, int]:
        """Score each maturity dimension.

        Args:
            context: ExecutionContext with all reports and metrics.

        Returns:
            Dictionary of dimension scores (0-100)
        """
        scores = {}

        # Project Structure (based on workspace organization)
        scores["project_structure"] = self._score_project_structure(context)

        # Code Understanding (based on graph complexity and clarity)
        scores["code_understanding"] = self._score_code_understanding(context)

        # Flow Understanding (based on flow analysis report)
        scores["flow_understanding"] = self._score_flow_understanding(context)

        # Data Understanding (based on data relationships in graph)
        scores["data_understanding"] = self._score_data_understanding(context)

        # Middleware Understanding (based on middleware topics and patterns)
        scores["middleware_understanding"] = self._score_middleware_understanding(context)

        # Test Intelligence (from test quality metrics)
        scores["test_intelligence"] = self._score_test_intelligence(context)

        # Documentation Quality (from generated documentation)
        scores["documentation_quality"] = self._score_documentation_quality(context)

        # Risk Analysis (from technical debt metrics)
        scores["risk_analysis"] = self._score_risk_analysis(context)

        return scores

    def _score_project_structure(self, context: ExecutionContext) -> int:
        """Score project structure and organization.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        if not context.workspace_config:
            return 50

        # Check for organized directory structure
        workspace_path = context.workspace_config.context_root
        subdirs = [d for d in workspace_path.iterdir() if d.is_dir() and not d.name.startswith(".")]

        # Expected structure elements
        structure_elements = ["src", "tests", "docs", "config"]
        found_elements = sum(1 for d in subdirs if d.name in structure_elements)

        # Base score on directory organization
        structure_score = min(100, 40 + (found_elements * 15))

        # Check for config files
        config_files = list(workspace_path.glob("**/*.yaml")) + list(workspace_path.glob("**/*.yml"))
        if config_files:
            structure_score = min(100, structure_score + 10)

        return structure_score

    def _score_code_understanding(self, context: ExecutionContext) -> int:
        """Score code understanding and clarity.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        if not context.graph or not context.graph.nodes:
            return 30

        # Score based on graph completeness
        node_count = len(context.graph.nodes)
        edge_count = len(context.graph.edges)

        # Nodes per edge indicates documentation density
        density = node_count / max(edge_count, 1)

        # Calculate score
        code_score = 30
        if node_count > 10:
            code_score += 20
        if node_count > 50:
            code_score += 20
        if edge_count > node_count:
            code_score += 20
        if 0.5 <= density <= 2.0:
            code_score += 10

        return min(100, code_score)

    def _score_flow_understanding(self, context: ExecutionContext) -> int:
        """Score business flow understanding.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        flow_report = context.reports.get("flow_analysis")
        if flow_report and flow_report.metrics:
            flow_score = flow_report.metrics.get("completeness_score", 50)
            return min(100, flow_score)

        # Default scoring from graph
        business_flows = [n for n in context.graph.nodes if n.type.value == "BUSINESS_FLOW"]
        flow_score = 30 + (min(40, len(business_flows) * 10))

        return min(100, flow_score)

    def _score_data_understanding(self, context: ExecutionContext) -> int:
        """Score data model understanding.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        # Check for database tables in graph
        db_tables = [n for n in context.graph.nodes if n.type.value == "DATABASE_TABLE"]
        db_nodes = [n for n in context.graph.nodes if n.type.value == "DATABASE"]

        data_score = 20
        if db_nodes:
            data_score += 30
        if len(db_tables) > 5:
            data_score += 30
        if len(db_tables) > 10:
            data_score += 20

        return min(100, data_score)

    def _score_middleware_understanding(self, context: ExecutionContext) -> int:
        """Score middleware pattern understanding.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        # Check for middleware nodes
        middleware_nodes = [n for n in context.graph.nodes if n.type.value == "MIDDLEWARE"]
        topics = [n for n in context.graph.nodes if n.type.value == "MIDDLEWARE_TOPIC"]

        middleware_score = 20
        if middleware_nodes:
            middleware_score += 40
        if topics:
            middleware_score += 40

        return min(100, middleware_score)

    def _score_test_intelligence(self, context: ExecutionContext) -> int:
        """Score test quality and coverage.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        test_report = context.reports.get("test_quality")
        if test_report and test_report.metrics:
            return test_report.metrics.get("test_maturity_score", 50)

        # Check for test files in workspace
        if context.workspace_config:
            test_files = list(context.workspace_config.context_root.rglob("test_*.py"))
            test_files += list(context.workspace_config.context_root.rglob("*_test.py"))
            test_files += list(context.workspace_config.context_root.rglob("Test*.java"))

            if test_files:
                return min(100, 50 + len(test_files) * 5)

        return 30

    def _score_documentation_quality(self, context: ExecutionContext) -> int:
        """Score documentation quality and completeness.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        doc_score = 20

        # Check for README
        if context.workspace_config:
            workspace_path = context.workspace_config.context_root
            if (workspace_path / "README.md").exists():
                doc_score += 20

            # Check for API documentation
            api_docs = list(workspace_path.rglob("API*.md")) + list(workspace_path.rglob("api*.md"))
            if api_docs:
                doc_score += 20

            # Check for architecture documentation
            arch_docs = list(workspace_path.rglob("ARCHITECTURE*.md")) + list(workspace_path.rglob("architecture*.md"))
            if arch_docs:
                doc_score += 20

            # Check for general markdown docs
            md_files = list(workspace_path.rglob("*.md"))
            if len(md_files) > 3:
                doc_score += 20

        return min(100, doc_score)

    def _score_risk_analysis(self, context: ExecutionContext) -> int:
        """Score risk and code quality.

        Args:
            context: ExecutionContext

        Returns:
            Score (0-100)
        """
        debt_report = context.reports.get("technical_debt")
        if debt_report and debt_report.metrics:
            # Inverse risk score: lower risk = higher score
            risk_score = debt_report.metrics.get("risk_score", 50)
            return max(0, 100 - risk_score)

        # Default: moderate risk
        return 60

    def _calculate_overall_score(self, dimension_scores: Dict[str, int]) -> int:
        """Calculate overall maturity score from dimension scores.

        Args:
            dimension_scores: Dictionary of dimension scores

        Returns:
            Overall score (0-100)
        """
        if not dimension_scores:
            return 0

        # Equal weighting for all dimensions
        total = sum(dimension_scores.values())
        average = total / len(dimension_scores)

        return int(average)

    def _generate_maturity_report(self, maturity_data: Dict[str, Any]) -> str:
        """Generate maturity report.

        Args:
            maturity_data: Maturity analysis data

        Returns:
            Report content as string
        """
        report = "# Codebase Maturity Report\n\n"

        overall = maturity_data["overall_score"]
        target = maturity_data["target_score"]
        status = maturity_data["status"]

        report += f"## Overall Maturity: {overall}% ({status})\n"
        report += f"Target: {target}% | Gap: {target - overall}%\n\n"

        report += "## Dimension Scores\n"
        for dim, score in maturity_data["dimension_scores"].items():
            bar_length = int(score / 10)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            report += f"- {dim.replace('_', ' ').title()}: {score}% [{bar}]\n"

        report += "\n## Interpretation\n"
        if overall >= 90:
            report += "- **Excellent**: Codebase is well-structured and mature\n"
        elif overall >= 80:
            report += "- **Good**: Solid foundation with minor improvements needed\n"
        elif overall >= 70:
            report += "- **Fair**: Functional but significant improvements recommended\n"
        elif overall >= 50:
            report += "- **Poor**: Major refactoring needed\n"
        else:
            report += "- **Critical**: Comprehensive overhaul required\n"

        return report

    def _generate_next_actions(
        self, dimension_scores: Dict[str, int], overall_score: int, context: ExecutionContext
    ) -> str:
        """Generate next actions based on maturity analysis.

        Args:
            dimension_scores: Dictionary of dimension scores
            overall_score: Overall maturity score
            context: ExecutionContext

        Returns:
            Next actions as markdown string
        """
        actions = "# Maturity Improvement Actions\n\n"

        # Find lowest scoring dimensions
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
        lowest_dims = sorted_dims[:3]

        actions += "## Priority Improvements\n\n"

        action_map = {
            "project_structure": "- Reorganize project directories to match standard structure\n"
            "  - Create separate src/, tests/, docs/ directories\n"
            "  - Establish module boundaries\n",
            "code_understanding": "- Improve code clarity and documentation\n"
            "  - Add docstrings/JSDoc to complex methods\n"
            "  - Refactor overly complex functions\n",
            "flow_understanding": "- Document business flows and workflows\n"
            "  - Create flow diagrams\n"
            "  - Add integration tests for critical paths\n",
            "data_understanding": "- Document data model and relationships\n"
            "  - Create database schema diagrams\n"
            "  - Add validation rules\n",
            "middleware_understanding": "- Document middleware and messaging patterns\n"
            "  - Create topology diagrams\n"
            "  - Document topic contracts\n",
            "test_intelligence": "- Improve test coverage and quality\n"
            "  - Increase unit test coverage to 80%+\n"
            "  - Add critical path integration tests\n",
            "documentation_quality": "- Expand project documentation\n"
            "  - Create comprehensive README\n"
            "  - Document APIs and architecture\n",
            "risk_analysis": "- Address technical debt\n"
            "  - Refactor large classes\n"
            "  - Resolve circular dependencies\n",
        }

        for dim_name, score in lowest_dims:
            if score < 70:
                actions += f"\n### {dim_name.replace('_', ' ').title()} ({score}%)\n"
                actions += action_map.get(dim_name, "- Address deficiencies in this area\n")

        actions += "\n## Overall Strategy\n"
        actions += f"- Current Score: {overall_score}%\n"
        gap = 100 - overall_score
        if gap > 20:
            actions += f"- Significant Gap: {gap}% below excellence\n"
            actions += "- Recommend: Multi-phase improvement plan\n"
        elif gap > 0:
            actions += f"- Minor Gap: {gap}% to excellence\n"
            actions += "- Recommend: Focus on 1-2 key areas\n"
        else:
            actions += "- Target Achieved!\n"
            actions += "- Focus: Maintain and continuous improvement\n"

        return actions
