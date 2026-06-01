"""LoggerService: Logging utilities with structured formatting and file rotation."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime


class LoggerService:
    """Manage logging configuration and formatting."""

    def __init__(self, name: str = __name__):
        """
        Initialize LoggerService.

        Args:
            name: Logger name
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.handlers = []

    def setup_console_handler(
        self, level: int = logging.INFO, format_str: Optional[str] = None
    ) -> logging.StreamHandler:
        """
        Setup console logging handler.

        Args:
            level: Logging level
            format_str: Optional custom format string

        Returns:
            StreamHandler instance
        """
        handler = logging.StreamHandler()
        handler.setLevel(level)

        if not format_str:
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        formatter = logging.Formatter(format_str)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.handlers.append(handler)

        return handler

    def setup_file_handler(
        self,
        file_path: Path,
        level: int = logging.DEBUG,
        format_str: Optional[str] = None,
        max_bytes: int = 10_000_000,
        backup_count: int = 5,
    ) -> logging.handlers.RotatingFileHandler:
        """
        Setup file logging handler with rotation.

        Args:
            file_path: Log file path
            level: Logging level
            format_str: Optional custom format string
            max_bytes: Max file size before rotation (default 10MB)
            backup_count: Number of backup files to keep

        Returns:
            RotatingFileHandler instance
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setLevel(level)

        if not format_str:
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        formatter = logging.Formatter(format_str)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.handlers.append(handler)

        return handler

    def set_level(self, level: int) -> None:
        """
        Set logging level for all handlers.

        Args:
            level: Logging level
        """
        self.logger.setLevel(level)
        for handler in self.handlers:
            handler.setLevel(level)

    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger.

        Returns:
            Logger instance
        """
        return self.logger

    def close(self) -> None:
        """Close all handlers."""
        for handler in self.handlers:
            handler.close()
        self.handlers.clear()

    def log_section(self, title: str, level: int = logging.INFO) -> None:
        """
        Log a section header.

        Args:
            title: Section title
            level: Logging level
        """
        separator = "=" * 70
        self.logger.log(level, separator)
        self.logger.log(level, title)
        self.logger.log(level, separator)

    def log_step(
        self, step_number: int, step_name: str, level: int = logging.INFO
    ) -> None:
        """
        Log a step in a pipeline.

        Args:
            step_number: Step number
            step_name: Step name
            level: Logging level
        """
        self.logger.log(level, f"[STEP {step_number}] {step_name}")

    def log_metrics(self, metrics: dict, level: int = logging.INFO) -> None:
        """
        Log metrics as key-value pairs.

        Args:
            metrics: Dictionary of metrics
            level: Logging level
        """
        self.logger.log(level, "Metrics:")
        for key, value in metrics.items():
            self.logger.log(level, f"  {key}: {value}")

    def log_error_with_context(
        self, error: Exception, context: Optional[str] = None
    ) -> None:
        """
        Log an error with optional context.

        Args:
            error: Exception instance
            context: Optional context string
        """
        if context:
            self.logger.error(f"[ERROR] {context}")
        self.logger.error(f"  Exception: {type(error).__name__}")
        self.logger.error(f"  Message: {str(error)}")
        self.logger.exception("Traceback:")

    def create_log_file(
        self, directory: Path, prefix: str = "context-builder"
    ) -> Path:
        """
        Create a timestamped log file path.

        Args:
            directory: Directory for log file
            prefix: Log file prefix

        Returns:
            Path to log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = directory / f"{prefix}_{timestamp}.log"
        return log_file
