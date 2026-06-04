import json
import sys
sys.path.insert(0, '/Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts')

def test_expert_panel_generator_structure():
    """Test that expert_panel_generator module can be imported and has required sections."""
    with open('agents/orchestrator/modules/expert_panel_generator.md', 'r') as f:
        content = f.read()

    # Verify required sections
    required_sections = [
        "# Expert Panel Generator Module",
        "## Purpose",
        "## Invocation",
        "## Expert Types Generated",
        "## Process",
        "## Output Format",
        "## Usage Example"
    ]

    for section in required_sections:
        assert section in content, f"Missing section: {section}"

    # Verify all 5 expert types are documented
    expert_types = [
        "Technical Architect",
        "DevOps/Infrastructure Specialist",
        "Performance Engineer",
        "Security Specialist",
        "Product/Business Lead"
    ]

    for expert in expert_types:
        assert expert in content, f"Missing expert type: {expert}"

def test_ideation_engine_structure():
    """Test ideation_engine module has all required process phases and outputs."""
    with open('agents/orchestrator/modules/ideation_engine.md', 'r') as f:
        content = f.read()

    # Verify required phases
    phases = [
        "### Phase 1: Clarification",
        "### Phase 2: Concept Refinement",
        "### Phase 3: Project Planning"
    ]

    for phase in phases:
        assert phase in content, f"Missing phase: {phase}"

    # Verify 7 clarification questions
    questions = [
        "Core Purpose",
        "Target Users",
        "Success Definition",
        "Constraints",
        "Differentiation",
        "MVP Scope",
        "Key Risks"
    ]

    for question in questions:
        assert question in content, f"Missing question: {question}"

    # Verify output sections
    outputs = [
        "idea_specification",
        "project_plan",
        "raid_analysis",
        "timeline"
    ]

    for output in outputs:
        assert output in content, f"Missing output section: {output}"

def test_design_solver_structure():
    """Test design_solver module has all required phases and dimensions."""
    with open('agents/orchestrator/modules/design_solver.md', 'r') as f:
        content = f.read()

    # Verify required phases
    phases = [
        "### Phase 1: Diagnosis",
        "### Phase 2: Solution Generation",
        "### Phase 3: Trade-Off Analysis",
        "### Phase 4: Recommendation"
    ]

    for phase in phases:
        assert phase in content, f"Missing phase: {phase}"

    # Verify solution dimensions
    dimensions = [
        "database_design",
        "api_throttling",
        "project_structure"
    ]

    for dimension in dimensions:
        assert dimension in content, f"Missing dimension: {dimension}"

if __name__ == '__main__':
    test_expert_panel_generator_structure()
    test_ideation_engine_structure()
    test_design_solver_structure()
    print("✓ All module structure tests passed")
