---
name: Centralized Instructions Framework Design
description: Complete framework for managing instructions across providers with middleware pipeline and plugin extensibility
metadata:
  created: "2026-05-27"
  version: "1.0"
---

# Centralized Instructions Framework with Provider-Specific Export Support

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:writing-plans (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish a centralized instruction management system that serves as the single source of truth for all AI agents, with support for hierarchical customization, provider-specific exports, and extensible middleware/plugin architecture.

**Architecture:** Three-layer system (Schema → Processing → Export) with middleware pipeline for transformations and plugin loader for extensibility.

**Tech Stack:** Python 3.11+, YAML+Markdown hybrid format, JSON intermediate representation, Pytest for testing.

---

## 1. Overview & Vision

### Problem Statement

Currently, instructions are scattered across multiple files with no unified management:
- `master_instruction_set.md` has core rules but no export mechanism
- No hierarchical support (global → provider → agent customization)
- Manual effort to adapt instructions for different AI providers
- No plugin system for custom instruction processors or exporters
- No validation or consistency checking across instruction sets

### Solution

A centralized framework that:
- ✅ Defines instructions once in YAML+Markdown hybrid format
- ✅ Automatically exports to 8+ AI provider platforms in native formats
- ✅ Supports hierarchical instruction inheritance with explicit precedence control
- ✅ Validates completeness, dependencies, and conflicts
- ✅ Provides extensibility through middleware pipeline + plugin loader
- ✅ Offers CLI tools for validation, export, documentation, and conflict detection

---

## 2. Instruction Schema Design

### Format: YAML+Markdown Hybrid

Instructions use YAML frontmatter for metadata + Markdown body for content.

**Example:**
```yaml
---
name: "Test-Driven Development Rule"
version: "1.0"
description: "Every new function must have corresponding tests"
category: "core"
priority: 10
applicability: ["claude", "openai", "gemini"]
precedence: "override"
scope: "global"
deprecated: false
tags: ["testing", "quality", "mandatory"]
depends_on: ["version-check-protocol"]
metadata:
  created: "2026-05-27"
  last_updated: "2026-05-27"
  author: "system"
---

# Test-Driven Development (RULE X)

**Never assume code is correct without tests. Tests are not optional.**

## AAA Pattern

Follow the Arrange-Act-Assert pattern:

```
// Arrange — set up data and objects
// Act     — call the method being tested
// Assert  — verify the outcome
```

## Test Naming Convention

Use `givenX_whenY_thenZ` format:

<!-- metadata: applies_to=java,python,javascript -->
```java
givenValidOrder_whenCreate_thenReturnsSavedOrder()
```

<!-- if: provider=claude -->
This approach ensures clarity and consistency across all Claude-powered agents.
<!-- endif -->

## Exceptions

<!-- metadata: precedence=merge -->
Agent-specific overrides can add provider-specific variations to this rule.
```

### Metadata Fields

| Field | Type | Purpose | Required |
|-------|------|---------|----------|
| `name` | string | Unique instruction identifier | ✅ |
| `version` | semver | Instruction version for tracking changes | ✅ |
| `description` | string | One-line summary | ✅ |
| `category` | enum | core\|behavioral\|constraints\|output-format | ✅ |
| `priority` | 1-10 | Critical (10) to nice-to-have (1) | ✅ |
| `applicability` | list | Which providers this applies to | ✅ |
| `precedence` | enum | merge\|override behavior | ✅ |
| `scope` | enum | global\|provider\|agent-specific | ✅ |
| `deprecated` | bool | Is this instruction obsolete? | ❌ |
| `deprecation_notice` | string | Why deprecated, what to use instead | ❌ |
| `tags` | list | Searchable tags for categorization | ❌ |
| `depends_on` | list | IDs of instructions this depends on | ❌ |
| `metadata.created` | ISO-8601 | When instruction was created | ✅ |
| `metadata.last_updated` | ISO-8601 | Last modification date | ✅ |
| `metadata.author` | string | Creator/maintainer | ✅ |

### Content Features

**Conditional Blocks:**
```markdown
<!-- if: provider=claude -->
Claude-specific guidance here
<!-- endif -->
```

**Section Metadata:**
```markdown
<!-- metadata: applies_to=java,python -->
Language-specific content
```

**Provider Variants:**
```markdown
<!-- variant: openai -->
OpenAI-specific approach
<!-- end_variant -->
```

---

## 3. Hierarchical Instruction System

### Hierarchy Levels

1. **Global** (`instructions/global/`) - Applied to all agents, all providers
2. **Provider** (`instructions/providers/{provider}/`) - Provider-specific customizations
3. **Agent** (`instructions/agents/{agent}/`) - Agent-specific overrides

### Resolution Rules

**Precedence (`merge` mode):**
- Global instructions form the base
- Provider customizations ADD or MODIFY global rules
- Agent-specific customizations ADD or MODIFY provider rules
- Result: All three levels combined, with agent-level taking precedence for conflicts

**Precedence (`override` mode):**
- Agent-specific COMPLETELY REPLACES provider-level
- Provider-level COMPLETELY REPLACES global
- No merging, clean override

**Explicit Control:**
Each instruction defines its own precedence in metadata:
```yaml
precedence: "merge"  # or "override"
```

### Conflict Resolution

When the same instruction appears at multiple levels:
1. Check `precedence` field in metadata
2. If `merge`: Combine intelligently (append sections, merge metadata)
3. If `override`: Replace completely
4. Log conflicts with detailed resolution trace

---

## 4. Processing Pipeline & Middleware

### Pipeline Stages

```
Load → Parse → Validate → Transform → Resolve → Export
```

**Stage 1: Load**
- Read all `.md` files from `instructions/global/`, `instructions/providers/*/`, `instructions/agents/*/`
- Skip hidden files, backup files, directories
- Track source path for each instruction

**Stage 2: Parse**
- Extract YAML frontmatter + Markdown body
- Parse conditional blocks (`<!-- if: -->...<!-- endif -->`)
- Extract metadata markers (`<!-- metadata: -->`)
- Build instruction object with all metadata

**Stage 3: Validate**
- Check required fields present
- Validate enum fields (category, precedence, scope)
- Check dependencies exist (via `depends_on`)
- Verify applicable providers are supported
- Report errors with source file + line number

**Stage 4: Transform**
- Apply middleware pipeline (see below)
- Each middleware can read/modify/filter instructions
- Custom plugins register middleware handlers

**Stage 5: Resolve**
- Apply hierarchical resolution (global → provider → agent)
- Merge or override based on precedence
- Resolve conditional blocks based on target provider
- Strip provider-specific blocks not applicable to target

**Stage 6: Export**
- Generate universal intermediate JSON (see Section 5)
- Call platform-specific exporters for each target
- Write output to platform-native directories

### Middleware Architecture

**Middleware Interface:**
```python
class InstructionMiddleware:
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Transform instructions. Can add, modify, or filter."""
        pass
```

**Core Middleware (Built-in):**
1. `validation_middleware.py` - Schema validation
2. `dependency_middleware.py` - Dependency resolution
3. `conflict_resolver_middleware.py` - Conflict detection
4. `precedence_applier_middleware.py` - Apply merge/override rules
5. `provider_filter_middleware.py` - Filter for target provider
6. `deprecation_middleware.py` - Warn about deprecated instructions

**Custom Middleware:**
- Loaded from `plugins/instruction_processors/`
- Registered in plugin manifest
- Executed in order specified

---

## 5. Export Layer: Universal Intermediate → Platform-Native

### Stage 1: Universal Intermediate Format (JSON Schema)

All instructions convert to standardized JSON:

```json
{
  "instruction": {
    "id": "test-driven-development-rule",
    "name": "Test-Driven Development Rule",
    "category": "core",
    "priority": 10,
    "content": "Full instruction text with markdown formatting",
    "sections": [
      {
        "heading": "AAA Pattern",
        "content": "Follow the Arrange-Act-Assert pattern...",
        "metadata": {
          "applies_to": ["java", "python", "javascript"]
        }
      }
    ],
    "metadata": {
      "version": "1.0",
      "applicability": ["claude", "openai", "gemini"],
      "precedence": "override",
      "scope": "global",
      "dependencies": ["version-check-protocol"],
      "created": "2026-05-27",
      "last_updated": "2026-05-27",
      "author": "system"
    },
    "provider_variants": {
      "claude": {
        "format_hint": "xml-tags",
        "custom_field": "custom_value"
      },
      "openai": {
        "format_hint": "system-message"
      },
      "gemini": {
        "format_hint": "json-structured"
      }
    }
  }
}
```

### Stage 2: Platform-Specific Exporters

Each exporter transforms intermediate JSON to native platform format:

**Claude Exporter** → XML-style tags + markdown
```
Output: .claude/instructions/test_driven_development_rule.md
Format: Markdown with <instruction>, <rule>, <example> tags
```

**OpenAI Exporter** → JSON system message format
```
Output: tools/output/openai/instructions/test_driven_development_rule.json
Format: {"system_message": "...", "metadata": {...}}
```

**Gemini Exporter** → Google instruction JSON
```
Output: .gemini/instructions/test_driven_development_rule.json
Format: Google's structured instruction format
```

**Copilot Exporter** → GitHub Copilot format
```
Output: .github/instructions/test_driven_development_rule.instructions.md
Format: Copilot-specific markdown
```

**Custom Exporter** → Template-based
```
Output: Configurable via template
Format: User-defined template with variable substitution
```

---

## 6. Plugin System & Extensibility

### Plugin Architecture

Plugins are Python modules that register handlers:

```
plugins/
├── instruction_processors/
│   ├── custom_validator.py
│   ├── domain_rules_processor.py
│   └── special_formatter.py
├── exporters/
│   ├── slack_exporter.py
│   ├── jira_exporter.py
│   └── custom_platform_exporter.py
└── manifest.yaml
```

**Plugin Manifest (manifest.yaml):**
```yaml
plugins:
  - name: "custom-validator"
    module: "instruction_processors.custom_validator"
    type: "middleware"
    hooks: ["validate"]
    
  - name: "slack-exporter"
    module: "exporters.slack_exporter"
    type: "exporter"
    target_platform: "slack"
```

### Plugin Types

**Middleware Plugins:**
- Implement `InstructionMiddleware` interface
- Hook into pipeline (validate, transform, resolve phases)
- Can add custom validation, transformation, filtering

**Exporter Plugins:**
- Implement `PlatformExporter` interface
- Register with plugin loader
- Custom platform-specific export formats

**Loader Plugins:**
- Custom instruction format loaders
- Support non-markdown instruction sources
- Example: Load from databases, APIs, external systems

### Plugin Loader

```python
class PluginLoader:
    def load_plugins(self, plugin_dir: Path) -> Dict[str, Plugin]
    def get_middleware(self, hook: str) -> List[InstructionMiddleware]
    def get_exporter(self, platform: str) -> PlatformExporter
    def get_loaders(self) -> List[InstructionLoader]
```

---

## 7. Agent Workspace Structure

### Directory Layout

```
awesome-prompts/
├── instructions/                          # Source of truth for all instructions
│   ├── global/                            # Applied to all agents, all providers
│   │   ├── core_rules.md
│   │   ├── coding_standards.md
│   │   ├── documentation.md
│   │   └── testing.md
│   │
│   ├── providers/                         # Provider-specific customizations
│   │   ├── claude/
│   │   │   ├── formatting_rules.md
│   │   │   ├── tool_usage.md
│   │   │   └── capabilities.md
│   │   ├── openai/
│   │   │   ├── system_message_format.md
│   │   │   └── function_calling.md
│   │   ├── gemini/
│   │   │   ├── json_format.md
│   │   │   └── safety_guidelines.md
│   │   └── custom/
│   │       └── proprietary_format.md
│   │
│   └── agents/                            # Agent-specific overrides
│       ├── implementation_agent/
│       │   ├── special_rules.md
│       │   └── implementation_constraints.md
│       ├── code_review_agent/
│       │   ├── review_standards.md
│       │   └── severity_levels.md
│       └── [other agents]/
│
├── instructions_framework/                # Framework implementation
│   ├── __init__.py
│   ├── schema.py                          # Instruction data model
│   ├── pipeline.py                        # Processing pipeline
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── validator.py
│   │   ├── dependency_resolver.py
│   │   ├── conflict_resolver.py
│   │   ├── precedence_applier.py
│   │   ├── provider_filter.py
│   │   └── deprecation.py
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── base_exporter.py
│   │   ├── intermediate_exporter.py
│   │   ├── claude_exporter.py
│   │   ├── openai_exporter.py
│   │   ├── gemini_exporter.py
│   │   ├── copilot_exporter.py
│   │   └── custom_exporter.py
│   ├── plugins.py                         # Plugin loader & registry
│   ├── cli.py                             # CLI interface
│   └── utils.py                           # Helpers
│
├── plugins/                               # Community & custom plugins
│   ├── instruction_processors/
│   │   ├── __init__.py
│   │   └── [custom processors]
│   ├── exporters/
│   │   ├── __init__.py
│   │   └── [custom exporters]
│   └── manifest.yaml
│
└── tests/
    ├── test_schema.py
    ├── test_pipeline.py
    ├── test_middleware.py
    ├── test_exporters.py
    ├── test_plugins.py
    ├── test_cli.py
    └── fixtures/
        ├── sample_instructions/
        └── expected_exports/
```

---

## 8. CLI Tool

### Command Reference

```bash
# Validate all instructions against schema
python -m instructions_framework validate

# Validate specific directory
python -m instructions_framework validate --path instructions/global/

# Export to all platforms
python -m instructions_framework export --all

# Export to specific platform
python -m instructions_framework export --platform claude,openai --output /path/to/output

# Show instruction hierarchy for an agent with provider filter
python -m instructions_framework show --agent implementation_agent --provider claude

# List all instructions with filtering
python -m instructions_framework list --category core --priority >=8

# Check dependencies and conflicts
python -m instructions_framework check --fix-conflicts

# Generate documentation
python -m instructions_framework docs --output docs/instructions_guide.md

# List loaded plugins
python -m instructions_framework plugins --list

# Test instruction export for a provider
python -m instructions_framework test-export --platform claude --instruction core_rules
```

---

## 9. Testing Strategy

### Unit Tests

- `test_schema.py` - Instruction model, validation, parsing
- `test_middleware.py` - Each middleware component
- `test_exporters.py` - Each exporter (Claude, OpenAI, Gemini, Copilot, Custom)
- `test_plugins.py` - Plugin loader, registration, execution
- `test_cli.py` - CLI commands and output formatting

### Integration Tests

- End-to-end pipeline: Load → Parse → Validate → Transform → Resolve → Export
- Hierarchical resolution: Global + Provider + Agent composition
- Conflict detection and resolution
- Plugin middleware execution chain

### Test Fixtures

- Sample instructions for each category
- Provider-specific test cases
- Expected output files for comparison
- Malformed instruction files (negative tests)

### Coverage Target

- **Core framework:** 90%+
- **Exporters:** 100% (critical for correctness)
- **Middleware:** 85%+
- **Overall:** 85%+

---

## 10. Success Criteria

✅ **Schema & Validation**
- Instruction schema defined and documented
- Validation catches missing required fields, invalid enums, broken dependencies

✅ **Hierarchical System**
- Global → Provider → Agent instructions resolve correctly
- Merge and override precedence work as designed
- Conflict detection identifies issues

✅ **Processing Pipeline**
- All middleware stages execute in correct order
- Custom middleware loads from plugins successfully
- Transformations applied correctly

✅ **Provider Exports**
- Claude exporter produces markdown with XML-style tags
- OpenAI exporter produces JSON system message format
- Gemini exporter produces Google instruction format
- Copilot exporter produces GitHub format
- All 4+ platforms exported correctly

✅ **CLI Tool**
- All commands execute without errors
- Output formatting is clear and useful
- Help documentation complete

✅ **Plugin System**
- Plugins load from manifest without errors
- Middleware plugins hook into pipeline correctly
- Custom exporters execute and produce output

✅ **Testing**
- 85%+ overall coverage
- 100% exporter coverage
- Integration tests validate complete pipeline

✅ **Documentation**
- Instruction schema documented with examples
- Architecture guide for contributors
- Plugin development guide
- CLI usage guide

---

## 11. Implementation Notes

### Backward Compatibility
- Existing `master_instruction_set.md` and intake files migrated as initial global instructions
- Current exporter enhanced to handle instructions directory
- No breaking changes to existing skill/agent export process

### Performance Considerations
- Lazy-load plugins only when needed
- Cache parsed instructions to avoid re-parsing
- Parallel export to multiple providers if possible

### Security & Validation
- Strict YAML parsing to prevent injection attacks
- Validate file paths to prevent directory traversal
- Sandbox plugin execution if running untrusted code

---

## Appendix: Example Instruction Files

**Example: global/core_rules.md**
```yaml
---
name: "Core Quality Rules"
version: "1.0"
description: "Non-negotiable quality standards for all agents"
category: "core"
priority: 10
applicability: ["claude", "openai", "gemini"]
precedence: "override"
scope: "global"
---

# Core Quality Rules

All agents must follow these rules without exception.

## Rule 1: Tests Required
Every new function must have tests.

## Rule 2: Documentation
All public APIs must have documentation.
```

**Example: providers/claude/formatting.md**
```yaml
---
name: "Claude Formatting Guidelines"
version: "1.0"
description: "Claude-specific formatting and output structure"
category: "output-format"
priority: 7
applicability: ["claude"]
precedence: "merge"
scope: "provider"
---

# Claude-Specific Formatting

When exporting to Claude, use these formatting guidelines...
```

**Example: agents/implementation_agent/constraints.md**
```yaml
---
name: "Implementation Agent Constraints"
version: "1.0"
description: "Agent-specific limitations and requirements"
category: "constraints"
priority: 8
applicability: ["claude", "openai"]
precedence: "override"
scope: "agent"
depends_on: ["core_rules"]
---

# Implementation Agent Constraints

This agent has the following specific constraints...
```

