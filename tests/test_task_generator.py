import pytest
from pathlib import Path
from tools.task_generator import TaskGenerator


def test_generate_tasks_from_requirement():
    """Test that 5 tasks are generated with correct IDs."""
    requirement_data = {
        'project_name': 'User Management System',
        'vision': 'A scalable user management system with authentication and role-based access control.',
        'tech_stack': {
            'frontend': 'React 18+',
            'backend': 'Python/FastAPI',
            'database': 'PostgreSQL',
        },
        'features': ['login', 'registration', 'user profiles', 'role management'],
        'timeline': '2 weeks',
        'constraints': [],
    }

    generator = TaskGenerator(requirement_data)
    tasks = generator.generate()

    # Verify 5 tasks are generated
    assert len(tasks) == 5

    # Verify task IDs are correct
    expected_ids = ['01', '02', '03', '04', '05']
    actual_ids = [task['id'] for task in tasks]
    assert actual_ids == expected_ids

    # Verify task titles
    expected_titles = [
        'Database Schema & Migrations',
        'Backend API & Services',
        'Frontend UI Components',
        'Integration Tests',
        'Deployment & CI/CD',
    ]
    actual_titles = [task['title'] for task in tasks]
    assert actual_titles == expected_titles


def test_task_spec_format():
    """Test that task specs are properly formatted."""
    requirement_data = {
        'project_name': 'User Authentication',
        'vision': 'A secure authentication system using JWT tokens.',
        'tech_stack': {
            'frontend': 'React 18+',
            'backend': 'Python/FastAPI',
            'database': 'PostgreSQL',
        },
        'features': ['login', 'registration', 'password reset'],
        'timeline': '1 week',
        'constraints': [],
    }

    generator = TaskGenerator(requirement_data)
    tasks = generator.generate()

    # Check first task (database schema)
    db_task = tasks[0]
    assert 'id' in db_task
    assert 'title' in db_task
    assert 'spec' in db_task
    assert 'skill' in db_task
    assert 'duration' in db_task

    # Verify spec format (markdown with YAML frontmatter)
    spec = db_task['spec']
    assert '---' in spec  # YAML frontmatter markers
    assert '# ' in spec  # Markdown heading
    assert 'Requirements:' in spec or 'requirements' in spec.lower()
    assert 'Acceptance Criteria:' in spec or 'acceptance criteria' in spec.lower()

    # Verify spec contains project context
    assert 'User Authentication' in spec or 'user authentication' in spec.lower()

    # Verify all 5 task specs exist and are formatted
    for task in tasks:
        assert isinstance(task['spec'], str)
        assert len(task['spec']) > 100  # Spec should have substantial content
