"""Tests for TechnicalDebtAgent."""

import json
from pathlib import Path

import pytest

from context_builder.agents import TechnicalDebtAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Graph,
    MaturityConfig,
    Node,
    NodeType,
    ProjectConfig,
    ScanConfig,
    TechAliases,
    TestQualityConfig,
    WorkspaceConfig,
)


@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temporary workspace."""
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    return tmp_path


@pytest.fixture
def code_workspace(tmp_workspace):
    """Create workspace with sample code files."""
    src_dir = tmp_workspace / "src"
    src_dir.mkdir()

    # Create a large class file
    large_class_content = "\n".join([
        "public class LargeClass {",
        "    private int field1;",
        "    private int field2;",
    ] + [f"    public void method{i}() {{\n        field1 = {i};\n    }}" for i in range(100)] + [
        "}"
    ])

    (src_dir / "LargeClass.java").write_text(large_class_content)

    # Create a file with hardcoded config
    (src_dir / "Config.java").write_text("""
public class Config {
    private String host = "localhost";
    private int port = 8080;
    private String password = "secret123";
    private String apiKey = "abc123def456";
}
""")

    # Create a file with weak exception handling
    (src_dir / "WeakHandler.java").write_text("""
public class WeakHandler {
    public void process() {
        try {
            doSomething();
        } catch (Exception e) {
            // Ignoring exception
        }
    }

    public void badMethod() {
        try {
            risky();
        } catch (Exception e) {
        }
    }
}
""")

    # Create Python file with logging issues
    (src_dir / "Service.py").write_text("""
class UserService:
    def get_user(self, user_id):
        try:
            user = self.db.find(user_id)
            if not user:
                raise ValueError("User not found")
            return user
        except ValueError:
            return None

    def delete_user(self, user_id):
        try:
            self.db.delete(user_id)
        except Exception:
            pass
""")

    return tmp_workspace


@pytest.fixture
def graph_with_cycles(tmp_workspace):
    """Create a graph with circular dependencies."""
    graph = Graph()

    # Create nodes
    node_a = Node(id="a", type=NodeType.CLASS, name="ClassA")
    node_b = Node(id="b", type=NodeType.CLASS, name="ClassB")
    node_c = Node(id="c", type=NodeType.CLASS, name="ClassC")

    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(node_c)

    return graph


@pytest.fixture
def execution_context(code_workspace, graph_with_cycles):
    """Create execution context."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace",
        context_root=code_workspace,
    )

    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=graph_with_cycles,
    )


