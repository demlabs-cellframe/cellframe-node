"""
🔀 Conditional Transaction Processor (Legacy Interface)

Legacy interface for conditional transactions. This module now serves
as a compatibility layer that re-exports the new modular ConditionalProcessor.

For new code, consider using the specialized processors directly:
- from cellframe.composer.cond import StakeLockProcessor
- from cellframe.composer.cond import ExchangeProcessor  
- from cellframe.composer.cond import VotingProcessor
- etc.

For backward compatibility, the original ConditionalProcessor interface
is maintained through the unified processor.
"""

# Re-export the new unified ConditionalProcessor for backward compatibility
from .cond.unified import ConditionalProcessor

# Re-export specialized processors for convenience
from .cond import (
    BaseConditionalProcessor,
    StakeLockProcessor,
    ExchangeProcessor,
    VotingProcessor,
    ServicePaymentProcessor,
    DelegationProcessor
)

__all__ = [
    # Main processor (backward compatibility)
    'ConditionalProcessor',
    
    # Specialized processors
    'BaseConditionalProcessor',
    'StakeLockProcessor',
    'ExchangeProcessor',
    'VotingProcessor',
    'ServicePaymentProcessor',
    'DelegationProcessor'
] 