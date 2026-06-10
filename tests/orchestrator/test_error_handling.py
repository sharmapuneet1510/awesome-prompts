import pytest
from unittest.mock import Mock, patch
from tools.orchestrator.auto_chain import auto_chain_context


class TestErrorHandling:
    """Test error handling when build, context, or commits fail."""

    def test_context_failure_returns_partial_success(self):
        """When context generation fails, system should:
           - Keep code commit (already made)
           - Skip context commit
           - Mark as 'partial_success'"""

        build_result = {"status": "success", "project_dir": "/tmp/project"}

        mock_context = Mock()
        mock_context.side_effect = Exception("Architecture analysis failed")

        result = auto_chain_context(
            build_result,
            invoke_context_fn=mock_context
        )

        assert result["status"] == "partial_success"
        assert result["build_status"] == "success"
        assert result["context_status"] == "failed"
        assert "context_error" in result

    def test_build_failure_skips_auto_chain(self):
        """When build fails, auto-chain should not be triggered."""

        build_result = {
            "status": "failed",
            "error": "Implementation failed"
        }

        mock_context = Mock()
        result = auto_chain_context(build_result, invoke_context_fn=mock_context)

        # Context should not be called on build failure
        mock_context.assert_not_called()
        assert result["status"] == "failed"
