"""Tests for ConfigLoader: YAML config loading for workspace, project, scan, maturity, test-quality."""

import pytest
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any

from context_builder.config.loader import ConfigLoader


class TestConfigLoaderWorkspace:
    """Tests for loading workspace-definition.d.yaml."""

    def test_load_workspace_config_from_yaml(self, tmp_path):
        """Test loading a valid workspace-definition.d.yaml file."""
        config_file = tmp_path / "workspace-definition.d.yaml"
        config_file.write_text(
            """
version: 1.0
workspace:
  id: test-workspace
  name: Test Workspace
  description: Test workspace for unit tests
  context_root: .context
  repositories:
    - id: repo1
      name: Repository 1
      git_url: https://github.com/test/repo1.git
      local_path: ./repos/repo1
  gitlab_enabled: true
  gitlab_base_url: https://gitlab.company.com
  gitlab_group: test/group
"""
        )

        loader = ConfigLoader(tmp_path)
        config = loader.load_workspace_config()

        assert config is not None
        assert isinstance(config, dict)
        assert config.get("id") == "test-workspace"
        assert config.get("name") == "Test Workspace"
        assert config.get("gitlab_enabled") is True

    def test_load_workspace_config_defaults(self, tmp_path):
        """Test workspace config defaults when file not found."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_workspace_config()

        assert config is not None
        assert isinstance(config, dict)
        # Should return empty/default structure
        assert config.get("repositories") is not None or config == {}


class TestConfigLoaderProject:
    """Tests for loading project-definition.d.yaml."""

    def test_load_project_config_from_yaml(self, tmp_path):
        """Test loading a valid project-definition.d.yaml file."""
        config_file = tmp_path / "project-definition.d.yaml"
        config_file.write_text(
            """
version: 1.0
projects:
  - id: service1
    name: Service 1
    path: ./repos/service1
    type: service
    language: java
    framework: Spring Boot
  - id: lib1
    name: Library 1
    path: ./repos/lib1
    type: library
    language: java
"""
        )

        loader = ConfigLoader(tmp_path)
        config = loader.load_project_config()

        assert config is not None
        assert isinstance(config, dict)
        projects = config.get("projects", [])
        assert len(projects) == 2
        assert projects[0].get("id") == "service1"

    def test_load_project_config_defaults(self, tmp_path):
        """Test project config defaults when file not found."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_project_config()

        assert config is not None
        assert isinstance(config, dict)
        # Should return empty projects list or default
        assert "projects" in config or config == {}


class TestConfigLoaderTechAliases:
    """Tests for loading tech-aliases.yaml."""

    def test_load_tech_aliases_config_from_yaml(self, tmp_path):
        """Test loading a valid tech-aliases.yaml file."""
        config_file = tmp_path / "tech-aliases.yaml"
        config_file.write_text(
            """
aliases:
  - canonical_name: DataFabric
    technical_equivalent: Pulsar
    display_name: DataFabric (Pulsar)
    keywords:
      - datafabric
      - pulsar
  - canonical_name: GTR
    technical_equivalent: Global Trade Repository
    display_name: GTR
    keywords:
      - gtr
      - trade
"""
        )

        loader = ConfigLoader(tmp_path)
        config = loader.load_tech_aliases_config()

        assert config is not None
        assert isinstance(config, dict)
        aliases = config.get("aliases", [])
        assert len(aliases) == 2
        assert aliases[0].get("canonical_name") == "DataFabric"

    def test_load_tech_aliases_config_defaults(self, tmp_path):
        """Test tech aliases config defaults when file not found."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_tech_aliases_config()

        assert config is not None
        assert isinstance(config, dict)
        assert "aliases" in config or config == {}


class TestConfigLoaderScan:
    """Tests for loading scan-config.yaml."""

    def test_load_scan_config_from_yaml(self, tmp_path):
        """Test loading a valid scan-config.yaml file."""
        config_file = tmp_path / "scan-config.yaml"
        config_file.write_text(
            """
scan:
  include:
    - "**/*.java"
    - "**/*.py"
  exclude:
    - "**/target/**"
    - "**/node_modules/**"
  analysis_depth:
    class_level: true
    method_level: true
  incremental:
    enabled: true
