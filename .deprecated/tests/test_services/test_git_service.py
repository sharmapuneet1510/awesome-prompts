"""Tests for GitService: git operations, cloning, pulling, file listing."""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from git.exc import GitCommandError

from context_builder.services import GitService


class TestGitService:
    """Test GitService class."""

    def test_git_service_init(self):
        """Test GitService initialization."""
        service = GitService()
        assert service is not None
        assert service.logger is not None

    def test_clone_repository(self):
        """Test cloning a repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = Path(tmpdir) / "test_repo"
            service = GitService()

            with patch('context_builder.services.git_service.Repo') as mock_repo:
                mock_repo.clone_from.return_value = Mock()
                result = service.clone(
                    "https://github.com/test/repo.git",
                    local_path,
                    branch="main"
                )
                assert result is True
                mock_repo.clone_from.assert_called_once()

    def test_clone_repository_failure(self):
        """Test clone handles git command errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = Path(tmpdir) / "test_repo"
            service = GitService()

            with patch('context_builder.services.git_service.Repo') as mock_repo:
                mock_repo.clone_from.side_effect = GitCommandError("git clone", 128, "fatal error")
                result = service.clone(
                    "https://invalid-url.git",
                    local_path,
                    branch="main"
                )
                assert result is False

    def test_pull_repository(self):
        """Test pulling latest changes from repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test_repo"
            repo_path.mkdir()
            service = GitService()

            with patch('context_builder.services.git_service.Repo') as mock_repo:
                mock_instance = Mock()
                mock_repo.return_value = mock_instance
                mock_instance.remotes.origin.pull.return_value = None

                result = service.pull(repo_path, branch="main")
                assert result is True
                mock_repo.assert_called_once_with(str(repo_path))

    def test_pull_repository_failure(self):
        """Test pull handles errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test_repo"
            repo_path.mkdir()
            service = GitService()

            with patch('context_builder.services.git_service.Repo') as mock_repo:
                mock_repo.side_effect = Exception("Repository not found")
                result = service.pull(repo_path, branch="main")
                assert result is False

    def test_get_repo_hash(self):
        """Test computing repository hash from HEAD commit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test_repo"
            repo_path.mkdir()
            service = GitService()

            with patch('context_builder.services.git_service.Repo') as mock_repo:
                mock_instance = Mock()
                mock_repo.return_value = mock_instance
                mock_instance.head.commit.hexsha = "abc123def456"

                hash_result = service.get_repo_hash(repo_path)
                assert hash_result is not None
                assert isinstance(hash_result, str)
                assert len(hash_result) == 32  # MD5 hex digest length

    def test_get_repo_hash_nonexistent(self):
        """Test get_repo_hash handles non-existent repositories."""
        service = GitService()
        nonexistent = Path("/nonexistent/path")

        with patch('context_builder.services.git_service.Repo') as mock_repo:
            mock_repo.side_effect = Exception("Repository not found")
            result = service.get_repo_hash(nonexistent)
            assert result is None

    def test_list_files(self):
        """Test listing files matching include patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Create test files
            (repo_path / "file1.py").touch()
            (repo_path / "file2.py").touch()
            (repo_path / "file3.txt").touch()
            subdir = repo_path / "subdir"
            subdir.mkdir()
            (subdir / "file4.py").touch()

            service = GitService()
            files = service.list_files(repo_path, ["**/*.py"])

            assert len(files) >= 3
            assert any(f.name == "file1.py" for f in files)
            assert any(f.name == "file2.py" for f in files)
            assert any(f.name == "file4.py" for f in files)

    def test_list_files_with_exclude(self):
        """Test listing files with exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Create test files
            (repo_path / "main.py").touch()
            (repo_path / "test.py").touch()
            exclude_dir = repo_path / "exclude"
            exclude_dir.mkdir()
            (exclude_dir / "ignored.py").touch()

            service = GitService()
            files = service.list_files(
                repo_path,
                include_patterns=["**/*.py"],
                exclude_patterns=["exclude/**"]
            )

            assert any(f.name == "main.py" for f in files)
            assert any(f.name == "test.py" for f in files)
            assert not any("exclude" in str(f) for f in files)

    def test_list_files_nonexistent_repo(self):
        """Test list_files handles missing repository."""
        service = GitService()
        nonexistent = Path("/nonexistent/path")

        files = service.list_files(nonexistent, ["**/*.py"])
        assert files == []

    def test_list_files_removes_duplicates(self):
        """Test list_files removes duplicate entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Create test files
            (repo_path / "file.py").touch()

            service = GitService()
            # Use overlapping patterns that could produce duplicates
            files = service.list_files(
                repo_path,
                include_patterns=["**/*.py", "file.py"]
            )

            # Should only have one copy of file.py
            file_names = [f.name for f in files]
            assert file_names.count("file.py") == 1

    def test_clone_creates_parent_directory(self):
        """Test clone creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = Path(tmpdir) / "nested" / "deep" / "repo"
            service = GitService()

            with patch('context_builder.services.git_service.Repo') as mock_repo:
                mock_repo.clone_from.return_value = Mock()
                result = service.clone(
                    "https://github.com/test/repo.git",
                    local_path,
                    branch="main"
                )
                assert result is True
