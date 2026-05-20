import json
import re
from pathlib import Path
from typing import Dict, List, Any


class ProjectDetector:
    """Detect whether a project is new or existing and gather initial context."""

    # Code file extensions to search for
    CODE_EXTENSIONS = {'.py', '.java', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs'}

    # Documentation file patterns
    DOC_PATTERNS = ['README*', 'ARCHITECTURE*', 'DESIGN*', '*.md']

    # Dependency files
    DEPENDENCY_FILES = {
        'requirements.txt': 'python',
        'package.json': 'node',
        'pom.xml': 'java',
        'build.gradle': 'java',
        'Pipfile': 'python',
        'poetry.lock': 'python',
        'Gemfile': 'ruby',
        'go.mod': 'go',
        'Cargo.lock': 'rust',
    }

    def __init__(self, project_path: str | Path):
        """Initialize detector with a project path."""
        self.project_path = Path(project_path)

    def detect(self) -> Dict[str, Any]:
        """
        Detect project type and gather initial context.

        Returns:
            dict: Project detection results containing:
                - project_type: 'new' or 'existing'
                - git_exists: bool
                - existing_code: bool
                - code_files: list of code file paths
                - existing_docs: list of documentation file paths
                - detected_stack: dict of detected technologies
                - git_history: dict with git metadata (placeholder)
        """
        git_exists = self._check_git_exists()
        code_files = self._find_code_files()
        existing_docs = self._find_documentation()
        detected_stack = self._detect_tech_stack()
        git_history = self._analyze_git_history()

        # Determine project type based on presence of .git and code files
        existing_code = len(code_files) > 0
        project_type = 'existing' if (git_exists or existing_code) else 'new'

        return {
            'project_type': project_type,
            'git_exists': git_exists,
            'existing_code': existing_code,
            'code_files': code_files,
            'existing_docs': existing_docs,
            'detected_stack': detected_stack,
            'git_history': git_history,
        }

    def _check_git_exists(self) -> bool:
        """Check if .git directory exists in the project."""
        git_dir = self.project_path / '.git'
        return git_dir.exists() and git_dir.is_dir()

    def _find_code_files(self) -> List[str]:
        """
        Find all code files in the project.

        Returns:
            list: Relative paths to code files
        """
        code_files = []
        for ext in self.CODE_EXTENSIONS:
            # Find files with matching extension, excluding common directories
            for file_path in self.project_path.rglob(f'*{ext}'):
                # Skip hidden directories and common build/cache directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(skip in file_path.parts for skip in ['node_modules', '__pycache__', 'dist', 'build', 'target']):
                    continue

                relative_path = str(file_path.relative_to(self.project_path))
                code_files.append(relative_path)

        return sorted(code_files)

    def _find_documentation(self) -> List[str]:
        """
        Find documentation files in the project.

        Returns:
            list: Relative paths to documentation files
        """
        docs = []
        for pattern in self.DOC_PATTERNS:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(self.project_path))
                    docs.append(relative_path)

        return sorted(docs)

    def _detect_tech_stack(self) -> Dict[str, List[str]]:
        """
        Detect technology stack from dependency files.

        Returns:
            dict: Technology stack organized by language/platform
        """
        stack = {}

        # Check Python dependencies
        python_deps = self._extract_python_dependencies()
        if python_deps:
            stack['python'] = python_deps

        # Check Node dependencies
        node_deps = self._extract_node_dependencies()
        if node_deps:
            stack['node'] = node_deps

        # Check Java dependencies
        java_deps = self._extract_java_dependencies()
        if java_deps:
            stack['java'] = java_deps

        return stack

    def _extract_python_dependencies(self) -> List[str]:
        """Extract Python dependencies from requirements.txt or Poetry."""
        deps = []

        # Check requirements.txt
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            content = req_file.read_text()
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, etc.)
                    package = re.split(r'[=!<>]', line)[0].strip()
                    if package:
                        deps.append(package.lower())

        return deps

    def _extract_node_dependencies(self) -> List[str]:
        """Extract Node dependencies from package.json."""
        deps = []
        package_json = self.project_path / 'package.json'

        if package_json.exists():
            try:
                content = json.loads(package_json.read_text())
                all_deps = {}

                # Merge dependencies and devDependencies
                if 'dependencies' in content:
                    all_deps.update(content['dependencies'])
                if 'devDependencies' in content:
                    all_deps.update(content['devDependencies'])

                deps = [dep.lower() for dep in all_deps.keys()]
            except (json.JSONDecodeError, KeyError):
                pass

        return deps

    def _extract_java_dependencies(self) -> List[str]:
        """Extract Java dependencies from pom.xml."""
        deps = []
        pom_file = self.project_path / 'pom.xml'

        if pom_file.exists():
            try:
                content = pom_file.read_text()

                # Simple regex to find artifact IDs
                artifact_pattern = r'<artifactId>([^<]+)</artifactId>'
                matches = re.findall(artifact_pattern, content)

                for match in matches:
                    # Convert to more readable format (spring-boot-starter-web -> spring-boot)
                    cleaned = match.lower()
                    if 'spring-boot' in cleaned or 'spring' in cleaned:
                        if 'spring-boot' not in deps:
                            deps.append('spring-boot')
                    elif 'spring' in cleaned:
                        if 'spring' not in deps:
                            deps.append('spring')
                    else:
                        deps.append(cleaned)
            except Exception:
                pass

        return deps

    def _analyze_git_history(self) -> Dict[str, Any]:
        """
        Analyze git history (placeholder for future expansion).

        Returns:
            dict: Git history metadata
        """
        history = {
            'commits': 0,
            'branches': [],
            'last_commit': None,
            'contributors': [],
        }

        if self._check_git_exists():
            # Placeholder for actual git analysis
            # Future: use GitPython or subprocess to get real data
            pass

        return history
