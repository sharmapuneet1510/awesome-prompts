"""Tests for orchestrator configuration module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import tempfile

from tools.orchestrator.config import OrchestratorConfig
from tools.orchestrator import load_orchestrator_config


class TestOrchestratorConfig:
    """Test OrchestratorConfig dataclass and factory methods."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = OrchestratorConfig()

        assert config.auto_generate_context is True
        assert config.context_depth == "comprehensive"
        assert config.separate_context_commit is True
        assert config.skip_on_context_failure is False

    def test_custom_values(self):
        """Test creating config with custom values."""
        config = OrchestratorConfig(
            auto_generate_context=False,
            context_depth="quick",
            separate_context_commit=False,
            skip_on_context_failure=True
        )

        assert config.auto_generate_context is False
        assert config.context_depth == "quick"
        assert config.separate_context_commit is False
        assert config.skip_on_context_failure is True

    def test_from_dict_with_none(self):
        """Test from_dict with None returns default config."""
        config = OrchestratorConfig.from_dict(None)

        assert config.auto_generate_context is True
        assert config.context_depth == "comprehensive"

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict returns default config."""
        config = OrchestratorConfig.from_dict({})

        assert config.auto_generate_context is True
        assert config.context_depth == "comprehensive"

    def test_from_dict_with_partial_config(self):
        """Test from_dict with partial configuration."""
        config_dict = {
            "build": {
                "auto_generate_context": False,
                "context_depth": "quick"
            }
        }
        config = OrchestratorConfig.from_dict(config_dict)

        assert config.auto_generate_context is False
        assert config.context_depth == "quick"
        assert config.separate_context_commit is True  # Default
        assert config.skip_on_context_failure is False  # Default

    def test_from_dict_with_full_config(self):
        """Test from_dict with complete configuration."""
        config_dict = {
            "build": {
                "auto_generate_context": False,
                "context_depth": "standard",
                "separate_context_commit": False,
                "skip_on_context_failure": True
            }
        }
        config = OrchestratorConfig.from_dict(config_dict)

        assert config.auto_generate_context is False
        assert config.context_depth == "standard"
        assert config.separate_context_commit is False
        assert config.skip_on_context_failure is True

    def test_default_factory_method(self):
        """Test default() factory method returns auto-chaining enabled."""
        config = OrchestratorConfig.default()

        assert config.auto_generate_context is True
        assert config.context_depth == "comprehensive"
        assert config.separate_context_commit is True
        assert config.skip_on_context_failure is False

    def test_disabled_factory_method(self):
        """Test disabled() factory method returns auto-chaining disabled."""
        config = OrchestratorConfig.disabled()

        assert config.auto_generate_context is False
        assert config.context_depth == "comprehensive"  # Other defaults remain
        assert config.separate_context_commit is True
        assert config.skip_on_context_failure is False

    def test_to_dict(self):
        """Test to_dict converts config back to dictionary format."""
        config = OrchestratorConfig(
            auto_generate_context=False,
            context_depth="quick",
            separate_context_commit=False,
            skip_on_context_failure=True
        )

        config_dict = config.to_dict()

        assert "build" in config_dict
        assert config_dict["build"]["auto_generate_context"] is False
        assert config_dict["build"]["context_depth"] == "quick"
        assert config_dict["build"]["separate_context_commit"] is False
        assert config_dict["build"]["skip_on_context_failure"] is True

    def test_round_trip_from_dict_to_dict(self):
        """Test round-trip conversion: dict -> config -> dict."""
        original_dict = {
            "build": {
                "auto_generate_context": False,
                "context_depth": "standard",
                "separate_context_commit": False,
                "skip_on_context_failure": True
            }
        }

        config = OrchestratorConfig.from_dict(original_dict)
        result_dict = config.to_dict()

        assert result_dict == original_dict

    def test_context_depth_values(self):
        """Test that context_depth can be set to valid values."""
        for depth in ["quick", "standard", "comprehensive"]:
            config = OrchestratorConfig(context_depth=depth)
            assert config.context_depth == depth


class TestLoadOrchestratorConfig:
    """Test load_orchestrator_config function."""

    def test_load_config_file_not_found(self):
        """Test loading config when file does not exist."""
        with patch("pathlib.Path.exists", return_value=False):
            config = load_orchestrator_config()

            assert config.auto_generate_context is True
            assert config.context_depth == "comprehensive"

    def test_load_config_from_file_full_config(self):
        """Test loading config from file with full configuration."""
        config_data = {
            "orchestrator": {
                "build": {
                    "auto_generate_context": False,
                    "context_depth": "quick",
                    "separate_context_commit": False,
                    "skip_on_context_failure": True
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".claude" / "settings.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(config_data, f)

            # Patch the load function to use our temp file
            with patch("tools.orchestrator.Path", return_value=config_file):
                config = load_orchestrator_config()

                assert config.auto_generate_context is False
                assert config.context_depth == "quick"
                assert config.separate_context_commit is False
                assert config.skip_on_context_failure is True

    def test_load_config_invalid_json_returns_defaults(self):
        """Test loading config with invalid JSON returns defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".claude" / "settings.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                f.write("{ invalid json }")

            with patch("tools.orchestrator.Path", return_value=config_file):
                config = load_orchestrator_config()

                # Should return defaults on error
                assert config.auto_generate_context is True
                assert config.context_depth == "comprehensive"

    def test_load_config_missing_orchestrator_section(self):
        """Test loading config with missing orchestrator section."""
        config_data = {
            "model": "haiku",
            "hooks": {}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".claude" / "settings.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(config_data, f)

            with patch("tools.orchestrator.Path", return_value=config_file):
                config = load_orchestrator_config()

                # Should return defaults when orchestrator section missing
                assert config.auto_generate_context is True
                assert config.context_depth == "comprehensive"

    def test_load_config_empty_orchestrator_section(self):
        """Test loading config with empty orchestrator section."""
        config_data = {
            "orchestrator": {}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".claude" / "settings.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(config_data, f)

            with patch("tools.orchestrator.Path", return_value=config_file):
                config = load_orchestrator_config()

                # Should return defaults when build section missing
                assert config.auto_generate_context is True
                assert config.context_depth == "comprehensive"
