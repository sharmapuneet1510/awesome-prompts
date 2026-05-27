# Instructions Framework Detailed Guide

Complete reference for using the Instructions Framework to manage, validate, and export instructions.

## Table of Contents

1. [Schema & Data Model](#schema--data-model)
2. [Parser & File Format](#parser--file-format)
3. [Loader & Discovery](#loader--discovery)
4. [Pipeline & Middleware](#pipeline--middleware)
5. [Plugin System](#plugin-system)
6. [Exporters](#exporters)
7. [CLI Tool](#cli-tool)
8. [Advanced Usage](#advanced-usage)

## Schema & Data Model

The framework uses a unified schema for all instruction types. Every instruction contains metadata, content, and optional provider variants.

### Instruction Structure

```python
@dataclass
class Instruction:
    id: str                                      # Unique identifier
    name: str                                    # Human-readable name
    category: InstructionCategory                # CORE, BEHAVIORAL, CONSTRAINTS, OUTPUT_FORMAT
    metadata: InstructionMetadata                # Metadata object
    content: str                                 # Main instruction text (markdown)
    sections: List[InstructionSection]           # Structured sections
    provider_variants: Dict[str, Dict]           # Provider-specific overrides
    source_path: Optional[str]                   # Where loaded from
```

### Metadata Structure

```python
@dataclass
class InstructionMetadata:
    version: str                 # Version string (e.g., "1.0.0")
    description: str             # What this instruction does
    priority: int                # 1-10, higher = more important
    applicability: List[str]     # ["claude", "openai", "gemini", ...]
    precedence: InstructionPrecedence  # MERGE or OVERRIDE
    scope: InstructionScope      # GLOBAL, PROVIDER, or AGENT
    deprecated: bool             # Is this instruction deprecated?
    deprecation_notice: str      # Why/when deprecated
    tags: List[str]              # Categorization tags
    depends_on: List[str]        # IDs of dependencies
    created: str                 # ISO timestamp
    last_updated: str            # ISO timestamp
    author: str                  # Who created it
```

### Categories

- **CORE**: Fundamental behavioral rules that must always apply
- **BEHAVIORAL**: Agent behavior guidelines and response patterns
- **CONSTRAINTS**: Limitations and rules for what not to do
- **OUTPUT_FORMAT**: Format specifications for output

### Precedence Modes

- **MERGE**: When duplicate instructions are found, combine their content and metadata (union of tags, etc.)
- **OVERRIDE**: Later instructions completely replace earlier ones

### Scope Levels

- **GLOBAL**: Applies to all AI providers
- **PROVIDER**: Applies only to specific providers (claude, openai, etc.)
- **AGENT**: Applies to specific agent roles

## Parser & File Format

### File Format

Instructions are stored as YAML/JSON with YAML frontmatter:

```yaml
---
version: "1.0.0"
description: "Implementation agent for feature development"
priority: 8
applicability: ["claude", "openai"]
precedence: "merge"
scope: "global"
deprecated: false
tags: ["agent", "implementation", "coding"]
depends_on: ["core-coding-standards"]
author: "system"
---

# Your instruction content in markdown

You are an implementation agent responsible for...

## Role

Clear role definition.

## Responsibilities

- Task 1
- Task 2

## Rules

Always follow these practices...
```

### Parsing Stages

1. **Read File**: Load YAML/JSON from disk
2. **Extract Frontmatter**: Parse metadata header
3. **Parse Content**: Extract sections and structure
4. **Validate**: Check required fields
5. **Create Object**: Instantiate Instruction

### Custom Parser Usage

```python
from instructions_framework import parse_instruction_file

instruction = parse_instruction_file("path/to/instruction.md")
print(instruction.id, instruction.name)
```

## Loader & Discovery

### Loading Instructions

The InstructionLoader discovers and loads instructions from directories:

```python
from instructions_framework import InstructionLoader

loader = InstructionLoader("path/to/instructions/dir")
instructions = loader.load()

# With pattern filter
instructions = loader.load(pattern="*agent*.md")

# From specific subdirectory
instructions = loader.load(glob_pattern="agents/**/*.md")
```

### Loader Behavior

- Recursively scans directory for `.md`, `.yaml`, `.yml`, `.json` files
- Skips hidden files (starting with `.`)
- Skips directories named `__pycache__`, `.git`, etc.
- Returns list of validated Instruction objects
- Raises exceptions on parsing errors

### Loader Hierarchy

```
InstructionLoader
├── Discovers files
├── For each file:
│   ├── Parse file (parser.py)
│   ├── Extract metadata
│   ├── Create Instruction object
│   └── Add to list
└── Return List[Instruction]
```

## Pipeline & Middleware

### Pipeline Execution

The pipeline applies middleware in sequence:

```python
from instructions_framework import InstructionPipeline

loader = InstructionLoader("path/to/instructions")
instructions = loader.load()

pipeline = InstructionPipeline()
results = pipeline.execute(instructions)

if results.has_errors:
    for error in results.errors:
        print(f"Error: {error}")

processed_instructions = results.instructions
```

### Pipeline Result

```python
@dataclass
class PipelineResult:
    instructions: List[Instruction]    # Processed instructions
    errors: List[str]                  # Error messages
    warnings: List[str]                # Warning messages
    has_errors: bool                   # Whether errors occurred
    has_warnings: bool                 # Whether warnings occurred
```

### Built-in Middleware

#### 1. Validator Middleware

Validates each instruction against schema:

```python
# Automatically applied in pipeline
# Checks:
# - Required fields present
# - Valid enum values
# - Priority is 1-10
# - Content not empty
# - Metadata valid
```

#### 2. Dependency Resolver

Resolves instruction dependencies:

```python
# Checks that all depends_on references exist
# Topologically sorts by dependencies
# Detects circular dependencies
# Tracks dependency graph
```

#### 3. Conflict Detector

Identifies conflicting instructions:

```python
# Checks for:
# - Duplicate IDs
# - Incompatible scopes
# - Provider conflicts
# - Tags indicating conflicts
```

#### 4. Precedence Applier

Applies precedence rules to duplicates:

```python
# If duplicate IDs found:
# - MERGE mode: combine content and metadata
# - OVERRIDE mode: keep latest, discard earlier
```

#### 5. Provider Filter

Filters by target provider:

```python
# Remove instructions not applicable to target
# Can be set in pipeline:
# pipeline.set_provider("claude")
# Only returns instructions with claude in applicability
```

### Custom Middleware

Create custom middleware by inheriting from InstructionMiddleware:

```python
from instructions_framework import InstructionMiddleware
from instructions_framework.schema import Instruction

class CustomMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Process instructions.
        
        Can:
        - Filter instructions (return fewer items)
        - Modify instructions (transform content)
        - Add instructions (return more items)
        - Validate and track errors
        """
        processed = []
        for instr in instructions:
            # Custom logic here
            processed.append(instr)
        return processed
```

Register in pipeline:

```python
from instructions_framework.pipeline import InstructionPipeline

pipeline = InstructionPipeline()
pipeline.add_middleware(CustomMiddleware())
results = pipeline.execute(instructions)
```

## Plugin System

### Plugin Registry

Register custom middleware and exporters:

```python
from instructions_framework.plugins import PluginRegistry

registry = PluginRegistry()

# Register custom middleware
registry.register_middleware("custom", CustomMiddleware)

# Register custom exporter
registry.register_exporter("myformat", CustomExporter)

# Retrieve
middleware = registry.get_middleware("custom")
exporter = registry.get_exporter("myformat")
```

### Dynamic Plugin Loading

Load plugins from a directory:

```python
registry.load_plugins(Path("./custom_plugins"))

# Automatically discovers:
# - Files in directory
# - Classes ending with 'Middleware' -> registered as middleware
# - Classes ending with 'Exporter' -> registered as exporters
```

Plugin file example:

```python
# custom_plugins/my_filter.py
from instructions_framework import InstructionMiddleware

class FilterByTagMiddleware(InstructionMiddleware):
    def __init__(self, tag: str):
        self.tag = tag
    
    def process(self, instructions):
        return [i for i in instructions if self.tag in i.metadata.tags]

class FilterByProviderExporter(BaseExporter):
    def __init__(self, provider: str):
        self.provider = provider
    
    def export(self, instructions, **kwargs):
        filtered = [i for i in instructions if self.provider in i.metadata.applicability]
        return json.dumps([i.to_dict() for i in filtered], indent=2)
```

Then load:

```python
registry = PluginRegistry()
registry.load_plugins(Path("./custom_plugins"))

# Now available:
# registry.get_middleware("filter_by_tag")
# registry.get_exporter("filter_by_provider")
```

### Global Registry

Use the global registry singleton:

```python
from instructions_framework.plugins import get_global_registry

registry = get_global_registry()
registry.register_middleware("custom", MyMiddleware)

# Available everywhere:
registry2 = get_global_registry()
same_middleware = registry2.get_middleware("custom")  # Returns MyMiddleware
```

## Exporters

### Available Exporters

1. **IntermediateExporter**: JSON format (all instruction data)
2. **ClaudeExporter**: Claude system prompt format
3. **OpenAIExporter**: OpenAI instruction format
4. **GeminiExporter**: Google Gemini format
5. **CopilotExporter**: GitHub Copilot format

### Using Exporters

```python
from instructions_framework.exporters import (
    IntermediateExporter,
    ClaudeExporter,
    OpenAIExporter,
)

instructions = loader.load()

# JSON export
json_exporter = IntermediateExporter()
json_output = json_exporter.export(instructions)

# Claude export
claude_exporter = ClaudeExporter()
claude_output = claude_exporter.export(instructions)

# OpenAI export
openai_exporter = OpenAIExporter()
openai_output = openai_exporter.export(instructions)
```

### Export Output Formats

#### Intermediate (JSON)

Complete instruction data in JSON:

```json
[
  {
    "id": "instruction-001",
    "name": "Instruction Name",
    "category": "core",
    "priority": 8,
    "content": "Full instruction text",
    "sections": [...],
    "metadata": {...},
    "provider_variants": {...}
  }
]
```

#### Claude

System prompt format for Claude:

```
# Instruction Name

Full instruction text with markdown formatting...

---

Priority: 8
Scope: global
Provider: claude
Version: 1.0.0
```

#### OpenAI

OpenAI function/system message format:

```json
{
  "instructions": [
    {
      "id": "instruction-001",
      "name": "Instruction Name",
      "description": "What it does",
      "content": "Full text",
      "priority": 8
    }
  ]
}
```

#### Gemini

Google Gemini instruction format:

```json
{
  "instructions": [
    {
      "id": "instruction-001",
      "description": "What it does",
      "text": "Full instruction text",
      "priority": 8
    }
  ]
}
```

#### Copilot

GitHub Copilot instruction format:

```
# Instruction Name

Full instruction text...

Instructions for Copilot behavior...
```

### Custom Exporters

Create custom exporters:

```python
from instructions_framework.exporters import BaseExporter
from instructions_framework.schema import Instruction

class CustomExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """Export to custom format"""
        result = []
        for instr in instructions:
            result.append(f"# {instr.name}\n\n{instr.content}")
        return "\n\n---\n\n".join(result)
```

## CLI Tool

### Commands

#### load

Load and list instructions:

```bash
python -m instructions_framework.cli load ./instructions
# Output:
# Successfully loaded 5 instruction(s) from ./instructions
#   - agent-001: Implementation Agent (priority: 8)
#   - skill-001: Testing Skill (priority: 7)
#   ...
```

#### validate

Validate instruction files:

```bash
python -m instructions_framework.cli validate ./instructions
# Output:
# All 5 instruction(s) validated successfully
```

With errors:

```bash
python -m instructions_framework.cli validate ./instructions
# Output:
# Validation failed with 2 error(s):
#   agent-001:
#     - priority must be 1-10
#     - author cannot be empty
```

#### export

Export to different formats:

```bash
# To stdout
python -m instructions_framework.cli export ./instructions --format claude

# To file
python -m instructions_framework.cli export ./instructions --format openai --output output.json

# All formats: json, claude, openai, gemini, copilot
```

#### check

Check for conflicts and issues:

```bash
python -m instructions_framework.cli check ./instructions
# Runs full pipeline, reports errors and warnings
```

#### apply-middleware

Apply specific middleware:

```bash
python -m instructions_framework.cli apply-middleware ./instructions validator
# Applies validator middleware and reports results
```

#### list

List available tools:

```bash
python -m instructions_framework.cli list
# Shows available middleware and exporters
```

## Advanced Usage

### Custom Processing Pipeline

```python
from instructions_framework import (
    InstructionLoader,
    InstructionPipeline,
)
from instructions_framework.middleware import InstructionMiddleware

# Custom middleware
class MyMiddleware(InstructionMiddleware):
    def process(self, instructions):
        # Custom processing
        return instructions

# Load
loader = InstructionLoader("./instructions")
instructions = loader.load()

# Create pipeline
pipeline = InstructionPipeline()

# Add custom middleware before execution
pipeline.add_middleware(MyMiddleware())

# Set provider filter
pipeline.set_provider("claude")

# Execute
results = pipeline.execute(instructions)

# Check results
if results.has_errors:
    print("Errors:", results.errors)

# Use results
print(f"Processed {len(results.instructions)} instructions")
```

### Provider-Specific Export

```python
from instructions_framework import InstructionPipeline, ClaudeExporter

loader = InstructionLoader("./instructions")
instructions = loader.load()

# Filter for Claude only
pipeline = InstructionPipeline()
pipeline.set_provider("claude")
results = pipeline.execute(instructions)

# Export
exporter = ClaudeExporter()
claude_text = exporter.export(results.instructions)
```

### Batch Processing

```python
from pathlib import Path
from instructions_framework import InstructionLoader, IntermediateExporter

input_dirs = [
    Path("./agents"),
    Path("./skills"),
    Path("./prompts"),
]

all_instructions = []
for dir in input_dirs:
    loader = InstructionLoader(dir)
    all_instructions.extend(loader.load())

exporter = IntermediateExporter()
output = exporter.export(all_instructions)

with open("all_instructions.json", "w") as f:
    f.write(output)
```

### Validation with Custom Rules

```python
from instructions_framework import InstructionMiddleware

class PriorityCheckMiddleware(InstructionMiddleware):
    def __init__(self, min_priority: int = 5):
        self.min_priority = min_priority
    
    def process(self, instructions):
        for instr in instructions:
            if instr.metadata.priority < self.min_priority:
                print(f"Warning: {instr.id} has low priority {instr.metadata.priority}")
        return instructions

pipeline = InstructionPipeline()
pipeline.add_middleware(PriorityCheckMiddleware(min_priority=6))
results = pipeline.execute(instructions)
```

## Troubleshooting

### "Instruction with id 'X' not found" (Dependency Error)

**Cause**: An instruction depends on another instruction that doesn't exist.

**Solution**: 
1. Check `depends_on` field in instruction
2. Ensure dependency instruction exists in loaded set
3. Verify dependency ID is spelled correctly

### "Priority must be 1-10"

**Cause**: Metadata priority is outside valid range.

**Solution**: Set priority to value between 1-10 inclusive.

### "Provider variant must be a dict"

**Cause**: Provider variant has incorrect structure.

**Solution**: Ensure provider_variants is:
```python
provider_variants = {
    "claude": {"content": "..."},
    "openai": {"content": "..."}
}
```

### Plugin Not Loading

**Cause**: Plugin file or class name incorrect.

**Solution**:
1. Class must inherit from InstructionMiddleware or BaseExporter
2. Name must end with "Middleware" or "Exporter"
3. File must be in plugin directory
4. No syntax errors in plugin file

## Best Practices

1. **Use unique IDs**: Each instruction needs a globally unique ID
2. **Set priorities**: Use priority to indicate importance
3. **Document dependencies**: Clearly mark depends_on
4. **Use sections**: Break content into logical sections
5. **Add tags**: Use tags for categorization and filtering
6. **Test exports**: Validate exported format works with target provider
7. **Version everything**: Update version when making changes
8. **Author attribution**: Track who created each instruction
