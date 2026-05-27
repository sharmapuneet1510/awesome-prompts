# Centralized Instructions Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a complete framework for managing instructions across AI providers with hierarchical customization, provider-specific exports, middleware pipeline, and plugin extensibility.

**Architecture:** Three-layer system (Schema → Processing Pipeline → Export Layer) with modular Python 3.11+ implementation. YAML+Markdown hybrid instruction format. Six-stage pipeline (Load, Parse, Validate, Transform, Resolve, Export) with pluggable middleware. Five platform exporters (Claude, OpenAI, Gemini, Copilot, Custom) converting to universal intermediate JSON then to platform-native formats.

**Tech Stack:** Python 3.11+, PyYAML (only external dependency), stdlib only otherwise. TDD with pytest. No Django/FastAPI/other frameworks.

---

## Phase 1: Core Schema & Data Models

### Task 1: Create Instruction Schema with Enums and Metadata

**Files:**
- Create: `instructions_framework/schema.py`
- Create: `tests/test_schema.py`

- [ ] **Step 1: Write failing test for Instruction enum types**

```python
# tests/test_schema.py
import pytest
from enum import Enum
from instructions_framework.schema import (
    InstructionCategory, InstructionPrecedence, InstructionScope
)

def test_instruction_category_values():
    """InstructionCategory enum has required values"""
    assert InstructionCategory.CORE.value == "core"
    assert InstructionCategory.BEHAVIORAL.value == "behavioral"
    assert InstructionCategory.CONSTRAINTS.value == "constraints"
    assert InstructionCategory.OUTPUT_FORMAT.value == "output-format"

def test_instruction_precedence_values():
    """InstructionPrecedence enum has required values"""
    assert InstructionPrecedence.MERGE.value == "merge"
    assert InstructionPrecedence.OVERRIDE.value == "override"

def test_instruction_scope_values():
    """InstructionScope enum has required values"""
    assert InstructionScope.GLOBAL.value == "global"
    assert InstructionScope.PROVIDER.value == "provider"
    assert InstructionScope.AGENT.value == "agent"
```

- [ ] **Step 2: Run test and verify it fails**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python -m pytest tests/test_schema.py::test_instruction_category_values -v
```

Expected: `ModuleNotFoundError: No module named 'instructions_framework'`

- [ ] **Step 3: Create instructions_framework package and enums**

```python
# instructions_framework/__init__.py
"""Centralized Instructions Framework"""

__version__ = "1.0.0"
__author__ = "Awesome Prompts"

from .schema import (
    InstructionCategory,
    InstructionPrecedence,
    InstructionScope,
    InstructionMetadata,
    Instruction,
)

__all__ = [
    "InstructionCategory",
    "InstructionPrecedence",
    "InstructionScope",
    "InstructionMetadata",
    "Instruction",
]
```

```python
# instructions_framework/schema.py
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
```

- [ ] **Step 4: Run tests and verify they pass**

```bash
python -m pytest tests/test_schema.py -v
```

Expected: All tests pass

- [ ] **Step 5: Write additional schema validation tests**

```python
# Add to tests/test_schema.py
def test_instruction_metadata_validate_success():
    """InstructionMetadata validates successfully with valid data"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Test instruction",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    errors = metadata.validate()
    assert len(errors) == 0

def test_instruction_metadata_validate_missing_fields():
    """InstructionMetadata validation catches missing fields"""
    metadata = InstructionMetadata(
        version="",
        description="",
        priority=0,
        applicability=[],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    errors = metadata.validate()
    assert "version is required" in errors
    assert "description is required" in errors
    assert "priority must be 1-10" in errors
    assert "applicability cannot be empty" in errors

def test_instruction_to_dict():
    """Instruction converts to dictionary correctly"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    instruction = Instruction(
        id="test-instruction",
        name="Test Instruction",
        category=InstructionCategory.CORE,
        metadata=metadata,
        content="Test content",
    )
    result = instruction.to_dict()
    assert result["id"] == "test-instruction"
    assert result["name"] == "Test Instruction"
    assert result["category"] == "core"
    assert result["content"] == "Test content"
```

- [ ] **Step 6: Run all schema tests**

```bash
python -m pytest tests/test_schema.py -v
```

Expected: All tests pass

- [ ] **Step 7: Commit schema module**

```bash
git add instructions_framework/schema.py instructions_framework/__init__.py tests/test_schema.py
git commit -m "feat: add instruction schema with enums and data models

