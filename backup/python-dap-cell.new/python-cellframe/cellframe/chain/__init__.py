"""
🔗 Cellframe Chain Module

Comprehensive blockchain interaction framework providing unified interfaces 
for wallet management, transaction composition, and ledger operations.

Usage:
    from cellframe.chain import Wallet
    from cellframe.composer import Composer
    
    # Open wallet and create transaction
    wallet = Wallet.open("/path/to/wallet", password="your_password")
    with Composer(net_name="mainnet", wallet=wallet) as composer:
        tx = composer.create_tx(dest_addr, amount, "CELL", fee)
"""

from .wallet import (
    Wallet,
    WalletAddress,
    WalletAccessType,
    WalletType,
    WalletError,
    InvalidAddressError,
    InsufficientFundsError,
    WalletManager,
    create_wallet,
    open_wallet,
    get_wallet,
    close_wallet,
    get_all_wallets,
    close_all_wallets
)

from .ledger import (
    Ledger,
    LedgerError,
    BalanceInfo,
    TransactionInfo
)

from .tx import (
    TX,
    TxError,
    TxType,
    TxStatus,
    TxInput,
    TxOutput,
    get_tx_by_hash,
    broadcast_tx
)

# Re-export composer module components for convenience
from ..composer import (
    Composer,
    FeeOptimizer,
    BatchProcessor,
    TransactionTemplates,
    ConditionalProcessor,
    ComposeConfig,
    FeeStructure,
    TransactionInput,
    TransactionOutput,
    ComposeError,
    FeeCalculationError,
    InputSelectionError,
    OutputCreationError,
    TemplateError,
    BatchProcessingError,
    ConditionalTransactionError,
    composer_context,
    quick_transfer
)

__all__ = [
    # Core wallet functionality
    'Wallet',
    'WalletAddress', 
    'WalletAccessType',
    'WalletType',
    'WalletError',
    'InvalidAddressError',
    'InsufficientFundsError',
    'WalletManager',
    'create_wallet',
    'open_wallet',
    'get_wallet',
    'close_wallet',
    'get_all_wallets',
    'close_all_wallets',
    
    # Ledger operations
    'Ledger',
    'LedgerError',
    'BalanceInfo',
    'TransactionInfo',
    
    # Transaction management
    'TX',
    'TxError',
    'TxType',
    'TxStatus',
    'TxInput',
    'TxOutput',
    'get_tx_by_hash',
    'broadcast_tx',
    
    # Advanced composition (from composer module)
    'Composer',
    'FeeOptimizer',
    'BatchProcessor',
    'TransactionTemplates',
    'ConditionalProcessor',
    'ComposeConfig',
    'FeeStructure',
    'TransactionInput',
    'TransactionOutput',
    'ComposeError',
    'FeeCalculationError',
    'InputSelectionError',
    'OutputCreationError',
    'TemplateError',
    'BatchProcessingError',
    'ConditionalTransactionError',
    'composer_context',
    'quick_transfer'
] 