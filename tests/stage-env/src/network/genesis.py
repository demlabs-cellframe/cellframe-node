"""
Genesis initialization for stagenet.

Handles initial setup tasks after network start:
- Creating validator stake orders
- Registering node aliases in GDB
- Setting up initial state
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import docker
import time

from ..utils.logger import get_logger
from .models import NodeConfig

logger = get_logger(__name__)


class GenesisInitializer:
    """Initialize genesis state for stagenet."""
    
    def __init__(self, base_path: Path, network_name: str = "stagenet", config_path: Path = None):
        """
        Initialize genesis initializer.
        
        Args:
            base_path: Base path to stage-env directory
            network_name: Network name (default: stagenet)
            config_path: Optional path to config file
        """
        self.base_path = base_path
        self.network_name = network_name
        self.docker_client = docker.from_env()
        # Load cache dir from config
        from ..config.loader import ConfigLoader
        config_loader = ConfigLoader(base_path, config_path)
        paths_config = config_loader.get_paths_config()
        cache_dir_relative = paths_config.get('cache_dir', 'cache')
        # Resolve cache dir relative to BASE_PATH (always)
        self.certs_cache = (base_path / cache_dir_relative / "certs").resolve()
        
        logger.info("genesis_initializer_created", network=network_name)
    
    def _read_node_addr_with_retry(
        self, 
        node_id: int, 
        max_retries: int = 10, 
        retry_delay: float = 1.0
    ) -> Optional[str]:
        """
        Read node_addr.txt from HOST filesystem (not container).
        
        The file is created by cert-generator on the host in certs_cache/nodeN/node_addr.txt
        and is NOT copied into the container.
        
        Args:
            node_id: Node ID
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Node address string or None if failed
        """
        addr_file = self.certs_cache / f"node{node_id}" / "node_addr.txt"
        
        for attempt in range(1, max_retries + 1):
            try:
                if addr_file.exists():
                    node_addr = addr_file.read_text().strip()
                    if node_addr:  # Ensure non-empty
                        logger.debug("read_node_address",
                                    node_id=node_id,
                                    node_addr=node_addr,
                                    attempt=attempt,
                                    source="host_filesystem")
                        return node_addr
                
                # File not ready yet
                if attempt < max_retries:
                    logger.debug("node_addr_not_ready_retrying",
                                node_id=node_id,
                                attempt=attempt,
                                max_retries=max_retries,
                                path=str(addr_file))
                    time.sleep(retry_delay)
                    
            except Exception as e:
                if attempt < max_retries:
                    logger.debug("node_addr_read_error_retrying",
                                node_id=node_id,
                                attempt=attempt,
                                error=str(e))
                    time.sleep(retry_delay)
                else:
                    logger.error("failed_to_get_node_address",
                                node_id=node_id,
                                error=str(e),
                                attempts=attempt)
        
        logger.error("failed_to_read_node_addr_after_retries",
                    node_id=node_id,
                    max_retries=max_retries,
                    path=str(addr_file),
                    exists=addr_file.exists())
        return None
    
    async def initialize(self, nodes: List[NodeConfig]) -> None:
        """
        Initialize genesis state.
        
        Creates validator orders for all validator nodes (root nodes).
        
        Args:
            nodes: List of node configurations
        """
        logger.info("starting_genesis_initialization", nodes=len(nodes))
        
        # Find root nodes (validators)
        validator_nodes = [n for n in nodes if n.is_seed_node]
        
        if not validator_nodes:
            logger.warning("no_validator_nodes_found")
            return
        
        logger.info("found_validator_nodes", count=len(validator_nodes))
        
        # Use first node to create orders (any node can do this)
        admin_node = nodes[0]
        container_name = f"cellframe-stage-node-{admin_node.node_id}"
        
        try:
            container = self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            logger.error("admin_node_container_not_found", container=container_name)
            raise RuntimeError(f"Container {container_name} not found")
        
        # Wait a bit for node to initialize
        logger.info("waiting_for_node_initialization")
        await asyncio.sleep(5)
        
        # Root nodes will connect to each other via seed_nodes_hosts configuration
        # No need to manually add them to nodelist - standard bootstrap mechanism will handle it
        logger.info("root_nodes_will_connect_via_seed_nodes_hosts",
                   seed_nodes=len(validator_nodes))
        
        # Create validator orders for each validator node
        for node in validator_nodes:
            await self._create_validator_order(container, node)
        
        logger.info("genesis_initialization_complete", orders_created=len(validator_nodes))
    
    async def _setup_root_nodelists(self, root_nodes: List[NodeConfig]) -> None:
        """
        Setup nodelists for root nodes - each root node adds all other root nodes.
        
        Root nodes are the bootstrap/seed nodes that manage the network topology.
        They need to know about each other immediately.
        
        Args:
            root_nodes: List of root node configurations
        """
        logger.info("setting_up_root_nodelists", count=len(root_nodes))
        
        # Read all root node addresses first (from containers, not host)
        root_node_data = []
        for node in root_nodes:
            # Use retry logic to read node_addr.txt
            node_addr = self._read_node_addr_with_retry(node.node_id)
            
            if node_addr:
                root_node_data.append({
                    'node': node,
                    'validator_addr': node_addr,  # Same as node_addr
                    'node_addr': node_addr
                })
            else:
                logger.warning("skipping_node_no_address",
                              node_id=node.node_id)
        
        # For each root node, add all other root nodes to its nodelist
        for current in root_node_data:
            container_name = f"cellframe-stage-node-{current['node'].node_id}"
            
            try:
                container = self.docker_client.containers.get(container_name)
            except docker.errors.NotFound:
                logger.warning("root_node_container_not_found",
                              node_id=current['node'].node_id,
                              container=container_name)
                continue
            
            # Add this node itself first
            await self._add_to_nodelist(
                container,
                current['node'],
                current['node_addr'],
                current['node'].ip_address,
                current['node'].node_port,
                is_self=True
            )
            
            # Then add all other root nodes
            for other in root_node_data:
                if other['node'].node_id == current['node'].node_id:
                    continue  # Skip self (already added)
                
                await self._add_to_nodelist(
                    container,
                    current['node'],
                    other['node_addr'],
                    other['node'].ip_address,
                    other['node'].node_port,
                    is_self=False
                )
        
        logger.info("root_nodelists_setup_complete")
    
    async def _add_to_nodelist(
        self,
        container: docker.models.containers.Container,
        current_node: NodeConfig,
        target_node_addr: str,
        target_ip: str,
        target_port: int,
        is_self: bool = False
    ) -> None:
        """
        Add a node to current node's nodelist.
        
        Args:
            container: Docker container of current node
            current_node: Current node configuration
            target_node_addr: Node address to add (hex format)
            target_ip: IP address of target node
            target_port: Port of target node
            is_self: Whether adding the node itself
        """
        # Command: node add -net <net> -addr <node_addr>
        # Note: Cellframe Node uses "node add" not "nodelist add"
        cmd = [
            "cellframe-node-cli",
            "node", "add",
            "-net", self.network_name,
            "-addr", target_node_addr
        ]
        
        logger.info("adding_to_nodelist",
                   current_node_id=current_node.node_id,
                   target_addr=target_node_addr,
                   target_endpoint=f"{target_ip}:{target_port}",
                   is_self=is_self)
        
        try:
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            if exit_code != 0:
                # Some errors are expected (e.g., node already in list)
                if "already" in stderr_str.lower() or "already" in stdout_str.lower():
                    logger.debug("node_already_in_nodelist",
                                current_node_id=current_node.node_id,
                                target_addr=target_node_addr)
                else:
                    logger.warning("nodelist_add_failed",
                                  current_node_id=current_node.node_id,
                                  target_addr=target_node_addr,
                                  exit_code=exit_code,
                                  stderr=stderr_str)
            else:
                logger.info("added_to_nodelist",
                           current_node_id=current_node.node_id,
                           target_addr=target_node_addr,
                           output=stdout_str.strip())
                
        except Exception as e:
            logger.exception("nodelist_add_exception",
                           current_node_id=current_node.node_id,
                           target_addr=target_node_addr,
                           error=str(e))
    
    async def _create_validator_order(
        self,
        container: docker.models.containers.Container,
        node: NodeConfig
    ) -> None:
        """
        Create validator order for a node.
        
        Args:
            container: Docker container to execute commands in
            node: Node configuration
        """
        # Certificate name for this validator (use private key)
        validator_idx = node.node_id - 1
        cert_name = f"pvt.{self.network_name}.master.{validator_idx}"
        
        # Read node address with retry logic
        node_addr = self._read_node_addr_with_retry(node.node_id)
        
        if not node_addr:
            logger.error("cannot_create_order_no_node_addr",
                        node_id=node.node_id)
            return
        
        logger.info("read_node_address",
                   node_id=node.node_id,
                   node_addr=node_addr)
        
        # Order parameters
        # value_min and value_max in datoshi (1 token = 10^18 datoshi)
        # For testing, use 100 tokens min, 10000 tokens max
        value_min = "100000000000000000000"  # 100 tokens
        value_max = "10000000000000000000000"  # 10000 tokens
        tax = "10.0"  # 10.0% tax (must be float с точкой)
        
        # Build CLI command
        cmd = [
            "cellframe-node-cli",
            "srv_stake", "order", "create", "validator",
            "-net", self.network_name,
            "-value_min", value_min,
            "-value_max", value_max,
            "-tax", tax,
            "-cert", cert_name,
            "-node_addr", node_addr,
            "-H", "hex"
        ]
        
        logger.info("creating_validator_order",
                   node_id=node.node_id,
                   cert=cert_name,
                   node_addr=node_addr)
        
        try:
            # Execute command in container
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            if exit_code != 0:
                logger.error("order_creation_failed",
                           node_id=node.node_id,
                           exit_code=exit_code,
                           stdout=stdout_str,
                           stderr=stderr_str)
                raise RuntimeError(f"Failed to create order for node {node.node_id}: {stderr_str}")
            
            logger.info("validator_order_created",
                       node_id=node.node_id,
                       cert=cert_name,
                       output=stdout_str.strip())
            
        except Exception as e:
            logger.exception("order_creation_exception",
                           node_id=node.node_id,
                           error=str(e))
            raise
    
    async def register_node_aliases(self, nodes: List[NodeConfig]) -> None:
        """
        Register node aliases in GDB for node discovery.
        
        This allows nodes to find each other by validator address.
        
        Args:
            nodes: List of node configurations
        """
        logger.info("registering_node_aliases", count=len(nodes))
        
        # Use first node as admin
        admin_node = nodes[0]
        container_name = f"cellframe-stage-node-{admin_node.node_id}"
        
        try:
            container = self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            logger.error("admin_node_container_not_found", container=container_name)
            raise RuntimeError(f"Container {container_name} not found")
        
        # Register each node
        for node in nodes:
            # Read node address with retry logic
            node_addr = self._read_node_addr_with_retry(node.node_id)
            
            if not node_addr:
                logger.warning("skipping_node_alias_no_address",
                              node_id=node.node_id)
                continue
            
            # GDB command to register node_alias
            # Format: global_db set -net <net> node_alias.<node_addr> <ip:port>
            cmd = [
                "cellframe-node-cli",
                "global_db", "set",
                "-net", self.network_name,
                f"node_alias.{node_addr}",
                f"{node.ip_address}:{node.node_port}"
            ]
            
            logger.info("registering_node_alias",
                       node_id=node.node_id,
                       node_addr=node_addr,
                       endpoint=f"{node.ip_address}:{node.node_port}")
            
            try:
                result = container.exec_run(cmd, demux=True)
                exit_code = result.exit_code
                
                if exit_code != 0:
                    stdout, stderr = result.output
                    stderr_str = stderr.decode() if stderr else ""
                    logger.warning("node_alias_registration_failed",
                                  node_id=node.node_id,
                                  exit_code=exit_code,
                                  stderr=stderr_str)
                else:
                    logger.info("node_alias_registered",
                              node_id=node.node_id,
                              node_addr=node_addr)
                    
            except Exception as e:
                logger.exception("node_alias_registration_exception",
                               node_id=node.node_id,
                               error=str(e))
        
        logger.info("node_alias_registration_complete")
        
        # Bring all nodes online explicitly (in case auto_online didn't work)
        logger.info("bringing_nodes_online")
        for node in nodes:
            container_name = f"cellframe-stage-node-{node.node_id}"
            try:
                container = self.docker_client.containers.get(container_name)
                cmd = ["cellframe-node-cli", "net", "-net", self.network_name, "go", "online"]
                result = container.exec_run(cmd, demux=True)
                
                if result.exit_code == 0:
                    logger.info("node_brought_online", node_id=node.node_id)
                else:
                    stdout, stderr = result.output
                    stderr_str = stderr.decode() if stderr else ""
                    logger.warning("failed_to_bring_node_online",
                                  node_id=node.node_id,
                                  stderr=stderr_str)
            except Exception as e:
                logger.warning("exception_bringing_node_online",
                              node_id=node.node_id,
                              error=str(e))
    
    async def register_all_nodes_via_cli(self, nodes: List[NodeConfig]) -> None:
        """
        Register ALL nodes in the network via CLI 'node add' command from node1.
        
        This ensures all nodes immediately know about each other without waiting
        for natural P2P discovery.
        
        Uses parallel registration for speed.
        
        Args:
            nodes: List of all node configurations
        """
        logger.info("registering_all_nodes_via_cli", total_nodes=len(nodes))
        
        # Get node-1 container (root node with admin rights)
        container_name = "cellframe-stage-node-1"
        try:
            container = self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            logger.error("node1_container_not_found", container=container_name)
            raise RuntimeError(f"Container {container_name} not found")
        
        # Prepare registration tasks for all nodes (except node1)
        async def register_single_node(node: NodeConfig) -> bool:
            """Register a single node. Returns True on success."""
            # Skip node1 itself
            if node.node_id == 1:
                return True
            
            # Read node address with retry logic
            node_addr = self._read_node_addr_with_retry(node.node_id)
            
            if not node_addr:
                logger.warning("skipping_node_registration_no_address",
                              node_id=node.node_id)
                return False
            
            # CLI command: node add -net <net> -addr <node_addr> -host <ip> -port <p2p_port>
            # Note: using node_port (8079) for P2P, not cf_port
            cmd = [
                "cellframe-node-cli",
                "node", "add",
                "-net", self.network_name,
                "-addr", node_addr,
                "-host", node.ip_address,
                "-port", str(node.node_port)  # P2P port (8079)
            ]
            
            logger.info("registering_node_via_cli",
                       node_id=node.node_id,
                       node_addr=node_addr[:20] + "...",
                       endpoint=f"{node.ip_address}:{node.node_port}")
            
            try:
                result = container.exec_run(cmd, demux=True)
                exit_code = result.exit_code
                stdout, stderr = result.output
                
                stdout_str = stdout.decode('utf-8').strip() if stdout else ""
                stderr_str = stderr.decode('utf-8').strip() if stderr else ""
                
                if exit_code == 0:
                    # Check for common success/warning messages
                    if "You have no access rights" in stdout_str:
                        logger.warning("node_add_no_rights",
                                      node_id=node.node_id)
                        return False
                    elif "already" in stdout_str.lower():
                        logger.debug("node_already_registered",
                                    node_id=node.node_id,
                                    output=stdout_str)
                        return True
                    else:
                        logger.info("node_registered_via_cli",
                                  node_id=node.node_id,
                                  output=stdout_str if stdout_str else "success")
                        return True
                else:
                    logger.warning("node_add_failed",
                                  node_id=node.node_id,
                                  exit_code=exit_code,
                                  stderr=stderr_str,
                                  stdout=stdout_str)
                    return False
                    
            except Exception as e:
                logger.exception("node_add_exception",
                               node_id=node.node_id,
                               error=str(e))
                return False
        
        # Run all registrations in parallel
        registration_tasks = [register_single_node(node) for node in nodes]
        results = await asyncio.gather(*registration_tasks, return_exceptions=True)
        
        # Count successes
        registered_count = sum(1 for r in results if r is True)
        
        logger.info("node_registration_via_cli_complete",
                   registered=registered_count,
                   total=len(nodes) - 1)  # -1 for node1 itself

