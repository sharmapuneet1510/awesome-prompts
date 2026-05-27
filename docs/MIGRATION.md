# Migration Guide: Legacy Format to Framework

This guide explains how to migrate existing instructions from legacy formats to the new Instructions Framework.

## Quick Start

```bash
# Generate migration template
python tools/migrate_instructions.py --template docs/MIGRATION_TEMPLATE.md

# Migrate files
python tools/migrate_instructions.py --input ./old_instructions --output ./new_instructions

# Validate migrated files
python -m instructions_framework.cli validate ./new_instructions

# Test export
python -m instructions_framework.cli export ./new_instructions --format claude
```

## Format Comparison

### Legacy Format

Simple structure with minimal metadata:

```json
{
  "id": "agent-001",
  "name": "Implementation Agent",
  "type": "agent",
  "content": "You are an implementation agent...",
  "priority": 5,
  "providers": ["claude", "openai"],
  "version": "1.0.0",
  "description": "Agent for implementing features"
}
```

**Issues with legacy format:**
- Minimal metadata
- No precedence rules
- No dependency tracking
- No provider variants
- Limited validation
- Flat structure

### New Framework Format

Complete structure with full metadata:

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
    "depends_on": [],
    "created": "2024-01-01T00:00:00",
    "last_updated": "2024-01-01T00:00:00",
    "author": "migrated"
  },
  "provider_variants": {},
  "source_path": null
}
```

**Benefits of new format:**
- Complete metadata
- Structured sections
- Dependency tracking
- Provider variants
- Comprehensive validation
- Extensible design

## Field Mapping

| Legacy Field | New Location | Mapping | Notes |
|--------------|--------------|---------|-------|
| id | root.id | Direct | Stays the same |
| name | root.name | Direct | Stays the same |
| type | root.category | Enum conversion | core, behavioral, constraints, output-format |
| content | root.content | Direct | Main instruction text |
| priority | root.metadata.priority | Direct | 1-10 scale |
| providers | root.metadata.applicability | Rename | List of provider names |
| version | root.metadata.version | Direct | Version string |
| description | root.metadata.description | Direct | What it does |
| dependencies | root.metadata.depends_on | Rename | List of dependency IDs |
| (new) | root.metadata.scope | Default: global | Where it applies |
| (new) | root.metadata.precedence | Default: merge | Duplicate resolution |
| (new) | root.metadata.tags | Default: [] | Categorization |
| (new) | root.metadata.deprecated | Default: false | Deprecation status |
| (new) | root.metadata.author | Default: migrated | Author attribution |
| (new) | root.sections | Default: [] | Structured sections |
| (new) | root.provider_variants | Default: {} | Provider-specific content |

## Step-by-Step Migration

### Step 1: Prepare Old Files

Organize legacy instruction files:

```
old_instructions/
├── agent-001.json
├── agent-002.json
├── skill-001.json
└── skill-002.json
```

Supported formats:
- JSON files
- YAML files
- One instruction per file or arrays of instructions

### Step 2: Run Migration Tool

```bash
python tools/migrate_instructions.py \
  --input ./old_instructions \
  --output ./new_instructions \
  --author "System"
```

**Options:**
- `--input`: Source directory with old format files
- `--output`: Destination directory for new files
- `--author`: Author name for migrated instructions (default: "migrated")

**Output:**

```
Successfully migrated 4 file(s)
Migrated: agent-001.json -> agent-001.json
Migrated: agent-002.json -> agent-002.json
Migrated: skill-001.json -> skill-001.json
Migrated: skill-002.json -> skill-002.json
```

### Step 3: Validate Migrated Files

```bash
python -m instructions_framework.cli validate ./new_instructions
```

Expected output (if all valid):

```
All 4 instruction(s) validated successfully
```

Or with errors:

```
Validation failed with 2 error(s):
  agent-001:
    - priority must be 1-10
  skill-001:
    - content is required
```

Fix any validation errors in the JSON files.

### Step 4: Test Exports

Test exporting to each target platform:

```bash
# Test Claude
python -m instructions_framework.cli export ./new_instructions --format claude

