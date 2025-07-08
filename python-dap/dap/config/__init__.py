"""
🧬 DAP Config Module

Direct Python wrappers over DAP config functions.
"""

from .config import DapConfig, get_dap_config
from ..core.exceptions import DapException, DapConfigError

__all__ = [
    'DapConfig', 'get_dap_config', 'DapException', 'DapConfigError'
]
