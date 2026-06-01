"""Java/Spring Boot code analyzer - Task 18

Parses Java classes, methods, annotations, and Spring Boot patterns.
Returns structured data with confidence scores.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class JavaClass:
    """Represents a parsed Java class"""

    name: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    methods: List["JavaMethod"] = field(default_factory=list)
    fields: List["JavaField"] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class JavaMethod:
    """Represents a parsed Java method"""

    name: str
    return_type: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class JavaField:
    """Represents a parsed Java field"""

    name: str
    field_type: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    confidence: float = 1.0


class JavaAnalyzer:
    """Analyzes Java/Spring Boot source files"""

    # Pattern to match class declarations
    CLASS_PATTERN = re.compile(
        r"(?:public|private|protected|static)?\s*(?:abstract|final)?\s*class\s+(\w+)"
        r"(?:\s+extends\s+(\w+(?:\s*<[^>]*>)?))?"
        r"(?:\s+implements\s+([^{]+))?"
    )

    # Pattern to match interface declarations
    INTERFACE_PATTERN = re.compile(r"(?:public|private|protected)?\s*interface\s+(\w+)")

    # Pattern to match annotations
    ANNOTATION_PATTERN = re.compile(r"@([A-Za-z_]\w*)")

    # Pattern to match method declarations
    METHOD_PATTERN = re.compile(
        r"(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*"
        r"([\w<>.]+)\s+(\w+)\s*\((.*?)\)"
    )

    # Pattern to match field declarations
    FIELD_PATTERN = re.compile(r"(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*([\w<>.]+)\s+(\w+);")

    # Spring Boot annotations
    SPRING_ANNOTATIONS = {
        "RestController",
        "Controller",
        "Service",
        "Repository",
        "Component",
        "Configuration",
        "Entity",
        "Table",
        "RequestMapping",
        "GetMapping",
        "PostMapping",
        "PutMapping",
        "DeleteMapping",
        "Autowired",
        "Qualifier",
        "Value",
        "ConfigurationProperties",
        "Bean",
        "Transactional",
        "Async",
        "Scheduled",
        "CrossOrigin",
        "EnableWebMvc",
    }

    def __init__(self):
        """Initialize Java analyzer"""
        self.content = ""
        self.classes: List[JavaClass] = []
        self.interfaces: List[str] = []
        self.imports: List[str] = []
        self.package_name: Optional[str] = None

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a Java file and extract classes, methods, annotations.

        Args:
            file_path: Path to Java file

        Returns:
            Dictionary with classes, methods, endpoints, imports, package, interfaces
        """
        file_path = Path(file_path)

        # Validate file
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "classes": [],
                "methods": [],
                "endpoints": [],
            }

        if file_path.suffix != ".java":
            return {
                "success": False,
                "error": f"Not a Java file: {file_path}",
                "classes": [],
                "methods": [],
                "endpoints": [],
            }

        try:
            self.content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "classes": [],
                "methods": [],
                "endpoints": [],
            }

        # Parse content
        self._parse_file()

        # Extract endpoints (Spring Boot mappings)
        endpoints = self._extract_endpoints()

        return {
            "success": True,
            "classes": [asdict(c) for c in self.classes],
            "interfaces": self.interfaces,
            "methods": self._extract_all_methods(),
            "endpoints": endpoints,
            "imports": self.imports,
            "package": self.package_name,
            "confidence": self._calculate_confidence(),
        }

    def _parse_file(self) -> None:
        """Parse Java file content"""
        lines = self.content.split("\n")

        # Extract package
        for line in lines[:20]:  # Usually in first few lines
            if line.strip().startswith("package "):
                match = re.search(r"package\s+([\w.]+);", line)
                if match:
                    self.package_name = match.group(1)
                    break

        # Extract imports
        self._parse_imports(lines)

        # Extract classes and their contents
        self._parse_classes()

        # Extract interfaces
        self._parse_interfaces()

    def _parse_imports(self, lines: List[str]) -> None:
        """Extract import statements"""
        for line in lines:
            if line.strip().startswith("import "):
                match = re.search(r"import\s+([\w.*]+);", line)
                if match:
                    self.imports.append(match.group(1))

    def _parse_classes(self) -> None:
        """Parse class declarations and their members"""
        # Find all class declarations with basic regex
        for match in self.CLASS_PATTERN.finditer(self.content):
            class_name = match.group(1)
            extends = match.group(2) if match.group(2) else None
            implements_raw = match.group(3)

            # Parse implements clause
            implements = []
            if implements_raw:
                implements = [
                    i.strip().split("<")[0]  # Remove generics
                    for i in implements_raw.split(",")
                ]

            # Extract annotations for this class (simple heuristic)
            # Look backwards from class declaration for annotations
            class_pos = match.start()
            annotations = self._extract_annotations_before(class_pos)

            # Extract methods in this class
            methods = self._extract_class_methods(class_name)
            fields = self._extract_class_fields(class_name)

            # Extract modifiers
            modifiers = self._extract_modifiers_for_class(class_name)

            java_class = JavaClass(
                name=class_name,
                modifiers=modifiers,
                annotations=annotations,
                extends=extends,
                implements=implements,
                methods=methods,
                fields=fields,
            )

            self.classes.append(java_class)

    def _parse_interfaces(self) -> None:
        """Parse interface declarations"""
        for match in self.INTERFACE_PATTERN.finditer(self.content):
            self.interfaces.append(match.group(1))

    def _extract_annotations_before(self, position: int, lookback: int = 500) -> List[str]:
        """Extract annotations before a given position"""
        start = max(0, position - lookback)
        snippet = self.content[start:position]

        annotations = []
        for match in self.ANNOTATION_PATTERN.finditer(snippet):
            ann = match.group(1)
            if ann not in annotations:
                annotations.append(ann)

        return annotations

    def _extract_modifiers_for_class(self, class_name: str) -> List[str]:
        """Extract modifiers for a specific class"""
        pattern = rf"(public|private|protected|static|final|abstract)\s+(?:class\s+{class_name})"
        modifiers = []

        for match in re.finditer(pattern, self.content):
            full_text = self.content[max(0, match.start() - 100) : match.start()]
            for word in ["public", "private", "protected", "static", "final", "abstract"]:
                if word in full_text.split():
                    if word not in modifiers:
                        modifiers.append(word)

        return modifiers

    def _extract_class_methods(self, class_name: str) -> List[JavaMethod]:
        """Extract methods from a class"""
        methods = []

        # Simple heuristic: find methods inside class block
        for match in self.METHOD_PATTERN.finditer(self.content):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)

            # Parse parameters
            params = [p.strip() for p in params_str.split(",") if p.strip()]

            method = JavaMethod(
                name=method_name,
                return_type=return_type,
                parameters=params,
            )

            methods.append(method)

        return methods

    def _extract_class_fields(self, class_name: str) -> List[JavaField]:
        """Extract fields from a class"""
        fields = []

        for match in self.FIELD_PATTERN.finditer(self.content):
            field_type = match.group(1)
            field_name = match.group(2)

            field = JavaField(
                name=field_name,
                field_type=field_type,
            )

            fields.append(field)

        return fields

    def _extract_endpoints(self) -> List[Dict[str, Any]]:
        """Extract REST endpoints from Spring Boot annotations"""
        endpoints = []
        mapping_annotations = {
            "RequestMapping",
            "GetMapping",
            "PostMapping",
            "PutMapping",
            "DeleteMapping",
        }

        # Find @RequestMapping, @GetMapping, etc.
        for class_obj in self.classes:
            for ann in class_obj.annotations:
                if ann in mapping_annotations:
                    endpoints.append(
                        {
                            "class": class_obj.name,
                            "annotation": ann,
                            "confidence": 0.9,
                        }
                    )

            for method in class_obj.methods:
                for ann in method.annotations:
                    if ann in mapping_annotations:
                        endpoints.append(
                            {
                                "class": class_obj.name,
                                "method": method.name,
                                "annotation": ann,
                                "confidence": 0.95,
                            }
                        )

        return endpoints

    def _extract_all_methods(self) -> List[Dict[str, Any]]:
        """Extract all methods from all classes"""
        methods = []

        for class_obj in self.classes:
            for method in class_obj.methods:
                methods.append(
                    {
                        "class": class_obj.name,
                        "name": method.name,
                        "return_type": method.return_type,
                        "parameters": method.parameters,
                        "confidence": method.confidence,
                    }
                )

        return methods

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score"""
        if not self.classes:
            return 0.5

        avg_class_confidence = sum(c.confidence for c in self.classes) / len(self.classes)
        return avg_class_confidence
