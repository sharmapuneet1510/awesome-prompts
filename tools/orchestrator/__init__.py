"""Orchestrator tools for auto-chaining and function invocation.

This module provides utilities for orchestrator:build auto-chaining logic,
which enables automated context generation after successful builds.
"""

from .auto_chain import auto_chain_context

__all__ = ["auto_chain_context"]
