"""
Data models for network management.

Defines common models used across network management modules.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class NodePackageSource(BaseModel):
    """Source for cellframe-node package for a specific node."""
    
    type: str  # url, repository, local
    # For URL source
    url: Optional[str] = None
    checksum: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    # For repository source
    git_url: Optional[str] = None
    branch: Optional[str] = None
    commit: Optional[str] = None
    submodules: Optional[bool] = None
    build_type: Optional[str] = None
    cmake_flags: Optional[str] = None
    git_username: Optional[str] = None
    git_token: Optional[str] = None
    build_script: Optional[str] = None
    
    # For local source
    local_path: Optional[str] = None
    
    # Advanced options
    cache_packages: Optional[bool] = True
    verify_signature: Optional[bool] = False
    gpg_key_url: Optional[str] = None
    docker_build_args: Optional[str] = None
    install_recommends: Optional[bool] = True
    force_reinstall: Optional[bool] = False


class NodeConfig(BaseModel):
    """Configuration for a single node."""
    
    node_id: int
    role: str  # root, master, full, validator
    node_type: str  # for grouping
    rpc_port: int
    p2p_port: int
    cf_port: int
    http_port: int
    node_port: int = 8079  # Standard Cellframe node port for P2P/HTTP communications
    ip_address: str
    is_seed_node: bool = False  # Whether this node acts as a seed node
    balancer_enabled: bool = False  # Whether HTTP balancer is enabled
    consensus_participation: bool = False  # Whether participates in consensus
    
    # Per-node package source (optional, overrides global node_source)
    package_source: Optional[NodePackageSource] = None
    
    # Per-node customizations (optional, extends role customizations)
    custom_packages: Optional[str] = None  # Comma-separated package names
    custom_post_script: Optional[str] = None  # Path to post-install script
    custom_env_vars: Optional[Dict[str, str]] = None  # Additional environment variables
    
    # Docker customizations (optional, extends base docker config)
    docker_volumes: Optional[List[str]] = None  # Additional volume mounts: ["host:container:mode"]
    docker_capabilities: Optional[List[str]] = None  # Additional capabilities: ["NET_ADMIN", "SYS_ADMIN"]
    docker_devices: Optional[List[str]] = None  # Device mappings: ["/dev/net/tun"]
    docker_extra_config: Optional[Dict[str, Any]] = None  # Raw docker-compose config sections

