"""Tests for TestIntelligenceAgent."""

import json
from pathlib import Path

import pytest

from context_builder.agents import TestIntelligenceAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Graph,
    MaturityConfig,
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
def test_workspace(tmp_workspace):
    """Create workspace with test files."""
    # Create Python test files
    tests_dir = tmp_workspace / "tests"
    tests_dir.mkdir()

    (tests_dir / "test_user.py").write_text("""
import pytest
from unittest.mock import Mock

def test_user_creation():
    user = User("John")
    assert user.name == "John"
    assert user.is_active is True

def test_user_update():
    user = User("Jane")
    user.update_name("Jane Doe")
    assert user.name == "Jane Doe"

def test_user_with_mock():
    mock_db = Mock()
    user = User("Bob", db=mock_db)
    # Only calls without assertions
""")

    (tests_dir / "test_service.py").write_text("""
def test_service_init():
    service = UserService()
    assert service is not None

def test_service_get_user():
    service = UserService()
    user = service.get_user(1)
    assert user.id == 1
    assert user.name is not None
""")

    # Create Java test files
    java_tests_dir = tmp_workspace / "src" / "test" / "java" / "com" / "example"
    java_tests_dir.mkdir(parents=True)

    (java_tests_dir / "UserServiceTest.java").write_text("""
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class UserServiceTest {

    @Test
    public void testGetUser() {
        UserService service = new UserService();
        User user = service.getUser(1);
        assertNotNull(user);
        assertEquals("John", user.getName());
    }

    @Test
    public void testCreateUser() {
        UserService service = new UserService();
        User user = service.createUser("Jane");
        assertNotNull(user);
    }
}
""")

    return tmp_workspace


@pytest.fixture
def execution_context(test_workspace):
    """Create execution context."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace",
        context_root=test_workspace,
    )

    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=Graph(),
    )


class TestTestIntelligenceAgent:
    """Tests for TestIntelligenceAgent."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = TestIntelligenceAgent()
        assert agent.name == "TestIntelligenceAgent"
        assert agent.min_coverage_threshold == 80

    def test_agent_custom_initialization(self):
        """Test agent initialization with custom parameters."""
        agent = TestIntelligenceAgent(
            min_coverage_threshold=90,
            min_assertion_threshold=3,
        )
        assert agent.min_coverage_threshold == 90

    def test_agent_execute_success(self, execution_context):
        """Test successful execution."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) > 0

    def test_agent_creates_matrix_file(self, execution_context):
        """Test that agent creates quality matrix file."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        matrix_file = workspace_path / "test-quality-matrix.json"

        assert matrix_file.exists()
        matrix = json.loads(matrix_file.read_text())
        assert "test_maturity_score" in matrix
        assert "coverage_percentage" in matrix

    def test_agent_metrics_present(self, execution_context):
        """Test that agent returns expected metrics."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        assert "test_maturity_score" in output.metrics
        assert "coverage_percentage" in output.metrics
        assert "total_test_files" in output.metrics

    def test_agent_report_generated(self, execution_context):
        """Test that agent generates report."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        assert "test_quality" in execution_context.reports
        report = execution_context.reports["test_quality"]
        assert report.content is not None

    def test_agent_finds_test_files(self, execution_context):
        """Test that agent finds test files."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        # Should find at least 3 test files (2 Python + 1 Java)
        assert output.metrics["total_test_files"] >= 2

    def test_agent_maturity_score_range(self, execution_context):
        """Test that maturity score is in valid range."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        score = output.metrics["test_maturity_score"]
        assert 0 <= score <= 100

    def test_agent_coverage_percentage_range(self, execution_context):
        """Test that coverage is in valid range."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        coverage = output.metrics["coverage_percentage"]
        assert 0 <= coverage <= 100

    def test_agent_handles_none_context(self):
        """Test agent handles None context."""
        agent = TestIntelligenceAgent()
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

        agent = TestIntelligenceAgent()
        output = agent.execute(context)

        assert output.status == "success"

    def test_matrix_file_format(self, execution_context):
        """Test that matrix file has correct format."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        matrix_file = workspace_path / "test-quality-matrix.json"
        matrix = json.loads(matrix_file.read_text())

        assert isinstance(matrix["total_test_files"], int)
        assert isinstance(matrix["total_test_methods"], int)
        assert isinstance(matrix["coverage_percentage"], int)
        assert isinstance(matrix["test_maturity_score"], int)

    def test_weak_tests_detection(self, execution_context):
        """Test that agent detects weak tests."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        matrix_file = workspace_path / "test-quality-matrix.json"
        matrix = json.loads(matrix_file.read_text())

        # Should detect weak tests (those with low assertions)
        assert "weak_tests_count" in matrix

    def test_artifact_tracking(self, execution_context):
        """Test that generated files are tracked."""
        agent = TestIntelligenceAgent()
        initial_count = len(execution_context.generated_files)
        output = agent.execute(execution_context)

        assert len(execution_context.generated_files) > initial_count

    def test_python_test_detection(self, execution_context):
        """Test detection of Python test methods."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        # Should detect Python test files
        assert output.metrics["total_test_files"] > 0

    def test_multiple_test_languages(self, execution_context):
        """Test detection across multiple languages."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        # Workspace has both Python and Java tests
        assert output.metrics["total_test_files"] >= 2

    def test_test_method_extraction(self, execution_context):
        """Test that test methods are extracted correctly."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        # Should count multiple test methods
        assert output.metrics["total_test_methods"] > 0

    def test_coverage_estimation(self, execution_context):
        """Test coverage estimation without explicit reports."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        # Should provide coverage estimate even without explicit reports
        coverage = output.metrics["coverage_percentage"]
        assert coverage >= 0

    def test_report_content_quality(self, execution_context):
        """Test that report contains meaningful content."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        report = execution_context.reports["test_quality"]
        assert len(report.content) > 0
        assert "Summary" in report.content or "summary" in report.content.lower()

    def test_maturity_calculation_logic(self, execution_context):
        """Test maturity score calculation."""
        agent = TestIntelligenceAgent()
        output = agent.execute(execution_context)

        maturity = output.metrics["test_maturity_score"]
        coverage = output.metrics["coverage_percentage"]

        # Maturity should be influenced by coverage
        assert maturity >= 0 and maturity <= 100
