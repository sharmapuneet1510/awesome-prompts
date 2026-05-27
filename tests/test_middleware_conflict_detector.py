import pytest
from instructions_framework.middleware.conflict_detector import ConflictDetectorMiddleware
from instructions_framework.schema import (
    Instruction, InstructionMetadata, InstructionCategory,
    InstructionPrecedence, InstructionScope
)


def create_instruction(id_val, version="1.0", name=None):
    """Helper to create test instructions"""
    if name is None:
        name = f"Instruction {id_val}"

    metadata = InstructionMetadata(
        version=version,
        description=f"Test instruction {id_val}",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    return Instruction(
        id=id_val,
        name=name,
        category=InstructionCategory.CORE,
        metadata=metadata,
        content=f"Content for {id_val}",
    )


def test_conflict_detector_finds_duplicate_ids():
    """Detects multiple instructions with same ID"""
    middleware = ConflictDetectorMiddleware()

    instr1 = create_instruction("test")
    instr2 = create_instruction("test", version="2.0", name="Test Updated")

    result = middleware.process([instr1, instr2])

    # Should have 1 conflict
    assert len(middleware.conflicts) == 1
    assert "Duplicate ID 'test'" in middleware.conflicts[0]


def test_conflict_detector_finds_version_conflicts():
    """Detects same instruction with different versions"""
    middleware = ConflictDetectorMiddleware()

    instr1 = create_instruction("auth", version="1.0")
    instr2 = create_instruction("auth", version="2.0")
    instr3 = create_instruction("auth", version="3.0")

    result = middleware.process([instr1, instr2, instr3])

    # Should have 2 conflicts (for 2nd and 3rd duplicates)
    assert len(middleware.conflicts) == 2
    assert any("version 2.0 conflicts" in c for c in middleware.conflicts)
    assert any("version 3.0 conflicts" in c for c in middleware.conflicts)


def test_conflict_detector_filters_conflicts():
    """Filters out conflicting instructions - keeps first, removes duplicates"""
    middleware = ConflictDetectorMiddleware()

    instr1 = create_instruction("feature", version="1.0", name="Feature v1")
    instr2 = create_instruction("feature", version="2.0", name="Feature v2")
    instr3 = create_instruction("other", version="1.0", name="Other")

    result = middleware.process([instr1, instr2, instr3])

    # Should have 2 instructions (first feature + other)
    assert len(result) == 2
    assert result[0].id == "feature"
    assert result[0].metadata.version == "1.0"
    assert result[1].id == "other"


def test_conflict_detector_tracks_conflicts():
    """Tracks all found conflicts"""
    middleware = ConflictDetectorMiddleware()

    instr1 = create_instruction("a")
    instr2 = create_instruction("a", version="2.0")
    instr3 = create_instruction("b")
    instr4 = create_instruction("b", version="2.0")

    result = middleware.process([instr1, instr2, instr3, instr4])

    # Should have 2 conflicts
    assert len(middleware.conflicts) == 2
    assert middleware.conflicts[0] == (
        "Duplicate ID 'a': version 2.0 conflicts with version 1.0"
    )
    assert middleware.conflicts[1] == (
        "Duplicate ID 'b': version 2.0 conflicts with version 1.0"
    )


def test_conflict_detector_no_conflicts():
    """Handles instructions with no conflicts - returns all"""
    middleware = ConflictDetectorMiddleware()

    instr1 = create_instruction("first")
    instr2 = create_instruction("second")
    instr3 = create_instruction("third")

    result = middleware.process([instr1, instr2, instr3])

    # Should have no conflicts
    assert len(middleware.conflicts) == 0
    # Should return all instructions
    assert len(result) == 3
    assert result[0].id == "first"
    assert result[1].id == "second"
    assert result[2].id == "third"


def test_conflict_detector_handles_empty_list():
    """Handles empty instruction list"""
    middleware = ConflictDetectorMiddleware()

    result = middleware.process([])

    assert len(result) == 0
    assert len(middleware.conflicts) == 0


def test_conflict_detector_single_instruction():
    """Handles single instruction without conflicts"""
    middleware = ConflictDetectorMiddleware()

    instr = create_instruction("solo")

    result = middleware.process([instr])

    assert len(result) == 1
    assert len(middleware.conflicts) == 0
    assert result[0].id == "solo"
