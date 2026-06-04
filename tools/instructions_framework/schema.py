"""Instruction data models and schema definitions"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class InstructionCategory(str, Enum):
    """Categories of instructions"""
    CORE = "core"
    BEHAVIORAL = "behavioral"
    CONSTRAINTS = "constraints"
    OUTPUT_FORMAT = "output-format"


class InstructionPrecedence(str, Enum):
    """How instructions resolve when duplicated"""
    MERGE = "merge"
    OVERRIDE = "override"


class InstructionScope(str, Enum):
    """Where instructions apply"""
    GLOBAL = "global"
    PROVIDER = "provider"
    AGENT = "agent"


@dataclass
class InstructionMetadata:
    """Instruction metadata"""
    version: str
    description: str
    priority: int  # 1-10
    applicability: List[str]  # ["claude", "openai", "gemini"]
    precedence: InstructionPrecedence
    scope: InstructionScope
    deprecated: bool = False
    deprecation_notice: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = "system"

    def validate(self) -> List[str]:
        """Validate metadata. Return list of errors."""
        errors = []
        if not self.version:
            errors.append("version is required")
        if not self.description:
            errors.append("description is required")
        if not 1 <= self.priority <= 10:
            errors.append("priority must be 1-10")
        if not self.applicability:
            errors.append("applicability cannot be empty")
        if not self.author or not self.author.strip():
            errors.append("author cannot be empty")
        if self.deprecated and not self.deprecation_notice:
            errors.append("deprecation_notice is required when deprecated=True")
        return errors


@dataclass
class InstructionSection:
    """A section within an instruction"""
    heading: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Instruction:
    """Complete instruction with metadata and content"""
    id: str
    name: str
    category: InstructionCategory
    metadata: InstructionMetadata
    content: str  # Full markdown body
    sections: List[InstructionSection] = field(default_factory=list)
    provider_variants: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    source_path: Optional[str] = None  # Where this was loaded from

    def validate(self) -> List[str]:
        """Validate instruction. Return list of errors."""
        errors = []
        if not self.id:
            errors.append("id is required")
        if not self.name:
            errors.append("name is required")
        if not self.content:
            errors.append("content is required")

        # Validate sections
        for i, section in enumerate(self.sections):
            if not section.heading or not section.heading.strip():
                errors.append(f"section {i} heading cannot be empty")

        # Validate provider_variants
        for provider, variant in self.provider_variants.items():
            if not isinstance(variant, dict):
                errors.append(f"provider_variants[{provider}] must be a dict")
            elif "content" not in variant:
                errors.append(f"provider_variants[{provider}] missing 'content' key")

        errors.extend(self.metadata.validate())
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "priority": self.metadata.priority,
            "content": self.content,
            "sections": [
                {
                    "heading": s.heading,
                    "content": s.content,
                    "metadata": s.metadata,
                }
                for s in self.sections
            ],
            "metadata": {
                "version": self.metadata.version,
                "description": self.metadata.description,
                "applicability": self.metadata.applicability,
                "precedence": self.metadata.precedence.value,
                "scope": self.metadata.scope.value,
                "deprecated": self.metadata.deprecated,
                "deprecation_notice": self.metadata.deprecation_notice,
                "tags": self.metadata.tags,
                "dependencies": self.metadata.depends_on,
                "created": self.metadata.created,
                "last_updated": self.metadata.last_updated,
                "author": self.metadata.author,
            },
            "provider_variants": self.provider_variants,
        }
