"""
Structured logging configuration using structlog.

Provides consistent logging across all stage environment modules with:
- Structured context
- Colored output for terminal
- JSON output for CI/CD
- Performance timing
"""

import logging
import sys
import re
from pathlib import Path
from typing import Any, Optional

import structlog
from rich.console import Console

# Console for rich output
console = Console()

# Global file handler reference
_file_handler: Optional[logging.FileHandler] = None

# ANSI color code pattern for stripping
_ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')

# Public exports
__all__ = [
    'setup_logging',
    'get_logger',
    'get_log_file',
    'strip_ansi_codes',
    'LogContext',
    'console',
]


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    return _ANSI_PATTERN.sub('', text)


class StripAnsiFormatter(logging.Formatter):
    """Formatter that strips ANSI color codes from log messages."""
    
    def format(self, record):
        message = super().format(record)
        return strip_ansi_codes(message)


def setup_logging(verbose: bool = False, json_output: bool = False, log_file: Optional[Path] = None) -> None:
    """
    Configure structured logging for stage environment.
    
    Args:
        verbose: Enable debug level logging
        json_output: Output logs as JSON (for CI/CD)
        log_file: Optional path to log file
    """
    global _file_handler
    
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add stdout handler (with colors)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(stdout_handler)
    
    # Add file handler if log_file specified (WITHOUT colors)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        _file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        _file_handler.setLevel(log_level)
        # Use formatter that strips ANSI codes
        _file_handler.setFormatter(StripAnsiFormatter("%(message)s"))
        root_logger.addHandler(_file_handler)
    
    # Processors for structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_output:
        # JSON output for CI/CD
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])
    else:
        # Human-readable colored output (colors will be stripped for file)
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Configured structlog logger
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("node_started", node_id=1, role="master")
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager for temporary log context.
    
    Example:
        >>> with LogContext(node_id=1, action="start"):
        ...     logger.info("starting_node")  # Will include node_id and action
    """
    
    def __init__(self, **context: Any):
        self.context = context
        self.token = None
    
    def __enter__(self):
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.unbind_contextvars(*self.context.keys())


def get_log_file() -> Optional[Path]:
    """
    Get current log file path if file logging is enabled.
    
    Returns:
        Path to log file or None if file logging is not enabled
    """
    if _file_handler:
        return Path(_file_handler.baseFilename)
    return None


# Module-level logger
logger = get_logger(__name__)

