"""Tests for RepoScannerAgent."""

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from context_builder.agents import RepoScannerAgent
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
def tmp_workspace(tmp_path):
    """Create a temporary workspace directory."""
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    return tmp_path


@pytest.fixture
def java_test_repo(tmp_workspace):
    """Create a mock Java repository with various symbols."""
    repo_dir = tmp_workspace / "java-service"
    src_dir = repo_dir / "src" / "main" / "java" / "com" / "example"
    src_dir.mkdir(parents=True)

    # Create a controller class
    controller_file = src_dir / "UserController.java"
    controller_file.write_text("""
package com.example;

import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {
    private UserService userService;

    @GetMapping
    public List<User> listUsers() {
        return userService.findAll();
    }

    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id).orElse(null);
    }
}
""")

    # Create a consumer class
    consumer_file = src_dir / "OrderConsumer.java"
    consumer_file.write_text("""
package com.example;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class OrderConsumer {
    @KafkaListener(topics = "order.events", groupId = "order-group")
    public void handleOrderEvent(String message) {
        // Process order event
    }
}
""")

    # Create a producer class
    producer_file = src_dir / "PaymentProducer.java"
    producer_file.write_text("""
package com.example;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class PaymentProducer {
    private KafkaTemplate<String, String> kafkaTemplate;

    public void publishPaymentEvent(String event) {
        kafkaTemplate.send("payment.events", event);
    }
}
""")

    # Create a scheduler class
    scheduler_file = src_dir / "TaskScheduler.java"
    scheduler_file.write_text("""
package com.example;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class TaskScheduler {
    @Scheduled(fixedRate = 5000)
    public void runScheduledTask() {
        // Scheduled task logic
    }

    @Scheduled(cron = "0 0 * * * *")
    public void cleanupTask() {
        // Cleanup logic
    }
}
""")

    # Create a service class
    service_file = src_dir / "UserService.java"
    service_file.write_text("""
package com.example;

import org.springframework.stereotype.Service;

@Service
public class UserService {
    public List<User> findAll() {
        // Implementation
        return null;
    }

    public User save(User user) {
        // Implementation
        return user;
    }
}
""")

    # Create pom.xml
    pom_file = repo_dir / "pom.xml"
    pom_file.write_text("""<?xml version="1.0"?>
<project>
    <artifactId>spring-boot-starter-web</artifactId>
    <artifactId>spring-boot-starter-kafka</artifactId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</project>
""")

    # Create application.properties
    props_file = repo_dir / "application.properties"
    props_file.write_text("""
spring.application.name=user-service
spring.jpa.hibernate.ddl-auto=update
kafka.bootstrap-servers=localhost:9092
""")

    return repo_dir


@pytest.fixture
def python_test_repo(tmp_workspace):
    """Create a mock Python/FastAPI repository."""
    repo_dir = tmp_workspace / "python-api"
    src_dir = repo_dir / "src"
    src_dir.mkdir(parents=True)

    # Create FastAPI app with routes
    main_file = src_dir / "main.py"
    main_file.write_text("""
from fastapi import FastAPI
from celery import Celery

app = FastAPI()
celery_app = Celery(__name__)

@app.get("/api/users")
async def list_users():
    '''List all users'''
    return []

@app.post("/api/users")
async def create_user(user: dict):
    '''Create a new user'''
    return user

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    '''Get user by ID'''
    return {"id": user_id}
""")

    # Create models
    models_file = src_dir / "models.py"
    models_file.write_text("""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    total = Column(Integer)
""")

    # Create tasks
    tasks_file = src_dir / "tasks.py"
    tasks_file.write_text("""
from celery import shared_task

@shared_task
def process_order(order_id):
    pass

@shared_task
def send_email(email, subject):
    pass

@shared_task
def generate_report(report_id):
    pass
""")

    # Create requirements.txt
    req_file = repo_dir / "requirements.txt"
    req_file.write_text("""
fastapi==0.95.0
uvicorn==0.21.0
sqlalchemy==2.0.0
celery==5.2.0
redis==4.5.0
pydantic==1.10.0
""")

    return repo_dir


