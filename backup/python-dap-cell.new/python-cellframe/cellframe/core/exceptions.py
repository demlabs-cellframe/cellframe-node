"""
🛡️ Cellframe SDK Exception Hierarchy

Exception classes for Cellframe SDK operations.
All exceptions inherit from base DAP exceptions for consistency.

Exception Hierarchy:
    DapException (from python-dap)
    └── CellframeException
        ├── BlockchainException
        │   ├── TransactionException
        │   ├── BlockException
        │   └── ConsensusException
        ├── NetworkException
        │   ├── ConnectionException
        │   └── PeerException
        ├── CryptoException
        │   ├── KeyException
        │   └── SignatureException
        ├── ValidationException
        ├── ConfigurationException
        ├── ResourceException
        ├── EventSystemException
        ├── WalletException
        └── ServiceException
"""

from typing import Any, Dict, List, Optional, Union

# Import base exceptions from python-dap
try:
    from dap import DapException, format_exception_context
except ImportError:
    # Fallback if python-dap not available
    class DapException(Exception):
        def __init__(self, message: str, error_code: str = "DAP_ERROR", **kwargs):
            super().__init__(message)
            self.message = message
            self.error_code = error_code
    
    def format_exception_context(exception): 
        return str(exception)


class CellframeException(DapException):
    """
    Base exception for all Cellframe SDK errors.
    
    Inherits from DapException to maintain consistency with DAP SDK.
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="CELLFRAME_ERROR",
            **kwargs
        )


class BlockchainException(CellframeException):
    """Exception for blockchain-related errors."""
    
    def __init__(self, message: str, chain_id: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="BLOCKCHAIN_ERROR",
            **kwargs
        )
        
        if chain_id:
            self.add_context("chain_id", chain_id)
        
        self.add_suggestion("Check blockchain configuration")
        self.add_suggestion("Verify chain synchronization")


class TransactionException(BlockchainException):
    """Exception for transaction-related errors."""
    
    def __init__(self, message: str, tx_hash: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            **kwargs
        )
        self.error_code = "TRANSACTION_ERROR"
        
        if tx_hash:
            self.add_context("transaction_hash", tx_hash)
        
        self.add_suggestion("Check transaction format")
        self.add_suggestion("Verify transaction signatures")


class BlockException(BlockchainException):
    """Exception for block-related errors."""
    
    def __init__(self, message: str, block_hash: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            **kwargs
        )
        self.error_code = "BLOCK_ERROR"
        
        if block_hash:
            self.add_context("block_hash", block_hash)
        
        self.add_suggestion("Check block format")
        self.add_suggestion("Verify block signatures")


class ConsensusException(BlockchainException):
    """Exception for consensus-related errors."""
    
    def __init__(self, message: str, consensus_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            **kwargs
        )
        self.error_code = "CONSENSUS_ERROR"
        
        if consensus_type:
            self.add_context("consensus_type", consensus_type)
        
        self.add_suggestion("Check consensus configuration")
        self.add_suggestion("Verify node participation")


class NetworkException(CellframeException):
    """Exception for network-related errors."""
    
    def __init__(self, message: str, network_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            **kwargs
        )
        
        if network_name:
            self.add_context("network_name", network_name)
        
        self.add_suggestion("Check network connectivity")
        self.add_suggestion("Verify network configuration")


class ConnectionException(NetworkException):
    """Exception for connection-related errors."""
    
    def __init__(self, message: str, peer_address: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            **kwargs
        )
        self.error_code = "CONNECTION_ERROR"
        
        if peer_address:
            self.add_context("peer_address", peer_address)
        
        self.add_suggestion("Check network connectivity to peer")
        self.add_suggestion("Verify peer address and port")


class PeerException(NetworkException):
    """Exception for peer-related errors."""
    
    def __init__(self, message: str, peer_id: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            **kwargs
        )
        self.error_code = "PEER_ERROR"
        
        if peer_id:
            self.add_context("peer_id", peer_id)
        
        self.add_suggestion("Check peer status")
        self.add_suggestion("Verify peer authentication")


class CryptoException(CellframeException):
    """Exception for cryptographic errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="CRYPTO_ERROR",
            **kwargs
        )
        
        if operation:
            self.add_context("crypto_operation", operation)
        
        self.add_suggestion("Check cryptographic key validity")
        self.add_suggestion("Verify crypto algorithm parameters")


