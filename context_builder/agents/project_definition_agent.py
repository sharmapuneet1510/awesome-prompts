"""Project Definition Agent for detecting project structure and tech stack."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

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


class ProjectDefinitionAgent(BaseAgent):
    """Detect project structure, tech stack, and entry points.

    Responsibilities:
    - Detect repositories and modules in workspace
    - Detect language and framework (Java/Spring, Python/FastAPI, etc.)
    - Detect service/library/UI/batch type
    - Identify entry points (APIs, consumers, schedulers)
    - Generate first-draft business purpose
    - Return AgentOutput with project config

    Attributes:
        DEPENDENCY_FILES: Map of dependency files to language/platform
        CODE_EXTENSIONS: Set of code file extensions to search for
    """

    DEPENDENCY_FILES = {
        "requirements.txt": "python",
        "setup.py": "python",
        "pyproject.toml": "python",
        "Pipfile": "python",
        "poetry.lock": "python",
        "package.json": "nodejs",
        "pom.xml": "java",
        "build.gradle": "java",
        "build.gradle.kts": "java",
        "go.mod": "go",
        "Cargo.toml": "rust",
        "Gemfile": "ruby",
    }

    CODE_EXTENSIONS = {".py", ".java", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs"}

    FRAMEWORK_MARKERS = {
        "python": {
            "django": ["django", "django.db"],
            "fastapi": ["fastapi"],
            "flask": ["flask"],
            "pytest": ["pytest"],
        },
        "java": {
            "spring_boot": ["spring-boot", "spring-boot-starter"],
            "spring": ["spring-core", "spring-context"],
            "junit": ["junit"],
            "hibernate": ["hibernate"],
        },
        "nodejs": {
            "react": ["react"],
            "vue": ["vue"],
            "angular": ["@angular"],
            "express": ["express"],
            "fastify": ["fastify"],
            "jest": ["jest"],
        },
    }

    def __init__(self):
        """Initialize the ProjectDefinitionAgent."""
        super().__init__(name="ProjectDefinitionAgent")

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Detect project structure and tech stack.

        Args:
            context: ExecutionContext containing workspace and scan configs.

        Returns:
            AgentOutput with detected projects and tech stack information.
        """
        if not self.validate_context(context):
            return AgentOutput(
                status="error",
                message="Invalid execution context",
                errors=["ExecutionContext is None"],
            )

        try:
            # Detect projects from workspace configuration
            projects = []
            confidence_levels = {}

            if context.workspace_config and context.workspace_config.repositories:
                for repo_config in context.workspace_config.repositories:
                    project = self._analyze_project(repo_config, context)
                    if project:
                        projects.append(project)
                        confidence_levels[project["id"]] = project.get(
                            "confidence", 0.5
                        )

            # Generate report with findings
            report = self._generate_report(projects, confidence_levels)
            context.reports["project_definition"] = report

            # Add nodes to graph for each detected project
            self._add_project_nodes_to_graph(projects, context)

            self.logger.info(f"Detected {len(projects)} projects")

            return AgentOutput(
                status="success",
                message=f"Detected {len(projects)} projects with tech stack analysis",
                artifacts=[report.file_path] if report.file_path else [],
                metrics={
                    "projects_detected": len(projects),
                    "avg_confidence": sum(confidence_levels.values())
                    / len(confidence_levels)
                    if confidence_levels
                    else 0.0,
                    "confidence_levels": confidence_levels,
                },
            )
        except Exception as e:
            self.logger.error(f"Error in ProjectDefinitionAgent: {e}", exc_info=True)
            return AgentOutput(
                status="error",
                message=str(e),
                errors=[str(e)],
            )

    def _analyze_project(
        self, repo_config: Dict[str, Any], context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single repository to detect project properties.

        Args:
            repo_config: Repository configuration from workspace config.
            context: ExecutionContext for access to scan config.

        Returns:
            Dictionary with project configuration or None if analysis fails.
        """
        repo_id = repo_config.get("id", "unknown")
        repo_name = repo_config.get("name", "")
        local_path = repo_config.get("local_path")

        if not local_path:
            self.logger.warning(f"Repository {repo_id} has no local_path")
            return None

        path = Path(local_path)
        if not path.exists():
            self.logger.warning(f"Repository path does not exist: {local_path}")
            return None

        # Detect tech stack
        tech_stack = self._detect_tech_stack(path)
        detected_language = self._get_primary_language(tech_stack)

        # Detect service type
        service_type = self._detect_service_type(path, tech_stack, detected_language)

        # Detect entry points
        entry_points = self._detect_entry_points(
            path, detected_language, service_type, tech_stack
        )

        # Generate business purpose (basic)
        business_purpose = self._generate_business_purpose(
            repo_name, service_type, tech_stack
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            tech_stack, service_type, entry_points
        )

        return {
            "id": repo_id,
            "name": repo_name,
            "path": local_path,
            "language": detected_language,
            "type": service_type,
            "tech_stack": tech_stack,
            "entry_points": entry_points,
            "business_purpose": business_purpose,
            "confidence": confidence,
        }

    def _detect_tech_stack(self, path: Path) -> Dict[str, List[str]]:
        """Detect technology stack from dependency files and code.

        Args:
            path: Path to project root.

        Returns:
            Dictionary with detected technologies organized by language.
        """
        tech_stack = {}

        # Check each dependency file
        for dep_file, language in self.DEPENDENCY_FILES.items():
            dep_path = path / dep_file
            if dep_path.exists():
                deps = self._extract_dependencies(dep_path, language)
                if deps:
                    if language not in tech_stack:
                        tech_stack[language] = []
                    tech_stack[language].extend(deps)

        # Detect frameworks from imports if no dependencies found
        for language in ["python", "java", "nodejs"]:
            if language not in tech_stack:
                code_files = self._find_code_files(path, language)
                if code_files:
                    frameworks = self._detect_frameworks_from_code(
                        code_files, language
                    )
                    if frameworks:
                        tech_stack[language] = frameworks

        return tech_stack

    def _extract_dependencies(self, dep_file: Path, language: str) -> List[str]:
        """Extract dependencies from a dependency file.

        Args:
            dep_file: Path to dependency file.
            language: Language/platform type.

        Returns:
            List of extracted dependency names.
        """
        deps = []

        try:
            if dep_file.name == "requirements.txt":
                deps = self._extract_python_deps(dep_file)
            elif dep_file.name == "package.json":
                deps = self._extract_node_deps(dep_file)
            elif dep_file.name in ("pom.xml", "build.gradle", "build.gradle.kts"):
                deps = self._extract_java_deps(dep_file)
            elif dep_file.name == "pyproject.toml":
                deps = self._extract_pyproject_deps(dep_file)
        except Exception as e:
            self.logger.debug(f"Error extracting dependencies from {dep_file}: {e}")

        return deps

    def _extract_python_deps(self, req_file: Path) -> List[str]:
        """Extract Python dependencies from requirements.txt.

        Args:
            req_file: Path to requirements.txt.

        Returns:
            List of package names.
        """
        deps = []
        try:
            content = req_file.read_text()
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (before ==, >=, etc.)
                    package = re.split(r"[=!<>]", line)[0].strip()
                    if package:
                        deps.append(package.lower())
        except Exception as e:
            self.logger.debug(f"Error reading requirements.txt: {e}")

        return deps

    def _extract_node_deps(self, package_json: Path) -> List[str]:
        """Extract Node dependencies from package.json.

        Args:
            package_json: Path to package.json.

        Returns:
            List of package names.
        """
        deps = []
        try:
            content = json.loads(package_json.read_text())
            all_deps = {}

            # Merge dependencies and devDependencies
            if "dependencies" in content:
                all_deps.update(content["dependencies"])
            if "devDependencies" in content:
                all_deps.update(content["devDependencies"])

            deps = [dep.lower() for dep in all_deps.keys()]
        except Exception as e:
            self.logger.debug(f"Error reading package.json: {e}")

        return deps

    def _extract_java_deps(self, build_file: Path) -> List[str]:
        """Extract Java dependencies from pom.xml or build.gradle.

        Args:
            build_file: Path to pom.xml or build.gradle.

        Returns:
            List of artifact names.
        """
        deps = []
        try:
            if build_file.name == "pom.xml":
                content = build_file.read_text()
                # Simple regex to find artifact IDs
                artifact_pattern = r"<artifactId>([^<]+)</artifactId>"
                matches = re.findall(artifact_pattern, content)
                deps = [m.lower() for m in matches]
            else:
                # For gradle, do simple string matching
                content = build_file.read_text()
                if "spring" in content.lower():
                    deps.append("spring-boot")
                if "junit" in content.lower():
                    deps.append("junit")
                if "hibernate" in content.lower():
                    deps.append("hibernate")
        except Exception as e:
            self.logger.debug(f"Error reading Java build file: {e}")

        return deps

    def _extract_pyproject_deps(self, pyproject_file: Path) -> List[str]:
        """Extract dependencies from pyproject.toml.

        Args:
            pyproject_file: Path to pyproject.toml.

        Returns:
            List of package names.
        """
        deps = []
        try:
            content = pyproject_file.read_text()
            # Simple regex to find package names in dependencies
            pattern = r'(?:dependencies|requires)\s*=\s*\[(.*?)\]'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                deps_str = match.group(1)
                for dep in re.findall(r'"([^"]+)"', deps_str):
                    pkg_name = re.split(r"[=!<>]", dep)[0].strip()
                    if pkg_name:
                        deps.append(pkg_name.lower())
        except Exception as e:
            self.logger.debug(f"Error reading pyproject.toml: {e}")

        return deps

    def _find_code_files(self, path: Path, language: str) -> List[Path]:
        """Find code files for a specific language.

        Args:
            path: Root path to search.
            language: Language identifier.

        Returns:
            List of code file paths.
        """
        extensions = []
        if language == "python":
            extensions = [".py"]
        elif language == "java":
            extensions = [".java"]
        elif language == "nodejs":
            extensions = [".js", ".ts", ".tsx", ".jsx"]

        code_files = []
        for ext in extensions:
            for file_path in path.rglob(f"*{ext}"):
                # Skip common exclusion directories
                if any(
                    part.startswith(".")
                    for part in file_path.parts
                ):
                    continue
                if any(
                    skip in file_path.parts
                    for skip in ["node_modules", "__pycache__", "dist", "build", "target"]
                ):
                    continue
                code_files.append(file_path)

        return code_files[:20]  # Limit to first 20 files for performance

    def _detect_frameworks_from_code(
        self, code_files: List[Path], language: str
    ) -> List[str]:
        """Detect frameworks by analyzing code imports/requires.

        Args:
            code_files: List of code file paths to analyze.
            language: Language identifier.

        Returns:
            List of detected framework names.
        """
        frameworks = []

        try:
            for code_file in code_files[:5]:  # Check first 5 files
                content = code_file.read_text(errors="ignore")

                # Check for framework markers in code
                if language in self.FRAMEWORK_MARKERS:
                    for framework, markers in self.FRAMEWORK_MARKERS[
                        language
                    ].items():
                        for marker in markers:
                            if marker in content:
                                if framework not in frameworks:
                                    frameworks.append(framework)
        except Exception as e:
            self.logger.debug(f"Error detecting frameworks from code: {e}")

        return frameworks

    def _get_primary_language(self, tech_stack: Dict[str, List[str]]) -> str:
        """Get the primary language from detected tech stack.

        Args:
            tech_stack: Dictionary of detected technologies.

        Returns:
            Primary language identifier.
        """
        language_priority = ["java", "python", "nodejs", "go", "rust"]
        for lang in language_priority:
            if lang in tech_stack and tech_stack[lang]:
                return lang
        return "unknown"

    def _detect_service_type(
        self, path: Path, tech_stack: Dict[str, List[str]], language: str
    ) -> str:
        """Detect whether project is a service, library, UI, or batch.

        Args:
            path: Root path of project.
            tech_stack: Detected technology stack.
            language: Primary language.

        Returns:
            Service type: 'service', 'library', 'ui', or 'batch'.
        """
        # Check for framework indicators
        all_tech = []
        for techs in tech_stack.values():
            all_tech.extend(techs)

        all_tech_str = " ".join(all_tech).lower()

        # UI indicators
        if any(
            tech in all_tech_str
            for tech in ["react", "vue", "angular", "nextjs", "nuxt"]
        ):
            return "ui"

        # Service indicators
        if any(
            tech in all_tech_str
            for tech in ["spring-boot", "fastapi", "express", "fastify", "django"]
        ):
            return "service"

        # Batch indicators
        config_file = path / "application.properties"
        if config_file.exists():
            content = config_file.read_text()
            if "batch" in content.lower() or "scheduler" in content.lower():
                return "batch"

        # Check for main/entry classes
        main_files = list(path.glob("**/main.py")) + list(
            path.glob("**/Main.java")
        )
        if main_files:
            return "batch"

        # Default to service if unclear
        return "service"

    def _detect_entry_points(
        self, path: Path, language: str, service_type: str, tech_stack: Dict[str, List[str]]
    ) -> List[Dict[str, str]]:
        """Detect entry points (APIs, consumers, schedulers).

        Args:
            path: Root path of project.
            language: Primary language.
            service_type: Type of service.
            tech_stack: Detected technologies.

        Returns:
            List of detected entry points.
        """
        entry_points = []

        try:
            if language == "java":
                entry_points.extend(self._detect_java_entry_points(path))
            elif language == "python":
                entry_points.extend(self._detect_python_entry_points(path))
            elif language == "nodejs":
                entry_points.extend(self._detect_nodejs_entry_points(path))
        except Exception as e:
            self.logger.debug(f"Error detecting entry points: {e}")

        return entry_points

    def _detect_java_entry_points(self, path: Path) -> List[Dict[str, str]]:
        """Detect Java entry points (controllers, consumers, schedulers).

        Args:
            path: Root path of project.

        Returns:
            List of entry points.
        """
        entry_points = []

        try:
            # Look for Spring controller annotations
            for java_file in path.rglob("*.java"):
                if any(skip in java_file.parts for skip in ["target", "test"]):
                    continue

                content = java_file.read_text(errors="ignore")

                if "@RestController" in content or "@Controller" in content:
                    class_match = re.search(r"public class (\w+)", content)
                    if class_match:
                        entry_points.append(
                            {
                                "type": "controller",
                                "name": class_match.group(1),
                                "file": str(java_file.relative_to(path)),
                            }
                        )

                if "@JmsListener" in content or "@KafkaListener" in content:
                    class_match = re.search(r"public class (\w+)", content)
                    if class_match:
                        entry_points.append(
                            {
                                "type": "consumer",
                                "name": class_match.group(1),
                                "file": str(java_file.relative_to(path)),
                            }
                        )

                if "@Scheduled" in content:
                    method_match = re.search(r"@Scheduled.*?\npublic void (\w+)", content, re.DOTALL)
                    if method_match:
                        entry_points.append(
                            {
                                "type": "scheduler",
                                "name": method_match.group(1),
                                "file": str(java_file.relative_to(path)),
                            }
                        )
        except Exception as e:
            self.logger.debug(f"Error detecting Java entry points: {e}")

        return entry_points

    def _detect_python_entry_points(self, path: Path) -> List[Dict[str, str]]:
        """Detect Python entry points (FastAPI routes, Flask routes).

        Args:
            path: Root path of project.

        Returns:
            List of entry points.
        """
        entry_points = []

        try:
            # Look for FastAPI/Flask route definitions
            for py_file in path.rglob("*.py"):
                if any(skip in py_file.parts for skip in ["__pycache__", "test", "venv"]):
                    continue

                content = py_file.read_text(errors="ignore")

                if "@app.get" in content or "@app.post" in content:
                    route_matches = re.findall(
                        r'@app\.(get|post|put|delete|patch)\("([^"]+)"\)\s*\ndef\s+(\w+)',
                        content,
                    )
                    for method, route, func in route_matches:
                        entry_points.append(
                            {
                                "type": "endpoint",
                                "name": f"{method.upper()} {route}",
                                "function": func,
                                "file": str(py_file.relative_to(path)),
                            }
                        )

                if "Celery" in content or "@shared_task" in content:
                    task_matches = re.findall(r"@.*task\s*\ndef\s+(\w+)", content)
                    for task in task_matches:
                        entry_points.append(
                            {
                                "type": "task",
                                "name": task,
                                "file": str(py_file.relative_to(path)),
                            }
                        )
        except Exception as e:
            self.logger.debug(f"Error detecting Python entry points: {e}")

        return entry_points

    def _detect_nodejs_entry_points(self, path: Path) -> List[Dict[str, str]]:
        """Detect Node.js entry points (Express routes, Next.js pages).

        Args:
            path: Root path of project.

        Returns:
            List of entry points.
        """
        entry_points = []

        try:
            # Look for Express/Next.js route definitions
            for ts_file in path.rglob("*.{ts,js}"):
                if any(skip in ts_file.parts for skip in ["node_modules", "dist", ".next"]):
                    continue

                try:
                    content = ts_file.read_text(errors="ignore")

                    # Express routes
                    if "app.get" in content or "app.post" in content:
                        route_matches = re.findall(
                            r"app\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]",
                            content,
                        )
                        for method, route in route_matches:
                            entry_points.append(
                                {
                                    "type": "endpoint",
                                    "name": f"{method.upper()} {route}",
                                    "file": str(ts_file.relative_to(path)),
                                }
                            )

                    # Next.js pages
                    if "pages/" in str(ts_file) or "app/" in str(ts_file):
                        relative = str(ts_file.relative_to(path))
                        if relative.startswith("pages/") or relative.startswith("app/"):
                            entry_points.append(
                                {
                                    "type": "page",
                                    "name": relative,
                                    "file": relative,
                                }
                            )
                except Exception:
                    pass
        except Exception as e:
            self.logger.debug(f"Error detecting Node.js entry points: {e}")

        return entry_points

    def _generate_business_purpose(
        self, repo_name: str, service_type: str, tech_stack: Dict[str, List[str]]
    ) -> str:
        """Generate a first-draft business purpose for the project.

        Args:
            repo_name: Repository name.
            service_type: Type of service.
            tech_stack: Detected technologies.

        Returns:
            Business purpose description.
        """
        purpose = f"This is a {service_type}"

        if service_type == "ui":
            purpose += " application providing user interface"
        elif service_type == "service":
            purpose += " that provides API endpoints"
        elif service_type == "batch":
            purpose += " that runs batch jobs or scheduled tasks"
        elif service_type == "library":
            purpose += " providing reusable code components"

        # Add tech stack info
        tech_list = []
        for language, techs in tech_stack.items():
            if techs:
                tech_list.append(f"{language}: {', '.join(techs[:3])}")

        if tech_list:
            purpose += f". Built with {'; '.join(tech_list)}"

        return purpose

    def _calculate_confidence(
        self, tech_stack: Dict[str, List[str]], service_type: str,
        entry_points: List[Dict[str, str]]
    ) -> float:
        """Calculate confidence level for the analysis.

        Args:
            tech_stack: Detected technologies.
            service_type: Type of service.
            entry_points: Detected entry points.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        confidence = 0.5  # Base confidence

        # Increase confidence with detected tech stack
        if tech_stack:
            confidence += 0.15

        # Increase confidence if service type is not 'unknown'
        if service_type != "unknown":
            confidence += 0.15

        # Increase confidence with detected entry points
        if entry_points:
            confidence += 0.2 * min(len(entry_points) / 5, 1.0)

        # Cap at 1.0
        return min(confidence, 1.0)

    def _generate_report(
        self, projects: List[Dict[str, Any]], confidence_levels: Dict[str, float]
    ) -> Report:
        """Generate a report with project definition findings.

        Args:
            projects: List of detected projects.
            confidence_levels: Confidence scores per project.

        Returns:
            Report object with findings.
        """
        content = "# Project Definition Report\n\n"

        if not projects:
            content += "No projects detected in the workspace.\n"
            return Report(name="project_definition", content=content)

        content += f"## Summary\n\n"
        content += f"Detected **{len(projects)}** project(s) with analysis:\n\n"

        for project in projects:
            content += f"### {project['name']} ({project['id']})\n\n"
            content += f"- **Language**: {project['language']}\n"
            content += f"- **Type**: {project['type']}\n"
            content += f"- **Confidence**: {project['confidence']:.1%}\n"
            content += f"- **Business Purpose**: {project['business_purpose']}\n"
            content += f"- **Path**: `{project['path']}`\n\n"

            if project.get("tech_stack"):
                content += "**Tech Stack**:\n"
                for language, techs in project["tech_stack"].items():
                    content += (
                        f"  - {language}: {', '.join(techs[:5])}\n"
                    )
                content += "\n"

            if project.get("entry_points"):
                content += "**Entry Points**:\n"
                for ep in project["entry_points"][:5]:
                    content += f"  - {ep['type']}: {ep.get('name', 'unknown')}\n"
                content += "\n"

        return Report(name="project_definition", content=content)

    def _add_project_nodes_to_graph(
        self, projects: List[Dict[str, Any]], context: ExecutionContext
    ) -> None:
        """Add detected projects as nodes to the context graph.

        Args:
            projects: List of detected projects.
            context: ExecutionContext with graph.
        """
        for project in projects:
            # Add repository node
            repo_node = Node(
                id=project["id"],
                type=NodeType.REPOSITORY,
                name=project["name"],
                path=project["path"],
                language=project["language"],
                framework_role=project["type"],
                attributes={
                    "tech_stack": project.get("tech_stack", {}),
                    "business_purpose": project.get("business_purpose", ""),
                    "confidence": project.get("confidence", 0.0),
                },
            )
            context.graph.add_node(repo_node)

            # Add entry point nodes
            for ep in project.get("entry_points", []):
                ep_type = NodeType.ENDPOINT
                if ep.get("type") == "consumer":
                    ep_type = NodeType.CONSUMER
                elif ep.get("type") == "scheduler":
                    ep_type = NodeType.SCHEDULER

                ep_node = Node(
                    id=f"{project['id']}-{ep.get('name', 'unknown').replace(' ', '_').replace('/', '-')}",
                    type=ep_type,
                    name=ep.get("name", "unknown"),
                    repository=project["id"],
                    path=ep.get("file"),
                )
                context.graph.add_node(ep_node)

                # Add edge from repository to entry point
                edge = Edge(
                    source=project["id"],
                    target=ep_node.id,
                    type=EdgeType.CONTAINS,
                )
                context.graph.add_edge(edge)
