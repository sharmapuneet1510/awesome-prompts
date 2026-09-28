"""Tests for Orchestrator class."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from context_builder.models import ExecutionContext, Graph, AgentOutput
from context_builder.orchestrator import Orchestrator


class TestOrchestratorInitialization:
    """Tests for Orchestrator initialization."""

    def test_init_with_context_root(self):
        """Test Orchestrator initialization with .context path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            assert orchestrator.context_root == context_root
            assert orchestrator.config_loader is not None
            assert orchestrator.logger is not None

    def test_init_with_project_root(self):
        """Test Orchestrator initialization with project root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            context_root = project_root / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(project_root)

            assert orchestrator.context_root == context_root

    def test_init_resolves_context_path(self):
        """Test that Orchestrator resolves .context path correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            context_root = project_root / ".context"
            context_root.mkdir()

            # Pass project root, should resolve to .context
            orchestrator = Orchestrator(project_root)
            assert orchestrator.context_root == context_root

            # Pass .context directly
            orchestrator2 = Orchestrator(context_root)
            assert orchestrator2.context_root == context_root

    def test_init_registers_target_maturity(self):
        """Test that target maturity is set correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            assert orchestrator.target_maturity == 80  # default
            assert orchestrator.max_iterations == 5    # default


class TestOrchestratorLoadConfigs:
    """Tests for configuration loading."""

    def test_load_configs_with_missing_files(self):
        """Test loading configs when files don't exist (should use defaults)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()

            assert "workspace" in configs
            assert "project" in configs
            assert "scan" in configs
            assert "maturity" in configs
            assert "test_quality" in configs

    def test_load_configs_returns_dict(self):
        """Test that load_configs returns dictionary with expected keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()

            expected_keys = {"workspace", "project", "tech_aliases", "scan", "maturity", "test_quality"}
            assert all(key in configs for key in expected_keys)


class TestOrchestratorInitializeContext:
    """Tests for ExecutionContext initialization."""

    def test_initialize_context_creates_valid_context(self):
        """Test that _initialize_context creates valid ExecutionContext."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()

            context = orchestrator._initialize_context(configs)

            assert isinstance(context, ExecutionContext)
            assert context.graph is not None
            assert context.reports == {}
            assert context.generated_files == []
            assert context.iteration == 0

    def test_initialize_context_sets_maturity_target(self):
        """Test that maturity target is set from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()

            context = orchestrator._initialize_context(configs)

            assert context.maturity_config is not None
            assert context.maturity_config.target_score == 80

    def test_initialize_context_with_workspace_config(self):
        """Test that workspace config is properly initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = {
                "workspace": {"id": "test", "name": "Test Workspace", "description": "Test"},
                "project": {},
                "tech_aliases": {},
                "scan": {},
                "maturity": {},
                "test_quality": {},
            }

            context = orchestrator._initialize_context(configs)

            assert context.workspace_config is not None
            assert context.workspace_config.id == "test"
            assert context.workspace_config.name == "Test Workspace"


class TestOrchestratorAgentRegistration:
    """Tests for agent registration."""

    def test_register_agents_adds_all_agents(self):
        """Test that _register_agents registers all 10 agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            orchestrator._register_agents()

            # Should register 10 agents
            assert len(orchestrator.agents) == 10
            assert orchestrator.agent_registry.has("ProjectDefinitionAgent")
            assert orchestrator.agent_registry.has("RepoScannerAgent")
            assert orchestrator.agent_registry.has("CodeGraphAgent")
            assert orchestrator.agent_registry.has("FlowAnalysisAgent")
            assert orchestrator.agent_registry.has("C4DiagramAgent")
            assert orchestrator.agent_registry.has("HTMLSiteAgent")
            assert orchestrator.agent_registry.has("RAGAgent")
            assert orchestrator.agent_registry.has("TestIntelligenceAgent")
            assert orchestrator.agent_registry.has("TechnicalDebtAgent")
            assert orchestrator.agent_registry.has("MaturityAgent")

    def test_register_agents_maintains_order(self):
        """Test that agents are registered in correct execution order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            orchestrator._register_agents()

            expected_order = [
                "ProjectDefinitionAgent",
                "RepoScannerAgent",
                "CodeGraphAgent",
                "FlowAnalysisAgent",
                "C4DiagramAgent",
                "HTMLSiteAgent",
                "RAGAgent",
                "TestIntelligenceAgent",
                "TechnicalDebtAgent",
                "MaturityAgent",
            ]

            actual_order = [agent.name for agent in orchestrator.agents]
            assert actual_order == expected_order


