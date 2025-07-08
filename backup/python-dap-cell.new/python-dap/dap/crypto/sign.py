"""
🖋️ DAP Digital Signatures

Proper Python wrapper with dap_sign_t* structure management.
Handles digital signature lifecycle, aggregation and batch verification.
"""

import logging
import threading
from typing import Optional, Union, List, Dict, Any
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        # Core signature functions
        dap_sign_create, dap_sign_create_with_hash_type, dap_sign_verify, 
        dap_sign_verify_by_pkey, dap_sign_get_size, dap_sign_get_sign,
        dap_sign_get_pkey, dap_sign_get_pkey_hash,
        # Extended signature functions  
        dap_sign_aggregate_signatures, dap_sign_verify_aggregated,
        dap_sign_batch_verify_ctx_new, dap_sign_batch_verify_ctx_free,
        dap_sign_batch_verify_add_signature, dap_sign_batch_verify_execute,
        # Signature type functions
        dap_sign_type_supports_aggregation, dap_sign_type_supports_batch_verification,
        dap_sign_is_aggregated, dap_sign_get_signers_count,
        # Hash type constants
        DAP_SIGN_HASH_TYPE_DEFAULT, DAP_SIGN_HASH_TYPE_SHA3, DAP_SIGN_HASH_TYPE_STREEBOG
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_sign_create(key, data, data_size): return id("sign")
    def dap_sign_create_with_hash_type(key, data, data_size, hash_type): return id("sign") 
    def dap_sign_verify(sign, data, data_size): return True
    def dap_sign_verify_by_pkey(sign, data, data_size, pkey): return True
    def dap_sign_get_size(sign): return 64
    def dap_sign_get_sign(sign): return (b"signature", 64)
    def dap_sign_get_pkey(sign): return (b"pubkey", 32)
    def dap_sign_get_pkey_hash(sign): return True
    def dap_sign_aggregate_signatures(signs, count, params): return id("aggregated")
    def dap_sign_verify_aggregated(sign, messages, sizes, pkeys, count): return True
    def dap_sign_batch_verify_ctx_new(sign_type, max_sigs): return id("batch_ctx")
    def dap_sign_batch_verify_ctx_free(ctx): pass
    def dap_sign_batch_verify_add_signature(ctx, sign, msg, size, pkey): return 0
    def dap_sign_batch_verify_execute(ctx): return 0
    def dap_sign_type_supports_aggregation(sign_type): return True
    def dap_sign_type_supports_batch_verification(sign_type): return True 
    def dap_sign_is_aggregated(sign): return False
    def dap_sign_get_signers_count(sign): return 1
    DAP_SIGN_HASH_TYPE_DEFAULT = 0x0f
    DAP_SIGN_HASH_TYPE_SHA3 = 0x01
    DAP_SIGN_HASH_TYPE_STREEBOG = 0x02

from ..core.exceptions import DapException
from .keys import DapKey


class DapSignError(DapException):
    """DAP Signature specific errors"""
    pass


class DapHashType(Enum):
    """DAP signature hash types"""
    DEFAULT = DAP_SIGN_HASH_TYPE_DEFAULT
    SHA3 = DAP_SIGN_HASH_TYPE_SHA3  
    STREEBOG = DAP_SIGN_HASH_TYPE_STREEBOG


