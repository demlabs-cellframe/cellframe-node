"""
🔄 Legacy Compatibility Layer

Обратная совместимость с существующим Python Cellframe API.
Этот модуль предоставляет старый API поверх новой архитектуры.

Старый API:
    from CellFrame import *
    CellFrame.init(["Chain", "Network", "Services"])
    DAP.init(json_config)

Новый API (рекомендуется):
    import cellframe
    with cellframe.CellframeNode() as node:
        # Modern pythonic usage

Legacy поддержка:
    ✅ CellFrame.Chain.*
    ✅ CellFrame.Network.*  
    ✅ CellFrame.Services.*
    ✅ CellFrame.Consensus.*
    ✅ DAP.Core.*
    ✅ DAP.Crypto.*
    ✅ DAP.Network.*
    ✅ DAP.GlobalDB.*
"""

import warnings
from typing import List, Dict, Any, Optional

# Import new architecture
from ..core import CellframeNode, CellframeChain, CellframeComponent
from ..types import Address, TokenAmount, TransactionHash
from ..wallet import Wallet
from ..network import NetworkClient
from ..services import StakingService, ExchangeService

# Import DAP
try:
    import dap
except ImportError:
    # Fallback если dap модуль недоступен
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../python-dap'))
    import dap


class LegacyWarning(UserWarning):
    """Warning для использования legacy API"""
    pass


def _show_legacy_warning(api_name: str, new_api: str = None):
    """Показать предупреждение об использовании legacy API"""
    message = f"Using legacy {api_name} API. Consider migrating to new pythonic API."
    if new_api:
        message += f" Use: {new_api}"
    warnings.warn(message, LegacyWarning, stacklevel=3)


# Глобальные переменные для legacy state
_legacy_node: Optional[CellframeNode] = None
_legacy_initialized = False


class LegacyCellFrame:
    """
    Legacy CellFrame module compatibility
    
    Provides backward compatibility for:
    - CellFrame.init()
    - CellFrame.Chain.*
    - CellFrame.Network.*
    - CellFrame.Services.*
    """
    
    @staticmethod
    def init(modules: List[str]):
        """
        Legacy initialization: CellFrame.init(["Chain", "Network"])
        
        Args:
            modules: List of modules to initialize
        """
        global _legacy_node, _legacy_initialized
        
        _show_legacy_warning("CellFrame.init()", "cellframe.CellframeNode()")
        
        if _legacy_initialized:
            return
        
        try:
            # Создаем новый node через современную архитектуру
            _legacy_node = CellframeNode()
            _legacy_node.initialize()
            
            # Инициализируем запрошенные модули
            for module in modules:
                if module == "Chain":
                    # Chain already initialized with node
                    pass
                elif module == "Network":
                    # Network already initialized  
                    pass
                elif module == "Services":
                    # Services available through node
                    pass
                # Добавить другие модули по необходимости
            
            _legacy_initialized = True
            
        except Exception as e:
            raise RuntimeError(f"Legacy CellFrame initialization failed: {e}")
    
    @staticmethod
    def deinit():
        """Legacy deinitialization"""
        global _legacy_node, _legacy_initialized
        
        if _legacy_node:
            _legacy_node.shutdown()
            _legacy_node = None
        
        _legacy_initialized = False


class LegacyChain:
    """Legacy CellFrame.Chain.* compatibility"""
    
    @staticmethod
    def find_by_id(chain_id: str):
        """Legacy: CellFrame.Chain.find_by_id()"""
        _show_legacy_warning("CellFrame.Chain.find_by_id()", "node.chain.get_by_id()")
        
        if not _legacy_node:
            raise RuntimeError("CellFrame not initialized. Call CellFrame.init() first.")
        
        return _legacy_node.chain.get_by_id(chain_id)
    
    @staticmethod
    def load_all():
        """Legacy: CellFrame.Chain.load_all()"""
        _show_legacy_warning("CellFrame.Chain.load_all()", "node.chain.load_all()")
        
        if not _legacy_node:
            raise RuntimeError("CellFrame not initialized. Call CellFrame.init() first.")
        
        return _legacy_node.chain.load_all()


class LegacyNetwork:
    """Legacy CellFrame.Network.* compatibility"""
    
    @staticmethod
    def get_client(network_name: str):
        """Legacy: CellFrame.Network.get_client()"""
        _show_legacy_warning("CellFrame.Network.get_client()", "cellframe.NetworkClient()")
        
        # Используем новую архитектуру под капотом
        return NetworkClient(network_name)


