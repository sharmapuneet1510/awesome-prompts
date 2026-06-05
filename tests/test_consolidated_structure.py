"""
Comprehensive test suite for consolidated repository structure.

Tests validate:
- Directory structure consolidation (no src/)
- File discovery and parsing
- Exporter functionality
- Platform export targets
- Documentation consistency
- Git state validation
"""

import sys
from pathlib import Path
import subprocess
import json
import re

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ═══════════════════════════════════════════════════════════════════════════════
# TEST FIXTURES & HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

REPO_ROOT = Path(__file__).parent.parent
REQUIRED_DIRS = {
    "agents": "Agent definitions (no subdirs at root)",
    "skills": "Reusable skill modules",
    "hooks": "Git hooks and scripts",
    "instructions": "Universal rules and intake forms",
    "tools": "Utilities and frameworks",
    "docs": "Documentation",
    "tests": "Test suite",
}

FORBIDDEN_DIRS = {
    "src": "Should be consolidated to root level",
}

EXPORTER_PLATFORMS = [
    "copilot", "claude", "cursor", "windsurf",
    "gemini", "continue", "openai", "aider"
]


class TestResult:
    """Track test results"""
    def __init__(self, name, passed, details=""):
        self.name = name
        self.passed = passed
        self.details = details

    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} | {self.name}" + (f" — {self.details}" if self.details else "")


def run_command(cmd, cwd=REPO_ROOT):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip(), result.returncode == 0
    except subprocess.TimeoutExpired:
        return "TIMEOUT", False
    except Exception as e:
        return str(e), False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST SUITES
# ═══════════════════════════════════════════════════════════════════════════════

class TestDirectoryStructure:
    """Test 1: Validate directory structure consolidation"""

    @staticmethod
    def test_required_dirs_exist():
        """All required directories exist at root"""
        results = []
        for dir_name, description in REQUIRED_DIRS.items():
            path = REPO_ROOT / dir_name
            exists = path.is_dir()
            results.append(TestResult(
                f"Directory: {dir_name}/",
                exists,
                description if exists else f"MISSING: {path}"
            ))
        return results

    @staticmethod
    def test_src_removed():
        """src/ directory should not exist"""
        src_path = REPO_ROOT / "src"
        exists = src_path.exists()
        result = TestResult(
            "src/ directory removed",
            not exists,
            f"Found at {src_path}" if exists else "✓ Completely removed"
        )
        return [result]

    @staticmethod
    def test_no_forbidden_dirs():
        """Forbidden directories don't exist"""
        results = []
        for dir_name, reason in FORBIDDEN_DIRS.items():
            path = REPO_ROOT / dir_name
            exists = path.exists()
            results.append(TestResult(
                f"No {dir_name}/ directory",
                not exists,
                reason if exists else "✓ Correctly absent"
            ))
        return results

    @staticmethod
    def test_agents_structure():
        """agents/ contains agent files + orchestrator subdirs"""
        agents_dir = REPO_ROOT / "agents"
        results = []

        # Check for agent files
        agent_files = list(agents_dir.glob("*_agent.md"))
        has_agents = len(agent_files) >= 5
        results.append(TestResult(
            "agents/ has 5+ agent definition files",
            has_agents,
            f"Found {len(agent_files)} agent files"
        ))

        # Check for orchestrator subdirs
        orchestrator_dir = agents_dir / "orchestrator"
        has_orchestrator = orchestrator_dir.is_dir()
        results.append(TestResult(
            "agents/orchestrator/ subdirectory exists",
            has_orchestrator,
            "With modules and functions"
        ))

        if has_orchestrator:
            modules = list((orchestrator_dir / "modules").glob("*.md"))
            functions = list((orchestrator_dir / "functions").glob("*.md"))
            results.append(TestResult(
                "orchestrator/modules/ has files",
                len(modules) > 0,
                f"Found {len(modules)} modules"
            ))
            results.append(TestResult(
                "orchestrator/functions/ has files",
                len(functions) > 0,
                f"Found {len(functions)} functions"
            ))

        return results


