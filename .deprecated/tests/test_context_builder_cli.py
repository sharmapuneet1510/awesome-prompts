"""Tests for context builder CLI commands."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from context_builder.cli import app


runner = CliRunner()


class TestCLIInit:
    """Tests for context-builder init command."""

    def test_init_creates_context_directory(self):
        """Test that init creates .context directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, ["init", "--path", tmpdir])

            assert result.exit_code == 0
            assert "Initialized context" in result.stdout
            assert (Path(tmpdir) / ".context").exists()

    def test_init_creates_agents_subdirectory(self):
        """Test that init creates .context/agents directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            agents_dir = Path(tmpdir) / ".context" / "agents"
            assert agents_dir.exists()

    def test_init_creates_reports_subdirectory(self):
        """Test that init creates .context/reports directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            reports_dir = Path(tmpdir) / ".context" / "reports"
            assert reports_dir.exists()

    def test_init_with_context_path(self):
        """Test init when passed .context path directly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_path = Path(tmpdir) / ".context"
            context_path.mkdir()

            result = runner.invoke(app, ["init", "--path", str(context_path)])

            assert result.exit_code == 0
            assert "Initialized context" in result.stdout

    def test_init_idempotent(self):
        """Test that init can be run multiple times safely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First run
            result1 = runner.invoke(app, ["init", "--path", tmpdir])
            assert result1.exit_code == 0

            # Second run
            result2 = runner.invoke(app, ["init", "--path", tmpdir])
            assert result2.exit_code == 0

    def test_init_defaults_to_current_directory(self):
        """Test that init defaults to current directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory and run without --path
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = runner.invoke(app, ["init"])
                assert result.exit_code == 0
                assert (Path(tmpdir) / ".context").exists()
            finally:
                os.chdir(old_cwd)


class TestCLIBuildContext:
    """Tests for context-builder build-context command."""

    def test_build_context_requires_initialized_directory(self):
        """Test that build-context fails without initialized .context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, ["build-context", "--path", tmpdir])

            assert result.exit_code == 1
            output = result.stdout + (result.stderr or "")
            assert "not found" in output

    def test_build_context_succeeds_after_init(self):
        """Test build-context after initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize first
            runner.invoke(app, ["init", "--path", tmpdir])

            # Mock the orchestrator
            with patch("context_builder.cli.Orchestrator") as mock_orch_class:
                mock_orch = MagicMock()
                mock_orch.build_context.return_value = True
                mock_orch.get_maturity_score.return_value = 82
                mock_orch.get_generated_files.return_value = [
                    Path("/tmp/file1.md"),
                    Path("/tmp/file2.json"),
                ]
                mock_orch.context.iteration = 1
                mock_orch.max_iterations = 5
                mock_orch_class.return_value = mock_orch

                result = runner.invoke(app, ["build-context", "--path", tmpdir])

                assert result.exit_code == 0
                assert "COMPLETE" in result.stdout
                assert "82/100" in result.stdout

    def test_build_context_without_until_mature_flag(self):
        """Test build-context without --until-mature flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            with patch("context_builder.cli.Orchestrator") as mock_orch_class:
                mock_orch = MagicMock()
                mock_orch.build_context.return_value = True
                mock_orch.get_maturity_score.return_value = 75
                mock_orch.get_generated_files.return_value = []
                mock_orch.context.iteration = 1
                mock_orch.max_iterations = 5
                mock_orch_class.return_value = mock_orch

                result = runner.invoke(app, ["build-context", "--path", tmpdir])

                assert result.exit_code == 0
                # until_mature should default to False
                mock_orch.build_context.assert_called_with(until_mature=False)

    def test_build_context_with_until_mature_flag(self):
        """Test build-context with --until-mature flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            with patch("context_builder.cli.Orchestrator") as mock_orch_class:
                mock_orch = MagicMock()
                mock_orch.build_context.return_value = True
                mock_orch.get_maturity_score.return_value = 82
                mock_orch.get_generated_files.return_value = []
                mock_orch.context.iteration = 2
                mock_orch.max_iterations = 5
                mock_orch_class.return_value = mock_orch

                result = runner.invoke(app, ["build-context", "--path", tmpdir, "--until-mature"])

                assert result.exit_code == 0
                # until_mature should be True
                mock_orch.build_context.assert_called_with(until_mature=True)

    def test_build_context_handles_failure(self):
        """Test build-context handles orchestrator failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            with patch("context_builder.cli.Orchestrator") as mock_orch_class:
                mock_orch = MagicMock()
                mock_orch.build_context.return_value = False  # Failure
                mock_orch.context = MagicMock()
                mock_orch.context.iteration = 1
                mock_orch_class.return_value = mock_orch

                result = runner.invoke(app, ["build-context", "--path", tmpdir])

                assert result.exit_code == 1
                output = result.stdout + (result.stderr or "")
                assert "FAILED" in output

    def test_build_context_reports_artifacts(self):
        """Test that build-context reports generated artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            with patch("context_builder.cli.Orchestrator") as mock_orch_class:
                mock_orch = MagicMock()
                mock_orch.build_context.return_value = True
                mock_orch.get_maturity_score.return_value = 80
                mock_orch.get_generated_files.return_value = [
                    Path("/tmp/file1.md"),
                    Path("/tmp/file2.json"),
                    Path("/tmp/file3.html"),
                ]
                mock_orch.context.iteration = 1
                mock_orch.max_iterations = 5
                mock_orch_class.return_value = mock_orch

                result = runner.invoke(app, ["build-context", "--path", tmpdir])

                assert result.exit_code == 0
                assert "Generated files: 3" in result.stdout


class TestCLIAsk:
    """Tests for context-builder ask command."""

    def test_ask_requires_initialized_context(self):
        """Test that ask fails without initialized .context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, ["ask", "What is the purpose?", "--path", tmpdir])

            assert result.exit_code == 1
            output = result.stdout + (result.stderr or "")
            assert "not found" in output

    def test_ask_requires_built_context(self):
        """Test that ask fails without built context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            result = runner.invoke(app, ["ask", "What is the purpose?", "--path", tmpdir])

            assert result.exit_code == 1
            output = result.stdout + (result.stderr or "")
            assert "context.json not found" in output

    def test_ask_with_valid_context(self):
        """Test ask command with valid context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            runner.invoke(app, ["init", "--path", tmpdir])

            # Create context.json
            (context_root / "context.json").write_text('{"nodes": []}')

            result = runner.invoke(app, ["ask", "What is the purpose?", "--path", tmpdir])

            assert result.exit_code == 0
            assert "Question Analysis" in result.stdout

    def test_ask_with_default_path(self):
        """Test ask command with default path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            runner.invoke(app, ["init", "--path", tmpdir])

            # Create context.json
            (context_root / "context.json").write_text('{"nodes": []}')

            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = runner.invoke(app, ["ask", "Test question?"])
                assert result.exit_code == 0
            finally:
                os.chdir(old_cwd)


class TestCLIStatus:
    """Tests for context-builder status command."""

    def test_status_uninitialized_context(self):
        """Test status for uninitialized context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, ["status", "--path", tmpdir])

            assert result.exit_code == 0
            assert "NOT INITIALIZED" in result.stdout

    def test_status_initialized_context(self):
        """Test status for initialized context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            result = runner.invoke(app, ["status", "--path", tmpdir])

            assert result.exit_code == 0
            assert "INITIALIZED" in result.stdout
            assert "Artifacts:" in result.stdout

    def test_status_shows_missing_artifacts(self):
        """Test that status shows missing artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            result = runner.invoke(app, ["status", "--path", tmpdir])

            assert result.exit_code == 0
            # Should show X marks for missing artifacts
            assert "✗" in result.stdout

    def test_status_shows_present_artifacts(self):
        """Test that status shows present artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            runner.invoke(app, ["init", "--path", tmpdir])

            # Create some artifacts
            (context_root / "context.json").write_text('{}')
            (context_root / "architecture.md").write_text('# Architecture')

            result = runner.invoke(app, ["status", "--path", tmpdir])

            assert result.exit_code == 0
            assert "✓" in result.stdout

    def test_status_shows_reports(self):
        """Test that status shows available reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            runner.invoke(app, ["init", "--path", tmpdir])

            # Create some reports
            reports_dir = context_root / "reports"
            (reports_dir / "analysis.md").write_text('# Analysis')
            (reports_dir / "metrics.json").write_text('{}')

            result = runner.invoke(app, ["status", "--path", tmpdir])

            assert result.exit_code == 0
            assert "Reports:" in result.stdout

    def test_status_shows_agents(self):
        """Test that status shows available agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"
            runner.invoke(app, ["init", "--path", tmpdir])

            # Create some agent definitions
            agents_dir = context_root / "agents"
            (agents_dir / "impl_agent.md").write_text('# Agent')

            result = runner.invoke(app, ["status", "--path", tmpdir])

            assert result.exit_code == 0
            assert "Agents:" in result.stdout

    def test_status_with_default_path(self):
        """Test status command with default path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = runner.invoke(app, ["status"])
                assert result.exit_code == 0
                assert "INITIALIZED" in result.stdout
            finally:
                os.chdir(old_cwd)


