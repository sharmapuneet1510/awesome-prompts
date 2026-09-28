"""Test orchestrator_bridge.py for full build → context → PR chain."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.orchestrator.orchestrator_bridge import invoke_build_and_context_chain


class TestOrchestratorBridge:
    """Test orchestrator bridge for coordinating build → context → pr chain."""

    def test_build_and_context_chain_success(self):
        """When build and context both succeed, dual commits and PR should be created."""

        # Mock orchestrator with both results
        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": {
                "status": "success",
                "artifacts": ["src/main.py", "tests/test_main.py"]
            },
            "context_result": {
                "status": "success",
                "artifacts": ["docs/architecture.md", "docs/tech-stack.md"]
            },
            "build_status": "success",
            "context_status": "success"
        }

        mock_orchestrator.pr.return_value = {
            "pr_url": "https://github.com/org/repo/pull/42",
            "pr_number": 42
        }

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_dual_commit:
            mock_dual_commit.return_value = ["abc1234", "def5678"]

            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

        # Verify dual commit was called
        mock_dual_commit.assert_called_once()
        assert result["status"] == "success"
        assert result["commits"] == ["abc1234", "def5678"]
        assert result["pr_url"] == "https://github.com/org/repo/pull/42"
        assert result["pr_number"] == 42

    def test_build_success_context_fails_single_commit(self):
        """When build succeeds but context fails, single commit should be created."""

        # Mock orchestrator with partial success
        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "partial_success",
            "build_result": {
                "status": "success",
                "artifacts": ["src/main.py", "tests/test_main.py"]
            },
            "build_status": "success",
            "context_status": "failed",
            "context_error": "Context generation failed"
        }

        mock_orchestrator.pr.return_value = {
            "pr_url": "https://github.com/org/repo/pull/41",
            "pr_number": 41
        }

        with patch('tools.orchestrator.orchestrator_bridge.single_commit') as mock_single:
            mock_single.return_value = "abc1234"

            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

        # Verify single commit was called (no context_artifacts)
        mock_single.assert_called_once()
        assert result["status"] == "success"
        assert result["commits"] == ["abc1234"]
        assert result["pr_url"] == "https://github.com/org/repo/pull/41"

    def test_build_fails_chain_stops(self):
        """When build fails, chain should stop immediately without commit."""

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "failed",
            "error": "Build generation failed"
        }

        result = invoke_build_and_context_chain(
            orchestrator=mock_orchestrator,
            requirements_path="requirements.md"
        )

        # Chain should stop, no commits
        assert result["status"] == "failed"
        assert "error" in result

    def test_no_artifacts_error(self):
        """When neither code nor context artifacts exist, error should be returned."""

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": {
                "status": "success",
                "artifacts": []  # No artifacts
            },
            "context_result": {},
            "build_status": "success"
        }

        result = invoke_build_and_context_chain(
            orchestrator=mock_orchestrator,
            requirements_path="requirements.md"
        )

        assert result["status"] == "error"
        assert "No artifacts to commit" in result["error"]

    def test_commit_failure_returns_error(self):
        """When commit fails, error should be returned with helpful message."""

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": {
                "status": "success",
                "artifacts": ["src/main.py"]
            },
            "context_result": {
                "status": "success",
                "artifacts": ["docs/arch.md"]
            },
            "build_status": "success",
            "context_status": "success"
        }

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_dual:
            mock_dual.side_effect = Exception("Git error: detached HEAD")

            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

        assert result["status"] == "error"
        assert "Commit failed" in result["error"]
        assert "Git error: detached HEAD" in result["details"]
        assert "please commit manually" in result["note"]

    def test_pr_creation_failure_commits_preserved(self):
        """When PR creation fails, commits should still be preserved."""

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": {
                "status": "success",
                "artifacts": ["src/main.py"]
            },
            "context_result": {
                "status": "success",
                "artifacts": ["docs/arch.md"]
            },
            "build_status": "success",
            "context_status": "success"
        }

        mock_orchestrator.pr.side_effect = Exception("GitHub API error")

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_dual:
            mock_dual.return_value = ["abc1234", "def5678"]

            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

        assert result["status"] == "pr_creation_failed"
        assert result["commits"] == ["abc1234", "def5678"]
        assert "PR creation failed" in result["error"]
        assert "create PR manually" in result["note"]

    def test_orchestrator_called_with_correct_args(self):
        """Verify orchestrator.build is called with all provided arguments."""

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "failed",
            "error": "Not important"
        }

        invoke_build_and_context_chain(
            orchestrator=mock_orchestrator,
            requirements_path="my_requirements.md",
            context="Business context here",
            tech_stack="Python/FastAPI"
        )

        # Verify build was called with all arguments
        mock_orchestrator.build.assert_called_once_with(
            requirements_path="my_requirements.md",
            context="Business context here",
            tech_stack="Python/FastAPI"
        )
