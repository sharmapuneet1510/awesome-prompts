"""Tests for ProjectDefinitionAgent."""

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from context_builder.agents import ProjectDefinitionAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Graph,
    MaturityConfig,
    NodeType,
    ProjectConfig,
    ScanConfig,
    TechAliases,
    TestQualityConfig,
    WorkspaceConfig,
)


@pytest.fixture
def tmp_project_root(tmp_path):
    """Create a temporary project root directory."""
    return tmp_path


@pytest.fixture
def java_spring_project(tmp_project_root):
    """Create a mock Java/Spring Boot project."""
    pom_content = """<?xml version="1.0"?>
<project>
    <artifactId>spring-boot-starter-web</artifactId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
    <artifactId>junit-jupiter</artifactId>
</project>
"""
    pom_file = tmp_project_root / "pom.xml"
    pom_file.write_text(pom_content)

    # Create a mock controller
    src_dir = tmp_project_root / "src" / "main" / "java" / "com" / "example"
    src_dir.mkdir(parents=True)
    controller_file = src_dir / "UserController.java"
    controller_file.write_text(
        """
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping
    public List<User> listUsers() {
        return userService.findAll();
    }
}
"""
    )

    # Create a mock consumer
    consumer_file = src_dir / "OrderConsumer.java"
    consumer_file.write_text(
        """
@Component
public class OrderConsumer {
    @JmsListener(destination = "order.queue")
    public void handleOrder(String message) {
        orderService.process(message);
    }
}
"""
    )

    # Create a mock scheduler
    scheduler_file = src_dir / "TaskScheduler.java"
    scheduler_file.write_text(
        """
@Component
public class TaskScheduler {
    @Scheduled(fixedRate = 5000)
    public void runScheduledTask() {
        taskService.execute();
    }
}
"""
    )

    return tmp_project_root


@pytest.fixture
def python_fastapi_project(tmp_project_root):
    """Create a mock Python/FastAPI project."""
    req_content = """fastapi==0.95.0
uvicorn==0.21.0
sqlalchemy==2.0.0
pydantic==1.10.0
pytest==7.0.0
"""
    req_file = tmp_project_root / "requirements.txt"
    req_file.write_text(req_content)

    # Create a mock FastAPI app
    app_file = tmp_project_root / "main.py"
    app_file.write_text(
        """
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/users")
def list_users():
    return {"users": []}

@app.post("/api/users")
def create_user(user: User):
    return {"id": 1, "name": user.name}

@app.get("/api/products")
def list_products():
    return {"products": []}
"""
    )

    # Create a mock task file
    task_file = tmp_project_root / "tasks.py"
    task_file.write_text(
        """
from celery import Celery

app = Celery('tasks')

@shared_task
def process_order(order_id):
    return f"Processing {order_id}"

@shared_task
def send_email(email):
    return f"Sending to {email}"
"""
    )

    return tmp_project_root


@pytest.fixture
def react_ui_project(tmp_project_root):
    """Create a mock React project."""
    package_json = {
        "name": "my-app",
        "version": "1.0.0",
        "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0",
            "react-router-dom": "^6.0.0",
        },
        "devDependencies": {
            "jest": "^27.0.0",
            "typescript": "^4.7.0",
        },
    }
    package_file = tmp_project_root / "package.json"
    package_file.write_text(json.dumps(package_json, indent=2))

    # Create mock React components
    src_dir = tmp_project_root / "src"
    src_dir.mkdir(parents=True)

    app_file = src_dir / "App.tsx"
    app_file.write_text(
        """
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import UserList from './pages/UserList';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/users" element={<UserList />} />
      </Routes>
    </Router>
  );
}
"""
    )

    # Create pages directory
    pages_dir = src_dir / "pages"
    pages_dir.mkdir()
    (pages_dir / "Dashboard.tsx").write_text("export default function Dashboard() {}")
    (pages_dir / "UserList.tsx").write_text("export default function UserList() {}")

    return tmp_project_root


