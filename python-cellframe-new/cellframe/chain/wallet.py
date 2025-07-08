"""
💰 Cellframe Wallet Module

Core wallet management functionality focused on wallet operations only.
Transaction creation is handled by the composer module.

Key Features:
- Wallet creation, opening, and management
- Balance queries and address generation
- Secure key management
- Thread-safe operations with proper locking
- Memory management with cleanup

For transaction creation, use the composer module:
    from cellframe.composer import Composer
    
    with Composer("mainnet", wallet.get_address()) as composer:
        tx = composer.create_transfer(dest_addr, amount, "CELL", fee)

💼 Cellframe Wallet Module

Pure wallet management functionality focused on wallet operations,
key management, and balance queries. For transaction creation, 
use the Composer module.

Usage:
    from cellframe.chain.wallet import Wallet
    from cellframe.composer import Composer
    
    # Open wallet and get balance
    wallet = Wallet.open("/path/to/wallet", password="your_password") 
    balance = wallet.get_balance("CELL")
    
    # Create transaction using composer
    with Composer(net_name="mainnet", wallet=wallet) as composer:
        tx = composer.create_tx(dest_addr, amount, "CELL", fee)
"""

import logging
import threading
from typing import Optional, Dict, Any, List, Union, Tuple
from enum import Enum
from pathlib import Path
from decimal import Decimal

# Import cellframe functions - always required
from python_cellframe_common import (
    # Real Cellframe wallet functions
    dap_chain_wallet_create, dap_chain_wallet_create_with_seed,
    dap_chain_wallet_create_with_seed_multi, dap_chain_wallet_open,
    dap_chain_wallet_open_ext, dap_chain_wallet_close, dap_chain_wallet_save,
    dap_chain_wallet_get_addr, dap_chain_wallet_get_balance,
    dap_chain_wallet_get_key, dap_chain_wallet_get_pkey,
    dap_chain_wallet_activate, dap_chain_wallet_deactivate,
    
    # Constants
    DAP_CHAIN_TICKER_SIZE_MAX,
)

from ..core.exceptions import CellframeException

logger = logging.getLogger(__name__)


class WalletError(CellframeException):
    """Base wallet exception."""
    pass


class InsufficientFundsError(WalletError):
    """Insufficient funds for transaction."""
    pass


class InvalidAddressError(WalletError):
    """Invalid wallet address."""
    pass


class WalletAccessType(Enum):
    """Types of wallet access."""
    LOCAL = "local"             # Local wallet
    REMOTE = "remote"           # Remote wallet access


class WalletType(Enum):
    """Types of wallets."""
    SIMPLE = "simple"           # Regular wallet
    MULTISIG = "multisig"       # Multi-signature
    SHARED = "shared"           # Shared wallet
    HARDWARE = "hardware"       # Hardware wallet


class WalletAddress:
    """Wallet address representation."""
    
    def __init__(self, address_str: str, net_id: int):
        """Initialize wallet address."""
        self.address = address_str
        self.net_id = net_id
    
    def __str__(self) -> str:
        return self.address
    
    def __repr__(self) -> str:
        return f"WalletAddress('{self.address}', net_id={self.net_id})"


