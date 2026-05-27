"""Migration tool to convert old instruction format to new framework format"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from instructions_framework.schema import (
    Instruction,
    InstructionMetadata,
    InstructionCategory,
    InstructionPrecedence,
    InstructionScope,
    InstructionSection,
)


def migrate_instruction(old_format: Dict[str, Any], author: str = "migrated") -> Instruction:
    """
    Convert old format dictionary to new Instruction object.

    Old format (example):
    {
        "id": "agent-001",
        "name": "Implementation Agent",
        "type": "agent",
        "content": "...",
        "priority": 5,
        "providers": ["claude", "openai"]
    }

    New format includes full metadata, validation, provider variants, etc.

    Args:
        old_format: Old format instruction dictionary
        author: Author name for migrated instructions

    Returns:
        New Instruction object

    Raises:
        KeyError: If required fields are missing
        ValueError: If values are invalid
    """
    # Extract required fields
    instr_id = old_format.get("id")
    if not instr_id:
        raise KeyError("'id' field is required")

    name = old_format.get("name")
    if not name:
        raise KeyError("'name' field is required")

    content = old_format.get("content", "")
    if not content:
        raise ValueError("'content' field is required and cannot be empty")

    # Map type to category
    instr_type = old_format.get("type", "core").lower()
    category_map = {
        "core": InstructionCategory.CORE,
        "behavioral": InstructionCategory.BEHAVIORAL,
        "constraints": InstructionCategory.CONSTRAINTS,
        "output-format": InstructionCategory.OUTPUT_FORMAT,
        "output_format": InstructionCategory.OUTPUT_FORMAT,
    }
    category = category_map.get(instr_type, InstructionCategory.CORE)

    # Extract optional fields with defaults
    priority = old_format.get("priority", 5)
    if not 1 <= priority <= 10:
        priority = 5

    providers = old_format.get("providers", old_format.get("applicability", ["claude"]))
    if isinstance(providers, str):
        providers = [providers]
    if not providers:
        providers = ["claude"]

    # Create metadata
    metadata = InstructionMetadata(
        version=old_format.get("version", "1.0.0"),
        description=old_format.get("description", f"Migrated instruction: {name}"),
        priority=priority,
        applicability=providers,
        precedence=InstructionPrecedence(
            old_format.get("precedence", "merge").lower()
        ),
        scope=InstructionScope(old_format.get("scope", "global").lower()),
        deprecated=old_format.get("deprecated", False),
        deprecation_notice=old_format.get("deprecation_notice"),
        tags=old_format.get("tags", []),
        depends_on=old_format.get("depends_on", old_format.get("dependencies", [])),
        created=old_format.get("created", datetime.now().isoformat()),
        last_updated=old_format.get(
            "last_updated", old_format.get("updated", datetime.now().isoformat())
        ),
        author=author,
    )

    # Extract sections if available
    sections = []
    if "sections" in old_format:
        for section_data in old_format["sections"]:
            if isinstance(section_data, dict):
                section = InstructionSection(
                    heading=section_data.get("heading", ""),
                    content=section_data.get("content", ""),
                    metadata=section_data.get("metadata", {}),
                )
                sections.append(section)

    # Extract provider variants if available
    provider_variants = old_format.get("provider_variants", {})
    if isinstance(provider_variants, dict):
        # Ensure each variant has required structure
        for provider, variant in provider_variants.items():
            if isinstance(variant, str):
                provider_variants[provider] = {"content": variant}
            elif not isinstance(variant, dict):
                provider_variants[provider] = {"content": str(variant)}

    # Create new instruction
    instruction = Instruction(
        id=instr_id,
        name=name,
        category=category,
        metadata=metadata,
        content=content,
        sections=sections,
        provider_variants=provider_variants,
        source_path=old_format.get("source_path"),
    )

    return instruction


def migrate_file(input_path: Path, output_path: Path, author: str = "migrated") -> bool:
    """
    Migrate a single instruction file from old to new format.

    Args:
        input_path: Path to old format file (JSON or dict-like)
        output_path: Path to write new format file
        author: Author name for migrated instructions

    Returns:
        True if successful, False otherwise

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If input is invalid JSON
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read input file
    with open(input_path, "r") as f:
        if input_path.suffix.lower() == ".json":
            old_format = json.load(f)
        else:
            # Assume JSON even if not .json extension
            old_format = json.load(f)

    # Handle both single object and list of objects
    if isinstance(old_format, list):
        instructions = [migrate_instruction(item, author) for item in old_format]
    else:
        instructions = [migrate_instruction(old_format, author)]

    # Write output file as JSON
    output_data = [instr.to_dict() for instr in instructions]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    return True


