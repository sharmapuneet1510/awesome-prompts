#!/usr/bin/env python3
"""
interactive_exporter.py — Interactive setup for Autonomous Developer System

Asks users for:
1. Project root directory
2. Target platforms
3. Confirms before copying skills and agents

Usage:
    python3 tools/interactive_exporter.py
"""

import sys
import subprocess
from pathlib import Path


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
    """Ask user to select target platforms."""
    print(f"{Colors.BOLD}Step 2: Target Platforms{Colors.ENDC}")
    print("Which platforms do you use? (Select with space, confirm with Enter)\n")

    platforms = [
        ("claude", "Claude Code (Default)"),
        ("copilot", "GitHub Copilot"),
        ("cursor", "Cursor IDE"),
        ("windsurf", "Windsurf"),
        ("gemini", "Google Gemini"),
        ("continue", "Continue IDE"),
        ("openai", "OpenAI"),
        ("aider", "Aider CLI"),
    ]

    selected = []

    for idx, (slug, name) in enumerate(platforms, 1):
        print(f"{idx}. [ ] {name}")

    print()
    default_choice = "1"  # Claude is default
    user_input = input("Enter platform numbers (space-separated, or press Enter for #1): ").strip()

    if not user_input:
        user_input = default_choice

    try:
        choices = [int(x) - 1 for x in user_input.split()]
        selected = [platforms[i][0] for i in choices if 0 <= i < len(platforms)]

        if not selected:
            selected = ["claude"]

        print(f"\n{Colors.OKGREEN}✓ Selected platforms:{Colors.ENDC}")
        for slug in selected:
            name = next(p[1] for p in platforms if p[0] == slug)
            print(f"  • {name}")
        print()

        return selected

    except (ValueError, IndexError):
        print(f"{Colors.WARNING}Invalid input. Using Claude Code (default).{Colors.ENDC}\n")
        return ["claude"]


def get_skills_and_agents() -> tuple[list[str], list[str]]:
    """Ask user which skills and agents to export."""
    print(f"{Colors.BOLD}Step 3: Skills & Agents to Export{Colors.ENDC}\n")

    # Default: export autonomous developer system
    skills = [
        "database_skill",
        "backend_skill",
        "frontend_skill",
        "test_skill",
    ]
    agents = ["autonomous_dev"]

    print("Exporting:")
    print(f"  Skills: {', '.join(skills)}")
    print(f"  Agents: {', '.join(agents)}")
    print(f"\n{Colors.OKGREEN}✓ Ready to export autonomous developer system{Colors.ENDC}\n")

    return skills, agents


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


def run_exporter(platforms: list[str], skills: list[str], agents: list[str]) -> bool:
    """Run the exporter tool."""
    print(f"\n{Colors.BOLD}Running export...{Colors.ENDC}\n")

    # Build command
    cmd = [
        "python3",
        "tools/exporter.py",
        "--target", " ".join(platforms),
        "--skills", ",".join(skills),
        "--agents", ",".join(agents),
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

        # Step 2: Get platforms
        platforms = get_platforms()

        # Step 3: Get skills and agents
        skills, agents = get_skills_and_agents()

        # Step 4: Confirm
        if not confirm_setup(project_root, platforms, skills, agents):
            print(f"\n{Colors.WARNING}Setup cancelled.{Colors.ENDC}\n")
            return

        # Step 5: Run exporter
        if not run_exporter(platforms, skills, agents):
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


if __name__ == "__main__":
    main()
