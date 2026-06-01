"""Tests for MarkdownService."""

import pytest
from pathlib import Path
import tempfile

from context_builder.services.markdown_service import MarkdownService


class TestMarkdownServiceInitialization:
    """Tests for MarkdownService initialization."""

    def test_init(self):
        """MarkdownService initializes successfully."""
        service = MarkdownService()
        assert service is not None
        assert service.logger is not None


class TestCreateDocument:
    """Tests for create_document method."""

    def test_create_document_with_title_only(self):
        """Create document with title only."""
        service = MarkdownService()
        doc = service.create_document("My Document")

        assert "# My Document" in doc

    def test_create_document_with_sections(self):
        """Create document with sections."""
        service = MarkdownService()

        sections = [
            {"heading": "Introduction", "level": 2, "content": "Welcome"},
            {"heading": "Details", "level": 2, "content": "More info"},
        ]

        doc = service.create_document("My Doc", sections=sections)

        assert "# My Doc" in doc
        assert "## Introduction" in doc
        assert "## Details" in doc
        assert "Welcome" in doc

    def test_create_document_with_metadata(self):
        """Create document with front matter metadata."""
        service = MarkdownService()

        metadata = {"author": "Test", "date": "2026-06-01"}
        doc = service.create_document("Doc", metadata=metadata)

        assert "---" in doc
        assert "author: Test" in doc
        assert "date: 2026-06-01" in doc


class TestAddTableOfContents:
    """Tests for add_table_of_contents method."""

    def test_add_table_of_contents(self):
        """Add table of contents to document."""
        service = MarkdownService()

        document = """# Main Title

## Section 1
Content here

## Section 2
More content
"""

        with_toc = service.add_table_of_contents(document)

        assert "## Table of Contents" in with_toc
        assert "[Section 1]" in with_toc
        assert "[Section 2]" in with_toc

    def test_add_table_of_contents_no_headings(self):
        """Add table of contents when no headings present."""
        service = MarkdownService()

        document = "# Title\n\nJust content"
        with_toc = service.add_table_of_contents(document)

        # Should not add TOC if no headings
        assert "## Table of Contents" not in with_toc


class TestCreateTable:
    """Tests for create_table method."""

    def test_create_table(self):
        """Create markdown table."""
        service = MarkdownService()

        headers = ["Name", "Age", "City"]
        rows = [["Alice", "30", "NYC"], ["Bob", "25", "LA"]]

        table = service.create_table(headers, rows)

        assert "| Name | Age | City |" in table
        assert "| Alice | 30 | NYC |" in table
        assert "| Bob | 25 | LA |" in table

    def test_create_table_with_alignment(self):
        """Create table with alignment."""
        service = MarkdownService()

        headers = ["Left", "Center", "Right"]
        rows = [["A", "B", "C"]]
        align = ["left", "center", "right"]

        table = service.create_table(headers, rows, align=align)

        assert ":---" in table  # left
        assert ":---:" in table  # center
        assert "---:" in table  # right

    def test_create_table_empty(self):
        """Create table with empty input."""
        service = MarkdownService()

        table = service.create_table([], [])
        assert table == ""


class TestCreateCodeBlock:
    """Tests for create_code_block method."""

    def test_create_code_block(self):
        """Create code block."""
        service = MarkdownService()

        code = 'print("hello")'
        block = service.create_code_block(code, language="python")

        assert "```python" in block
        assert 'print("hello")' in block
        assert "```" in block

    def test_create_code_block_with_title(self):
        """Create code block with title."""
        service = MarkdownService()

        code = "x = 1"
        block = service.create_code_block(code, language="python", title="Example")

        assert "**Example**" in block
        assert "```python" in block


class TestCreateList:
    """Tests for create_list method."""

    def test_create_unordered_list(self):
        """Create unordered list."""
        service = MarkdownService()

        items = ["Item 1", "Item 2", "Item 3"]
        lst = service.create_list(items, ordered=False)

        assert "- Item 1" in lst
        assert "- Item 2" in lst
        assert "- Item 3" in lst

    def test_create_ordered_list(self):
        """Create ordered list."""
        service = MarkdownService()

        items = ["First", "Second", "Third"]
        lst = service.create_list(items, ordered=True)

        assert "1. First" in lst
        assert "2. Second" in lst
        assert "3. Third" in lst

    def test_create_nested_list(self):
        """Create nested list with indentation."""
        service = MarkdownService()

        items = ["Level 1"]
        lst = service.create_list(items, level=2)

        assert "    - Level 1" in lst


class TestCreateCallout:
    """Tests for create_callout method."""

    def test_create_note_callout(self):
        """Create note callout."""
        service = MarkdownService()

        callout = service.create_callout("This is a note", callout_type="note")

        assert "> **NOTE**" in callout
        assert "This is a note" in callout

    def test_create_warning_callout(self):
        """Create warning callout."""
        service = MarkdownService()

        callout = service.create_callout("Be careful", callout_type="warning")

        assert "> **WARNING**" in callout

    def test_create_danger_callout(self):
        """Create danger callout."""
        service = MarkdownService()

        callout = service.create_callout("Danger!", callout_type="danger")

        assert "> **DANGER**" in callout


class TestCreateLink:
    """Tests for create_link method."""

    def test_create_link(self):
        """Create markdown link."""
        service = MarkdownService()

        link = service.create_link("Google", "https://google.com")

        assert "[Google](https://google.com)" == link


class TestFileOperations:
    """Tests for file operations."""

    def test_write_to_file(self):
        """Write markdown to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = MarkdownService()

            content = "# Test Document\n\nHello world"
            file_path = Path(tmpdir) / "test.md"

            result = service.write_to_file(content, file_path)

            assert result is True
            assert file_path.exists()
            assert file_path.read_text() == content

    def test_read_from_file(self):
        """Read markdown from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = MarkdownService()

            file_path = Path(tmpdir) / "test.md"
            content = "# Test\n\nContent here"
            file_path.write_text(content)

            read_content = service.read_from_file(file_path)

            assert read_content == content

    def test_read_from_nonexistent_file(self):
        """Read from nonexistent file returns None."""
        service = MarkdownService()

        result = service.read_from_file(Path("/nonexistent/file.md"))

        assert result is None


class TestAddTimestamp:
    """Tests for add_timestamp method."""

    def test_add_timestamp(self):
        """Add timestamp to document."""
        service = MarkdownService()

        document = "# Test Document\n\nContent"
        with_timestamp = service.add_timestamp(document)

        assert "Generated:" in with_timestamp
        assert "# Test Document" in with_timestamp
