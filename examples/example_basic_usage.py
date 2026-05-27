"""Example: Basic usage of Instructions Framework"""

from pathlib import Path
from instructions_framework import InstructionLoader, InstructionPipeline
from instructions_framework.exporters import IntermediateExporter, ClaudeExporter


def main():
    """
    Demonstrate basic framework usage:
    1. Load instructions
    2. Process through pipeline
    3. Export to different formats
    """

    print("=" * 60)
    print("Instructions Framework - Basic Usage Example")
    print("=" * 60)

    # Define paths
    instructions_dir = Path("./sample_instructions")

    # Check if sample directory exists
    if not instructions_dir.exists():
        print(f"\nNote: Create sample instructions in {instructions_dir}")
        print("Example instruction structure:")
        print("""
---
version: "1.0.0"
description: "Example instruction"
priority: 5
applicability: ["claude", "openai"]
precedence: "merge"
scope: "global"
deprecated: false
tags: ["example"]
author: "developer"
---

# Instruction Content

Your instruction text here...
        """)
        return

    # STEP 1: Load instructions
    print("\n1. Loading instructions from directory...")
    loader = InstructionLoader(instructions_dir)
    instructions = loader.load()
    print(f"   Loaded {len(instructions)} instruction(s)")

    for instr in instructions:
        print(f"   - {instr.id}: {instr.name} (priority: {instr.metadata.priority})")

    if not instructions:
        print("   No instructions found. Create some first!")
        return

    # STEP 2: Process through pipeline
    print("\n2. Processing through pipeline...")
    pipeline = InstructionPipeline()
    results = pipeline.execute(instructions)

    if results.has_errors:
        print("   Errors found:")
        for error in results.errors:
            print(f"   - {error}")
    else:
        print(f"   Pipeline completed successfully")
        print(f"   Processed {len(results.instructions)} instruction(s)")

    if results.has_warnings:
        print("   Warnings:")
        for warning in results.warnings:
            print(f"   - {warning}")

    processed_instructions = results.instructions

    # STEP 3: Export to JSON
    print("\n3. Exporting to JSON format...")
    json_exporter = IntermediateExporter()
    json_output = json_exporter.export(processed_instructions)
    print(f"   JSON export size: {len(json_output)} bytes")

    # Write to file
    json_file = Path("output_instructions.json")
    with open(json_file, "w") as f:
        f.write(json_output)
    print(f"   Saved to {json_file}")

    # STEP 4: Export to Claude format
    print("\n4. Exporting to Claude format...")
    claude_exporter = ClaudeExporter()
    claude_output = claude_exporter.export(processed_instructions)
    print(f"   Claude export size: {len(claude_output)} bytes")

    # Write to file
    claude_file = Path("output_claude.txt")
    with open(claude_file, "w") as f:
        f.write(claude_output)
    print(f"   Saved to {claude_file}")

    # STEP 5: Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Instructions loaded: {len(instructions)}")
    print(f"Instructions processed: {len(processed_instructions)}")
    print(f"Errors: {len(results.errors)}")
    print(f"Warnings: {len(results.warnings)}")
    print(f"\nOutput files:")
    print(f"  - {json_file}")
    print(f"  - {claude_file}")


if __name__ == "__main__":
    main()
