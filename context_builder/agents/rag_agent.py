"""RAG Agent for chunking Markdown files and creating vector-ready metadata."""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Report,
)


class RAGAgent(BaseAgent):
    """Chunk Markdown files for RAG and vector database indexing.

    Responsibilities:
    - Chunk Markdown files from project documentation
    - Create vector-ready chunks with metadata
    - Link chunks to graph node IDs where applicable
    - Generate chunks.jsonl with embeddings-ready format
    - Generate index-metadata.json with indexing metadata

    Attributes:
        chunk_size: Target characters per chunk (default 1024)
        overlap: Character overlap between chunks (default 128)
    """

    def __init__(self, chunk_size: int = 1024, overlap: int = 128):
        """Initialize the RAGAgent.

        Args:
            chunk_size: Target characters per chunk
            overlap: Character overlap between chunks for context
        """
        super().__init__(name="RAGAgent")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Chunk Markdown files and create RAG metadata.

        Args:
            context: ExecutionContext containing workspace config.

        Returns:
            AgentOutput with chunks.jsonl and index-metadata.json artifacts.
        """
        if not self.validate_context(context):
            return AgentOutput(
                status="error",
                message="Invalid execution context",
                errors=["ExecutionContext is None"],
            )

        if not context.workspace_config:
            return AgentOutput(
                status="error",
                message="Missing workspace config",
                errors=["WorkspaceConfig not loaded"],
            )

        try:
            # Find all markdown files in the workspace
            workspace_path = context.workspace_config.context_root
            md_files = self._find_markdown_files(workspace_path)

            # Process files and generate chunks
            chunks = []
            index_metadata = {
                "total_files": len(md_files),
                "total_chunks": 0,
                "chunk_size": self.chunk_size,
                "overlap": self.overlap,
                "files": {},
            }

            for md_file in md_files:
                file_chunks = self._chunk_file(md_file, workspace_path)
                chunks.extend(file_chunks)

                index_metadata["files"][str(md_file.relative_to(workspace_path))] = {
                    "chunks_count": len(file_chunks),
                    "first_chunk_id": file_chunks[0]["id"] if file_chunks else None,
                    "last_chunk_id": file_chunks[-1]["id"] if file_chunks else None,
                }

            index_metadata["total_chunks"] = len(chunks)

            # Save chunks as JSONL
            chunks_file = workspace_path / "chunks.jsonl"
            self._save_chunks_jsonl(chunks, chunks_file)

            # Save index metadata
            metadata_file = workspace_path / "index-metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(index_metadata, f, indent=2)

            context.generated_files.append(chunks_file)
            context.generated_files.append(metadata_file)

            # Add report
            report = Report(
                name="RAG Report",
                content=self._generate_report(md_files, chunks, index_metadata),
                file_path=workspace_path / "rag-report.md",
                metrics={
                    "files_processed": len(md_files),
                    "chunks_created": len(chunks),
                    "average_chunk_size": sum(len(c["content"]) for c in chunks) // max(len(chunks), 1),
                },
            )
            context.reports["rag_report"] = report

            return AgentOutput(
                status="success",
                message=f"Chunked {len(md_files)} Markdown files into {len(chunks)} RAG chunks",
                artifacts=[chunks_file, metadata_file],
                metrics={
                    "files_processed": len(md_files),
                    "chunks_created": len(chunks),
                    "average_chunk_size": sum(len(c["content"]) for c in chunks) // max(len(chunks), 1),
                },
            )
        except Exception as e:
            return AgentOutput(
                status="error",
                message=f"RAG agent failed: {str(e)}",
                errors=[str(e)],
            )

    def _find_markdown_files(self, workspace_path: Path) -> List[Path]:
        """Find all Markdown files in the workspace.

        Args:
            workspace_path: Root path to search

        Returns:
            List of Path objects for Markdown files
        """
        md_files = []
        if workspace_path.exists():
            for md_file in workspace_path.rglob("*.md"):
                # Skip hidden directories and common excludes
                if any(part.startswith(".") for part in md_file.parts):
                    continue
                if any(skip in str(md_file) for skip in ["/target/", "/build/", "/node_modules/", "/.git/"]):
                    continue
                md_files.append(md_file)
        return sorted(md_files)

    def _chunk_file(self, file_path: Path, workspace_path: Path) -> List[Dict[str, Any]]:
        """Chunk a single Markdown file.

        Args:
            file_path: Path to the Markdown file
            workspace_path: Workspace root path (for relative references)

        Returns:
            List of chunk dictionaries
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return []

        chunks = []
        chunk_id_base = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        chunk_counter = 0

        # Split by sections (## and ###) first
        sections = self._split_by_sections(content)

        current_chunk = ""
        section_index = 0

        for section in sections:
            if len(current_chunk) + len(section) <= self.chunk_size:
                current_chunk += section
            else:
                if current_chunk:
                    chunk_id = f"{chunk_id_base}_{chunk_counter}"
                    chunks.append({
                        "id": chunk_id,
                        "content": current_chunk.strip(),
                        "file": str(file_path.relative_to(workspace_path)),
                        "file_path": str(file_path),
                        "chunk_index": chunk_counter,
                        "length": len(current_chunk),
                        "metadata": {
                            "source": "markdown",
                            "repository": workspace_path.name,
                        },
                    })
                    chunk_counter += 1
                current_chunk = section

            section_index += 1

        # Add last chunk
        if current_chunk.strip():
            chunk_id = f"{chunk_id_base}_{chunk_counter}"
            chunks.append({
                "id": chunk_id,
                "content": current_chunk.strip(),
                "file": str(file_path.relative_to(workspace_path)),
                "file_path": str(file_path),
                "chunk_index": chunk_counter,
                "length": len(current_chunk),
                "metadata": {
                    "source": "markdown",
                    "repository": workspace_path.name,
                },
            })

        return chunks

    def _split_by_sections(self, content: str) -> List[str]:
        """Split Markdown content by sections.

        Args:
            content: Markdown content to split

        Returns:
            List of section strings
        """
        lines = content.split("\n")
        sections = []
        current_section = ""

        for line in lines:
            if line.startswith("##") and current_section:
                sections.append(current_section)
                current_section = line + "\n"
            else:
                current_section += line + "\n"

        if current_section:
            sections.append(current_section)

        return sections if sections else [content]

    def _save_chunks_jsonl(self, chunks: List[Dict[str, Any]], file_path: Path) -> None:
        """Save chunks in JSONL format (one JSON object per line).

        Args:
            chunks: List of chunk dictionaries
            file_path: Path to save JSONL file
        """
        with open(file_path, "w") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk) + "\n")

    def _generate_report(
        self,
        md_files: List[Path],
        chunks: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> str:
        """Generate a report of RAG chunking results.

        Args:
            md_files: List of processed Markdown files
            chunks: List of created chunks
            metadata: Index metadata

        Returns:
            Report content as string
        """
        report = "# RAG Chunking Report\n\n"
        report += f"## Summary\n"
        report += f"- Files processed: {len(md_files)}\n"
        report += f"- Total chunks created: {len(chunks)}\n"
        report += f"- Chunk size (target): {self.chunk_size} characters\n"
        report += f"- Overlap: {self.overlap} characters\n\n"

        report += f"## Files Processed\n"
        for md_file in md_files:
            report += f"- {md_file.name}\n"

        if chunks:
            avg_size = sum(len(c["content"]) for c in chunks) // len(chunks)
            report += f"\n## Statistics\n"
            report += f"- Average chunk size: {avg_size} characters\n"
            report += f"- Min chunk size: {min(len(c['content']) for c in chunks)} characters\n"
            report += f"- Max chunk size: {max(len(c['content']) for c in chunks)} characters\n"

        return report
