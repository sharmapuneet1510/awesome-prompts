"""Instruction processing pipeline"""

from pathlib import Path
from typing import List

from .loader import InstructionLoader
from .schema import Instruction
from .middleware.base import InstructionMiddleware
from .middleware.validator import ValidationMiddleware


class InstructionPipeline:
    """Six-stage instruction processing pipeline"""

    def __init__(self, instructions_dir: Path):
        """
        Initialize pipeline.

        Pipeline stages:
        1. Load - Load from file system
        2. Parse - Extract YAML + Markdown (done by loader)
        3. Validate - Check schema completeness
        4. Transform - Apply middleware
        5. Resolve - Hierarchical resolution
        6. Export - (done in exporters)
        """
        self.instructions_dir = Path(instructions_dir)
        self.middleware: List[InstructionMiddleware] = [
            ValidationMiddleware(),
        ]
        self.loader = InstructionLoader(instructions_dir)

    def add_middleware(self, middleware: InstructionMiddleware) -> "InstructionPipeline":
        """Add middleware to pipeline"""
        self.middleware.append(middleware)
        return self

    def run(self) -> List[Instruction]:
        """Run the complete pipeline"""
        # Stage 1 & 2: Load and Parse
        instructions = self.loader.load_all()

        # Stage 3 & 4: Validate and Transform
        for mw in self.middleware:
            instructions = mw.process(instructions)

        # Stage 5: Resolve (implemented in separate task)
        # Stage 6: Export (handled by exporters)

        return instructions
