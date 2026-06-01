"""Repo Scanner Agent for deterministic fact extraction from source code."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Node,
    NodeType,
    Report,
    Edge,
    EdgeType,
)
from context_builder.services.git_service import GitService


class RepoScannerAgent(BaseAgent):
    """Scan repositories and extract deterministic facts.

    Responsibilities:
    - Scan files using include/exclude patterns from scan config
    - Extract classes, methods, endpoints, consumers, producers, schedulers
    - Detect configuration files and properties
    - Detect database schemas and middleware topics
    - Return raw-symbols.json and scan-report.md

    Attributes:
        git_service: GitService instance for file operations
        JAVA_CLASS_PATTERN: Regex pattern for Java class detection
        JAVA_METHOD_PATTERN: Regex pattern for Java method detection
        PYTHON_CLASS_PATTERN: Regex pattern for Python class detection
        PYTHON_FUNCTION_PATTERN: Regex pattern for Python function detection
    """

    JAVA_CLASS_PATTERN = re.compile(r'(?:public|private|protected)?\s*(?:static)?\s*(?:abstract)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+(.+?))?(?:\s*[{\n])?', re.MULTILINE | re.IGNORECASE)
    JAVA_METHOD_PATTERN = re.compile(r'(?:public|private|protected)?\s*(?:static)?\s*(?:\w+\s+)*?(\w+)\s*\([^)]*\)\s*(?:throws\s+.+?)?\s*\{')
    JAVA_ENDPOINT_PATTERN = re.compile(r'@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\s*["\']([^"\']+)["\']')
    JAVA_CONSUMER_PATTERN = re.compile(r'@(?:JmsListener|KafkaListener|RabbitListener)\s*\(')
    JAVA_PRODUCER_PATTERN = re.compile(r'(?:JmsTemplate|KafkaTemplate|RabbitTemplate).*?(?:\.send|\.convertAndSend)', re.DOTALL)
    JAVA_SCHEDULER_PATTERN = re.compile(r'@Scheduled\s*\(')

    PYTHON_CLASS_PATTERN = re.compile(r'^class\s+(\w+)(?:\s*\((.+?)\))?:', re.MULTILINE)
    PYTHON_FUNCTION_PATTERN = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)
    PYTHON_ENDPOINT_PATTERN = re.compile(r'@(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']')
    PYTHON_TASK_PATTERN = re.compile(r'@(?:shared_task|celery\.task|task\.delay)\s*')

    CONFIG_FILES = {
        'properties': ['application.properties', 'application.yml', 'application.yaml'],
        'xml': ['pom.xml', 'web.xml', 'applicationContext.xml'],
        'gradle': ['build.gradle', 'build.gradle.kts'],
        'json': ['package.json', '.env', '.env.local', 'config.json'],
        'toml': ['pyproject.toml', 'Cargo.toml'],
        'sql': ['schema.sql', 'migration.sql'],
    }

    def __init__(self):
        """Initialize the RepoScannerAgent."""
        super().__init__(name="RepoScannerAgent")
        self.git_service = GitService()

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Scan repositories and extract deterministic facts.

        Args:
            context: ExecutionContext containing workspace and scan configs.

        Returns:
            AgentOutput with extracted symbols and scan report.
        """
        if not self.validate_context(context):
            return AgentOutput(
                status="error",
                message="Invalid execution context",
                errors=["ExecutionContext is None"],
            )

        if not context.workspace_config or not context.scan_config:
            return AgentOutput(
                status="error",
                message="Missing workspace or scan config",
                errors=["Config not loaded"],
            )

        try:
            symbols = {
                "classes": [],
                "methods": [],
                "endpoints": [],
                "consumers": [],
                "producers": [],
                "schedulers": [],
                "configurations": [],
                "databases": [],
                "middleware_topics": [],
                "external_apis": [],
            }

            total_files = 0
            total_symbols = 0
            processed_repos = 0

            # Scan each repository
            for repo_config in context.workspace_config.repositories:
                repo_path = Path(repo_config.get("local_path", ""))
                repo_id = repo_config.get("id", "unknown")

                if not repo_path.exists():
                    self.logger.warning(f"Repository path does not exist: {repo_path}")
                    continue

                processed_repos += 1

                # List files matching patterns
                files = self.git_service.list_files(
                    repo_path,
                    context.scan_config.include_patterns,
                    context.scan_config.exclude_patterns,
                )

                total_files += len(files)

                # Extract symbols from files
                repo_symbols = self._extract_symbols_from_files(
                    files, repo_id, repo_path, context
                )

                # Merge symbols
                for key in symbols:
                    if key in repo_symbols:
                        symbols[key].extend(repo_symbols[key])
                        total_symbols += len(repo_symbols[key])

                # Extract configuration files
                config_symbols = self._extract_configuration_symbols(
                    repo_path, repo_id, context.scan_config.include_patterns
                )
                symbols["configurations"].extend(config_symbols)

                # Extract database schemas
                db_symbols = self._extract_database_symbols(
                    repo_path, repo_id, context.scan_config.include_patterns
                )
                symbols["databases"].extend(db_symbols)

                # Extract middleware topics
                middleware_symbols = self._extract_middleware_symbols(
                    files, repo_id, repo_path
                )
                symbols["middleware_topics"].extend(middleware_symbols)

            # Generate raw-symbols.json
            symbols_artifact = self._save_symbols_json(symbols, context)

            # Generate scan-report.md
            report = self._generate_scan_report(
                symbols, total_files, processed_repos, total_symbols
            )
            context.reports["scan_report"] = report

            # Add symbols to graph
            self._add_symbols_to_graph(symbols, context)

            self.logger.info(
                f"Scanned {total_files} files across {processed_repos} repositories, "
                f"extracted {total_symbols} symbols"
            )

            return AgentOutput(
                status="success",
                message=f"Scanned {total_files} files and extracted {total_symbols} symbols",
                artifacts=[symbols_artifact] if symbols_artifact else [],
                metrics={
                    "total_files": total_files,
                    "processed_repos": processed_repos,
                    "total_symbols": total_symbols,
                    "classes": len(symbols.get("classes", [])),
                    "methods": len(symbols.get("methods", [])),
                    "endpoints": len(symbols.get("endpoints", [])),
                    "consumers": len(symbols.get("consumers", [])),
                    "producers": len(symbols.get("producers", [])),
                    "schedulers": len(symbols.get("schedulers", [])),
                    "configurations": len(symbols.get("configurations", [])),
                    "databases": len(symbols.get("databases", [])),
                    "middleware_topics": len(symbols.get("middleware_topics", [])),
                },
            )
        except Exception as e:
            self.logger.error(f"Error in RepoScannerAgent: {e}", exc_info=True)
            return AgentOutput(
                status="error",
                message=str(e),
                errors=[str(e)],
            )

    def _extract_symbols_from_files(
        self,
        files: List[Path],
        repo_id: str,
        repo_path: Path,
        context: ExecutionContext,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract symbols (classes, methods, endpoints) from files.

        Args:
            files: List of file paths to scan.
            repo_id: Repository identifier.
            repo_path: Root path of repository.
            context: ExecutionContext for configuration.

        Returns:
            Dictionary with extracted symbols categorized by type.
        """
        symbols = {
            "classes": [],
            "methods": [],
            "endpoints": [],
            "consumers": [],
            "producers": [],
            "schedulers": [],
            "external_apis": [],
        }

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                relative_path = file_path.relative_to(repo_path)

                # Detect language
                language = self._detect_language(file_path)

                if language == "java":
                    self._extract_java_symbols(
                        content, file_path, repo_id, symbols
                    )
                elif language == "python":
                    self._extract_python_symbols(
                        content, file_path, repo_id, symbols
                    )

            except Exception as e:
                self.logger.debug(f"Error processing file {file_path}: {e}")
                continue

        return symbols

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension.

        Args:
            file_path: File path to analyze.

        Returns:
            Language identifier or None if unknown.
        """
        ext_to_lang = {
            ".java": "java",
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".go": "go",
            ".rs": "rust",
        }
        return ext_to_lang.get(file_path.suffix)

    def _extract_java_symbols(
        self,
        content: str,
        file_path: Path,
        repo_id: str,
        symbols: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Extract symbols from Java source file.

        Args:
            content: File content as string.
            file_path: File path.
            repo_id: Repository identifier.
            symbols: Dictionary to populate with extracted symbols.
        """
        file_str = str(file_path)

        # Extract classes
        for class_match in self.JAVA_CLASS_PATTERN.finditer(content):
            class_name = class_match.group(1)
            parent_class = class_match.group(2)
            interfaces = class_match.group(3)

            symbols["classes"].append({
                "id": f"{repo_id}-class-{class_name}",
                "name": class_name,
                "type": "class",
                "file": file_str,
                "repository": repo_id,
                "parent": parent_class,
                "interfaces": interfaces,
            })

        # Extract endpoints
        for endpoint_match in self.JAVA_ENDPOINT_PATTERN.finditer(content):
            endpoint = endpoint_match.group(1)
            symbols["endpoints"].append({
                "id": f"{repo_id}-endpoint-{endpoint.replace('/', '-')}",
                "name": endpoint,
                "type": "endpoint",
                "file": file_str,
                "repository": repo_id,
                "framework": "spring",
            })

        # Extract consumers
        if self.JAVA_CONSUMER_PATTERN.search(content):
            # Find consumer class name
            class_match = self.JAVA_CLASS_PATTERN.search(content)
            if class_match:
                consumer_name = class_match.group(1)
                symbols["consumers"].append({
                    "id": f"{repo_id}-consumer-{consumer_name}",
                    "name": consumer_name,
                    "type": "consumer",
                    "file": file_str,
                    "repository": repo_id,
                    "framework": "spring",
                })

        # Extract producers
        if self.JAVA_PRODUCER_PATTERN.search(content):
            class_match = self.JAVA_CLASS_PATTERN.search(content)
            if class_match:
                producer_name = class_match.group(1)
                symbols["producers"].append({
                    "id": f"{repo_id}-producer-{producer_name}",
                    "name": producer_name,
                    "type": "producer",
                    "file": file_str,
                    "repository": repo_id,
                    "framework": "spring",
                })

        # Extract schedulers
        if self.JAVA_SCHEDULER_PATTERN.search(content):
            class_match = self.JAVA_CLASS_PATTERN.search(content)
            if class_match:
                scheduler_name = class_match.group(1)
                symbols["schedulers"].append({
                    "id": f"{repo_id}-scheduler-{scheduler_name}",
                    "name": scheduler_name,
                    "type": "scheduler",
                    "file": file_str,
                    "repository": repo_id,
                    "framework": "spring",
                })

    def _extract_python_symbols(
        self,
        content: str,
        file_path: Path,
        repo_id: str,
        symbols: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """Extract symbols from Python source file.

        Args:
            content: File content as string.
            file_path: File path.
            repo_id: Repository identifier.
            symbols: Dictionary to populate with extracted symbols.
        """
        file_str = str(file_path)

        # Extract classes
        for class_match in self.PYTHON_CLASS_PATTERN.finditer(content):
            class_name = class_match.group(1)
            parent_class = class_match.group(2)

            symbols["classes"].append({
                "id": f"{repo_id}-class-{class_name}",
                "name": class_name,
                "type": "class",
                "file": file_str,
                "repository": repo_id,
                "parent": parent_class,
            })

        # Extract endpoints
        for endpoint_match in self.PYTHON_ENDPOINT_PATTERN.finditer(content):
            endpoint = endpoint_match.group(1)
            symbols["endpoints"].append({
                "id": f"{repo_id}-endpoint-{endpoint.replace('/', '-')}",
                "name": endpoint,
                "type": "endpoint",
                "file": file_str,
                "repository": repo_id,
                "framework": "fastapi",
            })

        # Extract tasks/schedulers
        if self.PYTHON_TASK_PATTERN.search(content):
            # Find function definitions near task decorators
            for func_match in self.PYTHON_FUNCTION_PATTERN.finditer(content):
                func_name = func_match.group(1)
                symbols["schedulers"].append({
                    "id": f"{repo_id}-scheduler-{func_name}",
                    "name": func_name,
                    "type": "scheduler",
                    "file": file_str,
                    "repository": repo_id,
                    "framework": "celery",
                })

    def _extract_configuration_symbols(
        self,
        repo_path: Path,
        repo_id: str,
        include_patterns: List[str],
    ) -> List[Dict[str, Any]]:
        """Extract configuration files and properties.

        Args:
            repo_path: Root path of repository.
            repo_id: Repository identifier.
            include_patterns: Include patterns from scan config.

        Returns:
            List of configuration symbols.
        """
        config_symbols = []

        # Check for known configuration files
        for config_type, config_names in self.CONFIG_FILES.items():
            for config_name in config_names:
                config_path = repo_path / config_name
                if config_path.exists():
                    config_symbols.append({
                        "id": f"{repo_id}-config-{config_name}",
                        "name": config_name,
                        "type": "configuration",
                        "file": str(config_path),
                        "repository": repo_id,
                        "config_type": config_type,
                    })

        return config_symbols

    def _extract_database_symbols(
        self,
        repo_path: Path,
        repo_id: str,
        include_patterns: List[str],
    ) -> List[Dict[str, Any]]:
        """Extract database schemas and migration files.

        Args:
            repo_path: Root path of repository.
            repo_id: Repository identifier.
            include_patterns: Include patterns from scan config.

        Returns:
            List of database symbols.
        """
        db_symbols = []

        # Find SQL files and migration directories
        migration_dirs = [
            "migrations",
            "db/migrations",
            "database/migrations",
            "src/main/resources/db/migration",
        ]

        for migration_dir in migration_dirs:
            migration_path = repo_path / migration_dir
            if migration_path.exists():
                for sql_file in migration_path.glob("*.sql"):
                    db_symbols.append({
                        "id": f"{repo_id}-db-{sql_file.stem}",
                        "name": sql_file.stem,
                        "type": "database",
                        "file": str(sql_file),
                        "repository": repo_id,
                        "db_type": "migration",
                    })

        # Find schema definition files
        for schema_name in ["schema.sql", "schema.py", "models.py"]:
            schema_path = repo_path.rglob(schema_name)
            for file_path in schema_path:
                db_symbols.append({
                    "id": f"{repo_id}-db-{file_path.stem}",
                    "name": file_path.stem,
                    "type": "database",
                    "file": str(file_path),
                    "repository": repo_id,
                    "db_type": "schema",
                })

        return db_symbols

    def _extract_middleware_symbols(
        self,
        files: List[Path],
        repo_id: str,
        repo_path: Path,
    ) -> List[Dict[str, Any]]:
        """Extract middleware topics (Kafka, RabbitMQ, etc.).

        Args:
            files: List of file paths to scan.
            repo_id: Repository identifier.
            repo_path: Root path of repository.

        Returns:
            List of middleware topic symbols.
        """
        middleware_symbols = []
        middleware_patterns = {
            "kafka": re.compile(r'["\']([\w\-\.]+)["\'].*?(?:topic|Topic)', re.IGNORECASE),
            "rabbitmq": re.compile(r'["\']([\w\-\.]+)["\'].*?(?:queue|Queue|exchange|Exchange)', re.IGNORECASE),
            "jms": re.compile(r'destination\s*=\s*["\']([\w\-\.]+)["\']', re.IGNORECASE),
        }

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                for middleware_type, pattern in middleware_patterns.items():
                    for match in pattern.finditer(content):
                        topic_name = match.group(1)
                        middleware_symbols.append({
                            "id": f"{repo_id}-middleware-{middleware_type}-{topic_name}",
                            "name": topic_name,
                            "type": "middleware_topic",
                            "file": str(file_path.relative_to(repo_path)),
                            "repository": repo_id,
                            "middleware": middleware_type,
                        })

            except Exception as e:
                self.logger.debug(f"Error extracting middleware from {file_path}: {e}")
                continue

        return middleware_symbols

    def _save_symbols_json(
        self,
        symbols: Dict[str, List[Dict[str, Any]]],
        context: ExecutionContext,
    ) -> Optional[Path]:
        """Save extracted symbols to raw-symbols.json.

        Args:
            symbols: Dictionary of extracted symbols.
            context: ExecutionContext for file path resolution.

        Returns:
            Path to saved JSON file or None if save failed.
        """
        try:
            if not context.workspace_config:
                return None

            output_dir = Path(context.workspace_config.context_root) / "symbols"
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / "raw-symbols.json"
            with open(output_path, "w") as f:
                json.dump(symbols, f, indent=2, default=str)

            self.logger.info(f"Saved symbols to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error saving symbols JSON: {e}")
            return None

    def _generate_scan_report(
        self,
        symbols: Dict[str, List[Dict[str, Any]]],
        total_files: int,
        processed_repos: int,
        total_symbols: int,
    ) -> Report:
        """Generate scan report markdown.

        Args:
            symbols: Dictionary of extracted symbols.
            total_files: Total files scanned.
            processed_repos: Number of repositories processed.
            total_symbols: Total symbols extracted.

        Returns:
            Report object with scan findings.
        """
        content = "# Repository Scan Report\n\n"

        content += "## Summary\n\n"
        content += f"- **Repositories Processed**: {processed_repos}\n"
        content += f"- **Files Scanned**: {total_files}\n"
        content += f"- **Total Symbols Extracted**: {total_symbols}\n\n"

        content += "## Symbol Extraction Results\n\n"

        for symbol_type, symbol_list in symbols.items():
            if symbol_list:
                content += f"### {symbol_type.replace('_', ' ').title()}\n\n"
                content += f"**Count**: {len(symbol_list)}\n\n"

                # Show sample symbols (up to 10)
                content += "**Sample Symbols**:\n"
                for symbol in symbol_list[:10]:
                    symbol_name = symbol.get("name", "unknown")
                    symbol_file = symbol.get("file", "unknown")
                    content += f"- `{symbol_name}` ({symbol_file})\n"

                if len(symbol_list) > 10:
                    content += f"- ... and {len(symbol_list) - 10} more\n"

                content += "\n"

        return Report(name="scan_report", content=content)

    def _add_symbols_to_graph(
        self,
        symbols: Dict[str, List[Dict[str, Any]]],
        context: ExecutionContext,
    ) -> None:
        """Add extracted symbols to the context graph.

        Args:
            symbols: Dictionary of extracted symbols.
            context: ExecutionContext with graph.
        """
        symbol_type_map = {
            "classes": NodeType.CLASS,
            "methods": NodeType.METHOD,
            "endpoints": NodeType.ENDPOINT,
            "consumers": NodeType.CONSUMER,
            "producers": NodeType.PRODUCER,
            "schedulers": NodeType.SCHEDULER,
            "configurations": NodeType.CONFIG_FILE,
            "databases": NodeType.DATABASE,
            "middleware_topics": NodeType.MIDDLEWARE_TOPIC,
            "external_apis": NodeType.EXTERNAL_API,
        }

        for symbol_category, node_type in symbol_type_map.items():
            for symbol in symbols.get(symbol_category, []):
                try:
                    node = Node(
                        id=symbol.get("id", "unknown"),
                        type=node_type,
                        name=symbol.get("name", "unknown"),
                        repository=symbol.get("repository"),
                        path=symbol.get("file"),
                        language=self._detect_language_from_file(symbol.get("file", "")),
                        framework_role=symbol.get("framework"),
                        attributes=symbol,
                    )
                    context.graph.add_node(node)
                except Exception as e:
                    self.logger.debug(f"Error adding node for symbol {symbol}: {e}")

    def _detect_language_from_file(self, file_path: str) -> Optional[str]:
        """Detect language from file path string.

        Args:
            file_path: File path string.

        Returns:
            Language identifier or None.
        """
        path = Path(file_path)
        return self._detect_language(path)
