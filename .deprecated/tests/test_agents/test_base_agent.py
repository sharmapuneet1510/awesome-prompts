"""Tests for BaseAgent and AgentRegistry."""

import logging
from pathlib import Path
from typing import Optional

import pytest

from context_builder.agents import BaseAgent, AgentRegistry
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Graph,
    MaturityConfig,
    ProjectConfig,
    ScanConfig,
    TechAliases,
    TestQualityConfig,
    WorkspaceConfig,
)


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Execute the agent."""
        return AgentOutput(
            status="success",
            message="Test agent executed successfully",
            artifacts=[],
            metrics={"test": True},
        )


class FailingAgent(BaseAgent):
    """Agent that returns failed status."""

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Execute and return failure."""
        return AgentOutput(
            status="failed",
            message="Agent execution failed",
            artifacts=[],
            errors=["Test error"],
        )


@pytest.fixture
def execution_context():
    """Fixture providing a valid ExecutionContext."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace",
        context_root=Path("/tmp/test"),
    )
    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=Graph(),
    )


@pytest.fixture
def agent_registry():
    """Fixture providing an AgentRegistry instance."""
    return AgentRegistry()


class TestBaseAgent:
    """Test cases for BaseAgent."""

    def test_base_agent_name(self):
        """Test that agent is initialized with correct name."""
        agent = ConcreteAgent("test_agent")
        assert agent.name == "test_agent"

    def test_base_agent_logger(self):
        """Test that agent has a logger."""
        agent = ConcreteAgent("test_agent")
        assert agent.logger is not None
        assert isinstance(agent.logger, logging.Logger)
        assert agent.logger.name == "ConcreteAgent"

    def test_base_agent_execute(self, execution_context):
        """Test that agent can execute and return AgentOutput."""
        agent = ConcreteAgent("test_agent")
        output = agent.execute(execution_context)
        assert output.status == "success"
        assert output.message == "Test agent executed successfully"
        assert output.metrics == {"test": True}

    def test_base_agent_cannot_be_instantiated(self):
        """Test that BaseAgent cannot be directly instantiated."""
        with pytest.raises(TypeError):
            BaseAgent("test")

    def test_validate_context_with_valid_context(self, execution_context):
        """Test validate_context returns True for valid context."""
        agent = ConcreteAgent("test_agent")
        assert agent.validate_context(execution_context) is True

    def test_validate_context_with_none(self):
        """Test validate_context returns False when context is None."""
        agent = ConcreteAgent("test_agent")
        assert agent.validate_context(None) is False

    def test_agent_with_different_names(self):
        """Test creating agents with different names."""
        agent1 = ConcreteAgent("agent_one")
        agent2 = ConcreteAgent("agent_two")
        assert agent1.name == "agent_one"
        assert agent2.name == "agent_two"
        assert agent1.name != agent2.name

    def test_execute_returns_agent_output(self, execution_context):
        """Test that execute method returns AgentOutput instance."""
        agent = ConcreteAgent("test_agent")
        output = agent.execute(execution_context)
        assert isinstance(output, AgentOutput)
        assert hasattr(output, "status")
        assert hasattr(output, "message")
        assert hasattr(output, "artifacts")
        assert hasattr(output, "metrics")


class TestAgentRegistry:
    """Test cases for AgentRegistry."""

    def test_agent_registry_register(self, agent_registry):
        """Test registering an agent."""
        agent = ConcreteAgent("test_agent")
        agent_registry.register(agent)
        assert agent_registry.has("test_agent")

    def test_agent_registry_register_multiple(self, agent_registry):
        """Test registering multiple agents."""
        agent1 = ConcreteAgent("agent_one")
        agent2 = ConcreteAgent("agent_two")
        agent_registry.register(agent1)
        agent_registry.register(agent2)
        assert agent_registry.has("agent_one")
        assert agent_registry.has("agent_two")

    def test_agent_registry_get(self, agent_registry):
        """Test retrieving an agent by name."""
        agent = ConcreteAgent("test_agent")
        agent_registry.register(agent)
        retrieved = agent_registry.get("test_agent")
        assert retrieved is agent
        assert retrieved.name == "test_agent"

    def test_agent_registry_get_nonexistent(self, agent_registry):
        """Test retrieving non-existent agent returns None."""
        result = agent_registry.get("nonexistent")
        assert result is None

    def test_agent_registry_has(self, agent_registry):
        """Test checking if agent is registered."""
        agent = ConcreteAgent("test_agent")
        assert agent_registry.has("test_agent") is False
        agent_registry.register(agent)
        assert agent_registry.has("test_agent") is True

    def test_agent_registry_list_empty(self, agent_registry):
        """Test listing agents when registry is empty."""
        agents = agent_registry.list()
        assert agents == {}

    def test_agent_registry_list(self, agent_registry):
        """Test listing all registered agents."""
        agent1 = ConcreteAgent("agent_one")
        agent2 = ConcreteAgent("agent_two")
        agent_registry.register(agent1)
        agent_registry.register(agent2)
        agents = agent_registry.list()
        assert len(agents) == 2
        assert "agent_one" in agents
        assert "agent_two" in agents
        assert agents["agent_one"] is agent1
        assert agents["agent_two"] is agent2

    def test_agent_registry_list_returns_copy(self, agent_registry):
        """Test that list() returns a copy, not the internal dictionary."""
        agent = ConcreteAgent("test_agent")
        agent_registry.register(agent)
        agents = agent_registry.list()
        agents["fake_agent"] = None
        assert agent_registry.has("fake_agent") is False

    def test_agent_registry_register_overwrites(self, agent_registry):
        """Test that registering agent with same name overwrites."""
        agent1 = ConcreteAgent("test_agent")
        agent2 = ConcreteAgent("test_agent")
        agent_registry.register(agent1)
        agent_registry.register(agent2)
        assert agent_registry.get("test_agent") is agent2

    def test_agent_registry_register_invalid_type(self, agent_registry):
        """Test registering non-BaseAgent raises TypeError."""
        with pytest.raises(TypeError):
            agent_registry.register("not_an_agent")

    def test_agent_registry_logger(self):
        """Test that registry has a logger."""
        registry = AgentRegistry()
        assert registry.logger is not None
        assert isinstance(registry.logger, logging.Logger)

    def test_agent_registry_with_different_agent_types(self, agent_registry):
        """Test registry with different agent types."""
        concrete_agent = ConcreteAgent("concrete")
        failing_agent = FailingAgent("failing")
        agent_registry.register(concrete_agent)
        agent_registry.register(failing_agent)
        assert agent_registry.get("concrete") is concrete_agent
        assert agent_registry.get("failing") is failing_agent

    def test_agent_registry_execute_registered_agent(
        self, agent_registry, execution_context
    ):
        """Test executing a registered agent through registry."""
        agent = ConcreteAgent("test_agent")
        agent_registry.register(agent)
        retrieved = agent_registry.get("test_agent")
        output = retrieved.execute(execution_context)
        assert output.status == "success"

    def test_agent_registry_state_isolation(self):
        """Test that multiple registries maintain isolated state."""
        registry1 = AgentRegistry()
        registry2 = AgentRegistry()
        agent1 = ConcreteAgent("agent")
        agent2 = FailingAgent("agent")
        registry1.register(agent1)
        registry2.register(agent2)
        assert registry1.get("agent") is agent1
        assert registry2.get("agent") is agent2
        assert registry1.get("agent") is not registry2.get("agent")
