"""
🧬 DAP Events Module

Direct Python wrappers over DAP events functions.
"""

from .events import DapEvents, DapEventType, get_dap_events
from ..core.exceptions import DapException, DapEventError

__all__ = [
    'DapEvents', 'DapEventType', 'get_dap_events', 'DapException', 'DapEventError'
]
