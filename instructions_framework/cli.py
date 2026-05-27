"""Command-line interface for the instructions framework"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from .loader import InstructionLoader
from .pipeline import InstructionPipeline
from .plugins import PluginRegistry
from .exporters import IntermediateExporter, ClaudeExporter, OpenAIExporter, GeminiExporter, CopilotExporter


def load_command(args) -> int:
    """
    Load and display instructions from a directory.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            return 1

        loader = InstructionLoader(path)
        instructions = loader.load_all()

        print(f"Successfully loaded {len(instructions)} instruction(s) from {path}")
        for instr in instructions:
            print(f"  - {instr.id}: {instr.name} (priority: {instr.metadata.priority})")

        return 0
    except Exception as e:
        print(f"Error loading instructions: {str(e)}")
        return 1


def validate_command(args) -> int:
    """
    Validate instruction files in a directory.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            return 1

        loader = InstructionLoader(path)
        instructions = loader.load_all()

        all_errors = []
        for instr in instructions:
            errors = instr.validate()
            if errors:
                all_errors.append((instr.id, errors))

        if all_errors:
            print(f"Validation failed with {len(all_errors)} error(s):")
            for instr_id, errors in all_errors:
                print(f"\n  {instr_id}:")
                for error in errors:
                    print(f"    - {error}")
            return 1
        else:
            print(f"All {len(instructions)} instruction(s) validated successfully")
            return 0

    except Exception as e:
        print(f"Error validating instructions: {str(e)}")
        return 1


def export_command(args) -> int:
    """
    Export instructions to a specified format.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            return 1

        # Load instructions
        loader = InstructionLoader(path)
        instructions = loader.load_all()

        # Select exporter based on format
        format_choice = args.format.lower()
        exporter = None

        if format_choice == "json":
            exporter = IntermediateExporter()
        elif format_choice == "claude":
            exporter = ClaudeExporter()
        elif format_choice == "openai":
            exporter = OpenAIExporter()
        elif format_choice == "gemini":
            exporter = GeminiExporter()
        elif format_choice == "copilot":
            exporter = CopilotExporter()
        else:
            print(f"Error: Unknown format '{format_choice}'")
            print("Supported formats: json, claude, openai, gemini, copilot")
            return 1

        # Export
        result = exporter.export(instructions)

        # Output
        if args.output:
            output_path = Path(args.output)
            if format_choice == "json":
                with open(output_path, "w") as f:
                    json.dump(result, f, indent=2)
            else:
                with open(output_path, "w") as f:
                    f.write(result)
            print(f"Exported {len(instructions)} instruction(s) to {output_path}")
        else:
            if format_choice == "json":
                print(json.dumps(result, indent=2))
            else:
                print(result)

        return 0

    except Exception as e:
        print(f"Error exporting instructions: {str(e)}")
        return 1


def check_command(args) -> int:
    """
    Check for conflicts and dependency issues.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for issues found)
    """
    try:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            return 1

        loader = InstructionLoader(path)
        instructions = loader.load_all()

        # Run validation
        from instructions_framework.middleware.validator import ValidationMiddleware
        validator = ValidationMiddleware()
        processed = validator.process(instructions)

        print(f"Check passed: {len(processed)} instruction(s) OK")
        return 0

    except Exception as e:
        print(f"Error checking instructions: {str(e)}")
        return 1


def apply_middleware_command(args) -> int:
    """
    Apply a specific middleware to instructions.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            return 1

        middleware_name = args.middleware.lower()

        # Load instructions
        loader = InstructionLoader(path)
        instructions = loader.load_all()

        # Apply validation middleware by default
        if middleware_name == "validator":
            from instructions_framework.middleware.validator import ValidationMiddleware
            middleware = ValidationMiddleware()
            processed = middleware.process(instructions)
            print(f"Applied middleware '{middleware_name}' to {len(processed)} instruction(s)")
            return 0
        else:
            print(f"Error: Middleware '{middleware_name}' not found")
            print("Available middleware: validator")
            return 1

    except Exception as e:
        print(f"Error applying middleware: {str(e)}")
        return 1


def list_command(args) -> int:
    """
    List available exporters and middleware.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success)
    """
    print("Available Middleware:")
    print("  - validator")

    print("\nAvailable Exporters:")
    for name in ["json", "claude", "openai", "gemini", "copilot"]:
        print(f"  - {name}")

    return 0


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Instructions Framework CLI - Manage instruction files and exports"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Load command
    load_parser = subparsers.add_parser(
        "load", help="Load instructions from a directory"
    )
    load_parser.add_argument("path", help="Path to instructions directory")
    load_parser.set_defaults(func=load_command)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate instruction files"
    )
    validate_parser.add_argument("path", help="Path to instructions directory")
    validate_parser.set_defaults(func=validate_command)

    # Export command
    export_parser = subparsers.add_parser(
        "export", help="Export instructions to a format"
    )
    export_parser.add_argument("path", help="Path to instructions directory")
    export_parser.add_argument(
        "--format",
        default="json",
        help="Export format: json, claude, openai, gemini, copilot (default: json)",
    )
    export_parser.add_argument(
        "--output", "-o", help="Output file path (if not specified, print to stdout)"
    )
    export_parser.set_defaults(func=export_command)

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Check for conflicts and dependency issues"
    )
    check_parser.add_argument("path", help="Path to instructions directory")
    check_parser.set_defaults(func=check_command)

    # Apply middleware command
    middleware_parser = subparsers.add_parser(
        "apply-middleware", help="Apply a specific middleware"
    )
    middleware_parser.add_argument("path", help="Path to instructions directory")
    middleware_parser.add_argument("middleware", help="Name of middleware to apply")
    middleware_parser.set_defaults(func=apply_middleware_command)

    # List command
    list_parser = subparsers.add_parser(
        "list", help="List available exporters and middleware"
    )
    list_parser.set_defaults(func=list_command)

    # Parse arguments
    args = parser.parse_args(argv)

    # If no command specified, print help
    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
