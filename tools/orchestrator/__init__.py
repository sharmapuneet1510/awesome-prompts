"""Orchestrator tools for auto-chaining and function invocation.

This module provides utilities for orchestrator:build auto-chaining logic,
which enables automated context generation after successful builds.
"""

import json
from pathlib import Path

from .auto_chain import auto_chain_context
from .orchestrator_bridge import invoke_build_and_context_chain
from .config import OrchestratorConfig


def load_orchestrator_config() -> OrchestratorConfig:
    """Load orchestrator configuration from .claude/settings.json.

    Returns:
        OrchestratorConfig instance (defaults if file not found)
    """
    config_path = Path(".claude/settings.json")

    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                settings = json.load(f)
                orchestrator_config = settings.get("orchestrator", {})
                return OrchestratorConfig.from_dict(orchestrator_config)
        except (json.JSONDecodeError, IOError):
            return OrchestratorConfig.default()

    return OrchestratorConfig.default()


__all__ = [
    "auto_chain_context",
    "invoke_build_and_context_chain",
    "OrchestratorConfig",
    "load_orchestrator_config"
]