def create_migration_template(output_path: Path) -> None:
    """
    Create a template file showing before/after migration format.

    Args:
        output_path: Path to write template file
    """
    template = """# Instruction Migration Guide

## Old Format Example

```json
{
  "id": "agent-001",
  "name": "Implementation Agent",
  "type": "core",
  "content": "You are an implementation agent...",
  "priority": 5,
  "providers": ["claude", "openai"],
  "version": "1.0.0",
  "description": "Agent for implementing features"
}
```

## New Format Example

```json
{
  "id": "agent-001",
  "name": "Implementation Agent",
  "category": "core",
  "priority": 5,
  "content": "You are an implementation agent...",
  "sections": [
    {
      "heading": "Role",
      "content": "You are an implementation agent...",
      "metadata": {}
    }
  ],
  "metadata": {
    "version": "1.0.0",
    "description": "Agent for implementing features",
    "applicability": ["claude", "openai"],
    "precedence": "merge",
    "scope": "global",
    "deprecated": false,
    "deprecation_notice": null,
    "tags": [],
    "dependencies": [],
    "created": "2024-01-01T00:00:00",
    "last_updated": "2024-01-01T00:00:00",
    "author": "migrated"
  },
  "provider_variants": {},
  "source_path": null
}
```

## Migration Steps

1. Prepare old format files in a directory
2. Run migration: `python tools/migrate_instructions.py --input <dir> --output <dir>`
3. Validate migrated files: `python -m instructions_framework.cli validate <output_dir>`
4. Review migrated files for accuracy
5. Test with new framework

## Field Mapping

| Old Field | New Field | Notes |
|-----------|-----------|-------|
| type | category | Maps: core→CORE, behavioral→BEHAVIORAL, constraints→CONSTRAINTS, output-format→OUTPUT_FORMAT |
| providers | applicability | List of supported providers |
| priority | metadata.priority | 1-10 scale |
| version | metadata.version | Version string |
| description | metadata.description | Description of instruction |
| dependencies | metadata.depends_on | List of dependency IDs |
| - | metadata.precedence | How to resolve duplicates (merge/override) |
| - | metadata.scope | Where instruction applies (global/provider/agent) |
| - | metadata.author | Author of instruction |
| - | metadata.created/last_updated | Timestamps |
| - | sections | Structured content sections |
| - | provider_variants | Provider-specific overrides |

"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(template)


def main():
    """
    CLI entry point for migration tool.

    Usage:
        python tools/migrate_instructions.py --input <old_dir> --output <new_dir>
        python tools/migrate_instructions.py --template <output_path>
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate instructions from old format to new framework format"
    )

    parser.add_argument(
        "--input",
        type=Path,
        help="Input directory with old format instruction files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for migrated instructions",
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Generate migration template file",
    )
    parser.add_argument(
        "--author",
        default="migrated",
        help="Author name for migrated instructions (default: 'migrated')",
    )

    args = parser.parse_args()

    if args.template:
        # Generate template
        try:
            create_migration_template(args.template)
            print(f"Migration template created: {args.template}")
            return 0
        except Exception as e:
            print(f"Error creating template: {str(e)}")
            return 1

    elif args.input and args.output:
        # Migrate files
        try:
            input_dir = Path(args.input)
            output_dir = Path(args.output)

            if not input_dir.exists():
                print(f"Error: Input directory does not exist: {input_dir}")
                return 1

            # Find all JSON files
            json_files = list(input_dir.glob("*.json"))
            if not json_files:
                print(f"No JSON files found in {input_dir}")
                return 1

            migrated_count = 0
            for input_file in json_files:
                output_file = output_dir / input_file.name
                try:
                    migrate_file(input_file, output_file, args.author)
                    print(f"Migrated: {input_file.name} -> {output_file.name}")
                    migrated_count += 1
                except Exception as e:
                    print(f"Error migrating {input_file.name}: {str(e)}")

            print(f"\nSuccessfully migrated {migrated_count} file(s)")
            return 0

        except Exception as e:
            print(f"Error during migration: {str(e)}")
            return 1

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
