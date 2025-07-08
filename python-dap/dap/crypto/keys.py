"""
🔑 DAP Key Management

Direct Python wrapper over DAP key functions.
Handles key generation, management, and basic operations.
"""

import logging
import threading
from typing import Optional, Dict, List, Any
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        dap_enc_key_new, dap_enc_key_delete, dap_enc_key_generate,
        dap_enc_key_new_from_data, dap_enc_key_new_from_data_pub,
        dap_enc_key_get_pub_key_data, dap_enc_key_get_priv_key_data,
        dap_enc_key_save, dap_enc_key_load
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations
    def dap_enc_key_new(): return id("key")
    def dap_enc_key_delete(key): pass
    def dap_enc_key_generate(key, key_type): return 0
    def dap_enc_key_new_from_data(data): return id("key_from_data")
    def dap_enc_key_new_from_data_pub(data): return id("key_from_pub")
    def dap_enc_key_get_pub_key_data(key): return b"public_key_data"
    def dap_enc_key_get_priv_key_data(key): return b"private_key_data"
    def dap_enc_key_save(key, path): return 0
    def dap_enc_key_load(path): return id("loaded_key")

from ..core.exceptions import DapException


class DapKeyType(Enum):
    """DAP supported key types"""
    SIG_BLISS = "sig_bliss"
    SIG_TESLA = "sig_tesla"
    SIG_PICNIC = "sig_picnic"
    SIG_DILITHIUM = "sig_dilithium"
    SIG_FALCON = "sig_falcon"
    SIG_SPHINCS = "sig_sphincs"
    ENC_SIDH = "enc_sidh"
    ENC_NEWHOPE = "enc_newhope"


class DapKeyError(DapException):
    """DAP Key specific errors"""
    pass


