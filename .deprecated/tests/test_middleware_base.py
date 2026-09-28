import pytest
from instructions_framework.middleware.base import InstructionMiddleware
from instructions_framework.schema import Instruction, InstructionMetadata, InstructionCategory, InstructionPrecedence, InstructionScope

class SimpleLoggingMiddleware(InstructionMiddleware):
    """Simple middleware for testing"""
    def __init__(self):
        self.processed_count = 0

    def process(self, instructions):
        self.processed_count = len(instructions)
        return instructions

def test_middleware_base_process():
    """Middleware base class can process instructions"""
    middleware = SimpleLoggingMiddleware()

    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    instruction = Instruction(
        id="test",
        name="Test",
        category=InstructionCategory.CORE,
        metadata=metadata,
        content="Test content",
    )

    result = middleware.process([instruction])
    assert len(result) == 1
    assert middleware.processed_count == 1
