#!/usr/bin/env python3
"""
interactive_exporter.py — Enhanced interactive setup with agent/skill selection

Features:
1. Interactive project root selection
2. Platform multi-select with descriptions
3. Agent selection grouped by role with full descriptions
4. Skill selection grouped by tags with search/filter
5. Summary confirmation with stats
6. Export with progress indication

Usage:
    python3 tools/interactive_exporter.py
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from exporter import SkillFile, AgentFile, ExportOrchestrator


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'


def print_header():
    """Print welcome header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🤖 Autonomous Developer System - Interactive Setup 🤖    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")


def get_project_root() -> Path:
    """Ask user for project root directory."""
    print(f"{Colors.BOLD}Step 1: Project Root Directory{Colors.ENDC}")
    print("Where should the autonomous developer system be set up?")
    print(f"(Current directory: {Path.cwd()})\n")

    while True:
        user_input = input("Enter project root directory (or press Enter for current): ").strip()

        if not user_input:
            project_root = Path.cwd()
        else:
            project_root = Path(user_input).expanduser().resolve()

        if not project_root.exists():
            print(f"{Colors.WARNING}⚠️  Directory does not exist: {project_root}{Colors.ENDC}")
            print("Create it? (y/n): ", end="")
            if input().lower() == 'y':
                project_root.mkdir(parents=True, exist_ok=True)
                print(f"{Colors.OKGREEN}✓ Created directory{Colors.ENDC}\n")
                return project_root
            continue

        print(f"{Colors.OKGREEN}✓ Using: {project_root}{Colors.ENDC}\n")
        return project_root


def get_platforms() -> list[str]:
    """Ask user to select target platforms with enhanced UX."""
    print(f"{Colors.BOLD}Step 2: Target Platforms{Colors.ENDC}")
    print("Which platforms should we export to?\n")

    platforms = [
        ("claude", "Claude Code (Default)", "All Claude environments + .claude/"),
        ("copilot", "GitHub Copilot", "GitHub Copilot in .github/"),
        ("cursor", "Cursor IDE", "Cursor IDE rules in .cursor/"),
        ("windsurf", "Windsurf IDE", "Windsurf rules in .windsurf/"),
        ("gemini", "Google Gemini", "Gemini CLI in .gemini/"),
        ("continue", "Continue IDE", "Continue IDE prompts in .continue/"),
        ("openai", "OpenAI", "OpenAI format in tools/output/openai/"),
        ("aider", "Aider CLI", "Aider tool in .aider/"),
    ]

    selected_indices = set()
    default_selected = {0}  # Claude is default

    while True:
        print("\nAvailable platforms:")
        for idx, (slug, name, desc) in enumerate(platforms, 1):
            checkbox = "✓" if (idx - 1) in selected_indices else " "
            print(f"  {idx}. [{checkbox}] {name}")
            print(f"     {Colors.DIM}{desc}{Colors.ENDC}")

        print(f"\n{Colors.DIM}Enter numbers to toggle (space-separated), or press Enter to continue:{Colors.ENDC}")
        user_input = input("Selection: ").strip()

        if not user_input:
            if not selected_indices:
                selected_indices = default_selected
            break

        try:
            for num_str in user_input.split():
                num = int(num_str) - 1
                if 0 <= num < len(platforms):
                    if num in selected_indices:
                        selected_indices.discard(num)
                    else:
                        selected_indices.add(num)
                else:
                    print(f"{Colors.WARNING}Invalid number: {num_str}{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.WARNING}Please enter valid numbers{Colors.ENDC}")

    selected = [platforms[i][0] for i in sorted(selected_indices)]

    print(f"\n{Colors.OKGREEN}✓ Selected {len(selected)} platform(s):{Colors.ENDC}")
    for slug in selected:
        name = next(p[1] for p in platforms if p[0] == slug)
        print(f"  • {name}")
    print()

    return selected


def discover_skills_and_agents(repo_root: Path) -> tuple[list[SkillFile], list[AgentFile]]:
    """Discover all available skills and agents from source files."""
    try:
        orchestrator = ExportOrchestrator(repo_root)
        skills = orchestrator.discover_skills()
        agents = orchestrator.discover_agents()
        return skills, agents
    except Exception as e:
        print(f"{Colors.WARNING}⚠️  Could not discover items: {e}{Colors.ENDC}")
        return [], []