class TestFileDiscovery:
    """Test 2: Validate file discovery and counts"""

    @staticmethod
    def test_agent_files():
        """Verify agent definition files"""
        agents_dir = REPO_ROOT / "agents"
        agent_files = list(agents_dir.glob("*_agent.md"))
        expected_count = 5
        return [TestResult(
            f"Agent files: {len(agent_files)} found",
            len(agent_files) == expected_count,
            f"Expected {expected_count}: orchestrator, architect, implementer, quality, business_analyst"
        )]

    @staticmethod
    def test_skill_files():
        """Verify skill files"""
        skills_dir = REPO_ROOT / "skills"
        skill_files = list(skills_dir.glob("*_skill.md"))
        expected_count = 24
        return [TestResult(
            f"Skill files: {len(skill_files)} found",
            len(skill_files) == expected_count,
            f"Expected {expected_count} reusable skills"
        )]

    @staticmethod
    def test_hook_files():
        """Verify hook files"""
        hooks_dir = REPO_ROOT / "hooks"
        hook_files = list(hooks_dir.glob("*")) + list(hooks_dir.glob("*.*"))
        hook_files = [f for f in hook_files if f.is_file()]
        has_hooks = len(hook_files) > 0
        return [TestResult(
            f"Hook files found: {len(hook_files)}",
            has_hooks,
            "Scripts for pre-commit, user-prompt-submit, etc."
        )]

    @staticmethod
    def test_instruction_files():
        """Verify instruction files"""
        instructions_dir = REPO_ROOT / "instructions"
        instruction_files = list(instructions_dir.glob("*.md"))
        expected_count = 4
        return [TestResult(
            f"Instruction files: {len(instruction_files)} found",
            len(instruction_files) == expected_count,
            f"Expected {expected_count}: master_instruction_set, java_intake, python_intake, technical_intake"
        )]

    @staticmethod
    def test_module_files():
        """Verify module files"""
        modules_dir = REPO_ROOT / "agents" / "orchestrator" / "modules"
        module_files = list(modules_dir.glob("*.md"))
        expected_count = 3
        return [TestResult(
            f"Module files: {len(module_files)} found",
            len(module_files) == expected_count,
            f"Expected {expected_count}: design_solver, expert_panel_generator, ideation_engine"
        )]

    @staticmethod
    def test_function_files():
        """Verify function files"""
        functions_dir = REPO_ROOT / "agents" / "orchestrator" / "functions"
        function_files = list(functions_dir.glob("*.md"))
        expected_count = 2
        return [TestResult(
            f"Function files: {len(function_files)} found",
            len(function_files) == expected_count,
            f"Expected {expected_count}: ideate, solve"
        )]


class TestExporter:
    """Test 3: Validate exporter functionality"""

    @staticmethod
    def test_exporter_exists():
        """exporter.py exists and is executable"""
        exporter_path = REPO_ROOT / "tools" / "exporter.py"
        exists = exporter_path.exists()
        return [TestResult(
            "tools/exporter.py exists",
            exists,
            "Python script for platform exports"
        )]

    @staticmethod
    def test_exporter_list():
        """Exporter can list all items"""
        output, success = run_command("python3 tools/exporter.py --list")
        has_skills = "Skills:" in output
        has_agents = "Agents:" in output
        has_modules = "Modules:" in output
        has_functions = "Functions:" in output

        all_sections = has_skills and has_agents and has_modules and has_functions
        return [TestResult(
            "Exporter --list finds all sections",
            success and all_sections,
            "Skills, Agents, Modules, Functions discovered"
        )]

    @staticmethod
    def test_exporter_discovery_counts():
        """Exporter discovers correct counts"""
        output, success = run_command("python3 tools/exporter.py --list")

        results = []

        # Parse counts from output
        if "Skills:" in output:
            skills_section = output.split("Skills:")[1].split("Agents:")[0]
            skill_count = len([l for l in skills_section.split("\n") if l.strip() and not l.startswith("Skills")])
            results.append(TestResult(
                f"Exporter discovers 24 skills",
                skill_count >= 24,
                f"Found {skill_count}"
            ))

        if "Agents:" in output:
            agents_section = output.split("Agents:")[1].split("Modules:")[0]
            agent_count = len([l for l in agents_section.split("\n") if l.strip() and not l.startswith("Agents")])
            results.append(TestResult(
                f"Exporter discovers 5 agents",
                agent_count >= 5,
                f"Found {agent_count}"
            ))

        return results

    @staticmethod
    def test_exporter_dry_run():
        """Exporter --dry-run completes successfully"""
        output, success = run_command("python3 tools/exporter.py --dry-run")

        has_summary = "EXPORT SUMMARY" in output
        expected_stats = all(x in output for x in [
            "Skills", "Agents", "Modules", "Functions", "Hooks"
        ])

        return [TestResult(
            "Exporter --dry-run succeeds",
            success and has_summary and expected_stats,
            "Export summary with all platform counts"
        )]

    @staticmethod
    def test_exporter_platform_targets():
        """Exporter supports all 8 platforms"""
        output, success = run_command("python3 tools/exporter.py --list 2>&1")

        results = []
        for platform in EXPORTER_PLATFORMS:
            # Just verify exporter runs without error for each platform
            test_output, test_success = run_command(f"python3 tools/exporter.py --target {platform} --dry-run")
            results.append(TestResult(
                f"Platform: {platform}",
                test_success,
                "Exporter supports this target"
            ))

        return results


