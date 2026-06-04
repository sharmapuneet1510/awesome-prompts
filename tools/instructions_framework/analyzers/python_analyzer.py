"""Python code analyzer - Task 19

Parses Python modules, classes, functions, and decorators.
Returns structured data with confidence scores.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class PythonClass:
    """Represents a parsed Python class"""

    name: str
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    methods: List["PythonFunction"] = field(default_factory=list)
    docstring: Optional[str] = None
    confidence: float = 1.0


@dataclass
class PythonFunction:
    """Represents a parsed Python function or method"""

    name: str
    decorators: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    is_async: bool = False
    confidence: float = 1.0


class PythonAnalyzer:
    """Analyzes Python source files using AST"""

    def __init__(self):
        """Initialize Python analyzer"""
        self.content = ""
        self.tree: Optional[ast.AST] = None
        self.classes: List[PythonClass] = []
        self.functions: List[PythonFunction] = []
        self.imports: List[str] = []
        self.decorators: List[str] = []

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a Python file and extract classes, functions, decorators.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary with classes, functions, decorators, imports, endpoints
        """
        file_path = Path(file_path)

        # Validate file
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "classes": [],
                "functions": [],
                "decorators": [],
            }

        if file_path.suffix != ".py":
            return {
                "success": False,
                "error": f"Not a Python file: {file_path}",
                "classes": [],
                "functions": [],
                "decorators": [],
            }

        try:
            self.content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "classes": [],
                "functions": [],
                "decorators": [],
            }

        # Parse content
        try:
            self.tree = ast.parse(self.content)
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error in Python file: {e}",
                "classes": [],
                "functions": [],
                "decorators": [],
            }

        # Extract data
        self._extract_from_ast()

        # Extract endpoints (Flask, FastAPI, Django routes)
        endpoints = self._extract_endpoints()

        return {
            "success": True,
            "classes": [asdict(c) for c in self.classes],
            "functions": [asdict(f) for f in self.functions],
            "decorators": self.decorators,
            "imports": self.imports,
            "endpoints": endpoints,
            "confidence": self._calculate_confidence(),
        }

    def _extract_from_ast(self) -> None:
        """Extract data from AST"""
        if not self.tree:
            return

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self._extract_class(node)
            elif isinstance(node, ast.FunctionDef):
                self._extract_function(node)
            elif isinstance(node, ast.AsyncFunctionDef):
                self._extract_async_function(node)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                self._extract_import(node)

    def _extract_class(self, node: ast.ClassDef) -> None:
        """Extract class information"""
        decorators = [d.id if isinstance(d, ast.Name) else ast.unparse(d) for d in node.decorator_list]

        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            else:
                base_classes.append(ast.unparse(base))

        docstring = ast.get_docstring(node)

        methods: List[PythonFunction] = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._extract_function_node(item))
            elif isinstance(item, ast.AsyncFunctionDef):
                methods.append(self._extract_function_node(item, is_async=True))

        python_class = PythonClass(
            name=node.name,
            decorators=decorators,
            base_classes=base_classes,
            methods=methods,
            docstring=docstring,
        )

        self.classes.append(python_class)

    def _extract_function(self, node: ast.FunctionDef) -> None:
        """Extract function information"""
        func = self._extract_function_node(node)
        # Only add top-level functions (not methods)
        if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(self.tree) if hasattr(parent, "body") and node in parent.body):
            self.functions.append(func)

    def _extract_async_function(self, node: ast.AsyncFunctionDef) -> None:
        """Extract async function information"""
        func = self._extract_function_node(node, is_async=True)
        # Only add top-level functions (not methods)
        if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(self.tree) if hasattr(parent, "body") and node in parent.body):
            self.functions.append(func)

    def _extract_function_node(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool = False) -> PythonFunction:
        """Extract function node details"""
        decorators = [d.id if isinstance(d, ast.Name) else ast.unparse(d) for d in node.decorator_list]

        # Track decorators
        for dec in decorators:
            if dec not in self.decorators:
                self.decorators.append(dec)

        parameters = []
        if node.args:
            # Regular arguments
            for arg in node.args.args:
                parameters.append(arg.arg)
            # *args
            if node.args.vararg:
                parameters.append(f"*{node.args.vararg.arg}")
            # **kwargs
            if node.args.kwarg:
                parameters.append(f"**{node.args.kwarg.arg}")

        docstring = ast.get_docstring(node)

        return PythonFunction(
            name=node.name,
            decorators=decorators,
            parameters=parameters,
            docstring=docstring,
            is_async=is_async,
        )

    def _extract_import(self, node: ast.Import | ast.ImportFrom) -> None:
        """Extract import information"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                self.imports.append(f"{module}.{alias.name}" if module else alias.name)

    def _extract_endpoints(self) -> List[Dict[str, Any]]:
        """Extract REST endpoints from decorators"""
        endpoints = []

        # Common route decorators
        route_decorators = {"route", "get", "post", "put", "delete", "patch", "app", "router"}

        # Check all decorators in classes and functions
        for cls in self.classes:
            for method in cls.methods:
                for dec in method.decorators:
                    # Check if decorator looks like a route
                    if any(route in dec.lower() for route in route_decorators):
                        endpoints.append(
                            {
                                "class": cls.name,
                                "method": method.name,
                                "decorator": dec,
                                "confidence": 0.85,
                            }
                        )

        for func in self.functions:
            for dec in func.decorators:
                if any(route in dec.lower() for route in route_decorators):
                    endpoints.append(
                        {
                            "function": func.name,
                            "decorator": dec,
                            "confidence": 0.8,
                        }
                    )

        return endpoints

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score"""
        if not self.tree:
            return 0.0

        total_items = len(self.classes) + len(self.functions)
        if total_items == 0:
            return 0.5

        # Higher confidence for files with AST parsed successfully
        return 0.95
