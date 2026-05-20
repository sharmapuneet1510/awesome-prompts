import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from tools.github_sync import GitHubSync


def test_create_feature_branch():
    """Test that branch is created with correct format."""
    repo_path = Path("/tmp/test_repo")
    sync = GitHubSync(str(repo_path))

    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        branch_name = sync.create_branch("add-tests")

        # Verify branch name format: feature/auto-generated-YYYY-MM-DD-{name}
        assert branch_name.startswith("feature/auto-generated-")
        assert "add-tests" in branch_name
        assert branch_name.count("-") >= 5  # At least 5 dashes in the format

        # Verify git checkout -b was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "git" in call_args
        assert "checkout" in call_args
        assert "-b" in call_args
        assert branch_name in call_args