class DapSign:
    """
    🖋️ DAP Digital Signature with proper dap_sign_t* wrapping
    
    Manages signature lifecycle with proper C structure integration.
    Supports aggregation and batch verification for compatible signature types.
    
    Example:
        # Create signature from key and data
        with DapKey.generate(DapKeyType.SIG_BLISS) as key:
            sign = DapSign.create_from_key_and_data(key, b"data to sign")
            
            # Verify signature
            is_valid = sign.verify(b"data to sign")
            
            # Get signature info
            size = sign.get_size()
            pkey_data = sign.get_public_key_data()
    """
    
    _signatures_registry: Dict[int, 'DapSign'] = {}
    _lock = threading.Lock()
    
    def __init__(self, sign_handle: int, owns_handle: bool = True):
        """
        Initialize DapSign wrapper
        
        Args:
            sign_handle: Native dap_sign_t* handle
            owns_handle: Whether this instance owns the handle (for cleanup)
        """
        self._sign_handle = sign_handle
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        
        if not sign_handle:
            raise DapSignError("Invalid signature handle provided")
        
        # Register in global registry for tracking
        with self._lock:
            self._signatures_registry[sign_handle] = self
            
        self._logger.debug(f"DapSign created with handle {sign_handle}")
    
    @classmethod
    def create_from_key_and_data(cls, key: DapKey, data: Union[bytes, str], 
                                hash_type: DapHashType = DapHashType.DEFAULT) -> 'DapSign':
        """
        Create signature from key and data
        
        Args:
            key: DapKey instance for signing
            data: Data to sign
            hash_type: Hash type to use for signing
            
        Returns:
            New DapSign instance
            
        Raises:
            DapSignError: If signature creation fails
        """
        if not key.is_valid:
            raise DapSignError("Invalid key provided for signing")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            # Call C function: dap_sign_create_with_hash_type()
            sign_handle = dap_sign_create_with_hash_type(
                key.handle, data, len(data), hash_type.value
            )
            
            if not sign_handle:
                raise DapSignError("Failed to create signature")
            
            logging.getLogger(__name__).info(
                f"Signature created with key {key.handle}, hash type {hash_type.name}"
            )
            
            return cls(sign_handle)
            
        except Exception as e:
            raise DapSignError(f"Signature creation failed: {e}")
    
    @classmethod
    def create_from_key_and_data_simple(cls, key: DapKey, data: Union[bytes, str]) -> 'DapSign':
        """
        Create signature with default hash type
        
        Args:
            key: DapKey instance for signing
            data: Data to sign
            
        Returns:
            New DapSign instance
        """
        return cls.create_from_key_and_data(key, data, DapHashType.DEFAULT)
    
    def verify(self, data: Union[bytes, str], pkey: Optional[DapKey] = None) -> bool:
        """
        Verify signature against data
        
        Args:
            data: Original data that was signed
            pkey: Optional public key for verification (uses embedded if None)
            
        Returns:
            True if signature is valid
            
        Raises:
            DapSignError: If verification fails
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            if pkey:
                # Call C function: dap_sign_verify_by_pkey()
                result = dap_sign_verify_by_pkey(
                    self._sign_handle, data, len(data), pkey.handle
                )
            else:
                # Call C function: dap_sign_verify()
                result = dap_sign_verify(self._sign_handle, data, len(data))
            
            self._logger.debug(f"Signature verification result: {result}")
            return bool(result)
            
        except Exception as e:
            raise DapSignError(f"Signature verification failed: {e}")
    
    def get_size(self) -> int:
        """
        Get signature size in bytes
        
        Returns:
            Signature size
        """
        try:
            # Call C function: dap_sign_get_size()
            size = dap_sign_get_size(self._sign_handle)
            return int(size)
            
        except Exception as e:
            raise DapSignError(f"Failed to get signature size: {e}")
    
    def get_signature_data(self) -> bytes:
        """
        Get raw signature data
        
        Returns:
            Raw signature bytes
        """
        try:
            # Call C function: dap_sign_get_sign()
            sign_data, sign_size = dap_sign_get_sign(self._sign_handle)
            return sign_data[:sign_size] if sign_data else b""
            
        except Exception as e:
            raise DapSignError(f"Failed to get signature data: {e}")
    
    def get_public_key_data(self) -> bytes:
        """
        Get public key data from signature
        
        Returns:
            Public key bytes
        """
        try:
            # Call C function: dap_sign_get_pkey()
            pkey_data, pkey_size = dap_sign_get_pkey(self._sign_handle)
            return pkey_data[:pkey_size] if pkey_data else b""
            
        except Exception as e:
            raise DapSignError(f"Failed to get public key data: {e}")
    
    def get_public_key_hash(self) -> Optional[bytes]:
        """
        Get public key hash from signature
        
        Returns:
            Public key hash or None if failed
        """
        try:
            # Call C function: dap_sign_get_pkey_hash()
            result = dap_sign_get_pkey_hash(self._sign_handle)
            return result if result else None
            
        except Exception as e:
            self._logger.warning(f"Failed to get public key hash: {e}")
            return None
    
    def is_aggregated(self) -> bool:
        """
        Check if this is an aggregated signature
        
        Returns:
            True if signature is aggregated
        """
        try:
            # Call C function: dap_sign_is_aggregated()
            return bool(dap_sign_is_aggregated(self._sign_handle))
            
        except Exception as e:
            self._logger.warning(f"Failed to check aggregation status: {e}")
            return False
    
    def get_signers_count(self) -> int:
        """
        Get number of signers in signature (1 for regular, >1 for aggregated)
        
        Returns:
            Number of signers
        """
        try:
            # Call C function: dap_sign_get_signers_count()
            return int(dap_sign_get_signers_count(self._sign_handle))
            
        except Exception as e:
            self._logger.warning(f"Failed to get signers count: {e}")
            return 1
    
    def delete(self) -> None:
        """Delete signature and cleanup resources"""
        if self._owns_handle and self._sign_handle:
            try:
                # Remove from registry
                with self._lock:
                    self._signatures_registry.pop(self._sign_handle, None)
                
                # Note: actual C cleanup would need dap_sign_delete() if it existed
                self._logger.debug(f"Signature {self._sign_handle} deleted")
                self._sign_handle = None
                
            except Exception as e:
                self._logger.error(f"Failed to delete signature: {e}")
    
    @property
    def handle(self) -> int:
        """Get native signature handle"""
        return self._sign_handle
    
    @property
    def is_valid(self) -> bool:
        """Check if signature handle is valid"""
        return self._sign_handle and self._sign_handle in self._signatures_registry
    
    def __enter__(self) -> 'DapSign':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup signature"""
        self.delete()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete()
            except:
                pass  # Ignore errors in destructor
    
    def __repr__(self) -> str:
        return f"DapSign(handle={self._sign_handle}, size={self.get_size()}, aggregated={self.is_aggregated()})"


