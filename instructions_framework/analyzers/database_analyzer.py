"""Database analyzer - Task 22

Parses SQL migration files and schema files.
Detects tables, columns, and relationships.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Column:
    """Represents a database column"""

    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    unique: bool = False
    default: Optional[str] = None
    confidence: float = 1.0


@dataclass
class Table:
    """Represents a database table"""

    name: str
    columns: List[Column] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)
    indices: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class Migration:
    """Represents a database migration"""

    name: str
    version: Optional[str] = None
    timestamp: Optional[str] = None
    direction: str = "up"  # up or down
    operations: List[str] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)
    confidence: float = 1.0


class DatabaseAnalyzer:
    """Analyzes SQL migration and schema files"""

    # Pattern to match CREATE TABLE statements
    CREATE_TABLE_PATTERN = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(", re.IGNORECASE)

    # Pattern to match table name in migrations
    TABLE_NAME_PATTERN = re.compile(r"CREATE\s+TABLE\s+[`\"]?(\w+)[`\"]?", re.IGNORECASE)

    # Pattern to match column definitions
    COLUMN_PATTERN = re.compile(
        r"(\w+)\s+([\w()]+)(?:\s+(NOT\s+NULL|NULL|UNIQUE|PRIMARY\s+KEY|AUTO_INCREMENT|DEFAULT\s+['\"]?[^,\)]*['\"]?))?"
    )

    # Pattern to match ALTER TABLE statements
    ALTER_TABLE_PATTERN = re.compile(r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(\w+)", re.IGNORECASE)

    # Pattern to match DROP TABLE statements
    DROP_TABLE_PATTERN = re.compile(r"DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?(\w+)", re.IGNORECASE)

    # Pattern to match foreign key constraints
    FK_PATTERN = re.compile(
        r"FOREIGN\s+KEY\s*\((\w+)\)\s+REFERENCES\s+(\w+)\s*\((\w+)\)",
        re.IGNORECASE,
    )

    # Pattern to match migration version/timestamp
    MIGRATION_VERSION_PATTERN = re.compile(r"(\d{14}|\d{8}|\d+)_")

    def __init__(self):
        """Initialize database analyzer"""
        self.content = ""
        self.tables: List[Table] = []
        self.migrations: List[Migration] = []

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a SQL migration or schema file.

        Args:
            file_path: Path to SQL file

        Returns:
            Dictionary with tables, migrations, columns, relationships
        """
        file_path = Path(file_path)

        # Validate file
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "tables": [],
                "migrations": [],
            }

        if file_path.suffix not in [".sql"]:
            return {
                "success": False,
                "error": f"Not a SQL file: {file_path}",
                "tables": [],
                "migrations": [],
            }

        try:
            self.content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "tables": [],
                "migrations": [],
            }

        # Detect if this is a migration or schema file
        is_migration = self._is_migration_file(file_path)

        # Parse content
        if is_migration:
            self._parse_migration()
        else:
            self._parse_schema()

        return {
            "success": True,
            "file_type": "migration" if is_migration else "schema",
            "tables": [asdict(t) for t in self.tables],
            "migrations": [asdict(m) for m in self.migrations],
            "table_count": len(self.tables),
            "column_count": sum(len(t.columns) for t in self.tables),
            "relationship_count": sum(len(t.foreign_keys) for t in self.tables),
            "confidence": self._calculate_confidence(),
        }

    def _is_migration_file(self, file_path: Path) -> bool:
        """Determine if file is a migration or schema file"""
        name = file_path.name.lower()

        # Common migration patterns
        if "migration" in name or "migrate" in name:
            return True

        # Common version/timestamp patterns
        if self.MIGRATION_VERSION_PATTERN.search(name):
            return True

        # Schema files usually don't have version numbers
        if "schema" in name or "ddl" in name or "init" in name:
            return False

        # Check content for migration markers
        if "BEGIN" in self.content and "COMMIT" in self.content:
            return True

        return False

    def _parse_migration(self) -> None:
        """Parse a migration file"""
        # Extract migration metadata
        version = self._extract_version()

        # Split by statements
        statements = self._split_statements()

        operations = []
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue

            # Classify operation
            if "CREATE TABLE" in stmt.upper():
                operations.append("CREATE TABLE")
                table = self._parse_create_table(stmt)
                if table:
                    self.tables.append(table)
            elif "ALTER TABLE" in stmt.upper():
                operations.append("ALTER TABLE")
            elif "DROP TABLE" in stmt.upper():
                operations.append("DROP TABLE")
                match = self.DROP_TABLE_PATTERN.search(stmt)
                if match:
                    operations.append(f"DROP TABLE {match.group(1)}")
            elif "INSERT INTO" in stmt.upper():
                operations.append("INSERT DATA")
            elif "UPDATE" in stmt.upper():
                operations.append("UPDATE DATA")

        migration = Migration(
            name=version or "unknown",
            version=version,
            direction="up",
            operations=operations,
            tables=[t.name for t in self.tables],
        )

        self.migrations.append(migration)

    def _parse_schema(self) -> None:
        """Parse a schema/DDL file"""
        # Find all CREATE TABLE statements
        for match in self.CREATE_TABLE_PATTERN.finditer(self.content):
            # Extract the full statement from match position
            start = match.start()
            end = self._find_statement_end(start)

            statement = self.content[start:end]
            table = self._parse_create_table(statement)

            if table:
                self.tables.append(table)

    def _parse_create_table(self, statement: str) -> Optional[Table]:
        """Parse a CREATE TABLE statement"""
        # Extract table name
        match = self.TABLE_NAME_PATTERN.search(statement)
        if not match:
            return None

        table_name = match.group(1)

        # Extract content between parentheses
        start_paren = statement.find("(")
        end_paren = self._find_matching_paren(statement, start_paren)

        if start_paren == -1 or end_paren == -1:
            return None

        content = statement[start_paren + 1 : end_paren]

        # Parse columns and constraints
        columns = []
        primary_keys = []
        foreign_keys = []

        for line in content.split(","):
            line = line.strip()

            if not line:
                continue

            # Check for PRIMARY KEY constraint
            if "PRIMARY KEY" in line.upper():
                match = re.search(r"PRIMARY\s+KEY\s*\(([^)]+)\)", line, re.IGNORECASE)
                if match:
                    pks = match.group(1).split(",")
                    primary_keys.extend([pk.strip().strip("`\"") for pk in pks])
                continue

            # Check for FOREIGN KEY constraint
            if "FOREIGN KEY" in line.upper():
                fk_match = self.FK_PATTERN.search(line)
                if fk_match:
                    foreign_keys.append(
                        {
                            "column": fk_match.group(1),
                            "references_table": fk_match.group(2),
                            "references_column": fk_match.group(3),
                        }
                    )
                continue

            # Parse as column definition
            col = self._parse_column(line)
            if col:
                columns.append(col)

        table = Table(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
        )

        return table

    def _parse_column(self, definition: str) -> Optional[Column]:
        """Parse a column definition"""
        # Extract column name and type
        parts = definition.split()
        if len(parts) < 2:
            return None

        column_name = parts[0].strip("`\"")
        column_type = parts[1].strip("`\"")

        # Check modifiers
        nullable = "NOT NULL" not in definition.upper()
        primary_key = "PRIMARY KEY" in definition.upper()
        unique = "UNIQUE" in definition.upper()

        # Extract default value
        default = None
        if "DEFAULT" in definition.upper():
            match = re.search(r"DEFAULT\s+(['\"]?[^,\)]*['\"]?)", definition, re.IGNORECASE)
            if match:
                default = match.group(1)

        return Column(
            name=column_name,
            type=column_type,
            nullable=nullable,
            primary_key=primary_key,
            unique=unique,
            default=default,
        )

    def _find_statement_end(self, start: int) -> int:
        """Find the end of a SQL statement"""
        # Look for semicolon
        semicolon = self.content.find(";", start)
        if semicolon != -1:
            return semicolon + 1

        return len(self.content)

    def _find_matching_paren(self, text: str, start: int) -> int:
        """Find matching closing parenthesis"""
        count = 0
        for i in range(start, len(text)):
            if text[i] == "(":
                count += 1
            elif text[i] == ")":
                count -= 1
                if count == 0:
                    return i

        return -1

    def _split_statements(self) -> List[str]:
        """Split SQL content into individual statements"""
        statements = []
        current = ""

        for line in self.content.split("\n"):
            current += line + "\n"

            if ";" in line:
                statements.append(current)
                current = ""

        if current.strip():
            statements.append(current)

        return statements

    def _extract_version(self) -> Optional[str]:
        """Extract version/timestamp from file content or context"""
        # Look for version in content
        match = re.search(r"-- version:\s*(\d+)", self.content, re.IGNORECASE)
        if match:
            return match.group(1)

        match = re.search(r"--\s*(\d{14}|\d{8})", self.content)
        if match:
            return match.group(1)

        return None

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score"""
        if not self.tables and not self.migrations:
            return 0.3

        if self.tables:
            avg_table_confidence = sum(t.confidence for t in self.tables) / len(self.tables)
            return avg_table_confidence

        if self.migrations:
            avg_migration_confidence = sum(m.confidence for m in self.migrations) / len(self.migrations)
            return avg_migration_confidence

        return 0.5
