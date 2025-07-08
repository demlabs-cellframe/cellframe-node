"""
🏗️ Universal Context System

Универсальная система контекстов для работы в двух режимах:
- Plugin Mode: как плагин внутри cellframe-node  
- Library Mode: как обычная Python библиотека

Архитектура:
    AppContext (base)
    ├── PluginContext (для плагинов ноды)
    └── LibContext (для библиотеки)
"""

import abc
import logging
import threading
from typing import Dict, Any, Optional, Type, Union, Callable
from pathlib import Path
from enum import Enum

# Import DAP for core functionality
try:
    import dap
except ImportError:
    dap = None


class ExecutionMode(Enum):
    """Режимы выполнения"""
    PLUGIN = "plugin"      # Плагин внутри cellframe-node
    LIBRARY = "library"    # Обычная Python библиотека


class AppContext(abc.ABC):
    """
    Базовый контекст приложения
    
    Обеспечивает универсальную архитектуру для работы
    как в составе плагина ноды, так и как библиотека Python.
    """
    
    def __init__(self, mode: ExecutionMode, app_name: str = "cellframe-app"):
        """
        Initialize application context
        
        Args:
            mode: Execution mode (plugin/library)
            app_name: Application name
        """
        self.mode = mode
        self.app_name = app_name
        self._initialized = False
        self._config: Dict[str, Any] = {}
        self._resources: Dict[str, Any] = {}
        self._lock = threading.RLock()
        
        # Setup logging
        self.logger = logging.getLogger(f"cellframe.{mode.value}")
        
    @property
    def is_plugin_mode(self) -> bool:
        """Check if running as plugin"""
        return self.mode == ExecutionMode.PLUGIN
    
    @property
    def is_library_mode(self) -> bool:
        """Check if running as library"""
        return self.mode == ExecutionMode.LIBRARY
    
    @abc.abstractmethod
    def initialize(self) -> bool:
        """
        Initialize context
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abc.abstractmethod
    def shutdown(self) -> bool:
        """
        Shutdown context
        
        Returns:
            True if shutdown successful
        """
        pass
    
    @abc.abstractmethod
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        pass
    
    @abc.abstractmethod
    def set_config_value(self, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            True if set successfully
        """
        pass
    
    @abc.abstractmethod
    def get_data_dir(self) -> Path:
        """Get data directory path"""
        pass
    
    @abc.abstractmethod
    def get_log_dir(self) -> Path:
        """Get log directory path"""
        pass
    
    def get_resource(self, name: str) -> Any:
        """Get shared resource"""
        with self._lock:
            return self._resources.get(name)
    
    def set_resource(self, name: str, resource: Any) -> bool:
        """Set shared resource"""
        with self._lock:
            self._resources[name] = resource
            return True
    
    def remove_resource(self, name: str) -> bool:
        """Remove shared resource"""
        with self._lock:
            if name in self._resources:
                del self._resources[name]
                return True
            return False
    
    def is_initialized(self) -> bool:
        """Check if context is initialized"""
        return self._initialized
    
    def __enter__(self):
        """Context manager entry"""
        if not self.initialize():
            raise RuntimeError(f"Failed to initialize {self.__class__.__name__}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()


class PluginContext(AppContext):
    """
    Plugin context для работы внутри cellframe-node
    
    Имеет доступ к:
    - Манифесту плагина
    - Node API
    - Shared node resources
    - Node configuration
    """
    
    def __init__(self, app_name: str = "cellframe-plugin"):
        """Initialize plugin context"""
        super().__init__(ExecutionMode.PLUGIN, app_name)
        self._node_api: Optional[Any] = None
        self._plugin_manifest: Optional[Dict[str, Any]] = None
        self._node_config_path: Optional[Path] = None
    
    def initialize(self) -> bool:
        """Initialize plugin context"""
        try:
            self.logger.info(f"Initializing plugin context: {self.app_name}")
            
            # Initialize DAP if available
            if dap:
                self._init_dap()
            
            # Load plugin manifest
            self._load_plugin_manifest()
            
            # Connect to node API
            self._connect_node_api()
            
            # Load node configuration
            self._load_node_config()
            
            self._initialized = True
            self.logger.info("Plugin context initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin context initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown plugin context"""
        try:
            self.logger.info("Shutting down plugin context")
            
            # Cleanup resources
            with self._lock:
                self._resources.clear()
            
            # Disconnect from node API
            self._disconnect_node_api()
            
            # Cleanup DAP
            if dap:
                self._cleanup_dap()
            
            self._initialized = False
            self.logger.info("Plugin context shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin context shutdown failed: {e}")
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get config from node configuration"""
        if self._node_api and hasattr(self._node_api, 'get_config'):
            return self._node_api.get_config(key, default)
        return self._config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """Set config in node configuration"""
        if self._node_api and hasattr(self._node_api, 'set_config'):
            return self._node_api.set_config(key, value)
        
        with self._lock:
            self._config[key] = value
            return True
    
    def get_data_dir(self) -> Path:
        """Get plugin data directory"""
        if self._node_config_path:
            return self._node_config_path.parent / 'plugins' / self.app_name
        return Path.home() / f'.cellframe/plugins/{self.app_name}'
    
    def get_log_dir(self) -> Path:
        """Get plugin log directory"""
        return self.get_data_dir() / 'logs'
    
    def get_plugin_manifest(self) -> Optional[Dict[str, Any]]:
        """Get plugin manifest"""
        return self._plugin_manifest
    
    def get_node_api(self) -> Optional[Any]:
        """Get node API reference"""
        return self._node_api
    
    def get_node_config_path(self) -> Optional[Path]:
        """Get node configuration path"""
        return self._node_config_path
    
    def _init_dap(self):
        """Initialize DAP for plugin mode"""
        dap_instance = dap.get_dap()
        if not dap_instance.is_initialized:
            dap_instance.init()
        self.set_resource('dap', dap_instance)
    
    def _cleanup_dap(self):
        """Cleanup DAP"""
        dap_instance = self.get_resource('dap')
        if dap_instance:
            dap_instance.deinit()
            self.remove_resource('dap')
    
    def _load_plugin_manifest(self):
        """Load plugin manifest from expected locations"""
        # Check standard plugin manifest locations
        manifest_paths = [
            Path(__file__).parent.parent / 'plugin.json',
            Path(__file__).parent.parent / 'manifest.json',
            Path.cwd() / 'plugin.json'
        ]
        
        for manifest_path in manifest_paths:
            if manifest_path.exists():
                try:
                    import json
                    with open(manifest_path, 'r') as f:
                        self._plugin_manifest = json.load(f)
                    self.logger.info(f"Loaded plugin manifest: {manifest_path}")
                    break
                except Exception as e:
                    self.logger.warning(f"Failed to load manifest {manifest_path}: {e}")
    
    def _connect_node_api(self):
        """Connect to node API"""
        # Try to get node API through various methods
        try:
            # Method 1: Through DAP
            dap_instance = self.get_resource('dap')
            if dap_instance and hasattr(dap_instance, 'get_node_api'):
                self._node_api = dap_instance.get_node_api()
            
            # Method 2: Through global node reference (if available)
            # This would be set by the node when loading the plugin
            import sys
            if hasattr(sys.modules[__name__], '_cellframe_node_api'):
                self._node_api = sys.modules[__name__]._cellframe_node_api
            
            if self._node_api:
                self.logger.info("Connected to node API")
            else:
                self.logger.warning("Node API not available")
                
        except Exception as e:
            self.logger.warning(f"Failed to connect to node API: {e}")
    
    def _disconnect_node_api(self):
        """Disconnect from node API"""
        self._node_api = None
    
    def _load_node_config(self):
        """Load node configuration"""
        try:
            # Try to get config path from node API
            if self._node_api and hasattr(self._node_api, 'get_config_path'):
                self._node_config_path = Path(self._node_api.get_config_path())
            else:
                # Fallback to standard locations
                config_paths = [
                    Path('/opt/cellframe-node/etc/cellframe-node.cfg'),
                    Path.home() / '.cellframe/cellframe-node.cfg',
                    Path('/etc/cellframe-node.cfg')
                ]
                
                for config_path in config_paths:
                    if config_path.exists():
                        self._node_config_path = config_path
                        break
            
            if self._node_config_path:
                self.logger.info(f"Node config path: {self._node_config_path}")
            else:
                self.logger.warning("Node config path not found")
                
        except Exception as e:
            self.logger.warning(f"Failed to load node config: {e}")


class LibContext(AppContext):
    """
    Library context для работы как обычная Python библиотека
    
    Имеет доступ к:
    - Application configuration
    - Local data directories
    - Standard Python logging
    - Standalone DAP instance
    """
    
    def __init__(self, app_name: str = "cellframe-lib", config_dir: Optional[Path] = None):
        """
        Initialize library context
        
        Args:
            app_name: Application name
            config_dir: Custom configuration directory
        """
        super().__init__(ExecutionMode.LIBRARY, app_name)
        self._config_dir = config_dir or Path.home() / f'.{app_name}'
        self._config_file = self._config_dir / 'config.json'
        self._dap_instance: Optional[Any] = None
    
    def initialize(self) -> bool:
        """Initialize library context"""
        try:
            self.logger.info(f"Initializing library context: {self.app_name}")
            
            # Create directories
            self._setup_directories()
            
            # Load configuration
            self._load_config()
            
            # Initialize DAP
            if dap:
                self._init_dap()
            
            # Setup logging
            self._setup_logging()
            
            self._initialized = True
            self.logger.info("Library context initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Library context initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown library context"""
        try:
            self.logger.info("Shutting down library context")
            
            # Save configuration
            self._save_config()
            
            # Cleanup resources
            with self._lock:
                self._resources.clear()
            
            # Cleanup DAP
            if self._dap_instance:
                self._dap_instance.deinit()
                self._dap_instance = None
            
            self._initialized = False
            self.logger.info("Library context shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Library context shutdown failed: {e}")
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get config from local configuration"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """Set config in local configuration"""
        with self._lock:
            keys = key.split('.')
            config = self._config
            
            # Navigate to parent
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            
            # Set value
            config[keys[-1]] = value
            return True
    
    def get_data_dir(self) -> Path:
        """Get application data directory"""
        return self._config_dir / 'data'
    
    def get_log_dir(self) -> Path:
        """Get application log directory"""
        return self._config_dir / 'logs'
    
    def get_config_dir(self) -> Path:
        """Get configuration directory"""
        return self._config_dir
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        return self._save_config()
    
    def _setup_directories(self):
        """Setup required directories"""
        directories = [
            self._config_dir,
            self.get_data_dir(),
            self.get_log_dir()
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Load configuration from file"""
        if self._config_file.exists():
            try:
                import json
                with open(self._config_file, 'r') as f:
                    self._config = json.load(f)
                self.logger.info(f"Loaded config: {self._config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                self._config = {}
        else:
            # Create default configuration
            self._config = {
                'app_name': self.app_name,
                'mode': self.mode.value,
                'logging': {
                    'level': 'INFO',
                    'file_enabled': True
                },
                'dap': {
                    'auto_init': True
                }
            }
    
    def _save_config(self) -> bool:
        """Save configuration to file"""
        try:
            import json
            with self._lock:
                with open(self._config_file, 'w') as f:
                    json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def _init_dap(self):
        """Initialize DAP for library mode"""
        try:
            self._dap_instance = dap.Dap()
            self._dap_instance.init()
            self.set_resource('dap', self._dap_instance)
            self.logger.info("DAP initialized for library mode")
        except Exception as e:
            self.logger.warning(f"Failed to initialize DAP: {e}")
    
    def _setup_logging(self):
        """Setup logging for library mode"""
        log_level = self.get_config_value('logging.level', 'INFO')
        file_enabled = self.get_config_value('logging.file_enabled', True)
        
        # Configure root logger
        logger = logging.getLogger('cellframe')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Console handler
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, log_level.upper()))
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if file_enabled:
            log_file = self.get_log_dir() / f'{self.app_name}.log'
            if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(getattr(logging, log_level.upper()))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)


