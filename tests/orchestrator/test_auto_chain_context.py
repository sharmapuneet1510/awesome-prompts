import pytest
from unittest.mock import Mock, patch, call


class TestAutoChainContext:
    """Test auto-chaining of orchestrator:context after build completes."""

    def test_build_success_triggers_context_auto_chain(self):
        """When orchestrator:build completes successfully,
           orchestrator:context should be auto-invoked."""

        # Mock the orchestrator build result
        build_result = {
            "status": "success",
            "project_dir": "/tmp/generated_project",
            "artifacts": ["code", "tests", "docs"]
        }

        # Mock the context invocation
        with patch('orchestrator.invoke_context') as mock_context:
            mock_context.return_value = {
                "status": "success",
                "artifacts": ["architecture.md", "tech-stack.md"]
            }

            # Simulate build completion
            from orchestrator import auto_chain_context
            result = auto_chain_context(build_result)

            # Assert context was called with correct arguments
            mock_context.assert_called_once_with(
                path="/tmp/generated_project",
                depth="comprehensive"
            )

            assert result["status"] == "success"
            assert "context_artifacts" in result