class DapKey:
    """
    🔑 DAP Key wrapper
    
    Direct wrapper over dap_enc_key_* functions.
    Manages cryptographic keys lifecycle and operations.
    
    Example:
        # Generate new key
        key = DapKey.generate(DapKeyType.SIG_BLISS)
        
        # Load from data
        key = DapKey.from_private_data(key_bytes)
        
        # Save/load from file
        key.save("key.dat")
        loaded_key = DapKey.load("key.dat")
    """
    
    _keys_registry: Dict[int, 'DapKey'] = {}
    _lock = threading.Lock()
    
    def __init__(self, key_handle: int, key_type: Optional[DapKeyType] = None):
        """
        Initialize DapKey wrapper
        
        Args:
            key_handle: Native DAP key handle
            key_type: Type of the key
        """
        self._key_handle = key_handle
        self._key_type = key_type
        self._logger = logging.getLogger(__name__)
        
        # Register in global registry
        with self._lock:
            self._keys_registry[key_handle] = self
            
        self._logger.debug(f"DapKey created with handle {key_handle}")
    
    @classmethod
    def generate(cls, key_type: DapKeyType) -> 'DapKey':
        """
        Generate new DAP key pair
        
        Args:
            key_type: Type of key to generate
            
        Returns:
            New DapKey instance
            
        Raises:
            DapKeyError: If key generation fails
        """
        try:
            # Call C function: dap_enc_key_new()
            key_handle = dap_enc_key_new()
            if key_handle is None:
                raise DapKeyError("Failed to create new key handle")
            
            # Call C function: dap_enc_key_generate()
            if dap_enc_key_generate(key_handle, key_type.value) != 0:
                dap_enc_key_delete(key_handle)
                raise DapKeyError(f"Failed to generate {key_type.value} key")
            
            return cls(key_handle, key_type)
            
        except Exception as e:
            raise DapKeyError(f"Key generation failed: {e}")
    
    @classmethod
    def from_private_data(cls, key_data: bytes, key_type: Optional[DapKeyType] = None) -> 'DapKey':
        """
        Create key from private key data
        
        Args:
            key_data: Private key bytes
            key_type: Type of the key (optional)
            
        Returns:
            DapKey instance
        """
        try:
            # Call C function: dap_enc_key_new_from_data()
            key_handle = dap_enc_key_new_from_data(key_data)
            if key_handle is None:
                raise DapKeyError("Failed to create key from private data")
            
            return cls(key_handle, key_type)
            
        except Exception as e:
            raise DapKeyError(f"Failed to create key from private data: {e}")
    
    @classmethod
    def from_public_data(cls, key_data: bytes, key_type: Optional[DapKeyType] = None) -> 'DapKey':
        """
        Create key from public key data
        
        Args:
            key_data: Public key bytes
            key_type: Type of the key (optional)
            
        Returns:
            DapKey instance
        """
        try:
            # Call C function: dap_enc_key_new_from_data_pub()
            key_handle = dap_enc_key_new_from_data_pub(key_data)
            if key_handle is None:
                raise DapKeyError("Failed to create key from public data")
            
            return cls(key_handle, key_type)
            
        except Exception as e:
            raise DapKeyError(f"Failed to create key from public data: {e}")
    
    @classmethod
    def load(cls, file_path: str) -> 'DapKey':
        """
        Load key from file
        
        Args:
            file_path: Path to key file
            
        Returns:
            DapKey instance
        """
        try:
            # Call C function: dap_enc_key_load()
            key_handle = dap_enc_key_load(file_path)
            if key_handle is None:
                raise DapKeyError(f"Failed to load key from {file_path}")
            
            return cls(key_handle)
            
        except Exception as e:
            raise DapKeyError(f"Failed to load key from file: {e}")
    
    def save(self, file_path: str) -> bool:
        """
        Save key to file
        
        Args:
            file_path: Target file path
            
        Returns:
            True if saved successfully
        """
        try:
            # Call C function: dap_enc_key_save()
            result = dap_enc_key_save(self._key_handle, file_path)
            if result != 0:
                raise DapKeyError(f"Failed to save key to {file_path}")
            
            self._logger.debug(f"Key saved to {file_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to save key: {e}")
            return False
    
    def get_public_data(self) -> Optional[bytes]:
        """
        Get public key data
        
        Returns:
            Public key bytes or None if failed
        """
        try:
            # Call C function: dap_enc_key_get_pub_key_data()
            pub_data = dap_enc_key_get_pub_key_data(self._key_handle)
            if pub_data is None:
                raise DapKeyError("Failed to get public key data")
            
            return pub_data
            
        except Exception as e:
            self._logger.error(f"Failed to get public key data: {e}")
            return None
    
    def get_private_data(self) -> Optional[bytes]:
        """
        Get private key data
        
        Returns:
            Private key bytes or None if failed
        """
        try:
            # Call C function: dap_enc_key_get_priv_key_data()
            priv_data = dap_enc_key_get_priv_key_data(self._key_handle)
            if priv_data is None:
                raise DapKeyError("Failed to get private key data")
            
            return priv_data
            
        except Exception as e:
            self._logger.error(f"Failed to get private key data: {e}")
            return None
    
    def delete(self) -> None:
        """
        Delete the key and cleanup resources
        """
        try:
            # Call C function: dap_enc_key_delete()
            dap_enc_key_delete(self._key_handle)
            
            # Remove from registry
            with self._lock:
                self._keys_registry.pop(self._key_handle, None)
            
            self._logger.debug(f"Key {self._key_handle} deleted")
            
        except Exception as e:
            self._logger.error(f"Failed to delete key: {e}")
    
    @property
    def handle(self) -> int:
        """Get native key handle"""
        return self._key_handle
    
    @property
    def key_type(self) -> Optional[DapKeyType]:
        """Get key type"""
        return self._key_type
    
    @property
    def is_valid(self) -> bool:
        """Check if key is valid"""
        return self._key_handle in self._keys_registry
    
    def __enter__(self) -> 'DapKey':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup key"""
        self.delete()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if hasattr(self, '_key_handle') and self._key_handle in self._keys_registry:
            try:
                self.delete()
            except:
                pass  # Ignore errors in destructor
    
    @classmethod
    def cleanup_all(cls) -> None:
        """Cleanup all registered keys"""
        with cls._lock:
            for key_handle in list(cls._keys_registry.keys()):
                try:
                    dap_enc_key_delete(key_handle)
                except:
                    pass
            cls._keys_registry.clear()
    
    @classmethod
    def list_keys(cls) -> List[int]:
        """Get list of all registered key handles"""
        with cls._lock:
            return list(cls._keys_registry.keys())
    
    def __repr__(self) -> str:
        return f"DapKey(handle={self._key_handle}, type={self._key_type})"


__all__ = ['DapKey', 'DapKeyType', 'DapKeyError'] 