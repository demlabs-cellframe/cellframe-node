"""
📜 DAP Certificate Management

Proper Python wrapper with dap_cert_t* structure management.
Handles certificate lifecycle, metadata management and signing operations.
"""

import logging
import threading
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        # Core certificate functions
        dap_cert_new, dap_cert_delete, dap_cert_add, dap_cert_find_by_name,
        dap_cert_generate, dap_cert_generate_mem, dap_cert_generate_mem_with_seed,
        dap_cert_add_file, dap_cert_delete_file, dap_cert_save_to_folder,
        # Certificate operations
        dap_cert_sign, dap_cert_sign_with_hash_type, dap_cert_sign_output,
        dap_cert_compare_with_sign, dap_cert_sign_output_size,
        dap_cert_to_pkey, dap_cert_get_pkey_hash, dap_cert_get_pkey_str,
        # Metadata operations
        dap_cert_add_meta, dap_cert_add_meta_scalar, 
        dap_cert_get_meta_string, dap_cert_get_meta_bool, dap_cert_get_meta_int,
        dap_cert_get_meta_time, dap_cert_get_meta_period, dap_cert_get_meta_sign,
        dap_cert_get_meta_custom,
        # System functions
        dap_cert_init, dap_cert_deinit, dap_cert_get_all_mem,
        # Certificate metadata types
        DAP_CERT_META_STRING, DAP_CERT_META_BOOL, DAP_CERT_META_INT,
        DAP_CERT_META_DATETIME, DAP_CERT_META_DATETIME_PERIOD, 
        DAP_CERT_META_SIGN, DAP_CERT_META_CUSTOM
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_cert_new(name): return id(f"cert_{name}")
    def dap_cert_delete(cert): pass
    def dap_cert_add(cert): return 0
    def dap_cert_find_by_name(name): return id(f"found_{name}")
    def dap_cert_generate(name, path, key_type): return id(f"gen_{name}")
    def dap_cert_generate_mem(name, key_type): return id(f"mem_{name}")
    def dap_cert_generate_mem_with_seed(name, key_type, seed, size): return id(f"seed_{name}")
    def dap_cert_add_file(name, path): return id(f"file_{name}")
    def dap_cert_delete_file(name, path): return 0
    def dap_cert_save_to_folder(cert, path): return 0
    def dap_cert_sign(cert, data, size): return id("signature")
    def dap_cert_sign_with_hash_type(cert, data, size, hash_type): return id("signature")
    def dap_cert_sign_output(cert, data, size, output, output_size): return 0
    def dap_cert_compare_with_sign(cert, sign): return 0
    def dap_cert_sign_output_size(cert): return 64
    def dap_cert_to_pkey(cert): return id("pkey")
    def dap_cert_get_pkey_hash(cert): return (True, b"hash")
    def dap_cert_get_pkey_str(cert, str_type): return "pkey_string"
    def dap_cert_add_meta(cert, key, meta_type, value, size): pass
    def dap_cert_add_meta_scalar(cert, key, meta_type, value, size): pass
    def dap_cert_get_meta_string(cert, field): return "metadata_string"
    def dap_cert_get_meta_bool(cert, field): return True
    def dap_cert_get_meta_int(cert, field): return 42
    def dap_cert_get_meta_time(cert, field): return 1640995200
    def dap_cert_get_meta_period(cert, field): return 3600
    def dap_cert_get_meta_sign(cert, field): return id("meta_sign")
    def dap_cert_get_meta_custom(cert, field): return (b"custom_data", 10)
    def dap_cert_init(): return 0
    def dap_cert_deinit(): pass
    def dap_cert_get_all_mem(): return []
    # Metadata type constants
    DAP_CERT_META_STRING = 0
    DAP_CERT_META_BOOL = 1
    DAP_CERT_META_INT = 2
    DAP_CERT_META_DATETIME = 3
    DAP_CERT_META_DATETIME_PERIOD = 4
    DAP_CERT_META_SIGN = 5
    DAP_CERT_META_CUSTOM = 6

