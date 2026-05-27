# Framework Examples

Working examples demonstrating how to use the Instructions Framework.

## Running Examples

All examples are in the `examples/` directory. To run them:

```bash
# Make sure you have sample instructions
mkdir -p sample_instructions

# Create sample instruction (see sample below)
cat > sample_instructions/agent.md <<'EOF'
---
version: "1.0.0"
description: "Implementation agent for features"
priority: 8
applicability: ["claude", "openai"]
precedence: "merge"
scope: "global"
deprecated: false
tags: ["agent", "implementation"]
author: "system"
---

# Implementation Agent

You are an implementation agent responsible for building features...
EOF

# Run an example
python examples/example_basic_usage.py
```

## Example 1: Basic Usage

**File:** `examples/example_basic_usage.py`

Demonstrates the fundamental workflow:
1. Load instructions from a directory
2. Process through the pipeline
3. Export to different formats

**What it does:**
- Loads all instructions from a directory
- Runs through built-in middleware
- Exports to JSON and Claude formats
- Saves output to files

**Usage:**

```bash
python examples/example_basic_usage.py
```

**Key API calls:**

```python
from instructions_framework import InstructionLoader, InstructionPipeline
from instructions_framework.exporters import IntermediateExporter, ClaudeExporter

# Load
loader = InstructionLoader("./sample_instructions")
instructions = loader.load()

# Process
pipeline = InstructionPipeline()
results = pipeline.execute(instructions)

# Export
exporter = IntermediateExporter()
json_output = exporter.export(results.instructions)
```

## Example 2: Custom Middleware

**File:** `examples/example_custom_middleware.py`

Shows how to create and use custom middleware for processing.

**Included middleware classes:**
1. `FilterByTagMiddleware` - Filter instructions by tag
2. `PriorityValidationMiddleware` - Validate priority constraints
3. `EnrichMetadataMiddleware` - Add computed fields

**Examples included:**
1. Filter by tag
2. Priority validation
3. Metadata enrichment
4. Middleware chaining

**Usage:**

```bash
python examples/example_custom_middleware.py
```

**Creating custom middleware:**

```python
from instructions_framework import InstructionMiddleware
from instructions_framework.schema import Instruction
from typing import List

class CustomMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        # Your processing logic here
        filtered = [i for i in instructions if some_condition(i)]
        return filtered

# Use in pipeline
pipeline = InstructionPipeline()
pipeline.add_middleware(CustomMiddleware())
results = pipeline.execute(instructions)
```

### Filter by Tag Example

Filter to only instructions with a specific tag:

```python
class FilterByTagMiddleware(InstructionMiddleware):
    def __init__(self, required_tag: str):
        self.required_tag = required_tag

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        return [
            i for i in instructions
            if self.required_tag in i.metadata.tags
        ]

# Use it
pipeline = InstructionPipeline()
pipeline.add_middleware(FilterByTagMiddleware("agent"))
results = pipeline.execute(instructions)
```

### Enrich Metadata Example

Add computed fields to instructions:

```python
class EnrichMetadataMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        for instr in instructions:
            # Add word count
            word_count = len(instr.content.split())
            instr.metadata.__dict__["word_count"] = word_count

            # Add category as tag
            category = instr.category.value
            if category not in instr.metadata.tags:
                instr.metadata.tags.append(category)

        return instructions
```

### Middleware Chain Example

Apply multiple middleware in sequence:

```python
pipeline = InstructionPipeline()

# Chain: enrich -> validate -> filter
pipeline.add_middleware(EnrichMetadataMiddleware())
pipeline.add_middleware(PriorityValidationMiddleware(min_priority=5))
pipeline.add_middleware(FilterByTagMiddleware("core"))

results = pipeline.execute(instructions)
```

## Example 3: All Exporters

**File:** `examples/example_all_exporters.py`

Demonstrates exporting to all supported formats:
- JSON (Intermediate format)
- Claude
- OpenAI
- Gemini
- Copilot

**Examples included:**
1. Export to all formats
2. Selective export (filter before export)
3. Per-provider export

**Usage:**

```bash
python examples/example_all_exporters.py
```

### Export to All Formats

```python
from instructions_framework import InstructionLoader
from instructions_framework.exporters import (
    IntermediateExporter,
    ClaudeExporter,
    OpenAIExporter,
    GeminiExporter,
    CopilotExporter,
)

loader = InstructionLoader("./sample_instructions")
instructions = loader.load()

# JSON
json_exp = IntermediateExporter()
json_output = json_exp.export(instructions)

# Claude
claude_exp = ClaudeExporter()
claude_output = claude_exp.export(instructions)

# OpenAI
openai_exp = OpenAIExporter()
openai_output = openai_exp.export(instructions)

# Gemini
gemini_exp = GeminiExporter()
gemini_output = gemini_exp.export(instructions)

# Copilot
copilot_exp = CopilotExporter()
copilot_output = copilot_exp.export(instructions)
```

### Selective Export

Export only instructions matching criteria:

```python
# Export only Claude-compatible
claude_compatible = [
    i for i in instructions
    if "claude" in i.metadata.applicability
]
exporter = ClaudeExporter()
output = exporter.export(claude_compatible)

# Export only high priority
high_priority = [i for i in instructions if i.metadata.priority >= 8]
exporter = IntermediateExporter()
output = exporter.export(high_priority)
```