class TestGitIntegration:
    """Test 4: Validate git state and commits"""

    @staticmethod
    def test_git_status():
        """Git repository is clean (ignoring untracked files)"""
        output, success = run_command("git status")
        # Check for uncommitted tracked changes (ignore untracked files like .cursorrules)
        no_uncommitted = ("nothing to commit" in output or "working tree clean" in output or
                         "nothing added to commit" in output)
        return [TestResult(
            "Git working tree clean (tracked files)",
            success and no_uncommitted,
            "No uncommitted tracked changes (untracked files OK)"
        )]

    @staticmethod
    def test_git_branch():
        """On main branch and up to date"""
        output, success = run_command("git rev-parse --abbrev-ref HEAD")
        on_main = output.strip() == "main"

        status_output, status_success = run_command("git status")
        up_to_date = "up to date" in status_output or "Your branch is up to date" in status_output

        return [TestResult(
            "On main branch and up to date",
            on_main and up_to_date,
            "Ready for collaboration"
        )]

    @staticmethod
    def test_recent_commits():
        """Recent consolidation commits present"""
        output, success = run_command("git log --oneline -10")

        results = []
        results.append(TestResult(
            "Consolidation commits found",
            "consolidate" in output.lower() or "refactor" in output.lower(),
            "Repository structure consolidation in history"
        ))

        return results


class TestDocumentation:
    """Test 5: Validate documentation consistency"""

    @staticmethod
    def test_readme_structure():
        """README.md has correct structure references"""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text()

        results = []

        # Check for correct structure (no src/)
        has_root_agents = "├── 📋 agents/" in content
        results.append(TestResult(
            "README shows agents at root",
            has_root_agents,
            "agents/ not under src/"
        ))

        # Check for skill references
        has_root_skills = "├── 💡 skills/" in content
        results.append(TestResult(
            "README shows skills at root",
            has_root_skills,
            "skills/ not under src/"
        ))

        # Check for no src/ references in structure section
        no_src_structure = "├── 🔧 src/" not in content
        results.append(TestResult(
            "README doesn't show src/ directory",
            no_src_structure,
            "Structure is consolidated"
        ))

        return results

    @staticmethod
    def test_claude_md():
        """CLAUDE.md has correct structure references"""
        claude_md = REPO_ROOT / "CLAUDE.md"
        content = claude_md.read_text()

        results = []

        # Check for agents at root
        has_agents = "├── agents/" in content
        results.append(TestResult(
            "CLAUDE.md references agents at root",
            has_agents,
            "Agent definitions at root level"
        ))

        # Check for skills at root
        has_skills = "├── skills/" in content
        results.append(TestResult(
            "CLAUDE.md references skills at root",
            has_skills,
            "Skills at root level"
        ))

        return results

    @staticmethod
    def test_gitignore_platforms():
        """gitignore properly lists platform exports"""
        gitignore = REPO_ROOT / ".gitignore"
        content = gitignore.read_text()

        results = []

        platforms_to_check = {
            ".github/": "Copilot",
            ".cursor/": "Cursor IDE",
            ".windsurf/": "Windsurf IDE",
            ".gemini/": "Gemini CLI",
            ".continue/": "Continue IDE",
            ".aider/": "Aider CLI",
        }

        for pattern, name in platforms_to_check.items():
            has_pattern = pattern in content
            results.append(TestResult(
                f"gitignore excludes {pattern}",
                has_pattern,
                name
            ))

        # Check .claude/ is NOT in the exclusion section (it's tracked, not ignored)
        # .claude/ appears in gitignore but only .claude/settings.local.json is excluded
        has_claude_settings_only = ".claude/settings.local.json" in content and ".claude/skills" not in content
        results.append(TestResult(
            "gitignore allows .claude/ (tracked)",
            has_claude_settings_only,
            ".claude/ is intentionally committed, only settings.local.json ignored"
        ))

        return results


