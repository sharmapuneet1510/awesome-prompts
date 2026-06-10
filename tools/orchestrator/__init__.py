"""Orchestrator tools for auto-chaining and function invocation.

This module provides utilities for orchestrator:build auto-chaining logic,
which enables automated context generation after successful builds.
"""

from .auto_chain import auto_chain_context
from .orchestrator_bridge import invoke_build_and_context_chain

__all__ = ["auto_chain_context", "invoke_build_and_context_chain"]
