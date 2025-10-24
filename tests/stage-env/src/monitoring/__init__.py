"""
Monitoring subsystem for cellframe test infrastructure.

Provides unified access to:
- Health checking (nodes, endpoints)
- Datum lifecycle tracking
- Artifacts collection

Usage:
    from monitoring import MonitoringManager
    
    monitor = await MonitoringManager.get_instance()
    await monitor.start()
    
    # Track datum
    result = await monitor.datum.track_datum(hash, ...)
    
    # Check health
    status = await monitor.health.check_http(url, node_id)
    
    await monitor.stop()
"""

from .manager import MonitoringManager
from .datum import DatumMonitor, DatumMonitorResult
from .health import HealthChecker, HealthStatus

__all__ = [
    "MonitoringManager",
    "DatumMonitor",
    "DatumMonitorResult",
    "HealthChecker",
    "HealthStatus",
]