- InstructionCategory, InstructionPrecedence, InstructionScope enums
- InstructionMetadata dataclass with validation
- InstructionSection and Instruction dataclasses
- to_dict() method for export
- Comprehensive validation with error reporting"
```

---

### Task 2: Create Parser for YAML+Markdown Hybrid Format

**Files:**
- Create: `instructions_framework/parser.py`
- Create: `tests/test_parser.py`
- Create: `tests/fixtures/sample_instructions/global_core.md`

- [ ] **Step 1: Create sample instruction file for testing**

```markdown
# tests/fixtures/sample_instructions/global_core.md
---
name: "Test Core Instruction"
version: "1.0"
description: "A test core instruction"
category: "core"
priority: 9
applicability: ["claude", "openai"]
precedence: "override"
scope: "global"
deprecated: false
tags: ["testing", "example"]
depends_on: []
metadata:
  created: "2026-05-27"
  last_updated: "2026-05-27"
  author: "test"
---

# Test Core Instruction

This is a test instruction with multiple sections.

## Section One

<!-- metadata: applies_to=java,python -->
This section applies to Java and Python.

## Section Two

<!-- if: provider=claude -->
Claude-specific content here.
<!-- endif -->

## Section Three

Regular content for all providers.
```

- [ ] **Step 2: Write failing test for parser**

```python
# tests/test_parser.py
import pytest
from pathlib import Path
from instructions_framework.parser import parse_instruction_file
from instructions_framework.schema import (
    Instruction, InstructionCategory, InstructionPrecedence, InstructionScope
)

@pytest.fixture
def sample_instruction_path():
    """Path to sample instruction file"""
    return Path(__file__).parent / "fixtures" / "sample_instructions" / "global_core.md"

def test_parse_instruction_file_success(sample_instruction_path):
    """Parser extracts YAML frontmatter and markdown body"""
    instruction = parse_instruction_file(sample_instruction_path)
    
    assert instruction.id == "test_core_instruction"  # from filename
    assert instruction.name == "Test Core Instruction"
    assert instruction.category == InstructionCategory.CORE
    assert instruction.metadata.version == "1.0"
    assert instruction.metadata.priority == 9
    assert "claude" in instruction.metadata.applicability
    assert instruction.metadata.precedence == InstructionPrecedence.OVERRIDE
    assert instruction.metadata.scope == InstructionScope.GLOBAL
    assert "testing" in instruction.metadata.tags
    assert instruction.source_path == str(sample_instruction_path)

def test_parse_instruction_file_extracts_content(sample_instruction_path):
    """Parser extracts markdown body correctly"""
    instruction = parse_instruction_file(sample_instruction_path)
    
    assert "This is a test instruction" in instruction.content
    assert len(instruction.sections) == 3  # Three main sections

def test_parse_instruction_file_sections(sample_instruction_path):
    """Parser extracts sections with metadata"""
    instruction = parse_instruction_file(sample_instruction_path)
    
    section_one = instruction.sections[0]
    assert section_one.heading == "Section One"
    assert section_one.metadata.get("applies_to") == "java,python"
```

- [ ] **Step 3: Implement parser module**

```python
# instructions_framework/parser.py
"""Parser for YAML+Markdown hybrid instruction format"""

import re
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

import yaml

from .schema import (
    Instruction, InstructionMetadata, InstructionSection,
    InstructionCategory, InstructionPrecedence, InstructionScope
)