def select_agents(agents: list[AgentFile]) -> list[str]:
    """Interactive agent selection grouped by role."""
    if not agents:
        print(f"{Colors.WARNING}No agents found{Colors.ENDC}")
        return []

    print(f"{Colors.BOLD}Step 3a: Select Agents{Colors.ENDC}")
    print(f"Found {len(agents)} agent(s). Group by role:\n")

    # Group agents by role
    by_role = {}
    for agent in agents:
        if agent.role not in by_role:
            by_role[agent.role] = []
        by_role[agent.role].append(agent)

    selected = set()
    role_indices = {}
    global_idx = 1

    # Display agents grouped by role
    for role in sorted(by_role.keys()):
        print(f"{Colors.BOLD}{role.upper()}{Colors.ENDC}")
        for agent in sorted(by_role[role], key=lambda a: a.name):
            role_indices[global_idx] = agent.slug
            print(f"  {global_idx:2d}. [ ] {agent.name}")
            if agent.description:
                print(f"       {Colors.DIM}{agent.description[:60]}...{Colors.ENDC}")
            global_idx += 1
        print()

    while True:
        print(f"{Colors.DIM}Enter agent numbers to toggle (space-separated), or press Enter to continue:{Colors.ENDC}")
        user_input = input("Selection: ").strip()

        if not user_input:
            break

        try:
            for num_str in user_input.split():
                num = int(num_str)
                if num in role_indices:
                    slug = role_indices[num]
                    if slug in selected:
                        selected.discard(slug)
                    else:
                        selected.add(slug)
                else:
                    print(f"{Colors.WARNING}Invalid number: {num_str}{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.WARNING}Please enter valid numbers{Colors.ENDC}")

        # Show current selection
        if selected:
            print(f"{Colors.OKGREEN}Selected: {', '.join(sorted(selected))}{Colors.ENDC}")
        print()

    return sorted(selected)


def select_skills(skills: list[SkillFile]) -> list[str]:
    """Interactive skill selection grouped by tags."""
    if not skills:
        print(f"{Colors.WARNING}No skills found{Colors.ENDC}")
        return []

    print(f"{Colors.BOLD}Step 3b: Select Skills{Colors.ENDC}")
    print(f"Found {len(skills)} skill(s). Group by tags:\n")

    # Group skills by primary tag
    by_tag = {}
    for skill in skills:
        tag = skill.tags[0] if skill.tags else "general"
        if tag not in by_tag:
            by_tag[tag] = []
        by_tag[tag].append(skill)

    selected = set()
    tag_indices = {}
    global_idx = 1

    # Display skills grouped by tag
    for tag in sorted(by_tag.keys()):
        print(f"{Colors.BOLD}{tag.upper()}{Colors.ENDC}")
        for skill in sorted(by_tag[tag], key=lambda s: s.name):
            tag_indices[global_idx] = skill.slug
            applies = ", ".join(skill.applies_to) if skill.applies_to else "general"
            print(f"  {global_idx:2d}. [ ] {skill.name}")
            print(f"       {Colors.DIM}Applies to: {applies}{Colors.ENDC}")
            global_idx += 1
        print()

    while True:
        print(f"{Colors.DIM}Enter skill numbers to toggle (space-separated), or press Enter to continue:{Colors.ENDC}")
        user_input = input("Selection: ").strip()

        if not user_input:
            break

        try:
            for num_str in user_input.split():
                num = int(num_str)
                if num in tag_indices:
                    slug = tag_indices[num]
                    if slug in selected:
                        selected.discard(slug)
                    else:
                        selected.add(slug)
                else:
                    print(f"{Colors.WARNING}Invalid number: {num_str}{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.WARNING}Please enter valid numbers{Colors.ENDC}")

        # Show current selection
        if selected:
            print(f"{Colors.OKGREEN}Selected: {', '.join(sorted(selected))}{Colors.ENDC}")
        print()

    return sorted(selected)


def get_skills_and_agents(repo_root: Path) -> tuple[list[str], list[str]]:
    """Interactive selection of skills and agents with quick presets."""
    print(f"{Colors.BOLD}Step 3: Skills & Agents to Export{Colors.ENDC}\n")

    print("Quick options:")
    print("  1. [ ] All available skills and agents")
    print("  2. [ ] Core skills only (database, backend, frontend, test)")
    print("  3. [ ] Custom selection")
    print("  4. [ ] Minimal (just core agents)\n")

    user_input = input("Choose option (1-4, or press Enter for #1): ").strip()

    all_skills, all_agents = discover_skills_and_agents(repo_root)

    if user_input == "2":
        # Core skills only
        core_skill_slugs = [
            "database_skill",
            "backend_skill",
            "frontend_skill",
            "test_skill",
        ]
        agent_slugs = []
        print(f"\n{Colors.OKGREEN}✓ Selected core skills{Colors.ENDC}\n")
        return core_skill_slugs, agent_slugs

    elif user_input == "3":
        # Custom selection
        agent_slugs = select_agents(all_agents)
        skill_slugs = select_skills(all_skills)
        return skill_slugs, agent_slugs

    elif user_input == "4":
        # Minimal
        agent_slugs = [a.slug for a in all_agents if "autonomous" in a.slug.lower()]
        skill_slugs = []
        print(f"\n{Colors.OKGREEN}✓ Selected minimal setup{Colors.ENDC}\n")
        return skill_slugs, agent_slugs

    else:
        # All (default)
        skill_slugs = []  # Empty means all
        agent_slugs = []  # Empty means all
        print(f"\n{Colors.OKGREEN}✓ Selected all available skills and agents{Colors.ENDC}\n")
        return skill_slugs, agent_slugs