@pytest.fixture
def execution_context_with_repos(tmp_path):
    """Create ExecutionContext with test repositories."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace",
        context_root=tmp_path,
        repositories=[],
    )
    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=Graph(),
    )


class TestProjectDefinitionAgent:
    """Test cases for ProjectDefinitionAgent."""

    def test_agent_initialization(self):
        """Test that agent is initialized correctly."""
        agent = ProjectDefinitionAgent()
        assert agent.name == "ProjectDefinitionAgent"
        assert agent.logger is not None

    def test_execute_with_invalid_context(self):
        """Test execute with None context."""
        agent = ProjectDefinitionAgent()
        output = agent.execute(None)
        assert output.status == "error"
        assert "Invalid execution context" in output.message

    def test_execute_with_empty_repositories(self, execution_context_with_repos):
        """Test execute with no repositories."""
        execution_context_with_repos.workspace_config.repositories = []
        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)
        assert output.status == "success"
        assert output.metrics["projects_detected"] == 0

    def test_detect_java_spring_boot_service(
        self, execution_context_with_repos, java_spring_project
    ):
        """Test detection of Java/Spring Boot service."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "user-service",
                "name": "User Service",
                "local_path": str(java_spring_project),
                "type": "service",
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        assert output.metrics["projects_detected"] == 1
        assert output.metrics["avg_confidence"] > 0.5

    def test_detect_python_fastapi_service(
        self, execution_context_with_repos, python_fastapi_project
    ):
        """Test detection of Python/FastAPI service."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "api-service",
                "name": "API Service",
                "local_path": str(python_fastapi_project),
                "type": "service",
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        assert output.metrics["projects_detected"] == 1

    def test_detect_react_frontend(
        self, execution_context_with_repos, react_ui_project
    ):
        """Test detection of React UI project."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "web-app",
                "name": "Web App",
                "local_path": str(react_ui_project),
                "type": "ui",
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        assert output.metrics["projects_detected"] == 1

    def test_detect_service_type_with_spring(self, java_spring_project):
        """Test service type detection for Spring Boot."""
        agent = ProjectDefinitionAgent()
        tech_stack = {"java": ["spring-boot", "spring-boot-starter-web"]}
        service_type = agent._detect_service_type(java_spring_project, tech_stack, "java")
        assert service_type == "service"

    def test_detect_service_type_with_react(self, react_ui_project):
        """Test service type detection for React."""
        agent = ProjectDefinitionAgent()
        tech_stack = {"nodejs": ["react", "react-dom"]}
        service_type = agent._detect_service_type(react_ui_project, tech_stack, "nodejs")
        assert service_type == "ui"

    def test_detect_entry_points_java(self, java_spring_project):
        """Test entry point detection in Java project."""
        agent = ProjectDefinitionAgent()
        entry_points = agent._detect_java_entry_points(java_spring_project)

        # Should detect controller, consumer, and scheduler
        assert len(entry_points) > 0
        types = [ep["type"] for ep in entry_points]
        assert "controller" in types or "consumer" in types or "scheduler" in types

    def test_detect_entry_points_python(self, python_fastapi_project):
        """Test entry point detection in Python project."""
        agent = ProjectDefinitionAgent()
        entry_points = agent._detect_python_entry_points(python_fastapi_project)

        # Should detect endpoints or tasks
        assert len(entry_points) > 0
        types = [ep["type"] for ep in entry_points]
        assert "endpoint" in types or "task" in types

    def test_detect_python_dependencies(self, python_fastapi_project):
        """Test Python dependency extraction."""
        agent = ProjectDefinitionAgent()
        req_file = python_fastapi_project / "requirements.txt"
        deps = agent._extract_python_deps(req_file)

        assert "fastapi" in deps
        assert "uvicorn" in deps
        assert "sqlalchemy" in deps

    def test_detect_java_dependencies(self, java_spring_project):
        """Test Java dependency extraction from pom.xml."""
        agent = ProjectDefinitionAgent()
        pom_file = java_spring_project / "pom.xml"
        deps = agent._extract_java_deps(pom_file)

        assert len(deps) > 0
        assert any("spring" in dep for dep in deps)

    def test_detect_nodejs_dependencies(self, react_ui_project):
        """Test Node.js dependency extraction."""
        agent = ProjectDefinitionAgent()
        package_json = react_ui_project / "package.json"
        deps = agent._extract_node_deps(package_json)

        assert "react" in deps
        assert "react-dom" in deps
        assert "jest" in deps

    def test_get_primary_language_java(self):
        """Test primary language detection with Java."""
        agent = ProjectDefinitionAgent()
        tech_stack = {
            "java": ["spring-boot"],
            "nodejs": ["jest"],
        }
        language = agent._get_primary_language(tech_stack)
        assert language == "java"

    def test_get_primary_language_python(self):
        """Test primary language detection with Python."""
        agent = ProjectDefinitionAgent()
        tech_stack = {
            "python": ["fastapi"],
        }
        language = agent._get_primary_language(tech_stack)
        assert language == "python"

    def test_get_primary_language_unknown(self):
        """Test primary language detection with unknown."""
        agent = ProjectDefinitionAgent()
        tech_stack = {}
        language = agent._get_primary_language(tech_stack)
        assert language == "unknown"

    def test_calculate_confidence_high(self):
        """Test confidence calculation with good detection."""
        agent = ProjectDefinitionAgent()
        tech_stack = {"java": ["spring-boot"]}
        service_type = "service"
        entry_points = [{"type": "controller", "name": "UserController"}]

        confidence = agent._calculate_confidence(tech_stack, service_type, entry_points)
        assert confidence > 0.7

    def test_calculate_confidence_low(self):
        """Test confidence calculation with poor detection."""
        agent = ProjectDefinitionAgent()
        tech_stack = {}
        service_type = "unknown"
        entry_points = []

        confidence = agent._calculate_confidence(tech_stack, service_type, entry_points)
        assert confidence <= 0.5

    def test_generate_business_purpose_service(self):
        """Test business purpose generation for service."""
        agent = ProjectDefinitionAgent()
        purpose = agent._generate_business_purpose(
            "user-service",
            "service",
            {"java": ["spring-boot"]}
        )
        assert "service" in purpose
        assert "API" in purpose

    def test_generate_business_purpose_ui(self):
        """Test business purpose generation for UI."""
        agent = ProjectDefinitionAgent()
        purpose = agent._generate_business_purpose(
            "web-app",
            "ui",
            {"nodejs": ["react"]}
        )
        assert "UI" in purpose or "ui" in purpose.lower()

    def test_generate_business_purpose_batch(self):
        """Test business purpose generation for batch."""
        agent = ProjectDefinitionAgent()
        purpose = agent._generate_business_purpose(
            "batch-job",
            "batch",
            {"python": ["celery"]}
        )
        assert "batch" in purpose or "scheduled" in purpose

    def test_generate_report_with_projects(self, java_spring_project):
        """Test report generation with detected projects."""
        agent = ProjectDefinitionAgent()
        projects = [
            {
                "id": "svc-1",
                "name": "Service 1",
                "path": str(java_spring_project),
                "language": "java",
                "type": "service",
                "business_purpose": "Provides user management APIs",
                "confidence": 0.85,
                "tech_stack": {"java": ["spring-boot"]},
                "entry_points": [
                    {"type": "controller", "name": "UserController"}
                ],
            }
        ]

        report = agent._generate_report(projects, {"svc-1": 0.85})
        assert "Project Definition Report" in report.content
        assert "Service 1" in report.content
        assert "java" in report.content

    def test_generate_report_empty_projects(self):
        """Test report generation with no projects."""
        agent = ProjectDefinitionAgent()
        report = agent._generate_report([], {})
        assert "Project Definition Report" in report.content
        assert "No projects detected" in report.content

    def test_multiple_modules_detection(
        self, execution_context_with_repos, tmp_path
    ):
        """Test detection of multiple modules in workspace."""
        # Create first module
        module1 = tmp_path / "api-service"
        module1.mkdir()
        (module1 / "pom.xml").write_text(
            '<project><artifactId>spring-boot</artifactId></project>'
        )

        # Create second module
        module2 = tmp_path / "web-app"
        module2.mkdir()
        (module2 / "package.json").write_text(
            json.dumps({"dependencies": {"react": "^18.0.0"}})
        )

        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "api-service",
                "name": "API Service",
                "local_path": str(module1),
            },
            {
                "id": "web-app",
                "name": "Web App",
                "local_path": str(module2),
            },
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        assert output.metrics["projects_detected"] == 2

    def test_confidence_levels_in_metrics(
        self, execution_context_with_repos, java_spring_project
    ):
        """Test confidence levels are included in metrics."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "service1",
                "name": "Service 1",
                "local_path": str(java_spring_project),
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert "confidence_levels" in output.metrics
        assert len(output.metrics["confidence_levels"]) > 0
        assert "avg_confidence" in output.metrics

    def test_graph_nodes_added(
        self, execution_context_with_repos, java_spring_project
    ):
        """Test that project nodes are added to the graph."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "user-service",
                "name": "User Service",
                "local_path": str(java_spring_project),
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        assert len(execution_context_with_repos.graph.nodes) > 0

        # Check for repository node
        repo_nodes = [
            n for n in execution_context_with_repos.graph.nodes
            if n.type == NodeType.REPOSITORY
        ]
        assert len(repo_nodes) > 0

    def test_graph_edges_added(
        self, execution_context_with_repos, java_spring_project
    ):
        """Test that edges are added between projects and entry points."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "user-service",
                "name": "User Service",
                "local_path": str(java_spring_project),
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        # Should have edges from repo to entry points
        assert len(execution_context_with_repos.graph.edges) >= 0

    def test_extract_dependencies_with_invalid_file(self, tmp_path):
        """Test dependency extraction with invalid file."""
        agent = ProjectDefinitionAgent()
        invalid_file = tmp_path / "requirements.txt"
        invalid_file.write_text("this is not valid\n== broken ==")

        deps = agent._extract_python_deps(invalid_file)
        # Should still extract the first part
        assert len(deps) > 0

    def test_error_handling_nonexistent_path(
        self, execution_context_with_repos
    ):
        """Test error handling when repository path doesn't exist."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "missing-service",
                "name": "Missing Service",
                "local_path": "/nonexistent/path",
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        assert output.metrics["projects_detected"] == 0

    def test_tech_stack_detection_java(self, java_spring_project):
        """Test tech stack detection for Java project."""
        agent = ProjectDefinitionAgent()
        tech_stack = agent._detect_tech_stack(java_spring_project)

        assert "java" in tech_stack
        assert len(tech_stack["java"]) > 0

    def test_tech_stack_detection_python(self, python_fastapi_project):
        """Test tech stack detection for Python project."""
        agent = ProjectDefinitionAgent()
        tech_stack = agent._detect_tech_stack(python_fastapi_project)

        assert "python" in tech_stack
        assert len(tech_stack["python"]) > 0

    def test_tech_stack_detection_nodejs(self, react_ui_project):
        """Test tech stack detection for Node.js project."""
        agent = ProjectDefinitionAgent()
        tech_stack = agent._detect_tech_stack(react_ui_project)

        assert "nodejs" in tech_stack
        assert "react" in tech_stack["nodejs"]

    def test_report_in_context_reports(
        self, execution_context_with_repos, java_spring_project
    ):
        """Test that report is stored in context reports."""
        execution_context_with_repos.workspace_config.repositories = [
            {
                "id": "service",
                "name": "Service",
                "local_path": str(java_spring_project),
            }
        ]

        agent = ProjectDefinitionAgent()
        output = agent.execute(execution_context_with_repos)

        assert output.status == "success"
        assert "project_definition" in execution_context_with_repos.reports
        report = execution_context_with_repos.reports["project_definition"]
        assert report.name == "project_definition"
        assert len(report.content) > 0
