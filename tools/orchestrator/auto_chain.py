"""Auto-chaining logic for orchestrator context generation.

Automatically invokes orchestrator:context after successful build.
"""

from typing import Dict, Any, Optional, Callable


def auto_chain_context(
    build_result: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    invoke_context_fn: Optional[Callable] = None
) -> Dict[str, Any]:
    """Auto-invoke orchestrator:context after successful build.

    Args:
        build_result: Result from orchestrator:build containing:
            - status: "success" or "failed"
            - project_dir: Path to generated project (if success)
            - artifacts: List of generated artifacts
        config: Configuration dict with orchestrator settings:
            - orchestrator.build.auto_generate_context (bool, default True)
            - orchestrator.build.context_depth (str, default "comprehensive")
        invoke_context_fn: Function to call for context generation
            (for testing/mocking purposes)

    Returns:
        Combined result with both build and context outcomes:
        - On success: status="success", build_result, context_result
        - On context failure: status="partial_success", build_status="success", context_status="failed"
        - On build failure: Returns build_result unchanged
    """
    # Only auto-chain if build succeeded
    if build_result.get("status") != "success":
        return build_result

    # Get generated project directory
    project_dir = build_result.get("project_dir")
    if not project_dir:
        return {
            **build_result,
            "warning": "No project directory in build result"
        }

    # Load config (default if not provided)
    if config is None:
        config = {}

    # Check if auto-chaining is enabled (default: true)
    auto_chain_enabled = (
        config.get("orchestrator", {})
        .get("build", {})
        .get("auto_generate_context", True)
    )

    if not auto_chain_enabled:
        return build_result

    # Context generation not available (testing mode)
    if invoke_context_fn is None:
        return build_result

    # Invoke orchestrator:context
    try:
        context_depth = (
            config.get("orchestrator", {})
            .get("build", {})
            .get("context_depth", "comprehensive")
        )

        context_result = invoke_context_fn(
            path=project_dir,
            depth=context_depth
        )

        return {
            "status": "success",
            "build_result": build_result,
            "context_result": context_result,
            "build_status": "success",
            "context_status": context_result.get("status")
        }

    except Exception as e:
        # Context failed - mark as partial success
        return {
            "status": "partial_success",
            "build_result": build_result,
            "build_status": "success",
            "context_status": "failed",
            "context_error": str(e),
            "warning": f"Context generation failed: {str(e)}"
        }
