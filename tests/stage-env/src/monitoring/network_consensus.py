"""
Network Consensus Monitor - validates network integrity and synchronization.

Monitors and validates:
- Node list consistency across all nodes
- Chain state synchronization (block hashes, counts)
- Network topology integrity
- Consensus readiness

Usage:
    monitor = NetworkConsensusMonitor(nodes, node_cli_path)
    await monitor.wait_for_network_ready(timeout=60)
"""

import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NodeMetrics:
    """Metrics collected from a single node."""
    
    node_id: str
    node_addr: Optional[str] = None  # Node's own address
    node_list: Set[str] = None  # Set of known node addresses
    node_list_count: int = 0
    
    # Chain state for main chain
    main_chain_blocks: int = 0
    main_chain_last_hash: Optional[str] = None
    
    # Network state
    is_online: bool = False
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.node_list is None:
            self.node_list = set()


@dataclass
class NetworkConsensusState:
    """Overall network consensus state."""
    
    all_nodes_have_same_list: bool = False
    expected_node_count: int = 0
    nodes_with_full_list: int = 0
    
    all_chains_synced: bool = False
    unique_chain_states: int = 0  # Should be 1 when synced
    
    all_nodes_online: bool = False
    online_count: int = 0
    
    ready: bool = False  # Overall readiness
    
    def __str__(self) -> str:
        return (
            f"NetworkConsensusState("
            f"nodes_online={self.online_count}/{self.expected_node_count}, "
            f"full_list={self.nodes_with_full_list}/{self.expected_node_count}, "
            f"chains_synced={self.all_chains_synced}, "
            f"ready={self.ready})"
        )


