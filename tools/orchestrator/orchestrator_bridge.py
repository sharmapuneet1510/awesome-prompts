"""Bridge between orchestrator functions and git/PR handling.

Coordinates the full build → context → pr chain with proper
commit creation and linking.
"""

from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from git_handler import commit_with_chain, commit as single_commit


def invoke_build_and_context_chain(
    orchestrator,
    requirements_path: str,
    context: Optional[str] = None,
    tech_stack: Optional[str] = None
) -> Dict[str, Any]:
    """Execute full build + context + PR chain.

    Orchestrates the complete workflow:
    1. Build (which auto-chains context if available)
    2. Create commits (dual or single based on results)
    3. Create GitHub PR

    Args:
        orchestrator: Orchestrator agent instance with build/context/pr methods
        requirements_path: Path to requirements.md
        context: Optional business context
        tech_stack: Optional tech stack preference

    Returns:
        Result dict with:
        - status: "success", "error", "partial_success", or "pr_creation_failed"
        - build_status: Status of build phase
        - context_status: Status of context generation (if applicable)
        - commits: List of commit SHAs created
        - pr_url: GitHub PR URL (if PR created)
        - pr_number: GitHub PR number (if PR created)
        - error: Error message (if failed)
        - note: Additional information for user action

    Raises:
        Exception: Only if orchestrator methods raise unexpected errors
    """
    # Phase 1: Build (which auto-chains context if available)
    build_and_context_result = orchestrator.build(
        requirements_path=requirements_path,
        context=context,
        tech_stack=tech_stack
    )

    # Check if build succeeded (at least partial_success is acceptable)
    if build_and_context_result.get("status") not in ["success", "partial_success"]:
        return build_and_context_result

    # Extract artifacts for commit
    build_result = build_and_context_result.get("build_result", build_and_context_result)
    context_result = build_and_context_result.get("context_result", {})

    code_artifacts = build_result.get("artifacts", [])
    context_artifacts = context_result.get("artifacts", []) if context_result else []

    # Phase 2: Create commits
    try:
        commits = []

        if code_artifacts and context_artifacts:
            # Both succeeded - create dual commits
            code_sha, context_sha = commit_with_chain(
                code_artifacts=code_artifacts,
                context_artifacts=context_artifacts,
                code_message="feat: auto-generated implementation",
                context_message="docs: auto-generated project context"
            )
            commits = [code_sha, context_sha]

        elif code_artifacts:
            # Only code succeeded - single commit
            code_sha = single_commit(
                files=code_artifacts,
                message="feat: auto-generated implementation"
            )
            commits = [code_sha]

        else:
            return {
                "status": "error",
                "error": "No artifacts to commit",
                "build_status": build_and_context_result.get("build_status"),
                "context_status": build_and_context_result.get("context_status")
            }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Commit failed: {str(e)}",
            "note": "Generated artifacts are in memory, please commit manually",
            "details": str(e)
        }

    # Phase 3: Create PR
    try:
        pr_result = orchestrator.pr(commits=commits)

        return {
            "status": "success",
            "build_status": build_and_context_result.get("build_status"),
            "context_status": build_and_context_result.get("context_status"),
            "commits": commits,
            "pr_url": pr_result.get("pr_url"),
            "pr_number": pr_result.get("pr_number")
        }

    except Exception as e:
        return {
            "status": "pr_creation_failed",
            "commits": commits,
            "error": f"PR creation failed: {str(e)}",
            "note": "Commits are on branch, create PR manually at GitHub",
            "details": str(e)
        }
