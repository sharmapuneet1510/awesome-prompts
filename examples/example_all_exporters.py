"""Example: Using all available exporters"""

from pathlib import Path
from instructions_framework import InstructionLoader
from instructions_framework.exporters import (
    IntermediateExporter,
    ClaudeExporter,
    OpenAIExporter,
    GeminiExporter,
    CopilotExporter,
)


def export_all_formats(instructions_dir: str = "./sample_instructions"):
    """
    Load instructions and export to all available formats.

    Args:
        instructions_dir: Directory containing instructions
    """
    print("\n" + "=" * 60)
    print("Instructions Framework - All Exporters Example")
    print("=" * 60)

    # Load instructions
    print(f"\nLoading from {instructions_dir}...")
    loader = InstructionLoader(instructions_dir)
    instructions = loader.load()

    if not instructions:
        print("No instructions found to export!")
        return

    print(f"Loaded {len(instructions)} instruction(s)")

    # Define exporters
    exporters = {
        "json": (IntermediateExporter(), "output_instructions.json"),
        "claude": (ClaudeExporter(), "output_claude.md"),
        "openai": (OpenAIExporter(), "output_openai.json"),
        "gemini": (GeminiExporter(), "output_gemini.json"),
        "copilot": (CopilotExporter(), "output_copilot.md"),
    }

    print("\nExporting to all formats...\n")

    # Export with each exporter
    for format_name, (exporter, filename) in exporters.items():
        try:
            print(f"Exporting to {format_name:12} ...", end=" ")

            # Export
            output = exporter.export(instructions)

            # Write to file
            output_path = Path(filename)
            with open(output_path, "w") as f:
                f.write(output)

            # Print stats
            size = len(output)
            lines = output.count("\n")
            print(f"✓ {size:8} bytes, {lines:5} lines -> {filename}")

        except Exception as e:
            print(f"✗ Error: {str(e)}")

    print("\n" + "=" * 60)
    print("Export Summary")
    print("=" * 60)
    print("\nGenerated files:")
    for format_name, (_, filename) in exporters.items():
        output_path = Path(filename)
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"  ✓ {filename:30} ({size:8} bytes)")


def example_selective_export(instructions_dir: str = "./sample_instructions"):
    """
    Example: Export only specific instructions.

    Useful for:
    - Exporting only for specific providers
    - Exporting high-priority instructions
    - Exporting specific categories
    """
    print("\n" + "=" * 60)
    print("Selective Export Example")
    print("=" * 60)

    loader = InstructionLoader(instructions_dir)
    all_instructions = loader.load()

    if not all_instructions:
        print("No instructions found!")
        return

    # Filter for Claude-compatible only
    claude_instructions = [
        i for i in all_instructions if "claude" in i.metadata.applicability
    ]

    print(f"\nTotal instructions: {len(all_instructions)}")
    print(f"Claude-compatible: {len(claude_instructions)}")

    # Export only Claude-compatible
    exporter = ClaudeExporter()
    output = exporter.export(claude_instructions)

    with open("output_claude_filtered.md", "w") as f:
        f.write(output)

    print(f"Saved Claude-compatible export to output_claude_filtered.md")

    # Filter for high priority only (priority >= 8)
    high_priority = [i for i in all_instructions if i.metadata.priority >= 8]

    print(f"High priority (>=8): {len(high_priority)}")

    exporter = IntermediateExporter()
    output = exporter.export(high_priority)

    with open("output_high_priority.json", "w") as f:
        f.write(output)

    print(f"Saved high-priority export to output_high_priority.json")


def example_per_provider_export(instructions_dir: str = "./sample_instructions"):
    """
    Example: Export separately for each provider.
    """
    print("\n" + "=" * 60)
    print("Per-Provider Export Example")
    print("=" * 60)

    loader = InstructionLoader(instructions_dir)
    all_instructions = loader.load()

    if not all_instructions:
        print("No instructions found!")
        return

    # Get all unique providers
    providers = set()
    for instr in all_instructions:
        providers.update(instr.metadata.applicability)

    print(f"\nFound providers: {', '.join(sorted(providers))}")

    # Export for each provider
    for provider in sorted(providers):
        provider_instructions = [
            i for i in all_instructions if provider in i.metadata.applicability
        ]

        print(f"\n{provider}: {len(provider_instructions)} instruction(s)")

        # Export to JSON for each provider
        exporter = IntermediateExporter()
        output = exporter.export(provider_instructions)

        filename = f"output_{provider}_instructions.json"
        with open(filename, "w") as f:
            f.write(output)

        print(f"  Saved to {filename}")


def main():
    """Run all export examples"""
    instructions_dir = "./sample_instructions"

    # Check if sample instructions exist
    path = Path(instructions_dir)
    if not path.exists():
        print("\n" + "=" * 60)
        print("Instructions Framework - Exporters Example")
        print("=" * 60)
        print(f"\nNote: Sample instructions not found in {instructions_dir}")
        print("\nTo use this example:")
        print("1. Create sample instruction files in ./sample_instructions/")
        print("2. Each file should have YAML frontmatter with metadata")
        print("3. Re-run this script")
        print("\nExample instruction file structure:")
        print("""
---
version: "1.0.0"
description: "Example instruction"
priority: 5
applicability: ["claude", "openai"]
precedence: "merge"
scope: "global"
deprecated: false
tags: []
author: "system"
---

# Instruction Content

Your instruction text here...
        """)
        return

    # Run examples
    try:
        export_all_formats(instructions_dir)
    except Exception as e:
        print(f"Error in export_all_formats: {e}")

    try:
        example_selective_export(instructions_dir)
    except Exception as e:
        print(f"Error in example_selective_export: {e}")

    try:
        example_per_provider_export(instructions_dir)
    except Exception as e:
        print(f"Error in example_per_provider_export: {e}")


if __name__ == "__main__":
    main()
