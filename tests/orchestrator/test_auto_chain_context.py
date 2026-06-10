import pytest
from unittest.mock import Mock, patch, call
from tools.orchestrator.auto_chain import auto_chain_context


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
        mock_context = Mock()
        mock_context.return_value = {
            "status": "success",
            "artifacts": ["architecture.md", "tech-stack.md"]
        }

        # Simulate build completion
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
            invoke_context_fn=mock_context
        )

        # Assert context was called with correct arguments
        mock_context.assert_called_once_with(
            path="/tmp/generated_project",
            depth="comprehensive"
        )

        assert result["status"] == "success"
        assert result["context_result"]["status"] == "success"
