"""Loader for hierarchical instruction file system"""

import logging
from pathlib import Path
from typing import List, Dict
from .schema import Instruction
from .parser import parse_instruction_file

logger = logging.getLogger(__name__)


class InstructionLoader:
    """Load instructions from hierarchical directory structure.

    Directory structure:
    - global/: Global instructions applicable to all agents
    - providers/{provider_name}/: Provider-specific instructions (claude, openai, etc.)
    - agents/{agent_name}/: Agent-specific instructions
    """

    def __init__(self, instructions_dir: Path):
        """Initialize the InstructionLoader.

        Args:
            instructions_dir: Root directory containing global/, providers/, agents/ subdirectories
        """
        self.instructions_dir = Path(instructions_dir)
        self._cache: Dict[str, List[Instruction]] = {}

    def load_global(self) -> List[Instruction]:
        """Load instructions from global/ directory.

        Returns:
            List of Instruction objects from global/ directory.
            Returns empty list if directory doesn't exist.
        """
        cache_key = "global"
        if cache_key in self._cache:
            return self._cache[cache_key]

        global_dir = self.instructions_dir / "global"
        instructions = self._load_from_directory(global_dir)

        self._cache[cache_key] = instructions
        return instructions

    def load_provider(self, provider: str) -> List[Instruction]:
        """Load instructions from providers/{provider}/ directory.

        Args:
            provider: Provider name (e.g., "claude", "openai", "gemini")

        Returns:
            List of Instruction objects for the provider.
            Returns empty list if directory doesn't exist.
        """
        cache_key = f"provider_{provider}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        provider_dir = self.instructions_dir / "providers" / provider
        instructions = self._load_from_directory(provider_dir)

        self._cache[cache_key] = instructions
        return instructions

    def load_agent(self, agent_name: str) -> List[Instruction]:
        """Load instructions from agents/{agent_name}/ directory.

        Args:
            agent_name: Agent name (e.g., "implementation_agent")

        Returns:
            List of Instruction objects for the agent.
            Returns empty list if directory doesn't exist.
        """
        cache_key = f"agent_{agent_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        agent_dir = self.instructions_dir / "agents" / agent_name
        instructions = self._load_from_directory(agent_dir)

        self._cache[cache_key] = instructions
        return instructions

    def load_all(self) -> List[Instruction]:
        """Load all instructions from all hierarchy levels.

        Combines instructions from:
        - global/
        - providers/* (all subdirectories)
        - agents/* (all subdirectories)

        Returns:
            List of all Instruction objects from all levels.
        """
        cache_key = "all"
        if cache_key in self._cache:
            return self._cache[cache_key]

        all_instructions = []

        # Load global instructions
        all_instructions.extend(self.load_global())

        # Load all provider instructions
        providers_dir = self.instructions_dir / "providers"
        if providers_dir.exists() and providers_dir.is_dir():
            for provider_dir in providers_dir.iterdir():
                if provider_dir.is_dir() and not provider_dir.name.startswith("."):
                    provider_name = provider_dir.name
                    all_instructions.extend(self.load_provider(provider_name))

        # Load all agent instructions
        agents_dir = self.instructions_dir / "agents"
        if agents_dir.exists() and agents_dir.is_dir():
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                    agent_name = agent_dir.name
                    all_instructions.extend(self.load_agent(agent_name))

        self._cache[cache_key] = all_instructions
        return all_instructions

    def _load_from_directory(self, directory: Path) -> List[Instruction]:
        """Load all instruction files from a directory.

        Loads all .md files from the given directory, skipping hidden files
        (starting with .) and handling malformed files gracefully.

        Args:
            directory: Directory to load instructions from

        Returns:
            List of Instruction objects loaded from the directory.
            Returns empty list if directory doesn't exist.
        """
        if not directory.exists():
            return []

        if not directory.is_dir():
            return []

        instructions = []

        for file_path in sorted(directory.glob("*.md")):
            # Skip hidden files
            if file_path.name.startswith("."):
                continue

            try:
                instruction = parse_instruction_file(file_path)
                instructions.append(instruction)
            except Exception as e:
                # Log warning and skip malformed files without crashing
                logger.warning(
                    f"Failed to parse instruction file {file_path}: {e}"
                )
                continue

        return instructions
