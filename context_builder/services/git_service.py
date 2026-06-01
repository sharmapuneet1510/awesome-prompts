"""GitService: Handle git operations for repository management."""

import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from git import Repo
from git.exc import GitCommandError


class GitService:
    """Handle git operations: clone, pull, file listing, repo hashing."""

    def __init__(self):
        """Initialize GitService with logger."""
        self.logger = logging.getLogger(__name__)

    def clone(self, git_url: str, local_path: Path, branch: str = "main") -> bool:
        """
        Clone a repository to a local path.

        Args:
            git_url: Git URL (https or ssh)
            local_path: Local path to clone to
            branch: Branch to checkout (default: main)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to Path if needed
            local_path = Path(local_path)

            # Create parent directory if it doesn't exist
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Clone the repository
            Repo.clone_from(git_url, str(local_path), branch=branch)
            self.logger.info(f"Successfully cloned {git_url} to {local_path}")
            return True

        except GitCommandError as e:
            self.logger.error(f"Failed to clone {git_url}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error while cloning {git_url}: {e}")
            return False

    def pull(self, local_path: Path, branch: str = "main") -> bool:
        """
        Pull latest changes from repository.

        Args:
            local_path: Local path to repository
            branch: Branch to pull (default: main)

        Returns:
            True if successful, False otherwise
        """
        try:
            local_path = Path(local_path)
            repo = Repo(str(local_path))
            repo.remotes.origin.pull(branch)
            self.logger.info(f"Successfully pulled updates from {local_path}")
            return True

        except GitCommandError as e:
            self.logger.error(f"Failed to pull from {local_path}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error while pulling from {local_path}: {e}")
            return False

    def get_repo_hash(self, local_path: Path) -> Optional[str]:
        """
        Compute hash of repository state based on HEAD commit.

        Used for incremental analysis to detect repository changes.

        Args:
            local_path: Local path to repository

        Returns:
            MD5 hash of HEAD commit SHA, or None if repo not found
        """
        try:
            local_path = Path(local_path)
            repo = Repo(str(local_path))

            # Get the HEAD commit SHA
            head_sha = repo.head.commit.hexsha

            # Compute MD5 hash of the SHA
            hash_obj = hashlib.md5(head_sha.encode())
            hash_result = hash_obj.hexdigest()

            self.logger.debug(f"Computed hash for {local_path}: {hash_result}")
            return hash_result

        except Exception as e:
            self.logger.warning(f"Could not compute hash for {local_path}: {e}")
            return None

    def list_files(
        self,
        local_path: Path,
        include_patterns: List[str],
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[Path]:
        """
        List files matching include patterns, excluding exclude patterns.

        Args:
            local_path: Repository path
            include_patterns: Glob patterns to include (e.g., ["**/*.py"])
            exclude_patterns: Glob patterns to exclude (optional)

        Returns:
            List of matching file paths
        """
        local_path = Path(local_path)

        # Check if path exists
        if not local_path.exists():
            self.logger.warning(f"Repository path not found: {local_path}")
            return []

        exclude_patterns = exclude_patterns or []
        matching_files = []

        # Process each include pattern
        for pattern in include_patterns:
            try:
                matches = local_path.glob(pattern)
                for file_path in matches:
                    # Only include files, not directories
                    if file_path.is_file():
                        # Check if file matches any exclude pattern
                        excluded = any(
                            file_path.match(ep) for ep in exclude_patterns
                        )
                        if not excluded:
                            matching_files.append(file_path)

            except Exception as e:
                self.logger.warning(
                    f"Error processing pattern {pattern} in {local_path}: {e}"
                )

        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in matching_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)

        self.logger.debug(
            f"Found {len(unique_files)} files in {local_path} "
            f"matching patterns {include_patterns}"
        )
        return unique_files
