"""Tests for FlowAnalysisAgent."""

from pathlib import Path
from typing import Dict, Any

import pytest

from context_builder.agents import FlowAnalysisAgent
from context_builder.models import (
    AgentOutput,
    Edge,
    EdgeType,
    ExecutionContext,
    Graph,
    MaturityConfig,
    Node,
    NodeType,
    ProjectConfig,
    Report,
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
def workspace_config(tmp_workspace):
    """Create a workspace configuration."""
    return WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace for flow analysis",
        context_root=tmp_workspace / "context",
        repositories=[],
    )


@pytest.fixture
def execution_context(workspace_config):
    """Create an execution context with empty graph."""
    return ExecutionContext(
        workspace_config=workspace_config,
        project_config=ProjectConfig(),
        tech_aliases=TechAliases(),
        scan_config=ScanConfig(),
        maturity_config=MaturityConfig(),
        test_quality_config=TestQualityConfig(),
        graph=Graph(),
    )


@pytest.fixture
def graph_with_flows(execution_context):
    """Create a graph with API flow paths."""
    graph = execution_context.graph

    # Add endpoint node
    endpoint = Node(
        id="endpoint-1",
        type=NodeType.ENDPOINT,
        name="GET /api/users",
    )
    graph.add_node(endpoint)

    # Add service node
    service = Node(
        id="service-1",
        type=NodeType.CLASS,
        name="UserService",
        framework_role="service",
    )
    graph.add_node(service)

    # Add database node
    database = Node(
        id="db-1",
        type=NodeType.DATABASE,
        name="UserDatabase",
    )
    graph.add_node(database)

    # Add middleware node
    middleware = Node(
        id="middleware-1",
        type=NodeType.MIDDLEWARE,
        name="RabbitMQ",
    )
    graph.add_node(middleware)

    # Add exception node
    exception = Node(
        id="exception-1",
        type=NodeType.EXCEPTION,
        name="DatabaseException",
    )
    graph.add_node(exception)

    # Add exception handler
    handler = Node(
        id="handler-1",
        type=NodeType.CLASS,
        name="ExceptionHandler",
    )
    graph.add_node(handler)

    # Add edges for flow
    graph.add_edge(Edge(
        source="endpoint-1",
        target="service-1",
        type=EdgeType.CALLS,
    ))
    graph.add_edge(Edge(
        source="service-1",
        target="db-1",
        type=EdgeType.READS_FROM,
    ))
    graph.add_edge(Edge(
        source="service-1",
        target="middleware-1",
        type=EdgeType.PUBLISHES_TO,
    ))

    # Add exception handling edge
    graph.add_edge(Edge(
        source="handler-1",
        target="exception-1",
        type=EdgeType.HANDLES,
    ))

    return execution_context


class TestFlowAnalysisAgentExecution:
    """Test overall agent execution."""

    def test_execute_success(self, graph_with_flows):
        """Test successful flow analysis execution."""
        agent = FlowAnalysisAgent()
        output = agent.execute(graph_with_flows)

        assert output.status == "success"
        assert "flows" in output.message.lower()
        assert output.metrics["endpoints_found"] == 1
        assert output.metrics["flows_traced"] > 0

    def test_execute_invalid_context(self):
        """Test execution with invalid context."""
        agent = FlowAnalysisAgent()
        output = agent.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_execute_missing_graph(self, execution_context):
        """Test execution with missing graph."""
        execution_context.graph = None
        agent = FlowAnalysisAgent()
        output = agent.execute(execution_context)

        assert output.status == "error"
        assert "graph" in output.message.lower()


class TestFlowAnalysisAgentFlowDetection:
    """Test flow detection and tracing."""

    def test_find_endpoints(self, graph_with_flows):
        """Test finding API endpoints."""
        agent = FlowAnalysisAgent()
        endpoints = agent._find_endpoints(graph_with_flows)

        assert len(endpoints) == 1
        assert endpoints[0].name == "GET /api/users"

    def test_trace_flows_from_endpoint(self, graph_with_flows):
        """Test tracing flow from endpoint."""
        agent = FlowAnalysisAgent()
        endpoints = agent._find_endpoints(graph_with_flows)
        flows = agent._trace_flows_from_endpoint(endpoints[0], graph_with_flows)

        assert len(flows) > 0
        assert flows[0]["entry_point"] == "GET /api/users"
        assert flows[0]["length"] > 1

    def test_trace_multiple_endpoints(self, execution_context):
        """Test tracing flows from multiple endpoints."""
        graph = execution_context.graph

        # Add multiple endpoints
        for i in range(3):
            endpoint = Node(
                id=f"endpoint-{i}",
                type=NodeType.ENDPOINT,
                name=f"GET /api/resource-{i}",
            )
            graph.add_node(endpoint)

            # Add service
            service = Node(
                id=f"service-{i}",
                type=NodeType.CLASS,
                name=f"Service{i}",
            )
            graph.add_node(service)

            # Connect endpoint to service
            graph.add_edge(Edge(
                source=f"endpoint-{i}",
                target=f"service-{i}",
                type=EdgeType.CALLS,
            ))

        agent = FlowAnalysisAgent()
        endpoints = agent._find_endpoints(execution_context)
        assert len(endpoints) == 3