class TestCLIIntegration:
    """Integration tests for CLI workflows."""

    def test_full_workflow_init_then_status(self):
        """Test full workflow: init -> status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Init
            result1 = runner.invoke(app, ["init", "--path", tmpdir])
            assert result1.exit_code == 0

            # Step 2: Status
            result2 = runner.invoke(app, ["status", "--path", tmpdir])
            assert result2.exit_code == 0
            assert "INITIALIZED" in result2.stdout

    def test_full_workflow_with_context_json(self):
        """Test workflow with built context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_root = Path(tmpdir) / ".context"

            # Step 1: Init
            runner.invoke(app, ["init", "--path", tmpdir])

            # Step 2: Create context.json
            (context_root / "context.json").write_text('{"nodes": [], "edges": []}')

            # Step 3: Status
            result = runner.invoke(app, ["status", "--path", tmpdir])
            assert result.exit_code == 0
            assert "✓ context.json" in result.stdout

            # Step 4: Ask
            result = runner.invoke(app, ["ask", "Test question?", "--path", tmpdir])
            assert result.exit_code == 0

    def test_cli_help_messages(self):
        """Test that CLI commands have help messages."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize .context folder" in result.stdout

        result = runner.invoke(app, ["build-context", "--help"])
        assert result.exit_code == 0
        assert "Build complete project context" in result.stdout

        result = runner.invoke(app, ["ask", "--help"])
        assert result.exit_code == 0
        assert "Ask a question" in result.stdout

        result = runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0
        assert "Show context build status" in result.stdout


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_init_handles_permission_error(self):
        """Test that init handles permission errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to init in a read-only directory (simulate by using /dev/null)
            result = runner.invoke(app, ["init", "--path", "/dev/null"])
            assert result.exit_code == 1
            assert "Error" in result.stdout or "Error" in result.stderr

    def test_build_context_handles_missing_configs(self):
        """Test build-context with missing config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, ["init", "--path", tmpdir])

            with patch("context_builder.cli.Orchestrator") as mock_orch_class:
                # Simulate orchestrator returning False
                mock_orch = MagicMock()
                mock_orch.build_context.return_value = False
                mock_orch_class.return_value = mock_orch

                result = runner.invoke(app, ["build-context", "--path", tmpdir])

                assert result.exit_code == 1

    def test_ask_with_invalid_context_path(self):
        """Test ask with invalid context path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Don't initialize
            result = runner.invoke(app, ["ask", "Question?", "--path", tmpdir])
            assert result.exit_code == 1