# Context factory and global management
class ContextFactory:
    """Factory для создания контекстов"""
    
    @staticmethod
    def create_context(mode: Union[ExecutionMode, str], 
                      app_name: str = None,
                      **kwargs) -> AppContext:
        """
        Create appropriate context based on mode
        
        Args:
            mode: Execution mode
            app_name: Application name
            **kwargs: Additional arguments
            
        Returns:
            Appropriate context instance
        """
        if isinstance(mode, str):
            mode = ExecutionMode(mode)
        
        if mode == ExecutionMode.PLUGIN:
            return PluginContext(app_name or "cellframe-plugin")
        
        elif mode == ExecutionMode.LIBRARY:
            config_dir = kwargs.get('config_dir')
            return LibContext(app_name or "cellframe-lib", config_dir)
        
        else:
            raise ValueError(f"Unknown execution mode: {mode}")
    
    @staticmethod
    def auto_detect_mode() -> ExecutionMode:
        """
        Auto-detect execution mode
        
        Returns:
            Detected execution mode
        """
        import sys
        
        # Check if running as plugin (presence of node API)
        if hasattr(sys.modules.get(__name__, {}), '_cellframe_node_api'):
            return ExecutionMode.PLUGIN
        
        # Check for plugin manifest
        manifest_paths = [
            Path(__file__).parent.parent / 'plugin.json',
            Path.cwd() / 'plugin.json'
        ]
        
        for manifest_path in manifest_paths:
            if manifest_path.exists():
                return ExecutionMode.PLUGIN
        
        # Default to library mode
        return ExecutionMode.LIBRARY