class TestOrchestratorMaturityGate:
    """Tests for maturity gate checking."""

    def test_check_maturity_gate_passes_when_score_meets_target(self):
        """Test maturity gate passes when score >= target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Mock maturity report
            from context_builder.models import Report
            orchestrator.context.reports["maturityagent"] = Report(
                name="MaturityAgent",
                content="Test",
                metrics={"overall_score": 85}
            )

            result = orchestrator._check_maturity_gate()
            assert result is True

    def test_check_maturity_gate_fails_when_score_below_target(self):
        """Test maturity gate fails when score < target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Mock maturity report with low score
            from context_builder.models import Report
            orchestrator.context.reports["maturityagent"] = Report(
                name="MaturityAgent",
                content="Test",
                metrics={"overall_score": 70}
            )

            result = orchestrator._check_maturity_gate()
            assert result is False

    def test_check_maturity_gate_handles_missing_report(self):
        """Test maturity gate when maturity report is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Don't add maturity report
            result = orchestrator._check_maturity_gate()
            assert result is False


class TestOrchestratorExecuteAgents:
    """Tests for agent execution."""

    @patch("context_builder.orchestrator.ProjectDefinitionAgent")
    def test_execute_agents_runs_all_agents(self, mock_agent_class):
        """Test that execute_agents runs all registered agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Mock all agents to return success
            orchestrator.agents = [
                Mock(name=f"Agent{i}", execute=Mock(return_value=AgentOutput(status="success", message="OK")))
                for i in range(10)
            ]

            result = orchestrator._execute_agents(from_step=1)

            assert result is True
            for agent in orchestrator.agents:
                agent.execute.assert_called()

    def test_execute_agents_stops_on_critical_error(self):
        """Test that critical agent failures halt orchestration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # First agent is critical, fails
            critical_agent = MagicMock()
            critical_agent.name = "ProjectDefinitionAgent"
            critical_agent.execute.return_value = AgentOutput(status="error", message="Failed", errors=[])

            orchestrator.agents = [critical_agent] + [
                MagicMock(
                    name=f"Agent{i}",
                    execute=Mock(return_value=AgentOutput(status="success", message="OK", errors=[]))
                )
                for i in range(1, 10)
            ]

            result = orchestrator._execute_agents(from_step=1)

            assert result is False
            critical_agent.execute.assert_called()

    def test_execute_agents_continues_on_non_critical_error(self):
        """Test that non-critical agent failures don't halt orchestration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Non-critical agent fails
            non_critical_agent = Mock(
                name="RAGAgent",
                execute=Mock(return_value=AgentOutput(status="error", message="Failed"))
            )
            success_agents = [
                Mock(name=f"Agent{i}", execute=Mock(return_value=AgentOutput(status="success", message="OK")))
                for i in range(9)
            ]
            # Insert non-critical agent at position 6 (RAGAgent)
            orchestrator.agents = success_agents[:6] + [non_critical_agent] + success_agents[6:]

            result = orchestrator._execute_agents(from_step=1)

            assert result is True

    def test_execute_agents_from_specific_step(self):
        """Test that execute_agents can start from a specific step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Mock agents
            orchestrator.agents = [
                Mock(name=f"Agent{i}", execute=Mock(return_value=AgentOutput(status="success", message="OK")))
                for i in range(10)
            ]

            # Execute from step 4 (should skip first 3)
            orchestrator._execute_agents(from_step=4)

            # First 3 agents should NOT be called
            assert not orchestrator.agents[0].execute.called
            assert not orchestrator.agents[1].execute.called
            assert not orchestrator.agents[2].execute.called

            # Agents from step 4 onward SHOULD be called
            for agent in orchestrator.agents[3:]:
                agent.execute.assert_called()


class TestOrchestratorBuildContext:
    """Tests for build_context orchestration."""

    def test_build_context_without_maturity_iteration(self):
        """Test build_context without until_mature flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            with patch.object(orchestrator, "_execute_agents", return_value=True):
                with patch.object(orchestrator, "_generate_final_report"):
                    result = orchestrator.build_context(until_mature=False)

            assert result is True

    def test_build_context_with_maturity_iteration(self):
        """Test build_context with until_mature flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            with patch.object(orchestrator, "_execute_agents", return_value=True):
                with patch.object(orchestrator, "_check_maturity_gate", side_effect=[False, False, True]):
                    with patch.object(orchestrator, "_generate_final_report"):
                        result = orchestrator.build_context(until_mature=True)

            assert result is True

    def test_build_context_handles_execution_failure(self):
        """Test build_context handles agent execution failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            with patch.object(orchestrator, "_execute_agents", return_value=False):
                with patch.object(orchestrator, "_generate_final_report") as mock_report:
                    result = orchestrator.build_context(until_mature=False)

            assert result is False
            mock_report.assert_not_called()

    def test_build_context_respects_max_iterations(self):
        """Test that build_context respects max_iterations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            # Create a custom config with max_iterations=2
            configs = orchestrator._load_configs()
            configs["maturity"]["max_iterations"] = 2
            orchestrator.context = orchestrator._initialize_context(configs)

            with patch.object(orchestrator, "_execute_agents", return_value=True):
                with patch.object(orchestrator, "_check_maturity_gate", return_value=False):
                    with patch.object(orchestrator, "_generate_final_report"):
                        result = orchestrator.build_context(until_mature=True)

            assert result is True


class TestOrchestratorGetMethods:
    """Tests for getter methods."""

    def test_get_context_returns_none_before_build(self):
        """Test get_context returns None before build."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            assert orchestrator.get_context() is None

    def test_get_context_returns_context_after_init(self):
        """Test get_context returns context after initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            context = orchestrator.get_context()

            assert context is not None
            assert isinstance(context, ExecutionContext)

    def test_get_generated_files_empty_before_build(self):
        """Test get_generated_files returns empty list before build."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            files = orchestrator.get_generated_files()

            assert files == []

    def test_get_generated_files_after_init(self):
        """Test get_generated_files returns list after context init."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Add some generated files
            orchestrator.context.generated_files = [Path("/tmp/file1.md"), Path("/tmp/file2.json")]

            files = orchestrator.get_generated_files()

            assert len(files) == 2

    def test_get_maturity_score_zero_before_build(self):
        """Test get_maturity_score returns 0 before build."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)

            score = orchestrator.get_maturity_score()

            assert score == 0

    def test_get_maturity_score_from_context(self):
        """Test get_maturity_score returns score from context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            context_root.mkdir()

            orchestrator = Orchestrator(context_root)
            configs = orchestrator._load_configs()
            orchestrator.context = orchestrator._initialize_context(configs)

            # Add maturity report
            from context_builder.models import Report
            orchestrator.context.reports["maturityagent"] = Report(
                name="MaturityAgent",
                content="Test",
                metrics={"overall_score": 75}
            )

            score = orchestrator.get_maturity_score()

            assert score == 75
