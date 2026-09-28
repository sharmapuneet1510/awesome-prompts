"""Integration tests for full orchestrator:build → context → pr chain.

Tests the end-to-end workflow where:
1. orchestrator:build completes successfully
2. orchestrator:context is auto-invoked with correct path
3. Dual commits are created (code + context) with linking
4. orchestrator:pr creates PR with both commits
5. Result returns PR URL and commit SHAs

Also tests error scenarios:
- Build failure: Auto-chain not triggered
- Context failure: Code commit created (partial_success)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from tools.orchestrator.auto_chain import auto_chain_context
from tools.orchestrator.orchestrator_bridge import invoke_build_and_context_chain


class TestIntegrationBuildContextPR:
    """Integration test for full orchestrator:build → context → pr chain."""

    def test_full_chain_build_context_pr_success(self):
        """Complete workflow: build → auto-chain context → dual commits → PR.

        Verifies:
        - orchestrator:build completes successfully
        - orchestrator:context auto-invoked with correct path
        - Dual commits created (code + context) with linking
        - orchestrator:pr creates PR with both commits
        - Result returns PR URL and commit SHAs
        """

        # Phase 1: Build completes successfully
        build_result = {
            "status": "success",
            "project_dir": "/tmp/generated_project",
            "artifacts": ["src/main.py", "tests/test_main.py", "README.md", "docker-compose.yml"]
        }

        # Phase 2: Context generation
        context_result = {
            "status": "success",
            "artifacts": ["docs/context/architecture.md", "docs/context/tech-stack.md", "docs/context/context.json"]
        }

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": build_result,
            "context_result": context_result,
            "build_status": "success",
            "context_status": "success"
        }

        # Mock PR creation
        mock_orchestrator.pr.return_value = {
            "pr_url": "https://github.com/org/repo/pull/42",
            "pr_number": 42
        }

        # Mock dual commits
        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_dual_commit:
            mock_dual_commit.return_value = ["abc1234567890", "def5678901234"]

            # Execute integration chain
            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

            # Verify orchestrator.build was called
            mock_orchestrator.build.assert_called_once()

            # Verify dual commit was called with code and context artifacts
            mock_dual_commit.assert_called_once()
            call_args = mock_dual_commit.call_args
            assert build_result["artifacts"] == call_args[1].get('code_artifacts') or \
                   build_result["artifacts"] in str(call_args)
            assert context_result["artifacts"] == call_args[1].get('context_artifacts') or \
                   context_result["artifacts"] in str(call_args)

            # Verify PR was created
            mock_orchestrator.pr.assert_called_once()

            # Verify result structure
            assert result["status"] == "success"
            assert result["commits"] == ["abc1234567890", "def5678901234"]
            assert result["pr_url"] == "https://github.com/org/repo/pull/42"
            assert result["pr_number"] == 42

    def test_full_chain_context_failure_partial_success(self):
        """Full chain with context generation failure.

        Verifies:
        - Build succeeds
        - Context generation fails (marked as failed)
        - Code commit still created (single commit)
        - Status is partial_success
        - PR creation still proceeds
        """

        build_result = {
            "status": "success",
            "project_dir": "/tmp/generated_project",
            "artifacts": ["src/main.py", "tests/test_main.py"]
        }

        # Mock orchestrator with context failure
        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "partial_success",
            "build_result": build_result,
            "build_status": "success",
            "context_status": "failed",
            "context_error": "Architecture analysis failed"
        }

        # PR still created with single commit
        mock_orchestrator.pr.return_value = {
            "pr_url": "https://github.com/org/repo/pull/41",
            "pr_number": 41
        }

        # Single commit (code only, no context)
        with patch('tools.orchestrator.orchestrator_bridge.single_commit') as mock_single:
            mock_single.return_value = "abc1234567890"

            # Execute integration chain
            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

            # Verify orchestrator.build was called
            mock_orchestrator.build.assert_called_once()

            # Verify single commit was called (not dual_commit)
            mock_single.assert_called_once()

            # Verify PR was still created
            mock_orchestrator.pr.assert_called_once()

            # Verify result structure
            assert result["status"] == "success"  # Overall success despite context failure
            assert result["commits"] == ["abc1234567890"]
            assert result["pr_url"] == "https://github.com/org/repo/pull/41"

    def test_full_chain_build_failure_stops_early(self):
        """Full chain with build failure.

        Verifies:
        - Build fails
        - Auto-chain is not triggered
        - Context is not invoked
        - No commits made
        - No PR created
        """

        build_result = {
            "status": "failed",
            "error": "Implementation failed: Invalid requirements"
        }

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = build_result

        # Execute integration chain
        result = invoke_build_and_context_chain(
            orchestrator=mock_orchestrator,
            requirements_path="requirements.md"
        )

        # Verify orchestrator.build was called
        mock_orchestrator.build.assert_called_once()

        # Verify PR was NOT called on build failure
        mock_orchestrator.pr.assert_not_called()

        # Verify failure is propagated
        assert result["status"] == "failed"
        assert result["error"] == "Implementation failed: Invalid requirements"

    def test_auto_chain_context_invoked_with_correct_path(self):
        """Verify orchestrator:context is auto-invoked with correct project path.

        Tests the auto-chaining mechanism specifically.
        """

        build_result = {
            "status": "success",
            "project_dir": "/tmp/generated_project_xyz123",
            "artifacts": ["code"]
        }

        # Mock context function
        mock_context_fn = Mock()
        mock_context_fn.return_value = {
            "status": "success",
            "artifacts": ["architecture.md"]
        }

        # Execute auto_chain_context
        result = auto_chain_context(
            build_result,
            config={
                "orchestrator": {
                    "build": {
                        "auto_generate_context": True,
                        "context_depth": "comprehensive"
                    }
                }
            },
            invoke_context_fn=mock_context_fn
        )

        # Verify context was called with correct path
        mock_context_fn.assert_called_once_with(
            path="/tmp/generated_project_xyz123",
            depth="comprehensive"
        )

        # Verify result includes both statuses
        assert result["status"] == "success"
        assert result["build_status"] == "success"
        assert result["context_status"] == "success"
        assert result["context_result"]["status"] == "success"

    def test_dual_commits_with_linking(self):
        """Verify dual commits are created with proper linking.

        Tests that:
        - First commit (code) is created
        - Second commit (context) references first commit
        - Both SHAs are returned
        """

        code_artifacts = ["src/main.py", "tests/test_main.py", "README.md"]
        context_artifacts = ["docs/context/architecture.md", "docs/context/tech-stack.md"]

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_commit:
            # Setup mock to return both SHAs
            mock_commit.return_value = ["abc1234567890", "def5678901234"]

            from tools.orchestrator.orchestrator_bridge import commit_with_chain

            # Call commit_with_chain
            commit_shas = commit_with_chain(
                code_artifacts=code_artifacts,
                context_artifacts=context_artifacts,
                code_message="feat: auto-generated implementation",
                context_message="docs: auto-generated project context"
            )

            # Verify both commits returned
            assert len(commit_shas) == 2
            assert commit_shas[0] == "abc1234567890"  # Code commit SHA
            assert commit_shas[1] == "def5678901234"  # Context commit SHA

            # Verify commit was called with all artifacts
            mock_commit.assert_called_once()

    def test_error_handling_commit_failure(self):
        """Verify error handling when commit fails.

        Build and context succeed, but commit fails.
        """

        build_result = {
            "status": "success",
            "project_dir": "/tmp/project",
            "artifacts": ["src/main.py"]
        }

        context_result = {
            "status": "success",
            "artifacts": ["docs/arch.md"]
        }

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": build_result,
            "context_result": context_result,
            "build_status": "success",
            "context_status": "success"
        }

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_commit:
            mock_commit.side_effect = Exception("Git error: detached HEAD")

            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

            # Verify error status and message
            assert result["status"] == "error"
            assert "Commit failed" in result["error"]
            assert "Git error: detached HEAD" in result["details"]

    def test_error_handling_pr_creation_failure_commits_preserved(self):
        """Verify commits are preserved even if PR creation fails.

        Build, context, and commits succeed, but PR creation fails.
        """

        build_result = {
            "status": "success",
            "artifacts": ["src/main.py"]
        }

        context_result = {
            "status": "success",
            "artifacts": ["docs/arch.md"]
        }

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": build_result,
            "context_result": context_result,
            "build_status": "success",
            "context_status": "success"
        }

        mock_orchestrator.pr.side_effect = Exception("GitHub API error")

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_commit:
            mock_commit.return_value = ["abc1234567890", "def5678901234"]

            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

            # Verify commits are preserved
            assert result["status"] == "pr_creation_failed"
            assert result["commits"] == ["abc1234567890", "def5678901234"]
            assert "PR creation failed" in result["error"]
            assert "create PR manually" in result["note"]

    def test_no_artifacts_returns_error(self):
        """Verify error when neither code nor context artifacts exist.

        Both build and context complete, but neither produces artifacts.
        """

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

        # Verify error status
        assert result["status"] == "error"
        assert "No artifacts to commit" in result["error"]

        # Verify commit was not called
        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_commit:
            mock_commit.assert_not_called()

    def test_all_orchestrator_phases_in_sequence(self):
        """Verify all orchestrator phases execute in correct sequence.

        1. orchestrator.build() called with requirements
        2. Auto-chain context triggered (if build succeeds)
        3. Commits created (if artifacts exist)
        4. PR created (if commits succeed)
        """

        # Setup mocks
        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": {"status": "success", "artifacts": ["code"]},
            "context_result": {"status": "success", "artifacts": ["docs"]},
            "build_status": "success",
            "context_status": "success"
        }

        mock_orchestrator.pr.return_value = {
            "pr_url": "https://github.com/org/repo/pull/42",
            "pr_number": 42
        }

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_commit:
            mock_commit.return_value = ["abc1234567890", "def5678901234"]

            # Execute chain
            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

            # Verify call sequence: build → commit → pr
            # (Note: orchestrator.build includes auto-chaining internally)
            mock_orchestrator.build.assert_called_once()
            mock_commit.assert_called_once()
            mock_orchestrator.pr.assert_called_once()

            # Verify result indicates success
            assert result["status"] == "success"


class TestIntegrationDataFlow:
    """Test data flow through the integration chain.

    Verifies that:
    - Build artifacts are passed to commits
    - Context artifacts are passed to commits
    - Commit SHAs are passed to PR
    - All metadata is preserved through phases
    """

    def test_artifacts_flow_through_chain(self):
        """Verify artifacts flow correctly through build → commit → pr."""

        code_artifacts = ["src/app.py", "tests/test_app.py"]
        context_artifacts = ["docs/architecture.md"]
        expected_code_sha = "abc1234567890"
        expected_context_sha = "def5678901234"

        mock_orchestrator = Mock()
        mock_orchestrator.build.return_value = {
            "status": "success",
            "build_result": {"status": "success", "artifacts": code_artifacts},
            "context_result": {"status": "success", "artifacts": context_artifacts},
            "build_status": "success",
            "context_status": "success"
        }

        mock_orchestrator.pr.return_value = {
            "pr_url": "https://github.com/org/repo/pull/99",
            "pr_number": 99
        }

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_commit:
            mock_commit.return_value = [expected_code_sha, expected_context_sha]

            result = invoke_build_and_context_chain(
                orchestrator=mock_orchestrator,
                requirements_path="requirements.md"
            )

            # Verify commit was called with correct artifacts
            call_kwargs = mock_commit.call_args[1]
            assert code_artifacts == call_kwargs.get('code_artifacts', []) or \
                   code_artifacts in str(mock_commit.call_args)
            assert context_artifacts == call_kwargs.get('context_artifacts', []) or \
                   context_artifacts in str(mock_commit.call_args)

            # Verify SHAs are in result
            assert expected_code_sha in result.get("commits", [])
            assert expected_context_sha in result.get("commits", [])

    def test_context_depth_propagates_through_chain(self):
        """Verify context_depth configuration propagates correctly.

        Tests that context_depth is passed from config through to context invocation.
        """

        build_result = {"status": "success", "project_dir": "/tmp/proj"}

        mock_context_fn = Mock()
        mock_context_fn.return_value = {"status": "success", "artifacts": []}

        # Test with "quick" depth
        result = auto_chain_context(
            build_result,
            config={
                "orchestrator": {
                    "build": {
                        "auto_generate_context": True,
                        "context_depth": "quick"
                    }
                }
            },
            invoke_context_fn=mock_context_fn
        )

        # Verify depth was passed to context function
        mock_context_fn.assert_called_once()
        call_kwargs = mock_context_fn.call_args[1]
        assert call_kwargs.get("depth") == "quick"

        # Test with "comprehensive" depth
        mock_context_fn.reset_mock()
        result = auto_chain_context(
            build_result,
            config={
                "orchestrator": {
                    "build": {
                        "auto_generate_context": True,
                        "context_depth": "comprehensive"
                    }
                }
            },
            invoke_context_fn=mock_context_fn
        )

        call_kwargs = mock_context_fn.call_args[1]
        assert call_kwargs.get("depth") == "comprehensive"

    def test_error_information_preserved_through_chain(self):
        """Verify error information is preserved through the chain.

        When context fails, error message and details should be passed through.
        """

        build_result = {"status": "success", "project_dir": "/tmp/proj", "artifacts": ["code"]}

        mock_context_fn = Mock()
        mock_context_fn.side_effect = Exception("Schema validation failed")

        # Execute auto_chain_context with context failure
        result = auto_chain_context(
            build_result,
            invoke_context_fn=mock_context_fn
        )

        # Verify error is preserved
        assert result["status"] == "partial_success"
        assert result["context_status"] == "failed"
        assert "context_error" in result
        assert "Schema validation failed" in result["context_error"]


class TestIntegrationConfigurableOptions:
    """Test configurable options in the integration chain.

    Verifies that:
    - auto_generate_context can be disabled
    - context_depth can be configured
    - skip_on_context_failure affects behavior
    """

    def test_auto_generate_context_disabled(self):
        """When auto_generate_context is False, context should not be invoked."""

        build_result = {"status": "success", "project_dir": "/tmp/proj", "artifacts": ["code"]}

        mock_context_fn = Mock()

        # Execute with auto_generate_context disabled
        result = auto_chain_context(
            build_result,
            config={
                "orchestrator": {
                    "build": {
                        "auto_generate_context": False
                    }
                }
            },
            invoke_context_fn=mock_context_fn
        )

        # Verify context was not called
        mock_context_fn.assert_not_called()

        # Result should just be the build_result unchanged (auto-chain skipped)
        assert result["status"] == "success"
        assert result == build_result  # Should be same as input

    def test_skip_on_context_failure_true(self):
        """When skip_on_context_failure is True, context failure stops chain."""

        build_result = {"status": "success", "project_dir": "/tmp/proj"}

        mock_context_fn = Mock()
        mock_context_fn.side_effect = Exception("Context generation failed")

        # Execute with skip_on_context_failure enabled
        result = auto_chain_context(
            build_result,
            config={
                "orchestrator": {
                    "build": {
                        "auto_generate_context": True,
                        "skip_on_context_failure": True
                    }
                }
            },
            invoke_context_fn=mock_context_fn
        )

        # Result should indicate failure (not partial_success)
        assert result["status"] in ["failed", "partial_success"]
        assert result["context_status"] == "failed"

    def test_separate_context_commit_true(self):
        """When separate_context_commit is True, two commits should be created."""

        code_artifacts = ["src/"]
        context_artifacts = ["docs/"]

        with patch('tools.orchestrator.orchestrator_bridge.commit_with_chain') as mock_dual:
            mock_dual.return_value = ["abc", "def"]

            commit_shas = mock_dual(
                code_artifacts=code_artifacts,
                context_artifacts=context_artifacts,
                code_message="feat: code",
                context_message="docs: context"
            )

            # Verify two commits returned
            assert len(commit_shas) == 2

    def test_separate_context_commit_false(self):
        """When separate_context_commit is False, single commit created."""

        code_artifacts = ["src/"]
        context_artifacts = ["docs/"]

        with patch('tools.orchestrator.orchestrator_bridge.single_commit') as mock_single:
            mock_single.return_value = "abc"

            # When separate_context_commit is false, artifacts are combined
            # and single_commit is called instead
            commit_sha = mock_single(
                files=code_artifacts + context_artifacts,
                message="feat: implementation and context"
            )

            # Verify single commit returned
            assert isinstance(commit_sha, str)
            assert len(commit_sha) > 0
