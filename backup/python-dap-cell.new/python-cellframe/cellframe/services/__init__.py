"""
🏢 Cellframe Services Module

High-level APIs for Cellframe blockchain services.
Contains service interfaces that work across both plugin and library modes.

Key Services:
- StakingService: Staking and delegation operations
- ExchangeService: Token exchange and trading
- VotingService: Governance and voting operations  
- OrderService: Order management and matching
- BridgeService: Cross-chain bridging operations

Each service follows the universal architecture pattern with:
- Context-aware initialization
- Thread-safe operations
- Comprehensive error handling
- Fallback implementations for development
"""

# Import all services
from .staking import StakingService
from .exchange import ExchangeService
from .voting import VotingService
from .order import OrderService
from .bridge import BridgeService

# Export all services
__all__ = [
    'StakingService',
    'ExchangeService', 
    'VotingService',
    'OrderService',
    'BridgeService'
] 