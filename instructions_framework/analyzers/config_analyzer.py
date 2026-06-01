"""Configuration file analyzer - Task 21

Parses YAML, XML, properties, and other config formats.
Returns structured data with confidence scores.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

try:
    import yaml
except ImportError:
    yaml = None

try:
    import xml.etree.ElementTree as ET
except ImportError:
    ET = None


@dataclass
class ConfigProperty:
    """Represents a configuration property"""

    key: str
    value: Optional[str] = None
    section: Optional[str] = None
    confidence: float = 1.0


@dataclass
class ConfigDatabase:
    """Represents a database configuration"""

    name: str
    type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    properties: List[ConfigProperty] = field(default_factory=list)
    confidence: float = 1.0


class ConfigAnalyzer:
    """Analyzes configuration files (YAML, XML, Properties, JSON)"""

    def __init__(self):
        """Initialize config analyzer"""
        self.content = ""
        self.file_format = ""
        self.properties: List[ConfigProperty] = []
        self.databases: List[ConfigDatabase] = []
        self.sections: Dict[str, List[ConfigProperty]] = {}

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a configuration file.

        Args:
            file_path: Path to config file (YAML, XML, properties, JSON, etc.)

        Returns:
            Dictionary with properties, databases, sections
        """
        file_path = Path(file_path)

        # Validate file
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "properties": [],
                "databases": [],
            }

        # Determine file format
        self.file_format = self._detect_format(file_path)

        if not self.file_format:
            return {
                "success": False,
                "error": f"Unsupported config format: {file_path}",
                "properties": [],
                "databases": [],
            }

        try:
            self.content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "properties": [],
                "databases": [],
            }

        # Parse content based on format
        try:
            if self.file_format == "yaml":
                self._parse_yaml()
            elif self.file_format == "xml":
                self._parse_xml()
            elif self.file_format == "properties":
                self._parse_properties()
            elif self.file_format == "json":
                self._parse_json()
            elif self.file_format == "toml":
                self._parse_toml()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse {self.file_format} file: {e}",
                "properties": [],
                "databases": [],
            }

        return {
            "success": True,
            "format": self.file_format,
            "properties": [asdict(p) for p in self.properties],
            "databases": [asdict(d) for d in self.databases],
            "sections": {k: [asdict(p) for p in v] for k, v in self.sections.items()},
            "confidence": self._calculate_confidence(),
        }

    def _detect_format(self, file_path: Path) -> Optional[str]:
        """Detect configuration file format"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        if suffix in [".yaml", ".yml"]:
            return "yaml"
        elif suffix == ".xml":
            return "xml"
        elif suffix == ".properties":
            return "properties"
        elif suffix == ".json":
            return "json"
        elif suffix in [".toml", ".ini", ".cfg"]:
            return "toml"
        elif name in ["dockerfile", "docker-compose.yml", "docker-compose.yaml"]:
            return "yaml"
        elif "application" in name and suffix == ".properties":
            return "properties"

        return None

    def _parse_yaml(self) -> None:
        """Parse YAML configuration"""
        if not yaml:
            # Fallback to regex parsing
            self._parse_yaml_regex()
            return

        try:
            data = yaml.safe_load(self.content)
            self._flatten_dict(data, "")
        except Exception:
            # Fallback to regex parsing
            self._parse_yaml_regex()

    def _parse_yaml_regex(self) -> None:
        """Parse YAML using regex (fallback)"""
        current_section = None

        for line in self.content.split("\n"):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Check for section headers (no colon or ends with colon)
            if ":" in line and not line.endswith(":"):
                # It's a property
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key:
                    prop = ConfigProperty(
                        key=key,
                        value=value,
                        section=current_section,
                    )
                    self.properties.append(prop)

                    if current_section:
                        if current_section not in self.sections:
                            self.sections[current_section] = []
                        self.sections[current_section].append(prop)

                    # Check for database configs
                    if "database" in key.lower() or "db" in key.lower():
                        self._check_database_config(key, value)

            elif line.endswith(":"):
                # It's a section header
                current_section = line[:-1].strip()

    def _parse_properties(self) -> None:
        """Parse Java properties file"""
        current_section = None

        for line in self.content.split("\n"):
            line = line.strip()

            if not line or line.startswith("#") or line.startswith("!"):
                # Check for section comments
                if line.startswith("# "):
                    current_section = line[2:].strip()
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                prop = ConfigProperty(
                    key=key,
                    value=value,
                    section=current_section,
                )
                self.properties.append(prop)

                if current_section:
                    if current_section not in self.sections:
                        self.sections[current_section] = []
                    self.sections[current_section].append(prop)

                # Check for database configs
                if "database" in key.lower() or "db" in key.lower() or "datasource" in key.lower():
                    self._check_database_config(key, value)

    def _parse_xml(self) -> None:
        """Parse XML configuration"""
        if not ET:
            return

        try:
            root = ET.fromstring(self.content)
            self._extract_xml_properties(root)
        except Exception:
            pass

    def _extract_xml_properties(self, element: Any, path: str = "") -> None:
        """Recursively extract properties from XML"""
        current_path = f"{path}/{element.tag}" if path else element.tag

        # Extract properties from attributes
        for key, value in element.attrib.items():
            prop = ConfigProperty(
                key=key,
                value=value,
                section=current_path,
            )
            self.properties.append(prop)

        # Extract text content
        if element.text and element.text.strip():
            prop = ConfigProperty(
                key="value",
                value=element.text.strip(),
                section=current_path,
            )
            self.properties.append(prop)

        # Recurse into children
        for child in element:
            self._extract_xml_properties(child, current_path)

    def _parse_json(self) -> None:
        """Parse JSON configuration"""
        import json

        try:
            data = json.loads(self.content)
            self._flatten_dict(data, "")
        except Exception:
            pass

    def _parse_toml(self) -> None:
        """Parse TOML/INI configuration (using regex)"""
        current_section = None

        for line in self.content.split("\n"):
            line = line.strip()

            if not line or line.startswith("#") or line.startswith(";"):
                continue

            # Check for section headers
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                prop = ConfigProperty(
                    key=key,
                    value=value,
                    section=current_section,
                )
                self.properties.append(prop)

                if current_section:
                    if current_section not in self.sections:
                        self.sections[current_section] = []
                    self.sections[current_section].append(prop)

    def _flatten_dict(self, d: Dict[str, Any], prefix: str) -> None:
        """Flatten nested dictionary into properties"""
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # It's a section
                if full_key not in self.sections:
                    self.sections[full_key] = []

                self._flatten_dict(value, full_key)
            else:
                # It's a property
                prop = ConfigProperty(
                    key=key,
                    value=str(value) if value is not None else None,
                    section=prefix,
                )
                self.properties.append(prop)

                if prefix:
                    if prefix not in self.sections:
                        self.sections[prefix] = []
                    self.sections[prefix].append(prop)

                # Check for database configs
                if "database" in key.lower() or "db" in key.lower():
                    self._check_database_config(key, str(value))

    def _check_database_config(self, key: str, value: str) -> None:
        """Check if this is a database configuration and extract details"""
        key_lower = key.lower()

        # Common patterns for database names
        if "database" in key_lower or "schema" in key_lower:
            if key_lower not in [d.name for d in self.databases]:
                self.databases.append(ConfigDatabase(name=key, type="unknown"))

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score"""
        if not self.content:
            return 0.0

        if not self.properties and not self.databases:
            return 0.3

        return 0.85
