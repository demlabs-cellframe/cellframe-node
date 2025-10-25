"""
Unified monitoring manager.

Provides centralized access to all monitoring services:
- Datum tracking (lifecycle monitoring)
- Health checking (nodes, RPC endpoints)

Usage:
    # Get singleton instance
    monitor = MonitoringManager.get_instance()
    
    # Access datum monitor
    result = await monitor.datum.wait_for_datum(...)
    
    # Access health checker
    health = await monitor.health.check_http(...)
"""

from pathlib import Path
from typing import Optional

from .datum import DatumMonitor
from .health import HealthChecker


class MonitoringManager:
    """
    Singleton manager for all monitoring services.
    
    Provides centralized access to:
    - DatumMonitor: Direct datum tracking
    - HealthChecker: Node/endpoint health checks
    """
    
    _instance: Optional["MonitoringManager"] = None
    
    def __init__(
        self,
        node_cli_path: str = "cellframe-node-cli",
        log_file: Optional[Path] = None
    ):
        """
        Initialize monitoring manager.
        
        Args:
            node_cli_path: Path to cellframe-node-cli
            log_file: Optional log file for monitoring events
        """
        self.node_cli_path = node_cli_path
        self.log_file = log_file
        
        # Initialize services
        self.datum = DatumMonitor(
            node_cli_path=node_cli_path,
            log_file=log_file
        )
        
        self.health = HealthChecker(timeout=10.0)
    
    @classmethod
    def get_instance(
        cls,
        node_cli_path: Optional[str] = None,
        log_file: Optional[Path] = None
    ) -> "MonitoringManager":
        """
        Get or create singleton instance.
        
        Args:
            node_cli_path: Path to cellframe-node-cli (only used on first call)
            log_file: Optional log file (only used on first call)
            
        Returns:
            MonitoringManager singleton instance
        """
        if cls._instance is None:
            # First call - create instance with provided params or defaults
            cls._instance = MonitoringManager(
                node_cli_path=node_cli_path or "cellframe-node-cli",
                log_file=log_file
            )
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)."""
        cls._instance = None
