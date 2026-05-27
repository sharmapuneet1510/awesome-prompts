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
                "applicability": self.metadata.applicability,
                "precedence": self.metadata.precedence.value,
                "scope": self.metadata.scope.value,
                "dependencies": self.metadata.depends_on,
                "created": self.metadata.created,
                "last_updated": self.metadata.last_updated,
                "author": self.metadata.author,
            },
            "provider_variants": self.provider_variants,
        }
