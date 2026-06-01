"""CacheService: Manage caches for incremental analysis of repositories."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class CacheService:
    """Manage caches for incremental analysis.

    Tracks repository hashes (commit SHA → MD5) and scan state to detect changes
    and enable incremental analysis. Persists cache to JSON files.
    """

    def __init__(self, cache_dir: Path):
        """Initialize CacheService with cache directory.

        Args:
            cache_dir: Path to directory for storing cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.repo_hashes_file = self.cache_dir / "repo-hashes.json"
        self.scan_state_file = self.cache_dir / "scan-state.json"
        self._load_repo_hashes()

    def _load_repo_hashes(self) -> None:
        """Load repo hashes from cache file into memory."""
        if self.repo_hashes_file.exists():
            try:
                with open(self.repo_hashes_file) as f:
                    self.repo_hashes = json.load(f)
                self.logger.debug(
                    f"Loaded {len(self.repo_hashes)} repo hashes from cache"
                )
            except Exception as e:
                self.logger.warning(
                    f"Failed to load repo hashes from cache: {e}. "
                    "Starting with empty cache."
                )
                self.repo_hashes = {}
        else:
            self.repo_hashes = {}

    def _save_repo_hashes(self) -> None:
        """Save repo hashes to cache file."""
        try:
            with open(self.repo_hashes_file, "w") as f:
                json.dump(self.repo_hashes, f, indent=2)
            self.logger.debug(f"Saved {len(self.repo_hashes)} repo hashes to cache")
        except Exception as e:
            self.logger.error(f"Failed to save repo hashes to cache: {e}")

    def save_repo_hash(self, repo_id: str, hash_value: str) -> None:
        """Save repository hash to cache.

        Args:
            repo_id: Unique identifier for the repository
            hash_value: MD5 hash value representing repository state
        """
        self.repo_hashes[repo_id] = hash_value
        self._save_repo_hashes()
        self.logger.debug(f"Saved hash for repo {repo_id}")

    def get_repo_hash(self, repo_id: str) -> Optional[str]:
        """Get repository hash from cache.

        Args:
            repo_id: Unique identifier for the repository

        Returns:
            Cached hash value, or None if not found in cache
        """
        return self.repo_hashes.get(repo_id)

    def is_repo_unchanged(self, repo_id: str, current_hash: str) -> bool:
        """Check if repository has changed.

        Returns True if cached hash matches current hash (repo unchanged).
        Returns False if no cached hash exists or hashes differ.

        Args:
            repo_id: Unique identifier for the repository
            current_hash: Current MD5 hash of repository state

        Returns:
            True if repo hash unchanged, False otherwise
        """
        cached_hash = self.get_repo_hash(repo_id)
        if cached_hash is None:
            return False
        return cached_hash == current_hash

    def save_scan_state(self, state: Dict[str, Any]) -> None:
        """Save scan state to cache.

        Args:
            state: Dictionary containing scan metadata and results
        """
        try:
            with open(self.scan_state_file, "w") as f:
                json.dump(state, f, indent=2)
            self.logger.debug("Saved scan state to cache")
        except Exception as e:
            self.logger.error(f"Failed to save scan state to cache: {e}")

    def get_scan_state(self) -> Dict[str, Any]:
        """Get scan state from cache.

        Returns:
            Dictionary containing cached scan state, or empty dict if not found
        """
        if self.scan_state_file.exists():
            try:
                with open(self.scan_state_file) as f:
                    state = json.load(f)
                self.logger.debug("Loaded scan state from cache")
                return state
            except Exception as e:
                self.logger.warning(f"Failed to load scan state from cache: {e}")
                return {}
        return {}

    def clear_cache(self) -> None:
        """Clear all cached data.

        Deletes both repo-hashes.json and scan-state.json files,
        and clears the in-memory repo_hashes dictionary.
        """
        try:
            if self.repo_hashes_file.exists():
                self.repo_hashes_file.unlink()
                self.logger.debug("Deleted repo hashes cache file")

            if self.scan_state_file.exists():
                self.scan_state_file.unlink()
                self.logger.debug("Deleted scan state cache file")

            self.repo_hashes = {}
            self.logger.info("Cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
