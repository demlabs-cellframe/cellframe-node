"""
CLI utilities and helpers for stage environment commands.

Provides common CLI functionality like:
- Command execution with logging
- Error handling
- Output formatting
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Tuple, TextIO
from io import StringIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .logger import get_logger, get_log_file, strip_ansi_codes

logger = get_logger(__name__)


class DualOutputConsole:
    """Console wrapper that outputs to both terminal and log file (without colors)."""
    
    def __init__(self):
        self.console = Console()
        self._log_file = None
    
    def _write_to_log(self, text: str):
        """Write text to log file without ANSI codes."""
        log_file_path = get_log_file()
        if log_file_path:
            try:
                with open(log_file_path, 'a', encoding='utf-8') as f:
                    # Strip ANSI codes before writing
                    clean_text = strip_ansi_codes(text)
                    f.write(clean_text)
                    if not clean_text.endswith('\n'):
                        f.write('\n')
            except Exception:
                pass  # Don't break if logging fails
    
    def print(self, *args, **kwargs):
        """Print to console and log."""
        # Capture output to string
        string_io = StringIO()
        temp_console = Console(file=string_io, force_terminal=False)
        temp_console.print(*args, **kwargs)
        output = string_io.getvalue()
        
        # Write to log file
        self._write_to_log(output)
        
        # Print to actual console
        self.console.print(*args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate all other attributes to underlying console."""
        return getattr(self.console, name)


console = DualOutputConsole()


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    capture_output: bool = True,
    check: bool = True,
) -> Tuple[int, str, str]:
    """
    Run a shell command with logging.
    
    Args:
        cmd: Command and arguments as list
        cwd: Working directory
        capture_output: Capture stdout/stderr
        check: Raise exception on non-zero exit
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
        
    Raises:
        subprocess.CalledProcessError: If check=True and command fails
    """
    logger.debug("running_command", cmd=" ".join(cmd), cwd=str(cwd) if cwd else None)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        logger.error(
            "command_failed",
            cmd=" ".join(cmd),
            exit_code=e.returncode,
            stderr=e.stderr,
        )
        raise


def print_success(message: str) -> None:
    """Print success message with green checkmark."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message with red X."""
    # Note: DualOutputConsole doesn't support changing file attribute
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message with yellow exclamation."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message with blue dot."""
    console.print(f"[blue]•[/blue] {message}")


def print_panel(title: str, content: str, style: str = "blue") -> None:
    """Print content in a styled panel."""
    console.print(Panel(content, title=title, style=style))


def print_table(title: str, columns: List[str], rows: List[List[str]]) -> None:
    """
    Print data in a formatted table.
    
    Args:
        title: Table title
        columns: Column headers
        rows: Data rows
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    for col in columns:
        table.add_column(col)
    
    for row in rows:
        table.add_row(*row)
    
    console.print(table)


def confirm(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        message: Confirmation message
        default: Default value if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = console.input(f"{message}{suffix}").strip().lower()
    
    if not response:
        return default
    
    return response in ("y", "yes")


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "1h 30m 45s"
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


def check_prerequisites() -> bool:
    """
    Check if required tools are installed.
    
    Returns:
        True if all prerequisites are met
    """
    required_tools = ["docker", "python3"]
    missing = []
    
    for tool in required_tools:
        try:
            subprocess.run(
                [tool, "--version"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)
    
    if missing:
        print_error(f"Missing required tools: {', '.join(missing)}")
        return False
    
    return True