class Wallet:
    """
    Core Cellframe wallet management.
    
    Handles wallet creation, opening, key management, and balance queries.
    For transaction creation, use the composer module.
    """
    
    def __init__(self, name: str, wallet_handle: Any = None, 
                 access_type: WalletAccessType = WalletAccessType.LOCAL):
        """Initialize wallet instance."""
        self.name = name
        self._wallet_handle = wallet_handle
        self.access_type = access_type
        self._lock = threading.RLock()
        self._is_closed = False
        self.wallet_type = WalletType.SIMPLE
        
        logger.info("Wallet %s initialized with access_type=%s", name, access_type)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    @classmethod
    def create(cls, name: str, wallet_path: str, password: Optional[str] = None,
               seed: Optional[bytes] = None, signature_type: int = 0x0102) -> 'Wallet':
        """
        Create new wallet.
        
        Args:
            name: Wallet name
            wallet_path: Path to wallet directory
            password: Wallet password
            seed: Optional seed for recovery
            signature_type: Signature algorithm type
            
        Returns:
            Wallet: Created wallet instance
            
        Raises:
            WalletError: If wallet creation fails
        """
        try:
            if seed:
                wallet_handle = dap_chain_wallet_create_with_seed(
                    name, wallet_path, signature_type, seed, len(seed), password
                )
            else:
                wallet_handle = dap_chain_wallet_create(
                    name, wallet_path, signature_type, password
                )
            
            if not wallet_handle:
                raise WalletError(f"Failed to create wallet {name}")
                
            return cls(name, wallet_handle, WalletAccessType.LOCAL)
                
        except Exception as e:
            logger.error("Failed to create wallet %s: %s", name, e)
            raise WalletError(f"Failed to create wallet {name}: {e}")
    
    @classmethod
    def open(cls, name: str, wallet_path: str, password: Optional[str] = None) -> 'Wallet':
        """
        Open existing wallet.
        
        Args:
            name: Wallet name
            wallet_path: Path to wallet directory
            password: Wallet password
            
        Returns:
            Wallet: Opened wallet instance
            
        Raises:
            WalletError: If wallet opening fails
        """
        try:
            wallet_handle = dap_chain_wallet_open(name, wallet_path, password)
            if not wallet_handle:
                raise WalletError(f"Failed to open wallet {name}")
                
            return cls(name, wallet_handle, WalletAccessType.LOCAL)
                
        except Exception as e:
            logger.error("Failed to open wallet %s: %s", name, e)
            raise WalletError(f"Failed to open wallet {name}: {e}")
    
    def get_address(self, net_id: int) -> WalletAddress:
        """
        Get wallet address for network.
        
        Args:
            net_id: Network identifier
            
        Returns:
            WalletAddress: Wallet address object
            
        Raises:
            WalletError: If address retrieval fails
        """
        with self._lock:
            try:
                addr_ptr = dap_chain_wallet_get_addr(self._wallet_handle, net_id)
                if not addr_ptr:
                    raise WalletError("Failed to get address")
                return WalletAddress(str(addr_ptr), net_id)
                    
            except Exception as e:
                logger.error("Failed to get address for %s: %s", self.name, e)
                raise WalletError(f"Failed to get address: {e}")
    
    def get_balance(self, net_id: int, token_ticker: str) -> Decimal:
        """
        Get wallet balance for token.
        
        Args:
            net_id: Network identifier
            token_ticker: Token ticker symbol
            
        Returns:
            Decimal: Current balance
            
        Raises:
            WalletError: If balance retrieval fails
        """
        with self._lock:
            try:
                balance = dap_chain_wallet_get_balance(
                    self._wallet_handle, net_id, token_ticker
                )
                return Decimal(str(balance))
                    
            except Exception as e:
                logger.error("Failed to get balance for %s: %s", self.name, e)
                raise WalletError(f"Failed to get balance: {e}")
    
    def get_key(self, key_type: int = 0x0102):
        """
        Get wallet private key.
        
        Args:
            key_type: Key type identifier
            
        Returns:
            Key object
            
        Raises:
            WalletError: If key retrieval fails
        """
        with self._lock:
            try:
                key = dap_chain_wallet_get_key(self._wallet_handle, key_type)
                if not key:
                    raise WalletError("Failed to get private key")
                return key
                    
            except Exception as e:
                logger.error("Failed to get key for %s: %s", self.name, e)
                raise WalletError(f"Failed to get key: {e}")
    
    def get_public_key(self, key_type: int = 0x0102):
        """
        Get wallet public key.
        
        Args:
            key_type: Key type identifier
            
        Returns:
            Public key object
            
        Raises:
            WalletError: If public key retrieval fails
        """
        with self._lock:
            try:
                pkey = dap_chain_wallet_get_pkey(self._wallet_handle, key_type)
                if not pkey:
                    raise WalletError("Failed to get public key")
                return pkey
                    
            except Exception as e:
                logger.error("Failed to get public key for %s: %s", self.name, e)
                raise WalletError(f"Failed to get public key: {e}")
    
    def activate(self) -> bool:
        """
        Activate wallet.
        
        Returns:
            bool: True if activated successfully
            
        Raises:
            WalletError: If activation fails
        """
        with self._lock:
            try:
                result = dap_chain_wallet_activate(self._wallet_handle)
                return result == 0
                    
            except Exception as e:
                logger.error("Failed to activate wallet %s: %s", self.name, e)
                raise WalletError(f"Failed to activate wallet: {e}")
    
    def deactivate(self) -> bool:
        """
        Deactivate wallet.
        
        Returns:
            bool: True if deactivated successfully
            
        Raises:
            WalletError: If deactivation fails
        """
        with self._lock:
            try:
                result = dap_chain_wallet_deactivate(self._wallet_handle)
                return result == 0
                    
            except Exception as e:
                logger.error("Failed to deactivate wallet %s: %s", self.name, e)
                raise WalletError(f"Failed to deactivate wallet: {e}")
    
    def validate_address(self, address: str, net_id: int) -> bool:
        """
        Validate wallet address format.
        
        Args:
            address: Address to validate
            net_id: Network identifier
            
        Returns:
            True if address is valid
        """
        try:
            # Basic validation - can be enhanced with actual API call
            return len(address) > 20 and address.startswith('mC')
                
        except Exception as e:
            logger.error("Failed to validate address: %s", e)
            return False
    
    def save(self, password: Optional[str] = None) -> bool:
        """
        Save wallet to disk.
        
        Args:
            password: Optional password for encryption
            
        Returns:
            bool: True if saved successfully
            
        Raises:
            WalletError: If save fails
        """
        with self._lock:
            try:
                result = dap_chain_wallet_save(self._wallet_handle, password)
                return result == 0
                    
            except Exception as e:
                logger.error("Failed to save wallet %s: %s", self.name, e)
                raise WalletError(f"Failed to save wallet: {e}")
    
    def close(self):
        """Close wallet and release resources."""
        with self._lock:
            if not self._is_closed:
                try:
                    dap_chain_wallet_close(self._wallet_handle)
                    self._wallet_handle = None
                    self._is_closed = True
                    
                    logger.info("Wallet %s closed", self.name)
                    
                except Exception as e:
                    logger.error("Error closing wallet %s: %s", self.name, e)
    
    def __del__(self):
        """Destructor - ensure wallet is closed."""
        if not self._is_closed:
            self.close()


