"""Base agent class and registry for all sub-agents."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

from context_builder.models import AgentOutput, ExecutionContext


class BaseAgent(ABC):
    """Abstract base class for all sub-agents.

    All agents must inherit from this class and implement the execute method.
    """

    def __init__(self, name: str):
        """Initialize the base agent.

        Args:
            name: Unique name for the agent.
        """
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Execute the agent with the given execution context.

        Args:
            context: ExecutionContext containing workspace, project, and scan configs.

        Returns:
            AgentOutput with execution status, message, artifacts, and metrics.
        """
        pass

    def validate_context(self, context: ExecutionContext) -> bool:
        """Validate that the execution context is valid.

        Args:
            context: ExecutionContext to validate.

        Returns:
            True if context is valid, False otherwise.
        """
        if context is None:
            self.logger.warning(f"Agent {self.name}: ExecutionContext is None")
            return False
        return True


class AgentRegistry:
    """Registry for managing and accessing available agents.

    This registry maintains a mapping of agent names to agent instances,
    allowing agents to be registered, retrieved, and listed.
    """

    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, agent: BaseAgent) -> None:
        """Register an agent in the registry.

        Args:
            agent: BaseAgent instance to register.

        Raises:
            TypeError: If agent is not an instance of BaseAgent.
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(f"Expected BaseAgent instance, got {type(agent)}")
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    def get(self, name: str) -> Optional[BaseAgent]:
        """Retrieve an agent by name.

        Args:
            name: Name of the agent to retrieve.

        Returns:
            BaseAgent instance if found, None otherwise.
        """
        return self.agents.get(name)

    def list(self) -> Dict[str, BaseAgent]:
        """List all registered agents.

        Returns:
            Dictionary mapping agent names to BaseAgent instances.
        """
        return self.agents.copy()

    def has(self, name: str) -> bool:
        """Check if an agent is registered.

        Args:
            name: Name of the agent to check.

        Returns:
            True if agent is registered, False otherwise.
        """
        return name in self.agents