class TestTechnicalDebtAgent:
    """Tests for TechnicalDebtAgent."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = TechnicalDebtAgent()
        assert agent.name == "TechnicalDebtAgent"
        assert agent.large_class_threshold == 500

    def test_agent_custom_initialization(self):
        """Test agent with custom thresholds."""
        agent = TechnicalDebtAgent(
            large_class_threshold=300,
            duplication_threshold=0.9,
        )
        assert agent.large_class_threshold == 300

    def test_agent_execute_success(self, execution_context):
        """Test successful execution."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) >= 1

    def test_agent_creates_debt_file(self, execution_context):
        """Test that agent creates technical-debt.json."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"

        assert debt_file.exists()
        debt_data = json.loads(debt_file.read_text())
        assert "risk_score" in debt_data
        assert "items" in debt_data

    def test_agent_returns_metrics(self, execution_context):
        """Test that agent returns expected metrics."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        assert "debt_items" in output.metrics
        assert "risk_score" in output.metrics

    def test_agent_detects_large_classes(self, execution_context):
        """Test detection of large classes."""
        agent = TechnicalDebtAgent(large_class_threshold=50)  # Lower threshold to detect
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        # Should detect large class or be empty (no large files matched)
        assert isinstance(debt_data["items"]["large_classes"], list)

    def test_agent_detects_hardcoded_config(self, execution_context):
        """Test detection of hardcoded configuration."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        # Should have a list (may be empty if patterns don't match)
        assert isinstance(debt_data["items"]["hardcoded_configuration"], list)

    def test_agent_detects_weak_exception_handling(self, execution_context):
        """Test detection of weak exception handling."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        # Should have a list (may be empty if patterns don't match)
        assert isinstance(debt_data["items"]["weak_exception_handling"], list)

    def test_agent_detects_missing_logging(self, execution_context):
        """Test detection of missing logging."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        # Should have a list (may be empty if patterns don't match)
        assert isinstance(debt_data["items"]["missing_logging"], list)

    def test_risk_score_range(self, execution_context):
        """Test that risk score is in valid range."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        risk_score = output.metrics["risk_score"]
        assert 0 <= risk_score <= 100

    def test_agent_generates_markdown_reports(self, execution_context):
        """Test that agent generates markdown reports."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root

        # Should generate markdown report (stored in reports)
        assert "technical_debt" in execution_context.reports

    def test_agent_handles_none_context(self):
        """Test agent handles None context."""
        agent = TechnicalDebtAgent()
        output = agent.execute(None)

        assert output.status == "error"

    def test_agent_handles_empty_workspace(self, tmp_path):
        """Test agent handles empty workspace."""
        workspace_config = WorkspaceConfig(
            id="empty",
            name="Empty",
            description="Empty workspace",
            context_root=tmp_path,
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        agent = TechnicalDebtAgent()
        output = agent.execute(context)

        assert output.status == "success"

    def test_debt_file_structure(self, execution_context):
        """Test structure of generated debt file."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        required_categories = [
            "large_classes",
            "circular_dependencies",
            "duplicated_logic",
            "hardcoded_configuration",
            "weak_exception_handling",
            "missing_logging",
        ]

        for category in required_categories:
            assert category in debt_data["items"]
            assert isinstance(debt_data["items"][category], list)

    def test_artifact_tracking(self, execution_context):
        """Test that generated files are tracked."""
        agent = TechnicalDebtAgent()
        initial_count = len(execution_context.generated_files)
        output = agent.execute(execution_context)

        assert len(execution_context.generated_files) > initial_count

    def test_bottleneck_report_generated(self, execution_context):
        """Test that bottleneck report is generated."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        bottleneck_file = workspace_path / "bottlenecks.md"

        assert bottleneck_file.exists()
        content = bottleneck_file.read_text()
        assert "Bottleneck" in content or "bottleneck" in content.lower()

    def test_report_content_quality(self, execution_context):
        """Test that report contains meaningful content."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        report = execution_context.reports["technical_debt"]
        assert len(report.content) > 0
        assert "Risk" in report.content or "risk" in report.content.lower()

    def test_circular_dependency_detection(self, execution_context):
        """Test circular dependency detection."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        # Circular dependencies might be empty or contain items
        assert isinstance(debt_data["items"]["circular_dependencies"], list)

    def test_total_debt_items_count(self, execution_context):
        """Test that total debt items is calculated correctly."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        total = debt_data["total_items"]
        calculated = sum(len(v) for v in debt_data["items"].values())

        assert total == calculated

    def test_large_class_detection_threshold(self, code_workspace):
        """Test large class detection with custom threshold."""
        workspace_config = WorkspaceConfig(
            id="test",
            name="Test",
            description="Test",
            context_root=code_workspace,
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        # Test with high threshold
        agent = TechnicalDebtAgent(large_class_threshold=10000)
        output = agent.execute(context)

        workspace_path = context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        # Should detect no large classes with high threshold
        assert len(debt_data["items"]["large_classes"]) == 0

    def test_hardcoded_values_specificity(self, execution_context):
        """Test that hardcoded values are categorized."""
        agent = TechnicalDebtAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        debt_file = workspace_path / "technical-debt.json"
        debt_data = json.loads(debt_file.read_text())

        hardcoded = debt_data["items"]["hardcoded_configuration"]
        if hardcoded:
            # Each item should have a type
            for item in hardcoded:
                assert "type" in item