# Global context management
_global_context: Optional[AppContext] = None
_context_lock = threading.RLock()


def get_context() -> Optional[AppContext]:
    """Get global context instance"""
    return _global_context


def set_context(context: AppContext) -> bool:
    """Set global context instance"""
    global _global_context
    with _context_lock:
        _global_context = context
        return True


def initialize_context(mode: Union[ExecutionMode, str] = None,
                      app_name: str = None,
                      **kwargs) -> AppContext:
    """
    Initialize global context
    
    Args:
        mode: Execution mode (auto-detect if None)
        app_name: Application name
        **kwargs: Additional arguments
        
    Returns:
        Initialized context
    """
    global _global_context
    
    with _context_lock:
        if _global_context and _global_context.is_initialized():
            return _global_context
        
        # Auto-detect mode if not specified
        if mode is None:
            mode = ContextFactory.auto_detect_mode()
        
        # Create context
        context = ContextFactory.create_context(mode, app_name, **kwargs)
        
        # Initialize
        if not context.initialize():
            raise RuntimeError(f"Failed to initialize context: {context}")
        
        _global_context = context
        return context


def shutdown_context() -> bool:
    """Shutdown global context"""
    global _global_context
    
    with _context_lock:
        if _global_context:
            result = _global_context.shutdown()
            _global_context = None
            return result
        return True


__all__ = [
    'ExecutionMode',
    'AppContext',
    'PluginContext', 
    'LibContext',
    'ContextFactory',
    'get_context',
    'set_context',
    'initialize_context',
    'shutdown_context'
] 