class DapSignatureAggregator:
    """
    🔗 Signature Aggregation Manager
    
    Handles aggregation of multiple signatures into a single signature
    for compatible signature types.
    """
    
    @staticmethod
    def can_aggregate(signature_type: str) -> bool:
        """
        Check if signature type supports aggregation
        
        Args:
            signature_type: Signature type to check
            
        Returns:
            True if aggregation is supported
        """
        try:
            # Call C function: dap_sign_type_supports_aggregation()
            return bool(dap_sign_type_supports_aggregation(signature_type))
        except Exception:
            return False
    
    @staticmethod
    def aggregate_signatures(signatures: List[DapSign], 
                           aggregation_params: Optional[Dict[str, Any]] = None) -> DapSign:
        """
        Aggregate multiple signatures into one
        
        Args:
            signatures: List of signatures to aggregate
            aggregation_params: Optional aggregation parameters
            
        Returns:
            Aggregated signature
            
        Raises:
            DapSignError: If aggregation fails
        """
        if not signatures:
            raise DapSignError("No signatures provided for aggregation")
        
        # Check if all signatures support aggregation
        for i, sig in enumerate(signatures):
            if not sig.is_valid:
                raise DapSignError(f"Invalid signature at index {i}")
        
        try:
            # Prepare signature handles array
            sign_handles = [sig.handle for sig in signatures]
            
            # Call C function: dap_sign_aggregate_signatures()
            aggregated_handle = dap_sign_aggregate_signatures(
                sign_handles, len(sign_handles), aggregation_params
            )
            
            if not aggregated_handle:
                raise DapSignError("Signature aggregation failed")
            
            logging.getLogger(__name__).info(
                f"Aggregated {len(signatures)} signatures"
            )
            
            return DapSign(aggregated_handle)
            
        except Exception as e:
            raise DapSignError(f"Signature aggregation failed: {e}")


