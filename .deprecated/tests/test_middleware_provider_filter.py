import pytest
from instructions_framework.middleware.provider_filter import ProviderFilterMiddleware
from instructions_framework.schema import (
    Instruction, InstructionMetadata, InstructionCategory,
    InstructionPrecedence, InstructionScope
)


def create_instruction(
    id: str,
    name: str,
    applicability: list,
) -> Instruction:
    """Helper to create test instructions with specific provider applicability"""
    metadata = InstructionMetadata(
        version="1.0",
        description=f"Instruction {name}",
        priority=5,
        applicability=applicability,
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    return Instruction(
        id=id,
        name=name,
        category=InstructionCategory.CORE,
        metadata=metadata,
        content=f"Content for {name}",
    )


class TestProviderFilterMiddleware:
    """Tests for ProviderFilterMiddleware"""

    def test_provider_filter_single_provider(self):
        """Filters to single provider"""
        middleware = ProviderFilterMiddleware("claude")

        # Create instructions for multiple providers
        claude_only = create_instruction(
            id="claude-1",
            name="Claude Only",
            applicability=["claude"],
        )
        openai_only = create_instruction(
            id="openai-1",
            name="OpenAI Only",
            applicability=["openai"],
        )
        both = create_instruction(
            id="both-1",
            name="Both",
            applicability=["claude", "openai"],
        )
        gemini_only = create_instruction(
            id="gemini-1",
            name="Gemini Only",
            applicability=["gemini"],
        )

        result = middleware.process([claude_only, openai_only, both, gemini_only])

        # Should only have claude-applicable instructions
        assert len(result) == 2
        ids = {r.id for r in result}
        assert ids == {"claude-1", "both-1"}

    def test_provider_filter_multiple_providers(self):
        """Filters to multiple providers"""
        middleware = ProviderFilterMiddleware(["claude", "openai"])

        claude_only = create_instruction(
            id="claude-1",
            name="Claude Only",
            applicability=["claude"],
        )
        openai_only = create_instruction(
            id="openai-1",
            name="OpenAI Only",
            applicability=["openai"],
        )
        gemini_only = create_instruction(
            id="gemini-1",
            name="Gemini Only",
            applicability=["gemini"],
        )
        all_three = create_instruction(
            id="all-1",
            name="All",
            applicability=["claude", "openai", "gemini"],
        )

        result = middleware.process([claude_only, openai_only, gemini_only, all_three])

        # Should have instructions applicable to claude or openai
        assert len(result) == 3
        ids = {r.id for r in result}
        assert ids == {"claude-1", "openai-1", "all-1"}

    def test_provider_filter_no_matches(self):
        """Handles provider with no instructions"""
        middleware = ProviderFilterMiddleware("unknown_provider")

        claude_only = create_instruction(
            id="claude-1",
            name="Claude Only",
            applicability=["claude"],
        )
        openai_only = create_instruction(
            id="openai-1",
            name="OpenAI Only",
            applicability=["openai"],
        )

        result = middleware.process([claude_only, openai_only])

        # Should return empty list (no matches)
        assert len(result) == 0
        assert result == []

    def test_provider_filter_all_applicable(self):
        """Keeps instructions applicable to all"""
        middleware = ProviderFilterMiddleware("claude")

        universal = create_instruction(
            id="universal",
            name="Universal",
            applicability=["claude", "openai", "gemini"],
        )
        claude_only = create_instruction(
            id="claude-1",
            name="Claude Only",
            applicability=["claude"],
        )
        gemini_only = create_instruction(
            id="gemini-1",
            name="Gemini Only",
            applicability=["gemini"],
        )

        result = middleware.process([universal, claude_only, gemini_only])

        # Should include both universal and claude-only
        assert len(result) == 2
        ids = {r.id for r in result}
        assert ids == {"universal", "claude-1"}

    def test_provider_filter_empty_list(self):
        """Handles empty input list"""
        middleware = ProviderFilterMiddleware("claude")

        result = middleware.process([])

        # Should return empty list
        assert len(result) == 0
        assert result == []

    def test_provider_filter_single_instruction_match(self):
        """Single instruction that matches is returned"""
        middleware = ProviderFilterMiddleware("openai")

        openai_instr = create_instruction(
            id="openai-1",
            name="OpenAI",
            applicability=["openai"],
        )

        result = middleware.process([openai_instr])

        # Should return the matching instruction
        assert len(result) == 1
        assert result[0].id == "openai-1"

    def test_provider_filter_single_instruction_no_match(self):
        """Single instruction that doesn't match is filtered out"""
        middleware = ProviderFilterMiddleware("gemini")

        claude_instr = create_instruction(
            id="claude-1",
            name="Claude",
            applicability=["claude"],
        )

        result = middleware.process([claude_instr])

        # Should return empty list (no match)
        assert len(result) == 0

    def test_provider_filter_string_vs_list_init(self):
        """Initializing with string vs list produces same result"""
        instr_claude = create_instruction(
            id="claude-1",
            name="Claude",
            applicability=["claude"],
        )
        instr_openai = create_instruction(
            id="openai-1",
            name="OpenAI",
            applicability=["openai"],
        )

        instructions = [instr_claude, instr_openai]

        # String initialization
        middleware_str = ProviderFilterMiddleware("claude")
        result_str = middleware_str.process(instructions)

        # List initialization
        middleware_list = ProviderFilterMiddleware(["claude"])
        result_list = middleware_list.process(instructions)

        # Should be equivalent
        assert len(result_str) == len(result_list)
        assert {r.id for r in result_str} == {r.id for r in result_list}

    def test_provider_filter_multiple_providers_with_duplicates(self):
        """Multiple providers with overlapping applicability"""
        middleware = ProviderFilterMiddleware(["claude", "openai"])

        claude_and_openai = create_instruction(
            id="both-1",
            name="Both Claude and OpenAI",
            applicability=["claude", "openai"],
        )
        openai_and_gemini = create_instruction(
            id="openai-gemini",
            name="OpenAI and Gemini",
            applicability=["openai", "gemini"],
        )
        all_three = create_instruction(
            id="all-1",
            name="All three",
            applicability=["claude", "openai", "gemini"],
        )

        result = middleware.process([claude_and_openai, openai_and_gemini, all_three])

        # Should have all three (each has at least one matching provider)
        assert len(result) == 3
        ids = {r.id for r in result}
        assert ids == {"both-1", "openai-gemini", "all-1"}

    def test_provider_filter_case_sensitive(self):
        """Provider filter is case sensitive"""
        middleware = ProviderFilterMiddleware("Claude")  # Capital C

        claude_lowercase = create_instruction(
            id="claude-1",
            name="Claude",
            applicability=["claude"],  # lowercase
        )

        result = middleware.process([claude_lowercase])

        # Should not match (case sensitive)
        assert len(result) == 0

    def test_provider_filter_preserves_instruction_order(self):
        """Filter preserves original instruction order"""
        middleware = ProviderFilterMiddleware("claude")

        instr1 = create_instruction(
            id="first",
            name="First",
            applicability=["claude"],
        )
        instr2 = create_instruction(
            id="second",
            name="Second",
            applicability=["openai"],
        )
        instr3 = create_instruction(
            id="third",
            name="Third",
            applicability=["claude"],
        )

        result = middleware.process([instr1, instr2, instr3])

        # Should keep order: instr1, then instr3
        assert len(result) == 2
        assert result[0].id == "first"
        assert result[1].id == "third"
