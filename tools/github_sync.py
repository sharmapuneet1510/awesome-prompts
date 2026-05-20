import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


class GitHubSync:
    """Utility for syncing code to GitHub and creating pull requests."""

    def __init__(self, repo_path: str):
        """Initialize with repository path.

        Args:
            repo_path: Path to the git repository.
        """
        self.repo_path = Path(repo_path)

    def create_branch(self, feature_name: str) -> str:
        """Create a feature branch with date-based naming convention.

        Args:
            feature_name: Name of the feature (will be appended to branch name).

        Returns:
            The created branch name in format: feature/auto-generated-YYYY-MM-DD-{feature_name}

        Raises:
            subprocess.CalledProcessError: If git command fails.
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        branch_name = f'feature/auto-generated-{date_str}-{feature_name}'

        cmd = ['git', '-C', str(self.repo_path), 'checkout', '-b', branch_name]
        subprocess.run(cmd, check=True, text=True, capture_output=True)

        return branch_name

    def commit_changes(self, message: str) -> None:
        """Commit changes to the current branch.

        Args:
            message: Commit message.

        Raises:
            subprocess.CalledProcessError: If git command fails.
        """
        # Stage all changes
        add_cmd = ['git', '-C', str(self.repo_path), 'add', '.']
        subprocess.run(add_cmd, check=True, text=True, capture_output=True)

        # Commit with provided message
        commit_cmd = ['git', '-C', str(self.repo_path), 'commit', '-m', message]
        subprocess.run(commit_cmd, check=True, text=True, capture_output=True)

    def create_pr(self, title: str, body: str) -> str:
        """Create a pull request using GitHub CLI.

        Args:
            title: Title of the pull request.
            body: Description/body of the pull request.

        Returns:
            The URL of the created pull request.

        Raises:
            subprocess.CalledProcessError: If gh command fails.
        """
        cmd = ['gh', 'pr', 'create', '--title', title, '--body', body]
        result = subprocess.run(
            cmd,
            cwd=str(self.repo_path),
            check=True,
            text=True,
            capture_output=True
        )

        return result.stdout.strip()
