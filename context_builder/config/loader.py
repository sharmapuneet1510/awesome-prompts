"""ConfigLoader: YAML configuration loader for Context Builder.

Loads configuration from YAML files in the context root directory.
Provides sensible defaults for missing files.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None


class ConfigLoader:
    """Load configuration files from YAML.

    Loads 6 configuration files from the context root:
    1. workspace-definition.d.yaml
    2. project-definition.d.yaml
    3. tech-aliases.yaml
    4. scan-config.yaml
    5. maturity-config.yaml
    6. test-quality-config.yaml

    Attributes:
        context_root: Path to the .context directory
        logger: Logger instance for configuration loading
    """

    # Default values for scan configuration
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

    # Default values for maturity configuration (8 dimensions)
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

    # Default values for test quality configuration
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

    def __init__(self, context_root: Path):
        """Initialize ConfigLoader.

        Args:
            context_root: Path to the .context directory
        """
        self.context_root = Path(context_root) if not isinstance(context_root, Path) else context_root
        self.logger = logging.getLogger(__name__)

        if yaml is None:
            self.logger.warning("PyYAML not installed. Config loading will use defaults only.")

    def _load_yaml_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load a YAML file and return its contents.

        Args:
            file_path: Path to the YAML file

        Returns:
            Dictionary with file contents, or None if file not found or error loading

        Raises:
            None - catches exceptions and logs warnings
        """
        if not file_path.exists():
            self.logger.debug(f"Config file not found: {file_path}")
            return None

        if yaml is None:
            self.logger.warning(f"Cannot load {file_path}: PyYAML not installed")
            return None

        try:
            with open(file_path, "r") as f:
                content = yaml.safe_load(f)
                if content is None:
                    return {}
                return content
        except yaml.YAMLError as e:
            self.logger.warning(f"Error parsing YAML {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Error loading {file_path}: {e}")
            return None

    def load_workspace_config(self) -> Dict[str, Any]:
        """Load workspace configuration from workspace-definition.d.yaml.

        Returns:
            Dictionary with workspace configuration (empty dict if file not found)
        """
        config_file = self.context_root / "workspace-definition.d.yaml"
        data = self._load_yaml_file(config_file)

        if data is None:
            self.logger.info("workspace-definition.d.yaml not found, using empty defaults")
            return {}

        # Extract workspace section or return as-is if flat structure
        if "workspace" in data:
            return data["workspace"]
        return data

    def load_project_config(self) -> Dict[str, Any]:
        """Load project configuration from project-definition.d.yaml.

        Returns:
            Dictionary with project configuration (empty dict if file not found)
        """
        config_file = self.context_root / "project-definition.d.yaml"
        data = self._load_yaml_file(config_file)

        if data is None:
            self.logger.info("project-definition.d.yaml not found, using empty defaults")
            return {}

        # Extract projects section or return as-is if flat structure
        if "projects" in data:
            return {"projects": data["projects"]}
        return data

    def load_tech_aliases_config(self) -> Dict[str, Any]:
        """Load tech aliases configuration from tech-aliases.yaml.

        Returns:
            Dictionary with tech aliases configuration (empty dict if file not found)
        """
        config_file = self.context_root / "tech-aliases.yaml"
        data = self._load_yaml_file(config_file)

        if data is None:
            self.logger.info("tech-aliases.yaml not found, using empty defaults")
            return {}

        return data

    def load_scan_config(self) -> Dict[str, Any]:
        """Load scan configuration from scan-config.yaml.

        Provides comprehensive defaults if file not found.

        Returns:
            Dictionary with scan configuration including include/exclude patterns
        """
        config_file = self.context_root / "scan-config.yaml"
        data = self._load_yaml_file(config_file)

        if data is None:
            self.logger.info("scan-config.yaml not found, using comprehensive defaults")
            # Return defaults in flat structure
            return {
                "include": self.DEFAULT_SCAN_INCLUDES,
                "exclude": self.DEFAULT_SCAN_EXCLUDES,
                "analysis_depth": self.DEFAULT_ANALYSIS_DEPTH,
                "incremental": True,
            }

        # Handle nested structure (scan: {...})
        if "scan" in data:
            scan_config = data["scan"]
            # Fill in missing defaults
            if "include" not in scan_config:
                scan_config["include"] = self.DEFAULT_SCAN_INCLUDES
            if "exclude" not in scan_config:
                scan_config["exclude"] = self.DEFAULT_SCAN_EXCLUDES
            if "analysis_depth" not in scan_config:
                scan_config["analysis_depth"] = self.DEFAULT_ANALYSIS_DEPTH
            if "incremental" not in scan_config:
                scan_config["incremental"] = True
            return scan_config

        # Handle flat structure
        return {
            "include": data.get("include", self.DEFAULT_SCAN_INCLUDES),
            "exclude": data.get("exclude", self.DEFAULT_SCAN_EXCLUDES),
            "analysis_depth": data.get("analysis_depth", self.DEFAULT_ANALYSIS_DEPTH),
            "incremental": data.get("incremental", True),
        }

    def load_maturity_config(self) -> Dict[str, Any]:
        """Load maturity configuration from maturity-config.yaml.

        Provides defaults with 8 dimensions if file not found.

        Returns:
            Dictionary with maturity configuration
        """
        config_file = self.context_root / "maturity-config.yaml"
        data = self._load_yaml_file(config_file)

        if data is None:
            self.logger.info("maturity-config.yaml not found, using defaults with 8 dimensions")
            # Return defaults in flat structure
            return {
                "target_score": 80,
                "max_iterations": 5,
                "dimensions": self.DEFAULT_MATURITY_DIMENSIONS,
            }

        # Handle nested structure (maturity: {...})
        if "maturity" in data:
            maturity_config = data["maturity"]
            # Fill in missing defaults
            if "target_score" not in maturity_config:
                maturity_config["target_score"] = 80
            if "max_iterations" not in maturity_config:
                maturity_config["max_iterations"] = 5
            if "dimensions" not in maturity_config:
                maturity_config["dimensions"] = self.DEFAULT_MATURITY_DIMENSIONS
            return maturity_config

        # Handle flat structure
        return {
            "target_score": data.get("target_score", 80),
            "max_iterations": data.get("max_iterations", 5),
            "dimensions": data.get("dimensions", self.DEFAULT_MATURITY_DIMENSIONS),
        }

    def load_test_quality_config(self) -> Dict[str, Any]:
        """Load test quality configuration from test-quality-config.yaml.

        Provides defaults with language-specific coverage sources if file not found.

        Returns:
            Dictionary with test quality configuration
        """
        config_file = self.context_root / "test-quality-config.yaml"
        data = self._load_yaml_file(config_file)

        if data is None:
            self.logger.info("test-quality-config.yaml not found, using defaults with language-specific sources")
            # Return defaults in flat structure
            return {
                "target_score": 80,
                "coverage_sources": self.DEFAULT_TEST_COVERAGE_SOURCES,
                "scoring": self.DEFAULT_TEST_SCORING,
            }

        # Handle nested structure (test_quality: {...})
        if "test_quality" in data:
            tq_config = data["test_quality"]
            # Fill in missing defaults
            if "target_score" not in tq_config:
                tq_config["target_score"] = 80
            if "coverage_sources" not in tq_config:
                tq_config["coverage_sources"] = self.DEFAULT_TEST_COVERAGE_SOURCES
            if "scoring" not in tq_config:
                tq_config["scoring"] = self.DEFAULT_TEST_SCORING
            return tq_config

        # Handle flat structure
        return {
            "target_score": data.get("target_score", 80),
            "coverage_sources": data.get("coverage_sources", self.DEFAULT_TEST_COVERAGE_SOURCES),
            "scoring": data.get("scoring", self.DEFAULT_TEST_SCORING),
        }

    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load all 6 configuration files.

        Returns:
            Dictionary with keys: workspace, project, tech_aliases, scan, maturity, test_quality
            Each key maps to its configuration dictionary
        """
        return {
            "workspace": self.load_workspace_config(),
            "project": self.load_project_config(),
            "tech_aliases": self.load_tech_aliases_config(),
            "scan": self.load_scan_config(),
            "maturity": self.load_maturity_config(),
            "test_quality": self.load_test_quality_config(),
        }