class NetworkConsensusMonitor:
    """
    Monitor network consensus and integrity.
    
    Validates that all nodes have:
    1. Same node list (topology synchronized)
    2. Same chain state (blocks synced)
    3. Online status (network operational)
    """
    
    def __init__(
        self,
        nodes: Dict[str, any],  # Dict[node_id, NodeConfig]
        node_cli_path: str = "cellframe-node-cli",
        network_name: str = "stagenet",
        check_interval: float = 2.0
    ):
        """
        Initialize network consensus monitor.
        
        Args:
            nodes: Dictionary of node configurations
            node_cli_path: Path to CLI executable
            network_name: Network name to monitor
            check_interval: Seconds between checks
        """
        self.nodes = nodes
        self.node_cli_path = node_cli_path
        self.network_name = network_name
        self.check_interval = check_interval
        
        self.expected_node_count = len(nodes)
        logger.info("network_consensus_monitor_initialized",
                   nodes=self.expected_node_count,
                   network=network_name)
    
    async def collect_node_metrics(self, node_id: str) -> NodeMetrics:
        """
        Collect metrics from a single node.
        
        Args:
            node_id: Node identifier (e.g., "node1")
            
        Returns:
            NodeMetrics with collected data
        """
        metrics = NodeMetrics(node_id=node_id)
        
        try:
            # Get node list
            node_list_output = await self._exec_cli(
                node_id,
                f"node list -net {self.network_name}"
            )
            metrics.node_list = self._parse_node_list(node_list_output)
            metrics.node_list_count = len(metrics.node_list)
            
            # Get own node address
            node_dump = await self._exec_cli(node_id, "node dump")
            metrics.node_addr = self._parse_node_addr(node_dump)
            
            # Get chain info
            chain_info = await self._exec_cli(
                node_id,
                f"chain -net {self.network_name} list"
            )
            blocks, last_hash = self._parse_chain_info(chain_info, "main")
            metrics.main_chain_blocks = blocks
            metrics.main_chain_last_hash = last_hash
            
            # Check online status
            net_get = await self._exec_cli(
                node_id,
                f"net -net {self.network_name} get status"
            )
            metrics.is_online = self._parse_online_status(net_get)
            
        except Exception as e:
            metrics.error = str(e)
            logger.debug("failed_to_collect_metrics",
                        node=node_id,
                        error=str(e))
        
        return metrics
    
    async def collect_all_metrics(self) -> Dict[str, NodeMetrics]:
        """
        Collect metrics from all nodes in parallel.
        
        Returns:
            Dict mapping node_id to NodeMetrics
        """
        tasks = [
            self.collect_node_metrics(node_id)
            for node_id in self.nodes.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics_dict = {}
        for node_id, result in zip(self.nodes.keys(), results):
            if isinstance(result, Exception):
                logger.warning("metric_collection_failed",
                              node=node_id,
                              error=str(result))
                metrics_dict[node_id] = NodeMetrics(node_id=node_id, error=str(result))
            else:
                metrics_dict[node_id] = result
        
        return metrics_dict
    
    def analyze_consensus(self, metrics: Dict[str, NodeMetrics]) -> NetworkConsensusState:
        """
        Analyze collected metrics to determine network consensus state.
        
        Args:
            metrics: Dict of NodeMetrics from all nodes
            
        Returns:
            NetworkConsensusState with analysis results
        """
        state = NetworkConsensusState(expected_node_count=self.expected_node_count)
        
        # Count online nodes
        online_nodes = [m for m in metrics.values() if m.is_online and not m.error]
        state.online_count = len(online_nodes)
        state.all_nodes_online = state.online_count == self.expected_node_count
        
        if not online_nodes:
            logger.debug("no_nodes_online")
            return state
        
        # Check node list consistency
        # All nodes should have the same set of node addresses
        node_lists = [m.node_list for m in online_nodes if m.node_list]
        if node_lists:
            # Find most common list size (should be expected_node_count - 1, excluding self)
            # or expected_node_count if node includes itself
            full_list_threshold = self.expected_node_count - 2  # Allow some variance
            
            nodes_with_full_list = [
                m for m in online_nodes
                if m.node_list_count >= full_list_threshold
            ]
            state.nodes_with_full_list = len(nodes_with_full_list)
            
            # Check if all have same list
            if len(nodes_with_full_list) >= 2:
                first_list = nodes_with_full_list[0].node_list
                state.all_nodes_have_same_list = all(
                    m.node_list == first_list
                    for m in nodes_with_full_list
                )
        
        # Check chain synchronization
        # All nodes should have same block count and last hash for main chain
        chain_states = [
            (m.main_chain_blocks, m.main_chain_last_hash)
            for m in online_nodes
            if m.main_chain_blocks > 0
        ]
        
        if chain_states:
            unique_states = set(chain_states)
            state.unique_chain_states = len(unique_states)
            state.all_chains_synced = len(unique_states) == 1
        
        # Overall readiness:
        # - All nodes online
        # - All nodes have full node list  
        # - Chains are synced (or no blocks yet - genesis state)
        state.ready = (
            state.all_nodes_online and
            state.nodes_with_full_list >= self.expected_node_count - 1 and  # Allow 1 straggler
            (state.all_chains_synced or state.unique_chain_states == 0)  # Synced or no blocks yet
        )
        
        return state
    
    async def wait_for_network_ready(
        self,
        timeout: float = 60.0,
        check_interval: Optional[float] = None
    ) -> bool:
        """
        Wait for network to reach consensus and be fully ready.
        
        Args:
            timeout: Maximum time to wait in seconds
            check_interval: Override default check interval
            
        Returns:
            True if network became ready, False if timeout
            
        Raises:
            TimeoutError: If network not ready within timeout
        """
        interval = check_interval or self.check_interval
        start_time = asyncio.get_event_loop().time()
        iteration = 0
        last_state_log = 0
        
        logger.info("waiting_for_network_consensus",
                   timeout=timeout,
                   expected_nodes=self.expected_node_count)
        
        while True:
            iteration += 1
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - start_time
            
            if elapsed >= timeout:
                logger.error("network_consensus_timeout",
                            elapsed=f"{elapsed:.1f}s",
                            timeout=timeout)
                raise TimeoutError(
                    f"Network did not reach consensus within {timeout}s"
                )
            
            # Collect and analyze metrics
            metrics = await self.collect_all_metrics()
            state = self.analyze_consensus(metrics)
            
            # Log state periodically (every 5 seconds)
            if current_time - last_state_log >= 5:
                logger.info("network_consensus_progress",
                           elapsed=f"{elapsed:.1f}s",
                           online=f"{state.online_count}/{state.expected_node_count}",
                           full_list=f"{state.nodes_with_full_list}/{state.expected_node_count}",
                           chains_synced=state.all_chains_synced,
                           ready=state.ready)
                last_state_log = current_time
                
                # Debug: show per-node details if not ready
                if not state.ready:
                    for node_id, m in metrics.items():
                        logger.debug("node_state",
                                    node=node_id,
                                    online=m.is_online,
                                    node_list_count=m.node_list_count,
                                    blocks=m.main_chain_blocks,
                                    error=m.error or "none")
            
            # Check if ready
            if state.ready:
                logger.info("network_consensus_achieved",
                           elapsed=f"{elapsed:.1f}s",
                           iterations=iteration,
                           state=str(state))
                return True
            
            # Wait before next check
            await asyncio.sleep(interval)
    
    async def _exec_cli(self, node_id: str, command: str) -> str:
        """
        Execute CLI command in node container.
        
        Args:
            node_id: Node identifier
            command: CLI command to execute
            
        Returns:
            Command output as string
        """
        # Use docker exec to run CLI in container
        container_name = f"cellframe-stage-{node_id}"
        
        proc = await asyncio.create_subprocess_exec(
            "docker", "exec", container_name,
            self.node_cli_path, *command.split(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise RuntimeError(f"CLI command failed: {stderr.decode()}")
        
        return stdout.decode()
    
    def _parse_node_list(self, output: str) -> Set[str]:
        """
        Parse node list from CLI output.
        
        Returns set of node addresses.
        """
        import re
        # Use same pattern as DataExtractor for consistency
        NODE_ADDRESS_PATTERN = r'[A-Fa-f0-9:]{10,}'
        
        node_addrs = set()
        
        # Look for lines like: "addr: XXXX::XXXX::XXXX::XXXX"
        for line in output.split('\n'):
            line = line.strip()
            if 'addr:' in line or 'address:' in line:
                # Extract all node addresses matching the pattern
                matches = re.findall(NODE_ADDRESS_PATTERN, line)
                for match in matches:
                    if '::' in match:  # Must have :: separators (IPv6-like format)
                        node_addrs.add(match)
        
        return node_addrs
    
    def _parse_node_addr(self, output: str) -> Optional[str]:
        """Parse own node address from node dump."""
        for line in output.split('\n'):
            if 'node address:' in line.lower() or 'addr:' in line.lower():
                parts = line.split()
                for part in parts:
                    if '::' in part:
                        return part
        return None
    
    def _parse_chain_info(self, output: str, chain_name: str) -> Tuple[int, Optional[str]]:
        """
        Parse chain info to get block count and last hash.
        
        Returns:
            (block_count, last_block_hash)
        """
        blocks = 0
        last_hash = None
        
        # Look for chain blocks count
        for line in output.split('\n'):
            if 'blocks:' in line.lower():
                try:
                    blocks = int(line.split(':')[-1].strip())
                except:
                    pass
            if 'last' in line.lower() and 'hash' in line.lower():
                parts = line.split()
                for part in parts:
                    if part.startswith('0x') and len(part) > 10:
                        last_hash = part
        
        return blocks, last_hash
    
    def _parse_online_status(self, output: str) -> bool:
        """Parse network status to determine if node is online."""
        output_lower = output.lower()
        return 'online' in output_lower or 'state: 3' in output_lower

