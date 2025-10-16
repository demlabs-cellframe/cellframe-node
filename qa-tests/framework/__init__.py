"""
Cellframe Node Test Framework
Профессиональный фреймворк для тестирования Cellframe Node
"""

from .config import get_config, TestConfig
from .utils import execute_command, CommandResult
from .pages.node_cli import NodeCLI, NetworkStatus, NodeInfo
from .assertions import NodeAssertions
from .fixtures import *

__version__ = "1.0.0"

__all__ = [
    'get_config', 'TestConfig',
    'execute_command', 'CommandResult', 
    'NodeCLI', 'NetworkStatus', 'NodeInfo',
    'NodeAssertions'
]
