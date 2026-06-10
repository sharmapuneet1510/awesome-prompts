import pytest
from unittest.mock import Mock, patch, MagicMock


class TestDualCommits:
    """Test creating two separate commits (code + context) with linking."""

    def test_dual_commits_created_with_linking(self):
        """Two commits should be created:
           1. Code artifacts
           2. Context artifacts (referencing first commit)"""

        code_artifacts = ["src/", "tests/", "README.md"]
        context_artifacts = ["docs/context/architecture.md", "docs/context/tech-stack.md"]

        with patch('git_handler.commit') as mock_commit:
            # Setup mock to return commit SHAs
            mock_commit.side_effect = [
                "abc1234567890",  # First commit SHA
                "def1234567890"   # Second commit SHA
            ]

            from git_handler import commit_with_chain

            commit_shas = commit_with_chain(
                code_artifacts=code_artifacts,
                context_artifacts=context_artifacts,
                code_message="feat: auto-generated implementation",
                context_message="docs: auto-generated project context"
            )

            # Verify two commits were made
            assert mock_commit.call_count == 2

            # Verify first commit has code artifacts and message
            first_call = mock_commit.call_args_list[0]
            assert code_artifacts == first_call[0][0] or code_artifacts == first_call[1]['files']

            # Verify second commit has context artifacts
            # and references first commit
            second_call = mock_commit.call_args_list[1]
            assert context_artifacts == second_call[0][0] or context_artifacts == second_call[1]['files']
            assert "abc1234567890" in str(second_call)  # References first commit

            # Verify return value
            assert commit_shas == ["abc1234567890", "def1234567890"]
