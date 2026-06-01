"""Command-line interface for context builder.

Provides Typer-based CLI commands for:
- Initializing .context folder
- Building project context
- Querying the built context
- Checking status
"""

import logging
from pathlib import Path
from typing import Optional

import typer

from context_builder.orchestrator import Orchestrator

# Initialize Typer app
app = typer.Typer(
    name="context-builder",
    help="Master context builder for project analysis, understanding, and documentation",
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@app.command()
def init(
    path: str = typer.Option(
        ".",
        help="Path to project root (or .context directory)",
    ),
) -> None:
    """Initialize .context folder structure.

    Creates:
    - .context/ directory
    - .context/agents/ directory (for generated agent definitions)
    - Default configuration files (if not present)

    Example:
        context-builder init
        context-builder init --path /path/to/project
    """
    try:
        project_path = Path(path).resolve()

        # Handle case where user provides .context path
        if project_path.name == ".context":
            context_root = project_path
        else:
            context_root = project_path / ".context"

        # Create directories
        context_root.mkdir(parents=True, exist_ok=True)
        (context_root / "agents").mkdir(parents=True, exist_ok=True)
        (context_root / "reports").mkdir(parents=True, exist_ok=True)

        typer.echo(f"✓ Initialized context at {context_root}")
        typer.echo(f"  - Created .context/ directory")
        typer.echo(f"  - Created .context/agents/ directory")
        typer.echo(f"  - Created .context/reports/ directory")
        typer.echo()
        typer.echo("Next step: context-builder build-context")

    except Exception as e:
        typer.echo(f"✗ Error initializing context: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command()
def build_context(
    path: str = typer.Option(
        ".",
        help="Path to project root (or .context directory)",
    ),
    until_mature: bool = typer.Option(
        False,
        help="Iterate until maturity score reaches target (max 5 iterations)",
    ),
) -> None:
    """Build complete project context with 11-agent pipeline.

    Executes the orchestration pipeline:
    1. ProjectDefinitionAgent    - Detect tech stack and structure
    2. RepoScannerAgent          - Scan repositories
    3. CodeGraphAgent            - Build semantic code graph
    4. FlowAnalysisAgent         - Analyze business/request flows
    5. C4DiagramAgent            - Generate architecture diagrams
    6. HTMLSiteAgent             - Create interactive visualization
    7. RAGAgent                  - Build retrieval index
    8. TestIntelligenceAgent     - Analyze test quality
    9. TechnicalDebtAgent        - Identify technical debt
    10. MaturityAgent            - Score context maturity
    11. ReportSynthesisAgent     - Synthesize findings

    With --until-mature, iterates up to 5 times to reach target maturity (default: 80/100)

    Generates artifacts in .context/:
    - context.json               - Complete code graph
    - architecture.md            - C4 diagrams
    - design.html                - Interactive dashboard
    - reports/                   - Analysis reports
    - agents/                    - Generated agent definitions

    Example:
        context-builder build-context
        context-builder build-context --until-mature
        context-builder build-context --path /path/to/project --until-mature
    """
    try:
        project_path = Path(path).resolve()

        # Ensure .context exists
        if project_path.name == ".context":
            context_root = project_path
        else:
            context_root = project_path / ".context"

        if not context_root.exists():
            typer.echo(
                f"✗ .context directory not found at {context_root}\n"
                f"  Run: context-builder init --path {path}",
                err=True,
            )
            raise typer.Exit(code=1)

        # Create orchestrator and build context
        typer.echo("[Context Builder]")
        typer.echo(f"Project: {project_path}")
        typer.echo(f"Context root: {context_root}")
        typer.echo(f"Until mature: {until_mature}")
        typer.echo()

        orchestrator = Orchestrator(context_root)
        success = orchestrator.build_context(until_mature=until_mature)

        if success:
            # Report success and findings
            maturity_score = orchestrator.get_maturity_score()
            generated_files = orchestrator.get_generated_files()

            typer.echo()
            typer.echo("✓ Context build COMPLETE")
            typer.echo(f"  - Maturity score: {maturity_score}/100")
            typer.echo(f"  - Generated files: {len(generated_files)}")
            typer.echo(f"  - Iteration: {orchestrator.context.iteration}/{orchestrator.max_iterations}")
            typer.echo()
            typer.echo("Artifacts in .context/:")
            typer.echo(f"  - context.json               (code graph)")
            typer.echo(f"  - architecture.md            (C4 diagrams)")
            typer.echo(f"  - design.html                (interactive dashboard)")
            typer.echo(f"  - reports/                   (analysis reports)")
            typer.echo(f"  - agents/                    (generated agent definitions)")
            typer.echo()
            typer.echo(f"Next: Explore .context/ or use generated agents")

        else:
            typer.echo("✗ Context build FAILED", err=True)
            if orchestrator.context:
                typer.echo(f"  - Iteration: {orchestrator.context.iteration}")
                typer.echo(f"  - Reports: {len(orchestrator.context.reports)}")
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error building context: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command()
def ask(
    question: str = typer.Argument(
        ...,
        help="Question about the project",
    ),
    path: str = typer.Option(
        ".",
        help="Path to project root (or .context directory)",
    ),
) -> None:
    """Ask a question about the project using the built context.

    Uses the context graph, embeddings, and analysis to answer questions
    like:
    - "What are the main entry points?"
    - "How does user authentication work?"
    - "What databases are used?"
    - "What's the test coverage?"

    Requires context to be built first with: context-builder build-context

    Example:
        context-builder ask "What are the main entry points?"
        context-builder ask "How does payment flow work?" --path /path/to/project
    """
    try:
        project_path = Path(path).resolve()

        # Ensure .context exists
        if project_path.name == ".context":
            context_root = project_path
        else:
            context_root = project_path / ".context"

        if not context_root.exists():
            typer.echo(
                f"✗ .context directory not found at {context_root}\n"
                f"  Run: context-builder build-context --path {path}",
                err=True,
            )
            raise typer.Exit(code=1)

        # Check if context.json exists
        context_json = context_root / "context.json"
        if not context_json.exists():
            typer.echo(
                f"✗ context.json not found\n"
                f"  Run: context-builder build-context --path {path}",
                err=True,
            )
            raise typer.Exit(code=1)

        typer.echo(f"[Question Analysis]")
        typer.echo(f"Question: {question}")
        typer.echo(f"Context: {context_root}")
        typer.echo()
        typer.echo("(RAG query would be executed here)")
        typer.echo("This feature requires RAG integration in MaturityAgent")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error processing question: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command()
def status(
    path: str = typer.Option(
        ".",
        help="Path to project root (or .context directory)",
    ),
) -> None:
    """Show context build status.

    Checks:
    - .context/ folder exists
    - Which artifacts are present
    - Context build completion status
    - Maturity score (if available)

    Example:
        context-builder status
        context-builder status --path /path/to/project
    """
    try:
        project_path = Path(path).resolve()

        # Ensure .context path
        if project_path.name == ".context":
            context_root = project_path
        else:
            context_root = project_path / ".context"

        typer.echo("[Context Status]")
        typer.echo(f"Project: {project_path}")
        typer.echo()

        if not context_root.exists():
            typer.echo("Status: NOT INITIALIZED")
            typer.echo(f"  Run: context-builder init --path {path}")
            return

        typer.echo("Status: INITIALIZED")
        typer.echo(f"Location: {context_root}")
        typer.echo()

        # Check for context files
        artifacts = {
            "context.json": context_root / "context.json",
            "architecture.md": context_root / "architecture.md",
            "design.html": context_root / "design.html",
            "final_report.md": context_root / "final_report.md",
        }

        typer.echo("Artifacts:")
        for name, path_obj in artifacts.items():
            status_icon = "✓" if path_obj.exists() else "✗"
            typer.echo(f"  {status_icon} {name}")

        # Check for reports
        reports_dir = context_root / "reports"
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*.md")) + list(reports_dir.glob("*.json"))
            typer.echo()
            typer.echo(f"Reports: {len(report_files)} file(s)")
            for report_file in report_files[:5]:
                typer.echo(f"  - {report_file.name}")
            if len(report_files) > 5:
                typer.echo(f"  ... and {len(report_files) - 5} more")

        # Check for agents
        agents_dir = context_root / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*.md"))
            typer.echo()
            typer.echo(f"Agents: {len(agent_files)} definition(s)")
            for agent_file in agent_files[:5]:
                typer.echo(f"  - {agent_file.name}")
            if len(agent_files) > 5:
                typer.echo(f"  ... and {len(agent_files) - 5} more")

        typer.echo()
        typer.echo("Next: context-builder build-context --until-mature")

    except Exception as e:
        typer.echo(f"✗ Error checking status: {str(e)}", err=True)
        raise typer.Exit(code=1)


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    try:
        app(argv)
        return 0
    except typer.Exit as e:
        return e.exit_code
    except Exception as e:
        typer.echo(f"Fatal error: {str(e)}", err=True)
        return 1


if __name__ == "__main__":
    main()
