"""Plugin system for instructions framework - enables dynamic loading of custom middleware and exporters"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, Optional, Type
from .middleware.base import InstructionMiddleware
from .exporters.base import BaseExporter


class PluginRegistry:
    """
    Registry for custom middleware and exporters.

    Supports:
    - Registering custom middleware and exporter classes
    - Retrieving registered plugins by name
    - Dynamically loading plugins from filesystem

    Example:
        registry = PluginRegistry()
        registry.register_middleware("custom", CustomMiddleware)
        middleware = registry.get_middleware("custom")
    """

    def __init__(self):
        """Initialize empty registries for middleware and exporters"""
        self.middleware: Dict[str, Type[InstructionMiddleware]] = {}
        self.exporters: Dict[str, Type[BaseExporter]] = {}

    def register_middleware(self, name: str, cls: Type[InstructionMiddleware]) -> None:
        """
        Register a custom middleware class.

        Args:
            name: Unique name for the middleware
            cls: Middleware class (must inherit from InstructionMiddleware)

        Raises:
            TypeError: If cls is not a subclass of InstructionMiddleware
            ValueError: If name is already registered
        """
        if not issubclass(cls, InstructionMiddleware):
            raise TypeError(
                f"cls must be a subclass of InstructionMiddleware, got {cls.__name__}"
            )

        if name in self.middleware:
            raise ValueError(f"Middleware '{name}' is already registered")

        self.middleware[name] = cls

    def register_exporter(self, name: str, cls: Type[BaseExporter]) -> None:
        """
        Register a custom exporter class.

        Args:
            name: Unique name for the exporter
            cls: Exporter class (must inherit from BaseExporter)

        Raises:
            TypeError: If cls is not a subclass of BaseExporter
            ValueError: If name is already registered
        """
        if not issubclass(cls, BaseExporter):
            raise TypeError(
                f"cls must be a subclass of BaseExporter, got {cls.__name__}"
            )

        if name in self.exporters:
            raise ValueError(f"Exporter '{name}' is already registered")

        self.exporters[name] = cls

    def get_middleware(self, name: str) -> Optional[Type[InstructionMiddleware]]:
        """
        Retrieve a registered middleware class by name.

        Args:
            name: Name of the middleware

        Returns:
            Middleware class if found, None otherwise
        """
        return self.middleware.get(name)

    def get_exporter(self, name: str) -> Optional[Type[BaseExporter]]:
        """
        Retrieve a registered exporter class by name.

        Args:
            name: Name of the exporter

        Returns:
            Exporter class if found, None otherwise
        """
        return self.exporters.get(name)

    def list_middleware(self) -> Dict[str, Type[InstructionMiddleware]]:
        """Get all registered middleware as a dictionary"""
        return self.middleware.copy()

    def list_exporters(self) -> Dict[str, Type[BaseExporter]]:
        """Get all registered exporters as a dictionary"""
        return self.exporters.copy()

    def load_plugins(self, plugin_dir: Path) -> None:
        """
        Dynamically load plugins from a directory.

        Discovers Python files in plugin_dir, imports them, and automatically
        registers any classes that inherit from InstructionMiddleware or BaseExporter.

        Plugin naming convention:
        - Middleware classes should have names ending with 'Middleware'
        - Exporter classes should have names ending with 'Exporter'

        Args:
            plugin_dir: Path to directory containing plugin modules

        Raises:
            FileNotFoundError: If plugin_dir does not exist
            ImportError: If plugin modules cannot be imported

        Example:
            registry.load_plugins(Path("./custom_plugins"))
        """
        plugin_dir = Path(plugin_dir)

        if not plugin_dir.exists():
            raise FileNotFoundError(f"Plugin directory does not exist: {plugin_dir}")

        if not plugin_dir.is_dir():
            raise ValueError(f"Path is not a directory: {plugin_dir}")

        # Find all Python files in the plugin directory
        plugin_files = list(plugin_dir.glob("*.py"))

        for plugin_file in plugin_files:
            if plugin_file.name.startswith("_"):
                # Skip private/dunder files
                continue

            module_name = plugin_file.stem

            try:
                # Load the module dynamically
                spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Scan module for classes to register
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Skip non-classes and base classes
                    if not isinstance(attr, type):
                        continue

                    # Register middleware
                    if (
                        issubclass(attr, InstructionMiddleware)
                        and attr is not InstructionMiddleware
                        and attr_name.endswith("Middleware")
                    ):
                        plugin_name = (
                            attr_name[:-10].lower()
                        )  # Remove 'Middleware' suffix and lowercase
                        self.register_middleware(plugin_name, attr)

                    # Register exporters
                    elif (
                        issubclass(attr, BaseExporter)
                        and attr is not BaseExporter
                        and attr_name.endswith("Exporter")
                    ):
                        plugin_name = (
                            attr_name[:-8].lower()
                        )  # Remove 'Exporter' suffix and lowercase
                        self.register_exporter(plugin_name, attr)

            except Exception as e:
                raise ImportError(
                    f"Failed to load plugin from {plugin_file}: {str(e)}"
                ) from e

    def unregister_middleware(self, name: str) -> bool:
        """
        Unregister a middleware by name.

        Args:
            name: Name of the middleware to unregister

        Returns:
            True if unregistered, False if not found
        """
        if name in self.middleware:
            del self.middleware[name]
            return True
        return False

    def unregister_exporter(self, name: str) -> bool:
        """
        Unregister an exporter by name.

        Args:
            name: Name of the exporter to unregister

        Returns:
            True if unregistered, False if not found
        """
        if name in self.exporters:
            del self.exporters[name]
            return True
        return False

    def clear_middleware(self) -> None:
        """Clear all registered middleware"""
        self.middleware.clear()

    def clear_exporters(self) -> None:
        """Clear all registered exporters"""
        self.exporters.clear()

    def clear_all(self) -> None:
        """Clear all registered middleware and exporters"""
        self.clear_middleware()
        self.clear_exporters()


# Global plugin registry instance
_global_registry: Optional[PluginRegistry] = None


def get_global_registry() -> PluginRegistry:
    """
    Get or create the global plugin registry.

    Returns:
        Global PluginRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
    return _global_registry
