"""
🚀 Cellframe Python SDK

Universal Python SDK for Cellframe blockchain platform.

## Execution Modes

The SDK supports two execution modes:

### Plugin Mode
Run as a plugin inside cellframe-node:
```python
import cellframe

# Auto-detect plugin mode
with cellframe.auto_create_node() as node:
    chain = node.chain.get_by_id("mainnet")

# Or explicitly create plugin node
with cellframe.create_plugin_node("my-plugin") as node:
    # Plugin-specific operations
    manifest = node.context.get_plugin_manifest()
```

### Library Mode  
Run as a standalone Python library:
```python
import cellframe

# Auto-detect library mode
with cellframe.auto_create_node() as node:
    balance = node.get_balance(wallet, "CELL")

# Or explicitly create library node
with cellframe.create_library_node("my-app") as node:
    # Library-specific operations
    config_dir = node.context.get_config_dir()
```

## Quick Start

```python
import cellframe

# Universal approach - auto-detects mode
with cellframe.CellframeNode() as node:
    # Works in both plugin and library modes
    chain = node.chain.get_by_id("mainnet")
    status = node.get_status()
```

## Legacy Compatibility

The SDK maintains 100% backward compatibility:
```python
# Legacy code continues to work
from cellframe.legacy import CellFrame, DAP

CellFrame.init(["Chain", "Network"])
# Modern equivalent: cellframe.CellframeNode()
```

## Simple Usage

For simple applications in library mode:
```python
import cellframe

# Simple library usage
with cellframe.create_library_node("my-app") as node:
    chain = node.chain.get_by_id("mainnet")
    status = node.get_status()
```
"""

# Core universal architecture
from .core import (
    # Context system
    AppContext, PluginContext, LibContext, ExecutionMode,
    ContextFactory, get_context, initialize_context, shutdown_context,
    
    # Core classes
    CellframeComponent, CellframeChain, CellframeNode,
    
    # Convenience functions
    create_node, create_plugin_node, create_library_node, auto_create_node,
    
    # Exceptions
    CellframeException, CellframeConfigurationError
)

# Types
from .types import (
    Address, TokenAmount, TransactionHash, BlockHash, ChainId,
    KeyType, HashType, NetworkId, ServiceId
)

# Import other modules with context awareness
import logging

# Setup module logger
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "2.0.0"
__author__ = "Cellframe Development Team"
__email__ = "support@cellframe.net"
__description__ = "Universal Python SDK for Cellframe blockchain platform"


# Auto-initialization helpers
def _auto_detect_and_warn():
    """Auto-detect execution mode and show appropriate message"""
    try:
        mode = ContextFactory.auto_detect_mode()
        
        if mode == ExecutionMode.PLUGIN:
            logger.info("🔌 Plugin mode detected - running inside cellframe-node")
        else:
            logger.info("📚 Library mode detected - running as Python library")
        
        return mode
    except Exception as e:
        logger.warning(f"Mode detection failed: {e}")
        return ExecutionMode.LIBRARY


# Convenience imports for common use cases
def init_plugin(app_name: str = "cellframe-plugin") -> CellframeNode:
    """
    Initialize for plugin mode
    
    Args:
        app_name: Plugin name
        
    Returns:
        Initialized node instance
    """
    logger.info(f"🔌 Initializing Cellframe plugin: {app_name}")
    return create_plugin_node(app_name)


def init_library(app_name: str = "cellframe-lib", 
                config_dir: str = None) -> CellframeNode:
    """
    Initialize for library mode
    
    Args:
        app_name: Application name
        config_dir: Custom configuration directory
        
    Returns:
        Initialized node instance
    """
    from pathlib import Path
    
    logger.info(f"📚 Initializing Cellframe library: {app_name}")
    config_path = Path(config_dir) if config_dir else None
    return create_library_node(app_name, config_path)


def init_auto(app_name: str = None) -> CellframeNode:
    """
    Auto-detect mode and initialize
    
    Args:
        app_name: Application/plugin name
        
    Returns:
        Initialized node instance
    """
    mode = _auto_detect_and_warn()
    
    if mode == ExecutionMode.PLUGIN:
        return init_plugin(app_name or "cellframe-plugin")
    else:
        return init_library(app_name or "cellframe-lib")


