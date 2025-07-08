"""
⛓️ Cellframe Chain Module

High-level blockchain operations for Cellframe.
Contains wallet, transaction, and ledger management.

Key Classes:
- DapWallet: Wallet management with full lifecycle
- DapTransaction: Transaction creation and management  
- DapLedger: Ledger operations and state management
- DapAccount: Account representation and operations

Each class contains the corresponding C structure internally and provides:
- Thread-safe operations
- Proper lifecycle management
- Comprehensive error handling
- Context manager support
- Fallback implementations for development

Comprehensive blockchain operations for Cellframe SDK.
Handles wallets, transactions, ledger operations, and advanced transaction composition.

Components:
- Wallet: Advanced wallet management with transaction support
- Transaction: Transaction creation and management
- Ledger: Ledger operations and balance queries
- TxComposer: Advanced transaction composition engine

Usage:
    from cellframe.chain import Wallet, TxComposer, TransactionType
    
    # Create and use wallet
    wallet = Wallet.create("my_wallet", WalletAccessType.LOCAL)
    
    # Use transaction composer for complex operations
    with TxComposer("mainnet", wallet.get_address()) as composer:
        tx = composer.create_transfer(
            to_address=dest_addr,
            amount=Decimal("100.0"),
            token_ticker="CELL",
            fee=Decimal("0.1")
        )
"""

# Import all chain classes
from .wallet import (
    DapWallet, DapWalletType, DapWalletError, DapWalletManager,
    create_wallet, load_wallet, get_all_wallets,
    Wallet,
    WalletError,
    StakeLockError,
    TransactionError,
    WalletAccessType,
    WalletAddress,
    TransactionType,
    TransactionStatus
)

from .transaction import (
    DapTransaction, DapTransactionType, DapTransactionStatus, DapTransactionError,
    DapTransactionInput, DapTransactionOutput, DapTransactionManager,
    create_transaction, broadcast_transaction, get_transaction_history
)

from .ledger import (
    DapLedger, DapLedgerType, DapLedgerError, DapAccount, DapLedgerManager,
    create_ledger, get_ledger, get_account_balance
)

# Transaction composition functionality
from .transaction_composer import (
    TxComposer,
    ComposeError,
    FeeCalculationError,
    InsufficientFundsError,
    InputSelectionError,
    OutputCreationError,
    ComposeConfig,
    FeeStructure,
    TransactionInput,
    TransactionOutput,
    transaction_composer,
    quick_transfer
)

# Export all chain components
__all__ = [
    # Wallet
    'DapWallet', 'DapWalletType', 'DapWalletError', 'DapWalletManager',
    'create_wallet', 'load_wallet', 'get_all_wallets',
    
    # Transaction  
    'DapTransaction', 'DapTransactionType', 'DapTransactionStatus', 'DapTransactionError',
    'DapTransactionInput', 'DapTransactionOutput', 'DapTransactionManager',
    'create_transaction', 'broadcast_transaction', 'get_transaction_history',
    
    # Ledger
    'DapLedger', 'DapLedgerType', 'DapLedgerError', 'DapAccount', 'DapLedgerManager',
    'create_ledger', 'get_ledger', 'get_account_balance',
    
    # Wallet classes and types
    'Wallet',
    'WalletError',
    'StakeLockError', 
    'TransactionError',
    'WalletAccessType',
    'WalletAddress',
    'TransactionType',
    'TransactionStatus',
    
    # Transaction composer classes and types
    'TxComposer',
    'ComposeError',
    'FeeCalculationError',
    'InsufficientFundsError',
    'InputSelectionError',
    'OutputCreationError',
    'ComposeConfig',
    'FeeStructure',
    'TransactionInput',
    'TransactionOutput',
    
    # Convenience functions
    'transaction_composer',
    'quick_transfer',
] 