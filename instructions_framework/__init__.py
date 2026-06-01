"""Centralized Instructions Framework"""

__version__ = "1.0.0"
__author__ = "Awesome Prompts"

from .schema import (
    InstructionCategory,
    InstructionPrecedence,
    InstructionScope,
    InstructionMetadata,
    Instruction,
    InstructionSection,
)
from .parser import parse_instruction_file
from .loader import InstructionLoader
from .pipeline import InstructionPipeline
from .middleware import InstructionMiddleware
from .exporters import BaseExporter, IntermediateExporter
from .plugins import PluginRegistry, get_global_registry
from .analyzers import (
    JavaAnalyzer,
    PythonAnalyzer,
    TypeScriptAnalyzer,
    ConfigAnalyzer,
    DatabaseAnalyzer,
    MiddlewareAnalyzer,
)

__all__ = [
    "InstructionCategory",
    "InstructionPrecedence",
    "InstructionScope",
    "InstructionMetadata",
    "InstructionSection",
    "Instruction",
    "parse_instruction_file",
    "InstructionLoader",
    "InstructionPipeline",
    "InstructionMiddleware",
    "BaseExporter",
    "IntermediateExporter",
    "PluginRegistry",
    "get_global_registry",
    "JavaAnalyzer",
    "PythonAnalyzer",
    "TypeScriptAnalyzer",
    "ConfigAnalyzer",
    "DatabaseAnalyzer",
    "MiddlewareAnalyzer",
]
