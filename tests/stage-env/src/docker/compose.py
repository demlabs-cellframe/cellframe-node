"""
Docker Compose management using Docker SDK.

Modern replacement for deprecated docker-compose library.
Uses docker SDK 7.0+ with native compose v2 support.
"""

import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional

import docker
from docker.errors import DockerException, NotFound
from docker.models.containers import Container

from ..utils.logger import get_logger
from ..network.models import NodeConfig

logger = get_logger(__name__)


class DockerComposeManager:
    """Manage Docker Compose services using Docker SDK."""
    
    def __init__(self, project_dir: Path, project_name: str = "cellframe"):
        """
        Initialize Docker Compose manager.
        
        Args:
            project_dir: Project directory containing docker-compose.yml
            project_name: Docker Compose project name
        """
        self.project_dir = project_dir
        self.project_name = project_name
        self.compose_file = project_dir / "docker-compose.yml"
        
        try:
            self.client = docker.from_env()
            logger.info("docker_connected", version=self.client.version()["Version"])
        except DockerException as e:
            logger.error("docker_connection_failed", error=str(e))
            raise
    
    def build(
        self,
        services: Optional[List[str]] = None,
        no_cache: bool = False,
    ) -> None:
        """
        Build Docker images.
        
        Args:
            services: List of service names to build (None = all)
            no_cache: Don't use cache
        """
        logger.info("building_images", 
                   services=services or "all",
                   no_cache=no_cache)
        
        # Use docker compose CLI via subprocess for build
        # (docker SDK doesn't have direct compose build API yet)
        from ..utils.cli import run_command
        
        cmd = ["docker", "compose", "-f", str(self.compose_file),
               "-p", self.project_name, "build"]
        
        if no_cache:
            cmd.append("--no-cache")
        
        if services:
            cmd.extend(services)
        
        run_command(cmd, cwd=self.project_dir)
        logger.info("build_completed")
    
    def cleanup_stale_resources(self) -> None:
        """
        Clean up stale containers and networks from previous runs.
        
        This prevents "network overlap" and "container name conflict" errors.
        """
        logger.info("cleanup_stale_resources", project=self.project_name)
        
        # Find and remove stale containers with this project name
        try:
            stale_containers = self.client.containers.list(
                all=True,
                filters={"label": f"com.docker.compose.project={self.project_name}"}
            )
            
            if stale_containers:
                logger.info("removing_stale_containers", count=len(stale_containers))
                for container in stale_containers:
                    try:
                        logger.debug("removing_container", 
                                   name=container.name,
                                   id=container.short_id)
                        container.remove(force=True)
                    except Exception as e:
                        logger.warning("failed_to_remove_container",
                                     name=container.name,
                                     error=str(e))
            else:
                logger.debug("no_stale_containers")
        except Exception as e:
            logger.warning("failed_to_list_containers", error=str(e))
        
        # Find and remove stale networks with this project name
        try:
            all_networks = self.client.networks.list()
            stale_networks = [
                net for net in all_networks
                if self.project_name in net.name
            ]
            
            if stale_networks:
                logger.info("removing_stale_networks", count=len(stale_networks))
                for network in stale_networks:
                    try:
                        logger.debug("removing_network",
                                   name=network.name,
                                   id=network.short_id)
                        network.remove()
                    except Exception as e:
                        logger.warning("failed_to_remove_network",
                                     name=network.name,
                                     error=str(e))
            else:
                logger.debug("no_stale_networks")
        except Exception as e:
            logger.warning("failed_to_list_networks", error=str(e))
        
        logger.info("cleanup_completed")
    
    def generate_compose_for_nodes(
        self,
        nodes: List[NodeConfig],
        build_type: str = "debug",
        cellframe_version: str = "latest",
        cache_dir_relative: str = "cache"
    ) -> None:
        """
        Generate docker-compose.yml dynamically for given nodes.
        
        Args:
            nodes: List of node configurations
            build_type: Build type (debug/release)
            cellframe_version: Cellframe version tag
            cache_dir_relative: Relative path to cache directory
        """
        logger.info("generating_compose_file",
                   node_count=len(nodes),
                   build_type=build_type,
                   cache_dir=cache_dir_relative)
        
        # Read base template
        template_file = self.project_dir / "docker-compose.yml"
        
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")
        
        # Load base compose configuration
        with open(template_file, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        # Extract template from x-cf-node-template
        node_template = compose_data.get('x-cf-node-template')
        if not node_template:
            raise ValueError("No x-cf-node-template found in docker-compose.yml")
        
        # Clear existing node services (keep monitoring/test services)
        services_to_keep = {}
        for svc_name, svc_config in compose_data.get('services', {}).items():
            if svc_name not in ['cf-node']:
                services_to_keep[svc_name] = svc_config
        
        compose_data['services'] = services_to_keep
        
        # Generate service for each node
        for node in nodes:
            service_name = f"node-{node.node_id}"
            
            # Deep copy template
            node_service = yaml.safe_load(yaml.dump(node_template))
            
            # Update service configuration
            node_service['container_name'] = f"{self.project_name}-node-{node.node_id}"
            node_service['hostname'] = f"{self.project_name}-node-{node.node_id}"
            
            # Set network IP
            node_service['networks'] = {
                'stagenet': {
                    'ipv4_address': node.ip_address
                }
            }
            
            # Set ports - Cellframe uses 8079 for HTTP/JSON-RPC/P2P
            node_service['ports'] = [
                f"{node.http_port}:8079",  # Cellframe HTTP/JSON-RPC/P2P
            ]
            
            # Set volumes with node-specific paths
            node_service['volumes'] = [
                # Main config file (generated per node with HTTP settings)
                f"./{cache_dir_relative}/configs/node{node.node_id}/cellframe-node.cfg:/opt/cellframe-node/etc/cellframe-node.cfg",
                f"./{cache_dir_relative}/configs/node{node.node_id}/cellframe-node.cfg.d:/opt/cellframe-node/etc/cellframe-node.cfg.d",
                f"./{cache_dir_relative}/configs/node{node.node_id}/network:/opt/cellframe-node/etc/network",
                f"./{cache_dir_relative}/data/node{node.node_id}:/opt/cellframe-node/var",
                f"./{cache_dir_relative}/configs/shared/ca:/opt/cellframe-node/share/ca:ro",
                f"./{cache_dir_relative}/crash-artifacts/node{node.node_id}:/crash-artifacts/node-{node.node_id}",
                f"./{cache_dir_relative}/cellframe-packages:/var/cache/cellframe-packages"
            ]
            
            # Add custom volumes if specified
            if hasattr(node, 'docker_volumes') and node.docker_volumes:
                node_service['volumes'].extend(node.docker_volumes)
                logger.debug("added_custom_volumes",
                           node_id=node.node_id,
                           volumes=node.docker_volumes)
            
            # Set environment variables
            node_service['environment'] = {
                'NODE_ID': str(node.node_id),
                'NODE_ROLE': node.role,
                'NODE_TYPE': node.node_type,
                'NODE_IP': node.ip_address,
                'NETWORK_NAME': 'stagenet',
                'DAP_DEBUG': '1',
                'CELLFRAME_DEBUG': '1'
            }
            
            # Add custom environment variables if specified
            if hasattr(node, 'custom_env_vars') and node.custom_env_vars:
                node_service['environment'].update(node.custom_env_vars)
                logger.debug("added_custom_env_vars",
                           node_id=node.node_id,
                           vars=list(node.custom_env_vars.keys()))
            
            # Add custom capabilities if specified
            if hasattr(node, 'docker_capabilities') and node.docker_capabilities:
                if 'cap_add' not in node_service:
                    node_service['cap_add'] = []
                node_service['cap_add'].extend(node.docker_capabilities)
                logger.debug("added_custom_capabilities",
                           node_id=node.node_id,
                           caps=node.docker_capabilities)
            
            # Add custom devices if specified
            if hasattr(node, 'docker_devices') and node.docker_devices:
                node_service['devices'] = node.docker_devices
                logger.debug("added_custom_devices",
                           node_id=node.node_id,
                           devices=node.docker_devices)
            
            # Merge custom docker config if specified
            if hasattr(node, 'docker_extra_config') and node.docker_extra_config:
                for key, value in node.docker_extra_config.items():
                    if isinstance(value, dict) and key in node_service and isinstance(node_service[key], dict):
                        # Merge dictionaries
                        node_service[key].update(value)
                    elif isinstance(value, list) and key in node_service and isinstance(node_service[key], list):
                        # Extend lists
                        node_service[key].extend(value)
                    else:
                        # Override or add new key
                        node_service[key] = value
                logger.debug("merged_custom_docker_config",
                           node_id=node.node_id,
                           keys=list(node.docker_extra_config.keys()))
            
            # Add to services
            compose_data['services'][service_name] = node_service
        
        # Write generated compose file
        generated_file = self.project_dir / "docker-compose.generated.yml"
        
        with open(generated_file, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
        # Update compose_file to use generated file
        self.compose_file = generated_file
        
        logger.info("compose_file_generated",
                   path=str(generated_file),
                   services=len(nodes))
    
    def up(
        self,
        services: Optional[List[str]] = None,
        detach: bool = True,
        wait: bool = True,
    ) -> None:
        """
        Start services.
        
        Args:
            services: List of service names (None = all)
            detach: Run in background
            wait: Wait for services to be ready
        """
        logger.info("starting_services", services=services or "all")
        
        from ..utils.cli import run_command
        
        cmd = ["docker", "compose", "-f", str(self.compose_file),
               "-p", self.project_name, "up"]
        
        if detach:
            cmd.append("-d")
        
        if services:
            cmd.extend(services)
        
        run_command(cmd, cwd=self.project_dir)
        
        if wait:
            self.wait_for_services(services)
        
        logger.info("services_started")
    
    def down(self, volumes: bool = False, remove_images: bool = False) -> None:
        """
        Stop and remove services.
        
        Args:
            volumes: Remove volumes
            remove_images: Remove images
        """
        logger.info("stopping_services", volumes=volumes, remove_images=remove_images)
        
        from ..utils.cli import run_command
        
        cmd = ["docker", "compose", "-f", str(self.compose_file),
               "-p", self.project_name, "down"]
        
        if volumes:
            cmd.append("-v")
        
        if remove_images:
            cmd.extend(["--rmi", "all"])
        
        run_command(cmd, cwd=self.project_dir)
        logger.info("services_stopped")
    
    def pause(self, services: Optional[List[str]] = None) -> None:
        """
        Pause running containers (freeze processes).
        
        Args:
            services: List of service names (None = all)
        """
        logger.info("pausing_services", services=services or "all")
        
        from ..utils.cli import run_command
        
        cmd = ["docker", "compose", "-f", str(self.compose_file),
               "-p", self.project_name, "pause"]
        
        if services:
            cmd.extend(services)
        
        run_command(cmd, cwd=self.project_dir)
        logger.info("services_paused")
    
    def unpause(self, services: Optional[List[str]] = None) -> None:
        """
        Unpause containers (resume processes).
        
        Args:
            services: List of service names (None = all)
        """
        logger.info("unpausing_services", services=services or "all")
        
        from ..utils.cli import run_command
        
        cmd = ["docker", "compose", "-f", str(self.compose_file),
               "-p", self.project_name, "unpause"]
        
        if services:
            cmd.extend(services)
        
        run_command(cmd, cwd=self.project_dir)
        logger.info("services_unpaused")
    
    def ps(self) -> List[Container]:
        """
        List running containers for this project.
        
        Returns:
            List of Container objects
        """
        filters = {"label": f"com.docker.compose.project={self.project_name}"}
        containers = self.client.containers.list(filters=filters, all=True)
        
        logger.debug("containers_listed", count=len(containers))
        return containers
    
    def logs(
        self,
        service: str,
        follow: bool = False,
        tail: int = 100,
    ) -> str:
        """
        Get logs for a service.
        
        Args:
            service: Service name
            follow: Follow log output
            tail: Number of lines from end
            
        Returns:
            Log output as string
        """
        containers = self.ps()
        
        for container in containers:
            labels = container.labels
            if labels.get("com.docker.compose.service") == service:
                logger.debug("fetching_logs", service=service, tail=tail)
                
                if follow:
                    # For follow, return generator
                    return container.logs(stream=True, follow=True, tail=tail)
                else:
                    return container.logs(tail=tail).decode("utf-8")
        
        raise NotFound(f"Service '{service}' not found")
    
    def exec(
        self,
        service: str,
        command: List[str],
    ) -> tuple[int, str]:
        """
        Execute command in service container.
        
        Args:
            service: Service name
            command: Command to execute
            
        Returns:
            Tuple of (exit_code, output)
        """
        containers = self.ps()
        
        for container in containers:
            labels = container.labels
            if labels.get("com.docker.compose.service") == service:
                logger.debug("executing_command", 
                           service=service,
                           command=" ".join(command))
                
                result = container.exec_run(command)
                return result.exit_code, result.output.decode("utf-8")
        
        raise NotFound(f"Service '{service}' not found")
    
    def _check_container_logs_for_errors(self, container: Container) -> Optional[str]:
        """
        Check container logs for critical errors.
        
        Args:
            container: Container to check
            
        Returns:
            Error message if found, None otherwise
        """
        try:
            # Get last 50 lines of logs
            logs = container.logs(tail=50).decode("utf-8", errors="ignore")
            
            # Critical error patterns
            critical_patterns = [
                "CRITICAL",
                "FATAL",
                "Segmentation fault",
                "core dumped",
                "Cannot allocate memory",
                "Address already in use",
                "Permission denied",
            ]
            
            # Check "No such file or directory" only for non-cert files
            # SDK tries /var/lib/ca first, then /share/ca - ERR is expected and not critical
            if "No such file or directory" in logs and "/opt/cellframe-node" in logs:
                # Exclude cert file errors if followed by successful "Initialized auth cert"
                if "/ca/" in logs and "Initialized auth cert" in logs:
                    pass  # Not critical - cert loaded from alternative path
                else:
                    critical_patterns.append("No such file or directory")
            
            for pattern in critical_patterns:
                if pattern and pattern in logs:
                    # Extract context around error
                    lines = logs.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line:
                            # Get 3 lines before and after
                            context_start = max(0, i - 3)
                            context_end = min(len(lines), i + 4)
                            context = '\n'.join(lines[context_start:context_end])
                            return f"Critical error found: {pattern}\n{context}"
            
            return None
        except Exception as e:
            logger.warning("failed_to_check_logs", container=container.name, error=str(e))
            return None
    
    def _check_network_status(self, container: Container) -> Optional[str]:
        """
        Check network status in Cellframe node logs.
        
        Returns network state: "SYNC", "OFFLINE", "ONLINE", or None if unknown
        """
        try:
            logs = container.logs(tail=200).decode("utf-8", errors="ignore")
            
            # Find LAST occurrence of state (most recent state wins)
            last_online_pos = max(logs.rfind("NET_STATE_ONLINE"), logs.rfind("state ONLINE"))
            last_sync_pos = max(logs.rfind("NET_STATE_SYNC_CHAINS"), logs.rfind("Synchronizing"))
            last_offline_pos = max(logs.rfind("NET_STATE_OFFLINE"), logs.rfind("state OFFLINE"))
            
            # Determine which state appeared last in logs
            positions = {
                "ONLINE": last_online_pos,
                "SYNC": last_sync_pos,
                "OFFLINE": last_offline_pos
            }
            
            # Filter out -1 (not found) and get max position
            valid_positions = {state: pos for state, pos in positions.items() if pos >= 0}
            if valid_positions:
                return max(valid_positions, key=valid_positions.get)
            
            return None
        except Exception as e:
            logger.warning("failed_to_check_network_status",
                         container=container.name,
                         error=str(e))
            return None
    
    def _check_port_listening(self, container: Container, port: int = 8079) -> bool:
        """
        Check if node is listening on specified port.
        
        Args:
            container: Container to check
            port: Port number to check
            
        Returns:
            True if port is listening, False otherwise
        """
        try:
            # Check if port is listening using netstat or ss
            result = container.exec_run(
                f"sh -c 'netstat -tuln 2>/dev/null | grep :{port} || ss -tuln 2>/dev/null | grep :{port}'",
                demux=False
            )
            
            if result.exit_code == 0 and result.output:
                output = result.output.decode("utf-8", errors="ignore")
                # Check if listening on 0.0.0.0 or specific IP
                if f":{port}" in output and ("LISTEN" in output or "0.0.0.0" in output):
                    logger.debug("port_listening",
                               container=container.name,
                               port=port)
                    return True
            
            logger.warning("port_not_listening",
                         container=container.name,
                         port=port)
            return False
        except Exception as e:
            logger.warning("failed_to_check_port",
                         container=container.name,
                         port=port,
                         error=str(e))
            return False
    
    def _check_peer_connectivity(self, container: Container) -> Dict[str, bool]:
        """
        Check if node can connect to its configured peers.
        
        Args:
            container: Container to check
            
        Returns:
            Dict mapping peer addresses to connectivity status
        """
        try:
            # Get logs to find seed nodes and check connection attempts
            logs = container.logs(tail=100).decode("utf-8", errors="ignore")
            
            connectivity = {}
            
            # Look for connection refused errors
            connection_errors = []
            for line in logs.split('\n'):
                if "Connection refused" in line or "errno 111" in line:
                    # Extract peer address from error message
                    import re
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', line)
                    if match:
                        peer = f"{match.group(1)}:{match.group(2)}"
                        connection_errors.append(peer)
                        connectivity[peer] = False
            
            if connection_errors:
                logger.warning("peer_connection_failures",
                             container=container.name,
                             failed_peers=connection_errors)
                return connectivity
            
            # If no errors found, assume connectivity is OK
            return connectivity
        except Exception as e:
            logger.warning("failed_to_check_peer_connectivity",
                         container=container.name,
                         error=str(e))
            return {}
    
    def _perform_early_diagnostics(self, containers: List[Container]) -> Optional[str]:
        """
        Perform early diagnostics to catch common issues quickly.
        
        This runs after a short grace period (15-20s) to detect:
        - Ports not listening
        - Connection refused errors between nodes
        - Missing configuration
        
        Args:
            containers: List of containers to check
            
        Returns:
            Error message if critical issue found, None otherwise
        """
        issues = []
        
        for container in containers:
            service_name = container.labels.get("com.docker.compose.service", "unknown")
            container.reload()
            
            if container.status != "running":
                continue
            
            # Check if port 8079 is listening
            if not self._check_port_listening(container, 8079):
                issues.append(
                    f"{service_name}: Port 8079 not listening (check listen_address/listen_port_tcp in config)"
                )
            
            # Check peer connectivity
            peer_issues = self._check_peer_connectivity(container)
            if peer_issues:
                failed_peers = [peer for peer, status in peer_issues.items() if not status]
                if failed_peers:
                    issues.append(
                        f"{service_name}: Cannot connect to peers: {', '.join(failed_peers)}"
                    )
        
        if issues:
            error_msg = (
                "Early diagnostics detected critical issues:\n" +
                "\n".join(f"  • {issue}" for issue in issues) +
                "\n\nCommon fixes:\n" +
                "  1. Check listen_address=[0.0.0.0:8079] in cellframe-node.cfg\n" +
                "  2. Ensure all nodes have correct seed_nodes_hosts configuration\n" +
                "  3. Verify Docker network connectivity between containers"
            )
            return error_msg
        
        return None
    
    def _get_node_loading_status(self, container: Container) -> str:
        """
        Get detailed node loading status with progress information.
        
        Returns:
            Status string like: "NET_STATE_ONLINE" or "LINKS_CONNECTING (2/3)" or "Initializing consensus"
        """
        try:
            # Use cellframe-node-cli to get current state (most reliable)
            cli_result = container.exec_run(
                'cellframe-node-cli net get status -net stagenet',
                demux=False
            )
            
            if cli_result.exit_code == 0:
                output = cli_result.output.decode("utf-8")
                # Parse CLI output for current state
                for line in output.split('\n'):
                    line = line.strip()
                    if 'current:' in line and 'NET_STATE_' in line:
                        # Extract state like "current: NET_STATE_ONLINE"
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            state = parts[1].strip()
                            # Get link info if available
                            if "NET_STATE_LINKS_CONNECTING" in state or "NET_STATE_ONLINE" in state:
                                for info_line in output.split('\n'):
                                    if 'active:' in info_line:
                                        try:
                                            active = int(info_line.split(':')[1].strip())
                                            for req_line in output.split('\n'):
                                                if 'required:' in req_line:
                                                    required = int(req_line.split(':')[1].strip())
                                                    if "NET_STATE_LINKS_CONNECTING" in state:
                                                        return f"NET_STATE_LINKS_CONNECTING ({active}/{required} links)"
                                                    break
                                        except:
                                            pass
                            return state
                return "Loading"
            
            # Fallback to log parsing
            logs = container.logs(tail=200).decode("utf-8", errors="ignore")
            
            # Check for CURRENT state first (most recent messages)
            # Split by lines and check from bottom to top
            lines = logs.split('\n')
            for line in reversed(lines[-50:]):  # Check last 50 lines
                if "NET_STATE_ONLINE" in line and "target:" not in line.lower():
                    return "NET_STATE_ONLINE"
                if "NET_STATE_SYNC_CHAINS" in line and "target:" not in line.lower():
                    return "Syncing chains"
                if "NET_STATE_LINKS_CONNECTING" in line and "target:" not in line.lower():
                    return "Connecting to peers"
                if "NET_STATE_OFFLINE" in line and "target:" not in line.lower():
                    return "NET_STATE_OFFLINE"
            
            # Check for initialization phases (only if no state found above)
            if "Initializing consensus" in logs or "consensus.state: SYNC" in logs:
                return "Initializing consensus"
            if "Loading chain" in logs or "Loaded chain files" in logs:
                return "Loading chains"
            
            return "Starting"
            
        except Exception as e:
            logger.warning("failed_to_get_loading_status",
                         container=container.name,
                         error=str(e))
            return "Unknown"
    
    def _check_node_online_status(self, container: Container) -> bool:
        """
        Check if Cellframe node is actually ONLINE by examining logs and network state.
        
        Args:
            container: Container to check
            
        Returns:
            True if node is online, False otherwise
        """
        try:
            # Get recent logs
            logs = container.logs(tail=200).decode("utf-8", errors="ignore")
            
            # Check for critical network initialization
            if "No networks initialized!" in logs:
                logger.warning("no_networks_initialized",
                             container=container.name)
                return False
            
            if "Can't find any nets" in logs:
                logger.warning("no_nets_found",
                             container=container.name)
                return False
            
            # Use cellframe-node-cli to check ONLINE status
            cli_result = container.exec_run(
                'cellframe-node-cli net get status -net stagenet',
                demux=False
            )
            
            if cli_result.exit_code == 0:
                output = cli_result.output.decode("utf-8")
                # Check for current state
                for line in output.split('\n'):
                    line = line.strip()
                    if 'current:' in line and 'NET_STATE_' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            current_state = parts[1].strip()
                            logger.debug("cli_state_check", container=container.name, state=current_state)
                            if current_state in ["NET_STATE_ONLINE", "NET_STATE_SYNC_CHAINS"]:
                                logger.info("network_ready_via_cli",
                                           container=container.name,
                                           state=current_state)
                                return True
                            logger.debug("network_not_ready_via_cli",
                                       container=container.name,
                                       state=current_state)
                            return False
                # If we couldn't find state in CLI output, node might still be starting
                logger.debug("no_state_in_cli_output", container=container.name)
                return False
            
            # Fallback: Check network status via logs
            net_status = self._check_network_status(container)
            if net_status in ["ONLINE", "SYNC"]:
                logger.debug("network_ready_via_logs",
                           container=container.name,
                           status=net_status)
                return True
            
            logger.debug("network_not_ready",
                       container=container.name,
                       status=net_status or "UNKNOWN")
            return False
            
        except Exception as e:
            logger.warning("failed_to_check_node_status",
                         container=container.name,
                         error=str(e))
            return False
    
    def _register_root_nodes(self, containers: List[Container]) -> None:
        """
        Register root nodes in node list using CLI command.
        
        Root nodes need to register themselves in the node list to act as balancers
        for other nodes (master and full nodes).
        
        Similar to tests-in-docker-example: one root node (node-1) registers all root nodes.
        
        Args:
            containers: List of containers to check and register
        """
        import re
        
        # Collect info about all root nodes (first 3 nodes)
        root_nodes = []
        for container in containers:
            service_name = container.labels.get("com.docker.compose.service", "unknown")
            
            if not service_name.startswith("node-"):
                continue
            
            try:
                node_num = int(service_name.split("-")[1])
            except (IndexError, ValueError):
                continue
            
            if node_num > 3:
                continue
            
            try:
                # Get node address
                dump_result = container.exec_run(
                    "/opt/cellframe-node/bin/cellframe-node-cli node dump -net stagenet",
                    demux=True
                )
                
                if dump_result.exit_code != 0:
                    logger.warning("failed_to_get_node_address",
                                 node=service_name)
                    continue
                
                output = dump_result.output[0].decode('utf-8') if dump_result.output[0] else ""
                match = re.search(r'Node addr:\s*([0-9A-F:]+)', output)
                if not match:
                    continue
                
                node_addr = match.group(1)
                
                # Get container IP
                container.reload()
                networks = container.attrs['NetworkSettings']['Networks']
                container_ip = None
                for net_name, net_settings in networks.items():
                    if net_settings.get('IPAddress'):
                        container_ip = net_settings['IPAddress']
                        break
                
                if not container_ip:
                    continue
                
                root_nodes.append({
                    'container': container,
                    'service_name': service_name,
                    'node_num': node_num,
                    'addr': node_addr,
                    'ip': container_ip
                })
            except Exception as e:
                logger.error("failed_to_collect_root_node_info",
                           node=service_name,
                           error=str(e))
        
        if not root_nodes:
            logger.warning("no_root_nodes_found")
            return
        
        # Wait for node-1 to become ROOT (has authorization)
        # Then use it to register all root nodes
        node1 = next((n for n in root_nodes if n['node_num'] == 1), None)
        if not node1:
            logger.warning("node_1_not_found_for_registration")
            return
        
        # Wait up to 30 seconds for node-1 to have ROOT role
        logger.info("waiting_for_node1_root_role")
        max_wait = 30
        wait_interval = 2
        
        for attempt in range(max_wait // wait_interval):
            # Try to execute node list to check if we have ROOT rights
            test_result = node1['container'].exec_run(
                "/opt/cellframe-node/bin/cellframe-node-cli node list -net stagenet",
                demux=True
            )
            
            output = test_result.output[0].decode('utf-8') if test_result.output and test_result.output[0] else ""
            
            if "You have no access rights" not in output:
                logger.info("node1_has_root_role", elapsed=f"{attempt * wait_interval}s")
                break
            
            time.sleep(wait_interval)
        else:
            logger.warning("node1_root_role_timeout", waited=f"{max_wait}s")
            # Continue anyway - balancer will handle it
            return
        
        # Now register all root nodes via node-1
        for node_info in root_nodes:
            try:
                exec_result = node1['container'].exec_run(
                    f"/opt/cellframe-node/bin/cellframe-node-cli node add -net stagenet -addr {node_info['addr']} -host {node_info['ip']} -port 8079",
                    demux=True
                )
                
                if exec_result.exit_code == 0:
                    output = exec_result.output[0].decode('utf-8').strip() if exec_result.output[0] else ""
                    
                    # Check if actually succeeded (not "You have no access rights")
                    if "You have no access rights" in output:
                        logger.debug("root_registration_no_rights",
                                   registered_by="node-1",
                                   target=node_info['service_name'])
                    else:
                        logger.info("root_node_registered",
                                  registered_by="node-1",
                                  target_node=node_info['service_name'],
                                  addr=node_info['addr'],
                                  ip=node_info['ip'],
                                  output=output)
                else:
                    error_msg = exec_result.output[1].decode('utf-8').strip() if exec_result.output[1] else "Unknown error"
                    logger.debug("root_node_registration_failed",
                               registered_by="node-1",
                               target_node=node_info['service_name'],
                               error=error_msg)
            except Exception as e:
                logger.debug("failed_to_register_root_node",
                           registered_by="node-1",
                           target_node=node_info['service_name'],
                           error=str(e))
    
    def wait_for_services(
        self,
        services: Optional[List[str]] = None,
        timeout: int = 300,
        check_logs: bool = True,
    ) -> None:
        """
        Wait for services to be healthy and online.
        
        This method performs comprehensive checks:
        1. Container is running
        2. No critical errors in logs
        3. Node has transitioned to ONLINE state
        4. Immediate failure detection
        5. Early diagnostics after 15-20s (port listening, peer connectivity)
        
        Args:
            services: List of service names (None = all)
            timeout: Timeout in seconds
            check_logs: Whether to check logs for errors
        """
        logger.info("waiting_for_services", timeout=timeout, check_logs=check_logs)
        
        start_time = time.time()
        last_status_log = 0
        early_diagnostics_run = False
        
        while time.time() - start_time < timeout:
            containers = self.ps()  # Get all containers including stopped
            
            # Run early diagnostics after 15-20 seconds to catch configuration issues early
            current_time = time.time()
            if not early_diagnostics_run and (current_time - start_time) >= 15:
                logger.info("running_early_diagnostics", elapsed=f"{int(current_time - start_time)}s")
                diagnostic_error = self._perform_early_diagnostics(containers)
                if diagnostic_error:
                    logger.error("early_diagnostics_failed", error=diagnostic_error)
                    raise RuntimeError(f"Early diagnostics failed:\n{diagnostic_error}")
                else:
                    logger.info("early_diagnostics_passed")
                # Wait a bit more for nodes to fully initialize server components
                time.sleep(10)
                # Register root nodes immediately after diagnostics pass
                # This breaks the circular dependency: nodes need registered root nodes to go ONLINE
                self._register_root_nodes(containers)
                early_diagnostics_run = True
            
            if not containers:
                logger.debug("no_containers_found")
                time.sleep(2)
                continue
            
            all_healthy = True
            failed_containers = []
            pending_containers = []
            
            for container in containers:
                # Check if this is one of our target services
                service_name = container.labels.get("com.docker.compose.service")
                
                if services and service_name not in services:
                    continue
                
                # Refresh container state
                container.reload()
                
                # CRITICAL: Check if container has exited
                if container.status in ["exited", "dead", "removing"]:
                    exit_code = container.attrs.get("State", {}).get("ExitCode", -1)
                    
                    # Get last logs before failure
                    try:
                        logs = container.logs(tail=30).decode("utf-8", errors="ignore")
                    except Exception:
                        logs = "(unable to fetch logs)"
                    
                    error_msg = (
                        f"Container {service_name} has FAILED!\n"
                        f"Status: {container.status}\n"
                        f"Exit code: {exit_code}\n"
                        f"Last logs:\n{logs}"
                    )
                    
                    logger.error("container_failed",
                               service=service_name,
                               status=container.status,
                               exit_code=exit_code)
                    
                    raise RuntimeError(error_msg)
                
                # Check if running
                if container.status != "running":
                    all_healthy = False
                    pending_containers.append(service_name)
                    continue
                
                # Check for critical errors in logs
                if check_logs:
                    error = self._check_container_logs_for_errors(container)
                    if error:
                        logger.error("critical_error_in_logs",
                                   service=service_name,
                                   error=error)
                        raise RuntimeError(
                            f"Critical error detected in {service_name}:\n{error}"
                        )
                
                # If container has health check, verify it
                health = container.attrs.get("State", {}).get("Health", {})
                if health:
                    health_status = health.get("Status")
                    if health_status == "unhealthy":
                        all_healthy = False
                        failed_containers.append(f"{service_name} (unhealthy)")
                        continue
                    elif health_status != "healthy":
                        all_healthy = False
                        pending_containers.append(f"{service_name} ({health_status})")
                        continue
                
                # Check if node is actually ONLINE and get detailed status
                if not self._check_node_online_status(container):
                    all_healthy = False
                    # Get detailed loading status for better visibility
                    loading_status = self._get_node_loading_status(container)
                    pending_containers.append(f"{service_name} ({loading_status})")
                    continue
            
            # Log status periodically
            current_time = time.time()
            if current_time - last_status_log >= 5:
                elapsed = int(current_time - start_time)
                if pending_containers:
                    logger.info("waiting_progress",
                              elapsed=f"{elapsed}s",
                              pending=", ".join(pending_containers))
                last_status_log = current_time
            
            if all_healthy and containers:
                logger.info("services_ready", elapsed=f"{int(time.time() - start_time)}s")
                return
            
            time.sleep(2)
        
        # Timeout reached
        containers = self.ps()
        status_info = []
        for container in containers:
            service_name = container.labels.get("com.docker.compose.service", "unknown")
            container.reload()
            status_info.append(f"{service_name}: {container.status}")
        
        error_msg = (
            f"Services not ready after {timeout}s\n"
            f"Status: {', '.join(status_info)}"
        )
        logger.error("services_timeout", timeout=timeout, status=status_info)
        raise TimeoutError(error_msg)
    
    def get_service_status(self) -> Dict[str, str]:
        """
        Get status of all services.
        
        Returns:
            Dict mapping service name to status
        """
        containers = self.ps()
        
        status = {}
        for container in containers:
            service = container.labels.get("com.docker.compose.service", "unknown")
            status[service] = container.status
        
        return status

