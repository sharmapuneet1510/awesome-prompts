import pytest
from unittest.mock import Mock, patch


class TestErrorHandling:
    """Test error handling when build, context, or commits fail."""

    def test_context_failure_returns_partial_success(self):
        """When context generation fails, system should:
           - Keep code commit (already made)
           - Skip context commit
           - Mark as 'partial_success'"""

        build_result = {"status": "success", "project_dir": "/tmp/project"}

        with patch('orchestrator.invoke_context') as mock_context:
            mock_context.return_value = {
                "status": "failed",
                "error": "Architecture analysis failed"
            }

            from orchestrator import auto_chain_context
            result = auto_chain_context(build_result)

            assert result["status"] == "partial_success"
            assert result["build_status"] == "success"
            assert result["context_status"] == "failed"
            assert "error" in result

    def test_commit_failure_stops_chain(self):
        """When git commit fails, system should:
           - Return error to user
           - Not proceed to orchestrator:pr
           - Provide diagnostic info"""

        with patch('git_handler.commit') as mock_commit:
            mock_commit.side_effect = Exception("Permission denied: cannot commit")

            from git_handler import commit_with_chain

            with pytest.raises(Exception) as exc_info:
                commit_with_chain(
                    code_artifacts=["src/"],
                    context_artifacts=["docs/"],
                    code_message="feat: code",
                    context_message="docs: context"
                )

            assert "Permission denied" in str(exc_info.value)

    def test_build_failure_skips_auto_chain(self):
        """When build fails, auto-chain should not be triggered."""

        build_result = {
            "status": "failed",
            "error": "Implementation failed"
        }

        with patch('orchestrator.invoke_context') as mock_context:
            from orchestrator import auto_chain_context
            result = auto_chain_context(build_result)

            # Context should not be called on build failure
            mock_context.assert_not_called()
            assert result["status"] == "failed"
