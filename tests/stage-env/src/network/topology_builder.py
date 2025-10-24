"""
Dynamic topology builder from scenario node specifications.

Builds network topology configuration dynamically from scenario definitions,
allowing flexible node count and roles based on test requirements.
"""

from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

from ..config.loader import ConfigLoader, NetworkTopology
from ..scenarios.schema import NodeConfig as ScenarioNodeConfig
from .models import NodeConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TopologyBuilder:
    """Build network topology from scenario node specifications."""
    
    def __init__(self, base_path: Path, config_path: Optional[Path] = None):
        """
        Initialize topology builder.
        
        Args:
            base_path: Base path to stage-env directory
            config_path: Optional path to stage-env.cfg
        """
        self.base_path = base_path
        self.config_loader = ConfigLoader(base_path, config_path)
    
    def build_from_scenario_nodes(
        self,
        scenario_nodes: List[ScenarioNodeConfig],
        network_name: str = "stagenet",
        network_id: str = "0x1234"
    ) -> NetworkTopology:
        """
        Build topology from scenario node specifications.
        
        Args:
            scenario_nodes: List of node configurations from scenario
            network_name: Network name
            network_id: Network ID
            
        Returns:
            NetworkTopology object
        """
        logger.info("building_topology_from_scenario",
                   node_count=len(scenario_nodes),
                   network=network_name)
        
        # Group nodes by role and count them
        role_counts = self._count_nodes_by_role(scenario_nodes)
        
        logger.debug("node_role_distribution",
                    root=role_counts['root'],
                    master=role_counts['master'],
                    full=role_counts['full'])
        
        # Build topology configuration
        topology_dict = self._build_topology_dict(
            role_counts,
            network_name,
            network_id
        )
        
        # Validate and return
        topology = NetworkTopology(**topology_dict)
        return topology
    
    def build_node_configs(
        self,
        scenario_nodes: List[ScenarioNodeConfig],
        topology: NetworkTopology
    ) -> List[NodeConfig]:
        """
        Build node configurations from scenario nodes.
        
        Args:
            scenario_nodes: List of scenario node specs
            topology: Network topology
            
        Returns:
            List of NodeConfig objects
        """
        logger.info("building_node_configs", count=len(scenario_nodes))
        
        nodes = []
        
        for idx, scenario_node in enumerate(scenario_nodes, start=1):
            # Calculate ports
            base_cf_port = topology.network_settings.base_cf_port
            base_http_port = topology.network_settings.base_http_port
            base_p2p_port = topology.network_settings.base_p2p_port
            base_rpc_port = topology.network_settings.base_rpc_port
            # Use node_port from topology or scenario node override
            node_port = scenario_node.port if hasattr(scenario_node, 'port') and scenario_node.port else topology.network_settings.node_port
            
            # Calculate IP address
            base_ip_parts = topology.network_settings.base_ip.split('.')
            node_ip = f"{'.'.join(base_ip_parts[:3])}.{int(base_ip_parts[3]) + idx - 1}"
            
            # Determine if seed node and balancer
            is_seed = scenario_node.role == "root"
            balancer_enabled = scenario_node.role == "root"
            consensus_participation = scenario_node.validator or scenario_node.role == "master"
            
            node_config = NodeConfig(
                node_id=idx,
                role=scenario_node.role,
                node_type=scenario_node.role + "_nodes",  # For grouping
                rpc_port=base_rpc_port + idx - 1,
                p2p_port=base_p2p_port + idx - 1,
                cf_port=base_cf_port + idx - 1,
                http_port=base_http_port + idx - 1,
                node_port=node_port,
                ip_address=scenario_node.ip if scenario_node.ip else node_ip,
                is_seed_node=is_seed,
                balancer_enabled=balancer_enabled,
                consensus_participation=consensus_participation
            )
            
            nodes.append(node_config)
            logger.debug("node_config_created",
                        node_id=idx,
                        role=scenario_node.role,
                        ip=node_config.ip_address,
                        is_seed=is_seed)
        
        return nodes
    
    def _count_nodes_by_role(self, nodes: List[ScenarioNodeConfig]) -> Dict[str, int]:
        """Count nodes grouped by role."""
        counts = defaultdict(int)
        
        for node in nodes:
            counts[node.role] += 1
        
        return {
            'root': counts.get('root', 0),
            'master': counts.get('master', 0),
            'full': counts.get('full', 0),
            'light': counts.get('light', 0),
            'archive': counts.get('archive', 0)
        }
    
    def _build_topology_dict(
        self,
        role_counts: Dict[str, int],
        network_name: str,
        network_id: str
    ) -> Dict:
        """Build topology dictionary from role counts."""
        
        # Build topology nodes section
        topology_nodes = {}
        
        if role_counts['root'] > 0:
            topology_nodes['root_nodes'] = {
                'count': role_counts['root'],
                'role': 'root',
                'consensus_participation': False,
                'is_seed_node': True,
                'balancer_enabled': True,
                'description': 'Root seed nodes - authorized infrastructure with HTTP balancer'
            }
        
        if role_counts['master'] > 0:
            topology_nodes['master_nodes'] = {
                'count': role_counts['master'],
                'role': 'master',
                'consensus_participation': True,
                'is_seed_node': False,
                'description': 'Master validator nodes - consensus participants'
            }
        
        if role_counts['full'] > 0:
            topology_nodes['full_nodes'] = {
                'count': role_counts['full'],
                'role': 'full',
                'consensus_participation': False,
                'is_seed_node': False,
                'description': 'Full sync nodes without consensus participation'
            }
        
        if role_counts['archive'] > 0:
            topology_nodes['archive_nodes'] = {
                'count': role_counts['archive'],
                'role': 'archive',
                'consensus_participation': False,
                'is_seed_node': False,
                'description': 'Archive nodes for historical data'
            }
        
        # Build full topology structure
        topology_dict = {
            'network': {
                'name': network_name,
                'network_id': network_id,
                'consensus': 'esbocs'
            },
            'topology': topology_nodes,
            'consensus': {
                'type': 'esbocs',
                'min_validators': max(2, role_counts['root'] + role_counts['master'] - 1),
                'new_round_delay': 45,
                'collecting_level': 10.0,
                'auth_certs_prefix': f'{network_name}.master'
            },
            'balancer': {
                'enabled': role_counts['root'] > 0,
                'type': 'http',
                'uri': 'f0intlt4eyl03htogu',
                'max_links_response': 10,
                'request_delay': 20
            },
            'network_settings': {
                'base_rpc_port': 8545,
                'base_p2p_port': 31337,
                'base_cf_port': 7007,
                'base_http_port': 8079,
                'base_ip': '172.20.0.10',
                'subnet': '172.20.0.0/16'
            },
            'build': {
                'type': 'debug',
                'cellframe_version': 'latest'
            },
            'features': {
                'monitoring': False,
                'tests': False,
                'crash_artifacts': True
            }
        }
        
        return topology_dict
    
    def load_or_build_topology(
        self,
        topology_name: Optional[str] = None,
        scenario_nodes: Optional[List[ScenarioNodeConfig]] = None
    ) -> NetworkTopology:
        """
        Load topology from file or build from scenario nodes.
        
        Priority:
        1. If scenario_nodes provided, build dynamically from them
        2. Otherwise load topology_name from config
        
        Args:
            topology_name: Topology file name (without .json)
            scenario_nodes: Optional scenario node specifications
            
        Returns:
            NetworkTopology object
        """
        if scenario_nodes:
            logger.info("building_dynamic_topology_from_scenario",
                       node_count=len(scenario_nodes))
            return self.build_from_scenario_nodes(scenario_nodes)
        
        # Load from file
        topology_name = topology_name or "default"
        logger.info("loading_topology_from_file", topology=topology_name)
        return self.config_loader.load_topology(topology_name)

