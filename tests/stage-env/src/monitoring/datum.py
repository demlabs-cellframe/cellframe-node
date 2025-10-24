"""
Datum monitoring service for tracking datum processing through the network.

Background service that continuously monitors network for datum lifecycle:
  mempool → verification → blocks → propagation
  
Usage:
    # Start monitor service at scenario beginning
    monitor = DatumMonitor(...)
    await monitor.start()
    
    # Register datum for tracking during test execution
    result_future = monitor.track_datum(datum_hash, node, network, chain, timeouts)
    
    # Wait for result
    result = await result_future
    
    # Stop service at scenario end
    await monitor.stop()
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from ..scenarios.schema import DatumStatus


@dataclass
class DatumTrackingRequest:
    """Request to track a specific datum."""
    datum_hash: str
    node: str
    network: str
    chain: str
    check_master_nodes: bool
    timeout_total: float
    timeout_mempool: float
    timeout_verification: float
    timeout_in_blocks: float
    start_time: float
    
    # Result tracking
    future: asyncio.Future = field(default_factory=asyncio.Future)
    
    # State
    was_in_mempool: bool = False
    was_verified: bool = False
    was_in_blocks: bool = False
    block_number: Optional[int] = None
    
    mempool_start: Optional[float] = None
    verification_start: Optional[float] = None
    blocks_start: Optional[float] = None


class DatumMonitorResult:
    """Result of datum monitoring."""
    
    def __init__(
        self,
        status: DatumStatus,
        datum_hash: str,
        elapsed_time: float,
        details: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        self.status = status
        self.datum_hash = datum_hash
        self.elapsed_time = elapsed_time
        self.details = details or {}
        self.error_message = error_message
    
    def __repr__(self):
        return f"DatumMonitorResult(status={self.status}, hash={self.datum_hash[:16]}..., time={self.elapsed_time:.1f}s)"


class DatumMonitor:
    """
    Background service monitoring datum processing through all network stages.
    
    Continuously polls network and tracks registered datums through:
    - Mempool presence
    - Master node verification  
    - Block inclusion
    - Block propagation to target nodes
    
    Detects various failure scenarios with detailed diagnostics.
    """
    
    def __init__(self, node_cli_path: str = "cellframe-node-cli", log_file: Optional[Path] = None, check_interval: float = 2.0):
        """
        Initialize datum monitor service.
        
        Args:
            node_cli_path: Path to cellframe-node-cli executable
            log_file: Optional path to monitoring logs directory (will create datum-monitor.log inside)
            check_interval: Global check interval in seconds
        """
        self.node_cli_path = node_cli_path
        
        # Create separate datum monitor log
        if log_file:
            log_path = Path(log_file)
            
            # If it's a directory, create health-logs inside it
            if log_path.is_dir():
                health_logs = log_path / "health-logs"
                health_logs.mkdir(parents=True, exist_ok=True)
                self.log_file = health_logs / "datum-monitor.log"
            else:
                # It's a file path, use its parent directory
                health_logs = log_path.parent / "health-logs"
                health_logs.mkdir(parents=True, exist_ok=True)
                self.log_file = health_logs / "datum-monitor.log"
        else:
            self.log_file = None
        
        self.check_interval = check_interval
        
        # Tracking state
        self._tracking: Dict[str, DatumTrackingRequest] = {}
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    def _log(self, message: str):
        """Log message to scenario log file."""
        if not self.log_file:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [DATUM_MONITOR] {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    
    async def start(self):
        """Start background monitoring service."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        self._log("🚀 Datum monitor service started")
    
    async def stop(self):
        """Stop background monitoring service."""
        if not self._running:
            return
        
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Complete any pending futures with timeout
        async with self._lock:
            for req in self._tracking.values():
                if not req.future.done():
                    elapsed = asyncio.get_event_loop().time() - req.start_time
                    req.future.set_result(DatumMonitorResult(
                        status=DatumStatus.TIMEOUT_TOTAL,
                        datum_hash=req.datum_hash,
                        elapsed_time=elapsed,
                        error_message="Monitor service stopped before datum completed"
                    ))
        
        self._log("🛑 Datum monitor service stopped")
    
    def track_datum(
        self,
        datum_hash: str,
        node: str = "node1",
        network: str = "stagenet",
        chain: str = "main",
        check_master_nodes: bool = True,
        timeout_total: float = 300,
        timeout_mempool: float = 60,
        timeout_verification: float = 120,
        timeout_in_blocks: float = 180
    ) -> asyncio.Future:
        """
        Register datum for tracking.
        
        Args:
            datum_hash: Datum hash to monitor
            node: Target node to check
            network: Network name
            chain: Chain name
            check_master_nodes: Whether to check master nodes
            timeout_total: Total timeout in seconds
            timeout_mempool: Max time in mempool
            timeout_verification: Max time after verification
            timeout_in_blocks: Max time after block inclusion
            
        Returns:
            Future that resolves to DatumMonitorResult
        """
        if not self._running:
            raise RuntimeError("Datum monitor service is not running")
        
        request = DatumTrackingRequest(
            datum_hash=datum_hash,
            node=node,
            network=network,
            chain=chain,
            check_master_nodes=check_master_nodes,
            timeout_total=timeout_total,
            timeout_mempool=timeout_mempool,
            timeout_verification=timeout_verification,
            timeout_in_blocks=timeout_in_blocks,
            start_time=asyncio.get_event_loop().time()
        )
        
        # Register for tracking
        self._tracking[datum_hash] = request
        
        self._log(f"📝 Registered datum for tracking: {datum_hash[:16]}... (node={node}, timeouts: {timeout_total}s total)")
        
        return request.future
    
    async def _monitoring_loop(self):
        """Main monitoring loop - runs in background."""
        self._log("🔄 Monitoring loop started")
        
        try:
            while self._running:
                # Process all tracked datums
                async with self._lock:
                    completed = []
                    
                    for datum_hash, req in list(self._tracking.items()):
                        if req.future.done():
                            completed.append(datum_hash)
                            continue
                        
                        # Check this datum
                        result = await self._check_datum(req)
                        
                        if result:
                            # Datum completed (success or failure)
                            req.future.set_result(result)
                            completed.append(datum_hash)
                    
                    # Remove completed datums
                    for datum_hash in completed:
                        del self._tracking[datum_hash]
                
                # Sleep before next check
                await asyncio.sleep(self.check_interval)
        
        except asyncio.CancelledError:
            self._log("⚠️ Monitoring loop cancelled")
            raise
        except Exception as e:
            self._log(f"❌ Monitoring loop error: {e}")
            raise
    
    async def _check_datum(self, req: DatumTrackingRequest) -> Optional[DatumMonitorResult]:
        """
        Check single datum state and return result if completed.
        
        Returns:
            DatumMonitorResult if datum completed (success or failure), None if still in progress
        """
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - req.start_time
        
        # Check total timeout
        if elapsed > req.timeout_total:
            error = f"Total timeout after {elapsed:.1f}s"
            return DatumMonitorResult(
                status=DatumStatus.TIMEOUT_TOTAL,
                datum_hash=req.datum_hash,
                elapsed_time=elapsed,
                error_message=error
            )
        
        # Stage 1: Check mempool
        in_mempool = await self._check_mempool(req.node, req.network, req.chain, req.datum_hash)
        
        if in_mempool:
            if not req.was_in_mempool:
                self._log(f"  ✅ Datum {req.datum_hash[:16]}... entered mempool")
                req.was_in_mempool = True
                req.mempool_start = current_time
            else:
                # Check mempool timeout
                mempool_time = current_time - req.mempool_start
                if mempool_time > req.timeout_mempool:
                    error = f"Datum stuck in mempool for {mempool_time:.1f}s (expected verification within {req.timeout_mempool}s)"
                    return DatumMonitorResult(
                        status=DatumStatus.TIMEOUT_MEMPOOL,
                        datum_hash=req.datum_hash,
                        elapsed_time=elapsed,
                        details={"mempool_time": mempool_time},
                        error_message=error
                    )
            
            # Still in mempool, continue monitoring
            return None
        
        # Stage 2: Datum left mempool - check if verified
        if req.was_in_mempool and not req.was_verified and req.check_master_nodes:
            master_nodes = ["node1", "node2", "node3"]  # Standard stagenet
            verified = await self._check_verified(master_nodes, req.network, req.datum_hash)
            
            if verified:
                self._log(f"  ✅ Datum {req.datum_hash[:16]}... verified by master nodes")
                req.was_verified = True
                req.verification_start = current_time
            else:
                # Datum left mempool but not verified - might be rejected
                if elapsed > 10:  # Give it at least 10 seconds
                    error = "Datum disappeared from mempool without verification (likely rejected)"
                    return DatumMonitorResult(
                        status=DatumStatus.REJECTED,
                        datum_hash=req.datum_hash,
                        elapsed_time=elapsed,
                        error_message=error
                    )
        
        # Stage 3: Check if in blocks
        if req.check_master_nodes:
            master_nodes = ["node1", "node2", "node3"]
            in_blocks, block_num = await self._check_in_blocks(master_nodes, req.network, req.chain, req.datum_hash)
        else:
            in_blocks, block_num = await self._check_in_blocks([req.node], req.network, req.chain, req.datum_hash)
        
        if in_blocks:
            if not req.was_in_blocks:
                self._log(f"  ✅ Datum {req.datum_hash[:16]}... included in blocks")
                req.was_in_blocks = True
                req.blocks_start = current_time
                req.block_number = block_num
            
            # Stage 4: Check if propagated to target node
            if req.check_master_nodes:
                propagated = await self._check_propagated(req.node, req.network, req.chain, req.block_number)
                if propagated:
                    self._log(f"  🎉 Datum {req.datum_hash[:16]}... successfully propagated to {req.node}")
                    return DatumMonitorResult(
                        status=DatumStatus.PROPAGATED,
                        datum_hash=req.datum_hash,
                        elapsed_time=elapsed,
                        details={
                            "block_number": req.block_number,
                            "was_in_mempool": req.was_in_mempool,
                            "was_verified": req.was_verified
                        }
                    )
                
                # Check blocks propagation timeout
                blocks_time = current_time - req.blocks_start
                if blocks_time > req.timeout_in_blocks:
                    error = f"Block #{req.block_number} didn't propagate to {req.node} within {req.timeout_in_blocks}s"
                    return DatumMonitorResult(
                        status=DatumStatus.TIMEOUT_BLOCKS,
                        datum_hash=req.datum_hash,
                        elapsed_time=elapsed,
                        details={"block_number": req.block_number, "blocks_time": blocks_time},
                        error_message=error
                    )
            else:
                # Not checking masters - datum in blocks on target is success
                return DatumMonitorResult(
                    status=DatumStatus.IN_BLOCKS,
                    datum_hash=req.datum_hash,
                    elapsed_time=elapsed,
                    details={"block_number": req.block_number}
                )
        
        # Check verification timeout
        if req.was_verified and not req.was_in_blocks:
            verification_time = current_time - req.verification_start
            if verification_time > req.timeout_verification:
                error = f"Datum verified but not in blocks after {verification_time:.1f}s (timeout: {req.timeout_verification}s)"
                return DatumMonitorResult(
                    status=DatumStatus.TIMEOUT_VERIFICATION,
                    datum_hash=req.datum_hash,
                    elapsed_time=elapsed,
                    details={"verification_time": verification_time},
                    error_message=error
                )
        
        # Still in progress
        return None
    
    async def _run_cli(self, node: str, command: str) -> Tuple[int, str, str]:
        """Run CLI command on a node."""
        container_name = f"cellframe-stage-node-{node.replace('node', '')}"
        full_cmd = ["docker", "exec", container_name, self.node_cli_path] + command.split()
        
        proc = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')
    
    async def _check_mempool(self, node: str, network: str, chain: str, datum_hash: str) -> bool:
        """Check if datum is in mempool."""
        exit_code, stdout, stderr = await self._run_cli(
            node,
            f"mempool proc -net {network} -chain {chain}"
        )
        
        if exit_code != 0:
            return False
        
        return datum_hash.lower() in stdout.lower()
    
    async def _check_verified(self, master_nodes: List[str], network: str, datum_hash: str) -> bool:
        """Check if datum was verified by master nodes."""
        for node in master_nodes:
            exit_code, stdout, stderr = await self._run_cli(
                node,
                f"tx_history -net {network} -tx {datum_hash}"
            )
            
            if exit_code == 0 and datum_hash.lower() in stdout.lower():
                return True
        
        return False
    
    async def _check_in_blocks(
        self,
        nodes: List[str],
        network: str,
        chain: str,
        datum_hash: str
    ) -> Tuple[bool, Optional[int]]:
        """Check if datum is included in blocks."""
        for node in nodes:
            exit_code, stdout, stderr = await self._run_cli(
                node,
                f"chain ca -net {network} -chain {chain} -datum {datum_hash}"
            )
            
            if exit_code == 0:
                # Parse block number
                block_match = re.search(r'block\s*#?(\d+)', stdout, re.IGNORECASE)
                if block_match:
                    return True, int(block_match.group(1))
                elif "found" in stdout.lower():
                    return True, None
        
        return False, None
    
    async def _check_propagated(self, node: str, network: str, chain: str, block_num: Optional[int]) -> bool:
        """Check if block with datum propagated to target node."""
        if block_num is None:
            return False
        
        exit_code, stdout, stderr = await self._run_cli(
            node,
            f"chain info -net {network} -chain {chain}"
        )
        
        if exit_code != 0:
            return False
        
        # Parse current block height
        height_match = re.search(r'(?:block\s*)?height[:\s]+(\d+)', stdout, re.IGNORECASE)
        if not height_match:
            return False
        
        current_height = int(height_match.group(1))
        return current_height >= block_num