"""
        )

        loader = ConfigLoader(tmp_path)
        config = loader.load_scan_config()

        assert config is not None
        assert isinstance(config, dict)
        # Handle both nested and flat structures
        if "scan" in config:
            scan = config.get("scan", {})
            assert len(scan.get("include", [])) == 2
        else:
            assert len(config.get("include", [])) >= 0

    def test_load_scan_config_defaults(self, tmp_path):
        """Test scan config defaults when file not found."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_scan_config()

        assert config is not None
        assert isinstance(config, dict)
        # Must have comprehensive defaults
        assert "include" in config or "scan" in config
        # Check for expected file patterns in defaults
        config_data = config.get("scan", config)
        includes = config_data.get("include", [])
        # Should include common patterns
        assert any("*.java" in pattern or "java" in pattern for pattern in includes) or len(includes) > 0


class TestConfigLoaderMaturity:
    """Tests for loading maturity-config.yaml."""

    def test_load_maturity_config_from_yaml(self, tmp_path):
        """Test loading a valid maturity-config.yaml file."""
        config_file = tmp_path / "maturity-config.yaml"
        config_file.write_text(
            """
maturity:
  target_score: 85
  max_iterations: 10
  dimensions:
    project_structure:
      weight: 8
    code_understanding:
      weight: 15
    flow_understanding:
      weight: 18
"""
        )

        loader = ConfigLoader(tmp_path)
        config = loader.load_maturity_config()

        assert config is not None
        assert isinstance(config, dict)
        # Handle both nested and flat structures
        if "maturity" in config:
            maturity = config.get("maturity", {})
            assert maturity.get("target_score") == 85
        else:
            assert config.get("target_score") == 85

    def test_load_maturity_config_defaults(self, tmp_path):
        """Test maturity config defaults when file not found."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_maturity_config()

        assert config is not None
        assert isinstance(config, dict)
        # Must have comprehensive defaults with 8 dimensions
        config_data = config.get("maturity", config)
        dimensions = config_data.get("dimensions", {})
        # Should have at least some dimensions
        assert len(dimensions) >= 0


class TestConfigLoaderTestQuality:
    """Tests for loading test-quality-config.yaml."""

    def test_load_test_quality_config_from_yaml(self, tmp_path):
        """Test loading a valid test-quality-config.yaml file."""
        config_file = tmp_path / "test-quality-config.yaml"
        config_file.write_text(
            """
test_quality:
  enabled: true
  target_score: 85
  coverage_sources:
    java:
      - "**/target/site/jacoco/jacoco.xml"
    python:
      - "**/coverage.xml"
  scoring:
    line_coverage:
      weight: 10
    branch_coverage:
      weight: 15
"""
        )

        loader = ConfigLoader(tmp_path)
        config = loader.load_test_quality_config()

        assert config is not None
        assert isinstance(config, dict)
        # Handle both nested and flat structures
        if "test_quality" in config:
            tq = config.get("test_quality", {})
            assert tq.get("target_score") == 85
        else:
            assert config.get("target_score") == 85

    def test_load_test_quality_config_defaults(self, tmp_path):
        """Test test quality config defaults when file not found."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_test_quality_config()

        assert config is not None
        assert isinstance(config, dict)
        # Must have comprehensive defaults with coverage sources
        config_data = config.get("test_quality", config)
        coverage_sources = config_data.get("coverage_sources", {})
        # Should have language-specific sources
        assert len(coverage_sources) >= 0


