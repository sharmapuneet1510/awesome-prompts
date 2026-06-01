"""Technical Debt Agent for detecting code quality issues."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Report,
)


class TechnicalDebtAgent(BaseAgent):
    """Detect and analyze technical debt in codebase.

    Responsibilities:
    - Detect large classes (>500 lines)
    - Detect circular dependencies
    - Detect duplicated logic
    - Detect hardcoded configuration
    - Detect weak exception handling
    - Detect missing logging
    - Generate technical-debt.md and bottlenecks.md
    - Return metrics: debt_items, risk_score

    Attributes:
        large_class_threshold: Lines threshold for large class (default 500)
        duplication_threshold: Similarity threshold for duplication (0-1, default 0.8)
    """

    def __init__(self, large_class_threshold: int = 500, duplication_threshold: float = 0.8):
        """Initialize the TechnicalDebtAgent.

        Args:
            large_class_threshold: Line count threshold for flagging large classes
            duplication_threshold: Similarity threshold for duplication detection
        """
        super().__init__(name="TechnicalDebtAgent")
        self.large_class_threshold = large_class_threshold
        self.duplication_threshold = duplication_threshold

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Detect technical debt and generate reports.

        Args:
            context: ExecutionContext containing workspace and graph.

        Returns:
            AgentOutput with technical debt analysis and metrics.
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

            # Detect various debt patterns
            large_classes = self._detect_large_classes(workspace_path)
            circular_deps = self._detect_circular_dependencies(context.graph)
            duplications = self._detect_duplicated_logic(workspace_path)
            hardcoded_config = self._detect_hardcoded_configuration(workspace_path)
            weak_exceptions = self._detect_weak_exception_handling(workspace_path)
            missing_logging = self._detect_missing_logging(workspace_path)

            # Aggregate debt items
            debt_items = {
                "large_classes": large_classes,
                "circular_dependencies": circular_deps,
                "duplicated_logic": duplications,
                "hardcoded_configuration": hardcoded_config,
                "weak_exception_handling": weak_exceptions,
                "missing_logging": missing_logging,
            }

            # Calculate risk score
            risk_score = self._calculate_risk_score(debt_items)

            # Save technical debt report
            debt_file = workspace_path / "technical-debt.json"
            with open(debt_file, "w") as f:
                json.dump(
                    {
                        "total_items": sum(len(v) for v in debt_items.values()),
                        "risk_score": risk_score,
                        "items": debt_items,
                    },
                    f,
                    indent=2,
                )

            context.generated_files.append(debt_file)

            # Generate markdown reports
            debt_report = self._generate_debt_report(debt_items, risk_score)
            report = Report(
                name="Technical Debt Report",
                content=debt_report,
                file_path=workspace_path / "technical-debt.md",
                metrics={
                    "debt_items": sum(len(v) for v in debt_items.values()),
                    "risk_score": risk_score,
                },
            )
            context.reports["technical_debt"] = report

            bottleneck_report = self._generate_bottleneck_report(debt_items, large_classes)
            bottleneck_file = workspace_path / "bottlenecks.md"
            with open(bottleneck_file, "w") as f:
                f.write(bottleneck_report)
            context.generated_files.append(bottleneck_file)

            return AgentOutput(
                status="success",
                message=f"Detected {sum(len(v) for v in debt_items.values())} debt items with risk score {risk_score}",
                artifacts=[debt_file, bottleneck_file],
                metrics={
                    "debt_items": sum(len(v) for v in debt_items.values()),
                    "risk_score": risk_score,
                    "large_classes": len(large_classes),
                    "circular_dependencies": len(circular_deps),
                    "duplications": len(duplications),
                },
            )
        except Exception as e:
            return AgentOutput(
                status="error",
                message=f"Technical Debt agent failed: {str(e)}",
                errors=[str(e)],
            )

    def _detect_large_classes(self, workspace_path: Path) -> List[Dict[str, Any]]:
        """Detect classes that exceed line count threshold.

        Args:
            workspace_path: Root path to scan

        Returns:
            List of large class findings
        """
        large_classes = []

        for code_file in workspace_path.rglob("*"):
            if code_file.is_file() and code_file.suffix in [".java", ".py", ".ts", ".tsx", ".js", ".jsx"]:
                if any(skip in str(code_file) for skip in ["/test", "/tests", "/target/", "/build/", "/node_modules/"]):
                    continue

                try:
                    content = code_file.read_text(encoding="utf-8", errors="ignore")
                    lines = content.split("\n")

                    if len(lines) > self.large_class_threshold:
                        large_classes.append({
                            "file": str(code_file),
                            "lines": len(lines),
                            "excess": len(lines) - self.large_class_threshold,
                        })
                except Exception:
                    continue

        return sorted(large_classes, key=lambda x: x["lines"], reverse=True)[:20]

    def _detect_circular_dependencies(self, graph: Any) -> List[Dict[str, Any]]:
        """Detect circular dependencies in the graph.

        Args:
            graph: Context graph

        Returns:
            List of circular dependency findings
        """
        circular_deps = []

        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str, visited_set: set, rec_set: set, path: List[str]) -> bool:
            visited_set.add(node_id)
            rec_set.add(node_id)
            path.append(node_id)

            # Find outgoing edges
            for edge in graph.edges:
                if edge.source == node_id:
                    if edge.target not in visited_set:
                        if has_cycle(edge.target, visited_set, rec_set, path):
                            return True
                    elif edge.target in rec_set:
                        # Found cycle
                        cycle_start = path.index(edge.target)
                        cycle = path[cycle_start:] + [edge.target]
                        circular_deps.append({
                            "cycle": cycle,
                            "length": len(cycle),
                        })
                        return True

            path.pop()
            rec_set.discard(node_id)
            return False

        # Check for cycles starting from each node
        for node in graph.nodes[:10]:  # Limit to first 10 nodes for performance
            if node.id not in visited:
                has_cycle(node.id, visited, rec_stack, [])

        return circular_deps[:10]  # Return first 10 cycles

    def _detect_duplicated_logic(self, workspace_path: Path) -> List[Dict[str, Any]]:
        """Detect duplicated code patterns.

        Args:
            workspace_path: Root path to scan

        Returns:
            List of duplication findings
        """
        duplications = []
        code_snippets = []

        # Collect code snippets
        for code_file in workspace_path.rglob("*"):
            if code_file.is_file() and code_file.suffix in [".java", ".py"]:
                if any(skip in str(code_file) for skip in ["/test", "/target/", "/build/"]):
                    continue

                try:
                    content = code_file.read_text(encoding="utf-8", errors="ignore")
                    lines = content.split("\n")
                    # Take 5-line chunks as snippets
                    for i in range(len(lines) - 5):
                        snippet = "\n".join(lines[i : i + 5])
                        code_snippets.append({
                            "file": str(code_file),
                            "line": i,
                            "snippet": snippet,
                        })
                except Exception:
                    continue

        # Simple duplication detection: exact matches
        seen_snippets = {}
        for snippet_data in code_snippets:
            key = snippet_data["snippet"].strip()
            if key and len(key) > 20:  # Only track non-trivial snippets
                if key in seen_snippets:
                    duplications.append({
                        "file1": seen_snippets[key]["file"],
                        "file2": snippet_data["file"],
                        "similarity": 1.0,
                    })
                else:
                    seen_snippets[key] = snippet_data

        return duplications[:10]

    def _detect_hardcoded_configuration(self, workspace_path: Path) -> List[Dict[str, Any]]:
        """Detect hardcoded configuration values.

        Args:
            workspace_path: Root path to scan

        Returns:
            List of hardcoded config findings
        """
        hardcoded = []
        hardcoded_patterns = [
            (r"localhost|127\.0\.0\.1|0\.0\.0\.0", "hardcoded_host"),
            (r"password\s*=\s*['\"](\w+)['\"]", "hardcoded_password"),
            (r"api[_-]?key\s*=\s*['\"]([a-zA-Z0-9]+)['\"]", "hardcoded_apikey"),
            (r"port\s*=\s*\d{4,5}", "hardcoded_port"),
        ]

        for code_file in workspace_path.rglob("*"):
            if code_file.is_file() and code_file.suffix in [".java", ".py", ".properties", ".yaml", ".yml"]:
                if any(skip in str(code_file) for skip in ["/test", "/target/", "/build/"]):
                    continue

                try:
                    content = code_file.read_text(encoding="utf-8", errors="ignore")
                    for pattern, pattern_type in hardcoded_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count("\n") + 1
                            hardcoded.append({
                                "file": str(code_file),
                                "line": line_num,
                                "type": pattern_type,
                                "match": match.group(0)[:50],
                            })
                except Exception:
                    continue

        return hardcoded[:15]

    def _detect_weak_exception_handling(self, workspace_path: Path) -> List[Dict[str, Any]]:
        """Detect weak exception handling patterns.

        Args:
            workspace_path: Root path to scan

        Returns:
            List of weak exception handling findings
        """
        weak_handling = []
        weak_patterns = [
            (r"except\s*:\s*pass", "bare_except"),
            (r"catch\s*\(Exception\s+\w+\)\s*\{\s*\}", "empty_catch"),
            (r"except\s+Exception\s*:\s*(?:pass|return|continue)", "generic_exception"),
        ]

        for code_file in workspace_path.rglob("*"):
            if code_file.is_file() and code_file.suffix in [".java", ".py"]:
                if any(skip in str(code_file) for skip in ["/test", "/target/", "/build/"]):
                    continue

                try:
                    content = code_file.read_text(encoding="utf-8", errors="ignore")
                    for pattern, pattern_type in weak_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count("\n") + 1
                            weak_handling.append({
                                "file": str(code_file),
                                "line": line_num,
                                "type": pattern_type,
                            })
                except Exception:
                    continue

        return weak_handling[:15]

    def _detect_missing_logging(self, workspace_path: Path) -> List[Dict[str, Any]]:
        """Detect files with missing logging.

        Args:
            workspace_path: Root path to scan

        Returns:
            List of files with missing logging
        """
        missing_logging = []

        for code_file in workspace_path.rglob("*"):
            if code_file.is_file() and code_file.suffix in [".java", ".py"]:
                if any(skip in str(code_file) for skip in ["/test", "/tests", "/target/", "/build/"]):
                    continue

                try:
                    content = code_file.read_text(encoding="utf-8", errors="ignore")
                    lines = content.split("\n")

                    # Check if file has any logging
                    has_logging = bool(
                        re.search(r"log\.|logger\.|log\.info|log\.debug|print\(", content, re.IGNORECASE)
                    )

                    # Check for error handling
                    has_exception = bool(re.search(r"except|catch|throw", content, re.IGNORECASE))

                    # Flag if exception handling but no logging
                    if has_exception and not has_logging and len(lines) > 50:
                        missing_logging.append({
                            "file": str(code_file),
                            "lines": len(lines),
                            "reason": "Exception handling without logging",
                        })
                except Exception:
                    continue

        return missing_logging[:15]

    def _calculate_risk_score(self, debt_items: Dict[str, List[Dict[str, Any]]]) -> int:
        """Calculate overall risk score based on debt items.

        Args:
            debt_items: Debt findings by category

        Returns:
            Risk score (0-100)
        """
        weights = {
            "large_classes": 15,
            "circular_dependencies": 25,
            "duplicated_logic": 10,
            "hardcoded_configuration": 20,
            "weak_exception_handling": 20,
            "missing_logging": 10,
        }

        total_score = 0
        max_score = sum(weights.values())

        for category, weight in weights.items():
            count = len(debt_items.get(category, []))
            # Each item adds to risk (capped at weight)
            category_score = min(weight, count * 5)
            total_score += category_score

        risk_score = int((total_score / max_score) * 100)
        return min(100, max(0, risk_score))

    def _generate_debt_report(self, debt_items: Dict[str, List[Dict[str, Any]]], risk_score: int) -> str:
        """Generate technical debt report.

        Args:
            debt_items: Debt findings by category
            risk_score: Overall risk score

        Returns:
            Report content as string
        """
        report = "# Technical Debt Report\n\n"

        report += f"## Risk Score: {risk_score}/100\n\n"
        report += "## Summary\n"

        total_items = sum(len(v) for v in debt_items.values())
        report += f"- Total Debt Items: {total_items}\n"
        report += f"- Large Classes: {len(debt_items['large_classes'])}\n"
        report += f"- Circular Dependencies: {len(debt_items['circular_dependencies'])}\n"
        report += f"- Duplicated Logic: {len(debt_items['duplicated_logic'])}\n"
        report += f"- Hardcoded Config: {len(debt_items['hardcoded_configuration'])}\n"
        report += f"- Weak Exception Handling: {len(debt_items['weak_exception_handling'])}\n"
        report += f"- Missing Logging: {len(debt_items['missing_logging'])}\n\n"

        if debt_items["large_classes"]:
            report += "## Large Classes\n"
            for item in debt_items["large_classes"][:5]:
                report += f"- {item['file']} ({item['lines']} lines, +{item['excess']} excess)\n"

        if debt_items["circular_dependencies"]:
            report += "\n## Circular Dependencies\n"
            for item in debt_items["circular_dependencies"][:3]:
                report += f"- Cycle: {' -> '.join(item['cycle'][:3])}...\n"

        return report

    def _generate_bottleneck_report(
        self, debt_items: Dict[str, List[Dict[str, Any]]], large_classes: List[Dict[str, Any]]
    ) -> str:
        """Generate bottleneck report.

        Args:
            debt_items: Debt findings by category
            large_classes: Large class findings

        Returns:
            Report content as string
        """
        report = "# Bottlenecks Report\n\n"

        report += "## Critical Bottlenecks\n\n"

        if large_classes:
            report += "### Performance Bottlenecks\n"
            for item in large_classes[:5]:
                report += f"- {item['file']} (Refactor to reduce {item['excess']} lines)\n"

        if debt_items["circular_dependencies"]:
            report += "\n### Architecture Bottlenecks\n"
            report += f"- {len(debt_items['circular_dependencies'])} circular dependencies detected\n"

        if debt_items["duplicated_logic"]:
            report += "\n### Code Duplication\n"
            report += f"- {len(debt_items['duplicated_logic'])} duplicate code sections found\n"

        report += "\n## Recommended Actions\n"
        report += "1. Refactor large classes using Single Responsibility Principle\n"
        report += "2. Break circular dependencies with dependency injection\n"
        report += "3. Extract duplicated logic to shared utilities\n"
        report += "4. Move hardcoded values to configuration\n"

        return report
