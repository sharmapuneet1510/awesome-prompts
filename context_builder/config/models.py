"""Config data models for Context Builder.

These models define the structure of configuration files loaded from YAML.
They are distinct from context_builder.models which define graph nodes, edges, and execution context.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

# Default file scan patterns
DEFAULT_SCAN_INCLUDES = [
    "**/*.java",
    "**/*.py",
    "**/*.ts",
    "**/*.tsx",
    "**/*.js",
    "**/*.jsx",
    "**/*.yaml",
    "**/*.yml",
    "**/*.xml",
    "**/*.properties",
    "**/*.sql",
    "**/pom.xml",
    "**/build.gradle",
    "**/package.json",
]

DEFAULT_SCAN_EXCLUDES = [
    "**/target/**",
    "**/build/**",
    "**/node_modules/**",
    "**/.git/**",
    "**/logs/**",
    "**/dist/**",
    "**/.idea/**",
    "**/.vscode/**",
]

DEFAULT_ANALYSIS_DEPTH = {
    "class_level": True,
    "method_level": True,
    "flow_level": True,
    "config_level": True,
    "db_analysis": True,
    "middleware_analysis": True,
    "exception_flow": True,
    "test_quality": True,
    "technical_debt": True,
}

DEFAULT_MATURITY_DIMENSIONS = {
    "project_structure": {"weight": 8},
    "code_understanding": {"weight": 15},
    "flow_understanding": {"weight": 18},
    "data_understanding": {"weight": 12},
    "middleware_understanding": {"weight": 12},
    "test_intelligence": {"weight": 15},
    "documentation_quality": {"weight": 10},
    "risk_analysis": {"weight": 10},
}

DEFAULT_TEST_COVERAGE_SOURCES = {
    "java": [
        "**/target/site/jacoco/jacoco.xml",
        "**/target/surefire-reports/*.xml",
    ],
    "javascript": [
        "**/coverage/lcov.info",
        "**/jest-report.json",
    ],
    "python": [
        "**/coverage.xml",
        "**/pytest-report.xml",
    ],
}

DEFAULT_TEST_SCORING = {
    "line_coverage": 10,
    "branch_coverage": 15,
    "critical_flow_coverage": 25,
    "assertion_quality": 15,
    "negative_test_coverage": 10,
    "integration_test_coverage": 10,
    "boundary_case_coverage": 10,
    "test_maintainability": 5,
}


@dataclass
class WorkspaceConfigModel:
    """Workspace configuration model.

    Maps to workspace-definition.d.yaml structure.
    """

    id: str
    name: str
    description: str = ""
    context_root: str = ".context"
    repositories: List[Dict[str, Any]] = field(default_factory=list)
    gitlab_enabled: bool = False
    gitlab_base_url: Optional[str] = None
    gitlab_group: Optional[str] = None


@dataclass
class ProjectConfigModel:
    """Project configuration model.

    Maps to project-definition.d.yaml structure.
    """

    projects: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TechAliasesConfigModel:
    """Technology aliases configuration model.

    Maps to tech-aliases.yaml structure.
    """

    aliases: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScanConfigModel:
    """Scan configuration model.

    Maps to scan-config.yaml structure.
    Defines file patterns and analysis depth.
    """

    include_patterns: List[str] = field(default_factory=lambda: DEFAULT_SCAN_INCLUDES.copy())
    exclude_patterns: List[str] = field(default_factory=lambda: DEFAULT_SCAN_EXCLUDES.copy())
    analysis_depth: Dict[str, bool] = field(default_factory=lambda: DEFAULT_ANALYSIS_DEPTH.copy())
    incremental: bool = True


@dataclass
class MaturityConfigModel:
    """Maturity configuration model.

    Maps to maturity-config.yaml structure.
    Defines 8 dimensions with weights for maturity scoring.
    """

    target_score: int = 80
    max_iterations: int = 5
    dimensions: Dict[str, Dict[str, Any]] = field(default_factory=lambda: DEFAULT_MATURITY_DIMENSIONS.copy())


@dataclass
class TestQualityConfigModel:
    """Test quality configuration model.

    Maps to test-quality-config.yaml structure.
    Defines coverage sources and scoring weights per language.
    """

    target_score: int = 80
    coverage_sources: Dict[str, List[str]] = field(default_factory=lambda: DEFAULT_TEST_COVERAGE_SOURCES.copy())
    scoring: Dict[str, int] = field(default_factory=lambda: DEFAULT_TEST_SCORING.copy())


__all__ = [
    "DEFAULT_SCAN_INCLUDES",
    "DEFAULT_SCAN_EXCLUDES",
    "DEFAULT_ANALYSIS_DEPTH",
    "DEFAULT_MATURITY_DIMENSIONS",
    "DEFAULT_TEST_COVERAGE_SOURCES",
    "DEFAULT_TEST_SCORING",
    "WorkspaceConfigModel",
    "ProjectConfigModel",
    "TechAliasesConfigModel",
    "ScanConfigModel",
    "MaturityConfigModel",
    "TestQualityConfigModel",
]
