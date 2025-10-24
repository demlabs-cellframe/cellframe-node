"""
YAML scenario schema definitions using Pydantic.

Provides type-safe models for test scenario definitions,
ensuring validation and user-friendly error messages.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class NodeRole(str, Enum):
    """Node role in network topology."""
    ROOT = "root"
    MASTER = "master"
    FULL = "full"
    LIGHT = "light"
    ARCHIVE = "archive"


class ExpectResult(str, Enum):
    """Expected command result."""
    SUCCESS = "success"
    ERROR = "error"
    ANY = "any"


class DatumStatus(str, Enum):
    """Status of datum processing through the network."""
    NOT_FOUND = "not_found"
    IN_MEMPOOL = "in_mempool"
    VERIFIED = "verified"
    IN_BLOCKS = "in_blocks"
    PROPAGATED = "propagated"
    REJECTED = "rejected"
    TIMEOUT_MEMPOOL = "timeout_mempool"
    TIMEOUT_VERIFICATION = "timeout_verification"
    TIMEOUT_BLOCKS = "timeout_blocks"
    TIMEOUT_TOTAL = "timeout_total"


# ============================================================================
# Network Configuration Models
# ============================================================================

class NodePackageSourceConfig(BaseModel):
    """Package source configuration for a node in YAML scenarios."""
    type: str = Field(..., description="Source type: url, repository, or local")
    
    # URL source
    url: Optional[str] = Field(None, description="Package URL")
    checksum: Optional[str] = Field(None, description="Package checksum for verification")
    
    # Repository source  
    git_url: Optional[str] = Field(None, description="Git repository URL")
    branch: Optional[str] = Field(None, description="Git branch")
    commit: Optional[str] = Field(None, description="Specific commit hash")
    build_type: Optional[str] = Field(None, description="Build type: Debug, Release, RelWithDebInfo")
    
    # Local source
    local_path: Optional[str] = Field(None, description="Path to local .deb file")


class NodeConfig(BaseModel):
    """Single node configuration."""
    name: str = Field(..., description="Unique node identifier")
    role: NodeRole = Field(NodeRole.FULL, description="Node role in network")
    ip: Optional[str] = Field(None, description="Optional static IP")
    port: Optional[int] = Field(None, ge=1024, le=65535, description="Optional custom node port (default: 8079)")
    validator: bool = Field(False, description="Is validator node")
    
    # Per-node package source 
    package: Optional[NodePackageSourceConfig] = Field(None, description="Custom package source for this node")
    
    # Per-node customizations
    custom_packages: Optional[List[str]] = Field(None, description="Additional packages to install")
    custom_env: Optional[Dict[str, str]] = Field(None, description="Custom environment variables")
    
    # Docker customizations
    docker_volumes: Optional[List[str]] = Field(None, description="Additional volume mounts (host:container[:mode])")
    docker_capabilities: Optional[List[str]] = Field(None, description="Additional Linux capabilities")
    docker_devices: Optional[List[str]] = Field(None, description="Device mappings")
    docker_extra: Optional[Dict[str, Any]] = Field(None, description="Raw docker-compose config sections")
    
    class Config:
        use_enum_values = True


class NetworkConfig(BaseModel):
    """Network topology configuration."""
    topology: str = Field("default", description="Topology template name")
    nodes: List[NodeConfig] = Field(default_factory=list, description="Node configurations")
    
    @field_validator("topology")
    @classmethod
    def validate_topology(cls, v: str) -> str:
        """Ensure topology is specified."""
        if not v or not v.strip():
            raise ValueError("Network topology must be specified")
        return v.strip()


# ============================================================================
# Package Installation Models
# ============================================================================

class AptPackage(BaseModel):
    """APT package installation."""
    node: Union[str, List[str]] = Field(..., description="Node(s) to install on")
    apt: List[str] = Field(..., description="Package names to install")


class LocalPackage(BaseModel):
    """Local DEB package installation."""
    node: Union[str, List[str]] = Field(..., description="Node(s) to install on")
    local: str = Field(..., description="Local path to .deb file (supports glob)")


class URLPackage(BaseModel):
    """Remote package installation."""
    node: Union[str, List[str]] = Field(..., description="Node(s) to install on")
    url: str = Field(..., description="URL to download package from")
    checksum: Optional[str] = Field(None, description="Optional checksum (sha256:...)")


PackageSpec = Union[AptPackage, LocalPackage, URLPackage]


# ============================================================================
# File Placement Models
# ============================================================================

class FileFromSource(BaseModel):
    """Copy file from host to node."""
    node: Union[str, List[str]] = Field(..., description="Target node(s)")
    src: str = Field(..., description="Source file path on host")
    dst: str = Field(..., description="Destination path in node")
    mode: Optional[str] = Field(None, description="File permissions (e.g., '0755')")


class FileFromContent(BaseModel):
    """Create file from inline content."""
    node: Union[str, List[str]] = Field(..., description="Target node(s)")
    content: str = Field(..., description="File content (supports variables)")
    dst: str = Field(..., description="Destination path in node")
    mode: Optional[str] = Field(None, description="File permissions (e.g., '0755')")


FileSpec = Union[FileFromSource, FileFromContent]


# ============================================================================
# Extract Helpers - Built-in data extraction with validation
# ============================================================================

class ExtractType(str, Enum):
    """Type of data to extract and validate."""
    WALLET_ADDRESS = "wallet_address"  # Wallet address (base58, 75-105 chars)
    NODE_ADDRESS = "node_address"      # Node address (hex with :: separators, e.g., A1B2::C3D4::E5F6)
    HASH = "hash"                      # Transaction/block hash (0x... hex)
    NUMBER = "number"                  # Numeric value
    TOKEN_NAME = "token_name"          # Token ticker (alphanumeric)
    BOOL = "bool"                      # Boolean value
    RAW = "raw"                        # Raw string (no validation)


class ExtractSpec(BaseModel):
    """Specification for extracting and validating data from command output."""
    pattern: Optional[str] = Field(None, description="Regex pattern to extract data (auto-detected if not specified)")
    type: ExtractType = Field(ExtractType.RAW, description="Type of extracted data for validation")
    group: int = Field(1, description="Regex capture group number (default: 1)")
    required: bool = Field(True, description="Whether extraction failure should fail the test")
    default: Optional[str] = Field(None, description="Default value if extraction fails (only if not required)")
    
    class Config:
        use_enum_values = True


# ============================================================================
# Test Step Models
# ============================================================================

class CLIStep(BaseModel):
    """Execute CLI command."""
    cli: str = Field(..., description="CLI command to execute")
    node: str = Field("node1", description="Node to execute on")
    save: Optional[str] = Field(None, description="Variable name to save result to")
    extract_to: Optional[Dict[str, ExtractSpec]] = Field(None, description="Extract and save specific values from output")
    wait: Optional[str] = Field(None, description="Wait duration after command (e.g., '5s')")
    expect: ExpectResult = Field(ExpectResult.SUCCESS, description="Expected result")
    contains: Optional[str] = Field(None, description="Expected substring in output")
    timeout: Optional[int] = Field(30, description="Command timeout in seconds")
    
    class Config:
        use_enum_values = True


class RPCStep(BaseModel):
    """Execute JSON-RPC call."""
    rpc: str = Field(..., description="JSON-RPC method name")
    params: List[Any] = Field(default_factory=list, description="RPC parameters")
    node: str = Field("node1", description="Node to call RPC on")
    save: Optional[str] = Field(None, description="Variable name to save result to")
    wait: Optional[str] = Field(None, description="Wait duration after call")
    expect: ExpectResult = Field(ExpectResult.SUCCESS, description="Expected result")
    timeout: Optional[int] = Field(30, description="RPC call timeout")
    
    class Config:
        use_enum_values = True


class WaitStep(BaseModel):
    """Wait for duration or condition."""
    wait: str = Field(..., description="Duration (e.g., '5s') or condition")


class PythonStep(BaseModel):
    """Execute Python code with access to context."""
    python: str = Field(..., description="Python code to execute")
    save: Optional[str] = Field(None, description="Variable name to save result to")


class BashStep(BaseModel):
    """Execute Bash script."""
    bash: str = Field(..., description="Bash script to execute")
    node: str = Field("node1", description="Node to execute on")
    save: Optional[str] = Field(None, description="Variable name to save result to")
    expect: ExpectResult = Field(ExpectResult.SUCCESS, description="Expected result")
    timeout: Optional[int] = Field(30, description="Script timeout in seconds")
    
    class Config:
        use_enum_values = True


class LoopStep(BaseModel):
    """Loop over steps multiple times."""
    loop: int = Field(..., gt=0, description="Number of iterations")
    steps: List["TestStep"] = Field(..., description="Steps to repeat")


class WaitForDatumStep(BaseModel):
    """Wait for datum to be processed through mempool → verification → blocks → propagation."""
    wait_for_datum: Union[str, List[str]] = Field(..., description="Datum hash(es) to monitor")
    node: str = Field("node1", description="Target node to check for datum")
    network: str = Field("stagenet", description="Network name")
    chain: str = Field("main", description="Chain name")
    check_master_nodes: bool = Field(True, description="Check master nodes for verification and blocks")
    timeout_total: int = Field(300, description="Total timeout in seconds")
    timeout_mempool: int = Field(60, description="Timeout for mempool stage")
    timeout_verification: int = Field(120, description="Timeout after verification")
    timeout_in_blocks: int = Field(180, description="Timeout after appearing in blocks")
    check_interval: int = Field(2, description="Check interval in seconds")
    save_status: Optional[str] = Field(None, description="Variable name to save final status")


TestStep = Union[CLIStep, RPCStep, WaitStep, WaitForDatumStep, PythonStep, BashStep, LoopStep]


# ============================================================================
# Check/Assertion Models
# ============================================================================

class CLICheck(BaseModel):
    """Verify CLI command output."""
    cli: str = Field(..., description="CLI command to execute")
    node: str = Field("node1", description="Node to execute on")
    contains: Optional[str] = Field(None, description="Expected substring")
    not_contains: Optional[str] = Field(None, description="Substring that should not be present")
    equals: Optional[str] = Field(None, description="Exact expected output")
    timeout: Optional[int] = Field(30, description="Command timeout")


class RPCCheck(BaseModel):
    """Verify JSON-RPC call result."""
    rpc: str = Field(..., description="JSON-RPC method")
    params: List[Any] = Field(default_factory=list, description="RPC parameters")
    node: str = Field("node1", description="Node to call on")
    result_contains: Optional[Any] = Field(None, description="Expected value in result")
    result_equals: Optional[Any] = Field(None, description="Exact expected result")
    timeout: Optional[int] = Field(30, description="RPC timeout")


class PythonCheck(BaseModel):
    """Verify condition using Python code."""
    python: str = Field(..., description="Python code that should not raise AssertionError")


class BashCheck(BaseModel):
    """Verify condition using Bash script."""
    bash: str = Field(..., description="Bash script (exit 0 = success)")
    node: str = Field("node1", description="Node to execute on")
    timeout: Optional[int] = Field(30, description="Script timeout")


CheckSpec = Union[CLICheck, RPCCheck, PythonCheck, BashCheck]


# ============================================================================
# Step Defaults and Grouping
# ============================================================================

class StepDefaults(BaseModel):
    """Default parameters for steps in a section or group."""
    node: Optional[str] = Field(None, description="Default node for all steps")
    wait: Optional[str] = Field(None, description="Default wait duration after each step")
    expect: Optional[ExpectResult] = Field(None, description="Default expected result")
    timeout: Optional[int] = Field(None, description="Default timeout in seconds")
    cli: Optional[Dict[str, str]] = Field(None, description="Default CLI option prefixes (e.g., {'net': 'stagenet'})")
    
    class Config:
        use_enum_values = True


class StepGroup(BaseModel):
    """Group of steps with shared defaults."""
    name: Optional[str] = Field(None, description="Group name for logging")
    defaults: Optional[StepDefaults] = Field(None, description="Default parameters for this group")
    steps: List[Union["TestStep", "StepGroup"]] = Field(..., description="Steps in this group")


# Update TestStep to include StepGroup
TestStep = Union[CLIStep, RPCStep, WaitStep, WaitForDatumStep, PythonStep, BashStep, LoopStep, StepGroup]


# ============================================================================
# Section Configuration (for setup/test/check)
# ============================================================================

class SectionConfig(BaseModel):
    """Configuration for a test section (setup/test)."""
    defaults: Optional[StepDefaults] = Field(None, description="Default parameters for all steps in this section")
    steps: List[TestStep] = Field(default_factory=list, description="Steps in this section")


class CheckSectionConfig(BaseModel):
    """Configuration for check section (different from test/setup)."""
    defaults: Optional[StepDefaults] = Field(None, description="Default parameters for all checks in this section")
    steps: List[CheckSpec] = Field(default_factory=list, description="Checks in this section")


# ============================================================================
# Main Scenario Model
# ============================================================================

class ScenarioMetadata(BaseModel):
    """Scenario metadata and description."""
    name: str = Field(..., description="Scenario display name")
    description: str = Field(..., description="What this scenario tests")
    author: Optional[str] = Field(None, description="Scenario author")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    version: str = Field("1.0", description="Scenario version")


class SuiteDescriptor(BaseModel):
    """Test suite descriptor (metadata only, no executable steps)."""
    
    # Suite marker with name (elegant single field)
    suite: str = Field(..., description="Suite name (presence of this field marks it as suite descriptor)")
    
    # Metadata
    description: Optional[str] = Field(None, description="Suite description")
    author: Optional[str] = Field(None, description="Author name")
    tags: List[str] = Field(default_factory=list, description="Tags")
    version: str = Field("1.0", description="Version")
    
    # Suite-specific metadata
    scenarios: List[str] = Field(default_factory=list, description="List of scenario files in this suite")
    
    # Optional network configuration for suite-level defaults
    network: Optional[NetworkConfig] = Field(None, description="Default network topology for suite")
    
    @property
    def name(self) -> str:
        """Alias for suite name (for compatibility)."""
        return self.suite


class TestScenario(BaseModel):
    """Complete test scenario definition."""
    
    # Metadata
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    author: Optional[str] = Field(None, description="Author name")
    tags: List[str] = Field(default_factory=list, description="Tags")
    version: str = Field("1.0", description="Version")
    
    # Includes for reusable configs
    includes: List[str] = Field(default_factory=list, description="Paths to included YAML files")
    
    # Network configuration (optional, defaults to 'default' topology)
    network: Optional[NetworkConfig] = Field(None, description="Network topology (default: topology='default')")
    
    # Package installation
    packages: List[PackageSpec] = Field(default_factory=list, description="Packages to install")
    
    # File placement
    files: List[FileSpec] = Field(default_factory=list, description="Files to place in nodes")
    
    # Global defaults (applied to all sections)
    defaults: Optional[StepDefaults] = Field(None, description="Global default parameters")
    
    # Setup phase - can be either list of steps (old format) or SectionConfig (new format)
    setup: Union[List[TestStep], SectionConfig] = Field(default_factory=list, description="Setup steps")
    
    # Test phase - can be either list of steps (old format) or SectionConfig (new format)
    test: Union[List[TestStep], SectionConfig] = Field(..., description="Test steps")
    
    # Check phase - can be either list of checks (old format) or CheckSectionConfig (new format)
    check: Union[List[CheckSpec], CheckSectionConfig] = Field(default_factory=list, description="Assertions")
    
    # Variables (runtime context)
    variables: Dict[str, Any] = Field(default_factory=dict, description="Predefined variables")
    
    @model_validator(mode='after')
    def validate_scenario(self) -> 'TestScenario':
        """Validate scenario structure."""
        # Set default network if not specified
        if self.network is None:
            self.network = NetworkConfig(topology="default")
        
        # Normalize sections to SectionConfig/CheckSectionConfig format
        if isinstance(self.setup, list):
            self.setup = SectionConfig(steps=self.setup)
        if isinstance(self.test, list):
            self.test = SectionConfig(steps=self.test)
        if isinstance(self.check, list):
            self.check = CheckSectionConfig(steps=self.check)
        
        # Validate at least one test step
        if not self.test.steps:
            raise ValueError("Test scenario must have at least one test step")
        
        return self


# Allow forward references for recursive models
LoopStep.model_rebuild()
StepGroup.model_rebuild()

