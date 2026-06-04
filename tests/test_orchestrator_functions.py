import json
import sys
sys.path.insert(0, '/Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts')

def test_ideate_function_invokes_modules():
    """Test orchestrator:ideate references required modules."""
    with open('agents/orchestrator/functions/ideate.md', 'r') as f:
        content = f.read()

    # Verify function signature
    assert "# Function: orchestrator:ideate" in content
    assert "**Prefix:** `orchestrator:ideate`" in content

    # Verify it invokes required modules
    assert "ideation_engine" in content
    assert "expert_panel_generator" in content

    # Verify input spec is present
    assert "## Input Specification" in content
    assert "idea: string" in content

    # Verify output spec is present
    assert "## Output" in content
    assert "idea-spec.md" in content
    assert "project-plan.json" in content
    assert "raid-analysis.md" in content
    assert "project-plan.csv" in content

if __name__ == '__main__':
    test_ideate_function_invokes_modules()
    print("✓ orchestrator:ideate function structure test passed")
