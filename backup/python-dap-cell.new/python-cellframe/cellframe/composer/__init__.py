"""
🎼 Cellframe Transaction Composer Module

Advanced transaction composition framework with modular architecture.
Provides high-level API for creating complex transactions with automatic
fee calculation, input selection, and output management.

Components:
- Composer: Main transaction composition engine
- FeeOptimizer: Fee calculation and optimization algorithms  
- BatchProcessor: Batch transaction processing
- TransactionTemplates: Predefined transaction templates
- ConditionalProcessor: Conditional transaction handling (unified)

Specialized Conditional Processors:
- StakeLockProcessor: Advanced stake lock operations with penalties/rewards
- ExchangeProcessor: Token exchange orders with market/limit pricing
- VotingProcessor: Voting proposals and governance operations
- ServicePaymentProcessor: Payments for network services with conditions
- DelegationProcessor: Stake delegation to validators with rewards

Usage:
    from cellframe.composer import Composer, TransactionTemplates
    from cellframe.chain.wallet import Wallet
    
    # Open wallet and create transaction
    wallet = Wallet.open("/path/to/wallet", password="your_password")
    with Composer(net_name="mainnet", wallet=wallet) as composer:
        tx = composer.create_tx(to_addr, amount, "CELL", fee)
    
    # Using templates
    templates = TransactionTemplates(composer)
    tx = templates.create_from_template("simple_transfer", 
                                       to_address=addr, 
                                       amount="10", 
                                       token_ticker="CELL")
    
    # Using specialized conditional processors
    from cellframe.composer.cond import StakeLockProcessor
    stake_processor = StakeLockProcessor(composer)
    tx = stake_processor.create_stake_lock_order(amount, lock_time, reinvest, fee)
    
    # Or using unified processor (backward compatibility)
    from cellframe.composer import ConditionalProcessor
    cond_processor = ConditionalProcessor(composer)
    tx = cond_processor.create_conditional_transaction(...)
"""

from .core import (
    Composer,
    ComposeConfig,
    FeeStructure, 
    TransactionInput,
    TransactionOutput
)

from .fee_optimizer import FeeOptimizer
from .batch_processor import BatchProcessor  
from .templates import TransactionTemplates

# Conditional processors - unified and specialized
from .conditional import (
    ConditionalProcessor,
    StakeLockProcessor,
    ExchangeProcessor,
    VotingProcessor,
    ServicePaymentProcessor,
    DelegationProcessor
)

from .exceptions import (
    ComposeError,
    FeeCalculationError,
    InsufficientFundsError,
    InputSelectionError,
    OutputCreationError,
    ConditionalTransactionError,
    TemplateError
)

from .utils import (
    composer_context,
    quick_transfer,
    quick_exchange,
    quick_stake_lock
)

__all__ = [
    # Core components
    'Composer',
    'ComposeConfig',
    'FeeStructure',
    'TransactionInput',
    'TransactionOutput',
    
    # Processing components
    'FeeOptimizer',
    'BatchProcessor',
    'TransactionTemplates',
    
    # Conditional processors
    'ConditionalProcessor',           # Unified processor
    'StakeLockProcessor',            # Specialized for stake locks
    'ExchangeProcessor',             # Specialized for exchanges
    'VotingProcessor',               # Specialized for voting
    'ServicePaymentProcessor',       # Specialized for service payments  
    'DelegationProcessor',           # Specialized for delegations
    
    # Exceptions
    'ComposeError',
    'FeeCalculationError',
    'InsufficientFundsError',
    'InputSelectionError',
    'OutputCreationError',
    'ConditionalTransactionError',
    'TemplateError',
    
    # Utilities
    'composer_context',
    'quick_transfer',
    'quick_exchange',
    'quick_stake_lock'
] 