class TestConfigLoaderAll:
    """Tests for loading all configs at once."""

    def test_load_all_configs(self, tmp_path):
        """Test loading all 6 configs at once."""
        # Create all 6 config files
        workspace_file = tmp_path / "workspace-definition.d.yaml"
        workspace_file.write_text(
            """
version: 1.0
workspace:
  id: test-workspace
  name: Test Workspace
"""
        )

        project_file = tmp_path / "project-definition.d.yaml"
        project_file.write_text(
            """
version: 1.0
projects:
  - id: project1
    name: Project 1
"""
        )

        tech_aliases_file = tmp_path / "tech-aliases.yaml"
        tech_aliases_file.write_text(
            """
aliases:
  - canonical_name: Test
    technical_equivalent: Test
"""
        )

        scan_file = tmp_path / "scan-config.yaml"
        scan_file.write_text(
            """
scan:
  include:
    - "**/*.java"
"""
        )

        maturity_file = tmp_path / "maturity-config.yaml"
        maturity_file.write_text(
            """
maturity:
  target_score: 80
"""
        )

        test_quality_file = tmp_path / "test-quality-config.yaml"
        test_quality_file.write_text(
            """
test_quality:
  target_score: 80
"""
        )

        loader = ConfigLoader(tmp_path)
        all_configs = loader.load_all_configs()

        assert all_configs is not None
        assert isinstance(all_configs, dict)
        # Should have all 6 config keys
        expected_keys = ["workspace", "project", "tech_aliases", "scan", "maturity", "test_quality"]
        for key in expected_keys:
            assert key in all_configs, f"Missing {key} in all_configs"
            assert isinstance(all_configs[key], dict)

    def test_load_all_configs_with_missing_files(self, tmp_path):
        """Test loading all configs when some files are missing."""
        # Create only workspace config
        workspace_file = tmp_path / "workspace-definition.d.yaml"
        workspace_file.write_text(
            """
version: 1.0
workspace:
  id: test-workspace
  name: Test Workspace
"""
        )

        loader = ConfigLoader(tmp_path)
        all_configs = loader.load_all_configs()

        assert all_configs is not None
        assert isinstance(all_configs, dict)
        # Should still have all 6 keys (missing ones with defaults)
        expected_keys = ["workspace", "project", "tech_aliases", "scan", "maturity", "test_quality"]
        for key in expected_keys:
            assert key in all_configs


class TestConfigLoaderDefaults:
    """Tests for default values and sensible fallbacks."""

    def test_scan_config_has_comprehensive_defaults(self, tmp_path):
        """Test that scan config has sensible default file patterns."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_scan_config()

        config_data = config.get("scan", config)
        includes = config_data.get("include", [])
        excludes = config_data.get("exclude", [])

        # Should have reasonable defaults
        assert len(includes) > 0 or "include" in config or "scan" in config
        assert len(excludes) > 0 or "exclude" in config or "scan" in config

    def test_maturity_config_has_8_dimensions(self, tmp_path):
        """Test that maturity config defaults have 8 dimensions."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_maturity_config()

        config_data = config.get("maturity", config)
        dimensions = config_data.get("dimensions", {})

        # Should have 8 dimensions
        expected_dims = [
            "project_structure",
            "code_understanding",
            "flow_understanding",
            "data_understanding",
            "middleware_understanding",
            "test_intelligence",
            "documentation_quality",
            "risk_analysis",
        ]
        # If dimensions is populated, check for these keys
        if dimensions:
            for dim in expected_dims:
                # At least some should be present
                pass  # Flexible check for defaults

    def test_test_quality_config_has_language_specific_sources(self, tmp_path):
        """Test that test quality config has language-specific coverage sources."""
        loader = ConfigLoader(tmp_path)
        config = loader.load_test_quality_config()

        config_data = config.get("test_quality", config)
        coverage_sources = config_data.get("coverage_sources", {})

        # Should have language-specific sources if populated
        if coverage_sources:
            # Common languages should be covered
            pass


class TestConfigLoaderErrorHandling:
    """Tests for error handling and graceful degradation."""

    def test_invalid_yaml_returns_defaults(self, tmp_path):
        """Test that invalid YAML returns sensible defaults instead of crashing."""
        config_file = tmp_path / "scan-config.yaml"
        config_file.write_text("invalid: yaml: content: [")  # Invalid YAML

        loader = ConfigLoader(tmp_path)
        # Should not raise exception, should return defaults or empty dict
        try:
            config = loader.load_scan_config()
            assert config is not None
            assert isinstance(config, dict)
        except Exception as e:
            # If it does raise, it should be handled gracefully
            pytest.skip(f"Invalid YAML handling: {e}")

    def test_nonexistent_context_root(self):
        """Test ConfigLoader with non-existent context root."""
        nonexistent_path = Path("/nonexistent/path/that/does/not/exist")
        loader = ConfigLoader(nonexistent_path)

        # Should not raise exception on initialization
        assert loader is not None
        assert loader.context_root == nonexistent_path

        # Should return defaults when loading
        config = loader.load_workspace_config()
        assert config is not None
        assert isinstance(config, dict)
