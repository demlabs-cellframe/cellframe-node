"""
Network manager for cellframe test environment.

Manages the lifecycle of test network:
- Dynamic node creation based on topology
- Node startup/shutdown
- Network readiness checking
- Node discovery and configuration
- Snapshot-based suite isolation for fast environment restoration
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from ..config.loader import ConfigLoader, NetworkTopology
from ..config.generator import ConfigGenerator
from ..docker.compose import DockerComposeManager
from ..monitoring.health import HealthChecker, HealthStatus
from ..utils.logger import get_logger
from ..utils.artifacts import ArtifactsManager
from ..snapshots.manager import SnapshotManager, SnapshotMode
from .models import NodeConfig
from .genesis import GenesisInitializer

logger = get_logger(__name__)


class NetworkManager:
    """Manage cellframe test network lifecycle."""
    
    def __init__(self, base_path: Path, topology_name: str = "default", config_path: Optional[Path] = None):
        """
        Initialize network manager.
        
        Args:
            base_path: Base path to stage-env directory
            topology_name: Name of topology to use
            config_path: Optional path to stage-env.cfg
        """
        self.base_path = base_path
        self.topology_name = topology_name
        self.config_path = config_path
        
        # Load configuration
        self.config_loader = ConfigLoader(base_path, config_path)
        self.topology = self.config_loader.load_topology(topology_name)
        
        # Config generator
        self.config_generator = ConfigGenerator(base_path, config_path)
        
        # Docker compose manager
        self.compose = DockerComposeManager(
            base_path,
            project_name="cellframe-stage"
        )
        
        # Health checker
        self.health_checker = HealthChecker()
        
        # Genesis initializer
        self.genesis = GenesisInitializer(
            base_path,
            network_name=self.topology.network.name,
            config_path=config_path
        )
        
        # Node configurations
        self.nodes: Dict[str, NodeConfig] = {}
        
        # Load timeouts from config
        self.timeouts = self.config_loader.get_timeouts()
        
        # Load paths from config
        self.paths_config = self.config_loader.get_paths_config()
        
        # Initialize artifacts manager
        artifacts_config = self.config_loader.get_artifacts_config()
        self.artifacts_manager = ArtifactsManager(base_path, artifacts_config)
        
        # Initialize snapshot manager for suite isolation
        suite_isolation_config = self.config_loader.get_suite_isolation_config()
        snapshot_mode_str = suite_isolation_config.get('mode', 'filesystem')
        
        # Convert mode string to enum
        try:
            snapshot_mode = SnapshotMode(snapshot_mode_str)
        except ValueError:
            logger.warning("invalid_snapshot_mode",
                          mode=snapshot_mode_str,
                          fallback="filesystem")
            snapshot_mode = SnapshotMode.FILESYSTEM
        
        # Pass full config including cache_dir
        snapshot_config = dict(suite_isolation_config)
        snapshot_config['cache_dir'] = self.paths_config.get('cache_dir', '../testing/cache')
        
        self.snapshot_manager = SnapshotManager(
            base_path,
            mode=snapshot_mode,
            config=snapshot_config
        )
        
        self.suite_isolation_config = suite_isolation_config
        
        logger.info("network_manager_initialized",
                   topology=topology_name,
                   network=self.topology.network.name,
                   timeouts=self.timeouts,
                   cache_dir=self.paths_config.get('cache_dir'),
                   snapshot_mode=snapshot_mode.value)
    
    def generate_node_configs(self) -> List[NodeConfig]:
        """
        Generate node configurations from topology.
        
        Returns:
            List of NodeConfig objects
        """
        logger.info("generating_node_configs")
        
        configs = []
        node_counter = 1
        
        # Base settings from topology
        settings = self.topology.network_settings
        
        for node_type, node_spec in self.topology.topology.items():
            for i in range(node_spec.count):
                # Determine if seed node and balancer based on topology spec
                is_seed = getattr(node_spec, 'is_seed_node', node_spec.role == 'root')
                balancer_enabled = getattr(node_spec, 'balancer_enabled', node_spec.role == 'root')
                consensus_participation = getattr(node_spec, 'consensus_participation', False)
                
                config = NodeConfig(
                    node_id=node_counter,
                    role=node_spec.role,
                    node_type=node_type,
                    rpc_port=settings.base_rpc_port + node_counter - 1,
                    p2p_port=settings.base_p2p_port + node_counter - 1,
                    cf_port=settings.base_cf_port + node_counter - 1,
                    http_port=settings.base_http_port + node_counter - 1,
                    ip_address=self._calculate_ip(
                        settings.base_ip,
                        node_counter
                    ),
                    is_seed_node=is_seed,
                    balancer_enabled=balancer_enabled,
                    consensus_participation=consensus_participation
                )
                
                configs.append(config)
                self.nodes[f"node{node_counter}"] = config
                node_counter += 1
        
        logger.info("node_configs_generated",
                   count=len(configs),
                   seed_nodes=sum(1 for c in configs if c.is_seed_node),
                   validators=sum(1 for c in configs if c.consensus_participation))
        return configs
    
    def _calculate_ip(self, base_ip: str, node_id: int) -> str:
        """
        Calculate node IP address.
        
        Args:
            base_ip: Base IP (e.g., "172.20.0.10")
            node_id: Node ID
            
        Returns:
            IP address string
        """
        parts = base_ip.split(".")
        last_octet = int(parts[3]) + node_id - 1
        return f"{parts[0]}.{parts[1]}.{parts[2]}.{last_octet}"
    
    async def start(
        self,
        rebuild: bool = False,
        wait_ready: bool = True,
    ) -> None:
        """
        Start the test network.
        
        Args:
            rebuild: Rebuild Docker images before starting
            wait_ready: Wait for all nodes to be ready
        """
        logger.info("starting_network",
                   topology=self.topology_name,
                   rebuild=rebuild)
        
        # Generate node configurations
        if not self.nodes:
            node_configs = self.generate_node_configs()
        else:
            node_configs = list(self.nodes.values())
        
        # Generate configuration files and certificates
        logger.info("generating_configs_and_certs")
        self.config_generator.generate_all(
            self.topology,
            node_configs,
            force=rebuild
        )
        
        # Stop previous environment (keep volumes - they contain certs!)
        logger.info("stopping_previous_environment")
        try:
            self.compose.down(volumes=False, remove_images=False)
            logger.info("previous_environment_stopped")
        except Exception as e:
            logger.debug("no_previous_environment", error=str(e))
        
        # Clean up any remaining stale resources
        self.compose.cleanup_stale_resources()
        
        # Generate dynamic docker-compose.yml for all nodes
        logger.info("generating_docker_compose")
        cache_dir_relative = self.paths_config.get('cache_dir', 'cache')
        self.compose.generate_compose_for_nodes(node_configs, cache_dir_relative=cache_dir_relative)
        
        # Build images if requested
        if rebuild:
            logger.info("rebuilding_images")
            self.compose.build(no_cache=rebuild)
        
        # Start services
        logger.info("starting_docker_services")
        self.compose.up(detach=True, wait=False)
        
        # Wait for nodes to be ready
        if wait_ready:
            await self._wait_for_network_ready()
        
        # Initialize genesis state (create validator orders, register node aliases)
        logger.info("initializing_genesis_state")
        try:
            await self.genesis.initialize(node_configs)
            await self.genesis.register_node_aliases(node_configs)
        except Exception as e:
            logger.error("genesis_initialization_failed", error=str(e))
            # Don't fail the whole start process, just log the error
            # Validator orders might already exist in a restarted network
        
        # OPTIMIZATION: Pause containers → Create snapshot → Unpause
        # This way first suite can use already running network immediately
        # and snapshot remains pristine for subsequent suites
        if self.suite_isolation_config.get('auto_create_on_startup', True):
            if self.snapshot_manager.mode != SnapshotMode.DISABLED:
                logger.info("creating_initial_clean_snapshot_with_pause")
                try:
                    # CRITICAL: Stop containers before cleaning data to avoid crashes
                    logger.info("stopping_containers_for_data_cleanup")
                    self.compose.down(volumes=False, remove_images=False)
                    
                    # Clean node data to ensure pristine state
                    logger.info("cleaning_node_data_for_pristine_snapshot")
                    self._clean_node_data()
                    
                    # Restart containers with clean data
                    logger.info("restarting_containers_with_clean_data")
                    self.compose.up(detach=True, wait=False)
                    await self._wait_for_network_ready()
                    
                    # Pause all containers to freeze state
                    logger.info("pausing_containers_for_snapshot")
                    self.compose.pause()
                    
                    # Create snapshot of paused state
                    await self.create_clean_snapshot()
                    logger.info("initial_snapshot_created")
                    
                    # Unpause containers - ready for first suite
                    logger.info("unpausing_containers")
                    self.compose.unpause()
                    logger.info("containers_unpaused_ready_for_first_suite")
                    
                except Exception as e:
                    # Make sure we unpause even on error
                    try:
                        self.compose.unpause()
                    except:
                        pass
                    logger.warning("initial_snapshot_creation_failed",
                                  error=str(e),
                                  note="Will fallback to traditional cleanup")
        
        logger.info("network_started",
                   nodes=len(self.nodes),
                   topology=self.topology.network.name)
    
    async def stop(self, remove_volumes: bool = False) -> None:
        """
        Stop the test network.
        
        Args:
            remove_volumes: Remove data volumes
        """
        logger.info("stopping_network", remove_volumes=remove_volumes)
        
        # Stop Docker services
        self.compose.down(volumes=remove_volumes)
        
        logger.info("network_stopped")
    
    async def restart(self, node_name: Optional[str] = None) -> None:
        """
        Restart network or specific node.
        
        Args:
            node_name: Node to restart (None = all)
        """
        if node_name:
            logger.info("restarting_node", node=node_name)
            # Restart specific container
            containers = self.compose.ps()
            for container in containers:
                service = container.labels.get("com.docker.compose.service")
                if service == node_name:
                    container.restart()
                    logger.info("node_restarted", node=node_name)
                    return
            
            logger.warning("node_not_found", node=node_name)
        else:
            logger.info("restarting_network")
            await self.stop(remove_volumes=False)
            await self.start(rebuild=False, wait_ready=True)
    
    async def get_status(self) -> Dict[str, any]:
        """
        Get network status.
        
        Returns:
            Status information dict
        """
        logger.debug("getting_network_status")
        
        # Get container status
        service_status = self.compose.get_service_status()
        
        # Get health status via JSON-RPC (CLI)
        health_status = {}
        for node_name, config in self.nodes.items():
            try:
                # Convert node_name to container name (node1 -> node-1)
                if node_name.startswith('node'):
                    container_name = f"cellframe-stage-node-{node_name[4:]}"
                else:
                    container_name = f"cellframe-stage-{node_name}"
                
                container = self.compose.client.containers.get(container_name)
                cli_result = container.exec_run(
                    'cellframe-node-cli net get status -net stagenet',
                    demux=False
                )
                
                if cli_result.exit_code == 0:
                    output = cli_result.output.decode("utf-8")
                    # Parse state
                    current_state = "unknown"
                    for line in output.split('\n'):
                        if 'current:' in line and 'NET_STATE_' in line:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                current_state = parts[1].strip()
                                break
                    
                    health_status[node_name] = {
                        "healthy": current_state == "NET_STATE_ONLINE",
                        "state": current_state,
                        "response_time_ms": 0,  # Not applicable for CLI
                    }
                else:
                    health_status[node_name] = {
                        "healthy": False,
                        "state": "unavailable",
                        "response_time_ms": 0,
                    }
            except Exception as e:
                logger.warning("failed_to_get_node_health", node=node_name, error=str(e))
                health_status[node_name] = {
                    "healthy": False,
                    "state": "error",
                    "response_time_ms": 0,
                }
        
        # Build nodes array with combined info
        nodes_data = []
        for node_name, config in self.nodes.items():
            # Get container status
            container_status = service_status.get(node_name, {})
            # Get health status
            health = health_status.get(node_name, {})
            
            nodes_data.append({
                "name": node_name,
                "role": config.role,
                "container_status": container_status.get("status", "unknown"),
                "health_status": health.get("state", "unknown"),
                "healthy": health.get("healthy", False),
                "rpc_port": config.rpc_port,
                "p2p_port": config.p2p_port,
            })
        
        return {
            "topology": self.topology_name,
            "network_name": self.topology.network.name,
            "total_nodes": len(self.nodes),
            "nodes": nodes_data,
            "containers": service_status,
            "health": health_status,
        }
    
    async def _wait_for_network_ready(self) -> None:
        """
        Wait for all nodes to be ready.
        
        Uses timeout from config [timeouts] section.
        """
        timeout = self.timeouts.get('health_check', 300)
        logger.info("waiting_for_network_ready", timeout=timeout)
        
        # Wait for Docker containers and nodes to reach ONLINE state
        # This is now handled entirely by compose.wait_for_services()
        # which uses CLI to check node state
        self.compose.wait_for_services(timeout=int(timeout))
        
        logger.info("network_ready", nodes=len(self.nodes))
    
    def get_node_logs(
        self,
        node_name: str,
        tail: int = 100,
        follow: bool = False,
    ) -> str:
        """
        Get logs for a node.
        
        Args:
            node_name: Node identifier
            tail: Number of lines from end
            follow: Follow log output
            
        Returns:
            Log output
        """
        logger.debug("fetching_logs", node=node_name, tail=tail)
        
        return self.compose.logs(node_name, follow=follow, tail=tail)
    
    def exec_in_node(
        self,
        node_name: str,
        command: List[str],
    ) -> tuple[int, str]:
        """
        Execute command in node container.
        
        Args:
            node_name: Node identifier
            command: Command to execute
            
        Returns:
            Tuple of (exit_code, output)
        """
        logger.debug("executing_in_node",
                    node=node_name,
                    command=" ".join(command))
        
        return self.compose.exec(node_name, command)
    
    def list_nodes(self) -> List[Dict[str, any]]:
        """
        List all configured nodes.
        
        Returns:
            List of node information dicts
        """
        return [
            {
                "name": name,
                "id": config.node_id,
                "role": config.role,
                "type": config.node_type,
                "rpc_port": config.rpc_port,
                "p2p_port": config.p2p_port,
                "ip": config.ip_address,
            }
            for name, config in self.nodes.items()
        ]
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.health_checker.close()
    
    async def create_clean_snapshot(self, name: Optional[str] = None) -> bool:
        """
        Create a snapshot of current clean environment state.
        
        Should be called after network is fully initialized and ready,
        before any tests are run.
        
        Args:
            name: Optional snapshot name (defaults to config snapshot_name)
            
        Returns:
            True if snapshot created successfully
        """
        snapshot_name = name or self.suite_isolation_config.get('snapshot_name', 'clean_state')
        
        logger.info("creating_clean_snapshot",
                   name=snapshot_name,
                   mode=self.snapshot_manager.mode.value)
        
        result = await self.snapshot_manager.create_snapshot(snapshot_name)
        
        if result and self.suite_isolation_config.get('auto_cleanup', True):
            # Cleanup old snapshots
            keep_count = self.suite_isolation_config.get('keep_snapshot_count', 5)
            await self.snapshot_manager.cleanup_old_snapshots(keep_count)
        
        return result
    
    async def restore_clean_state(self, name: Optional[str] = None) -> bool:
        """
        Restore environment to clean snapshot state.
        
        This replaces the current clean_test_data() approach with snapshot restoration,
        providing much faster suite isolation.
        
        Args:
            name: Optional snapshot name (defaults to config snapshot_name)
            
        Returns:
            True if restore successful
        """
        snapshot_name = name or self.suite_isolation_config.get('snapshot_name', 'clean_state')
        
        logger.info("restoring_clean_state",
                   name=snapshot_name,
                   mode=self.snapshot_manager.mode.value)
        
        # Special case for 'recreate' mode - use traditional cleanup
        if self.snapshot_manager.mode == SnapshotMode.RECREATE:
            logger.info("recreate_mode_using_clean_test_data")
            await self.clean_test_data()
            return True
        
        # For other modes, restore from snapshot
        # CRITICAL: Stop containers before restore to avoid file conflicts
        logger.info("stopping_containers_before_snapshot_restore")
        await self.stop(remove_volumes=False)
        
        # Restore snapshot with containers stopped
        result = await self.snapshot_manager.restore_snapshot(snapshot_name)
        
        if not result:
            logger.warning("snapshot_restore_failed_fallback_to_cleanup")
            # Restart containers even if restore failed
            logger.info("starting_containers_after_failed_restore")
            await self.start(rebuild=False, wait_ready=True)
            # Only try cleanup if containers are running
            if self.compose and self.compose.is_running():
                await self.clean_test_data()
            else:
                logger.warning("containers_not_running_skipping_cleanup")
            return False
        
        # Restart containers with restored data
        logger.info("starting_containers_after_snapshot_restore")
        await self.start(rebuild=False, wait_ready=True)
        
        return result
    
    async def clean_test_data(self) -> None:
        """
        Clean test data from all nodes (traditional approach).
        
        This is the original cleanup method, now used as fallback or for 'recreate' mode.
        Removes user-generated data while preserving system files.
        """
        logger.info("cleaning_test_data_traditional_method")
        
        for node_name in self.nodes.keys():
            try:
                # Execute cleanup inside container to avoid permission issues
                cleanup_script = """
                # Clean user-generated data
                rm -f /opt/cellframe-node/var/lib/wallet/*.dwallet 2>/dev/null || true
                rm -rf /opt/cellframe-node/var/lib/chains/* 2>/dev/null || true
                rm -rf /opt/cellframe-node/var/lib/gdb/* 2>/dev/null || true
                rm -f /opt/cellframe-node/var/log/*.log 2>/dev/null || true
                
                # Preserve:
                # - /opt/cellframe-node/var/lib/ca/ (validator certificates)
                # - /opt/cellframe-node/var/run/ (PID files, sockets)
                
                echo "Cleanup complete for $(hostname)"
                """
                
                exit_code, output = self.compose.exec(
                    node_name,
                    ["sh", "-c", cleanup_script]
                )
                
                if exit_code == 0:
                    logger.debug("node_data_cleaned", node=node_name)
                else:
                    logger.warning("node_cleanup_failed",
                                  node=node_name,
                                  exit_code=exit_code,
                                  output=output)
            except Exception as e:
                logger.error("node_cleanup_error",
                            node=node_name,
                            error=str(e))
    
    def _clean_node_data(self):
        """
        Clean node data directories on host before creating pristine snapshot.
        
        This method removes and recreates data directories mounted into containers,
        ensuring that wallets, chains, and other runtime data from previous runs
        don't pollute the snapshot.
        
        Called before pause→snapshot→unpause to guarantee pristine state.
        """
        import shutil
        
        cache_dir = self.paths_config.get('cache_dir', '../testing/cache')
        cache_path = (self.base_path / cache_dir).resolve()
        data_dir = cache_path / "data"
        
        if not data_dir.exists():
            logger.debug("node_data_dir_not_exists", path=str(data_dir))
            return
        
        logger.info("removing_node_data_directories", path=str(data_dir))
        
        # Remove entire data directory tree
        try:
            shutil.rmtree(data_dir)
            logger.info("node_data_removed")
        except Exception as e:
            logger.error("failed_to_remove_node_data", error=str(e))
            raise
        
        # Recreate empty data directory structure for each node
        data_dir.mkdir(parents=True, exist_ok=True)
        
        for node_id in range(1, len(self.nodes) + 1):
            node_data_path = data_dir / f"node{node_id}"
            node_data_path.mkdir(parents=True, exist_ok=True)
            logger.debug("recreated_node_data_dir", node_id=node_id, path=str(node_data_path))
        
        logger.info("node_data_cleaned_and_recreated", nodes=len(self.nodes))