class WalletManager:
    """
    Manages multiple wallets in a centralized way.
    """
    
    def __init__(self):
        """Initialize wallet manager."""
        self._wallets: Dict[str, Wallet] = {}
        self._lock = threading.RLock()
        
        logger.info("WalletManager initialized")
    
    def create_wallet(self, name: str, wallet_path: str, password: Optional[str] = None,
                     seed: Optional[bytes] = None, signature_type: int = 0x0102) -> Wallet:
        """
        Create and register new wallet.
        
        Args:
            name: Wallet name
            wallet_path: Path to wallet directory
            password: Wallet password
            seed: Optional seed for recovery
            signature_type: Signature algorithm type
            
        Returns:
            Wallet: Created wallet instance
            
        Raises:
            WalletError: If wallet creation fails
        """
        with self._lock:
            try:
                if name in self._wallets:
                    raise WalletError(f"Wallet {name} already exists")
                
                wallet = Wallet.create(name, wallet_path, password, seed, signature_type)
                self._wallets[name] = wallet
                
                logger.info("Wallet %s created and registered", name)
                return wallet
                
            except Exception as e:
                logger.error("Failed to create wallet %s: %s", name, e)
                raise
    
    def open_wallet(self, name: str, wallet_path: str, password: Optional[str] = None) -> Wallet:
        """
        Open and register existing wallet.
        
        Args:
            name: Wallet name
            wallet_path: Path to wallet directory
            password: Wallet password
            
        Returns:
            Wallet: Opened wallet instance
            
        Raises:
            WalletError: If wallet opening fails
        """
        with self._lock:
            try:
                if name in self._wallets:
                    logger.warning("Wallet %s already open, returning existing instance", name)
                    return self._wallets[name]
                
                wallet = Wallet.open(name, wallet_path, password)
                self._wallets[name] = wallet
                
                logger.info("Wallet %s opened and registered", name)
                return wallet
                
            except Exception as e:
                logger.error("Failed to open wallet %s: %s", name, e)
                raise
    
    def get_wallet(self, name: str) -> Optional[Wallet]:
        """
        Get registered wallet by name.
        
        Args:
            name: Wallet name
            
        Returns:
            Wallet instance or None if not found
        """
        with self._lock:
            return self._wallets.get(name)
    
    def close_wallet(self, name: str):
        """
        Close and unregister wallet.
        
        Args:
            name: Wallet name
        """
        with self._lock:
            if name in self._wallets:
                self._wallets[name].close()
                del self._wallets[name]
                logger.info("Wallet %s closed and unregistered", name)
    
    def get_all_wallets(self) -> Dict[str, Wallet]:
        """
        Get all registered wallets.
        
        Returns:
            Dict mapping wallet names to wallet instances
        """
        with self._lock:
            return self._wallets.copy()
    
    def close_all(self):
        """Close all registered wallets."""
        with self._lock:
            for name in list(self._wallets.keys()):
                self.close_wallet(name)
            
            logger.info("All wallets closed")


# Global wallet manager instance
_global_wallet_manager = WalletManager()


# Convenience functions using global manager
def create_wallet(name: str, wallet_path: str, password: Optional[str] = None,
                 seed: Optional[bytes] = None) -> Wallet:
    """Create wallet using global manager."""
    return _global_wallet_manager.create_wallet(name, wallet_path, password, seed)


def open_wallet(name: str, wallet_path: str, password: Optional[str] = None) -> Wallet:
    """Open wallet using global manager."""
    return _global_wallet_manager.open_wallet(name, wallet_path, password)


def get_wallet(name: str) -> Optional[Wallet]:
    """Get wallet using global manager."""
    return _global_wallet_manager.get_wallet(name)


def close_wallet(name: str):
    """Close wallet using global manager."""
    _global_wallet_manager.close_wallet(name)


def get_all_wallets() -> Dict[str, Wallet]:
    """Get all wallets using global manager."""
    return _global_wallet_manager.get_all_wallets()


def close_all_wallets():
    """Close all wallets using global manager."""
    _global_wallet_manager.close_all() 