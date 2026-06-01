"""Tests for RAGAgent."""

import json
from pathlib import Path

import pytest

from context_builder.agents import RAGAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Graph,
    MaturityConfig,
    ProjectConfig,
    ScanConfig,
    TechAliases,
    TestQualityConfig,
    WorkspaceConfig,
)


@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temporary workspace."""
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    return tmp_path


@pytest.fixture
def markdown_workspace(tmp_workspace):
    """Create workspace with markdown files."""
    # Create some markdown files
    docs_dir = tmp_workspace / "docs"
    docs_dir.mkdir()

    (docs_dir / "architecture.md").write_text("""
# Architecture

## Overview
This is the system architecture.

### Microservices
The system uses microservices architecture.

### Database
PostgreSQL is used for primary storage.
""")

    (docs_dir / "api.md").write_text("""
# API Documentation

## Endpoints

### GET /api/users
Retrieve all users.

### POST /api/users
Create a new user.
""")

    (tmp_workspace / "README.md").write_text("""
# Project README

## Getting Started
To get started, follow these steps.

## Installation
Install dependencies using pip.
""")

    return tmp_workspace


@pytest.fixture
def execution_context(markdown_workspace):
    """Create execution context with workspace config."""
    workspace_config = WorkspaceConfig(
        id="test-workspace",
        name="Test Workspace",
        description="Test workspace for RAG",
        context_root=markdown_workspace,
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


class TestRAGAgent:
    """Tests for RAGAgent."""

    def test_rag_agent_initialization(self):
        """Test agent initialization."""
        agent = RAGAgent()
        assert agent.name == "RAGAgent"
        assert agent.chunk_size == 1024
        assert agent.overlap == 128

    def test_rag_agent_custom_initialization(self):
        """Test agent initialization with custom parameters."""
        agent = RAGAgent(chunk_size=512, overlap=64)
        assert agent.chunk_size == 512
        assert agent.overlap == 64

    def test_rag_agent_execute_success(self, execution_context):
        """Test successful execution of RAG agent."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        assert output.status == "success"
        assert "chunks" in output.message.lower()
        assert len(output.artifacts) == 2  # chunks.jsonl and index-metadata.json

    def test_rag_agent_creates_chunks_file(self, execution_context):
        """Test that agent creates chunks.jsonl file."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        chunks_file = workspace_path / "chunks.jsonl"

        assert chunks_file.exists()
        assert chunks_file.stat().st_size > 0

    def test_rag_agent_creates_metadata_file(self, execution_context):
        """Test that agent creates index-metadata.json file."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        metadata_file = workspace_path / "index-metadata.json"

        assert metadata_file.exists()
        metadata = json.loads(metadata_file.read_text())
        assert "total_files" in metadata
        assert "total_chunks" in metadata

    def test_rag_agent_chunks_format(self, execution_context):
        """Test that chunks have correct format."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        chunks_file = workspace_path / "chunks.jsonl"

        lines = chunks_file.read_text().strip().split("\n")
        assert len(lines) > 0

        # Parse first chunk
        chunk = json.loads(lines[0])
        assert "id" in chunk
        assert "content" in chunk
        assert "file" in chunk
        assert "metadata" in chunk

    def test_rag_agent_metadata_completeness(self, execution_context):
        """Test metadata file completeness."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        metadata_file = workspace_path / "index-metadata.json"
        metadata = json.loads(metadata_file.read_text())

        assert metadata["chunk_size"] == agent.chunk_size
        assert metadata["overlap"] == agent.overlap
        assert "files" in metadata

    def test_rag_agent_metrics(self, execution_context):
        """Test that agent returns correct metrics."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        assert "files_processed" in output.metrics
        assert "chunks_created" in output.metrics
        assert "average_chunk_size" in output.metrics
        assert output.metrics["files_processed"] >= 0
        assert output.metrics["chunks_created"] >= 0

    def test_rag_agent_report_generated(self, execution_context):
        """Test that agent generates report."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        assert "rag_report" in execution_context.reports
        report = execution_context.reports["rag_report"]
        assert "Chunking" in report.content or "chunking" in report.content.lower()

    def test_rag_agent_handles_empty_workspace(self, tmp_path):
        """Test agent handles empty workspace gracefully."""
        workspace_config = WorkspaceConfig(
            id="empty-workspace",
            name="Empty Workspace",
            description="Empty workspace",
            context_root=tmp_path,
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        agent = RAGAgent()
        output = agent.execute(context)

        assert output.status == "success"

    def test_rag_agent_handles_none_context(self):
        """Test agent handles None context."""
        agent = RAGAgent()
        output = agent.execute(None)

        assert output.status == "error"
        assert len(output.errors) > 0

    def test_rag_agent_file_chunking(self, execution_context):
        """Test that files are chunked properly."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        chunks_file = workspace_path / "chunks.jsonl"

        lines = chunks_file.read_text().strip().split("\n")
        chunks = [json.loads(line) for line in lines]

        # Verify chunks are not empty
        assert all(len(c["content"]) > 0 for c in chunks)

        # Verify chunk content is valid
        assert all("file" in c for c in chunks)

    def test_rag_agent_chunk_indexing(self, execution_context):
        """Test chunk indexing within files."""
        agent = RAGAgent()
        output = agent.execute(execution_context)

        workspace_path = execution_context.workspace_config.context_root
        chunks_file = workspace_path / "chunks.jsonl"

        lines = chunks_file.read_text().strip().split("\n")
        chunks = [json.loads(line) for line in lines]

        # Group chunks by file
        chunks_by_file = {}
        for chunk in chunks:
            file_key = chunk["file"]
            if file_key not in chunks_by_file:
                chunks_by_file[file_key] = []
            chunks_by_file[file_key].append(chunk)

        # Verify indexing within each file
        for file_chunks in chunks_by_file.values():
            indices = [c["chunk_index"] for c in file_chunks]
            assert len(set(indices)) == len(indices)  # All unique

    def test_rag_agent_finds_multiple_files(self, markdown_workspace):
        """Test that agent finds multiple markdown files."""
        workspace_config = WorkspaceConfig(
            id="multi-file-workspace",
            name="Multi File",
            description="Multiple files",
            context_root=markdown_workspace,
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        agent = RAGAgent()
        output = agent.execute(context)

        # Should have found at least 2 markdown files
        assert output.metrics["files_processed"] >= 2

    def test_rag_agent_artifact_tracking(self, execution_context):
        """Test that generated files are tracked in context."""
        agent = RAGAgent()
        initial_count = len(execution_context.generated_files)
        output = agent.execute(execution_context)

        # Should have added 2 artifacts
        assert len(execution_context.generated_files) == initial_count + 2

    def test_rag_agent_custom_chunk_size(self, markdown_workspace):
        """Test agent with custom chunk size."""
        workspace_config = WorkspaceConfig(
            id="custom-chunk-workspace",
            name="Custom Chunk",
            description="Custom chunk size",
            context_root=markdown_workspace,
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        agent = RAGAgent(chunk_size=256)
        output = agent.execute(context)

        assert output.status == "success"

    def test_rag_agent_excludes_hidden_dirs(self, tmp_path):
        """Test that agent excludes hidden directories."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        hidden_dir = tmp_path / ".hidden"
        hidden_dir.mkdir()

        (docs_dir / "visible.md").write_text("# Visible")
        (hidden_dir / "hidden.md").write_text("# Hidden")

        workspace_config = WorkspaceConfig(
            id="hidden-test",
            name="Hidden Test",
            description="Test hidden dirs",
            context_root=tmp_path,
        )

        context = ExecutionContext(
            workspace_config=workspace_config,
            project_config=ProjectConfig(),
            tech_aliases=TechAliases(),
            scan_config=ScanConfig(),
            maturity_config=MaturityConfig(),
            test_quality_config=TestQualityConfig(),
            graph=Graph(),
        )

        agent = RAGAgent()
        output = agent.execute(context)

        workspace_path = context.workspace_config.context_root
        chunks_file = workspace_path / "chunks.jsonl"

        lines = chunks_file.read_text().strip().split("\n")
        chunks = [json.loads(line) if line.strip() else {} for line in lines if line.strip()]

        # Should only find visible.md
        files = set(c.get("file") for c in chunks if c)
        assert any("visible" in f for f in files if f)
        assert not any("hidden" in f for f in files if f)
