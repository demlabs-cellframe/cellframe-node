"""
🔀 Conditional Transaction Processors

Modular conditional transaction processing framework with specialized processors
for different types of conditional transactions.

Architecture:
- BaseConditionalProcessor: Abstract base class with common functionality
- StakeLockProcessor: Stake lock operations with penalties and rewards
- ExchangeProcessor: Token exchange orders with market/limit pricing
- VotingProcessor: Voting proposals and governance operations
- ServicePaymentProcessor: Payments for network services
- DelegationProcessor: Stake delegation to validators

Usage:
    from cellframe.composer.cond import StakeLockProcessor, ExchangeProcessor
    from cellframe.composer import Composer
    
    # Create specialized processor
    stake_processor = StakeLockProcessor(composer)
    tx = stake_processor.create_stake_lock_order(amount, lock_time, reinvest, fee)
    
    # Or use the unified ConditionalProcessor
    from cellframe.composer.cond import ConditionalProcessor
    cond_processor = ConditionalProcessor(composer)
    tx = cond_processor.create_conditional_transaction(...)
"""

from .base import BaseConditionalProcessor
from .stake_lock import StakeLockProcessor
from .exchange import ExchangeProcessor
from .voting import VotingProcessor
from .service_payment import ServicePaymentProcessor
from .delegation import DelegationProcessor

# Unified processor that routes to specialized processors
from .unified import ConditionalProcessor

__all__ = [
    # Base class
    'BaseConditionalProcessor',
    
    # Specialized processors
    'StakeLockProcessor',
    'ExchangeProcessor', 
    'VotingProcessor',
    'ServicePaymentProcessor',
    'DelegationProcessor',
    
    # Unified processor
    'ConditionalProcessor'
] 