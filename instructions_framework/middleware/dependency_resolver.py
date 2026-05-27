"""Dependency resolver middleware using topological sort"""

from typing import List, Dict, Set
from collections import defaultdict, deque
from ..schema import Instruction
from .base import InstructionMiddleware


class DependencyResolverMiddleware(InstructionMiddleware):
    """Resolves instruction dependencies using topological sort (Kahn's algorithm)"""

    def __init__(self):
        self.circular_dependencies: List[str] = []

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Sort instructions by dependencies using topological sort.
        Detects and raises on circular dependencies.

        Args:
            instructions: List of instructions to process

        Returns:
            List of instructions sorted by dependency order

        Raises:
            ValueError: If circular dependencies are detected
        """
        self.circular_dependencies = []

        if not instructions:
            return instructions

        # Build instruction ID map
        id_map = {instr.id: instr for instr in instructions}

        # Detect and raise on circular dependencies
        if self._has_circular_dependency(id_map):
            raise ValueError("Circular dependencies detected")

        # Topological sort using Kahn's algorithm
        return self._topological_sort(instructions, id_map)

    def _has_circular_dependency(self, id_map: Dict[str, Instruction]) -> bool:
        """
        Detect circular dependencies using DFS.

        Args:
            id_map: Dictionary mapping instruction IDs to instructions

        Returns:
            True if circular dependency exists, False otherwise
        """
        visited = set()
        rec_stack = set()

        def has_cycle(instruction_id: str) -> bool:
            """DFS helper to detect cycle"""
            visited.add(instruction_id)
            rec_stack.add(instruction_id)

            instruction = id_map.get(instruction_id)
            if instruction:
                for dependency_id in instruction.metadata.depends_on:
                    if dependency_id not in visited:
                        if has_cycle(dependency_id):
                            return True
                    elif dependency_id in rec_stack:
                        self.circular_dependencies.append(instruction_id)
                        return True

            rec_stack.remove(instruction_id)
            return False

        # Check each instruction for cycles
        for instruction_id in id_map:
            if instruction_id not in visited:
                if has_cycle(instruction_id):
                    return True

        return False

    def _topological_sort(
        self,
        instructions: List[Instruction],
        id_map: Dict[str, Instruction]
    ) -> List[Instruction]:
        """
        Perform topological sort using Kahn's algorithm.

        Args:
            instructions: List of instructions to sort
            id_map: Dictionary mapping instruction IDs to instructions

        Returns:
            Topologically sorted list of instructions
        """
        # Build adjacency list and in-degree map
        graph: Dict[str, Set[str]] = defaultdict(set)  # id -> set of dependents
        in_degree: Dict[str, int] = defaultdict(int)

        # Initialize all instructions with in_degree 0
        for instruction in instructions:
            if instruction.id not in in_degree:
                in_degree[instruction.id] = 0

        # Build graph
        for instruction in instructions:
            instr_id = instruction.id
            for dependency_id in instruction.metadata.depends_on:
                # Only add edge if dependency exists in instruction set
                if dependency_id in id_map:
                    graph[dependency_id].add(instr_id)
                    in_degree[instr_id] += 1
                # If dependency doesn't exist, it becomes a "floating" dependency
                # We don't increase in_degree for non-existent dependencies

        # Find all nodes with in_degree 0
        queue = deque([
            instr_id for instr_id in in_degree
            if in_degree[instr_id] == 0
        ])

        sorted_instructions = []

        # Process nodes with in_degree 0
        while queue:
            current_id = queue.popleft()
            sorted_instructions.append(id_map[current_id])

            # Reduce in_degree for dependents
            for dependent_id in graph[current_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        return sorted_instructions
