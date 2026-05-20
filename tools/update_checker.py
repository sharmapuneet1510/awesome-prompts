#!/usr/bin/env python3
"""
update_checker.py — Auto-update checker for awesome-prompts repository.

Checks for latest release on GitHub, compares version, downloads and extracts
if newer version is available.

Usage:
    python tools/update_checker.py --check              # Check for updates
    python tools/update_checker.py --apply              # Apply updates if available
    python tools/update_checker.py --version            # Show current version
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional


class Colors:
    """Terminal color codes."""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class VersionChecker:
    """Check and manage updates for awesome-prompts."""

    REPO = "sharmapuneet1510/awesome-prompts"
    GITHUB_API = "https://api.github.com"
    CURRENT_VERSION = "4.0.0"

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize version checker.

        Args:
            repo_root: Path to repository root. If None, auto-detect.
        """
        self.repo_root = repo_root or self._find_repo_root()

    @staticmethod
    def _find_repo_root() -> Path:
        """Find repository root by looking for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()

    def get_latest_release(self) -> Optional[dict]:
        """Fetch latest release info from GitHub API.

        Returns:
            Release dict with 'tag_name' and 'zipball_url', or None if error.
        """
        try:
            url = f"{self.GITHUB_API}/repos/{self.REPO}/releases/latest"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read())
                return {
                    "tag": data.get("tag_name", ""),
                    "url": data.get("zipball_url", ""),
                    "name": data.get("name", ""),
                }
        except Exception as e:
            print(f"{Colors.FAIL}Failed to check for updates: {e}{Colors.ENDC}")
            return None

    @staticmethod
    def _parse_version(version_str: str) -> tuple[int, ...]:
        """Parse semantic version string.

        Args:
            version_str: Version string like "4.0.0" or "v4.0.0"

        Returns:
            Tuple of integers for comparison.
        """
        version_str = version_str.lstrip('v')
        try:
            return tuple(int(x) for x in version_str.split('.')[:3])
        except (ValueError, AttributeError):
            return (0, 0, 0)

    def check_for_updates(self) -> Optional[dict]:
        """Check if update is available.

        Returns:
            Release info if newer version exists, None if current or no update.
        """
        release = self.get_latest_release()
        if not release:
            return None

        latest_version = self._parse_version(release["tag"])
        current_version = self._parse_version(self.CURRENT_VERSION)

        if latest_version > current_version:
            return release
        return None

    def download_and_extract(self, release: dict) -> bool:
        """Download and extract latest release.

        Args:
            release: Release dict from GitHub API

        Returns:
            True if successful, False otherwise.
        """
        try:
            zip_path = self.repo_root / "awesome-prompts-latest.zip"
            extract_dir = self.repo_root / "update-temp"

            print(f"Downloading {release['tag']}...", end=" ", flush=True)

            # Download
            urllib.request.urlretrieve(release["url"], zip_path)
            print("✓")

            print(f"Extracting...", end=" ", flush=True)

            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Get the extracted folder (GitHub names it like owner-repo-hash)
            extracted_items = list(extract_dir.glob("*"))
            if not extracted_items:
                print(f"{Colors.FAIL}✗ No files extracted{Colors.ENDC}")
                return False

            extracted_root = extracted_items[0]

            # Copy files back to repo root (preserve .git, .claude, etc.)
            self._merge_files(extracted_root, self.repo_root)
            print("✓")

            # Cleanup
            zip_path.unlink()
            import shutil
            shutil.rmtree(extract_dir)

            print(f"{Colors.OKGREEN}✓ Update applied successfully{Colors.ENDC}")
            return True

        except Exception as e:
            print(f"{Colors.FAIL}✗ Failed to download/extract: {e}{Colors.ENDC}")
            return False

    def _merge_files(self, src: Path, dst: Path) -> None:
        """Merge files from src to dst, skipping .git and local config.

        Args:
            src: Source directory (extracted files)
            dst: Destination directory (repo root)
        """
        import shutil

        skip_items = {'.git', '.claude/settings.local.json', '.env.local',
                      'graphify-out', '__pycache__', '.pytest_cache', 'node_modules'}

        for item in src.rglob('*'):
            if any(skip in item.parts for skip in skip_items):
                continue

            rel_path = item.relative_to(src)
            dst_item = dst / rel_path

            if item.is_dir():
                dst_item.mkdir(parents=True, exist_ok=True)
            else:
                dst_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst_item)

    def apply_update(self) -> bool:
        """Check for and apply update if available.

        Returns:
            True if update applied, False if already current or error.
        """
        print(f"Checking for updates (current: {Colors.BOLD}v{self.CURRENT_VERSION}{Colors.ENDC})...")

        release = self.check_for_updates()
        if not release:
            print(f"{Colors.OKGREEN}✓ Already up to date{Colors.ENDC}")
            return True

        print(f"New version available: {Colors.OKGREEN}{release['tag']}{Colors.ENDC}")
        print(f"Release: {release['name']}")

        return self.download_and_extract(release)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Update checker for awesome-prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/update_checker.py --check      Check for updates
  python tools/update_checker.py --apply      Apply updates if available
  python tools/update_checker.py --version    Show current version
        """
    )

    parser.add_argument("--check", action="store_true",
                        help="Check for available updates")
    parser.add_argument("--apply", action="store_true",
                        help="Apply updates if available")
    parser.add_argument("--version", action="store_true",
                        help="Show current version")
    parser.add_argument("--repo-root", type=Path,
                        help="Repository root (auto-detect if omitted)")

    args = parser.parse_args()

    checker = VersionChecker(repo_root=args.repo_root)

    if args.version:
        print(f"awesome-prompts version {Colors.BOLD}{checker.CURRENT_VERSION}{Colors.ENDC}")
        return 0

    if args.apply:
        success = checker.apply_update()
        return 0 if success else 1

    if args.check:
        release = checker.check_for_updates()
        if release:
            print(f"Update available: {Colors.OKGREEN}{release['tag']}{Colors.ENDC}")
            print(f"Run: python tools/update_checker.py --apply")
            return 1
        else:
            print(f"{Colors.OKGREEN}Already up to date{Colors.ENDC}")
            return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
