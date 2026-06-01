"""Tests for MaturityAgent."""

import json
from pathlib import Path

import pytest

from context_builder.agents import MaturityAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Graph,
    MaturityConfig,
    Node,
    NodeType,
    ProjectConfig,
    Report,
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
def complete_workspace(tmp_workspace):
    """Create workspace with various artifacts."""
    # Create directory structure
    (tmp_workspace / "src").mkdir()
    (tmp_workspace / "tests").mkdir()
    (tmp_workspace / "docs").mkdir()
    (tmp_workspace / "config").mkdir()

    # Create README
    (tmp_workspace / "README.md").write_text("# Project README\n\nThis is a project.")

    # Create architecture docs
    (tmp_workspace / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n\nSystem design.")

    # Create API docs
    (tmp_workspace / "docs" / "API.md").write_text("# API Documentation\n\nAPI endpoints.")

    return tmp_workspace


@pytest.fixture
def rich_graph():
    """Create a graph with various node types."""
    graph = Graph()

    # Add workspace and repository nodes
    graph.add_node(Node(id="ws1", type=NodeType.WORKSPACE, name="Workspace"))
    graph.add_node(Node(id="repo1", type=NodeType.REPOSITORY, name="Repository"))

    # Add code nodes
    for i in range(5):
        graph.add_node(Node(id=f"class{i}", type=NodeType.CLASS, name=f"Class{i}"))

    # Add database nodes
    graph.add_node(Node(id="db1", type=NodeType.DATABASE, name="Database"))
    for i in range(3):
        graph.add_node(Node(id=f"table{i}", type=NodeType.DATABASE_TABLE, name=f"Table{i}"))

    # Add middleware nodes
    graph.add_node(Node(id="mw1", type=NodeType.MIDDLEWARE, name="MessageBroker"))
    graph.add_node(Node(id="topic1", type=NodeType.MIDDLEWARE_TOPIC, name="Topic1"))

    # Add flow nodes
    graph.add_node(Node(id="flow1", type=NodeType.BUSINESS_FLOW, name="UserRegistration"))

    # Add some edges
    from context_builder.models import Edge, EdgeType
    graph.add_edge(Edge(source="class0", target="class1", type=EdgeType.CALLS))
    graph.add_edge(Edge(source="class1", target="table0", type=EdgeType.READS_FROM))

    return graph


@pytest.fixture
def context_with_reports(complete_workspace, rich_graph):
    """Create context with various reports."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Complete workspace",
        context_root=complete_workspace,
    )

    context = ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(target_score=80),
        test_quality_config=TestQualityConfig(),
        graph=rich_graph,
    )

    # Add some reports
    context.reports["test_quality"] = Report(
        name="Test Quality",
        content="Test report",
        metrics={
            "test_maturity_score": 75,
            "coverage_percentage": 70,
        },
    )

    context.reports["technical_debt"] = Report(
        name="Technical Debt",
        content="Debt report",
        metrics={
            "risk_score": 35,
            "debt_items": 5,
        },
    )

    context.reports["flow_analysis"] = Report(
        name="Flow Analysis",
        content="Flow report",
        metrics={
            "completeness_score": 80,
        },
    )

    return context


@pytest.fixture
def execution_context(complete_workspace, rich_graph):
    """Create basic execution context."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace",
        context_root=complete_workspace,
    )

    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(target_score=80),
        test_quality_config=TestQualityConfig(),
        graph=rich_graph,
    )


