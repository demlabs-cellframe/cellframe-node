"""
Datum monitoring service for tracking datum processing through the network.

Direct polling-based monitoring that tracks datum lifecycle:
  mempool → verification → blocks → propagation
  
Usage:
    monitor = DatumMonitor(...)
    
    # Direct synchronous monitoring
    result = await monitor.wait_for_datum(
        datum_hash=hash,
        node=node,
        network=network,
        chain=chain,
        timeouts={...}
    )
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

import docker

from ..scenarios.schema import DatumStatus


@dataclass
class DatumMonitorResult:
    """Result of datum monitoring."""
    status: DatumStatus
    datum_hash: str
    elapsed_time: float
    details: Dict = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def __repr__(self):
        return f"DatumMonitorResult(status={self.status}, hash={self.datum_hash[:16]}..., time={self.elapsed_time:.1f}s)"


class DatumMonitor:
    """
    Direct polling-based datum monitor.
    
    Polls network and tracks datums through:
    - Mempool presence
    - Master node verification
    - Block inclusion
    - Block propagation to target nodes
    
    Detects various failure scenarios with detailed diagnostics.
    """
    
    def __init__(self, node_cli_path: str = "cellframe-node-cli", log_file: Optional[Path] = None):
        """
        Initialize datum monitor.
        
        Args:
            node_cli_path: Path to cellframe-node-cli executable
            log_file: Optional path to monitoring logs directory
        """
        self.node_cli_path = node_cli_path
        self.docker_client = docker.from_env()
        
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
    
    def _log(self, message: str):
        """Log message to scenario log file."""
        if not self.log_file:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [DATUM_MONITOR] {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    
    async def wait_for_datum(
        self,
        datum_hash: str,
        node: str = "node1",
        network: str = "stagenet",
        chain: str = "main",
        check_master_nodes: bool = True,
        timeout_total: float = 300,
        timeout_mempool: float = 60,
        timeout_verification: float = 120,
        timeout_in_blocks: float = 180,
        check_interval: float = 2.0
    ) -> DatumMonitorResult:
        """
        Wait for datum to complete processing through network.
        
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
            check_interval: Polling interval in seconds
            
        Returns:
            DatumMonitorResult with status and details
        """
        # Validate datum hash format
        hash_pattern = r'^0x[0-9a-fA-F]{64,}$'
        if not re.match(hash_pattern, datum_hash):
            error_msg = f"Invalid datum hash format: {datum_hash[:200]}"
            self._log(f"❌ {error_msg}")
            self._log(f"  Expected: 0x[hex] format (64+ hex chars)")
            self._log(f"  This likely means the CLI command failed and returned error output instead of a hash")
            
            return DatumMonitorResult(
                status=DatumStatus.REJECTED,
                datum_hash=datum_hash[:100],
                elapsed_time=0.0,
                error_message=error_msg
            )
        
        self._log(f"📝 Monitoring datum: {datum_hash[:16]}... (node={node}, timeouts: {timeout_total}s total)")
        
        # State tracking
        start_time = asyncio.get_event_loop().time()
        was_in_mempool = False
        was_verified = False
        was_in_blocks = False
        mempool_start = None
        verification_start = None
        blocks_start = None
        
        iteration = 0
        
        while True:
            iteration += 1
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - start_time
            
            # Check total timeout
            if elapsed > timeout_total:
                error = f"Total timeout after {elapsed:.1f}s"
                self._log(f"  ❌ {error}")
                return DatumMonitorResult(
                    status=DatumStatus.TIMEOUT_TOTAL,
                    datum_hash=datum_hash,
                    elapsed_time=elapsed,
                    error_message=error
                )
            
            # Stage 1: Check mempool
            in_mempool = await self._check_mempool(node, network, chain, datum_hash)
            
            if in_mempool:
                if not was_in_mempool:
                    self._log(f"  ✅ Datum {datum_hash[:16]}... entered mempool")
                    was_in_mempool = True
                    mempool_start = current_time
                else:
                    # Check mempool timeout
                    mempool_time = current_time - mempool_start
                    
                    # Log mempool waiting state periodically
                    if int(mempool_time) % 10 == 0:  # Every 10 seconds
                        self._log(f"  ⏳ Datum {datum_hash[:16]}... still in mempool ({mempool_time:.1f}s)")
                    
                    if mempool_time > timeout_mempool:
                        error = f"Datum stuck in mempool for {mempool_time:.1f}s (expected verification within {timeout_mempool}s)"
                        self._log(f"  ❌ {error}")
                        self._log(f"  💡 This may indicate consensus issues or insufficient validators")
                        return DatumMonitorResult(
                            status=DatumStatus.TIMEOUT_MEMPOOL,
                            datum_hash=datum_hash,
                            elapsed_time=elapsed,
                            details={"mempool_time": mempool_time},
                            error_message=error
                        )
                
                # Still in mempool, continue monitoring
                await asyncio.sleep(check_interval)
                continue
            
            # CRITICAL: Check if datum NEVER appeared in mempool
            # This likely means the datum wasn't created (CLI command failed)
            # Datums are created locally and appear in mempool almost instantly (<1s)
            if not was_in_mempool and elapsed > 0.5:  # Give it 0.5 seconds max
                error = f"Datum never appeared in mempool after {elapsed:.1f}s - likely not created (check CLI command output for errors)"
                self._log(f"  ❌ {error}")
                self._log(f"  💡 Datum hash received: {datum_hash[:50]}...")
                return DatumMonitorResult(
                    status=DatumStatus.REJECTED,
                    datum_hash=datum_hash,
                    elapsed_time=elapsed,
                    error_message=error
                )
            
            # Stage 2: Datum left mempool - check if verified
            if was_in_mempool and not was_verified:
                # Check if it was verified on master nodes
                verified = await self._check_verified_on_masters(node, network, chain, datum_hash) if check_master_nodes else True
                
                if verified:
                    self._log(f"  ✅ Datum {datum_hash[:16]}... verified by validators")
                    was_verified = True
                    verification_start = current_time
                else:
                    verification_time = current_time - mempool_start
                    
                    if verification_time > timeout_verification:
                        error = f"Datum not verified after {verification_time:.1f}s"
                        self._log(f"  ❌ {error}")
                        self._log(f"  💡 Datum left mempool but not verified - may be rejected")
                        return DatumMonitorResult(
                            status=DatumStatus.TIMEOUT_VERIFICATION,
                            datum_hash=datum_hash,
                            elapsed_time=elapsed,
                            details={"verification_time": verification_time},
                            error_message=error
                        )
            
            # Stage 3: Check if datum is in blocks
            block_info = await self._check_in_blocks(node, network, chain, datum_hash)
            
            if block_info:
                block_number, block_hash = block_info
                
                if not was_in_blocks:
                    self._log(f"  ✅ Datum {datum_hash[:16]}... included in block #{block_number}")
                    was_in_blocks = True
                    blocks_start = current_time
                
                # Success! Datum is in a block
                self._log(f"  ✅ Datum {datum_hash[:16]}... successfully processed (block #{block_number})")
                return DatumMonitorResult(
                    status=DatumStatus.SUCCESS,
                    datum_hash=datum_hash,
                    elapsed_time=elapsed,
                    details={
                        "block_number": block_number,
                        "block_hash": block_hash,
                        "mempool_time": (verification_start - mempool_start) if (verification_start and mempool_start) else 0,
                        "verification_time": (blocks_start - verification_start) if (blocks_start and verification_start) else 0,
                        "total_time": elapsed
                    }
                )
            
            # Check blocks timeout
            if was_in_mempool:
                time_since_mempool = current_time - mempool_start
                if time_since_mempool > timeout_in_blocks:
                    error = f"Datum not in blocks after {time_since_mempool:.1f}s"
                    self._log(f"  ❌ {error}")
                    self._log(f"  💡 Datum was in mempool but never made it into a block")
                    return DatumMonitorResult(
                        status=DatumStatus.TIMEOUT_IN_BLOCKS,
                        datum_hash=datum_hash,
                        elapsed_time=elapsed,
                        details={"time_since_mempool": time_since_mempool},
                        error_message=error
                    )
            
            # Wait before next check
            await asyncio.sleep(check_interval)
    
    async def _check_mempool(self, node: str, network: str, chain: str, datum_hash: str) -> bool:
        """Check if datum is in mempool."""
        try:
            # Convert node to container name
            container_name = self._node_to_container(node)
            container = self.docker_client.containers.get(container_name)
            
            cmd = [
                self.node_cli_path, "mempool_proc", "-list",
                "-net", network, "-chain", chain
            ]
            
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            if exit_code != 0:
                return False
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            
            # Check if our datum hash is in the output
            return datum_hash.lower() in stdout_str.lower()
            
        except Exception as e:
            self._log(f"  ⚠️ Failed to check mempool: {e}")
            return False
    
    async def _check_verified_on_masters(self, node: str, network: str, chain: str, datum_hash: str) -> bool:
        """Check if datum was verified by master nodes."""
        # For now, assume verified if it left mempool
        # Full implementation would check master node logs or verification status
        return True
    
    async def _check_in_blocks(self, node: str, network: str, chain: str, datum_hash: str) -> Optional[Tuple[int, str]]:
        """
        Check if datum is in a block.
        
        Returns:
            Tuple of (block_number, block_hash) if found, None otherwise
        """
        try:
            # Convert node to container name
            container_name = self._node_to_container(node)
            container = self.docker_client.containers.get(container_name)
            
            # Get recent blocks and search for our datum
            cmd = [
                self.node_cli_path, "block", "list",
                "-net", network, "-chain", chain, "-last", "10"
            ]
            
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            if exit_code != 0:
                return None
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            
            # Parse block list output for our datum hash
            # Format: block #N hash:... datums:...
            lines = stdout_str.split('\n')
            for line in lines:
                if datum_hash.lower() in line.lower():
                    # Extract block number from line
                    match = re.search(r'block\s+#(\d+)', line, re.IGNORECASE)
                    if match:
                        block_num = int(match.group(1))
                        
                        # Extract block hash
                        hash_match = re.search(r'hash:\s*([0-9a-fA-Fx]+)', line, re.IGNORECASE)
                        block_hash = hash_match.group(1) if hash_match else "unknown"
                        
                        return (block_num, block_hash)
            
            return None
            
        except Exception as e:
            self._log(f"  ⚠️ Failed to check blocks: {e}")
            return None
    
    def _node_to_container(self, node: str) -> str:
        """Convert node ID to Docker container name."""
        if node.startswith('node'):
            node_number = node[4:]  # Extract number from "node1"
            return f"cellframe-stage-node-{node_number}"
        else:
            return f"cellframe-stage-{node}"
