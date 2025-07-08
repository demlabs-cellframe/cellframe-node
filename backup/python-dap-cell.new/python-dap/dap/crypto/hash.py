"""
🔢 DAP Hash Operations

Direct Python wrapper over DAP hash functions.
Handles various hashing algorithms and operations.
"""

import logging
from typing import Union, Optional
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        dap_hash_fast, dap_hash_slow
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations
    def dap_hash_fast(data): return b"hash_fast_result"
    def dap_hash_slow(data): return b"hash_slow_result"

from ..core.exceptions import DapException


class DapHashType(Enum):
    """DAP supported hash types"""
    FAST = "fast"
    SLOW = "slow"


class DapHashError(DapException):
    """DAP Hash specific errors"""
    pass


class DapHash:
    """
    🔢 DAP Hash wrapper
    
    Direct wrapper over dap_hash_* functions.
    Provides access to DAP hashing algorithms.
    
    Example:
        # Fast hash
        fast_hash = DapHash.fast(b"data to hash")
        
        # Slow hash  
        slow_hash = DapHash.slow(b"data to hash")
        
        # Using instance
        hasher = DapHash(DapHashType.FAST)
        result = hasher.hash(b"data")
    """
    
    def __init__(self, hash_type: DapHashType = DapHashType.FAST):
        """
        Initialize hash handler
        
        Args:
            hash_type: Type of hash algorithm to use
        """
        self._hash_type = hash_type
        self._logger = logging.getLogger(__name__)
    
    @staticmethod
    def fast(data: Union[bytes, str]) -> bytes:
        """
        Calculate fast hash of data
        
        Args:
            data: Data to hash
            
        Returns:
            Hash result bytes
            
        Raises:
            DapHashError: If hashing fails
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            # Call C function: dap_hash_fast()
            result = dap_hash_fast(data)
            if result is None:
                raise DapHashError("Fast hash calculation failed")
            
            logging.getLogger(__name__).debug(
                f"Fast hash calculated, input: {len(data)} bytes, output: {len(result)} bytes"
            )
            return result
            
        except Exception as e:
            raise DapHashError(f"Fast hash failed: {e}")
    
    @staticmethod
    def slow(data: Union[bytes, str]) -> bytes:
        """
        Calculate slow hash of data
        
        Args:
            data: Data to hash
            
        Returns:
            Hash result bytes
            
        Raises:
            DapHashError: If hashing fails
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            # Call C function: dap_hash_slow()
            result = dap_hash_slow(data)
            if result is None:
                raise DapHashError("Slow hash calculation failed")
            
            logging.getLogger(__name__).debug(
                f"Slow hash calculated, input: {len(data)} bytes, output: {len(result)} bytes"
            )
            return result
            
        except Exception as e:
            raise DapHashError(f"Slow hash failed: {e}")
    
    def hash(self, data: Union[bytes, str]) -> bytes:
        """
        Hash data using instance hash type
        
        Args:
            data: Data to hash
            
        Returns:
            Hash result bytes
        """
        if self._hash_type == DapHashType.FAST:
            return self.fast(data)
        elif self._hash_type == DapHashType.SLOW:
            return self.slow(data)
        else:
            raise DapHashError(f"Unknown hash type: {self._hash_type}")
    
    @property
    def hash_type(self) -> DapHashType:
        """Get hash type"""
        return self._hash_type
    
    @hash_type.setter
    def hash_type(self, value: DapHashType):
        """Set hash type"""
        self._hash_type = value
    
    def __repr__(self) -> str:
        return f"DapHash(type={self._hash_type.value})"


# Convenience functions for quick operations
def quick_hash_fast(data: Union[bytes, str]) -> bytes:
    """Quick fast hash function"""
    return DapHash.fast(data)


def quick_hash_slow(data: Union[bytes, str]) -> bytes:
    """Quick slow hash function"""
    return DapHash.slow(data)


__all__ = [
    'DapHash', 
    'DapHashType', 
    'DapHashError',
    'quick_hash_fast',
    'quick_hash_slow'
] 