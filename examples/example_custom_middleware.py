"""Example: Creating and using custom middleware"""

from typing import List
from pathlib import Path
from instructions_framework import (
    InstructionLoader,
    InstructionPipeline,
    InstructionMiddleware,
)
from instructions_framework.schema import Instruction


class FilterByTagMiddleware(InstructionMiddleware):
    """Custom middleware that filters instructions by tag"""

    def __init__(self, required_tag: str):
        """
        Initialize with tag to filter by.

        Args:
            required_tag: Instructions must have this tag
        """
        self.required_tag = required_tag

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Filter to only instructions with required tag"""
        filtered = [
            instr
            for instr in instructions
            if self.required_tag in instr.metadata.tags
        ]
        print(f"FilterByTag('{self.required_tag}'): {len(instructions)} -> {len(filtered)}")
        return filtered


class PriorityValidationMiddleware(InstructionMiddleware):
    """Custom middleware that validates and enforces priority constraints"""

    def __init__(self, min_priority: int = 5, max_instructions: int = 10):
        """
        Initialize with validation rules.

        Args:
            min_priority: Minimum allowed priority
            max_instructions: Maximum number of instructions to allow
        """
        self.min_priority = min_priority
        self.max_instructions = max_instructions

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Validate and filter by priority"""
        # Check priority
        low_priority = [
            instr
            for instr in instructions
            if instr.metadata.priority < self.min_priority
        ]

        if low_priority:
            print(f"⚠ Warning: {len(low_priority)} instruction(s) below priority {self.min_priority}:")
            for instr in low_priority:
                print(
                    f"  - {instr.id} (priority: {instr.metadata.priority})"
                )

        # Check count limit
        if len(instructions) > self.max_instructions:
            print(
                f"⚠ Warning: {len(instructions)} instructions exceed "
                f"maximum of {self.max_instructions}"
            )

        return instructions


class EnrichMetadataMiddleware(InstructionMiddleware):
    """Custom middleware that enriches instruction metadata"""

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Add derived metadata fields"""
        for instr in instructions:
            # Add computed field: word count
            word_count = len(instr.content.split())
            if "computed_fields" not in instr.metadata.__dict__:
                instr.metadata.__dict__["word_count"] = word_count

            # Add category-based tag if not present
            category_tag = instr.category.value
            if category_tag not in instr.metadata.tags:
                instr.metadata.tags.append(category_tag)

        print(f"EnrichMetadata: enriched {len(instructions)} instruction(s)")
        return instructions


def example_filter_by_tag():
    """Example: Filter instructions by tag"""
    print("\n" + "=" * 60)
    print("Example 1: Filter by Tag")
    print("=" * 60)

    # Load instructions
    loader = InstructionLoader("./sample_instructions")
    instructions = loader.load()

    if not instructions:
        print("No instructions found")
        return

    # Create pipeline with custom middleware
    pipeline = InstructionPipeline()

    # Add custom filter middleware
    pipeline.add_middleware(FilterByTagMiddleware("agent"))

    # Execute
    results = pipeline.execute(instructions)

    print(f"\nResult: {len(results.instructions)} instruction(s) with 'agent' tag")
    for instr in results.instructions:
        print(f"  - {instr.id}: {instr.name}")


def example_priority_validation():
    """Example: Validate priorities"""
    print("\n" + "=" * 60)
    print("Example 2: Priority Validation")
    print("=" * 60)

    loader = InstructionLoader("./sample_instructions")
    instructions = loader.load()

    if not instructions:
        print("No instructions found")
        return

    # Create pipeline with validation middleware
    pipeline = InstructionPipeline()

    # Add custom validation middleware
    pipeline.add_middleware(PriorityValidationMiddleware(min_priority=6, max_instructions=20))

    # Execute
    results = pipeline.execute(instructions)

    print(f"\nValidation completed: {len(results.instructions)} instruction(s)")


def example_enrich_metadata():
    """Example: Enrich metadata with computed fields"""
    print("\n" + "=" * 60)
    print("Example 3: Enrich Metadata")
    print("=" * 60)

    loader = InstructionLoader("./sample_instructions")
    instructions = loader.load()

    if not instructions:
        print("No instructions found")
        return

    # Create pipeline with enrichment middleware
    pipeline = InstructionPipeline()
    pipeline.add_middleware(EnrichMetadataMiddleware())

    # Execute
    results = pipeline.execute(instructions)

    print(f"\nEnriched {len(results.instructions)} instruction(s)")
    for instr in results.instructions[:3]:  # Show first 3
        print(f"  - {instr.id}")
        print(f"    Tags: {instr.metadata.tags}")


def example_middleware_chain():
    """Example: Chain multiple custom middleware"""
    print("\n" + "=" * 60)
    print("Example 4: Middleware Chain")
    print("=" * 60)

    loader = InstructionLoader("./sample_instructions")
    instructions = loader.load()

    if not instructions:
        print("No instructions found")
        return

    # Create pipeline with multiple middleware
    pipeline = InstructionPipeline()

    # Chain: enrich -> validate -> filter
    pipeline.add_middleware(EnrichMetadataMiddleware())
    pipeline.add_middleware(PriorityValidationMiddleware(min_priority=5))
    pipeline.add_middleware(FilterByTagMiddleware("core"))

    # Execute
    results = pipeline.execute(instructions)

    print(f"\nChain completed: {len(results.instructions)} final instruction(s)")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Instructions Framework - Custom Middleware Examples")
    print("=" * 60)

    print("\nNote: These examples expect sample instructions in ./sample_instructions/")

    # Run examples
    try:
        example_filter_by_tag()
    except FileNotFoundError:
        print("Skipping example_filter_by_tag: sample_instructions not found")

    try:
        example_priority_validation()
    except FileNotFoundError:
        print("Skipping example_priority_validation: sample_instructions not found")

    try:
        example_enrich_metadata()
    except FileNotFoundError:
        print("Skipping example_enrich_metadata: sample_instructions not found")

    try:
        example_middleware_chain()
    except FileNotFoundError:
        print("Skipping example_middleware_chain: sample_instructions not found")

    print("\n" + "=" * 60)
    print("Examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
