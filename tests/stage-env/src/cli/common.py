"""
Common utilities and helper functions for CLI commands.
"""
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel


# Global console instance
console = Console()


def print_info(message: str):
    """Print informational message."""
    console.print(f"[cyan]ℹ️  {message}[/cyan]")


def print_success(message: str):
    """Print success message."""
    console.print(f"[green]✅ {message}[/green]")


def print_error(message: str):
    """Print error message."""
    console.print(f"[red]❌ {message}[/red]")


def print_warning(message: str):
    """Print warning message."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_panel(title: str, content: str, style: str = "cyan"):
    """Print a styled panel."""
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


def confirm(message: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    from rich.prompt import Confirm
    return Confirm.ask(message, default=default)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def check_prerequisites() -> bool:
    """Check if all required tools are installed."""
    import shutil
    
    required_tools = ["docker", "docker-compose"]
    missing = []
    
    for tool in required_tools:
        if not shutil.which(tool):
            missing.append(tool)
    
    if missing:
        print_error(f"Missing required tools: {', '.join(missing)}")
        print_info("Please install Docker and Docker Compose")
        return False
    
    return True


def setup_logging(verbose: bool = False, json_output: bool = False, log_file: Optional[Path] = None):
    """Setup logging configuration."""
    from ..utils.logger import setup_logging as internal_setup
    internal_setup(verbose=verbose, json_output=json_output, log_file=log_file)
