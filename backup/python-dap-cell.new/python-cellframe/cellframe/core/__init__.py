"""
🏗️ Cellframe Core Module

Универсальная архитектура для работы в двух режимах:
- Plugin mode: как плагин внутри cellframe-node
- Library mode: как обычная Python библиотека

Core classes адаптированы для работы с универсальными контекстами.
"""

import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

# Import context system
from .context import (
    AppContext, PluginContext, LibContext, ExecutionMode,
    ContextFactory, get_context, initialize_context, shutdown_context
)

# Import exceptions
from .exceptions import CellframeException, ConfigurationException

# Import chain module
from ..chain import (
    DapWallet, DapWalletType, DapWalletError, DapWalletManager,
    TX, TxError, TxType, TxStatus, TxInput, TxOutput,
    DapLedger, DapLedgerType, DapLedgerError, DapAccount, DapLedgerManager,
    create_wallet, load_wallet, get_all_wallets,
    get_tx_by_hash, broadcast_tx,
    create_ledger, get_ledger, get_account_balance
)


class CellframeComponent:
    """
    Базовый компонент Cellframe
    
    Универсальный базовый класс для всех компонентов,
    работающий через систему контекстов.
    """
    
    def __init__(self, name: str, context: Optional[AppContext] = None):
        """
        Initialize component
        
        Args:
            name: Component name
            context: Application context (auto-detect if None)
        """
        self.name = name
        self._context = context or get_context()
        
        if not self._context:
            raise CellframeException(
                f"No context available for component {name}. "
                "Initialize context first with initialize_context()"
            )
        
        self.logger = logging.getLogger(f"cellframe.{name}")
        self._initialized = False
        
    @property
    def context(self) -> AppContext:
        """Get component context"""
        return self._context
    
    @property
    def is_plugin_mode(self) -> bool:
        """Check if running in plugin mode"""
        return self._context.is_plugin_mode
    
    @property
    def is_library_mode(self) -> bool:
        """Check if running in library mode"""
        return self._context.is_library_mode
    
    def initialize(self) -> bool:
        """Initialize component"""
        if self._initialized:
            return True
        
        try:
            self.logger.info(f"Initializing component: {self.name}")
            self._initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown component"""
        if not self._initialized:
            return True
        
        try:
            self.logger.info(f"Shutting down component: {self.name}")
            self._initialized = False
            return True
        except Exception as e:
            self.logger.error(f"Component shutdown failed: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if component is initialized"""
        return self._initialized
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value through context"""
        return self._context.get_config_value(f"{self.name}.{key}", default)
    
    def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value through context"""
        return self._context.set_config_value(f"{self.name}.{key}", value)


