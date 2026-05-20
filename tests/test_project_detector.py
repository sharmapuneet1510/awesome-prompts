import pytest
import tempfile
import shutil
from pathlib import Path
from tools.project_detector import ProjectDetector


class TestProjectDetector:
    """Test suite for ProjectDetector."""

    def test_detect_new_project(self):
        """Test detection of a new project (no git, no code files)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            detector = ProjectDetector(project_path)
            result = detector.detect()

            assert result['project_type'] == 'new'
            assert result['git_exists'] is False
            assert result['existing_code'] is False
            assert result['code_files'] == []
            assert result['existing_docs'] == []
            assert result['detected_stack'] == {}
            assert isinstance(result['git_history'], dict)

    def test_detect_existing_project_with_git(self):
        """Test detection of existing project with git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create .git directory to simulate existing git repo
            git_dir = project_path / '.git'
            git_dir.mkdir()
            (git_dir / 'HEAD').write_text('ref: refs/heads/main\n')

            # Create some code files
            (project_path / 'main.py').write_text('print("hello")')
            (project_path / 'utils.py').write_text('def helper(): pass')

            # Create documentation
            (project_path / 'README.md').write_text('# Project')
            (project_path / 'ARCHITECTURE.md').write_text('# Architecture')

            detector = ProjectDetector(project_path)
            result = detector.detect()

            assert result['project_type'] == 'existing'
            assert result['git_exists'] is True
            assert result['existing_code'] is True
            assert len(result['code_files']) >= 2
            assert any('main.py' in str(f) for f in result['code_files'])
            assert any('utils.py' in str(f) for f in result['code_files'])
            assert len(result['existing_docs']) >= 2
            assert any('README.md' in str(f) for f in result['existing_docs'])
            assert any('ARCHITECTURE.md' in str(f) for f in result['existing_docs'])

    def test_extract_tech_stack_from_package_files(self):
        """Test extraction of tech stack from dependency files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create Python requirements.txt
            (project_path / 'requirements.txt').write_text(
                'fastapi==0.104.1\n'
                'sqlalchemy==2.0.0\n'
                'pydantic==2.0.0\n'
            )

            # Create Node package.json
            (project_path / 'package.json').write_text(
                '{\n'
                '  "dependencies": {\n'
                '    "react": "^18.0.0",\n'
                '    "typescript": "^5.0.0"\n'
                '  }\n'
                '}\n'
            )

            # Create Java pom.xml
            (project_path / 'pom.xml').write_text(
                '<?xml version="1.0"?>\n'
                '<project>\n'
                '  <dependencies>\n'
                '    <dependency>\n'
                '      <artifactId>spring-boot-starter-web</artifactId>\n'
                '    </dependency>\n'
                '  </dependencies>\n'
                '</project>\n'
            )

            detector = ProjectDetector(project_path)
            result = detector.detect()

            # Check Python stack
            assert 'python' in result['detected_stack']
            assert 'fastapi' in result['detected_stack']['python']
            assert 'sqlalchemy' in result['detected_stack']['python']

            # Check Node stack
            assert 'node' in result['detected_stack']
            assert 'react' in result['detected_stack']['node']
            assert 'typescript' in result['detected_stack']['node']

            # Check Java stack
            assert 'java' in result['detected_stack']
            assert 'spring-boot' in result['detected_stack']['java']