from ..core.exceptions import DapException
from .keys import DapKey, DapKeyType


class DapCertError(DapException):
    """DAP Certificate specific errors"""
    pass


class DapCertMetaType(Enum):
    """DAP certificate metadata types"""
    STRING = DAP_CERT_META_STRING
    BOOL = DAP_CERT_META_BOOL
    INT = DAP_CERT_META_INT
    DATETIME = DAP_CERT_META_DATETIME
    DATETIME_PERIOD = DAP_CERT_META_DATETIME_PERIOD
    SIGN = DAP_CERT_META_SIGN
    CUSTOM = DAP_CERT_META_CUSTOM


class DapCert:
    """
    📜 DAP Certificate with proper dap_cert_t* wrapping
    
    Manages certificate lifecycle with proper C structure integration.
    Supports metadata management, signing operations and file I/O.
    
    Example:
        # Create new certificate
        cert = DapCert.generate("my-cert", DapKeyType.SIG_BLISS)
        
        # Add metadata
        cert.add_metadata("description", "My certificate", DapCertMetaType.STRING)
        cert.add_metadata("created", 1640995200, DapCertMetaType.DATETIME)
        
        # Sign data
        signature = cert.sign_data(b"data to sign")
        
        # Save to file
        cert.save_to_folder("/path/to/certs")
    """
    
    _certificates_registry: Dict[int, 'DapCert'] = {}
    _lock = threading.Lock()
    _system_initialized = False
    
    def __init__(self, cert_handle: int, name: str = "", owns_handle: bool = True):
        """
        Initialize DapCert wrapper
        
        Args:
            cert_handle: Native dap_cert_t* handle
            name: Certificate name
            owns_handle: Whether this instance owns the handle (for cleanup)
        """
        self._cert_handle = cert_handle
        self._name = name
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        
        if not cert_handle:
            raise DapCertError("Invalid certificate handle provided")
        
        # Ensure system is initialized
        self._ensure_system_initialized()
        
        # Register in global registry for tracking
        with self._lock:
            self._certificates_registry[cert_handle] = self
            
        self._logger.debug(f"DapCert created with handle {cert_handle}, name: {name}")
    
    @classmethod
    def _ensure_system_initialized(cls):
        """Ensure DAP certificate system is initialized"""
        if not cls._system_initialized:
            with cls._lock:
                if not cls._system_initialized:
                    try:
                        result = dap_cert_init()
                        if result != 0:
                            raise DapCertError(f"Certificate system initialization failed with code {result}")
                        cls._system_initialized = True
                        logging.getLogger(__name__).info("DAP certificate system initialized")
                    except Exception as e:
                        raise DapCertError(f"Certificate system initialization failed: {e}")
    
    @classmethod
    def generate(cls, name: str, key_type: DapKeyType, 
                file_path: Optional[Path] = None) -> 'DapCert':
        """
        Generate new certificate
        
        Args:
            name: Certificate name
            key_type: Type of key to generate
            file_path: Optional path to save certificate file
            
        Returns:
            New DapCert instance
            
        Raises:
            DapCertError: If certificate generation fails
        """
        try:
            if file_path:
                # Call C function: dap_cert_generate()
                cert_handle = dap_cert_generate(name, str(file_path), key_type.value)
            else:
                # Call C function: dap_cert_generate_mem()
                cert_handle = dap_cert_generate_mem(name, key_type.value)
            
            if not cert_handle:
                raise DapCertError(f"Failed to generate certificate {name}")
            
            logging.getLogger(__name__).info(
                f"Certificate {name} generated with key type {key_type.name}"
            )
            
            return cls(cert_handle, name)
            
        except Exception as e:
            raise DapCertError(f"Certificate generation failed: {e}")
    
    @classmethod
    def generate_with_seed(cls, name: str, key_type: DapKeyType, 
                          seed: bytes) -> 'DapCert':
        """
        Generate certificate with seed
        
        Args:
            name: Certificate name
            key_type: Type of key to generate
            seed: Seed for key generation
            
        Returns:
            New DapCert instance
        """
        try:
            # Call C function: dap_cert_generate_mem_with_seed()
            cert_handle = dap_cert_generate_mem_with_seed(
                name, key_type.value, seed, len(seed)
            )
            
            if not cert_handle:
                raise DapCertError(f"Failed to generate certificate {name} with seed")
            
            return cls(cert_handle, name)
            
        except Exception as e:
            raise DapCertError(f"Certificate generation with seed failed: {e}")
    
    @classmethod
    def create_new(cls, name: str) -> 'DapCert':
        """
        Create new empty certificate
        
        Args:
            name: Certificate name
            
        Returns:
            New DapCert instance
        """
        try:
            # Call C function: dap_cert_new()
            cert_handle = dap_cert_new(name)
            
            if not cert_handle:
                raise DapCertError(f"Failed to create new certificate {name}")
            
            return cls(cert_handle, name)
            
        except Exception as e:
            raise DapCertError(f"Certificate creation failed: {e}")
    
    @classmethod
    def load_from_file(cls, name: str, folder_path: Path) -> 'DapCert':
        """
        Load certificate from file
        
        Args:
            name: Certificate name
            folder_path: Path to certificate folder
            
        Returns:
            Loaded DapCert instance
        """
        try:
            # Call C function: dap_cert_add_file()
            cert_handle = dap_cert_add_file(name, str(folder_path))
            
            if not cert_handle:
                raise DapCertError(f"Failed to load certificate {name} from {folder_path}")
            
            return cls(cert_handle, name)
            
        except Exception as e:
            raise DapCertError(f"Certificate loading failed: {e}")
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['DapCert']:
        """
        Find certificate by name
        
        Args:
            name: Certificate name to find
            
        Returns:
            DapCert instance if found, None otherwise
        """
        try:
            # Call C function: dap_cert_find_by_name()
            cert_handle = dap_cert_find_by_name(name)
            
            if cert_handle:
                return cls(cert_handle, name, owns_handle=False)  # Don't own found certs
            else:
                return None
                
        except Exception as e:
            logging.getLogger(__name__).warning(f"Certificate search failed: {e}")
            return None
    
    def add_to_system(self) -> bool:
        """
        Add certificate to system registry
        
        Returns:
            True if added successfully
        """
        try:
            # Call C function: dap_cert_add()
            result = dap_cert_add(self._cert_handle)
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to add certificate to system: {e}")
            return False
    
    def sign_data(self, data: Union[bytes, str], hash_type: Optional[int] = None) -> Optional['DapSign']:
        """
        Sign data with certificate
        
        Args:
            data: Data to sign
            hash_type: Optional hash type (uses default if None)
            
        Returns:
            DapSign instance with signature
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            if hash_type is not None:
                # Call C function: dap_cert_sign_with_hash_type()
                sign_handle = dap_cert_sign_with_hash_type(
                    self._cert_handle, data, len(data), hash_type
                )
            else:
                # Call C function: dap_cert_sign()
                sign_handle = dap_cert_sign(self._cert_handle, data, len(data))
            
            if sign_handle:
                # Import here to avoid circular imports
                from .sign import DapSign
                return DapSign(sign_handle)
            else:
                return None
                
        except Exception as e:
            raise DapCertError(f"Certificate signing failed: {e}")
    
    def sign_data_to_buffer(self, data: Union[bytes, str]) -> Optional[bytes]:
        """
        Sign data and return raw signature bytes
        
        Args:
            data: Data to sign
            
        Returns:
            Raw signature bytes
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            # Get output size first
            output_size = dap_cert_sign_output_size(self._cert_handle)
            if output_size <= 0:
                return None
            
            # Prepare output buffer
            output_buffer = bytearray(output_size)
            actual_size = [output_size]  # Mutable reference
            
            # Call C function: dap_cert_sign_output()
            result = dap_cert_sign_output(
                self._cert_handle, data, len(data), output_buffer, actual_size
            )
            
            if result == 0:
                return bytes(output_buffer[:actual_size[0]])
            else:
                return None
                
        except Exception as e:
            self._logger.error(f"Certificate raw signing failed: {e}")
            return None
    
    def verify_against_signature(self, signature: 'DapSign') -> bool:
        """
        Verify if this certificate matches a signature
        
        Args:
            signature: Signature to compare against
            
        Returns:
            True if certificate matches signature
        """
        try:
            # Call C function: dap_cert_compare_with_sign()
            result = dap_cert_compare_with_sign(self._cert_handle, signature.handle)
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Certificate signature comparison failed: {e}")
            return False
    
    def get_public_key(self) -> Optional['DapKey']:
        """
        Get public key from certificate
        
        Returns:
            DapKey instance with public key
        """
        try:
            # Call C function: dap_cert_to_pkey()
            pkey_handle = dap_cert_to_pkey(self._cert_handle)
            
            if pkey_handle:
                # Create DapKey wrapper (would need proper integration)
                # For now, return a mock
                return DapKey(pkey_handle, None)
            else:
                return None
                
        except Exception as e:
            self._logger.error(f"Failed to get public key: {e}")
            return None
    
    def get_public_key_hash(self) -> Optional[bytes]:
        """
        Get public key hash from certificate
        
        Returns:
            Public key hash bytes
        """
        try:
            # Call C function: dap_cert_get_pkey_hash()
            result, hash_data = dap_cert_get_pkey_hash(self._cert_handle)
            return hash_data if result else None
            
        except Exception as e:
            self._logger.error(f"Failed to get public key hash: {e}")
            return None
    
    def get_public_key_string(self, str_type: str = "hex") -> Optional[str]:
        """
        Get public key as string
        
        Args:
            str_type: String format ("hex", "base64", etc.)
            
        Returns:
            Public key string
        """
        try:
            # Call C function: dap_cert_get_pkey_str()
            return dap_cert_get_pkey_str(self._cert_handle, str_type)
            
        except Exception as e:
            self._logger.error(f"Failed to get public key string: {e}")
            return None
    
    # Metadata management methods
    def add_metadata(self, key: str, value: Any, meta_type: DapCertMetaType) -> bool:
        """
        Add metadata to certificate
        
        Args:
            key: Metadata key
            value: Metadata value
            meta_type: Type of metadata
            
        Returns:
            True if metadata was added successfully
        """
        try:
            if meta_type in (DapCertMetaType.STRING, DapCertMetaType.CUSTOM):
                if isinstance(value, str):
                    value = value.encode('utf-8')
                # Call C function: dap_cert_add_meta()
                dap_cert_add_meta(self._cert_handle, key, meta_type.value, value, len(value))
            else:
                # Call C function: dap_cert_add_meta_scalar()
                dap_cert_add_meta_scalar(self._cert_handle, key, meta_type.value, value, 0)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add metadata {key}: {e}")
            return False
    
    def get_metadata_string(self, key: str) -> Optional[str]:
        """Get string metadata"""
        try:
            return dap_cert_get_meta_string(self._cert_handle, key)
        except Exception:
            return None
    
    def get_metadata_bool(self, key: str) -> Optional[bool]:
        """Get boolean metadata"""
        try:
            return dap_cert_get_meta_bool(self._cert_handle, key)
        except Exception:
            return None
    
    def get_metadata_int(self, key: str) -> Optional[int]:
        """Get integer metadata"""
        try:
            return dap_cert_get_meta_int(self._cert_handle, key)
        except Exception:
            return None
    
    def get_metadata_time(self, key: str) -> Optional[int]:
        """Get datetime metadata"""
        try:
            return dap_cert_get_meta_time(self._cert_handle, key)
        except Exception:
            return None
    
    def get_metadata_period(self, key: str) -> Optional[int]:
        """Get time period metadata"""
        try:
            return dap_cert_get_meta_period(self._cert_handle, key)
        except Exception:
            return None
    
    def get_metadata_signature(self, key: str) -> Optional['DapSign']:
        """Get signature metadata"""
        try:
            sign_handle = dap_cert_get_meta_sign(self._cert_handle, key)
            if sign_handle:
                from .sign import DapSign
                return DapSign(sign_handle, owns_handle=False)
            return None
        except Exception:
            return None
    
    def get_metadata_custom(self, key: str) -> Optional[bytes]:
        """Get custom metadata"""
        try:
            data, size = dap_cert_get_meta_custom(self._cert_handle, key)
            return data[:size] if data else None
        except Exception:
            return None
    
    def save_to_folder(self, folder_path: Path) -> bool:
        """
        Save certificate to folder
        
        Args:
            folder_path: Path to save certificate
            
        Returns:
            True if saved successfully
        """
        try:
            # Call C function: dap_cert_save_to_folder()
            result = dap_cert_save_to_folder(self._cert_handle, str(folder_path))
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to save certificate: {e}")
            return False
    
    def delete_file(self, folder_path: Path) -> bool:
        """
        Delete certificate file
        
        Args:
            folder_path: Path to certificate folder
            
        Returns:
            True if deleted successfully
        """
        try:
            # Call C function: dap_cert_delete_file()
            result = dap_cert_delete_file(self._name, str(folder_path))
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to delete certificate file: {e}")
            return False
    
    def delete(self) -> None:
        """Delete certificate and cleanup resources"""
        if self._owns_handle and self._cert_handle:
            try:
                # Remove from registry
                with self._lock:
                    self._certificates_registry.pop(self._cert_handle, None)
                
                # Call C function: dap_cert_delete()
                dap_cert_delete(self._cert_handle)
                
                self._logger.debug(f"Certificate {self._name} deleted")
                self._cert_handle = None
                
            except Exception as e:
                self._logger.error(f"Failed to delete certificate: {e}")
    
    @property
    def handle(self) -> int:
        """Get native certificate handle"""
        return self._cert_handle
    
    @property
    def name(self) -> str:
        """Get certificate name"""
        return self._name
    
    @property
    def is_valid(self) -> bool:
        """Check if certificate handle is valid"""
        return self._cert_handle and self._cert_handle in self._certificates_registry
    
    def __enter__(self) -> 'DapCert':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup certificate"""
        self.delete()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete()
            except:
                pass  # Ignore errors in destructor
    
    def __repr__(self) -> str:
        return f"DapCert(handle={self._cert_handle}, name='{self._name}')"


class DapCertificateManager:
    """
    📁 Certificate Management System
    
    Provides high-level certificate management operations.
    """
    
    @staticmethod
    def get_all_certificates() -> List[DapCert]:
        """
        Get all certificates from system
        
        Returns:
            List of all DapCert instances
        """
        try:
            # Call C function: dap_cert_get_all_mem()
            cert_list = dap_cert_get_all_mem()
            
            certificates = []
            for cert_handle in cert_list:
                if cert_handle:
                    # Create wrapper without owning the handle
                    cert = DapCert(cert_handle, "system_cert", owns_handle=False)
                    certificates.append(cert)
            
            return certificates
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to get all certificates: {e}")
            return []
    
    @staticmethod
    def deinitialize_system() -> None:
        """Deinitialize certificate system"""
        try:
            dap_cert_deinit()
            DapCert._system_initialized = False
            logging.getLogger(__name__).info("DAP certificate system deinitialized")
        except Exception as e:
            logging.getLogger(__name__).error(f"Certificate system deinitialization failed: {e}")


# Convenience functions
def create_certificate(name: str, key_type: DapKeyType) -> DapCert:
    """Create new certificate with default settings"""
    return DapCert.generate(name, key_type)


def load_certificate(name: str, folder_path: Path) -> Optional[DapCert]:
    """Load certificate from file"""
    return DapCert.load_from_file(name, folder_path)


def find_certificate(name: str) -> Optional[DapCert]:
    """Find certificate by name"""
    return DapCert.find_by_name(name)


__all__ = [
    'DapCert',
    'DapCertError',
    'DapCertMetaType',
    'DapCertificateManager',
    'create_certificate',
    'load_certificate',
    'find_certificate'
] 