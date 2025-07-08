"""
🏗️ Core Types for Cellframe Python SDK

This module defines the core type system used throughout the SDK.
All types are designed to be type-safe, self-validating, and pythonic.
"""

from typing import Union, Optional, Any, Dict, List, NewType
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from enum import Enum
import re


# ===== STRING-BASED TYPES =====
# These are type-safe string types with validation

class Address(str):
    """Cellframe wallet address with validation."""
    
    def __new__(cls, value: str) -> 'Address':
        if not cls.is_valid_address(value):
            raise ValueError(f"Invalid address format: {value}")
        return super().__new__(cls, value)
    
    @classmethod
    def is_valid_address(cls, address: str) -> bool:
        """Validate address format."""
        # Basic validation - in real implementation would use proper validation
        return bool(re.match(r'^[A-Za-z0-9]{40,64}$', address))
    
    @classmethod
    def from_public_key(cls, public_key: 'CryptoKey') -> 'Address':
        """Create address from public key."""
        # Implementation would derive address from public key
        raise NotImplementedError("Address.from_public_key not implemented")
    
    def to_bytes(self) -> bytes:
        """Convert address to bytes."""
        return bytes.fromhex(self)
    
    def is_contract_address(self) -> bool:
        """Check if this is a contract address."""
        # Implementation would check contract address patterns
        return False


class TransactionHash(str):
    """Transaction hash with validation."""
    
    def __new__(cls, value: str) -> 'TransactionHash':
        if not cls.is_valid_hash(value):
            raise ValueError(f"Invalid transaction hash format: {value}")
        return super().__new__(cls, value)
    
    @classmethod
    def is_valid_hash(cls, hash_str: str) -> bool:
        """Validate hash format."""
        return bool(re.match(r'^[a-fA-F0-9]{64}$', hash_str))
    
    def to_bytes(self) -> bytes:
        """Convert hash to bytes."""
        return bytes.fromhex(self)


class BlockHash(str):
    """Block hash with validation."""
    
    def __new__(cls, value: str) -> 'BlockHash':
        if not cls.is_valid_hash(value):
            raise ValueError(f"Invalid block hash format: {value}")
        return super().__new__(cls, value)
    
    @classmethod
    def is_valid_hash(cls, hash_str: str) -> bool:
        """Validate hash format."""
        return bool(re.match(r'^[a-fA-F0-9]{64}$', hash_str))
    
    def to_bytes(self) -> bytes:
        """Convert hash to bytes."""
        return bytes.fromhex(self)


class Mnemonic(str):
    """BIP39 mnemonic phrase with validation."""
    
    def __new__(cls, value: str) -> 'Mnemonic':
        if not cls.is_valid_mnemonic(value):
            raise ValueError(f"Invalid mnemonic phrase")
        return super().__new__(cls, value)
    
    @classmethod
    def is_valid_mnemonic(cls, mnemonic: str) -> bool:
        """Validate mnemonic phrase."""
        words = mnemonic.split()
        return len(words) in [12, 15, 18, 21, 24]
    
    def to_seed(self, passphrase: str = "") -> bytes:
        """Convert mnemonic to seed bytes."""
        # Implementation would use BIP39 standard
        raise NotImplementedError("Mnemonic.to_seed not implemented")


# ===== NETWORK TYPES =====

NetworkID = NewType('NetworkID', str)  # Network identifier


# ===== ENUMS =====

class NetworkType(Enum):
    """Network type enumeration."""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    PRIVATE = "private"
    REGTEST = "regtest"


class KeyType(Enum):
    """Cryptographic key type enumeration."""
    ECDSA_SECP256K1 = "ecdsa_secp256k1"
    ECDSA_P256 = "ecdsa_p256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ED25519 = "ed25519"
    X25519 = "x25519"


class HashAlgorithm(Enum):
    """Hash algorithm enumeration."""
    SHA256 = "sha256"
    SHA3_256 = "sha3_256"
    BLAKE2B = "blake2b"
    KECCAK256 = "keccak256"


class CipherAlgorithm(Enum):
    """Cipher algorithm enumeration."""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    XCHACHA20_POLY1305 = "xchacha20_poly1305"


class SignatureAlgorithm(Enum):
    """Signature algorithm enumeration."""
    ECDSA_SHA256 = "ecdsa_sha256"
    ECDSA_SHA3_256 = "ecdsa_sha3_256"
    ED25519 = "ed25519"
    RSA_PSS_SHA256 = "rsa_pss_sha256"


class TransactionType(Enum):
    """Transaction type enumeration."""
    TRANSFER = "transfer"
    CONTRACT_CALL = "contract_call"
    CONTRACT_DEPLOY = "contract_deploy"
    STAKE = "stake"
    UNSTAKE = "unstake"
    GOVERNANCE = "governance"


