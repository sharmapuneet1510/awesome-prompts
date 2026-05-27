"""Tests for CLI interface"""

import pytest
import tempfile
import json
from pathlib import Path
from instructions_framework.cli import main


class TestCLILoad:
    """Test load command"""

    def test_load_nonexistent_directory(self):
        """Test load with nonexistent directory"""
        result = main(["load", "/nonexistent/path"])
        assert result == 1

    def test_load_empty_directory(self):
        """Test load with empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = main(["load", tmpdir])
            assert result == 0

    def test_load_with_instructions(self):
        """Test load with valid instructions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid instruction file
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test instruction"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
---

Test content
""")

            result = main(["load", tmpdir])
            assert result == 0


class TestCLIValidate:
    """Test validate command"""

    def test_validate_nonexistent_directory(self):
        """Test validate with nonexistent directory"""
        result = main(["validate", "/nonexistent/path"])
        assert result == 1

    def test_validate_empty_directory(self):
        """Test validate with empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = main(["validate", tmpdir])
            assert result == 0

    def test_validate_valid_instructions(self):
        """Test validate with valid instructions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
---

Content
""")

            result = main(["validate", tmpdir])
            assert result == 0



class TestCLIExport:
    """Test export command"""

    def test_export_nonexistent_directory(self):
        """Test export with nonexistent directory"""
        result = main(["export", "/nonexistent/path"])
        assert result == 1

    def test_export_json_format(self):
        """Test export to JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create instruction
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            result = main(["export", tmpdir, "--format", "json"])
            assert result == 0

    def test_export_claude_format(self):
        """Test export to Claude format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            result = main(["export", tmpdir, "--format", "claude"])
            assert result == 0

    def test_export_openai_format(self):
        """Test export to OpenAI format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["openai"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            result = main(["export", tmpdir, "--format", "openai"])
            assert result == 0

    def test_export_gemini_format(self):
        """Test export to Gemini format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["gemini"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            result = main(["export", tmpdir, "--format", "gemini"])
            assert result == 0

    def test_export_copilot_format(self):
        """Test export to Copilot format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            result = main(["export", tmpdir, "--format", "copilot"])
            assert result == 0

    def test_export_to_file(self):
        """Test export to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            output_file = Path(tmpdir) / "output.json"
            result = main(
                ["export", tmpdir, "--format", "json", "--output", str(output_file)]
            )

            assert result == 0
            assert output_file.exists()

    def test_export_invalid_format(self):
        """Test export with invalid format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = main(["export", tmpdir, "--format", "invalid"])
            assert result == 1


class TestCLICheck:
    """Test check command"""

    def test_check_nonexistent_directory(self):
        """Test check with nonexistent directory"""
        result = main(["check", "/nonexistent/path"])
        assert result == 1

    def test_check_empty_directory(self):
        """Test check with empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = main(["check", tmpdir])
            assert result == 0

    def test_check_valid_instructions(self):
        """Test check with valid instructions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            result = main(["check", tmpdir])
            assert result == 0


class TestCLIList:
    """Test list command"""

    def test_list_command(self):
        """Test list command shows available tools"""
        result = main(["list"])
        assert result == 0


class TestCLIHelp:
    """Test help and no-command behavior"""

    def test_no_command(self):
        """Test running with no command prints help"""
        result = main([])
        assert result == 0

    def test_help_flag(self):
        """Test help flag"""
        try:
            result = main(["--help"])
            # argparse exits with SystemExit(0) on --help
        except SystemExit as e:
            assert e.code == 0

    def test_version_flag(self):
        """Test version flag"""
        try:
            result = main(["--version"])
            # argparse exits with SystemExit(0) on --version
        except SystemExit as e:
            assert e.code == 0


class TestCLIApplyMiddleware:
    """Test apply-middleware command"""

    def test_apply_middleware_nonexistent_directory(self):
        """Test apply-middleware with nonexistent directory"""
        result = main(["apply-middleware", "/nonexistent/path", "validator"])
        assert result == 1

    def test_apply_middleware_valid(self):
        """Test apply-middleware with valid middleware"""
        with tempfile.TemporaryDirectory() as tmpdir:
            instr_file = Path(tmpdir) / "instruction.md"
            instr_file.write_text("""---
version: "1.0.0"
description: "Test"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
deprecated: false
author: "test"
id: "test-001"
---

Content
""")

            result = main(["apply-middleware", tmpdir, "validator"])
            assert result == 0

    def test_apply_middleware_nonexistent(self):
        """Test apply-middleware with nonexistent middleware"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = main(["apply-middleware", tmpdir, "nonexistent"])
            assert result == 1
