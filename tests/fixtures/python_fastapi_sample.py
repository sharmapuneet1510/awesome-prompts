"""Test fixtures for Python FastAPI sample projects."""

from pathlib import Path
import tempfile
from typing import Optional


class PythonFastAPISample:
    """Generate sample Python FastAPI project for testing."""

    @staticmethod
    def create_sample_project(
        tmpdir: Optional[Path] = None, with_tests: bool = True
    ) -> Path:
        """
        Create a sample Python FastAPI project.

        Args:
            tmpdir: Base directory (uses temp if None)
            with_tests: Include test files

        Returns:
            Path to project root
        """
        if tmpdir is None:
            tmpdir = Path(tempfile.mkdtemp())

        # Create directory structure
        app_dir = tmpdir / "app"
        app_dir.mkdir(exist_ok=True)

        if with_tests:
            (tmpdir / "tests").mkdir(exist_ok=True)

        # Main app file
        main_file = app_dir / "main.py"
        main_file.write_text(
            '''"""Main FastAPI application."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services import UserService
from app.database import Database

app = FastAPI(title="User API", version="1.0.0")

class UserRequest(BaseModel):
    """User request model."""
    name: str
    email: str

class UserResponse(BaseModel):
    """User response model."""
    id: int
    name: str
    email: str

user_service = UserService()

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await Database.initialize()

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID."""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users", response_model=UserResponse)
async def create_user(request: UserRequest):
    """Create a new user."""
    user = user_service.create_user(request.name, request.email)
    return user
'''
        )

        # Models file
        models_file = app_dir / "models.py"
        models_file.write_text(
            '''"""Data models."""

from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """User model."""
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
'''
        )

        # Service file
        service_file = app_dir / "services.py"
        service_file.write_text(
            '''"""Business logic services."""

from typing import Optional, List
from app.models import User
from app.database import Database

class UserService:
    """User service with business logic."""

    def __init__(self):
        self.db = Database()

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID from database."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        user = User(name=name, email=email)
        return self.db.add(user)

    def list_users(self) -> List[User]:
        """List all users."""
        return self.db.query(User).all()

    def update_user(self, user_id: int, name: str, email: str) -> User:
        """Update existing user."""
        user = self.get_user(user_id)
        if user:
            user.name = name
            user.email = email
            self.db.update(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_user(user_id)
        if user:
            self.db.delete(user)
            return True
        return False
'''
        )

        # Database file
        db_file = app_dir / "database.py"
        db_file.write_text(
            '''"""Database connection and ORM."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

class Database:
    """Database connection manager."""

    _instance: Optional["Database"] = None
    _engine = None
    _session_local = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(cls, database_url: str = "sqlite:///./test.db"):
        """Initialize database connection."""
        cls._engine = create_engine(database_url)
        cls._session_local = sessionmaker(bind=cls._engine)

    @classmethod
    def get_session(cls):
        """Get database session."""
        return cls._session_local()

    def query(self, model):
        """Query database."""
        return self.get_session().query(model)

    def add(self, obj):
        """Add object to database."""
        session = self.get_session()
        session.add(obj)
        session.commit()
        return obj

    def update(self, obj):
        """Update object in database."""
        session = self.get_session()
        session.merge(obj)
        session.commit()

    def delete(self, obj):
        """Delete object from database."""
        session = self.get_session()
        session.delete(obj)
        session.commit()
'''
        )

        # __init__ file
        init_file = app_dir / "__init__.py"
        init_file.write_text('"""FastAPI application package."""\n')

        # Test files
        if with_tests:
            test_main = tmpdir / "tests" / "test_main.py"
            test_main.write_text(
                '''"""Tests for main API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 404

def test_create_user():
    """Test user creation."""
    response = client.post(
        "/api/users",
        json={"name": "John Doe", "email": "john@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"

def test_get_user():
    """Test getting user by ID."""
    response = client.get("/api/users/1")
    assert response.status_code == 200

def test_get_nonexistent_user():
    """Test getting nonexistent user."""
    response = client.get("/api/users/9999")
    assert response.status_code == 404
'''
            )

            test_services = tmpdir / "tests" / "test_services.py"
            test_services.write_text(
                '''"""Tests for business logic services."""

import pytest
from app.services import UserService

@pytest.fixture
def service():
    return UserService()

def test_create_user(service):
    """Test user creation."""
    user = service.create_user("Jane Doe", "jane@example.com")
    assert user.name == "Jane Doe"
    assert user.email == "jane@example.com"

def test_get_user(service):
    """Test getting user."""
    user = service.create_user("John", "john@example.com")
    retrieved = service.get_user(user.id)
    assert retrieved.name == "John"

def test_delete_user(service):
    """Test deleting user."""
    user = service.create_user("Delete Me", "delete@example.com")
    result = service.delete_user(user.id)
    assert result is True
'''
            )

            test_init = tmpdir / "tests" / "__init__.py"
            test_init.write_text('"""Test package."""\n')

        # requirements.txt
        requirements = tmpdir / "requirements.txt"
        requirements.write_text(
            """fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.4.0
pydantic-settings==2.0.0
email-validator==2.1.0
sqlalchemy==2.0.0
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.25.0
"""
        )

        # pyproject.toml
        pyproject = tmpdir / "pyproject.toml"
        pyproject.write_text(
            """[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fastapi-user-api"
version = "1.0.0"
description = "FastAPI user management API"
requires-python = ">=3.9"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.4.0",
    "sqlalchemy>=2.0.0",
]
"""
        )

        return tmpdir