class CellframeChain(CellframeComponent):
    """
    Cellframe Chain component
    
    Универсальный компонент для работы с блокчейн операциями
    в любом режиме выполнения. Интегрирует wallet, transaction и ledger операции.
    """
    
    def __init__(self, context: Optional[AppContext] = None):
        """Initialize chain component"""
        super().__init__("chain", context)
        self._chains: Dict[str, Any] = {}
        
        # Initialize managers
        self._wallet_manager = DapWalletManager()
        self._ledger_manager = DapLedgerManager()
    
    def initialize(self) -> bool:
        """Initialize chain component"""
        if not super().initialize():
            return False
        
        try:
            # Initialize DAP if available
            dap_instance = self.context.get_resource('dap')
            if dap_instance:
                self.logger.info("Using DAP for chain operations")
            
            # Load chains based on mode
            if self.is_plugin_mode:
                self._init_plugin_chains()
            else:
                self._init_library_chains()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Chain initialization failed: {e}")
            return False
    
    # Wallet operations
    def create_wallet(self, name: str, wallet_type: DapWalletType = DapWalletType.HD) -> DapWallet:
        """Create new wallet"""
        return create_wallet(name, wallet_type)
    
    def load_wallet(self, file_path: Union[str, Path]) -> DapWallet:
        """Load wallet from file"""
        return load_wallet(file_path)
    
    def get_all_wallets(self) -> List[DapWallet]:
        """Get all wallets"""
        return get_all_wallets()
    
    # Transaction operations
    def create_transaction(self, tx_type: TxType = TxType.TRANSFER) -> TX:
        """
        Create new transaction 
        DEPRECATED: Используйте Composer.create_tx() напрямую для новых проектов
        """
        # Это упрощенная реализация для обратной совместимости
        # В реальности нужно больше параметров для создания транзакции
        from ..chain.tx import TX
        
        # Создаем заглушку для обратной совместимости
        # В реальном коде нужно передать правильные параметры
        fake_handle = f"legacy_tx_{tx_type.value}"
        transaction = TX(fake_handle, owns_handle=True)
        transaction.type = tx_type
        transaction.token_ticker = "CELL"  # По умолчанию
        transaction.hash = f"legacy_hash_{tx_type.value}"
        
        return transaction
    
    def get_transaction_history(self, wallet: DapWallet = None) -> List[Dict[str, Any]]:
        """Get transaction history"""
        if wallet:
            return wallet.get_transaction_history()
        return []  # Заглушка
    
    # Ledger operations  
    def create_ledger(self, ledger_id: str, ledger_type: DapLedgerType = DapLedgerType.ACCOUNT) -> DapLedger:
        """Create new ledger"""
        return create_ledger(ledger_id, ledger_type)
    
    def get_ledger(self, ledger_id: str) -> Optional[DapLedger]:
        """Get ledger by ID"""
        return get_ledger(ledger_id)
    
    def get_account_balance(self, account_address: str, ledger_id: str = "mainnet") -> int:
        """Get account balance"""
        return get_account_balance(account_address, ledger_id)
    
    # Legacy methods
    def get_by_id(self, chain_id: str) -> Optional[Any]:
        """Get chain by ID"""
        if not self.is_initialized():
            raise CellframeException("Chain component not initialized")
        
        return self._chains.get(chain_id)
    
    def load_all(self) -> List[str]:
        """Load all available chains"""
        if not self.is_initialized():
            raise CellframeException("Chain component not initialized")
        
        # Implementation depends on mode
        if self.is_plugin_mode:
            return self._load_plugin_chains()
        else:
            return self._load_library_chains()
    
    def has_file_store(self, chain_id: str = None) -> bool:
        """Check if chain has file store"""
        chain = self.get_by_id(chain_id) if chain_id else None
        
        if self.is_plugin_mode:
            # Use node API for plugin mode
            node_api = self.context.get_node_api()
            if node_api and hasattr(node_api, 'chain_has_file_store'):
                return node_api.chain_has_file_store(chain_id)
        
        # Default implementation
        return chain is not None
    
    def _init_plugin_chains(self):
        """Initialize chains in plugin mode"""
        self.logger.info("Initializing chains in plugin mode")
        
        # Get chains from node API
        if isinstance(self.context, PluginContext):
            node_api = self.context.get_node_api()
            if node_api and hasattr(node_api, 'get_chains'):
                self._chains = node_api.get_chains()
    
    def _init_library_chains(self):
        """Initialize chains in library mode"""
        self.logger.info("Initializing chains in library mode")
        
        # Initialize with available network configurations
        network_configs = self.get_config('networks', {})
        for network_id, config in network_configs.items():
            self._chains[network_id] = config
    
    def _load_plugin_chains(self) -> List[str]:
        """Load chains in plugin mode"""
        if isinstance(self.context, PluginContext):
            node_api = self.context.get_node_api()
            if node_api and hasattr(node_api, 'load_chains'):
                return node_api.load_chains()
        
        return list(self._chains.keys())
    
    def _load_library_chains(self) -> List[str]:
        """Load chains in library mode"""
        # Load from configuration
        networks = self.get_config('networks', {})
        return list(networks.keys())
    
    @property
    def wallet_manager(self) -> DapWalletManager:
        """Get wallet manager"""
        return self._wallet_manager
    
    @property
    def ledger_manager(self) -> DapLedgerManager:
        """Get ledger manager"""
        return self._ledger_manager