class TransactionStatus(Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REJECTED = "rejected"


# ===== COMPLEX TYPES =====

class TokenAmount:
    """Token amount with decimal precision and validation."""
    
    def __init__(self, value: Union[str, int, float, Decimal], symbol: str = "CELL"):
        """Initialize token amount.
        
        Args:
            value: Amount value
            symbol: Token symbol (default: CELL)
        """
        if isinstance(value, str):
            self.value = Decimal(value)
        elif isinstance(value, (int, float)):
            self.value = Decimal(str(value))
        elif isinstance(value, Decimal):
            self.value = value
        else:
            raise TypeError(f"Unsupported value type: {type(value)}")
        
        self.symbol = symbol
        
        if self.value < 0:
            raise ValueError("Token amount cannot be negative")
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.value} {self.symbol}"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"TokenAmount('{self.value}', '{self.symbol}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, TokenAmount):
            return False
        return self.value == other.value and self.symbol == other.symbol
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, TokenAmount):
            raise TypeError("Cannot compare TokenAmount with non-TokenAmount")
        if self.symbol != other.symbol:
            raise ValueError("Cannot compare different token types")
        return self.value < other.value
    
    def __add__(self, other) -> 'TokenAmount':
        """Addition."""
        if not isinstance(other, TokenAmount):
            raise TypeError("Cannot add TokenAmount with non-TokenAmount")
        if self.symbol != other.symbol:
            raise ValueError("Cannot add different token types")
        return TokenAmount(self.value + other.value, self.symbol)
    
    def __sub__(self, other) -> 'TokenAmount':
        """Subtraction."""
        if not isinstance(other, TokenAmount):
            raise TypeError("Cannot subtract TokenAmount with non-TokenAmount")
        if self.symbol != other.symbol:
            raise ValueError("Cannot subtract different token types")
        return TokenAmount(self.value - other.value, self.symbol)
    
    def __mul__(self, scalar: Union[int, float, Decimal]) -> 'TokenAmount':
        """Multiplication by scalar."""
        if isinstance(scalar, (int, float)):
            scalar = Decimal(str(scalar))
        elif not isinstance(scalar, Decimal):
            raise TypeError("Can only multiply by numeric types")
        return TokenAmount(self.value * scalar, self.symbol)
    
    def to_wei(self, decimals: int = 18) -> int:
        """Convert to wei (smallest unit)."""
        return int(self.value * (10 ** decimals))
    
    @classmethod
    def from_wei(cls, wei_value: int, symbol: str = "CELL", decimals: int = 18) -> 'TokenAmount':
        """Create from wei value."""
        value = Decimal(wei_value) / (10 ** decimals)
        return cls(value, symbol)
    
    def format_display(self, precision: int = 6) -> str:
        """Format for display with specified precision."""
        rounded = self.value.quantize(Decimal(10) ** -precision)
        return f"{rounded} {self.symbol}"


# ===== CONFIGURATION TYPES =====

class NodeConfig:
    """Node configuration with validation."""
    
    def __init__(
        self,
        network: str = 'mainnet',
        data_dir: Optional[Path] = None,
        log_level: str = 'INFO',
        max_connections: int = 50,
        enable_mining: bool = False,
        plugin_mode: bool = False,
        **kwargs
    ):
        """Initialize node configuration."""
        self.network = network
        self.data_dir = data_dir or Path.home() / '.cellframe'
        self.log_level = log_level
        self.max_connections = max_connections
        self.enable_mining = enable_mining
        self.plugin_mode = plugin_mode
        self.extra_config = kwargs
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration."""
        valid_networks = ['mainnet', 'testnet', 'private', 'regtest']
        if self.network not in valid_networks:
            raise ValueError(f"Invalid network: {self.network}. Must be one of {valid_networks}")
        
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")
        
        if self.max_connections <= 0:
            raise ValueError("max_connections must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'network': self.network,
            'data_dir': str(self.data_dir),
            'log_level': self.log_level,
            'max_connections': self.max_connections,
            'enable_mining': self.enable_mining,
            'plugin_mode': self.plugin_mode,
            **self.extra_config
        }
    
    def merge(self, other: 'NodeConfig') -> 'NodeConfig':
        """Merge with another configuration."""
        merged_config = self.to_dict()
        merged_config.update(other.to_dict())
        return NodeConfig(**merged_config)


# ===== UTILITY TYPES =====

class ValidationResult:
    """Result of validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        """Initialize validation result."""
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def __bool__(self) -> bool:
        """Boolean conversion."""
        return self.is_valid
    
    def __str__(self) -> str:
        """String representation."""
        if self.is_valid:
            return "Valid"
        return f"Invalid: {', '.join(self.errors)}"
    
    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)


# ===== TYPE ALIASES =====

# Event system types
EventCallback = NewType('EventCallback', callable)
EventFilter = Dict[str, Any]

# Network types
PeerID = NewType('PeerID', str)
ConnectionID = NewType('ConnectionID', str)

# Crypto types
KeyFingerprint = NewType('KeyFingerprint', str)
Nonce = NewType('Nonce', int)

# Export all types
__all__ = [
    # Core types
    'Address', 'TransactionHash', 'BlockHash', 'Mnemonic',
    'NetworkID', 'TokenAmount', 'NodeConfig', 'ValidationResult',
    
    # Enums
    'NetworkType', 'KeyType', 'HashAlgorithm', 'CipherAlgorithm',
    'SignatureAlgorithm', 'TransactionType', 'TransactionStatus',
    
    # Type aliases
    'EventCallback', 'EventFilter', 'PeerID', 'ConnectionID',
    'KeyFingerprint', 'Nonce'
] 