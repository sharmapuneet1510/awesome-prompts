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

if __name__ == '__main__':
    test_expert_panel_generator_structure()
    print("✓ expert_panel_generator module structure test passed")
