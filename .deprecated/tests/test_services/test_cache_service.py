"""Tests for CacheService: cache management, repo hashing, and scan state tracking."""

import json
import tempfile
from pathlib import Path

import pytest

from context_builder.services import CacheService


class TestCacheServiceInitialization:
    """Test CacheService initialization."""

    def test_cache_service_init(self):
        """Test CacheService initialization with cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            assert service is not None
            assert service.cache_dir == cache_dir
            assert service.logger is not None
            assert service.repo_hashes == {}
            assert (cache_dir / "repo-hashes.json").parent.exists()

    def test_cache_service_creates_cache_directory(self):
        """Test CacheService creates cache directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "nested" / "cache"
            assert not cache_dir.exists()

            service = CacheService(cache_dir)

            assert cache_dir.exists()
            assert service.cache_dir == cache_dir

    def test_cache_service_loads_existing_hashes(self):
        """Test CacheService loads existing repo hashes from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # Create cache file with existing hashes
            hashes_file = cache_dir / "repo-hashes.json"
            existing_hashes = {
                "repo1": "hash1",
                "repo2": "hash2",
            }
            with open(hashes_file, "w") as f:
                json.dump(existing_hashes, f)

            # Create service and verify it loaded the hashes
            service = CacheService(cache_dir)

            assert service.repo_hashes == existing_hashes
            assert service.get_repo_hash("repo1") == "hash1"
            assert service.get_repo_hash("repo2") == "hash2"


class TestRepoHashOperations:
    """Test repository hash operations."""

    def test_save_repo_hash(self):
        """Test saving a repository hash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("test_repo", "abc123def456")

            assert service.repo_hashes["test_repo"] == "abc123def456"

    def test_get_repo_hash(self):
        """Test retrieving a repository hash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("repo1", "hash_value_123")
            result = service.get_repo_hash("repo1")

            assert result == "hash_value_123"

    def test_get_repo_hash_not_found(self):
        """Test getting hash for non-existent repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            result = service.get_repo_hash("nonexistent_repo")

            assert result is None

    def test_save_multiple_repo_hashes(self):
        """Test saving multiple repository hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("repo1", "hash1")
            service.save_repo_hash("repo2", "hash2")
            service.save_repo_hash("repo3", "hash3")

            assert len(service.repo_hashes) == 3
            assert service.get_repo_hash("repo1") == "hash1"
            assert service.get_repo_hash("repo2") == "hash2"
            assert service.get_repo_hash("repo3") == "hash3"

    def test_update_repo_hash(self):
        """Test updating an existing repository hash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("repo1", "old_hash")
            assert service.get_repo_hash("repo1") == "old_hash"

            service.save_repo_hash("repo1", "new_hash")
            assert service.get_repo_hash("repo1") == "new_hash"


class TestRepoChangeDetection:
    """Test repository change detection."""

    def test_is_repo_unchanged_matches(self):
        """Test detecting unchanged repository when hashes match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("repo1", "hash_abc123")
            is_unchanged = service.is_repo_unchanged("repo1", "hash_abc123")

            assert is_unchanged is True

    def test_is_repo_unchanged_differs(self):
        """Test detecting changed repository when hashes differ."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("repo1", "old_hash")
            is_unchanged = service.is_repo_unchanged("repo1", "new_hash")

            assert is_unchanged is False

    def test_is_repo_unchanged_not_cached(self):
        """Test detecting change when repository not yet cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            is_unchanged = service.is_repo_unchanged("uncached_repo", "some_hash")

            assert is_unchanged is False

    def test_is_repo_unchanged_empty_cache(self):
        """Test change detection on empty cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            assert service.repo_hashes == {}
            is_unchanged = service.is_repo_unchanged("repo1", "hash123")

            assert is_unchanged is False


