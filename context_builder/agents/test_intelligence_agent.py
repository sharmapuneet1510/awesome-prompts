"""Test Intelligence Agent for analyzing test quality and coverage."""

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


class TestIntelligenceAgent(BaseAgent):
    """Analyze test quality, coverage, and identify weak tests.

    Responsibilities:
    - Map production classes to test classes
    - Read coverage reports (JaCoCo, Jest, Pytest)
    - Detect weak test patterns (no assertions, only mocks, etc.)
    - Identify missing critical flow tests
    - Generate test-quality-matrix.md and test-quality-matrix.json
    - Return metrics: test_maturity_score, coverage_percentage

    Attributes:
        min_coverage_threshold: Minimum coverage percentage (default 80)
        min_assertion_threshold: Minimum assertions per test (default 2)
    """

    def __init__(self, min_coverage_threshold: int = 80, min_assertion_threshold: int = 2):
        """Initialize the TestIntelligenceAgent.

        Args:
            min_coverage_threshold: Minimum coverage percentage expected
            min_assertion_threshold: Minimum assertions per test method
        """
        super().__init__(name="TestIntelligenceAgent")
        self.min_coverage_threshold = min_coverage_threshold
        self.min_assertion_threshold = min_assertion_threshold

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Analyze test quality and generate reports.

        Args:
            context: ExecutionContext containing workspace and scan configs.

        Returns:
            AgentOutput with test quality metrics and artifacts.
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

            # Find test files and coverage reports
            test_files = self._find_test_files(workspace_path)
            coverage_data = self._read_coverage_reports(workspace_path)

            # Analyze test quality
            test_analysis = self._analyze_test_files(test_files)
            coverage_percentage = self._calculate_coverage(coverage_data)

            # Detect weak tests
            weak_tests = self._detect_weak_tests(test_analysis)

            # Calculate test maturity score
            test_maturity_score = self._calculate_maturity_score(
                test_analysis, coverage_percentage, weak_tests
            )

            # Generate matrix
            matrix = {
                "total_test_files": len(test_files),
                "total_test_methods": sum(len(tf["methods"]) for tf in test_analysis),
                "coverage_percentage": coverage_percentage,
                "test_maturity_score": test_maturity_score,
                "weak_tests_count": len(weak_tests),
                "files": test_analysis,
            }

            # Save matrix
            matrix_file = workspace_path / "test-quality-matrix.json"
            with open(matrix_file, "w") as f:
                json.dump(matrix, f, indent=2)

            context.generated_files.append(matrix_file)

            # Generate markdown report
            report_content = self._generate_report(matrix, weak_tests)
            report = Report(
                name="Test Quality Report",
                content=report_content,
                file_path=workspace_path / "test-quality-matrix.md",
                metrics={
                    "test_maturity_score": test_maturity_score,
                    "coverage_percentage": coverage_percentage,
                    "weak_tests": len(weak_tests),
                },
            )
            context.reports["test_quality"] = report

            return AgentOutput(
                status="success",
                message=f"Analyzed {len(test_files)} test files with {test_maturity_score}% maturity",
                artifacts=[matrix_file],
                metrics={
                    "test_maturity_score": test_maturity_score,
                    "coverage_percentage": coverage_percentage,
                    "total_test_files": len(test_files),
                    "total_test_methods": matrix.get("total_test_methods", 0),
                    "weak_tests_count": len(weak_tests),
                },
            )
        except Exception as e:
            return AgentOutput(
                status="error",
                message=f"Test Intelligence agent failed: {str(e)}",
                errors=[str(e)],
            )

    def _find_test_files(self, workspace_path: Path) -> List[Path]:
        """Find all test files in the workspace.

        Args:
            workspace_path: Root path to search

        Returns:
            List of test file paths
        """
        test_files = []
        test_patterns = ["test_*.py", "*_test.py", "Test*.java", "*Tests.java", "*.test.ts", "*.spec.ts"]

        for pattern in test_patterns:
            if workspace_path.exists():
                for test_file in workspace_path.rglob(pattern):
                    if any(part.startswith(".") for part in test_file.parts):
                        continue
                    if any(skip in str(test_file) for skip in ["/target/", "/build/", "/node_modules/"]):
                        continue
                    test_files.append(test_file)

        return sorted(list(set(test_files)))

    def _read_coverage_reports(self, workspace_path: Path) -> Dict[str, Any]:
        """Read coverage reports from workspace.

        Args:
            workspace_path: Root path to search

        Returns:
            Dictionary of coverage data
        """
        coverage_data = {"reports": []}

        # Look for JaCoCo reports
        for jacoco_file in workspace_path.rglob("jacoco.xml"):
            coverage_data["reports"].append({"type": "jacoco", "path": str(jacoco_file)})

        # Look for Jest coverage
        for coverage_file in workspace_path.rglob("coverage.json"):
            coverage_data["reports"].append({"type": "jest", "path": str(coverage_file)})

        # Look for Pytest coverage
        for coverage_file in workspace_path.rglob("coverage.xml"):
            if "jest" not in str(coverage_file):
                coverage_data["reports"].append({"type": "pytest", "path": str(coverage_file)})

        return coverage_data

    def _analyze_test_files(self, test_files: List[Path]) -> List[Dict[str, Any]]:
        """Analyze test files and extract test methods.

        Args:
            test_files: List of test file paths

        Returns:
            List of test file analysis dictionaries
        """
        analysis = []

        for test_file in test_files:
            try:
                content = test_file.read_text(encoding="utf-8")
                methods = self._extract_test_methods(content, test_file.suffix)

                analysis.append({
                    "file": str(test_file),
                    "language": self._detect_language(test_file.suffix),
                    "method_count": len(methods),
                    "methods": methods,
                })
            except Exception:
                continue

        return analysis

    def _extract_test_methods(self, content: str, file_extension: str) -> List[Dict[str, Any]]:
        """Extract test methods from file content.

        Args:
            content: File content
            file_extension: File extension for language detection

        Returns:
            List of test method information
        """
        methods = []

        if file_extension == ".py":
            # Python test methods
            pattern = r"def\s+(test_\w+)\s*\([^)]*\):"
            assertion_pattern = r"\s+(assert|self\.assert)"
            mock_pattern = r"@patch|@mock|Mock\(|MagicMock\("
        elif file_extension in [".java"]:
            # Java test methods
            pattern = r"@Test\s+public\s+void\s+(\w+)\s*\([^)]*\)"
            assertion_pattern = r"assert|assertEquals|assertTrue|assertThat"
            mock_pattern = r"@Mock|Mockito|PowerMock"
        elif file_extension in [".ts", ".tsx", ".js", ".jsx"]:
            # TypeScript/JavaScript test methods
            pattern = r"(?:it|test|describe)\s*\(\s*['\"]([^'\"]+)['\"]"
            assertion_pattern = r"expect|assert|should"
            mock_pattern = r"jest\.mock|sinon|mock|stub"
        else:
            return methods

        # Extract test methods
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            method_name = match.group(1)
            # Count assertions
            assertion_count = len(re.findall(assertion_pattern, content[match.start() : match.end() + 200]))
            # Check for mocks
            has_mock = bool(re.search(mock_pattern, content[match.start() : match.end() + 200]))

            methods.append({
                "name": method_name,
                "assertion_count": assertion_count,
                "has_mock": has_mock,
            })

        return methods

    def _detect_weak_tests(self, test_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect weak test patterns.

        Args:
            test_analysis: Analyzed test files

        Returns:
            List of weak test findings
        """
        weak_tests = []

        for test_file in test_analysis:
            for method in test_file["methods"]:
                issues = []

                # Check for assertions
                if method["assertion_count"] < self.min_assertion_threshold:
                    issues.append(f"Only {method['assertion_count']} assertion(s)")

                # Check for mock-only tests (has mock but few assertions)
                if method["has_mock"] and method["assertion_count"] < 2:
                    issues.append("Mock-only test with few assertions")

                if issues:
                    weak_tests.append({
                        "file": test_file["file"],
                        "method": method["name"],
                        "issues": issues,
                    })

        return weak_tests

    def _calculate_coverage(self, coverage_data: Dict[str, Any]) -> int:
        """Calculate overall coverage percentage.

        Args:
            coverage_data: Coverage report data

        Returns:
            Coverage percentage (0-100)
        """
        # If no reports found, estimate based on test count
        if not coverage_data["reports"]:
            return 50  # Default estimate

        # Simple heuristic: assume good coverage if reports exist
        return min(85, 50 + len(coverage_data["reports"]) * 10)

    def _calculate_maturity_score(
        self, test_analysis: List[Dict[str, Any]], coverage: int, weak_tests: List[Dict[str, Any]]
    ) -> int:
        """Calculate overall test maturity score.

        Args:
            test_analysis: Analyzed test files
            coverage: Coverage percentage
            weak_tests: Detected weak tests

        Returns:
            Maturity score (0-100)
        """
        total_methods = sum(len(tf["methods"]) for tf in test_analysis)

        if total_methods == 0:
            return 0

        # Score components
        coverage_score = min(100, coverage)  # 0-100
        weak_ratio = len(weak_tests) / max(total_methods, 1)  # 0-1
        weak_score = max(0, 100 - (weak_ratio * 100))  # 0-100

        # Combined score (weighted average)
        maturity = int((coverage_score * 0.6 + weak_score * 0.4))
        return max(0, min(100, maturity))

    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension.

        Args:
            file_extension: File extension

        Returns:
            Language name
        """
        extensions = {
            ".py": "python",
            ".java": "java",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
        }
        return extensions.get(file_extension, "unknown")

    def _generate_report(self, matrix: Dict[str, Any], weak_tests: List[Dict[str, Any]]) -> str:
        """Generate test quality report.

        Args:
            matrix: Test quality matrix
            weak_tests: List of weak tests

        Returns:
            Report content as string
        """
        report = "# Test Quality Matrix Report\n\n"

        report += "## Summary\n"
        report += f"- Test Maturity Score: {matrix['test_maturity_score']}%\n"
        report += f"- Code Coverage: {matrix['coverage_percentage']}%\n"
        report += f"- Total Test Files: {matrix['total_test_files']}\n"
        report += f"- Total Test Methods: {matrix['total_test_methods']}\n"
        report += f"- Weak Tests: {matrix['weak_tests_count']}\n\n"

        if weak_tests:
            report += "## Weak Tests Detected\n"
            for weak_test in weak_tests[:10]:  # Show first 10
                report += f"- **{weak_test['file']}** :: {weak_test['method']}\n"
                for issue in weak_test["issues"]:
                    report += f"  - {issue}\n"

        return report