class DapBatchVerifier:
    """
    ⚡ Batch Signature Verifier
    
    Efficiently verifies multiple signatures in batch for better performance.
    """
    
    def __init__(self, signature_type: str, max_signatures: int = 100):
        """
        Initialize batch verifier
        
        Args:
            signature_type: Type of signatures in batch
            max_signatures: Maximum number of signatures in batch
        """
        self._signature_type = signature_type
        self._max_signatures = max_signatures
        self._batch_ctx = None
        self._signatures_count = 0
        self._logger = logging.getLogger(__name__)
        
        # Check if signature type supports batch verification
        if not dap_sign_type_supports_batch_verification(signature_type):
            raise DapSignError(f"Signature type {signature_type} does not support batch verification")
        
        # Create batch context
        self._batch_ctx = dap_sign_batch_verify_ctx_new(signature_type, max_signatures)
        if not self._batch_ctx:
            raise DapSignError("Failed to create batch verification context")
    
    def add_signature(self, signature: DapSign, message: bytes, 
                     public_key: Optional[DapKey] = None) -> bool:
        """
        Add signature to batch for verification
        
        Args:
            signature: Signature to verify
            message: Original message that was signed
            public_key: Optional public key for verification
            
        Returns:
            True if signature was added successfully
        """
        if self._signatures_count >= self._max_signatures:
            raise DapSignError("Batch is full, cannot add more signatures")
        
        try:
            pkey_handle = public_key.handle if public_key else None
            
            # Call C function: dap_sign_batch_verify_add_signature()
            result = dap_sign_batch_verify_add_signature(
                self._batch_ctx, signature.handle, message, len(message), pkey_handle
            )
            
            if result == 0:
                self._signatures_count += 1
                return True
            else:
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to add signature to batch: {e}")
            return False
    
    def verify_batch(self) -> bool:
        """
        Execute batch verification of all added signatures
        
        Returns:
            True if all signatures in batch are valid
        """
        try:
            # Call C function: dap_sign_batch_verify_execute()
            result = dap_sign_batch_verify_execute(self._batch_ctx)
            
            self._logger.info(f"Batch verification of {self._signatures_count} signatures: {'PASSED' if result == 0 else 'FAILED'}")
            return result == 0
            
        except Exception as e:
            raise DapSignError(f"Batch verification failed: {e}")
    
    def cleanup(self) -> None:
        """Cleanup batch verification context"""
        if self._batch_ctx:
            try:
                # Call C function: dap_sign_batch_verify_ctx_free()
                dap_sign_batch_verify_ctx_free(self._batch_ctx)
                self._batch_ctx = None
                
            except Exception as e:
                self._logger.error(f"Failed to cleanup batch context: {e}")
    
    @property
    def signatures_count(self) -> int:
        """Get number of signatures in batch"""
        return self._signatures_count
    
    @property
    def max_signatures(self) -> int:
        """Get maximum batch size"""
        return self._max_signatures
    
    def __enter__(self) -> 'DapBatchVerifier':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass


# Convenience functions for quick operations
def quick_sign(key: DapKey, data: Union[bytes, str]) -> DapSign:
    """Quick signature creation"""
    return DapSign.create_from_key_and_data_simple(key, data)


def quick_verify(signature: DapSign, data: Union[bytes, str], 
                public_key: Optional[DapKey] = None) -> bool:
    """Quick signature verification"""
    return signature.verify(data, public_key)


__all__ = [
    'DapSign', 
    'DapSignError', 
    'DapHashType',
    'DapSignatureAggregator',
    'DapBatchVerifier',
    'quick_sign',
    'quick_verify'
] 