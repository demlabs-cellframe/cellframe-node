"""
🧬 DAP Core Module

Specialized core classes for DAP operations:
- Dap: Central initialization and coordination
- DapType: Type conversion and formatting utilities
- DapLogging: Logging configuration and management
- DapTime: Time operations and DAP time utilities
- DapSystem: System utilities for DAP-specific operations

Example:
    # Initialize all DAP systems
    with Dap() as dap:
        # Access subsystems
        logging = dap.logging
        time = dap.time
        system = dap.system
        
        # Use subsystems
        current_time = time.now_dap()
        result = system.execute_dap_command("dap_command")
"""

from .exceptions import (
    DapException,
    DapInitializationError,
    DapTypeError,
    DapLoggingError,
    DapTimeError,
    DapSystemError,
    DapCoreError
)

from .dap import (
    Dap,
    get_dap,
    init_dap,
    deinit_dap,
    dap_status
)

from .types import (
    DapType,
    DapTypeError,
    format_bytes
)

from .logging import (
    DapLogging,
    DapLogLevel,
    DapLoggingError,
    set_debug_logging,
    set_info_logging,
    set_error_logging
)

from .time import (
    DapTime,
    DapTimeError,
    now_dap,
    to_rfc822,
    format_duration
)

from .system import (
    DapSystem,
    DapSystemError,
    execute_dap_command,
    safe_execute_dap_command
)

__all__ = [
    # Exceptions
    'DapException',
    'DapInitializationError',
    'DapTypeError',
    'DapLoggingError',
    'DapTimeError',
    'DapSystemError',
    'DapCoreError',
    
    # Core coordination
    'Dap',
    'get_dap',
    'init_dap',
    'deinit_dap',
    'dap_status',
    
    # Type utilities
    'DapType',
    'format_bytes',
    
    # Logging
    'DapLogging',
    'DapLogLevel',
    'set_debug_logging',
    'set_info_logging',
    'set_error_logging',
    
    # Time utilities
    'DapTime',
    'now_dap',
    'to_rfc822',
    'format_duration',
    
    # System utilities
    'DapSystem',
    'execute_dap_command',
    'safe_execute_dap_command',
] 