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

def test_solve_function_invokes_modules():
    """Test orchestrator:solve references required modules."""
    with open('agents/orchestrator/functions/solve.md', 'r') as f:
        content = f.read()

    # Verify function signature
    assert "# Function: orchestrator:solve" in content
    assert "**Prefix:** `orchestrator:solve`" in content

    # Verify it invokes required modules
    assert "design_solver" in content
    assert "expert_panel_generator" in content

    # Verify input spec is present
    assert "## Input Specification" in content
    assert "problem: string" in content
    assert "dimensions: string[]" in content

    # Verify output spec is present
    assert "## Output" in content
    assert "solutions.md" in content
    assert "recommendation.md" in content
    assert "comparison-table.csv" in content
    assert "implementation-roadmap.json" in content

if __name__ == '__main__':
    test_ideate_function_invokes_modules()
    test_solve_function_invokes_modules()
    print("✓ All orchestrator functions passed structure tests")
