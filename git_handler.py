"""Git handler for orchestrator agent.

Handles committing generated artifacts with proper linking
and error handling.
"""

import subprocess
from typing import List


def commit(files: List[str], message: str, parent_commit: str = None) -> str:
    """Create a git commit with the given files and message.

    Args:
        files: List of file paths to commit
        message: Commit message
        parent_commit: Optional SHA of parent commit (for reference in message)

    Returns:
        Commit SHA (hash)

    Raises:
        subprocess.CalledProcessError: If git commit fails
        ValueError: If no files provided
    """
    if not files:
        raise ValueError("No files to commit")

    # Stage files
    subprocess.run(["git", "add"] + files, check=True)

    # Add parent reference if provided
    full_message = message
    if parent_commit:
        full_message = f"{message}\n\nAutomated context for {parent_commit}"

    # Create commit
    result = subprocess.run(
        ["git", "commit", "-m", full_message],
        capture_output=True,
        text=True,
        check=True
    )

    # Extract SHA from output (first 7 chars)
    # Output format: [main abc1234] commit message
    commit_sha = result.stdout.split()[1].rstrip("]")
    return commit_sha


def commit_with_chain(
    code_artifacts: List[str],
    context_artifacts: List[str],
    code_message: str,
    context_message: str
) -> List[str]:
    """Create two linked commits: code + context.

    Args:
        code_artifacts: List of files for code commit
        context_artifacts: List of files for context commit
        code_message: Message for code commit
        context_message: Message for context commit

    Returns:
        List of [code_commit_sha, context_commit_sha]

    Raises:
        subprocess.CalledProcessError: If either commit fails
        ValueError: If artifact lists are empty
    """
    # Commit 1: Code artifacts
    code_sha = commit(code_artifacts, code_message)

    # Commit 2: Context (references code commit)
    context_sha = commit(context_artifacts, context_message, parent_commit=code_sha)

    return [code_sha, context_sha]
