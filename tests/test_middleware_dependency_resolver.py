import pytest
from instructions_framework.middleware.dependency_resolver import DependencyResolverMiddleware
from instructions_framework.schema import (
    Instruction, InstructionMetadata, InstructionCategory,
    InstructionPrecedence, InstructionScope
)


def create_instruction(instruction_id, name, depends_on=None):
    """Helper to create instruction with dependencies"""
    metadata = InstructionMetadata(
        version="1.0",
        description=f"Instruction {name}",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
        depends_on=depends_on or []
    )
    return Instruction(
        id=instruction_id,
        name=name,
        category=InstructionCategory.CORE,
        metadata=metadata,
        content=f"Content for {name}"
    )


def test_dependency_resolver_sorts_by_dependencies():
    """Resolver orders instructions by dependencies"""
    # Create 3 instructions: B depends on A, C depends on B
    # Expected order: A, B, C
    instr_a = create_instruction("a", "A", depends_on=[])
    instr_b = create_instruction("b", "B", depends_on=["a"])
    instr_c = create_instruction("c", "C", depends_on=["b"])

    # Create in reverse order to ensure sorting actually happens
    middleware = DependencyResolverMiddleware()
    result = middleware.process([instr_c, instr_b, instr_a])

    # Should be sorted by dependencies
    assert len(result) == 3
    assert result[0].id == "a"
    assert result[1].id == "b"
    assert result[2].id == "c"


def test_dependency_resolver_detects_circular_dependencies():
    """Resolver detects circular dependency chains"""
    # Create circular: A depends on B, B depends on A
    instr_a = create_instruction("a", "A", depends_on=["b"])
    instr_b = create_instruction("b", "B", depends_on=["a"])

    middleware = DependencyResolverMiddleware()

    with pytest.raises(ValueError, match="Circular"):
        middleware.process([instr_a, instr_b])


def test_dependency_resolver_handles_no_dependencies():
    """Resolver handles instructions with no dependencies"""
    # All instructions have empty depends_on
    instr_a = create_instruction("a", "A", depends_on=[])
    instr_b = create_instruction("b", "B", depends_on=[])
    instr_c = create_instruction("c", "C", depends_on=[])

    middleware = DependencyResolverMiddleware()
    result = middleware.process([instr_a, instr_b, instr_c])

    # Should return all instructions
    assert len(result) == 3
    assert set(r.id for r in result) == {"a", "b", "c"}


def test_dependency_resolver_handles_missing_dependencies():
    """Resolver handles references to non-existent dependencies"""
    # A depends on non-existent B
    instr_a = create_instruction("a", "A", depends_on=["nonexistent"])
    instr_c = create_instruction("c", "C", depends_on=[])

    middleware = DependencyResolverMiddleware()
    result = middleware.process([instr_c, instr_a])

    # Should include both instructions, C can be processed first
    assert len(result) == 2
    # C should come before A since A has unmet dependency
    assert result[0].id == "c"
    assert result[1].id == "a"


def test_dependency_resolver_handles_complex_dependencies():
    """Resolver handles complex dependency graphs"""
    # D depends on B and C
    # B depends on A
    # C depends on A
    # Expected order: A, then B and C (in any order), then D
    instr_a = create_instruction("a", "A", depends_on=[])
    instr_b = create_instruction("b", "B", depends_on=["a"])
    instr_c = create_instruction("c", "C", depends_on=["a"])
    instr_d = create_instruction("d", "D", depends_on=["b", "c"])

    middleware = DependencyResolverMiddleware()
    result = middleware.process([instr_d, instr_a, instr_c, instr_b])

    assert len(result) == 4
    assert result[0].id == "a"
    # B and C can be in any order but both must be before D
    assert {result[1].id, result[2].id} == {"b", "c"}
    assert result[3].id == "d"


def test_dependency_resolver_detects_self_circular_dependency():
    """Resolver detects self-circular dependency"""
    # A depends on itself
    instr_a = create_instruction("a", "A", depends_on=["a"])

    middleware = DependencyResolverMiddleware()

    with pytest.raises(ValueError, match="Circular"):
        middleware.process([instr_a])


def test_dependency_resolver_handles_empty_list():
    """Resolver handles empty instruction list"""
    middleware = DependencyResolverMiddleware()
    result = middleware.process([])

    assert result == []


def test_dependency_resolver_tracks_circular_dependencies():
    """Resolver tracks circular dependency errors"""
    # A depends on B, B depends on A
    instr_a = create_instruction("a", "A", depends_on=["b"])
    instr_b = create_instruction("b", "B", depends_on=["a"])

    middleware = DependencyResolverMiddleware()

    try:
        middleware.process([instr_a, instr_b])
    except ValueError:
        pass

    # Should have tracked the circular dependency
    assert len(middleware.circular_dependencies) > 0
