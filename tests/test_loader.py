"""Tests for InstructionLoader - hierarchical file system loader"""

import pytest
from pathlib import Path
from instructions_framework.loader import InstructionLoader
from instructions_framework import Instruction


class TestInstructionLoader:
    """Test suite for InstructionLoader class"""

    @pytest.fixture
    def fixture_dir(self):
        """Path to test fixtures directory"""
        return Path(__file__).parent / "fixtures" / "sample_instructions"

    @pytest.fixture
    def loader(self, fixture_dir):
        """Create an InstructionLoader instance with test fixtures"""
        return InstructionLoader(fixture_dir)

    def test_loader_loads_global_instructions(self, loader):
        """Test loading instructions from global/ directory"""
        global_instructions = loader.load_global()

        # Verify results are returned
        assert isinstance(global_instructions, list)
        assert len(global_instructions) > 0

        # Verify loaded instructions
        assert all(isinstance(inst, Instruction) for inst in global_instructions)

        # Verify specific instruction is loaded
        instruction_ids = [inst.id for inst in global_instructions]
        assert "core_rules" in instruction_ids

        # Verify scope is global
        for inst in global_instructions:
            assert inst.metadata.scope.value == "global"

    def test_loader_loads_provider_instructions(self, loader):
        """Test loading instructions from providers/X/ directory"""
        provider_instructions = loader.load_provider("claude")

        # Verify results are returned
        assert isinstance(provider_instructions, list)
        assert len(provider_instructions) > 0

        # Verify loaded instructions
        assert all(isinstance(inst, Instruction) for inst in provider_instructions)

        # Verify specific instruction is loaded
        instruction_ids = [inst.id for inst in provider_instructions]
        assert "formatting" in instruction_ids

        # Verify scope is provider
        for inst in provider_instructions:
            assert inst.metadata.scope.value == "provider"

    def test_loader_loads_agent_instructions(self, loader):
        """Test loading instructions from agents/X/ directory"""
        agent_instructions = loader.load_agent("implementation_agent")

        # Verify results are returned
        assert isinstance(agent_instructions, list)
        assert len(agent_instructions) > 0

        # Verify loaded instructions
        assert all(isinstance(inst, Instruction) for inst in agent_instructions)

        # Verify specific instruction is loaded
        instruction_ids = [inst.id for inst in agent_instructions]
        assert "constraints" in instruction_ids

        # Verify scope is agent
        for inst in agent_instructions:
            assert inst.metadata.scope.value == "agent"

    def test_loader_loads_all_instructions(self, loader):
        """Test loading all instructions from all hierarchy levels"""
        all_instructions = loader.load_all()

        # Verify results are returned
        assert isinstance(all_instructions, list)
        assert len(all_instructions) >= 3  # At least global + provider + agent

        # Verify all are Instruction objects
        assert all(isinstance(inst, Instruction) for inst in all_instructions)

        # Verify instructions from all levels are present
        instruction_ids = [inst.id for inst in all_instructions]
        assert "core_rules" in instruction_ids  # From global/
        assert "formatting" in instruction_ids  # From providers/claude/
        assert "constraints" in instruction_ids  # From agents/implementation_agent/

        # Verify scopes are represented
        scopes = {inst.metadata.scope.value for inst in all_instructions}
        assert "global" in scopes
        assert "provider" in scopes
        assert "agent" in scopes

    def test_loader_caches_results(self, loader):
        """Test that loader caches results and returns same object on second load"""
        # Load global instructions twice
        first_load = loader.load_global()
        second_load = loader.load_global()

        # Verify same object reference is returned (caching works)
        assert first_load is second_load

        # Load provider instructions twice
        first_provider = loader.load_provider("claude")
        second_provider = loader.load_provider("claude")

        # Verify same object reference is returned
        assert first_provider is second_provider

        # Load agent instructions twice
        first_agent = loader.load_agent("implementation_agent")
        second_agent = loader.load_agent("implementation_agent")

        # Verify same object reference is returned
        assert first_agent is second_agent