class TestScanStateOperations:
    """Test scan state save and retrieve operations."""

    def test_save_scan_state(self):
        """Test saving scan state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state = {
                "timestamp": "2026-06-01T10:00:00Z",
                "repos_scanned": 5,
                "files_found": 150,
            }
            service.save_scan_state(state)

            assert (cache_dir / "scan-state.json").exists()

    def test_get_scan_state(self):
        """Test retrieving scan state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state = {
                "timestamp": "2026-06-01T10:00:00Z",
                "repos_scanned": 5,
                "files_found": 150,
                "analysis": {
                    "patterns_found": ["pattern1", "pattern2"],
                },
            }
            service.save_scan_state(state)
            retrieved_state = service.get_scan_state()

            assert retrieved_state == state
            assert retrieved_state["timestamp"] == "2026-06-01T10:00:00Z"
            assert retrieved_state["repos_scanned"] == 5
            assert retrieved_state["files_found"] == 150
            assert retrieved_state["analysis"]["patterns_found"] == ["pattern1", "pattern2"]

    def test_get_scan_state_not_found(self):
        """Test getting scan state when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state = service.get_scan_state()

            assert state == {}
            assert isinstance(state, dict)

    def test_save_complex_scan_state(self):
        """Test saving complex nested scan state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state = {
                "timestamp": "2026-06-01T10:00:00Z",
                "repos": {
                    "repo1": {
                        "hash": "hash1",
                        "files": 50,
                        "stats": {"py": 30, "js": 20},
                    },
                    "repo2": {
                        "hash": "hash2",
                        "files": 75,
                        "stats": {"py": 60, "js": 15},
                    },
                },
                "summary": {
                    "total_repos": 2,
                    "total_files": 125,
                },
            }
            service.save_scan_state(state)
            retrieved = service.get_scan_state()

            assert retrieved == state
            assert retrieved["repos"]["repo1"]["files"] == 50
            assert retrieved["repos"]["repo2"]["stats"]["py"] == 60

    def test_scan_state_overwrite(self):
        """Test that saving new scan state overwrites previous state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state1 = {"version": 1, "data": "first"}
            service.save_scan_state(state1)

            state2 = {"version": 2, "data": "second"}
            service.save_scan_state(state2)

            retrieved = service.get_scan_state()
            assert retrieved == state2
            assert retrieved["version"] == 2


class TestCachePersistence:
    """Test cache persistence to files."""

    def test_repo_hashes_persisted_to_file(self):
        """Test that repo hashes are persisted to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("repo1", "hash1")
            service.save_repo_hash("repo2", "hash2")

            # Verify file exists and contains correct data
            hashes_file = cache_dir / "repo-hashes.json"
            assert hashes_file.exists()

            with open(hashes_file) as f:
                saved_data = json.load(f)

            assert saved_data["repo1"] == "hash1"
            assert saved_data["repo2"] == "hash2"

    def test_hashes_reloaded_on_new_instance(self):
        """Test that hashes are reloaded when creating new CacheService instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # First instance: save hashes
            service1 = CacheService(cache_dir)
            service1.save_repo_hash("repo1", "hash1")
            service1.save_repo_hash("repo2", "hash2")

            # Second instance: verify it loads the saved hashes
            service2 = CacheService(cache_dir)
            assert service2.get_repo_hash("repo1") == "hash1"
            assert service2.get_repo_hash("repo2") == "hash2"

    def test_scan_state_persisted_to_file(self):
        """Test that scan state is persisted to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state = {
                "timestamp": "2026-06-01T10:00:00Z",
                "repos_scanned": 3,
            }
            service.save_scan_state(state)

            # Verify file exists and contains correct data
            state_file = cache_dir / "scan-state.json"
            assert state_file.exists()

            with open(state_file) as f:
                saved_data = json.load(f)

            assert saved_data == state

    def test_scan_state_reloaded_on_new_instance(self):
        """Test that scan state is reloaded when creating new CacheService instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # First instance: save state
            service1 = CacheService(cache_dir)
            state = {
                "timestamp": "2026-06-01T10:00:00Z",
                "repos_scanned": 5,
            }
            service1.save_scan_state(state)

            # Second instance: verify it can load the saved state
            service2 = CacheService(cache_dir)
            loaded_state = service2.get_scan_state()
            assert loaded_state == state


class TestClearCache:
    """Test cache clearing operations."""

    def test_clear_cache(self):
        """Test clearing all cached data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            # Add data to both cache files
            service.save_repo_hash("repo1", "hash1")
            service.save_scan_state({"data": "state"})

            # Verify files exist
            assert (cache_dir / "repo-hashes.json").exists()
            assert (cache_dir / "scan-state.json").exists()

            # Clear cache
            service.clear_cache()

            # Verify files are deleted and memory is cleared
            assert not (cache_dir / "repo-hashes.json").exists()
            assert not (cache_dir / "scan-state.json").exists()
            assert service.repo_hashes == {}

    def test_clear_cache_with_empty_repo_hashes(self):
        """Test clearing cache when repo hashes file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            # Only save scan state, not repo hashes
            service.save_scan_state({"data": "state"})
            assert (cache_dir / "scan-state.json").exists()
            assert not (cache_dir / "repo-hashes.json").exists()

            # Clear cache should not raise error
            service.clear_cache()

            assert not (cache_dir / "scan-state.json").exists()

    def test_clear_cache_with_empty_scan_state(self):
        """Test clearing cache when scan state file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            # Only save repo hashes, not scan state
            service.save_repo_hash("repo1", "hash1")
            assert (cache_dir / "repo-hashes.json").exists()
            assert not (cache_dir / "scan-state.json").exists()

            # Clear cache should not raise error
            service.clear_cache()

            assert not (cache_dir / "repo-hashes.json").exists()

    def test_clear_cache_on_empty_service(self):
        """Test clearing cache on service with no saved data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            # Call clear on empty service (should not raise error)
            service.clear_cache()

            assert service.repo_hashes == {}

    def test_cache_operations_after_clear(self):
        """Test that cache can be used normally after clearing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            # Add, clear, then add again
            service.save_repo_hash("repo1", "hash1")
            service.clear_cache()
            service.save_repo_hash("repo2", "hash2")

            assert service.get_repo_hash("repo1") is None
            assert service.get_repo_hash("repo2") == "hash2"
            assert (cache_dir / "repo-hashes.json").exists()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_repo_id(self):
        """Test handling of empty repository ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            service.save_repo_hash("", "hash_value")
            assert service.get_repo_hash("") == "hash_value"

    def test_special_characters_in_repo_id(self):
        """Test handling of special characters in repository ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            repo_id = "repo/with/slashes:special-chars_123"
            service.save_repo_hash(repo_id, "hash_value")
            assert service.get_repo_hash(repo_id) == "hash_value"

    def test_long_hash_value(self):
        """Test handling of very long hash values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            long_hash = "a" * 1000
            service.save_repo_hash("repo1", long_hash)
            assert service.get_repo_hash("repo1") == long_hash

    def test_unicode_in_scan_state(self):
        """Test handling of Unicode characters in scan state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state = {
                "description": "Scan with Unicode: 你好 مرحبا",
                "emojis": "🚀 🎯 ✅",
            }
            service.save_scan_state(state)
            retrieved = service.get_scan_state()

            assert retrieved == state

    def test_null_values_in_scan_state(self):
        """Test handling of null/None values in scan state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            state = {
                "required_field": "value",
                "optional_field": None,
                "nested": {
                    "data": None,
                },
            }
            service.save_scan_state(state)
            retrieved = service.get_scan_state()

            assert retrieved == state
            assert retrieved["optional_field"] is None

    def test_concurrent_repo_hash_updates(self):
        """Test that multiple save operations work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            service = CacheService(cache_dir)

            # Simulate multiple rapid updates
            for i in range(10):
                service.save_repo_hash(f"repo{i}", f"hash{i}")

            # Verify all updates were saved
            for i in range(10):
                assert service.get_repo_hash(f"repo{i}") == f"hash{i}"

            # Verify file persistence
            new_service = CacheService(cache_dir)
            for i in range(10):
                assert new_service.get_repo_hash(f"repo{i}") == f"hash{i}"
