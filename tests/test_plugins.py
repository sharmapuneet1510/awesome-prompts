"""Tests for plugin registry system"""

import pytest
import tempfile
from pathlib import Path
from typing import List
from instructions_framework import InstructionMiddleware
from instructions_framework.exporters import BaseExporter
from instructions_framework.plugins import PluginRegistry, get_global_registry
from instructions_framework.schema import Instruction


# Test middleware and exporter classes
class TestMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        return instructions


class AnotherTestMiddleware(InstructionMiddleware):
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        return instructions


class TestExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        return "test output"


class AnotherTestExporter(BaseExporter):
    def export(self, instructions: List[Instruction], **kwargs) -> str:
        return "another output"


class TestPluginRegistry:
    """Test PluginRegistry class"""

    def test_register_middleware(self):
        """Test registering middleware"""
        registry = PluginRegistry()
        registry.register_middleware("test", TestMiddleware)

        assert registry.get_middleware("test") is TestMiddleware

    def test_register_exporter(self):
        """Test registering exporter"""
        registry = PluginRegistry()
        registry.register_exporter("test", TestExporter)

        assert registry.get_exporter("test") is TestExporter

    def test_register_middleware_invalid_type(self):
        """Test registering non-middleware class raises error"""
        registry = PluginRegistry()

        with pytest.raises(TypeError):
            registry.register_middleware("invalid", str)

    def test_register_exporter_invalid_type(self):
        """Test registering non-exporter class raises error"""
        registry = PluginRegistry()

        with pytest.raises(TypeError):
            registry.register_exporter("invalid", str)

    def test_register_duplicate_middleware(self):
        """Test registering duplicate middleware raises error"""
        registry = PluginRegistry()
        registry.register_middleware("test", TestMiddleware)

        with pytest.raises(ValueError):
            registry.register_middleware("test", AnotherTestMiddleware)

    def test_register_duplicate_exporter(self):
        """Test registering duplicate exporter raises error"""
        registry = PluginRegistry()
        registry.register_exporter("test", TestExporter)

        with pytest.raises(ValueError):
            registry.register_exporter("test", AnotherTestExporter)

    def test_get_nonexistent_middleware(self):
        """Test getting nonexistent middleware returns None"""
        registry = PluginRegistry()

        assert registry.get_middleware("nonexistent") is None

    def test_get_nonexistent_exporter(self):
        """Test getting nonexistent exporter returns None"""
        registry = PluginRegistry()

        assert registry.get_exporter("nonexistent") is None

    def test_list_middleware(self):
        """Test listing all middleware"""
        registry = PluginRegistry()
        registry.register_middleware("test1", TestMiddleware)
        registry.register_middleware("test2", AnotherTestMiddleware)

        middleware = registry.list_middleware()
        assert len(middleware) == 2
        assert "test1" in middleware
        assert "test2" in middleware

    def test_list_exporters(self):
        """Test listing all exporters"""
        registry = PluginRegistry()
        registry.register_exporter("test1", TestExporter)
        registry.register_exporter("test2", AnotherTestExporter)

        exporters = registry.list_exporters()
        assert len(exporters) == 2
        assert "test1" in exporters
        assert "test2" in exporters

    def test_unregister_middleware(self):
        """Test unregistering middleware"""
        registry = PluginRegistry()
        registry.register_middleware("test", TestMiddleware)

        # Verify it exists
        assert registry.get_middleware("test") is TestMiddleware

        # Unregister
        result = registry.unregister_middleware("test")
        assert result is True

        # Verify it's gone
        assert registry.get_middleware("test") is None

    def test_unregister_nonexistent_middleware(self):
        """Test unregistering nonexistent middleware returns False"""
        registry = PluginRegistry()

        result = registry.unregister_middleware("nonexistent")
        assert result is False

    def test_unregister_exporter(self):
        """Test unregistering exporter"""
        registry = PluginRegistry()
        registry.register_exporter("test", TestExporter)

        # Verify it exists
        assert registry.get_exporter("test") is TestExporter

        # Unregister
        result = registry.unregister_exporter("test")
        assert result is True

        # Verify it's gone
        assert registry.get_exporter("test") is None

    def test_unregister_nonexistent_exporter(self):
        """Test unregistering nonexistent exporter returns False"""
        registry = PluginRegistry()

        result = registry.unregister_exporter("nonexistent")
        assert result is False

    def test_clear_middleware(self):
        """Test clearing all middleware"""
        registry = PluginRegistry()
        registry.register_middleware("test1", TestMiddleware)
        registry.register_middleware("test2", AnotherTestMiddleware)

        registry.clear_middleware()

        assert len(registry.list_middleware()) == 0

    def test_clear_exporters(self):
        """Test clearing all exporters"""
        registry = PluginRegistry()
        registry.register_exporter("test1", TestExporter)
        registry.register_exporter("test2", AnotherTestExporter)

        registry.clear_exporters()

        assert len(registry.list_exporters()) == 0

    def test_clear_all(self):
        """Test clearing all plugins"""
        registry = PluginRegistry()
        registry.register_middleware("test1", TestMiddleware)
        registry.register_exporter("test1", TestExporter)

        registry.clear_all()

        assert len(registry.list_middleware()) == 0
        assert len(registry.list_exporters()) == 0


