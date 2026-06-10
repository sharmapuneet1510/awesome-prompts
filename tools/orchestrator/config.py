"""Configuration for orchestrator auto-chaining behavior."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class OrchestratorConfig:
    """Orchestrator configuration settings.

    Attributes:
        auto_generate_context: Enable/disable auto-context generation (default: True)
        context_depth: Depth for context generation (quick|standard|comprehensive, default: comprehensive)
        separate_context_commit: Create separate commit for context (default: True)
        skip_on_context_failure: Continue to PR even if context fails (default: False)
    """

    auto_generate_context: bool = True
    context_depth: str = "comprehensive"  # quick, standard, comprehensive
    separate_context_commit: bool = True
    skip_on_context_failure: bool = False

    @staticmethod
    def from_dict(config_dict: Optional[Dict[str, Any]]) -> "OrchestratorConfig":
        """Load configuration from dictionary (e.g., from .claude/settings.json).

        Args:
            config_dict: Dictionary with orchestrator settings or None

        Returns:
            OrchestratorConfig instance with defaults or provided values
        """
        if not config_dict:
            return OrchestratorConfig()

        build_config = config_dict.get("build", {})

        return OrchestratorConfig(
            auto_generate_context=build_config.get("auto_generate_context", True),
            context_depth=build_config.get("context_depth", "comprehensive"),
            separate_context_commit=build_config.get("separate_context_commit", True),
            skip_on_context_failure=build_config.get("skip_on_context_failure", False)
        )

    @staticmethod
    def default() -> "OrchestratorConfig":
        """Return default configuration (auto-chaining enabled)."""
        return OrchestratorConfig()

    @staticmethod
    def disabled() -> "OrchestratorConfig":
        """Return configuration with auto-chaining disabled (manual control)."""
        return OrchestratorConfig(auto_generate_context=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage."""
        return {
            "build": {
                "auto_generate_context": self.auto_generate_context,
                "context_depth": self.context_depth,
                "separate_context_commit": self.separate_context_commit,
                "skip_on_context_failure": self.skip_on_context_failure
            }
        }