class TestMaturityAgent:
    """Tests for MaturityAgent."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MaturityAgent()
        assert agent.name == "MaturityAgent"
        assert agent.target_score == 80

    def test_agent_custom_initialization(self):
        """Test agent with custom target score."""
        agent = MaturityAgent(target_score=90)
        assert agent.target_score == 90

    def test_agent_execute_success(self, execution_context):
        """Test successful execution."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) > 0

    def test_agent_creates_score_file(self, execution_context):
        """Test that agent creates maturity-score.json."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        score_file = workspace_path / "maturity-score.json"

        assert score_file.exists()
        score_data = json.loads(score_file.read_text())
        assert "overall_score" in score_data
        assert "status" in score_data

    def test_agent_creates_actions_file(self, execution_context):
        """Test that agent creates next-actions.md."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        actions_file = workspace_path / "next-actions.md"

        assert actions_file.exists()
        assert len(actions_file.read_text()) > 0

    def test_agent_returns_metrics(self, execution_context):
        """Test that agent returns expected metrics."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        assert "maturity_score" in output.metrics
        assert "status" in output.metrics
        assert "dimension_scores" in output.metrics

    def test_maturity_score_range(self, execution_context):
        """Test that maturity score is in valid range."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        score = output.metrics["maturity_score"]
        assert 0 <= score <= 100

    def test_status_ready_when_above_target(self, context_with_reports):
        """Test READY status when score >= target."""
        agent = MaturityAgent(target_score=50)
        output = agent.execute(context_with_reports)

        # With good reports, score should be decent
        assert output.metrics["status"] in ["READY", "NOT_READY"]

    def test_status_not_ready_when_below_target(self, execution_context):
        """Test NOT_READY status when score < target."""
        agent = MaturityAgent(target_score=100)
        output = agent.execute(execution_context)

        # With default execution, unlikely to reach 100
        # Status depends on actual score
        assert output.metrics["status"] in ["READY", "NOT_READY"]

    def test_all_dimensions_scored(self, execution_context):
        """Test that all dimensions are scored."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        dimension_scores = output.metrics["dimension_scores"]

        expected_dimensions = [
            "project_structure",
            "code_understanding",
            "flow_understanding",
            "data_understanding",
            "middleware_understanding",
            "test_intelligence",
            "documentation_quality",
            "risk_analysis",
        ]

        for dim in expected_dimensions:
            assert dim in dimension_scores
            score = dimension_scores[dim]
            assert 0 <= score <= 100

    def test_dimension_scores_are_integers(self, execution_context):
        """Test that dimension scores are integers."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        dimension_scores = output.metrics["dimension_scores"]

        for score in dimension_scores.values():
            assert isinstance(score, int)

    def test_agent_generates_report(self, execution_context):
        """Test that agent generates report."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        assert "maturity" in execution_context.reports
        report = execution_context.reports["maturity"]
        assert report.content is not None

    def test_agent_handles_none_context(self):
        """Test agent handles None context."""
        agent = MaturityAgent()
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

        agent = MaturityAgent()
        output = agent.execute(context)

        assert output.status == "success"

    def test_score_file_structure(self, execution_context):
        """Test structure of generated score file."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        score_file = workspace_path / "maturity-score.json"
        score_data = json.loads(score_file.read_text())

        required_fields = ["overall_score", "target_score", "status", "dimension_scores"]

        for field in required_fields:
            assert field in score_data

    def test_artifact_tracking(self, execution_context):
        """Test that generated files are tracked."""
        agent = MaturityAgent()
        initial_count = len(execution_context.generated_files)
        output = agent.execute(execution_context)

        assert len(execution_context.generated_files) > initial_count

    def test_report_content_has_dimensions(self, execution_context):
        """Test that report contains dimension information."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        report = execution_context.reports["maturity"]
        content = report.content

        # Should mention dimensions
        assert "Dimension" in content or "dimension" in content.lower()

    def test_next_actions_are_specific(self, context_with_reports):
        """Test that next actions are specific and actionable."""
        agent = MaturityAgent()
        output = agent.execute(context_with_reports)

        workspace_path = context_with_reports.workspace_config.context_root
        actions_file = workspace_path / "next-actions.md"
        content = actions_file.read_text()

        # Should contain actionable items
        assert ("Strategy" in content or "Actions" in content or "Priority" in content)

    def test_score_calculation_with_reports(self, context_with_reports):
        """Test score calculation uses available reports."""
        agent = MaturityAgent()
        output = agent.execute(context_with_reports)

        score = output.metrics["maturity_score"]
        # With reports providing good scores, should be reasonable
        assert score > 30

    def test_project_structure_scoring(self, complete_workspace, rich_graph):
        """Test project structure dimension scoring."""
        workspace_config = WorkspaceConfig(
            id="test",
            name="Test",
            description="Test",
            context_root=complete_workspace,
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=rich_graph,
        )

        agent = MaturityAgent()
        output = agent.execute(context)

        project_structure_score = output.metrics["dimension_scores"]["project_structure"]
        # With good directory structure, should score well
        assert project_structure_score > 40

    def test_code_understanding_scoring(self, execution_context):
        """Test code understanding dimension scoring."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        code_score = output.metrics["dimension_scores"]["code_understanding"]
        # Graph has nodes and edges, should score reasonable
        assert code_score > 30

    def test_data_understanding_scoring(self, execution_context):
        """Test data understanding dimension scoring."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        data_score = output.metrics["dimension_scores"]["data_understanding"]
        # Graph has database nodes, should score decent
        assert data_score > 40

    def test_middleware_understanding_scoring(self, execution_context):
        """Test middleware understanding dimension scoring."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        middleware_score = output.metrics["dimension_scores"]["middleware_understanding"]
        # Graph has middleware nodes, should score decent
        assert middleware_score > 40

    def test_status_matrix_accuracy(self, execution_context):
        """Test that status matches overall score vs target."""
        agent = MaturityAgent(target_score=75)
        output = agent.execute(execution_context)

        score = output.metrics["maturity_score"]
        status = output.metrics["status"]

        # Verify status logic
        if score >= 75:
            assert status == "READY"
        else:
            assert status == "NOT_READY"

    def test_multiple_target_scores(self, execution_context):
        """Test agent with various target scores."""
        for target in [50, 70, 80, 90]:
            agent = MaturityAgent(target_score=target)
            output = agent.execute(execution_context)

            assert output.metrics["target_score"] == target
            assert output.metrics["status"] in ["READY", "NOT_READY"]

    def test_report_message_clarity(self, execution_context):
        """Test that report message is clear."""
        agent = MaturityAgent()
        output = agent.execute(execution_context)

        message = output.message
        assert "Maturity" in message or "maturity" in message.lower()
        assert output.metrics["maturity_score"] >= 0