class TestPluginLoading:
    """Test dynamic plugin loading"""

    def test_load_plugins_directory_not_found(self):
        """Test loading from nonexistent directory raises error"""
        registry = PluginRegistry()

        with pytest.raises(FileNotFoundError):
            registry.load_plugins(Path("/nonexistent/path"))

    def test_load_plugins_not_a_directory(self):
        """Test loading from non-directory path raises error"""
        registry = PluginRegistry()

        with tempfile.NamedTemporaryFile() as tmp:
            with pytest.raises(ValueError):
                registry.load_plugins(Path(tmp.name))

    def test_load_plugins_from_directory(self):
        """Test loading plugins from directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create plugin file
            plugin_file = Path(tmpdir) / "test_plugin.py"
            plugin_file.write_text("""
from instructions_framework import InstructionMiddleware

class CustomMiddleware(InstructionMiddleware):
    def process(self, instructions):
        return instructions
""")

            registry = PluginRegistry()
            registry.load_plugins(Path(tmpdir))

            # Should be registered with lowercased name minus "Middleware"
            assert registry.get_middleware("custom") is not None

    def test_load_plugins_multiple_classes(self):
        """Test loading multiple plugins from one file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = Path(tmpdir) / "test_plugins.py"
            plugin_file.write_text("""
from instructions_framework import InstructionMiddleware
from instructions_framework.exporters import BaseExporter

class FilterMiddleware(InstructionMiddleware):
    def process(self, instructions):
        return instructions

class CustomExporter(BaseExporter):
    def export(self, instructions, **kwargs):
        return "output"
""")

            registry = PluginRegistry()
            registry.load_plugins(Path(tmpdir))

            assert registry.get_middleware("filter") is not None
            assert registry.get_exporter("custom") is not None

    def test_load_plugins_skips_private_files(self):
        """Test that private files are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create private plugin file
            private_file = Path(tmpdir) / "_private_plugin.py"
            private_file.write_text("""
from instructions_framework import InstructionMiddleware

class PrivateMiddleware(InstructionMiddleware):
    def process(self, instructions):
        return instructions
""")

            registry = PluginRegistry()
            registry.load_plugins(Path(tmpdir))

            # Private files should be skipped
            assert registry.get_middleware("private") is None

    def test_load_plugins_skips_non_plugin_classes(self):
        """Test that non-plugin classes are not registered"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = Path(tmpdir) / "test_plugins.py"
            plugin_file.write_text("""
from instructions_framework import InstructionMiddleware

class RegularClass:
    pass

class CustomMiddleware(InstructionMiddleware):
    def process(self, instructions):
        return instructions
""")

            registry = PluginRegistry()
            registry.load_plugins(Path(tmpdir))

            # Only CustomMiddleware should be registered
            assert registry.get_middleware("custom") is not None
            middleware_count = len(registry.list_middleware())
            assert middleware_count == 1


class TestGlobalRegistry:
    """Test global registry singleton"""

    def test_get_global_registry_same_instance(self):
        """Test that get_global_registry returns same instance"""
        registry1 = get_global_registry()
        registry2 = get_global_registry()

        assert registry1 is registry2

    def test_global_registry_persistence(self):
        """Test that registrations persist in global registry"""
        registry1 = get_global_registry()
        registry1.register_middleware("test_global", TestMiddleware)

        registry2 = get_global_registry()
        assert registry2.get_middleware("test_global") is TestMiddleware


class TestPluginIntegration:
    """Integration tests for plugin system"""

    def test_plugin_registry_with_pipeline(self):
        """Test using registered plugins in a pipeline"""
        from instructions_framework import InstructionPipeline

        registry = PluginRegistry()
        registry.register_middleware("test", TestMiddleware)

        # Should be able to get middleware from registry
        middleware_class = registry.get_middleware("test")
        assert middleware_class is not None

        # Should be able to instantiate and use
        middleware = middleware_class()
        assert middleware is not None

    def test_multiple_registries_isolated(self):
        """Test that different registries are isolated"""
        registry1 = PluginRegistry()
        registry2 = PluginRegistry()

        registry1.register_middleware("test", TestMiddleware)

        # registry2 should not have the plugin
        assert registry2.get_middleware("test") is None
        assert registry1.get_middleware("test") is TestMiddleware
