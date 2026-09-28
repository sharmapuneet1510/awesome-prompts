"""Tests for ScannerService."""

import pytest
from pathlib import Path
import tempfile

from context_builder.services.scanner_service import ScannerService


class TestScannerServiceInitialization:
    """Tests for ScannerService initialization."""

    def test_init(self):
        """ScannerService initializes successfully."""
        service = ScannerService()
        assert service is not None
        assert service.logger is not None


class TestScanDirectory:
    """Tests for scan_directory method."""

    def test_scan_directory_with_valid_patterns(self):
        """Scan directory finds files matching patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test files
            (root / "test1.py").touch()
            (root / "test2.py").touch()
            (root / "readme.md").touch()

            service = ScannerService()
            files = service.scan_directory(root, ["**/*.py"])

            assert len(files) == 2
            assert any(f.name == "test1.py" for f in files)
            assert any(f.name == "test2.py" for f in files)

    def test_scan_directory_with_exclude_patterns(self):
        """Scan directory respects exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test structure
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "src" / "main.py").touch()
            (root / "tests" / "test_main.py").touch()

            service = ScannerService()
            files = service.scan_directory(
                root, ["**/*.py"], exclude_patterns=["**/tests/**"]
            )

            assert len(files) == 1
            assert files[0].name == "main.py"

    def test_scan_directory_nonexistent_path(self):
        """Scan directory handles nonexistent paths gracefully."""
        service = ScannerService()
        files = service.scan_directory(Path("/nonexistent"), ["**/*.py"])

        assert files == []

    def test_scan_directory_multiple_patterns(self):
        """Scan directory matches multiple patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "file.py").touch()
            (root / "file.java").touch()
            (root / "readme.md").touch()

            service = ScannerService()
            files = service.scan_directory(root, ["**/*.py", "**/*.java"])

            assert len(files) == 2

    def test_scan_directory_no_duplicates(self):
        """Scan directory doesn't return duplicate files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "file.py").touch()

            service = ScannerService()
            # Use overlapping patterns
            files = service.scan_directory(root, ["**/*.py", "**/*.py"])

            assert len(files) == 1


class TestScanForFileTypes:
    """Tests for scan_for_file_types method."""

    def test_scan_for_file_types(self):
        """Scan by file type returns organized results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "file1.py").touch()
            (root / "file2.py").touch()
            (root / "file3.java").touch()

            service = ScannerService()
            result = service.scan_for_file_types(root, [".py", ".java"])

            assert ".py" in result
            assert ".java" in result
            assert len(result[".py"]) == 2
            assert len(result[".java"]) == 1

    def test_scan_for_file_types_with_exclude(self):
        """Scan by file type respects exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "main.py").touch()
            (root / "test.py").touch()

            service = ScannerService()
            result = service.scan_for_file_types(
                root, [".py"], exclude_patterns=["**/test.py"]
            )

            assert len(result[".py"]) == 1
            assert result[".py"][0].name == "main.py"


class TestCountFiles:
    """Tests for count_files method."""

    def test_count_files(self):
        """Count files returns correct count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "file1.py").touch()
            (root / "file2.py").touch()
            (root / "readme.md").touch()

            service = ScannerService()
            count = service.count_files(root, ["**/*.py"])

            assert count == 2


class TestGetFileStats:
    """Tests for get_file_stats method."""

    def test_get_file_stats(self):
        """Get file stats returns correct statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files with content
            (root / "file1.py").write_text("print('hello')")
            (root / "file2.py").write_text("x = 1")
            (root / "readme.md").write_text("# README")

            service = ScannerService()
            stats = service.get_file_stats(root, ["**/*.py"])

            assert stats["total_files"] == 2
            assert stats["total_size_bytes"] > 0
            assert ".py" in stats["extensions"]
            assert stats["extensions"][".py"] == 2

    def test_get_file_stats_empty_directory(self):
        """Get file stats handles empty results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            service = ScannerService()
            stats = service.get_file_stats(root, ["**/*.py"])

            assert stats["total_files"] == 0
            assert stats["total_size_bytes"] == 0