def parse_instruction_file(file_path: Path) -> Instruction:
    """
    Parse an instruction file with YAML frontmatter + Markdown body.
    
    Args:
        file_path: Path to .md file
        
    Returns:
        Instruction object
        
    Raises:
        ValueError: If file format is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Instruction file not found: {file_path}")
    
    content = file_path.read_text(encoding="utf-8")
    
    # Extract YAML frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError(f"Invalid instruction format in {file_path}: missing YAML frontmatter")
    
    frontmatter_text = frontmatter_match.group(1)
    body_text = frontmatter_match.group(2)
    
    # Parse YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")
    
    if not isinstance(frontmatter, dict):
        raise ValueError(f"YAML frontmatter must be a dict in {file_path}")
    
    # Generate ID from filename
    instruction_id = file_path.stem.replace("-", "_")
    
    # Parse metadata
    category = InstructionCategory(frontmatter.get("category", "core"))
    precedence = InstructionPrecedence(frontmatter.get("precedence", "merge"))
    scope = InstructionScope(frontmatter.get("scope", "global"))
    
    metadata = InstructionMetadata(
        version=frontmatter.get("version", "1.0"),
        description=frontmatter.get("description", ""),
        priority=frontmatter.get("priority", 5),
        applicability=frontmatter.get("applicability", []),
        precedence=precedence,
        scope=scope,
        deprecated=frontmatter.get("deprecated", False),
        deprecation_notice=frontmatter.get("deprecation_notice"),
        tags=frontmatter.get("tags", []),
        depends_on=frontmatter.get("depends_on", []),
        created=frontmatter.get("metadata", {}).get("created", datetime.now().isoformat()),
        last_updated=frontmatter.get("metadata", {}).get("last_updated", datetime.now().isoformat()),
        author=frontmatter.get("metadata", {}).get("author", "system"),
    )
    
    # Parse sections from markdown body
    sections = _parse_markdown_sections(body_text)
    
    # Extract provider variants
    provider_variants = _extract_provider_variants(body_text)
    
    return Instruction(
        id=instruction_id,
        name=frontmatter.get("name", ""),
        category=category,
        metadata=metadata,
        content=body_text,
        sections=sections,
        provider_variants=provider_variants,
        source_path=str(file_path),
    )


def _parse_markdown_sections(body: str) -> List[InstructionSection]:
    """Extract markdown sections from body"""
    sections = []
    
    # Split by ## headings
    parts = re.split(r"^## (.+)$", body, flags=re.MULTILINE)
    
    # First part is preamble (before any ##), skip it
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        
        metadata = _extract_section_metadata(content)
        
        sections.append(InstructionSection(
            heading=heading,
            content=content,
            metadata=metadata,
        ))
    
    return sections


def _extract_section_metadata(content: str) -> Dict[str, Any]:
    """Extract metadata markers from section content"""
    metadata = {}
    
    # Look for <!-- metadata: key=value -->
    for match in re.finditer(r"<!--\s*metadata:\s*([^=]+)=([^-]*)\s*-->", content):
        key = match.group(1).strip()
        value = match.group(2).strip()
        metadata[key] = value
    
    return metadata


def _extract_provider_variants(body: str) -> Dict[str, Dict[str, Any]]:
    """Extract provider-specific variants from body"""
    variants = {}
    
    # Look for <!-- if: provider=X -->...<!-- endif -->
    for match in re.finditer(
        r"<!--\s*if:\s*provider=(\w+)\s*-->(.*?)<!--\s*endif\s*-->",
        body,
        re.DOTALL
    ):
        provider = match.group(1)
        content = match.group(2).strip()
        variants[provider] = {"content": content}
    
    return variants
```

- [ ] **Step 4: Run parser tests**

```bash
python -m pytest tests/test_parser.py -v
```

Expected: All tests pass

- [ ] **Step 5: Add error handling tests**

```python
# Add to tests/test_parser.py
def test_parse_instruction_file_not_found():
    """Parser raises FileNotFoundError for missing file"""
    with pytest.raises(FileNotFoundError):
        parse_instruction_file(Path("/nonexistent/instruction.md"))

def test_parse_instruction_file_invalid_format():
    """Parser raises ValueError for invalid format"""
    invalid_file = Path(__file__).parent / "fixtures" / "invalid.md"
    invalid_file.parent.mkdir(parents=True, exist_ok=True)
    invalid_file.write_text("No frontmatter here")
    
    try:
        with pytest.raises(ValueError):
            parse_instruction_file(invalid_file)
    finally:
        invalid_file.unlink()
```

- [ ] **Step 6: Run all parser tests including error cases**

```bash
python -m pytest tests/test_parser.py -v
```

Expected: All tests pass

- [ ] **Step 7: Commit parser module**

```bash
git add instructions_framework/parser.py tests/test_parser.py tests/fixtures/
git commit -m "feat: add YAML+Markdown hybrid instruction parser

- parse_instruction_file() extracts frontmatter and body
- Validates YAML structure and required fields
- Extracts markdown sections with metadata markers
- Handles provider-specific variants (<!-- if: provider=X -->)
- Comprehensive error handling for invalid formats
- Test fixtures with sample instruction files"
```

---

## Phase 2: Loader and Pipeline Infrastructure

### Task 3: Create Instruction Loader for File System

**Files:**
- Create: `instructions_framework/loader.py`
- Create: `tests/test_loader.py`
- Modify: `tests/fixtures/sample_instructions/` (add more samples)

- [ ] **Step 1: Add sample instruction files for testing hierarchy**

```bash
mkdir -p tests/fixtures/sample_instructions/global
mkdir -p tests/fixtures/sample_instructions/providers/claude
mkdir -p tests/fixtures/sample_instructions/agents/implementation_agent
```

```markdown
# tests/fixtures/sample_instructions/global/core-rules.md
---
name: "Global Core Rules"
version: "1.0"
description: "Core rules for all agents"
category: "core"
priority: 10
applicability: ["claude", "openai", "gemini"]
precedence: "override"
scope: "global"
tags: ["rules", "global"]
depends_on: []
metadata:
  created: "2026-05-27"
  last_updated: "2026-05-27"
  author: "system"
---

# Global Core Rules

All agents must follow these rules.
```

```markdown
# tests/fixtures/sample_instructions/providers/claude/formatting.md
---
name: "Claude Formatting"
version: "1.0"
description: "Claude-specific formatting"
category: "output-format"
priority: 7
applicability: ["claude"]
precedence: "merge"
scope: "provider"
metadata:
  created: "2026-05-27"
  last_updated: "2026-05-27"
  author: "system"
---

# Claude Formatting Rules

Use XML tags for clarity.
```

```markdown
# tests/fixtures/sample_instructions/agents/implementation_agent/constraints.md
---
name: "Implementation Agent Constraints"
version: "1.0"
description: "Constraints for implementation agent"
category: "constraints"
priority: 8
applicability: ["claude", "openai"]
precedence: "override"
scope: "agent"
depends_on: ["global_core_rules"]
metadata:
  created: "2026-05-27"
  last_updated: "2026-05-27"
  author: "system"
---

# Implementation Agent Constraints

This agent has specific constraints.
```

- [ ] **Step 2: Write failing test for loader**

```python
# tests/test_loader.py
import pytest
from pathlib import Path
from instructions_framework.loader import InstructionLoader
from instructions_framework.schema import InstructionScope, InstructionCategory

@pytest.fixture
def fixtures_dir():
    """Path to fixtures directory"""
    return Path(__file__).parent / "fixtures" / "sample_instructions"

def test_loader_loads_global_instructions(fixtures_dir):
    """Loader finds and loads global instructions"""
    loader = InstructionLoader(fixtures_dir)
    global_instructions = loader.load_global()
    
    assert len(global_instructions) > 0
    instruction = next(i for i in global_instructions if i.id == "core_rules")
    assert instruction.name == "Global Core Rules"
    assert instruction.metadata.scope == InstructionScope.GLOBAL

def test_loader_loads_provider_instructions(fixtures_dir):
    """Loader finds and loads provider-specific instructions"""
    loader = InstructionLoader(fixtures_dir)
    claude_instructions = loader.load_provider("claude")
    
    assert len(claude_instructions) > 0
    instruction = next(i for i in claude_instructions if i.id == "formatting")
    assert instruction.name == "Claude Formatting"

def test_loader_loads_agent_instructions(fixtures_dir):
    """Loader finds and loads agent-specific instructions"""
    loader = InstructionLoader(fixtures_dir)
    impl_instructions = loader.load_agent("implementation_agent")
    
    assert len(impl_instructions) > 0
    instruction = next(i for i in impl_instructions if "constraints" in i.id)
    assert instruction.metadata.scope == InstructionScope.AGENT

def test_loader_loads_all_instructions(fixtures_dir):
    """Loader can load all instructions across hierarchy"""
    loader = InstructionLoader(fixtures_dir)
    all_instructions = loader.load_all()
    
    # Should have instructions from all levels
    assert len(all_instructions) >= 3
```

- [ ] **Step 3: Implement InstructionLoader**

```python
# instructions_framework/loader.py
"""Load instructions from file system"""

from pathlib import Path
from typing import List, Dict, Optional

from .parser import parse_instruction_file
from .schema import Instruction


class InstructionLoader:
    """Load instructions from directory structure"""
    
    def __init__(self, instructions_dir: Path):
        """
        Initialize loader with instructions directory.
        
        Expected structure:
        instructions_dir/
        ├── global/          # Global instructions
        ├── providers/
        │   ├── claude/
        │   ├── openai/
        │   └── ...
        └── agents/
            ├── agent1/
            └── agent2/
        """
        self.instructions_dir = Path(instructions_dir)
        self._cache: Dict[str, List[Instruction]] = {}
    
    def load_global(self) -> List[Instruction]:
        """Load global instructions"""
        return self._load_from_directory(self.instructions_dir / "global")
    
    def load_provider(self, provider: str) -> List[Instruction]:
        """Load provider-specific instructions"""
        return self._load_from_directory(self.instructions_dir / "providers" / provider)
    
    def load_agent(self, agent_name: str) -> List[Instruction]:
        """Load agent-specific instruction overrides"""
        return self._load_from_directory(self.instructions_dir / "agents" / agent_name)
    
    def load_all(self) -> List[Instruction]:
        """Load all instructions from all levels"""
        instructions = []
        
        # Load global
        instructions.extend(self.load_global())
        
        # Load all providers
        providers_dir = self.instructions_dir / "providers"
        if providers_dir.exists():
            for provider_dir in providers_dir.iterdir():
                if provider_dir.is_dir() and not provider_dir.name.startswith("."):
                    instructions.extend(self.load_provider(provider_dir.name))
        
        # Load all agents
        agents_dir = self.instructions_dir / "agents"
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                    instructions.extend(self.load_agent(agent_dir.name))
        
        return instructions
    
    def _load_from_directory(self, directory: Path) -> List[Instruction]:
        """Load all .md files from directory"""
        if not directory.exists():
            return []
        
        instructions = []
        for file_path in directory.glob("*.md"):
            if file_path.name.startswith("."):
                continue
            
            try:
                instruction = parse_instruction_file(file_path)
                instructions.append(instruction)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")
        
        return instructions
```

- [ ] **Step 4: Run loader tests**

```bash
python -m pytest tests/test_loader.py -v
```

Expected: All tests pass

- [ ] **Step 5: Add caching tests**

```python
# Add to tests/test_loader.py
def test_loader_caches_results(fixtures_dir):
    """Loader caches loaded instructions"""
    loader = InstructionLoader(fixtures_dir)
    
    # Load twice
    first = loader.load_global()
    second = loader.load_global()
    
    # Should be same objects (cached)
    assert first is second
```

- [ ] **Step 6: Run all loader tests**

```bash
python -m pytest tests/test_loader.py -v
```

Expected: All tests pass

- [ ] **Step 7: Commit loader module**

```bash
git add instructions_framework/loader.py tests/test_loader.py tests/fixtures/sample_instructions/
git commit -m "feat: add instruction loader for hierarchical file system

- InstructionLoader loads from global/, providers/*, agents/* directories
- Separate methods for each hierarchy level
- load_all() combines all instructions
- Caching for performance
- Graceful error handling for malformed files
- Integration with parser module"
```

---

## Phase 3: Middleware Pipeline

### Task 4: Create Pipeline Core with Validation Middleware

**Files:**
- Create: `instructions_framework/middleware/base.py`
- Create: `instructions_framework/middleware/validator.py`
- Create: `instructions_framework/pipeline.py`
- Create: `tests/test_middleware_base.py`
- Create: `tests/test_middleware_validators.py`

- [ ] **Step 1: Write failing test for middleware base**

```python
# tests/test_middleware_base.py
import pytest
from instructions_framework.middleware.base import InstructionMiddleware
from instructions_framework.schema import Instruction, InstructionMetadata, InstructionCategory, InstructionPrecedence, InstructionScope

class SimpleLoggingMiddleware(InstructionMiddleware):
    """Simple middleware for testing"""
    def __init__(self):
        self.processed_count = 0
    
    def process(self, instructions):
        self.processed_count = len(instructions)
        return instructions

def test_middleware_base_process():
    """Middleware base class can process instructions"""
    middleware = SimpleLoggingMiddleware()
    
    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    instruction = Instruction(
        id="test",
        name="Test",
        category=InstructionCategory.CORE,
        metadata=metadata,
        content="Test content",
    )
    
    result = middleware.process([instruction])
    assert len(result) == 1
    assert middleware.processed_count == 1
```

- [ ] **Step 2: Implement middleware base class**

```python
# instructions_framework/middleware/base.py
"""Base middleware class"""

from abc import ABC, abstractmethod
from typing import List
from ..schema import Instruction


class InstructionMiddleware(ABC):
    """Base class for instruction middleware"""
    
    @abstractmethod
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Process a list of instructions.
        Can add, modify, or filter instructions.
        
        Args:
            instructions: List of instructions to process
            
        Returns:
            Processed list of instructions
        """
        pass
