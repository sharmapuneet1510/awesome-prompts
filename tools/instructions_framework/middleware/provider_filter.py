"""Provider Filter Middleware"""

from typing import List, Union
from ..schema import Instruction
from .base import InstructionMiddleware


class ProviderFilterMiddleware(InstructionMiddleware):
    """Filters instructions by provider applicability"""

    def __init__(self, providers: Union[str, List[str]]):
        """
        Initialize filter with target provider(s).

        Args:
            providers: Single provider string or list of provider strings
                      (e.g., "claude" or ["claude", "openai", "gemini"])
        """
        if isinstance(providers, str):
            self.providers = [providers]
        else:
            self.providers = providers if providers else []

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Filter instructions to only those applicable for target provider(s).

        An instruction is included if its metadata.applicability list contains
        at least one of the target providers (case-sensitive).

        Args:
            instructions: List of instructions to filter

        Returns:
            Filtered list with only applicable instructions
        """
        return [
            instr for instr in instructions
            if any(p in instr.metadata.applicability for p in self.providers)
        ]
