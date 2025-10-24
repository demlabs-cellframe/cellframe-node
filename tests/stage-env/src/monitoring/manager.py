"""
Unified monitoring manager singleton.

Provides centralized access to all monitoring services:
- Health checking (nodes, RPC endpoints)
- Datum tracking (lifecycle monitoring)
- Artifacts collection

Usage:
    # Get singleton instance
    monitor = MonitoringManager.get_instance()
    
    # Start all services
    await monitor.start()
    
    # Access datum monitor
    datum_future = monitor.datum.track_datum(...)
    
    # Access health checker
    health = await monitor.health.check_http(...)
    
    # Stop all services
    await monitor.stop()
"""

import asyncio
from pathlib import Path
from typing import Optional

from .datum import DatumMonitor
from .health import HealthChecker


class MonitoringManager:
    """
    Singleton manager for all monitoring services.
    
    Provides centralized lifecycle management and access to:
    - DatumMonitor: Background datum tracking
    - HealthChecker: Node/endpoint health checks
    """
    
    _instance: Optional["MonitoringManager"] = None
    _lock = asyncio.Lock()
    
    def __init__(
        self,
        node_cli_path: str = "cellframe-node-cli",
        log_file: Optional[Path] = None,
        datum_check_interval: float = 2.0
    ):
        """
        Initialize monitoring manager.
        
        Args:
            node_cli_path: Path to cellframe-node-cli
            log_file: Optional log file for monitoring events
            datum_check_interval: Check interval for datum monitor
        """
        self.node_cli_path = node_cli_path
        self.log_file = log_file
        
        # Initialize services
        self.datum = DatumMonitor(
            node_cli_path=node_cli_path,
            log_file=log_file,
            check_interval=datum_check_interval
        )
        
        self.health = HealthChecker(timeout=10.0)
        
        self._started = False
    
    @classmethod
    async def get_instance(
        cls,
        node_cli_path: Optional[str] = None,
        log_file: Optional[Path] = None,
        datum_check_interval: Optional[float] = None
    ) -> "MonitoringManager":
        """
        Get or create singleton instance.
        
        Args:
            node_cli_path: Path to cellframe-node-cli (only used on first call)
            log_file: Optional log file (only used on first call)
            datum_check_interval: Check interval (only used on first call)
            
        Returns:
            MonitoringManager singleton instance
        """
        async with cls._lock:
            if cls._instance is None:
                # First call - create instance with provided params or defaults
                cls._instance = MonitoringManager(
                    node_cli_path=node_cli_path or "cellframe-node-cli",
                    log_file=log_file,
                    datum_check_interval=datum_check_interval or 2.0
                )
            return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)."""
        cls._instance = None
    
    async def start(self):
        """Start all monitoring services."""
        if self._started:
            return
        
        # Start datum monitor (background service)
        await self.datum.start()
        
        # Health checker is stateless, no start needed
        
        self._started = True
    
    async def stop(self):
        """Stop all monitoring services."""
        if not self._started:
            return
        
        # Stop datum monitor
        await self.datum.stop()
        
        # Close health checker HTTP client
        await self.health.client.aclose()
        
        self._started = False
    
    def is_started(self) -> bool:
        """Check if monitoring services are started."""
        return self._started

