"""
🔀 Unified Conditional Transaction Processor

Main conditional processor that routes requests to specialized processors
based on transaction type. Provides backward compatibility with the original
ConditionalProcessor interface while using the new modular architecture.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional

from .stake_lock import StakeLockProcessor
from .exchange import ExchangeProcessor
from .voting import VotingProcessor
from .service_payment import ServicePaymentProcessor
from .delegation import DelegationProcessor
from ..exceptions import ConditionalTransactionError
from ...chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class ConditionalProcessor:
    """
    🔀 Unified Conditional Transaction Processor
    
    Main entry point for conditional transactions that routes requests
    to specialized processors based on transaction type.
    
    Maintains backward compatibility with the original ConditionalProcessor
    interface while leveraging the new modular architecture underneath.
    
    Supported Transaction Types:
    - SRV_PAY: Service payment conditions → ServicePaymentProcessor
    - SRV_XCHANGE: Token exchange conditions → ExchangeProcessor
    - SRV_STAKE_LOCK: Stake lock conditions → StakeLockProcessor
    - SRV_VOTING: Voting proposal conditions → VotingProcessor
    - SRV_STAKE_POS_DELEGATE: Delegation conditions → DelegationProcessor
    """
    
    def __init__(self, composer):
        """
        Initialize unified conditional processor.
        
        Args:
            composer: Main composer instance
        """
        self.composer = composer
        
        # Initialize specialized processors
        self._processors = {
            TransactionType.SRV_PAY: ServicePaymentProcessor(composer),
            TransactionType.SRV_XCHANGE: ExchangeProcessor(composer),
            TransactionType.SRV_STAKE_LOCK: StakeLockProcessor(composer),
            TransactionType.SRV_VOTING: VotingProcessor(composer),
            TransactionType.SRV_STAKE_POS_DELEGATE: DelegationProcessor(composer),
        }
        
        logger.debug("ConditionalProcessor initialized with %d specialized processors", 
                    len(self._processors))
    
    def create_conditional_transaction(self, condition_type: TransactionType, 
                                     value: Decimal, fee: Decimal,
                                     **kwargs) -> str:
        """
        Create conditional transaction using appropriate specialized processor.
        
        Args:
            condition_type: Type of conditional transaction
            value: Amount to lock in condition
            fee: Transaction fee
            **kwargs: Condition-specific parameters
            
        Returns:
            str: Transaction hash
            
        Raises:
            ConditionalTransactionError: If transaction creation fails
        """
        try:
            # Get specialized processor for this transaction type
            processor = self._get_processor(condition_type)
            
            # Delegate to specialized processor
            return processor.create_conditional_transaction(value, fee, **kwargs)
            
        except Exception as e:
            logger.error("Failed to create conditional transaction: %s", e)
            raise ConditionalTransactionError(f"Failed to create conditional transaction: {e}")
    
    def _get_processor(self, condition_type: TransactionType):
        """Get specialized processor for transaction type."""
        processor = self._processors.get(condition_type)
        if not processor:
            raise ConditionalTransactionError(f"Unsupported condition type: {condition_type}")
        return processor
    
    # === Backward Compatibility Methods ===
    
    def create_exchange_order(self, token_sell: str, token_buy: str, 
                            amount: Decimal, rate: Decimal, fee: Decimal,
                            expiration: Optional[int] = None) -> str:
        """Create exchange order - delegates to ExchangeProcessor."""
        return self._processors[TransactionType.SRV_XCHANGE].create_exchange_order(
            token_sell, token_buy, amount, rate, fee, expiration
        )
    
    def create_stake_lock_order(self, amount: Decimal, lock_time: str, 
                               reinvest_percent: Decimal, fee: Decimal) -> str:
        """Create stake lock order - delegates to StakeLockProcessor."""
        return self._processors[TransactionType.SRV_STAKE_LOCK].create_stake_lock_order(
            amount, lock_time, reinvest_percent, fee
        )
    
    def create_voting_proposal(self, question: str, options: List[str], 
                             max_votes: int, fee: Decimal,
                             expire_time: Optional[int] = None) -> str:
        """Create voting proposal - delegates to VotingProcessor."""
        return self._processors[TransactionType.SRV_VOTING].create_voting_proposal(
            question, options, max_votes, fee, expire_time
        )
    
    def create_vote_transaction(self, voting_hash: str, vote_option: str, fee: Decimal) -> str:
        """Create vote transaction - delegates to VotingProcessor."""
        return self._processors[TransactionType.SRV_VOTING].create_vote_transaction(
            voting_hash, vote_option, fee
        )
    
    # === Extended Access to Specialized Processors ===
    
    @property
    def stake_lock(self) -> StakeLockProcessor:
        """Get access to StakeLockProcessor for advanced stake lock operations."""
        return self._processors[TransactionType.SRV_STAKE_LOCK]
    
    @property
    def exchange(self) -> ExchangeProcessor:
        """Get access to ExchangeProcessor for advanced exchange operations."""
        return self._processors[TransactionType.SRV_XCHANGE]
    
    @property
    def voting(self) -> VotingProcessor:
        """Get access to VotingProcessor for advanced voting operations."""
        return self._processors[TransactionType.SRV_VOTING]
    
    @property
    def service_payment(self) -> ServicePaymentProcessor:
        """Get access to ServicePaymentProcessor for advanced service payment operations."""
        return self._processors[TransactionType.SRV_PAY]
    
    @property
    def delegation(self) -> DelegationProcessor:
        """Get access to DelegationProcessor for advanced delegation operations."""
        return self._processors[TransactionType.SRV_STAKE_POS_DELEGATE]
    
    # === Convenience Methods that Route to Specialized Processors ===
    
    def get_stake_locks(self, wallet_address: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all stake locks - delegates to StakeLockProcessor."""
        return self.stake_lock.get_stake_locks(wallet_address)
    
    def partial_unlock(self, lock_hash: str, unlock_amount: Decimal, fee: Decimal) -> str:
        """Partial unlock - delegates to StakeLockProcessor."""
        return self.stake_lock.partial_unlock(lock_hash, unlock_amount, fee)
    
    def compound_rewards(self, lock_hash: str, compound_percent: Decimal, fee: Decimal) -> str:
        """Compound rewards - delegates to StakeLockProcessor."""
        return self.stake_lock.compound_rewards(lock_hash, compound_percent, fee)
    
    def emergency_unlock(self, lock_hash: str, emergency_reason: str, fee: Decimal) -> str:
        """Emergency unlock - delegates to StakeLockProcessor."""
        return self.stake_lock.emergency_unlock(lock_hash, emergency_reason, fee)
    
    def get_exchange_orders(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Get exchange orders - delegates to ExchangeProcessor."""
        return self.exchange.get_exchange_orders(wallet_address)
    
    def get_voting_proposals(self, status: str = "active") -> List[Dict[str, Any]]:
        """Get voting proposals - delegates to VotingProcessor."""
        return self.voting.get_voting_proposals(status)
    
    def get_delegations(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Get delegations - delegates to DelegationProcessor."""
        return self.delegation.get_delegations(wallet_address)
    
    def get_service_payments(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Get service payments - delegates to ServicePaymentProcessor."""
        return self.service_payment.get_service_payments(wallet_address)
    
    # === Advanced Operations ===
    
    def get_all_conditional_operations(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary of all conditional operations for wallet.
        
        Args:
            wallet_address: Wallet address (uses composer wallet if None)
            
        Returns:
            Dict[str, Any]: Summary of all conditional operations
        """
        try:
            target_address = wallet_address or str(self.composer.wallet_addr)
            
            return {
                'stake_locks': self.stake_lock.get_stake_locks(target_address),
                'exchange_orders': self.exchange.get_exchange_orders(target_address),
                'delegations': self.delegation.get_delegations(target_address),
                'service_payments': self.service_payment.get_service_payments(target_address),
                'votes_cast': self.voting.get_user_votes(target_address)
            }
            
        except Exception as e:
            logger.error("Failed to get all conditional operations: %s", e)
            raise ConditionalTransactionError(f"Failed to get all conditional operations: {e}")
    
    def get_conditional_transaction_info(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get information about any conditional transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dict[str, Any]: Transaction information
        """
        # In real implementation, this would determine transaction type
        # and route to appropriate processor
        return {
            'tx_hash': tx_hash,
            'type': 'unknown',
            'status': 'pending',
            'created_at': self._processors[TransactionType.SRV_STAKE_LOCK]._get_current_time_yymmdd()
        } 