def confirm_setup(project_root: Path, platforms: list[str], skills: list[str], agents: list[str]) -> bool:
    """Show summary and ask for confirmation."""
    print(f"{Colors.BOLD}Setup Summary:{Colors.ENDC}\n")
    print(f"Project Root:    {Colors.OKCYAN}{project_root}{Colors.ENDC}")
    print(f"Platforms:       {Colors.OKCYAN}{len(platforms)} selected{Colors.ENDC}")
    for platform in platforms:
        print(f"                 • {platform}")
    print(f"Skills:          {Colors.OKCYAN}{len(skills)} skills{Colors.ENDC}")
    for skill in skills:
        print(f"                 • {skill}")
    print(f"Agents:          {Colors.OKCYAN}{len(agents)} agent{Colors.ENDC}")
    for agent in agents:
        print(f"                 • {agent}")

    print(f"\n{Colors.WARNING}⚠️  This will copy skills and agents to your project{Colors.ENDC}")
    print("Proceed with setup? (y/n): ", end="")

    return input().lower() == 'y'


def run_exporter(project_root: Path, platforms: list[str], skills: list[str], agents: list[str]) -> bool:
    """Run the exporter tool."""
    import sys

    print(f"\n{Colors.BOLD}Running export...{Colors.ENDC}\n")

    # Build command with target-project parameter
    # Use the same Python executable that's running this script
    cmd = [
        sys.executable,
        str(Path(__file__).parent / "exporter.py"),
        "--target", *platforms,
        "--skills", ",".join(skills),
        "--agents", ",".join(agents),
        "--target-project", str(project_root),
    ]

    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.FAIL}Error running exporter: {e}{Colors.ENDC}")
        return False


def print_next_steps(project_root: Path):
    """Print next steps after successful setup."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              ✨ Setup Complete! What's Next? ✨            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    print(f"{Colors.BOLD}1. Create Your Requirements File:{Colors.ENDC}")
    print(f"   cat > {project_root}/requirement.txt << 'EOF'")
    print("   We need a user authentication system with JWT tokens.")
    print("   Use React for frontend, Python FastAPI for backend, PostgreSQL for database.")
    print("   Support login, registration, and profile management.")
    print("   EOF\n")

    print(f"{Colors.BOLD}2. Invoke the Autonomous Developer Agent:{Colors.ENDC}")
    print("   • In Claude Code: Type '/autonomous-developer'")
    print("   • In GitHub Copilot: '@autonomous-developer'")
    print("   • In your terminal: 'python3 -m autonomous_dev_agent'\n")

    print(f"{Colors.BOLD}3. Monitor Progress:{Colors.ENDC}")
    print(f"   cat {project_root}/task-completion.json\n")

    print(f"{Colors.BOLD}4. Review Generated Code:{Colors.ENDC}")
    print(f"   ls -la {project_root}/tasks/\n")

    print(f"{Colors.BOLD}📚 Full Documentation:{Colors.ENDC}")
    print("   See AUTONOMOUS_DEVELOPER_README.md\n")

    print(f"{Colors.OKGREEN}🎉 Ready to build! Happy coding!{Colors.ENDC}\n")


def main():
    """Main interactive setup flow."""
    try:
        print_header()

        # Step 1: Get project root
        project_root = get_project_root()

        # Resolve repo root (for discovering skills/agents)
        repo_root = resolve_repo_root()

        # Step 2: Get platforms
        platforms = get_platforms()

        # Step 3: Get skills and agents
        skills, agents = get_skills_and_agents(repo_root)

        # Step 4: Confirm
        if not confirm_setup(project_root, platforms, skills, agents):
            print(f"\n{Colors.WARNING}Setup cancelled.{Colors.ENDC}\n")
            return

        # Step 5: Run exporter
        if not run_exporter(project_root, platforms, skills, agents):
            print(f"\n{Colors.FAIL}Export failed. Please check the errors above.{Colors.ENDC}\n")
            return

        # Step 6: Print next steps
        print_next_steps(project_root)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelled by user.{Colors.ENDC}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}\n")
        sys.exit(1)


def resolve_repo_root() -> Path:
    """Resolve the repository root (awesome-prompts directory)."""
    # Start from the script location and go up to find awesome-prompts
    current = Path(__file__).resolve().parent.parent
    if (current / "skills").exists() and (current / "agents").exists():
        return current
    raise FileNotFoundError("Could not find awesome-prompts repository root")


if __name__ == "__main__":
    main()
