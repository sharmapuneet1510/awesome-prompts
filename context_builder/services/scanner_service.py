"""ScannerService: File scanning with include/exclude patterns and directory traversal."""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Set
import fnmatch


class ScannerService:
    """Scan directories for files matching patterns."""

    def __init__(self):
        """Initialize ScannerService."""
        self.logger = logging.getLogger(__name__)

    def scan_directory(
        self,
        directory: Path,
        include_patterns: List[str],
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[Path]:
        """
        Scan directory recursively for files matching include patterns.

        Args:
            directory: Root directory to scan
            include_patterns: List of glob patterns to include (e.g., ["**/*.java", "**/*.py"])
            exclude_patterns: List of glob patterns to exclude (e.g., ["**/test/**", "**/node_modules/**"])

        Returns:
            List of matching file paths
        """
        if not directory.exists():
            self.logger.warning(f"Directory not found: {directory}")
            return []

        exclude_patterns = exclude_patterns or []
        matching_files = []
        seen_paths: Set[str] = set()

        try:
            for pattern in include_patterns:
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        # Normalize path to avoid duplicates
                        normalized = str(file_path.resolve())
                        if normalized in seen_paths:
                            continue

                        # Check exclude patterns
                        excluded = False
                        for exclude_pattern in exclude_patterns:
                            if file_path.match(exclude_pattern):
                                excluded = True
                                break

                        if not excluded:
                            matching_files.append(file_path)
                            seen_paths.add(normalized)

            self.logger.info(
                f"Scanned {directory}: found {len(matching_files)} files"
            )
            return matching_files

        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            return []

    def scan_for_file_types(
        self,
        directory: Path,
        file_extensions: List[str],
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, List[Path]]:
        """
        Scan directory for files by extension.

        Args:
            directory: Root directory to scan
            file_extensions: List of extensions (e.g., [".java", ".py", ".ts"])
            exclude_patterns: Patterns to exclude

        Returns:
            Dictionary mapping extension to list of file paths
        """
        exclude_patterns = exclude_patterns or []
        result: Dict[str, List[Path]] = {}

        try:
            for ext in file_extensions:
                # Normalize extension (add dot if missing)
                normalized_ext = ext if ext.startswith(".") else f".{ext}"
                include_pattern = f"**/*{normalized_ext}"

                files = self.scan_directory(
                    directory, [include_pattern], exclude_patterns
                )
                if files:
                    result[normalized_ext] = files

            return result

        except Exception as e:
            self.logger.error(f"Error scanning for file types in {directory}: {e}")
            return {}

    def count_files(
        self,
        directory: Path,
        include_patterns: List[str],
        exclude_patterns: Optional[List[str]] = None,
    ) -> int:
        """
        Count files matching patterns.

        Args:
            directory: Root directory to scan
            include_patterns: Patterns to include
            exclude_patterns: Patterns to exclude

        Returns:
            Count of matching files
        """
        files = self.scan_directory(directory, include_patterns, exclude_patterns)
        return len(files)

    def get_file_stats(
        self,
        directory: Path,
        include_patterns: List[str],
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Get statistics about scanned files.

        Args:
            directory: Root directory to scan
            include_patterns: Patterns to include
            exclude_patterns: Patterns to exclude

        Returns:
            Dictionary with file statistics
        """
        files = self.scan_directory(directory, include_patterns, exclude_patterns)

        total_size = sum(f.stat().st_size for f in files)
        extensions: Dict[str, int] = {}

        for file_path in files:
            ext = file_path.suffix or "no_extension"
            extensions[ext] = extensions.get(ext, 0) + 1

        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "extensions": extensions,
        }
