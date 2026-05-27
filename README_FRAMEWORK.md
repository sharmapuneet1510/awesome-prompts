# Instructions Framework

A comprehensive, extensible framework for managing, validating, and exporting instruction files for AI systems. Built with modularity, validation, and multi-provider support in mind.

## Features

- **Unified Schema**: Single canonical format for all instruction types (agents, skills, prompts)
- **Multi-Provider Support**: Export to Claude, OpenAI, Gemini, Copilot, and custom formats
- **Middleware Pipeline**: Transform and validate instructions with pluggable middleware
- **Plugin System**: Register custom middleware and exporters dynamically
- **CLI Tool**: Command-line interface for load, validate, export, and check operations
- **Migration Support**: Tools to migrate from legacy instruction formats
- **Comprehensive Validation**: Catch errors early with multi-level validation

## Quick Start

### Installation

```bash
# Navigate to project root
cd /path/to/awesome-prompts

# Install framework in development mode
pip install -e instructions_framework/
```

### Basic Usage

```python
from instructions_framework import InstructionLoader, InstructionPipeline, IntermediateExporter

# Load instructions from a directory
loader = InstructionLoader("path/to/instructions")
instructions = loader.load()

# Process through pipeline (applies middleware)
pipeline = InstructionPipeline()
results = pipeline.execute(instructions)

# Export to JSON
exporter = IntermediateExporter()
json_output = exporter.export(instructions)
```

### CLI Usage

```bash
# Load instructions
python -m instructions_framework.cli load ./instructions

# Validate instructions
python -m instructions_framework.cli validate ./instructions

# Export to different formats
python -m instructions_framework.cli export ./instructions --format claude
python -m instructions_framework.cli export ./instructions --format openai --output output.json

# Check for issues
python -m instructions_framework.cli check ./instructions

# List available tools
python -m instructions_framework.cli list
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Input (Files/API)                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│          Parser (YAML/JSON → Schema)                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│          Loader (Discover & Aggregate)                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│     Pipeline (Middleware Chain Execution)                │
│  ├─ Validator Middleware                                │
│  ├─ Dependency Resolver Middleware                       │
│  ├─ Conflict Detector Middleware                         │
│  ├─ Precedence Applier Middleware                        │
│  └─ Provider Filter Middleware                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│         Registry (Plugin System)                         │
│  ├─ Custom Middleware                                   │
│  └─ Custom Exporters                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│         Exporters (Format Conversion)                    │
│  ├─ JSON                                                │
│  ├─ Claude                                              │
│  ├─ OpenAI                                              │
│  ├─ Gemini                                              │
│  └─ Copilot                                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│            Output (Files/API Response)                   │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### Schema (`schema.py`)

Defines the canonical instruction data model:

- **InstructionCategory**: CORE, BEHAVIORAL, CONSTRAINTS, OUTPUT_FORMAT
- **InstructionPrecedence**: MERGE (combine), OVERRIDE (replace)
- **InstructionScope**: GLOBAL, PROVIDER, AGENT
- **InstructionMetadata**: Version, author, priority, dependencies, timestamps
- **Instruction**: Complete instruction with metadata, content, sections, variants

### Parser (`parser.py`)

Converts raw files to Instruction objects:

- Reads YAML/JSON from files
- Extracts metadata frontmatter
- Validates basic structure
- Returns Instruction objects

### Loader (`loader.py`)

Discovers and loads instructions:

- Scans directories recursively
- Loads from multiple file formats
- Aggregates results
- Supports filtering by pattern

### Pipeline (`pipeline.py`)

Executes middleware chain:

- Applies middleware in order
- Tracks errors and warnings
- Returns processing results
- Supports custom middleware

### Middleware System (`middleware/`)

Built-in middleware:

1. **Validator**: Validates instruction format and content
2. **Dependency Resolver**: Tracks and resolves dependencies
3. **Conflict Detector**: Identifies conflicting instructions
4. **Precedence Applier**: Resolves duplicates per precedence rules
5. **Provider Filter**: Filters by target provider

### Plugin Registry (`plugins.py`)

Dynamic plugin system:

- Register custom middleware and exporters
- Load plugins from filesystem
- Access plugins by name
- Global registry for singleton access

### Exporters (`exporters/`)

Platform-specific formatters:

1. **IntermediateExporter**: JSON intermediate format
2. **ClaudeExporter**: Claude system prompt format
3. **OpenAIExporter**: OpenAI format
4. **GeminiExporter**: Google Gemini format
5. **CopilotExporter**: GitHub Copilot format

### CLI (`cli.py`)

Command-line interface:

- `load`: Load and list instructions
- `validate`: Check instruction validity
- `export`: Convert to target format
- `check`: Scan for conflicts/issues
- `apply-middleware`: Apply specific middleware
- `list`: Show available tools

## Key Concepts

### Instruction Precedence

When duplicate instructions are loaded:
- **MERGE**: Combine content, metadata union
- **OVERRIDE**: Latest version replaces previous

### Instruction Scope

Where instructions apply:
- **GLOBAL**: All providers
- **PROVIDER**: Specific provider (claude, openai, etc.)
- **AGENT**: Specific agent role

### Provider Variants

Provider-specific overrides in `provider_variants`:

```json
{
  "id": "example-instruction",
  "name": "Example",
  "content": "Base instruction text",
  "provider_variants": {
    "claude": {
      "content": "Claude-specific version"
    },
    "openai": {
      "content": "OpenAI-specific version"
    }
  }
}
```

## Testing

```bash
# Run all tests
pytest tests/test_*.py -v

# Run specific test module
pytest tests/test_plugins.py -v

# Run with coverage
pytest tests/ --cov=instructions_framework
```

## File Structure

```
instructions_framework/
├── __init__.py                 # Package exports
├── schema.py                   # Data models
├── parser.py                   # File parsing
├── loader.py                   # Directory loading
├── pipeline.py                 # Middleware execution
├── plugins.py                  # Plugin registry
├── cli.py                      # CLI interface
├── middleware/
│   ├── base.py                 # Base middleware class
│   ├── validator.py            # Validation middleware
│   ├── dependency_resolver.py  # Dependency resolution
│   ├── conflict_detector.py    # Conflict detection
│   ├── precedence_applier.py   # Precedence handling
│   └── provider_filter.py      # Provider filtering
└── exporters/
    ├── base.py                 # Base exporter class
    ├── intermediate.py         # JSON format
    ├── claude.py               # Claude format
    ├── openai.py               # OpenAI format
    ├── gemini.py               # Gemini format
    └── copilot.py              # Copilot format
```

## Next Steps

- See [FRAMEWORK_GUIDE.md](docs/FRAMEWORK_GUIDE.md) for detailed usage
- See [API_REFERENCE.md](docs/API_REFERENCE.md) for class documentation
- Check [examples/](examples/) for working examples
- Review [MIGRATION.md](docs/MIGRATION.md) for legacy format migration

## License

Part of the Awesome Prompts project
