import pytest
from pathlib import Path
from instructions_framework.pipeline import InstructionPipeline

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures" / "sample_instructions"

def test_pipeline_basic_workflow(fixtures_dir):
    """Pipeline loads and validates instructions"""
    pipeline = InstructionPipeline(fixtures_dir)
    result = pipeline.run()

    assert len(result) > 0
    # All results should be valid
    for instruction in result:
        assert len(instruction.validate()) == 0