# Test OpenAI
python -m instructions_framework.cli export ./new_instructions --format openai

# Test Gemini
python -m instructions_framework.cli export ./new_instructions --format gemini

# Test Copilot
python -m instructions_framework.cli export ./new_instructions --format copilot

# Test JSON
python -m instructions_framework.cli export ./new_instructions --format json --output output.json
```

### Step 5: Review & Adjust

After migration, review and adjust:

1. **Check metadata**: Ensure version, author, priority are correct
2. **Verify dependencies**: Make sure depends_on IDs exist
3. **Add tags**: Add meaningful tags for categorization
4. **Structure content**: Break content into sections if needed
5. **Add variants**: Create provider_variants if needed
6. **Update scope**: Set scope to PROVIDER or AGENT if needed

### Step 6: Replace Old Files

Once satisfied with migrated files:

```bash
# Backup old files
mv old_instructions old_instructions.backup

# Use new files
mv new_instructions old_instructions
```

Or integrate gradually:

```bash
# Copy migrated files to production location
cp -r new_instructions/* production/instructions/
```

## Common Migration Patterns

### Pattern 1: Simple Instruction

**Before:**
```json
{
  "id": "rule-001",
  "name": "Always Be Helpful",
  "type": "core",
  "content": "Always prioritize being helpful to users",
  "priority": 9,
  "providers": ["claude"],
  "version": "1.0.0"
}
```

**After:**
```json
{
  "id": "rule-001",
  "name": "Always Be Helpful",
  "category": "core",
  "priority": 9,
  "content": "Always prioritize being helpful to users",
  "sections": [],
  "metadata": {
    "version": "1.0.0",
    "description": "Core rule for helpfulness",
    "applicability": ["claude"],
    "precedence": "merge",
    "scope": "global",
    "deprecated": false,
    "tags": ["helpfulness"],
    "depends_on": [],
    "author": "migrated"
  },
  "provider_variants": {}
}
```

### Pattern 2: Instruction with Dependencies

**Before:**
```json
{
  "id": "agent-001",
  "name": "Coding Agent",
  "type": "behavioral",
  "content": "You are a coding assistant...",
  "priority": 8,
  "providers": ["claude", "openai"],
  "version": "1.0.0",
  "dependencies": ["rule-001", "rule-002"]
}
```

**After:**
```json
{
  "id": "agent-001",
  "name": "Coding Agent",
  "category": "behavioral",
  "priority": 8,
  "content": "You are a coding assistant...",
  "sections": [],
  "metadata": {
    "version": "1.0.0",
    "description": "Agent for coding tasks",
    "applicability": ["claude", "openai"],
    "precedence": "merge",
    "scope": "global",
    "deprecated": false,
    "tags": ["coding", "agent"],
    "depends_on": ["rule-001", "rule-002"],
    "author": "migrated"
  },
  "provider_variants": {}
}
```

### Pattern 3: Instruction with Provider Variants

**Before:**
```json
{
  "id": "prompt-001",
  "name": "Response Format",
  "type": "output-format",
  "content": "Use standard markdown formatting",
  "priority": 7,
  "providers": ["claude", "openai", "gemini"],
  "version": "1.0.0"
}
```

**After (add provider variants):**
```json
{
  "id": "prompt-001",
  "name": "Response Format",
  "category": "output-format",
  "priority": 7,
  "content": "Use standard markdown formatting",
  "sections": [],
  "metadata": {
    "version": "1.0.0",
    "description": "Format specification for responses",
    "applicability": ["claude", "openai", "gemini"],
    "precedence": "merge",
    "scope": "global",
    "deprecated": false,
    "tags": ["formatting"],
    "depends_on": [],
    "author": "migrated"
  },
  "provider_variants": {
    "claude": {
      "content": "Use Claude-compatible markdown"
    },
    "openai": {
      "content": "Use OpenAI function calling format"
    },
    "gemini": {
      "content": "Use Gemini-compatible format"
    }
  }
}
```

## Handling Migration Issues

### Issue: Missing Required Fields

**Error:** `id is required`

**Solution:** Ensure all instructions have unique IDs.

### Issue: Invalid Priority

**Error:** `priority must be 1-10`

**Solution:** Set priority between 1 and 10.

```python
# In old format
if "priority" not in instr:
    instr["priority"] = 5  # Default
elif instr["priority"] < 1 or instr["priority"] > 10:
    instr["priority"] = 5  # Normalize
```

### Issue: Circular Dependencies

**Error:** `circular dependency detected`

**Solution:** Check depends_on chains for cycles.

```python
# Example: A depends on B, B depends on A
# Remove one dependency or restructure
```

### Issue: Missing Dependencies

**Error:** `dependency 'X' not found`

**Solution:** Ensure all referenced dependencies exist.

```python
# Check all IDs in depends_on exist in loaded set
# Either add missing instruction or remove dependency
```

### Issue: Type Not Recognized

**Error:** `unknown instruction type 'X'`

**Solution:** Map to valid category.

```python
type_map = {
    "agent": "core",
    "skill": "behavioral",
    "rule": "core",
    "constraint": "constraints",
    "format": "output-format",
    # Map your types accordingly
}
```

## Batch Migration Script

For multiple directories:

```python
from pathlib import Path
from tools.migrate_instructions import migrate_file

# Define your old format directories
old_dirs = {
    "agents": "old_agents/",
    "skills": "old_skills/",
    "prompts": "old_prompts/",
}

# Define output directories
new_dirs = {
    "agents": "new_instructions/agents/",
    "skills": "new_instructions/skills/",
    "prompts": "new_instructions/prompts/",
}

# Migrate each directory
for category, old_path in old_dirs.items():
    old_dir = Path(old_path)
    new_dir = Path(new_dirs[category])
    
    if not old_dir.exists():
        print(f"Skipping {category}: directory not found")
        continue
    
    for file in old_dir.glob("*.json"):
        try:
            migrate_file(file, new_dir / file.name, author="system")
            print(f"Migrated {category}/{file.name}")
        except Exception as e:
            print(f"Error migrating {category}/{file.name}: {e}")

print("Batch migration complete")
```

## Testing Migration Quality

After migration, verify:

### 1. Completeness

```bash
# Count files
wc -l old_instructions/*.json new_instructions/*.json
```

### 2. Validity

```bash
# Validate all files
python -m instructions_framework.cli validate new_instructions
```

### 3. Content Preservation

```python
from instructions_framework import InstructionLoader
import json

# Load old
with open("old_instructions/agent-001.json") as f:
    old = json.load(f)

# Load new
loader = InstructionLoader("new_instructions")
instructions = loader.load()
new = [i for i in instructions if i.id == "agent-001"][0]

# Compare
assert old["name"] == new.name
assert old["content"] == new.content
assert old["priority"] == new.metadata.priority
print("Migration verified!")
```

### 4. Export Compatibility

```bash
# Test all export formats work
for fmt in json claude openai gemini copilot; do
    echo "Testing $fmt..."
    python -m instructions_framework.cli export new_instructions --format $fmt > /dev/null
    if [ $? -eq 0 ]; then
        echo "  ✓ $fmt OK"
    else
        echo "  ✗ $fmt FAILED"
    fi
done
```

## Post-Migration Checklist

- [ ] All files migrated successfully
- [ ] All files pass validation
- [ ] All export formats work
- [ ] Content preserved accurately
- [ ] Metadata reviewed and corrected
- [ ] Tags added appropriately
- [ ] Dependencies verified
- [ ] Provider variants created if needed
- [ ] Old files backed up
- [ ] New files integrated into workflow

## Rollback Plan

If migration has issues:

```bash
# Restore from backup
rm -rf production/instructions
mv production/instructions.backup production/instructions

# Fix issues in migration scripts
# Re-run migration with corrections
# Re-validate all files
# Carefully test before deploying again
```

## Next Steps

After successful migration:

1. Update CI/CD to use new framework
2. Train team on new format
3. Update documentation
4. Add new instructions using new format
5. Maintain backward compatibility during transition (if needed)
6. Eventually deprecate legacy format
