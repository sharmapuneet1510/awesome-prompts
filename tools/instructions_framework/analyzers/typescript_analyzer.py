"""TypeScript/JavaScript code analyzer - Task 20

Parses TS/JS components, exports, imports, and interfaces.
Returns structured data with confidence scores.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TypeScriptComponent:
    """Represents a parsed TypeScript/JavaScript component"""

    name: str
    kind: str  # "class", "function", "interface", "type"
    exports: bool = False
    decorators: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    docstring: Optional[str] = None
    confidence: float = 1.0


@dataclass
class TypeScriptInterface:
    """Represents a parsed TypeScript interface"""

    name: str
    properties: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    confidence: float = 1.0


class TypeScriptAnalyzer:
    """Analyzes TypeScript/JavaScript source files"""

    # Pattern to match imports
    IMPORT_PATTERN = re.compile(
        r"import\s+(?:{[^}]*}|\w+(?:\s*,\s*{[^}]*})?)\s+from\s+['\"]([^'\"]+)['\"]"
    )

    # Pattern to match exports
    EXPORT_PATTERN = re.compile(r"export\s+(?:default\s+)?(class|function|interface|type|const)\s+(\w+)")

    # Pattern to match React components
    COMPONENT_PATTERN = re.compile(r"(?:export\s+)?(?:const|function)\s+(\w+)\s*(?::|=).*?=>?\s*(?:\{|<)")

    # Pattern to match interfaces
    INTERFACE_PATTERN = re.compile(r"(?:export\s+)?interface\s+(\w+)\s*(?:\{)")

    # Pattern to match types
    TYPE_PATTERN = re.compile(r"(?:export\s+)?type\s+(\w+)\s*(?:=|{)")

    # Pattern to match function declarations
    FUNCTION_PATTERN = re.compile(
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)\s*(?::\s*([\w<>.,\[\]]+))?"
    )

    # Pattern to match class declarations
    CLASS_PATTERN = re.compile(r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?")

    # Pattern to match decorators
    DECORATOR_PATTERN = re.compile(r"@(\w+)")

    def __init__(self):
        """Initialize TypeScript analyzer"""
        self.content = ""
        self.components: List[TypeScriptComponent] = []
        self.interfaces: List[TypeScriptInterface] = []
        self.imports: List[str] = []
        self.exports: List[str] = []
        self.decorators: List[str] = []

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a TypeScript/JavaScript file.

        Args:
            file_path: Path to TS/JS file

        Returns:
            Dictionary with components, interfaces, imports, exports
        """
        file_path = Path(file_path)

        # Validate file
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "components": [],
                "interfaces": [],
            }

        if file_path.suffix not in [".ts", ".tsx", ".js", ".jsx"]:
            return {
                "success": False,
                "error": f"Not a TypeScript/JavaScript file: {file_path}",
                "components": [],
                "interfaces": [],
            }

        try:
            self.content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "components": [],
                "interfaces": [],
            }

        # Parse content
        self._parse_file()

        return {
            "success": True,
            "components": [asdict(c) for c in self.components],
            "interfaces": [asdict(i) for i in self.interfaces],
            "imports": self.imports,
            "exports": self.exports,
            "decorators": self.decorators,
            "confidence": self._calculate_confidence(),
        }

    def _parse_file(self) -> None:
        """Parse TypeScript/JavaScript file content"""
        # Remove comments to avoid false positives
        clean_content = self._remove_comments(self.content)

        # Extract imports
        self._extract_imports(clean_content)

        # Extract exports
        self._extract_exports(clean_content)

        # Extract decorators
        self._extract_decorators(clean_content)

        # Extract interfaces
        self._extract_interfaces(clean_content)

        # Extract types
        self._extract_types(clean_content)

        # Extract functions
        self._extract_functions(clean_content)

        # Extract classes
        self._extract_classes(clean_content)

        # Extract React components (arrow functions & components)
        self._extract_components(clean_content)

    def _remove_comments(self, content: str) -> str:
        """Remove single-line and multi-line comments"""
        # Remove single-line comments
        content = re.sub(r"//.*", "", content)

        # Remove multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        return content

    def _extract_imports(self, content: str) -> None:
        """Extract import statements"""
        for match in self.IMPORT_PATTERN.finditer(content):
            module = match.group(1)
            if module not in self.imports:
                self.imports.append(module)

    def _extract_exports(self, content: str) -> None:
        """Extract export statements"""
        for match in self.EXPORT_PATTERN.finditer(content):
            kind = match.group(1)
            name = match.group(2)

            if name not in self.exports:
                self.exports.append(name)

            # Add to components
            self.components.append(
                TypeScriptComponent(
                    name=name,
                    kind=kind,
                    exports=True,
                )
            )

    def _extract_decorators(self, content: str) -> None:
        """Extract decorator usages"""
        for match in self.DECORATOR_PATTERN.finditer(content):
            dec = match.group(1)
            if dec not in self.decorators:
                self.decorators.append(dec)

    def _extract_interfaces(self, content: str) -> None:
        """Extract interface declarations"""
        for match in self.INTERFACE_PATTERN.finditer(content):
            name = match.group(1)

            # Extract properties from interface (simple heuristic)
            # Find the block after interface declaration
            start_pos = match.end()
            brace_count = 0
            block_content = ""

            for i, char in enumerate(content[start_pos:]):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        block_content = content[start_pos : start_pos + i]
                        break
                elif brace_count > 0:
                    block_content += char

            properties = self._extract_properties(block_content)
            methods = self._extract_interface_methods(block_content)

            interface = TypeScriptInterface(
                name=name,
                properties=properties,
                methods=methods,
            )

            self.interfaces.append(interface)

    def _extract_types(self, content: str) -> None:
        """Extract type definitions"""
        for match in self.TYPE_PATTERN.finditer(content):
            name = match.group(1)

            self.components.append(
                TypeScriptComponent(
                    name=name,
                    kind="type",
                )
            )

    def _extract_functions(self, content: str) -> None:
        """Extract function declarations"""
        for match in self.FUNCTION_PATTERN.finditer(content):
            name = match.group(1)
            params = match.group(2) if match.group(2) else ""
            returns = match.group(3) if match.group(3) else None

            parameters = [p.strip() for p in params.split(",") if p.strip()]

            # Check if exported
            is_exported = f"export" in content[max(0, match.start() - 20) : match.start()]

            self.components.append(
                TypeScriptComponent(
                    name=name,
                    kind="function",
                    parameters=parameters,
                    returns=returns,
                    exports=is_exported,
                )
            )

    def _extract_classes(self, content: str) -> None:
        """Extract class declarations"""
        for match in self.CLASS_PATTERN.finditer(content):
            name = match.group(1)

            # Check if exported
            is_exported = "export" in content[max(0, match.start() - 20) : match.start()]

            self.components.append(
                TypeScriptComponent(
                    name=name,
                    kind="class",
                    exports=is_exported,
                )
            )

    def _extract_components(self, content: str) -> None:
        """Extract React/Vue components (arrow functions returning JSX)"""
        for match in self.COMPONENT_PATTERN.finditer(content):
            name = match.group(1)

            # Check if it's a React hook (starts with "use")
            is_hook = name.startswith("use")

            kind = "hook" if is_hook else "component"

            # Check if exported
            is_exported = "export" in content[max(0, match.start() - 20) : match.start()]

            # Check if already added
            if not any(c.name == name for c in self.components):
                self.components.append(
                    TypeScriptComponent(
                        name=name,
                        kind=kind,
                        exports=is_exported,
                    )
                )

    def _extract_properties(self, block_content: str) -> List[str]:
        """Extract properties from an interface or type"""
        properties = []

        # Match property declarations: name: type;
        pattern = re.compile(r"(\w+)\s*:\s*([^;]+);")

        for match in pattern.finditer(block_content):
            prop = match.group(1)
            if prop not in properties:
                properties.append(prop)

        return properties

    def _extract_interface_methods(self, block_content: str) -> List[str]:
        """Extract method declarations from interface"""
        methods = []

        # Match method declarations: name(params): returnType;
        pattern = re.compile(r"(\w+)\s*\((.*?)\)\s*:\s*([^;]+);")

        for match in pattern.finditer(block_content):
            method = match.group(1)
            if method not in methods:
                methods.append(method)

        return methods

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score"""
        if not self.content:
            return 0.0

        total_items = len(self.components) + len(self.interfaces)
        if total_items == 0:
            return 0.5

        return 0.9