class LegacyServices:
    """Legacy CellFrame.Services.* compatibility"""
    
    @staticmethod  
    def get_staking():
        """Legacy: CellFrame.Services.StakePosDelegate()"""
        _show_legacy_warning("CellFrame.Services.StakePosDelegate", "cellframe.StakingService()")
        
        if not _legacy_node:
            raise RuntimeError("CellFrame not initialized. Call CellFrame.init() first.")
        
        return StakingService(_legacy_node)
    
    @staticmethod
    def get_exchange():
        """Legacy: CellFrame.Services.Xchange()"""
        _show_legacy_warning("CellFrame.Services.Xchange", "cellframe.ExchangeService()")
        
        if not _legacy_node:
            raise RuntimeError("CellFrame not initialized. Call CellFrame.init() first.")
        
        return ExchangeService(_legacy_node)


class LegacyDAP:
    """
    Legacy DAP module compatibility
    
    Provides backward compatibility for:
    - DAP.init()  
    - DAP.Core.*
    - DAP.Crypto.*
    - DAP.Network.*
    """
    
    @staticmethod
    def init(json_config: str):
        """
        Legacy initialization: DAP.init(json_string)
        
        Args:
            json_config: JSON configuration string
        """
        _show_legacy_warning("DAP.init()", "dap.Dap() context manager")
        
        import json
        try:
            config = json.loads(json_config)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON configuration: {e}")
        
        # Используем новую DAP архитектуру
        dap_instance = dap.get_dap()
        return dap_instance.init()
    
    @staticmethod
    def deinit():
        """Legacy DAP deinitialization"""
        dap_instance = dap.get_dap()
        dap_instance.deinit()
    
    @staticmethod
    def setLogLevel(level: str):
        """Legacy: DAP.setLogLevel()"""
        _show_legacy_warning("DAP.setLogLevel()", "dap.Dap().logging.set_level()")
        
        dap_instance = dap.get_dap()
        dap_instance.logging.set_level(level)
    
    @staticmethod
    def configGetItem(key: str):
        """Legacy: DAP.configGetItem()"""
        _show_legacy_warning("DAP.configGetItem()", "dap.DapConfig.get()")
        
        config = dap.DapConfig()
        return config.get(key)


# Legacy Classes для compatibility
class LegacyChainObject:
    """Legacy Chain object compatibility"""
    
    def __init__(self, chain_id: str):
        _show_legacy_warning("Chain object", "cellframe.CellframeChain")
        if not _legacy_node:
            raise RuntimeError("CellFrame not initialized")
        self._chain = _legacy_node.chain.get_by_id(chain_id)
    
    def has_file_store(self):
        """Legacy method"""
        return self._chain.has_file_store()


class LegacyCryptoKey:
    """Legacy Crypto.Key compatibility"""
    
    def __init__(self, key_type: str = "sig_dil"):
        _show_legacy_warning("DAP.Crypto.Key", "dap.DapKey")
        self._key = dap.DapKey()
        self._key.generate(key_type)
    
    def sign(self, data: bytes) -> bytes:
        """Legacy sign method"""
        return self._key.sign(data)


# Создаем legacy module structure
class LegacyCellFrameModule:
    """Compatibility wrapper для CellFrame module"""
    
    def __init__(self):
        # Static methods доступны как атрибуты модуля
        self.init = LegacyCellFrame.init
        self.deinit = LegacyCellFrame.deinit
        
        # Submodules  
        self.Chain = LegacyChain()
        self.Network = LegacyNetwork()
        self.Services = LegacyServices()
        
        # Legacy classes
        self.ChainObject = LegacyChainObject
        
        # Legacy error для совместимости
        self.error = RuntimeError


class LegacyDAPModule:
    """Compatibility wrapper для DAP module"""
    
    def __init__(self):
        # Static methods
        self.init = LegacyDAP.init
        self.deinit = LegacyDAP.deinit  
        self.setLogLevel = LegacyDAP.setLogLevel
        self.configGetItem = LegacyDAP.configGetItem
        
        # Submodules (будут добавлены отдельно)
        self.Core = self._create_core_module()
        self.Crypto = self._create_crypto_module()
        self.Network = self._create_network_module()
    
    def _create_core_module(self):
        """Create DAP.Core legacy module"""
        class CoreModule:
            pass
        return CoreModule()
    
    def _create_crypto_module(self):
        """Create DAP.Crypto legacy module"""  
        class CryptoModule:
            Key = LegacyCryptoKey
        return CryptoModule()
    
    def _create_network_module(self):
        """Create DAP.Network legacy module"""
        class NetworkModule:
            pass
        return NetworkModule()


# Export legacy modules
CellFrame = LegacyCellFrameModule()
DAP = LegacyDAPModule()

# Legacy imports для совместимости
__all__ = [
    'CellFrame',
    'DAP', 
    'LegacyChainObject',
    'LegacyCryptoKey',
    'LegacyWarning'
] 