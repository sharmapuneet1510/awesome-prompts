import pytest
import json
import tempfile
import os
from pathlib import Path
from tools.context_builder import ContextBuilder


def test_build_context_for_new_project():
    """Test building context for a new project with basic requirements."""
    requirement_data = {
        'project_name': 'User Auth System',
        'vision': 'A secure authentication system for managing user login and registration.',
        'tech_stack': {
            'frontend': 'React 18+',
            'backend': 'Python/FastAPI',
            'database': 'PostgreSQL'
        },
        'features': ['user login', 'user registration', 'JWT authentication', 'email verification'],
        'success_criteria': [
            '[ ] User can register with email',
            '[ ] User can login with credentials',
            '[ ] JWT tokens are generated and validated',
            '[ ] Password is securely hashed'
        ],
        'timeline': '2 weeks',
        'constraints': ['Team: 2 people']
    }

    builder = ContextBuilder(requirement_data)
    context = builder.build()

    # Verify basic structure
    assert context['project_name'] == 'User Auth System'
    assert 'created_at' in context
    assert 'tech_stack' in context
    assert 'file_structure' in context
    assert 'api_endpoints' in context
    assert 'database' in context
    assert 'dependencies' in context
    assert 'test_coverage' in context

    # Verify tech stack is preserved
    assert context['tech_stack']['backend'] == 'Python/FastAPI'
    assert context['tech_stack']['frontend'] == 'React 18+'
    assert context['tech_stack']['database'] == 'PostgreSQL'

    # Verify file structure is created
    assert isinstance(context['file_structure'], dict)
    assert 'backend' in context['file_structure'] or 'src' in context['file_structure']

    # Verify test coverage exists
    assert 'unit_tests' in context['test_coverage']
    assert 'integration_tests' in context['test_coverage']


def test_context_includes_api_endpoints():
    """Test that context builder infers API endpoints from features."""
    requirement_data = {
        'project_name': 'E-commerce API',
        'vision': 'An e-commerce platform API.',
        'tech_stack': {
            'frontend': 'React 18+',
            'backend': 'Python/FastAPI',
            'database': 'PostgreSQL'
        },
        'features': [
            'user login',
            'user registration',
            'product listing',
            'shopping cart management',
            'order checkout'
        ],
        'success_criteria': [],
        'timeline': '1 month',
        'constraints': []
    }

    builder = ContextBuilder(requirement_data)
    context = builder.build()

    # Verify API endpoints are inferred
    assert 'api_endpoints' in context
    api_endpoints = context['api_endpoints']

    # Check for auth endpoints
    auth_endpoints = [ep for ep in api_endpoints if 'auth' in ep.get('path', '').lower() or 'login' in ep.get('path', '').lower()]
    assert len(auth_endpoints) > 0, "Should have auth/login endpoints"

    # Check for product endpoints
    product_endpoints = [ep for ep in api_endpoints if 'product' in ep.get('path', '').lower()]
    assert len(product_endpoints) > 0, "Should have product endpoints"

    # Check for order endpoints
    order_endpoints = [ep for ep in api_endpoints if 'order' in ep.get('path', '').lower() or 'checkout' in ep.get('path', '').lower()]
    assert len(order_endpoints) > 0, "Should have order/checkout endpoints"

    # Verify endpoint structure
    for endpoint in api_endpoints:
        assert 'path' in endpoint
        assert 'method' in endpoint
        assert endpoint['method'] in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']


def test_context_database_schema():
    """Test that database schema is correctly inferred from features."""
    requirement_data = {
        'project_name': 'Activity Tracker',
        'vision': 'Track user activities and generate reports.',
        'tech_stack': {
            'frontend': 'React 18+',
            'backend': 'Python/FastAPI',
            'database': 'PostgreSQL'
        },
        'features': [
            'user authentication',
            'activity logging',
            'user profile management',
            'activity reporting'
        ],
        'success_criteria': [],
        'timeline': '3 weeks',
        'constraints': []
    }

    builder = ContextBuilder(requirement_data)
    context = builder.build()

    # Verify database structure
    assert 'database' in context
    db_config = context['database']

    # Check for tables
    assert 'tables' in db_config
    tables = db_config['tables']

    # Should have users table (from authentication)
    users_table = [t for t in tables if t['name'].lower() == 'users']
    assert len(users_table) > 0, "Should have users table for authentication"

    # Should have activity logs table (from activity logging)
    activity_table = [t for t in tables if 'activity' in t['name'].lower() or 'log' in t['name'].lower()]
    assert len(activity_table) > 0, "Should have activity/logs table for activity tracking"

    # Verify table structure includes columns
    for table in tables:
        assert 'name' in table
        assert 'columns' in table
        assert isinstance(table['columns'], list)
        assert len(table['columns']) > 0

        # Verify columns have required fields
        for column in table['columns']:
            assert 'name' in column
            assert 'type' in column