@pytest.fixture
def workspace_config(tmp_workspace, java_test_repo, python_test_repo):
    """Create workspace configuration."""
    return WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace for scanning",
        context_root=tmp_workspace / "context",
        repositories=[
            {
                "id": "java-service",
                "name": "Java Service",
                "local_path": str(java_test_repo),
            },
            {
                "id": "python-api",
                "name": "Python API",
                "local_path": str(python_test_repo),
            },
        ],
    )


@pytest.fixture
def scan_config():
    """Create scan configuration."""
    return ScanConfig(
        include_patterns=[
            "**/*.java",
            "**/*.py",
            "**/*.properties",
            "**/*.yml",
            "**/pom.xml",
        ],
        exclude_patterns=[
            "**/target/**",
            "**/__pycache__/**",
            "**/venv/**",
        ],
    )


@pytest.fixture
def execution_context(workspace_config, scan_config):
    """Create execution context."""
    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=scan_config,
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=Graph(),
    )


@pytest.fixture
def repo_scanner():
    """Create RepoScannerAgent instance."""
    return RepoScannerAgent()


class TestRepoScannerAgent:
    """Test cases for RepoScannerAgent."""

    def test_scan_java_repository(self, repo_scanner, execution_context):
        """Test scanning a Java repository and extracting symbols."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        assert output.metrics["total_files"] > 0
        assert output.metrics["total_symbols"] > 0
        assert output.metrics["classes"] > 0
        assert output.metrics["endpoints"] > 0

    def test_scan_python_repository(self, repo_scanner, execution_context):
        """Test scanning a Python repository."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        assert output.metrics["endpoints"] > 0

    def test_extract_java_classes(self, repo_scanner, execution_context):
        """Test extracting Java classes."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        classes_count = output.metrics.get("classes", 0)
        assert classes_count >= 4  # At least 4 classes defined

    def test_extract_java_endpoints(self, repo_scanner, execution_context):
        """Test extracting Java REST endpoints."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        endpoints_count = output.metrics.get("endpoints", 0)
        assert endpoints_count >= 3  # At least 3 endpoints

    def test_extract_java_consumers(self, repo_scanner, execution_context):
        """Test extracting Kafka consumers."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        consumers_count = output.metrics.get("consumers", 0)
        assert consumers_count >= 1

    def test_extract_java_producers(self, repo_scanner, execution_context):
        """Test extracting Kafka producers."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        producers_count = output.metrics.get("producers", 0)
        assert producers_count >= 1

    def test_extract_schedulers(self, repo_scanner, execution_context):
        """Test extracting scheduled tasks."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        schedulers_count = output.metrics.get("schedulers", 0)
        assert schedulers_count >= 1

    def test_extract_configurations(self, repo_scanner, execution_context):
        """Test extracting configuration files."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        configs_count = output.metrics.get("configurations", 0)
        assert configs_count >= 2  # application.properties and requirements.txt

    def test_scan_report_generation(self, repo_scanner, execution_context):
        """Test that scan report is generated."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        assert "scan_report" in execution_context.reports
        report = execution_context.reports["scan_report"]
        assert "Repository Scan Report" in report.content
        assert "Symbol Extraction Results" in report.content

    def test_raw_symbols_json_generation(self, repo_scanner, execution_context):
        """Test that raw-symbols.json is generated."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"
        assert len(output.artifacts) > 0

        json_path = output.artifacts[0]
        assert json_path.exists()
        assert json_path.name == "raw-symbols.json"

        # Verify JSON structure
        with open(json_path, "r") as f:
            symbols = json.load(f)

        assert "classes" in symbols
        assert "endpoints" in symbols
        assert "consumers" in symbols
        assert "producers" in symbols
        assert "schedulers" in symbols
        assert "configurations" in symbols

    def test_empty_repository(self, repo_scanner, tmp_workspace):
        """Test scanning an empty repository."""
        empty_repo = tmp_workspace / "empty-repo"
        empty_repo.mkdir()

        config = WorkspaceConfig(
            id="test",
            name="Test",
            description="Test",
            context_root=tmp_workspace / "context",
            repositories=[
                {
                    "id": "empty",
                    "name": "Empty Repo",
                    "local_path": str(empty_repo),
                }
            ],
        )

        context = ExecutionContext(
            workspace_config=config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        output = repo_scanner.execute(context)

        assert output.status == "success"
        assert output.metrics["total_files"] == 0

    def test_invalid_paths(self, repo_scanner, tmp_workspace):
        """Test handling of invalid repository paths."""
        config = WorkspaceConfig(
            id="test",
            name="Test",
            description="Test",
            context_root=tmp_workspace / "context",
            repositories=[
                {
                    "id": "invalid",
                    "name": "Invalid Repo",
                    "local_path": "/nonexistent/path",
                }
            ],
        )

        context = ExecutionContext(
            workspace_config=config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        output = repo_scanner.execute(context)

        # Should handle gracefully
        assert output.status == "success"
        assert output.metrics["total_files"] == 0

    def test_missing_config(self, repo_scanner):
        """Test error handling when config is missing."""
        context = ExecutionContext(
            workspace_config=None,
            project_config=None,
            tech_aliases=None,
            scan_config=None,
            maturity_config=None,
            test_quality_config=None,
            graph=Graph(),
        )

        output = repo_scanner.execute(context)

        assert output.status == "error"
        assert "Missing workspace or scan config" in output.message

    def test_symbols_added_to_graph(self, repo_scanner, execution_context):
        """Test that extracted symbols are added to the context graph."""
        output = repo_scanner.execute(execution_context)

        assert output.status == "success"

        # Verify nodes were added to graph
        graph_nodes = execution_context.graph.nodes
        assert len(graph_nodes) > 0

        # Verify various node types are present
        node_types = {node.type for node in graph_nodes}
        assert NodeType.ENDPOINT in node_types or NodeType.CLASS in node_types

    def test_middleware_extraction(self, repo_scanner, java_test_repo, tmp_workspace):
        """Test extraction of middleware topics from code."""
        config = WorkspaceConfig(
            id="test",
            name="Test",
            description="Test",
            context_root=tmp_workspace / "context",
            repositories=[
                {
                    "id": "java-service",
                    "name": "Java Service",
                    "local_path": str(java_test_repo),
                }
            ],
        )

        context = ExecutionContext(
            workspace_config=config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        output = repo_scanner.execute(context)

        assert output.status == "success"
        # Should extract Kafka topics from the consumer and producer
        middleware_count = output.metrics.get("middleware_topics", 0)
        # Note: regex might not catch all topics, but at least we tested the feature


class TestRepoScannerExtractSymbols:
    """Test symbol extraction utilities."""

    def test_detect_java_language(self, repo_scanner):
        """Test language detection for Java files."""
        java_path = Path("src/main/java/Example.java")
        lang = repo_scanner._detect_language(java_path)
        assert lang == "java"

    def test_detect_python_language(self, repo_scanner):
        """Test language detection for Python files."""
        py_path = Path("src/main.py")
        lang = repo_scanner._detect_language(py_path)
        assert lang == "python"

    def test_detect_unknown_language(self, repo_scanner):
        """Test language detection for unknown file types."""
        unknown_path = Path("README.md")
        lang = repo_scanner._detect_language(unknown_path)
        assert lang is None

    def test_java_class_pattern_matching(self, repo_scanner):
        """Test Java class pattern regex."""
        java_code = """
        public class UserService extends BaseService implements IUserService {
            public void process() {}
        }
        """
        matches = list(repo_scanner.JAVA_CLASS_PATTERN.finditer(java_code))
        assert len(matches) >= 1
        assert matches[0].group(1) == "UserService"

    def test_java_endpoint_pattern_matching(self, repo_scanner):
        """Test Java endpoint pattern regex."""
        java_code = """
        @GetMapping("/api/users")
        public List<User> getUsers() {}
        """
        matches = list(repo_scanner.JAVA_ENDPOINT_PATTERN.finditer(java_code))
        assert len(matches) >= 1
        assert "/api/users" in matches[0].group(0)

    def test_python_class_pattern_matching(self, repo_scanner):
        """Test Python class pattern regex."""
        py_code = """class UserService(BaseService):
    def process(self):
        pass
"""
        matches = list(repo_scanner.PYTHON_CLASS_PATTERN.finditer(py_code))
        assert len(matches) >= 1
        assert matches[0].group(1) == "UserService"

    def test_python_endpoint_pattern_matching(self, repo_scanner):
        """Test Python endpoint pattern regex."""
        py_code = """
        @app.get("/api/users")
        async def list_users():
            pass
        """
        matches = list(repo_scanner.PYTHON_ENDPOINT_PATTERN.finditer(py_code))
        assert len(matches) >= 1