### Per-Provider Export

Export separately for each provider:

```python
# Get unique providers
providers = set()
for instr in instructions:
    providers.update(instr.metadata.applicability)

# Export for each provider
for provider in providers:
    provider_instructions = [
        i for i in instructions
        if provider in i.metadata.applicability
    ]
    exporter = IntermediateExporter()
    output = exporter.export(provider_instructions)
    # Save to file...
```

## Creating Sample Instructions

To run the examples, create sample instruction files:

### Sample 1: Agent Instruction

```yaml
# sample_instructions/agent.md
---
version: "1.0.0"
description: "Implementation agent for feature development"
priority: 8
applicability: ["claude", "openai"]
precedence: "merge"
scope: "global"
deprecated: false
tags: ["agent", "implementation", "coding"]
author: "system"
---

# Implementation Agent

You are an implementation agent responsible for building features end-to-end.

## Role

Develop high-quality, well-tested code that follows best practices.

## Responsibilities

- Analyze requirements thoroughly
- Design clean architecture
- Implement with 95%+ test coverage
- Write comprehensive documentation
- Create pull requests with clear descriptions

## Rules

- Always include unit tests
- Follow the team's coding standards
- Write readable, maintainable code
- Document complex logic
```

### Sample 2: Skill Instruction

```yaml
# sample_instructions/testing.md
---
version: "1.0.0"
description: "Testing skill for comprehensive test coverage"
priority: 7
applicability: ["claude", "openai", "gemini"]
precedence: "merge"
scope: "global"
deprecated: false
tags: ["skill", "testing", "qa"]
author: "system"
---

# Testing Skill

Guidelines for generating comprehensive test suites.

## Test Types

- **Unit Tests**: Test individual functions
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test full workflows

## Test Coverage

Aim for 95%+ code coverage.

## Test Naming

Use: `givenXxx_whenYyy_thenZzz()`
```

### Sample 3: Rule Instruction

```yaml
# sample_instructions/security.md
---
version: "1.0.0"
description: "Security rules for all code"
priority: 10
applicability: ["claude", "openai", "gemini", "copilot"]
precedence: "override"
scope: "global"
deprecated: false
tags: ["security", "rules", "mandatory"]
author: "system"
---

# Security Rules

Non-negotiable security practices.

## Secrets

- Never log secrets
- Never commit secrets
- Use environment variables
- Rotate secrets regularly

## Input Validation

- Always validate user input
- Use parameterized queries
- Escape output appropriately
```

## Running All Examples

Create sample instructions and run all examples:

```bash
# Create sample instructions directory
mkdir -p sample_instructions

# Create sample files (use samples above)
cat > sample_instructions/agent.md <<'EOF'
---
version: "1.0.0"
description: "Implementation agent"
priority: 8
applicability: ["claude", "openai"]
precedence: "merge"
scope: "global"
deprecated: false
tags: ["agent"]
author: "system"
---

# Implementation Agent

Content here...
EOF

# Run examples
python examples/example_basic_usage.py
python examples/example_custom_middleware.py
python examples/example_all_exporters.py
```

## Output Files

After running examples, you'll see output files:

```
output_instructions.json      # JSON intermediate format
output_claude.txt             # Claude system prompt
output_openai.json            # OpenAI format
output_gemini.json            # Gemini format
output_copilot.txt            # Copilot format
```

## Example Use Cases

### Use Case 1: Multi-Provider Instruction Distribution

Load instructions once, export to all platforms:

```python
# Load once
loader = InstructionLoader("./instructions")
instructions = loader.load()

# Export to each platform
for exporter_class, filename in [
    (ClaudeExporter(), "claude.md"),
    (OpenAIExporter(), "openai.json"),
    (GeminiExporter(), "gemini.json"),
    (CopilotExporter(), "copilot.md"),
]:
    output = exporter_class.export(instructions)
    with open(filename, "w") as f:
        f.write(output)
```

### Use Case 2: Provider-Specific Instructions

Export different instructions for different providers:

```python
# Load
loader = InstructionLoader("./instructions")
instructions = loader.load()

# Filter for Claude
claude_only = [i for i in instructions if "claude" in i.metadata.applicability]
claude_exporter = ClaudeExporter()
with open("claude.md", "w") as f:
    f.write(claude_exporter.export(claude_only))

# Filter for OpenAI
openai_only = [i for i in instructions if "openai" in i.metadata.applicability]
openai_exporter = OpenAIExporter()
with open("openai.json", "w") as f:
    f.write(openai_exporter.export(openai_only))
```

### Use Case 3: Quality Gates

Add custom middleware to enforce quality:

```python
class QualityGate(InstructionMiddleware):
    def process(self, instructions):
        # Must have description
        for i in instructions:
            if not i.metadata.description:
                raise ValueError(f"{i.id} missing description")
        
        # Must have tags
        for i in instructions:
            if not i.metadata.tags:
                raise ValueError(f"{i.id} missing tags")
        
        return instructions

pipeline = InstructionPipeline()
pipeline.add_middleware(QualityGate())
results = pipeline.execute(instructions)
```

## Next Steps

- Read [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) for detailed documentation
- Check [API_REFERENCE.md](API_REFERENCE.md) for class documentation
- See [MIGRATION.md](MIGRATION.md) for migrating legacy formats
- Build custom middleware for your use cases