# Legacy compatibility functions
def init(modules: list = None) -> CellframeNode:
    """
    Legacy initialization function
    
    Provides backward compatibility with old CellFrame.init() API
    """
    import warnings
    warnings.warn(
        "cellframe.init() is deprecated. Use cellframe.CellframeNode() context manager instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    logger.info("🔄 Legacy initialization mode")
    return init_auto()


# Module-level convenience functions
def get_version() -> str:
    """Get SDK version"""
    return __version__


def get_mode() -> ExecutionMode:
    """Get current execution mode"""
    context = get_context()
    if context:
        return context.mode
    return ContextFactory.auto_detect_mode()


def is_plugin_mode() -> bool:
    """Check if running in plugin mode"""
    return get_mode() == ExecutionMode.PLUGIN


def is_library_mode() -> bool:
    """Check if running in library mode"""
    return get_mode() == ExecutionMode.LIBRARY


def get_current_context() -> AppContext:
    """Get current application context"""
    context = get_context()
    if not context:
        raise CellframeException(
            "No active context. Initialize with cellframe.CellframeNode() first."
        )
    return context


# Plugin detection and setup
def setup_plugin_api(node_api):
    """
    Setup plugin API reference
    
    This function is called by cellframe-node when loading the plugin
    to provide access to node API.
    
    Args:
        node_api: Node API reference
    """
    import sys
    sys.modules[__name__]._cellframe_node_api = node_api
    logger.info("🔌 Plugin API reference established")


# Quick examples for documentation
def _example_plugin():
    """Example: Plugin mode usage"""
    with create_plugin_node("my-plugin") as node:
        # Access plugin manifest
        manifest = node.context.get_plugin_manifest()
        
        # Use node API
        node_api = node.context.get_node_api()
        
        # Chain operations
        chain = node.chain.get_by_id("mainnet")


def _example_library():
    """Example: Library mode usage"""
    with create_library_node("my-app") as node:
        # Access local config
        config_dir = node.context.get_config_dir()
        
        # Chain operations
        chains = node.chain.load_all()


def _example_universal():
    """Example: Universal usage"""
    with auto_create_node() as node:
        # Works in both modes
        status = node.get_status()
        chain = node.chain.get_by_id("mainnet")


# Export everything needed
__all__ = [
    # Version info
    '__version__', '__author__', '__email__', '__description__',
    
    # Core classes (universal)
    'CellframeNode', 'CellframeChain', 'CellframeComponent',
    
    # Context system
    'AppContext', 'PluginContext', 'LibContext', 'ExecutionMode',
    'ContextFactory', 'get_context', 'initialize_context', 'shutdown_context',
    
    # Node creation functions
    'create_node', 'create_plugin_node', 'create_library_node', 'auto_create_node',
    
    # Initialization functions
    'init_plugin', 'init_library', 'init_auto', 'init',
    
    # Utility functions
    'get_version', 'get_mode', 'is_plugin_mode', 'is_library_mode',
    'get_current_context', 'setup_plugin_api',
    
    # Types
    'Address', 'TokenAmount', 'TransactionHash', 'BlockHash', 'ChainId',
    'KeyType', 'HashType', 'NetworkId', 'ServiceId',
    
    # Exceptions
    'CellframeException', 'CellframeConfigurationError'
]


# Import warnings for legacy usage
import warnings

# Show deprecation warning for direct module imports in legacy style
def __getattr__(name):
    """Handle legacy attribute access"""
    if name in ('Chain', 'Network', 'Services'):
        warnings.warn(
            f"Direct access to {name} is deprecated. "
            f"Use cellframe.CellframeNode().{name.lower()} instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Return appropriate component
        context = get_context()
        if context:
            node = CellframeNode(context=context)
            if name == 'Chain':
                return node.chain
        
        raise AttributeError(f"'{name}' requires active context. Use cellframe.CellframeNode() first.")
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Auto-detection on module import (non-intrusive)
try:
    _detected_mode = _auto_detect_and_warn()
except Exception:
    # Silent fallback if detection fails
    pass 