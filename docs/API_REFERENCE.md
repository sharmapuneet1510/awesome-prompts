# API Reference

Complete API documentation for all classes and functions in the Instructions Framework.

## Table of Contents

- [Schema Classes](#schema-classes)
- [Parser Functions](#parser-functions)
- [Loader Class](#loader-class)
- [Pipeline Class](#pipeline-class)
- [Plugin Registry](#plugin-registry)
- [Middleware Classes](#middleware-classes)
- [Exporter Classes](#exporter-classes)
- [CLI Functions](#cli-functions)

## Schema Classes

### InstructionCategory

Enum for instruction categories.

```python
class InstructionCategory(str, Enum):
    CORE = "core"
    BEHAVIORAL = "behavioral"
    CONSTRAINTS = "constraints"
    OUTPUT_FORMAT = "output-format"
```

**Values:**
- `CORE`: Fundamental rules
- `BEHAVIORAL`: Behavior guidelines
- `CONSTRAINTS`: Limitations and rules
- `OUTPUT_FORMAT`: Output specifications

### InstructionPrecedence

Enum for duplicate resolution strategy.

```python
class InstructionPrecedence(str, Enum):
    MERGE = "merge"
    OVERRIDE = "override"
```

**Values:**
- `MERGE`: Combine duplicate instructions
- `OVERRIDE`: Replace with latest version

### InstructionScope

Enum for instruction application scope.

```python
class InstructionScope(str, Enum):
    GLOBAL = "global"
    PROVIDER = "provider"
    AGENT = "agent"
```

**Values:**
- `GLOBAL`: Applies everywhere
- `PROVIDER`: Specific provider
- `AGENT`: Specific agent role

### InstructionMetadata

Metadata for an instruction.

```python
@dataclass
class InstructionMetadata:
    version: str
    description: str
    priority: int
    applicability: List[str]
    precedence: InstructionPrecedence
    scope: InstructionScope
    deprecated: bool = False
    deprecation_notice: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = "system"
```

**Methods:**

```python
def validate(self) -> List[str]:
    """
    Validate metadata.
    
    Returns:
        List of error messages. Empty list if valid.
    """
```

**Validation Rules:**
- version: Required, non-empty
- description: Required, non-empty
- priority: 1-10
- applicability: Not empty
- author: Non-empty
- deprecated: If true, deprecation_notice required

### InstructionSection

A structured section within an instruction.

```python
@dataclass
class InstructionSection:
    heading: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Fields:**
- `heading`: Section title
- `content`: Section body (markdown)
- `metadata`: Optional key-value pairs

### Instruction

Complete instruction with all data.

```python
@dataclass
class Instruction:
    id: str
    name: str
    category: InstructionCategory
    metadata: InstructionMetadata
    content: str
    sections: List[InstructionSection] = field(default_factory=list)
    provider_variants: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    source_path: Optional[str] = None
```

**Methods:**

```python
def validate(self) -> List[str]:
    """
    Validate instruction.
    
    Returns:
        List of error messages. Empty list if valid.
    """

def to_dict(self) -> Dict[str, Any]:
    """
    Convert to dictionary for export.
    
    Returns:
        Dictionary representation of instruction.
    """
```

**Validation Rules:**
- id: Required, non-empty
- name: Required, non-empty
- content: Required, non-empty
- sections: Headings must be non-empty
- provider_variants: Must have valid structure
- metadata: Must pass metadata validation

## Parser Functions

### parse_instruction_file

Parse a single instruction file.

```python
def parse_instruction_file(file_path: Path) -> Instruction:
    """
    Parse an instruction file (YAML, JSON, or Markdown with frontmatter).
    
    Args:
        file_path: Path to instruction file
        
    Returns:
        Parsed Instruction object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If parsing fails
        
    Example:
        instruction = parse_instruction_file("instruction.md")
    """
```

**Supported Formats:**
- YAML with frontmatter: `---\nmetadata\n---\ncontent`
- JSON: Complete Instruction as JSON object
- Markdown: Content with YAML frontmatter

## Loader Class

### InstructionLoader

Discovers and loads instructions from directories.

```python
class InstructionLoader:
    def __init__(self, directory: Path):
        """
        Initialize loader for a directory.
        
        Args:
            directory: Path to instructions directory
        """
    
    def load(self, pattern: str = "*.md", 
             glob_pattern: Optional[str] = None) -> List[Instruction]:
        """
        Load instructions from directory.
        
        Args:
            pattern: File pattern to match (default: "*.md")
            glob_pattern: Glob pattern for recursive search
            
        Returns:
            List of loaded instructions
            
        Raises:
            FileNotFoundError: If directory doesn't exist
        """
    
    def load_file(self, file_path: Path) -> Optional[Instruction]:
        """
        Load a single file.
        
        Args:
            file_path: Path to instruction file
            
        Returns:
            Instruction or None if parse fails
        """
```

**Examples:**

```python
loader = InstructionLoader("./instructions")

# Load all markdown files
instructions = loader.load()

# Load specific pattern
instructions = loader.load(pattern="*agent*.md")

# Recursive glob
instructions = loader.load(glob_pattern="**/*.md")
```

## Pipeline Class

### InstructionPipeline

Executes middleware pipeline on instructions.

```python
class InstructionPipeline:
    def __init__(self):
        """Initialize empty pipeline."""
    
    def add_middleware(self, middleware: InstructionMiddleware) -> None:
        """
        Add middleware to pipeline.
        
        Args:
            middleware: Middleware instance to add
        """
    
    def set_provider(self, provider: str) -> None:
        """
        Set target provider for filtering.
        
        Args:
            provider: Provider name (e.g., "claude")
        """
    
    def execute(self, instructions: List[Instruction]) -> PipelineResult:
        """
        Execute pipeline on instructions.
        
        Args:
            instructions: Instructions to process
            
        Returns:
            PipelineResult with processed instructions and any errors
        """
    
    def get_middleware(self, name: str) -> Optional[InstructionMiddleware]:
        """
        Get middleware by name.
        
        Args:
            name: Middleware name
            
        Returns:
            Middleware instance or None
        """
    
    def list_middleware(self) -> List[str]:
        """
        Get list of middleware names.
        
        Returns:
            List of middleware names
        """
```

### PipelineResult

Result from pipeline execution.

```python
@dataclass
class PipelineResult:
    instructions: List[Instruction]
    errors: List[str]
    warnings: List[str]
    has_errors: bool
    has_warnings: bool
```

**Examples:**

```python
pipeline = InstructionPipeline()
pipeline.set_provider("claude")

results = pipeline.execute(instructions)

if results.has_errors:
    for error in results.errors:
        print(f"Error: {error}")

processed = results.instructions
```

## Plugin Registry

### PluginRegistry

Registry for custom middleware and exporters.

```python
class PluginRegistry:
    def __init__(self):
        """Initialize empty registry."""
    
    def register_middleware(self, name: str, 
                          cls: Type[InstructionMiddleware]) -> None:
        """
        Register custom middleware class.
        
        Args:
            name: Unique name for middleware
            cls: Middleware class (must inherit from InstructionMiddleware)
            
        Raises:
            TypeError: If cls is not InstructionMiddleware subclass
            ValueError: If name already registered
        """
    
    def register_exporter(self, name: str, 
                         cls: Type[BaseExporter]) -> None:
        """
        Register custom exporter class.
        
        Args:
            name: Unique name for exporter
            cls: Exporter class (must inherit from BaseExporter)
            
        Raises:
            TypeError: If cls is not BaseExporter subclass
            ValueError: If name already registered
        """
    
    def get_middleware(self, name: str) -> Optional[Type[InstructionMiddleware]]:
        """
        Retrieve registered middleware class.
        
        Args:
            name: Middleware name
            
        Returns:
            Middleware class or None if not found
        """
    
    def get_exporter(self, name: str) -> Optional[Type[BaseExporter]]:
        """
        Retrieve registered exporter class.
        
        Args:
            name: Exporter name
            
        Returns:
            Exporter class or None if not found
        """
    
    def list_middleware(self) -> Dict[str, Type[InstructionMiddleware]]:
        """Get all registered middleware."""
    
    def list_exporters(self) -> Dict[str, Type[BaseExporter]]:
        """Get all registered exporters."""
    
    def load_plugins(self, plugin_dir: Path) -> None:
        """
        Dynamically load plugins from directory.
        
        Args:
            plugin_dir: Path to plugin directory
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            ImportError: If plugin import fails
        """
    
    def unregister_middleware(self, name: str) -> bool:
        """Unregister middleware. Returns True if found."""
    
    def unregister_exporter(self, name: str) -> bool:
        """Unregister exporter. Returns True if found."""
    
    def clear_all(self) -> None:
        """Clear all registered plugins."""
```

### get_global_registry

Get or create global registry singleton.

```python
def get_global_registry() -> PluginRegistry:
    """
    Get or create global plugin registry.
    
    Returns:
        Global PluginRegistry instance
    """
```

**Example:**

```python
from instructions_framework.plugins import get_global_registry

registry = get_global_registry()
registry.register_middleware("custom", MyMiddleware)

# Available everywhere
registry2 = get_global_registry()
assert registry2.get_middleware("custom") is MyMiddleware
```

## Middleware Classes

### InstructionMiddleware (Base)

Base class for all middleware.

```python
class InstructionMiddleware(ABC):
    @abstractmethod
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Process instructions.
        
        Args:
            instructions: Instructions to process
            
        Returns:
            Processed instructions (can be fewer, more, or modified)
        """
```

### ValidatorMiddleware

Validates instruction schema and content.

```python
class ValidatorMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Validates each instruction, tracks validation errors."""
```

### DependencyResolverMiddleware

Resolves and validates dependencies.

```python
class DependencyResolverMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Resolves dependencies, detects circular dependencies."""
```

### ConflictDetectorMiddleware

Detects conflicting instructions.

```python
class ConflictDetectorMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Detects duplicate IDs, incompatible scopes, provider conflicts."""
```

### PrecedenceApplierMiddleware

Applies precedence rules to duplicates.

```python
class PrecedenceApplierMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Applies MERGE or OVERRIDE per instruction precedence setting."""
```

### ProviderFilterMiddleware

Filters instructions by provider.

```python
class ProviderFilterMiddleware(InstructionMiddleware):
    def __init__(self, provider: str):
        """
        Initialize with target provider.
        
        Args:
            provider: Provider name (e.g., "claude")
        """
    
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Filters to only instructions applicable to provider."""
```

## Exporter Classes

### BaseExporter (Base)

Base class for all exporters.

```python
class BaseExporter(ABC):
    @abstractmethod
    def export(self, instructions: List[Instruction], **kwargs) -> Any:
        """
        Export instructions to format-specific structure.
        
        Args:
            instructions: Instructions to export
            **kwargs: Format-specific options
            
        Returns:
            Exported instructions in target format
        """
```

### IntermediateExporter

Exports to JSON intermediate format (all data).

```python
class IntermediateExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export to JSON.
        
        Returns:
            JSON string with all instruction data
        """
```

### ClaudeExporter

Exports to Claude system prompt format.

```python
class ClaudeExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export to Claude format.
        
        Returns:
            Claude system prompt text
        """
```

### OpenAIExporter

Exports to OpenAI format.

```python
class OpenAIExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export to OpenAI format.
        
        Returns:
            OpenAI instruction JSON
        """
```

### GeminiExporter

Exports to Google Gemini format.

```python
class GeminiExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export to Gemini format.
        
        Returns:
            Gemini instruction JSON
        """
```

### CopilotExporter

Exports to GitHub Copilot format.

```python
class CopilotExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export to Copilot format.
        
        Returns:
            Copilot instruction text
        """
```

## CLI Functions

### main

CLI entry point.

```python
def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success)
    """
```

**Commands:**

| Command | Arguments | Description |
|---------|-----------|-------------|
| `load` | `path` | Load and list instructions |
| `validate` | `path` | Validate instruction files |
| `export` | `path --format --output` | Export to format |
| `check` | `path` | Check for conflicts |
| `apply-middleware` | `path middleware` | Apply middleware |
| `list` | | List available tools |

**Examples:**

```bash
# Load
python -m instructions_framework.cli load ./instructions

# Validate
python -m instructions_framework.cli validate ./instructions

# Export
python -m instructions_framework.cli export ./instructions --format claude --output output.txt

# Check
python -m instructions_framework.cli check ./instructions

# Apply middleware
python -m instructions_framework.cli apply-middleware ./instructions validator

# List
python -m instructions_framework.cli list
```

## Migration Functions

### migrate_instruction

Convert old format to new format.

```python
def migrate_instruction(old_format: Dict[str, Any], 
                       author: str = "migrated") -> Instruction:
    """
    Convert old format dictionary to new Instruction.
    
    Args:
        old_format: Old format instruction dict
        author: Author name for migrated instructions
        
    Returns:
        New Instruction object
        
    Raises:
        KeyError: If required fields missing
        ValueError: If values invalid
    """
```

### migrate_file

Migrate a file from old to new format.

```python
def migrate_file(input_path: Path, output_path: Path, 
                author: str = "migrated") -> bool:
    """
    Migrate instruction file.
    
    Args:
        input_path: Old format file
        output_path: New format file output
        author: Author name
        
    Returns:
        True if successful
    """
```

### create_migration_template

Create migration template documentation.

```python
def create_migration_template(output_path: Path) -> None:
    """
    Create migration guide template.
    
    Args:
        output_path: Path to write template
    """
```
