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
        logger.info("starting_parallel_node_registration", node_count=len(nodes) - 1)
        registration_tasks = [register_single_node(node) for node in nodes]
        results = await asyncio.gather(*registration_tasks, return_exceptions=True)
        
        # Count successes and log details
        registered_count = 0
        failed_nodes = []
        for i, (node, result) in enumerate(zip(nodes, results)):
            if node.node_id == 1:
                continue  # Skip node1
            
            if isinstance(result, Exception):
                failed_nodes.append(f"node{node.node_id}(exception: {result})")
                logger.error("node_registration_exception",
                           node_id=node.node_id,
                           error=str(result))
            elif result is True:
                registered_count += 1
            else:
                failed_nodes.append(f"node{node.node_id}(failed)")
        
        logger.info("node_registration_via_cli_complete",
                   registered=registered_count,
                   total=len(nodes) - 1,
                   failed=len(failed_nodes),
                   failed_nodes=", ".join(failed_nodes) if failed_nodes else "none")
    
    async def generate_fee_wallet(self) -> str:
        """
        Generate fee collection wallet on node1.
        
        Creates a wallet named 'fee_collector' on the first node
        and returns its address for use in chain configuration.
        
        Returns:
            Wallet address string
            
        Raises:
            RuntimeError: If wallet creation or address extraction fails
        """
        logger.info("generating_fee_wallet", node="node1")
        
        try:
            # Get node1 container
            container_name = f"cellframe-stage-node-1"
            container = self.docker_client.containers.get(container_name)
            
            # Create wallet
            cmd = ["cellframe-node-cli", "wallet", "new", "-w", "fee_collector", "-net", self.network_name]
            logger.debug("creating_fee_wallet", command=" ".join(cmd))
            
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            if exit_code != 0:
                error_msg = f"Failed to create fee wallet: exit code {exit_code}"
                if stderr_str:
                    error_msg += f", stderr: {stderr_str}"
                logger.error("fee_wallet_creation_failed", error=error_msg)
                raise RuntimeError(error_msg)
            
            logger.debug("fee_wallet_created", output=stdout_str[:200])
            
            # Get wallet address
            cmd_info = ["cellframe-node-cli", "wallet", "info", "-w", "fee_collector", "-net", self.network_name]
            logger.debug("getting_fee_wallet_address", command=" ".join(cmd_info))
            
            result_info = container.exec_run(cmd_info, demux=True)
            exit_code_info = result_info.exit_code
            stdout_info, stderr_info = result_info.output
            
            stdout_info_str = stdout_info.decode('utf-8') if stdout_info else ""
            stderr_info_str = stderr_info.decode('utf-8') if stderr_info else ""
            
            if exit_code_info != 0:
                error_msg = f"Failed to get wallet address: exit code {exit_code_info}"
                if stderr_info_str:
                    error_msg += f", stderr: {stderr_info_str}"
                logger.error("fee_wallet_info_failed", error=error_msg)
                raise RuntimeError(error_msg)
            
            # Extract address from wallet info output
            # Format: "addr: <address>"
            import re
            addr_match = re.search(r'addr:\s*(\S+)', stdout_info_str, re.IGNORECASE)
            if not addr_match:
                logger.error("fee_wallet_address_not_found", output=stdout_info_str[:200])
                raise RuntimeError(f"Could not extract wallet address from output: {stdout_info_str[:200]}")
            
            fee_addr = addr_match.group(1)
            logger.info("fee_wallet_generated", address=fee_addr)
            
            return fee_addr
            
        except docker.errors.NotFound:
            error_msg = f"Container {container_name} not found"
            logger.error("container_not_found", error=error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            logger.error("fee_wallet_generation_error", error=str(e))
            raise
    
    async def create_native_token(self, root_cert_name: str = "pvt.stagenet.master.0") -> str:
        """
        Create TCELL native token on zerochain.
        
        Executes token_decl on root node to create the native token.
        Uses zerochain (token declarations chain).
        
        Args:
            root_cert_name: Certificate name for signing (default: pvt.stagenet.master.0 for node1)
            
        Returns:
            Token declaration datum hash
            
        Raises:
            RuntimeError: If token creation fails
        """
        logger.info("creating_native_token", token="TCELL", chain="zerochain", cert=root_cert_name)
        
        try:
            # Get node1 container (root node)
            container_name = f"cellframe-stage-node-1"
            container = self.docker_client.containers.get(container_name)
            
            # Create TCELL token on zerochain
            cmd = [
                "cellframe-node-cli", "token_decl",
                "-token", "TCELL",
                "-total_supply", "1000000000",
                "-decimals", "18",
                "-signs_total", "1",
                "-signs_emission", "1",
                "-certs", root_cert_name,
                "-net", self.network_name,
                "-chain", "zerochain"
            ]
            
            logger.debug("executing_token_decl", command=" ".join(cmd))
            
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            # Parse YAML output to check for errors
            import yaml
            try:
                output_data = yaml.safe_load(stdout_str)
                if isinstance(output_data, dict) and 'errors' in output_data:
                    error_code = output_data['errors'].get('code', -1)
                    error_msg = output_data['errors'].get('message', '')
                    
                    if error_code != 0:
                        logger.error("token_decl_failed", code=error_code, message=error_msg)
                        raise RuntimeError(f"token_decl failed: code={error_code}, message={error_msg}")
                    
                    # Success - extract hash from message
                    # Format: "Datum 0x... with token TCELL is placed in datum pool"
                    import re
                    hash_match = re.search(r'(0x[A-Fa-f0-9]{64})', error_msg)
                    if hash_match:
                        token_hash = hash_match.group(1)
                        logger.info("native_token_created", token="TCELL", hash=token_hash)
                        return token_hash
                    else:
                        logger.error("token_hash_not_found", message=error_msg)
                        raise RuntimeError(f"Could not extract token hash from: {error_msg}")
                        
            except yaml.YAMLError as e:
                logger.error("failed_to_parse_token_decl_output", error=str(e), output=stdout_str[:200])
                raise RuntimeError(f"Failed to parse token_decl output: {e}")
            
            if exit_code != 0:
                error_msg = f"token_decl failed: exit code {exit_code}"
                if stderr_str:
                    error_msg += f", stderr: {stderr_str}"
                logger.error("token_decl_execution_failed", error=error_msg)
                raise RuntimeError(error_msg)
            
            # Fallback: no errors dict found
            logger.error("unexpected_token_decl_output", output=stdout_str[:200])
            raise RuntimeError(f"Unexpected token_decl output format: {stdout_str[:200]}")
            
        except docker.errors.NotFound:
            error_msg = f"Container {container_name} not found"
            logger.error("container_not_found", error=error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            logger.error("native_token_creation_error", error=str(e))
            raise
    
    async def emit_native_token(self, fee_addr: str, root_cert_name: str = "pvt.stagenet.master.0") -> str:
        """
        Emit TCELL native token to fee wallet on zerochain.
        
        Executes token_emit on root node to create emission.
        Uses zerochain (emission chain).
        
        Args:
            fee_addr: Fee wallet address to receive emission
            root_cert_name: Certificate name for signing (default: pvt.stagenet.master.0)
            
        Returns:
            Emission datum hash
            
        Raises:
            RuntimeError: If emission fails
        """
        logger.info("emitting_native_token", token="TCELL", chain="zerochain", to=fee_addr)
        
        try:
            container_name = f"cellframe-stage-node-1"
            container = self.docker_client.containers.get(container_name)
            
            cmd = [
                "cellframe-node-cli", "token_emit",
                "-token", "TCELL",
                "-emission_value", "1000000000",
                "-addr", fee_addr,
                "-certs", root_cert_name,
                "-net", self.network_name,
                "-chain", "zerochain"
            ]
            
            logger.debug("executing_token_emit", command=" ".join(cmd))
            
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            logger.info("token_emit_raw_output", exit_code=exit_code, stdout_preview=stdout_str[:500], stderr_preview=stderr_str[:200])
            
            import yaml, re
            try:
                output_data = yaml.safe_load(stdout_str)
                if isinstance(output_data, dict) and 'errors' in output_data:
                    error_code = output_data['errors'].get('code', -1)
                    error_msg = output_data['errors'].get('message', '')
                    
                    if error_code != 0:
                        logger.error("token_emit_failed", code=error_code, message=error_msg)
                        raise RuntimeError(f"token_emit failed: code={error_code}, message={error_msg}")
                    
                    hash_match = re.search(r'(0x[A-Fa-f0-9]{64})', error_msg)
                    if hash_match:
                        emission_hash = hash_match.group(1)
                        logger.info("native_token_emitted", token="TCELL", hash=emission_hash)
                        return emission_hash
                    else:
                        raise RuntimeError(f"Could not extract emission hash from: {error_msg}")
                        
            except yaml.YAMLError as e:
                logger.error("failed_to_parse_token_emit_output", error=str(e))
                raise RuntimeError(f"Failed to parse token_emit output: {e}")
            
            if exit_code != 0:
                raise RuntimeError(f"token_emit failed: exit code {exit_code}")
            
            raise RuntimeError(f"Unexpected token_emit output format")
            
        except Exception as e:
            logger.error("native_token_emission_error", error=str(e))
            raise
    
    async def create_first_transaction(self, emission_hash: str) -> str:
        """
        Create first TCELL transaction on main chain.
        
        Creates a transaction from emission to initiate main chain.
        Uses main chain (transactions chain).
        
        Args:
            emission_hash: Emission datum hash to spend from
            
        Returns:
            Transaction datum hash
            
        Raises:
            RuntimeError: If transaction creation fails
        """
        logger.info("creating_first_transaction", token="TCELL", chain="main", from_emission=emission_hash[:16])
        
        try:
            container_name = f"cellframe-stage-node-1"
            container = self.docker_client.containers.get(container_name)
            
            cmd = [
                "cellframe-node-cli", "tx_create",
                "-token", "TCELL",
                "-from_emission", emission_hash,
                "-value", "100000000",
                "-fee", "0.1",
                "-net", self.network_name,
                "-chain", "main"
            ]
            
            logger.debug("executing_tx_create", command=" ".join(cmd))
            
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, stderr = result.output
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            
            logger.info("tx_create_raw_output", exit_code=exit_code, stdout_preview=stdout_str[:500])
            
            import yaml, re
            try:
                output_data = yaml.safe_load(stdout_str)
                if isinstance(output_data, dict) and 'errors' in output_data:
                    error_code = output_data['errors'].get('code', -1)
                    error_msg = output_data['errors'].get('message', '')
                    
                    if error_code != 0:
                        logger.error("tx_create_failed", code=error_code, message=error_msg)
                        raise RuntimeError(f"tx_create failed: code={error_code}, message={error_msg}")
                    
                    hash_match = re.search(r'(0x[A-Fa-f0-9]{64})', error_msg)
                    if hash_match:
                        tx_hash = hash_match.group(1)
                        logger.info("first_transaction_created", token="TCELL", hash=tx_hash)
                        return tx_hash
                    else:
                        raise RuntimeError(f"Could not extract tx hash from: {error_msg}")
                        
            except yaml.YAMLError as e:
                logger.error("failed_to_parse_tx_create_output", error=str(e))
                raise RuntimeError(f"Failed to parse tx_create output: {e}")
            
            if exit_code != 0:
                raise RuntimeError(f"tx_create failed: exit code {exit_code}")
            
            raise RuntimeError(f"Unexpected tx_create output format")
            
        except Exception as e:
            logger.error("first_transaction_creation_error", error=str(e))
            raise
    
    async def process_zerochain_datum(self, datum_hash: str, root_nodes: List[NodeConfig], timeout: int = 60) -> None:
        """
        Process datum through zerochain DAG-PoA consensus.
        
        Waits for datum to appear on first root node, then triggers
        mempool_proc on remaining root nodes to finalize via DAG-PoA.
        
        Args:
            datum_hash: Datum hash to process
            root_nodes: List of root node configurations
            timeout: Timeout in seconds for datum to appear
            
        Raises:
            RuntimeError: If datum processing fails
        """
        logger.info("processing_zerochain_datum", datum=datum_hash[:16], root_count=len(root_nodes))
        
        if not root_nodes:
            raise RuntimeError("No root nodes provided for zerochain datum processing")
        
        try:
            # Step 1: Wait for datum to appear in mempool on first root node
            first_node = root_nodes[0]
            container_name = f"cellframe-stage-node-{first_node.node_id}"
            container = self.docker_client.containers.get(container_name)
            
            logger.debug("waiting_for_datum_in_mempool", node=f"node{first_node.node_id}", datum=datum_hash[:16])
            
            # Poll mempool for datum
            import time
            start_time = time.time()
            found = False
            
            while time.time() - start_time < timeout:
                cmd = ["cellframe-node-cli", "mempool_list", "-net", self.network_name, "-chain", "zerochain"]
                result = container.exec_run(cmd, demux=True)
                stdout, _ = result.output
                stdout_str = stdout.decode('utf-8') if stdout else ""
                
                if datum_hash.lower() in stdout_str.lower():
                    found = True
                    logger.info("datum_appeared_in_mempool", node=f"node{first_node.node_id}", elapsed=f"{time.time() - start_time:.1f}s")
                    break
                
                await asyncio.sleep(1)
            
            if not found:
                raise RuntimeError(f"Datum {datum_hash[:16]}... did not appear in mempool within {timeout}s")
            
            # Step 2: Trigger mempool_proc on remaining root nodes
            for node in root_nodes[1:]:
                container_name = f"cellframe-stage-node-{node.node_id}"
                try:
                    node_container = self.docker_client.containers.get(container_name)
                    
                    cmd_proc = ["cellframe-node-cli", "mempool_proc", "-datum", datum_hash, "-net", self.network_name, "-chain", "zerochain"]
                    logger.debug("triggering_mempool_proc", node=f"node{node.node_id}", datum=datum_hash[:16])
                    
                    result_proc = node_container.exec_run(cmd_proc, demux=True)
                    exit_code = result_proc.exit_code
                    
                    if exit_code == 0:
                        logger.info("mempool_proc_triggered", node=f"node{node.node_id}")
                    else:
                        logger.warning("mempool_proc_failed", node=f"node{node.node_id}", exit_code=exit_code)
                        
                except Exception as e:
                    logger.warning("failed_to_trigger_mempool_proc", node=f"node{node.node_id}", error=str(e))
            
            # Step 3: Wait for datum to be finalized in block (simple check)
            await asyncio.sleep(3)  # Give DAG-PoA time to finalize
            
            # Verify datum in blocks
            cmd_blocks = ["cellframe-node-cli", "block", "list", "-net", self.network_name, "-chain", "zerochain", "-last", "10"]
            result_blocks = container.exec_run(cmd_blocks, demux=True)
            stdout_blocks, _ = result_blocks.output
            stdout_blocks_str = stdout_blocks.decode('utf-8') if stdout_blocks else ""
            
            if datum_hash.lower() in stdout_blocks_str.lower():
                logger.info("datum_finalized_in_zerochain", datum=datum_hash[:16])
            else:
                logger.warning("datum_not_yet_in_block", datum=datum_hash[:16], note="May need more time")
                
        except Exception as e:
            logger.error("zerochain_datum_processing_error", error=str(e))
            raise
    
    async def sync_network(self, nodes: List[NodeConfig], timeout: int = 120) -> None:
        """
        Synchronize all nodes in the network.
        
        Triggers sync on all nodes and waits for completion.
        Monitors sync progress via net status.
        
        Args:
            nodes: List of all node configurations
            timeout: Timeout in seconds for sync completion
            
        Raises:
            RuntimeError: If sync fails or times out
        """
        logger.info("synchronizing_network", node_count=len(nodes), timeout=timeout)
        
        try:
            # Trigger sync on all nodes
            for node in nodes:
                container_name = f"cellframe-stage-node-{node.node_id}"
                try:
                    container = self.docker_client.containers.get(container_name)
                    
                    cmd_sync = ["cellframe-node-cli", "net", "-net", self.network_name, "sync", "all"]
                    logger.debug("triggering_sync", node=f"node{node.node_id}")
                    
                    result = container.exec_run(cmd_sync, demux=True)
                    exit_code = result.exit_code
                    
                    if exit_code == 0:
                        logger.debug("sync_triggered", node=f"node{node.node_id}")
                    else:
                        logger.warning("sync_trigger_failed", node=f"node{node.node_id}", exit_code=exit_code)
                        
                except Exception as e:
                    logger.warning("failed_to_trigger_sync", node=f"node{node.node_id}", error=str(e))
            
            # Monitor sync progress
            import time
            start_time = time.time()
            check_interval = 5
            
            while time.time() - start_time < timeout:
                all_synced = True
                sync_status = {}
                
                for node in nodes:
                    container_name = f"cellframe-stage-node-{node.node_id}"
                    try:
                        container = self.docker_client.containers.get(container_name)
                        
                        cmd_status = ["cellframe-node-cli", "net", "-net", self.network_name, "get", "status"]
                        result = container.exec_run(cmd_status, demux=True)
                        stdout, _ = result.output
                        stdout_str = stdout.decode('utf-8') if stdout else ""
                        
                        # Check for "synced" status
                        import re
                        synced = bool(re.search(r'status:\s*synced', stdout_str, re.IGNORECASE))
                        sync_status[f"node{node.node_id}"] = "synced" if synced else "syncing"
                        
                        if not synced:
                            all_synced = False
                            
                    except Exception as e:
                        logger.warning("failed_to_check_sync_status", node=f"node{node.node_id}", error=str(e))
                        all_synced = False
                        sync_status[f"node{node.node_id}"] = "error"
                
                if all_synced:
                    logger.info("network_synchronized", elapsed=f"{time.time() - start_time:.1f}s")
                    return
                
                logger.debug("sync_progress", status=sync_status, elapsed=f"{time.time() - start_time:.1f}s")
                await asyncio.sleep(check_interval)
            
            # Timeout reached
            logger.warning("sync_timeout", elapsed=timeout, final_status=sync_status)
            # Don't raise - sync may complete eventually
            
        except Exception as e:
            logger.error("network_sync_error", error=str(e))
            raise
    
    async def get_genesis_block_hash(self, chain_name: str) -> Optional[str]:
        """
        Get genesis block hash from specified chain.
        
        Retrieves the first block hash from a chain for use in
        static_genesis_block configuration.
        
        Args:
            chain_name: Chain name (zerochain or main)
            
        Returns:
            Genesis block hash or None if not found
        """
        logger.info("getting_genesis_block", chain=chain_name)
        
        try:
            # Get from node1
            container_name = f"cellframe-stage-node-1"
            container = self.docker_client.containers.get(container_name)
            
            cmd = ["cellframe-node-cli", "block", "list", "-net", self.network_name, "-chain", chain_name, "-first", "1"]
            logger.debug("fetching_first_block", chain=chain_name)
            
            result = container.exec_run(cmd, demux=True)
            exit_code = result.exit_code
            stdout, _ = result.output
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            
            if exit_code != 0:
                logger.warning("block_list_failed", chain=chain_name, exit_code=exit_code)
                return None
            
            # Parse block hash from output
            # Format: "block #0 hash: 0x..."
            import re
            hash_match = re.search(r'hash:\s*(0x[A-Fa-f0-9]{64})', stdout_str, re.IGNORECASE)
            if hash_match:
                genesis_hash = hash_match.group(1)
                logger.info("genesis_block_found", chain=chain_name, hash=genesis_hash[:16])
                return genesis_hash
            
            # Try alternative format
            hash_match = re.search(r'(0x[A-Fa-f0-9]{64})', stdout_str)
            if hash_match:
                genesis_hash = hash_match.group(1)
                logger.info("genesis_block_found_alt_format", chain=chain_name, hash=genesis_hash[:16])
                return genesis_hash
            
            logger.warning("genesis_block_not_found", chain=chain_name, output=stdout_str[:200])
            return None
            
        except Exception as e:
            logger.error("genesis_block_retrieval_error", chain=chain_name, error=str(e))
            return None

