"""
Monitoring subsystem for cellframe test infrastructure.

Provides unified access to:
- Health checking (nodes, endpoints)
- Datum lifecycle tracking
- Network consensus and integrity validation
- Artifacts collection

Usage:
    from monitoring import MonitoringManager
    
    monitor = await MonitoringManager.get_instance()
    await monitor.start()
    
    # Track datum
    result = await monitor.datum.track_datum(hash, ...)
    
    # Check health
    status = await monitor.health.check_http(url, node_id)
    
    # Check network consensus
    from monitoring import NetworkConsensusMonitor
    consensus = NetworkConsensusMonitor(nodes, ...)
    await consensus.wait_for_network_ready()
    
    await monitor.stop()
"""

from .manager import MonitoringManager
from .datum import DatumMonitor, DatumMonitorResult
from .health import HealthChecker, HealthStatus
from .network_consensus import (
    NetworkConsensusMonitor,
    NetworkConsensusState,
    NodeMetrics,
    MempoolMetrics,
    ConsensusMetrics,
    ESBocsRoundState
)

__all__ = [
    "MonitoringManager",
    "DatumMonitor",
    "DatumMonitorResult",
    "HealthChecker",
    "HealthStatus",
    "NetworkConsensusMonitor",
    "NetworkConsensusState",
    "NodeMetrics",
    "MempoolMetrics",
    "ConsensusMetrics",
    "ESBocsRoundState",
]

