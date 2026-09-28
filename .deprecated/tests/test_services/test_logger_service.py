"""Tests for LoggerService."""

import pytest
import logging
from pathlib import Path
import tempfile

from context_builder.services.logger_service import LoggerService


class TestLoggerServiceInitialization:
    """Tests for LoggerService initialization."""

    def test_init_with_name(self):
        """LoggerService initializes with custom name."""
        service = LoggerService("test.logger")
        assert service.name == "test.logger"
        assert service.logger is not None

    def test_init_default_name(self):
        """LoggerService initializes with default name."""
        service = LoggerService()
        assert service.logger is not None


class TestConsoleHandler:
    """Tests for console handler setup."""

    def test_setup_console_handler(self):
        """Setup console handler successfully."""
        service = LoggerService()
        handler = service.setup_console_handler()

        assert handler is not None
        assert len(service.handlers) == 1

    def test_setup_console_handler_with_level(self):
        """Setup console handler with custom level."""
        service = LoggerService()
        handler = service.setup_console_handler(level=logging.DEBUG)

        assert handler.level == logging.DEBUG

    def test_setup_console_handler_with_format(self):
        """Setup console handler with custom format."""
        service = LoggerService()
        format_str = "%(levelname)s - %(message)s"
        handler = service.setup_console_handler(format_str=format_str)

        assert handler.formatter is not None


class TestFileHandler:
    """Tests for file handler setup."""

    def test_setup_file_handler(self):
        """Setup file handler successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = LoggerService()
            log_file = Path(tmpdir) / "test.log"

            handler = service.setup_file_handler(log_file)

            assert handler is not None
            assert len(service.handlers) == 1

    def test_setup_file_handler_creates_directory(self):
        """Setup file handler creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = LoggerService()
            log_file = Path(tmpdir) / "logs" / "nested" / "test.log"

            handler = service.setup_file_handler(log_file)

            assert log_file.parent.exists()

    def test_setup_file_handler_with_rotation(self):
        """Setup file handler with rotation parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = LoggerService()
            log_file = Path(tmpdir) / "test.log"

            handler = service.setup_file_handler(
                log_file, max_bytes=1_000_000, backup_count=3
            )

            assert handler.maxBytes == 1_000_000
            assert handler.backupCount == 3


class TestSetLevel:
    """Tests for set_level method."""

    def test_set_level(self):
        """Set logging level for all handlers."""
        service = LoggerService()
        service.setup_console_handler()
        service.setup_console_handler()

        service.set_level(logging.DEBUG)

        assert service.logger.level == logging.DEBUG
        for handler in service.handlers:
            assert handler.level == logging.DEBUG


class TestGetLogger:
    """Tests for get_logger method."""

    def test_get_logger(self):
        """Get configured logger."""
        service = LoggerService("test")
        logger = service.get_logger()

        assert logger is not None
        assert logger.name == "test"


class TestClose:
    """Tests for close method."""

    def test_close_handlers(self):
        """Close all handlers."""
        service = LoggerService()
        service.setup_console_handler()

        assert len(service.handlers) == 1

        service.close()

        assert len(service.handlers) == 0


class TestLogSection:
    """Tests for log_section method."""

    def test_log_section(self):
        """Log section header."""
        service = LoggerService()
        service.setup_console_handler()

        # Just verify it doesn't raise an exception
        service.log_section("Test Section")


class TestLogStep:
    """Tests for log_step method."""

    def test_log_step(self):
        """Log a pipeline step."""
        service = LoggerService()
        service.setup_console_handler()

        # Just verify it doesn't raise an exception
        service.log_step(1, "Initialize")


class TestLogMetrics:
    """Tests for log_metrics method."""

    def test_log_metrics(self):
        """Log metrics dictionary."""
        service = LoggerService()
        service.setup_console_handler()

        metrics = {"files_scanned": 100, "classes_found": 45, "coverage": 85.5}

        # Just verify it doesn't raise an exception
        service.log_metrics(metrics)


class TestLogErrorWithContext:
    """Tests for log_error_with_context method."""

    def test_log_error_with_context(self):
        """Log error with context."""
        service = LoggerService()
        service.setup_console_handler()

        try:
            raise ValueError("Test error")
        except ValueError as e:
            # Just verify it doesn't raise an exception
            service.log_error_with_context(e, context="Testing error handling")

    def test_log_error_without_context(self):
        """Log error without context."""
        service = LoggerService()
        service.setup_console_handler()

        try:
            raise RuntimeError("Test")
        except RuntimeError as e:
            service.log_error_with_context(e)


class TestCreateLogFile:
    """Tests for create_log_file method."""

    def test_create_log_file(self):
        """Create timestamped log file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = LoggerService()
            log_dir = Path(tmpdir)

            log_file = service.create_log_file(log_dir)

            assert log_dir in log_file.parents
            assert log_file.name.startswith("context-builder_")
            assert log_file.name.endswith(".log")

    def test_create_log_file_with_prefix(self):
        """Create log file with custom prefix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = LoggerService()
            log_dir = Path(tmpdir)

            log_file = service.create_log_file(log_dir, prefix="custom")

            assert log_file.name.startswith("custom_")


class TestIntegration:
    """Integration tests for LoggerService."""

    def test_full_setup(self):
        """Full logger setup with console and file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = LoggerService("integration_test")

            # Setup handlers
            service.setup_console_handler(level=logging.INFO)
            log_file = Path(tmpdir) / "test.log"
            service.setup_file_handler(log_file, level=logging.DEBUG)

            # Use logger
            logger = service.get_logger()
            logger.info("Test message")
            logger.debug("Debug message")

            # Verify file was created
            assert log_file.exists()

            # Cleanup
            service.close()