class KeyException(CryptoException):
    """Exception for key-related errors."""
    
    def __init__(self, message: str, key_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            **kwargs
        )
        self.error_code = "KEY_ERROR"
        
        if key_type:
            self.add_context("key_type", key_type)
        
        self.add_suggestion("Check key format and validity")
        self.add_suggestion("Verify key generation parameters")


class SignatureException(CryptoException):
    """Exception for signature-related errors."""
    
    def __init__(self, message: str, signature_algorithm: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            **kwargs
        )
        self.error_code = "SIGNATURE_ERROR"
        
        if signature_algorithm:
            self.add_context("signature_algorithm", signature_algorithm)
        
        self.add_suggestion("Check signature format")
        self.add_suggestion("Verify signing key")


class ValidationException(CellframeException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, validation_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            **kwargs
        )
        
        if validation_type:
            self.add_context("validation_type", validation_type)
        
        self.add_suggestion("Check input data format")
        self.add_suggestion("Verify validation rules")


class ConfigurationException(CellframeException):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            **kwargs
        )
        
        if config_key:
            self.add_context("config_key", config_key)
        
        self.add_suggestion("Check configuration documentation")
        self.add_suggestion("Validate configuration schema")


class ResourceException(CellframeException):
    """Exception for resource-related errors."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="RESOURCE_ERROR",
            **kwargs
        )
        
        if resource_type:
            self.add_context("resource_type", resource_type)
        
        self.add_suggestion("Check resource availability")
        self.add_suggestion("Verify resource permissions")


class EventSystemException(CellframeException):
    """Exception for event system errors."""
    
    def __init__(self, message: str, event_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EVENT_ERROR",
            **kwargs
        )
        
        if event_type:
            self.add_context("event_type", event_type)
        
        self.add_suggestion("Check event system initialization")
        self.add_suggestion("Verify event handler registration")


class WalletException(CellframeException):
    """Exception for wallet-related errors."""
    
    def __init__(self, message: str, wallet_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="WALLET_ERROR",
            **kwargs
        )
        
        if wallet_name:
            self.add_context("wallet_name", wallet_name)
        
        self.add_suggestion("Check wallet file integrity")
        self.add_suggestion("Verify wallet password")


class ServiceException(CellframeException):
    """Exception for service-related errors."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="SERVICE_ERROR",
            **kwargs
        )
        
        if service_name:
            self.add_context("service_name", service_name)
        
        self.add_suggestion("Check service configuration")
        self.add_suggestion("Verify service dependencies")


def create_exception_from_error_code(
    error_code: str,
    message: str,
    **context
) -> CellframeException:
    """Create appropriate Cellframe exception based on error code."""
    exception_map = {
        'CELLFRAME_ERROR': CellframeException,
        'BLOCKCHAIN_ERROR': BlockchainException,
        'TRANSACTION_ERROR': TransactionException,
        'BLOCK_ERROR': BlockException,
        'CONSENSUS_ERROR': ConsensusException,
        'NETWORK_ERROR': NetworkException,
        'CONNECTION_ERROR': ConnectionException,
        'PEER_ERROR': PeerException,
        'CRYPTO_ERROR': CryptoException,
        'KEY_ERROR': KeyException,
        'SIGNATURE_ERROR': SignatureException,
        'VALIDATION_ERROR': ValidationException,
        'CONFIG_ERROR': ConfigurationException,
        'RESOURCE_ERROR': ResourceException,
        'EVENT_ERROR': EventSystemException,
        'WALLET_ERROR': WalletException,
        'SERVICE_ERROR': ServiceException
    }
    
    exception_class = exception_map.get(error_code, CellframeException)
    return exception_class(message=message, error_code=error_code, context=context)


__all__ = [
    # Base
    'CellframeException',
    
    # Blockchain
    'BlockchainException', 'TransactionException', 'BlockException', 'ConsensusException',
    
    # Network
    'NetworkException', 'ConnectionException', 'PeerException',
    
    # Crypto
    'CryptoException', 'KeyException', 'SignatureException',
    
    # General
    'ValidationException', 'ConfigurationException', 'ResourceException', 
    'EventSystemException', 'WalletException', 'ServiceException',
    
    # Utilities
    'create_exception_from_error_code'
] 