class TestConsistency:
    """Test 6: Cross-file consistency checks"""

    @staticmethod
    def test_no_src_references():
        """No references to src/ in key files"""
        files_to_check = {
            "CLAUDE.md": REPO_ROOT / "CLAUDE.md",
            "README.md": REPO_ROOT / "README.md",
            ".gitignore": REPO_ROOT / ".gitignore",
        }

        results = []
        for name, path in files_to_check.items():
            content = path.read_text()
            # Count references to src/agents, src/skills, src/hooks, src/instructions
            src_refs = len(re.findall(r'src/(agents|skills|hooks|instructions)', content))
            results.append(TestResult(
                f"{name} has no src/ directory references",
                src_refs == 0,
                f"Found {src_refs} references (should be 0)"
            ))

        return results

    @staticmethod
    def test_agents_agent_files():
        """All *_agent.md files are in agents/ directory (root level, not subdirs)"""
        # Only check root-level agents/ directory, not exported versions
        agent_files = list((REPO_ROOT / "agents").glob("*_agent.md"))
        expected_count = 5
        correct_count = len(agent_files) == expected_count

        return [TestResult(
            f"All {expected_count} agent files in agents/ directory",
            correct_count,
            f"Found {len(agent_files)} agent files at root level"
        )]

    @staticmethod
    def test_skills_skill_files():
        """All *_skill.md files are in skills/ directory (root level, not subdirs)"""
        # Only check root-level skills/ directory, not exported versions
        skill_files = list((REPO_ROOT / "skills").glob("*_skill.md"))
        expected_count = 24
        correct_count = len(skill_files) == expected_count

        return [TestResult(
            f"All {expected_count} skill files in skills/ directory",
            correct_count,
            f"Found {len(skill_files)} skill files at root level"
        )]


# ═══════════════════════════════════════════════════════════════════════════════
# TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_all_tests():
    """Execute all test suites and generate report"""

    test_classes = [
        TestDirectoryStructure,
        TestFileDiscovery,
        TestExporter,
        TestGitIntegration,
        TestDocumentation,
        TestConsistency,
    ]

    all_results = []

    print("\n" + "="*80)
    print("COMPREHENSIVE REPOSITORY STRUCTURE TEST SUITE")
    print("="*80 + "\n")

    for test_class in test_classes:
        print(f"\n🧪 {test_class.__doc__}")
        print("-" * 80)

        for method_name in dir(test_class):
            if method_name.startswith("test_"):
                method = getattr(test_class, method_name)
                try:
                    results = method()
                    if isinstance(results, list):
                        for result in results:
                            print(f"  {result}")
                            all_results.append(result)
                    else:
                        print(f"  {results}")
                        all_results.append(results)
                except Exception as e:
                    error_result = TestResult(method_name, False, str(e))
                    print(f"  {error_result}")
                    all_results.append(error_result)

    # Summary
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests:  {total}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {total - passed}")
    print(f"Pass Rate:    {pass_rate:.1f}%")
    print("="*80 + "\n")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Repository is fully consolidated and working correctly!")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the output above.")

    print()
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