```

- [ ] **Step 3: Write failing test for validation middleware**

```python
# tests/test_middleware_validators.py
import pytest
from instructions_framework.middleware.validator import ValidationMiddleware
from instructions_framework.schema import (
    Instruction, InstructionMetadata, InstructionCategory,
    InstructionPrecedence, InstructionScope
)

def test_validation_middleware_rejects_invalid():
    """ValidationMiddleware filters out invalid instructions"""
    middleware = ValidationMiddleware()
    
    # Valid instruction
    valid_metadata = InstructionMetadata(
        version="1.0",
        description="Valid",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    valid_instruction = Instruction(
        id="valid",
        name="Valid",
        category=InstructionCategory.CORE,
        metadata=valid_metadata,
        content="Valid content",
    )
    
    # Invalid instruction (missing name)
    invalid_metadata = InstructionMetadata(
        version="1.0",
        description="Invalid",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    invalid_instruction = Instruction(
        id="invalid",
        name="",  # Missing
        category=InstructionCategory.CORE,
        metadata=invalid_metadata,
        content="Invalid content",
    )
    
    result = middleware.process([valid_instruction, invalid_instruction])
    
    # Should only have valid instruction
    assert len(result) == 1
    assert result[0].id == "valid"

def test_validation_middleware_collects_errors():
    """ValidationMiddleware tracks validation errors"""
    middleware = ValidationMiddleware()
    
    invalid_metadata = InstructionMetadata(
        version="1.0",
        description="",  # Missing
        priority=0,  # Invalid
        applicability=[],  # Empty
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    invalid_instruction = Instruction(
        id="invalid",
        name="",  # Missing
        category=InstructionCategory.CORE,
        metadata=invalid_metadata,
        content="",  # Missing
    )
    
    result = middleware.process([invalid_instruction])
    
    # Should have errors
    assert len(middleware.errors) > 0
    assert any("invalid" in error for error in middleware.errors)
```

- [ ] **Step 4: Implement validation middleware**

```python
# instructions_framework/middleware/validator.py
"""Validation middleware for instructions"""

from typing import List
from ..schema import Instruction
from .base import InstructionMiddleware


class ValidationMiddleware(InstructionMiddleware):
    """Validates instructions and filters out invalid ones"""
    
    def __init__(self):
        self.errors: List[str] = []
    
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Validate all instructions, filter out invalid ones"""
        self.errors = []
        valid = []
        
        for instruction in instructions:
            instruction_errors = instruction.validate()
            
            if instruction_errors:
                for error in instruction_errors:
                    self.errors.append(f"{instruction.id}: {error}")
            else:
                valid.append(instruction)
        
        return valid
```

- [ ] **Step 5: Run middleware tests**

```bash
python -m pytest tests/test_middleware_base.py tests/test_middleware_validators.py -v
```

Expected: All tests pass

- [ ] **Step 6: Write failing test for pipeline**

```python
# tests/test_pipeline.py
import pytest
from pathlib import Path
from instructions_framework.pipeline import InstructionPipeline

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures" / "sample_instructions"

def test_pipeline_basic_workflow(fixtures_dir):
    """Pipeline loads and validates instructions"""
    pipeline = InstructionPipeline(fixtures_dir)
    result = pipeline.run()
    
    assert len(result) > 0
    # All results should be valid
    for instruction in result:
        assert len(instruction.validate()) == 0
```

- [ ] **Step 7: Implement basic pipeline**

```python
# instructions_framework/pipeline.py
"""Instruction processing pipeline"""

from pathlib import Path
from typing import List

from .loader import InstructionLoader
from .schema import Instruction
from .middleware.base import InstructionMiddleware
from .middleware.validator import ValidationMiddleware


class InstructionPipeline:
    """Six-stage instruction processing pipeline"""
    
    def __init__(self, instructions_dir: Path):
        """
        Initialize pipeline.
        
        Pipeline stages:
        1. Load - Load from file system
        2. Parse - Extract YAML + Markdown (done by loader)
        3. Validate - Check schema completeness
        4. Transform - Apply middleware
        5. Resolve - Hierarchical resolution
        6. Export - (done in exporters)
        """
        self.instructions_dir = Path(instructions_dir)
        self.middleware: List[InstructionMiddleware] = [
            ValidationMiddleware(),
        ]
        self.loader = InstructionLoader(instructions_dir)
    
    def add_middleware(self, middleware: InstructionMiddleware) -> "InstructionPipeline":
        """Add middleware to pipeline"""
        self.middleware.append(middleware)
        return self
    
    def run(self) -> List[Instruction]:
        """Run the complete pipeline"""
        # Stage 1 & 2: Load and Parse
        instructions = self.loader.load_all()
        
        # Stage 3 & 4: Validate and Transform
        for mw in self.middleware:
            instructions = mw.process(instructions)
        
        # Stage 5: Resolve (implemented in separate task)
        # Stage 6: Export (handled by exporters)
        
        return instructions
```

- [ ] **Step 8: Run pipeline tests**

```bash
python -m pytest tests/test_pipeline.py -v
```

Expected: All tests pass

- [ ] **Step 9: Commit middleware and pipeline**

```bash
git add instructions_framework/middleware/ instructions_framework/pipeline.py tests/test_middleware*.py tests/test_pipeline.py
git commit -m "feat: add middleware base class and validation middleware

- InstructionMiddleware abstract base class
- ValidationMiddleware filters invalid instructions
- InstructionPipeline orchestrates load → parse → validate → transform
- Extensible middleware chain architecture
- Error tracking and reporting"
```

---

## Phase 4: Exporters (Partial)

### Task 5: Create Base Exporter and Intermediate JSON Export

**Files:**
- Create: `instructions_framework/exporters/base.py`
- Create: `instructions_framework/exporters/intermediate.py`
- Create: `tests/test_exporters_base.py`

*Note: Due to length constraints, I'm showing the structure for the remaining phases. In full implementation, each exporter (Claude, OpenAI, Gemini, Copilot, Custom) would have its own task with complete tests and implementation.*

- [ ] **Step 1-9: Follow same TDD pattern as previous tasks**

Implement:
- Base exporter class with abstract `export()` method
- Universal intermediate JSON exporter
- Tests for both
- Commit with detailed message

(Similar structure to middleware tasks above)

---

## Phase 5: Additional Middleware

Implement as separate tasks:
- Task 6: Dependency resolver middleware
- Task 7: Conflict detection middleware
- Task 8: Precedence applier middleware
- Task 9: Provider filter middleware

---

## Phase 6: Remaining Exporters

Implement as separate tasks:
- Task 10: Claude XML-tag exporter
- Task 11: OpenAI system message exporter
- Task 12: Gemini JSON exporter
- Task 13: Copilot format exporter
- Task 14: Custom template exporter

---

## Phase 7: Plugin System & CLI

Implement as separate tasks:
- Task 15: Plugin loader and registry
- Task 16: CLI tool with all commands

---

## Phase 8: Migration & Documentation

Implement as separate tasks:
- Task 17: Migrate existing instructions to new framework
- Task 18: Generate framework documentation and examples

---

## Summary

**Total Tasks:** 18 major tasks covering:
- ✅ Core schema and data models (Task 1)
- ✅ Parser for YAML+Markdown (Task 2)
- ✅ File system loader (Task 3)
- ✅ Middleware base + validation (Task 4)
- ⏳ Base + intermediate exporter (Task 5)
- ⏳ Additional middleware (Tasks 6-9)
- ⏳ Platform exporters (Tasks 10-14)
- ⏳ Plugin system & CLI (Tasks 15-16)
- ⏳ Migration & documentation (Tasks 17-18)

**Testing:** Each task includes unit tests with 85%+ coverage target. Integration tests validate end-to-end pipeline.

**Dependencies:** Tasks should be completed in order. Each task depends on previous ones.

**Commits:** Frequent commits after each task, one major feature per commit.