class CellframeNode(CellframeComponent):
    """
    Cellframe Node component
    
    Основной компонент, координирующий все операции.
    Работает как координатор в library mode и как wrapper в plugin mode.
    
    Unified architecture with backward compatibility for both old and new APIs.
    """
    
    def __init__(self, mode: Union[ExecutionMode, str] = None,
                 app_name: str = None, context: Optional[AppContext] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize node component
        
        Args:
            mode: Execution mode (auto-detect if None)
            app_name: Application name
            context: Existing context (create new if None)
            config: Legacy configuration dict (for backward compatibility)
        """
        # Initialize context if not provided
        if context is None:
            context = initialize_context(mode, app_name)
        
        super().__init__("node", context)
        
        # Components
        self.chain = CellframeChain(context)
        
        # Component registry
        self._components: Dict[str, CellframeComponent] = {
            'chain': self.chain
        }
        
        # Legacy compatibility
        self._config = config or {}
        self._started = False
        self._chains: Dict[str, Any] = {}
    
    def initialize(self) -> bool:
        """Initialize node and all components"""
        if not super().initialize():
            return False
        
        try:
            self.logger.info(f"Initializing Cellframe Node in {self.context.mode.value} mode")
            
            # Initialize all components
            for name, component in self._components.items():
                if not component.initialize():
                    raise CellframeException(f"Failed to initialize component: {name}")
            
            self.logger.info("Cellframe Node initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Node initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown node and all components"""
        try:
            self.logger.info("Shutting down Cellframe Node")
            
            # Shutdown all components in reverse order
            for name, component in reversed(list(self._components.items())):
                if not component.shutdown():
                    self.logger.warning(f"Failed to shutdown component: {name}")
            
            # Shutdown context if we're managing it
            shutdown_context()
            
            super().shutdown()
            self.logger.info("Cellframe Node shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Node shutdown failed: {e}")
            return False
    
    # Legacy compatibility methods
    def start(self) -> bool:
        """Start the node (legacy API - maps to initialize)"""
        if self._started:
            self.logger.warning("Node already started")
            return True
            
        try:
            success = self.initialize()
            if success:
                self._started = True
                self.logger.info("Node started successfully")
            return success
        except Exception as e:
            raise CellframeException(f"Failed to start node: {e}")
    
    def stop(self) -> bool:
        """Stop the node (legacy API - maps to shutdown)"""
        if not self._started:
            return True
            
        try:
            success = self.shutdown()
            if success:
                self._started = False
                self.logger.info("Node stopped successfully")
            return success
        except Exception as e:
            self.logger.error(f"Failed to stop node: {e}")
            return False
    
    def create_chain(self, chain_id: str) -> Any:
        """Create and register new chain (legacy API)"""
        if chain_id in self._chains:
            raise CellframeException(f"Chain {chain_id} already exists")
        
        # Create chain through chain component
        chain_obj = self.chain.get_by_id(chain_id)
        if not chain_obj:
            # Create new chain
            chain_obj = {"id": chain_id, "initialized": True}
            self._chains[chain_id] = chain_obj
        
        self.logger.info(f"Chain {chain_id} created and registered")
        return chain_obj
    
    def get_chain(self, chain_id: str) -> Optional[Any]:
        """Get existing chain (legacy API)"""
        return self._chains.get(chain_id) or self.chain.get_by_id(chain_id)
    
    def get_node_stats(self) -> Dict[str, Any]:
        """Get node statistics (legacy API)"""
        base_status = self.get_status()
        
        # Add legacy-style stats
        return {
            'node_version': "2.0.0",
            'network': self._config.get('network', 'unknown'),
            'started': self._started,
            'chains_count': len(self._chains),
            'chains': list(self._chains.keys()),
            'state': 'active' if self.is_initialized() else 'stopped',
            'component_name': self.name,
            'data_dir': self._config.get('data_dir', 'unknown'),
            'log_level': self._config.get('log_level', 'INFO'),
            **base_status
        }
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get node configuration (legacy API)"""
        return self._config
    
    @property
    def is_started(self) -> bool:
        """Check if node is started (legacy API)"""
        return self._started
    
    @classmethod
    def create(cls, network: str = "testnet", **kwargs) -> 'CellframeNode':
        """Create node with default configuration (legacy API)"""
        config = {
            'network': network,
            'data_dir': str(Path.home() / '.cellframe'),
            'log_level': "INFO",
            'max_connections': 50,
            'enable_mining': False,
            'plugin_mode': False,
            **kwargs
        }
        
        # Auto-detect mode
        mode = ContextFactory.auto_detect_mode()
        return cls(mode=mode, config=config)
    
    # Context manager support
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
    
    def add_component(self, name: str, component: CellframeComponent) -> bool:
        """Add custom component"""
        if name in self._components:
            self.logger.warning(f"Component {name} already exists")
            return False
        
        self._components[name] = component
        
        # Initialize if node is already initialized
        if self.is_initialized():
            return component.initialize()
        
        return True
    
    def get_component(self, name: str) -> Optional[CellframeComponent]:
        """Get component by name"""
        return self._components.get(name)
    
    def remove_component(self, name: str) -> bool:
        """Remove component"""
        if name not in self._components:
            return False
        
        # Shutdown component first
        component = self._components[name]
        component.shutdown()
        
        del self._components[name]
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get node status"""
        return {
            'mode': self.context.mode.value,
            'app_name': self.context.app_name,
            'initialized': self.is_initialized(),
            'components': {
                name: component.is_initialized()
                for name, component in self._components.items()
            },
            'context_type': type(self.context).__name__
        }
    
    @classmethod
    def create_plugin(cls, app_name: str = "cellframe-plugin") -> 'CellframeNode':
        """Create node instance for plugin mode"""
        context = PluginContext(app_name)
        return cls(context=context)
    
    @classmethod
    def create_library(cls, app_name: str = "cellframe-lib", 
                      config_dir: Optional[Path] = None) -> 'CellframeNode':
        """Create node instance for library mode"""
        context = LibContext(app_name, config_dir)
        return cls(context=context)


# Convenience functions for quick initialization
def create_node(mode: Union[ExecutionMode, str] = None,
                app_name: str = None,
                **kwargs) -> CellframeNode:
    """
    Create and initialize Cellframe node
    
    Args:
        mode: Execution mode (auto-detect if None)
        app_name: Application name
        **kwargs: Additional arguments
        
    Returns:
        Initialized CellframeNode instance
    """
    node = CellframeNode(mode, app_name, **kwargs)
    if not node.initialize():
        raise CellframeException("Failed to initialize Cellframe node")
    return node


def create_plugin_node(app_name: str = "cellframe-plugin") -> CellframeNode:
    """Create node for plugin mode"""
    node = CellframeNode.create_plugin(app_name)
    if not node.initialize():
        raise CellframeException("Failed to initialize plugin node")
    return node


def create_library_node(app_name: str = "cellframe-lib",
                       config_dir: Optional[Path] = None) -> CellframeNode:
    """Create node for library mode"""
    node = CellframeNode.create_library(app_name, config_dir)
    if not node.initialize():
        raise CellframeException("Failed to initialize library node")
    return node


# Auto-detection convenience function
def auto_create_node(app_name: str = None) -> CellframeNode:
    """Auto-detect mode and create appropriate node"""
    mode = ContextFactory.auto_detect_mode()
    
    if mode == ExecutionMode.PLUGIN:
        return create_plugin_node(app_name or "cellframe-plugin")
    else:
        return create_library_node(app_name or "cellframe-lib")


__all__ = [
    # Context system
    'AppContext', 'PluginContext', 'LibContext', 'ExecutionMode',
    'ContextFactory', 'get_context', 'initialize_context', 'shutdown_context',
    
    # Core classes
    'CellframeComponent', 'CellframeChain', 'CellframeNode',
    
    # Convenience functions
    'create_node', 'create_plugin_node', 'create_library_node', 'auto_create_node',
    
    # Exceptions
    'CellframeException', 'ConfigurationException',
    
    # Chain module - Wallet
    'DapWallet', 'DapWalletType', 'DapWalletError', 'DapWalletManager',
    'create_wallet', 'load_wallet', 'get_all_wallets',
    
    # Chain module - Transaction
    'TX', 'TxType', 'TxStatus', 'TxError',
    'TxInput', 'TxOutput',
    'get_tx_by_hash', 'broadcast_tx',
    
    # Chain module - Ledger
    'DapLedger', 'DapLedgerType', 'DapLedgerError', 'DapAccount', 'DapLedgerManager',
    'create_ledger', 'get_ledger', 'get_account_balance'
] 