class TestFlowAnalysisAgentExceptionFlows:
    """Test exception flow analysis."""

    def test_analyze_exception_flows(self, graph_with_flows):
        """Test exception flow analysis."""
        agent = FlowAnalysisAgent()
        count = agent._analyze_exception_flows(graph_with_flows)

        assert count == 1
        assert len(agent.exception_flows) == 1
        assert agent.exception_flows[0]["exception"] == "DatabaseException"
        assert agent.exception_flows[0]["handler"] == "ExceptionHandler"

    def test_exception_flows_empty(self, execution_context):
        """Test with no exception flows."""
        agent = FlowAnalysisAgent()
        count = agent._analyze_exception_flows(execution_context)

        assert count == 0
        assert len(agent.exception_flows) == 0


class TestFlowAnalysisAgentPatternDetection:
    """Test retry and timeout pattern detection."""

    def test_detect_retry_patterns(self, execution_context):
        """Test detecting retry/resilience patterns."""
        graph = execution_context.graph

        # Add method with retry attribute
        method = Node(
            id="method-1",
            type=NodeType.METHOD,
            name="retryableOperation",
            attributes={"retry_enabled": True, "max_retries": 3},
        )
        graph.add_node(method)

        agent = FlowAnalysisAgent()
        count = agent._detect_retry_patterns(execution_context)

        assert count == 1
        assert len(agent.retry_patterns) == 1

    def test_detect_timeout_patterns(self, execution_context):
        """Test detecting timeout patterns."""
        graph = execution_context.graph

        # Add method with timeout
        method = Node(
            id="method-1",
            type=NodeType.METHOD,
            name="timedOperation",
            attributes={"timeout": 5000, "deadline": "2024-01-01"},
        )
        graph.add_node(method)

        agent = FlowAnalysisAgent()
        count = agent._detect_timeout_patterns(execution_context)

        assert count == 1
        assert len(agent.timeout_patterns) == 1

    def test_no_patterns_detected(self, execution_context):
        """Test with no retry/timeout patterns."""
        graph = execution_context.graph

        # Add simple method without patterns
        method = Node(
            id="method-1",
            type=NodeType.METHOD,
            name="simpleMethod",
        )
        graph.add_node(method)

        agent = FlowAnalysisAgent()
        retry_count = agent._detect_retry_patterns(execution_context)
        timeout_count = agent._detect_timeout_patterns(execution_context)

        assert retry_count == 0
        assert timeout_count == 0


class TestFlowAnalysisAgentArtifacts:
    """Test artifact generation."""

    def test_generate_flow_mermaid(self):
        """Test generating flow Mermaid diagram."""
        agent = FlowAnalysisAgent()
        agent.flows = [
            {
                "id": "flow_0",
                "entry_point": "GET /api/users",
                "path": ["endpoint-1", "service-1", "db-1"],
                "length": 3,
                "endpoints": ["GET /api/users", "UserService", "Database"],
            }
        ]

        mermaid = agent._generate_flow_mermaid()

        assert "graph TD" in mermaid
        assert "GET /api/users" in mermaid or "GET" in mermaid

    def test_generate_exception_flow_mermaid(self):
        """Test generating exception flow Mermaid diagram."""
        agent = FlowAnalysisAgent()
        agent.exception_flows = [
            {
                "exception": "DatabaseException",
                "handler": "ExceptionHandler",
                "handler_type": "CLASS",
            }
        ]

        mermaid = agent._generate_exception_flow_mermaid()

        assert "graph TD" in mermaid
        assert "DatabaseException" in mermaid
        assert "ExceptionHandler" in mermaid

    def test_generate_artifacts(self, graph_with_flows):
        """Test artifact file generation."""
        agent = FlowAnalysisAgent()
        agent.execute(graph_with_flows)

        artifacts = agent._generate_artifacts(graph_with_flows)

        assert len(artifacts) > 0
        # Check files exist
        for artifact in artifacts:
            assert artifact.exists()


class TestFlowAnalysisAgentReports:
    """Test report generation."""

    def test_flow_report_content(self):
        """Test flow analysis report content."""
        agent = FlowAnalysisAgent()
        agent.flows = [
            {
                "id": "flow_0",
                "entry_point": "GET /api/users",
                "path": ["endpoint-1", "service-1", "db-1"],
                "length": 3,
                "endpoints": ["GET /api/users", "UserService", "Database"],
            }
        ]

        report = agent._generate_flow_report(1)

        assert "Flow Analysis Report" in report
        assert "GET /api/users" in report or "UserService" in report
        assert "Flows Traced" in report and "1" in report

    def test_exception_report_content(self):
        """Test exception flow report content."""
        agent = FlowAnalysisAgent()
        agent.exception_flows = [
            {
                "exception": "DatabaseException",
                "handler": "ExceptionHandler",
                "handler_type": "CLASS",
            }
        ]

        report = agent._generate_exception_report(1)

        assert "Exception Flow Report" in report
        assert "DatabaseException" in report
        assert "ExceptionHandler" in report

    def test_create_reports(self, graph_with_flows):
        """Test report creation in execution context."""
        agent = FlowAnalysisAgent()
        agent.flows = [
            {
                "id": "flow_0",
                "entry_point": "GET /api/users",
                "path": ["endpoint-1", "service-1", "db-1"],
                "length": 3,
                "endpoints": ["GET /api/users", "UserService", "Database"],
            }
        ]

        agent._create_reports(graph_with_flows, 1, 0)

        assert "flow_analysis_report" in graph_with_flows.reports
        assert "exception_flow_report" in graph_with_flows.reports
