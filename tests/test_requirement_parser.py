import pytest
from tools.requirement_parser import RequirementParser

def test_parse_basic_requirement():
    """Test parsing plain-text requirement into structured data."""
    requirement_txt = """
    We need a user management system with login and registration.
    Use React for frontend, Python FastAPI for backend, PostgreSQL for database.
    Support JWT authentication. Timeline: 2 weeks.
    """

    parser = RequirementParser(requirement_txt)
    result = parser.parse()

    assert result['project_name'] is not None
    assert 'react' in result['tech_stack']['frontend'].lower()
    assert 'fastapi' in result['tech_stack']['backend'].lower()
    assert 'postgresql' in result['tech_stack']['database'].lower()
    assert 'jwt' in str(result['features']).lower()
    assert result['timeline'] == '2 weeks'

def test_generate_requirement_md():
    """Test generating requirement.md from parsed data."""
    requirement_txt = """
    User authentication system with JWT tokens.
    React + Python FastAPI + PostgreSQL.
    """

    parser = RequirementParser(requirement_txt)
    md_content = parser.to_markdown()

    assert '# Project:' in md_content
    assert '## Vision' in md_content
    assert '## Tech Stack' in md_content
    assert '## Features' in md_content
    assert '---' in md_content  # frontmatter
