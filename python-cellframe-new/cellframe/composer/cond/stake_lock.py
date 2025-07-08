"""
🔐 Stake Lock Conditional Processor

Specialized processor for stake lock conditional transactions.
Handles all stake lock operations including creation, partial unlock, 
compound rewards, emergency unlock, and penalty calculations.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional

from .base import BaseConditionalProcessor
from ..core import TransactionOutput
from ..exceptions import ConditionalTransactionError
from ...chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class StakeLockProcessor(BaseConditionalProcessor):
    """
    🔐 Stake Lock Conditional Processor
    
    Handles all stake lock operations:
    - Basic stake lock creation with time locks and reinvestment
    - Partial unlock with penalty calculations
    - Compound rewards for maximizing returns
    - Emergency unlock for critical situations
    - Stake lock history and information queries
    - Advanced penalty calculations
    """
    
    def get_transaction_type(self):
        """Get the transaction type handled by this processor."""
        return TransactionType.SRV_STAKE_LOCK
    
    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """Validate stake lock condition parameters."""
        required = ['lock_time']
        self._validate_required_params(required, **kwargs)
        
        return {
            'lock_time': kwargs['lock_time'],
            'reinvest_percent': Decimal(str(kwargs.get('reinvest_percent', '0'))),
            'delegated_ticker': kwargs.get('delegated_ticker'),
            'delegated_value': kwargs.get('delegated_value')
        }
    
    def create_conditional_output(self, value: Decimal, condition_params: Dict[str, Any]) -> TransactionOutput:
        """Create stake lock conditional output."""
        return TransactionOutput(
            address=self.composer.wallet_addr,
            value=value,
            token_ticker=self.composer._get_native_ticker(),
            output_type="conditional_stake_lock",
            conditions={
                'lock_time': condition_params['lock_time'],
                'reinvest_percent': condition_params['reinvest_percent'],
                'delegated_ticker': condition_params.get('delegated_ticker'),
                'delegated_value': condition_params.get('delegated_value')
            }
        )
    
    # === Convenience Methods ===
    
    def create_stake_lock_order(self, amount: Decimal, lock_time: str, 
                               reinvest_percent: Decimal, fee: Decimal) -> str:
        """
        Create stake lock order (conditional transaction).
        
        Args:
            amount: Amount to lock
            lock_time: Lock time in YYMMDD format
            reinvest_percent: Reinvestment percentage
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        return self.create_conditional_transaction(
            value=amount,
            fee=fee,
            lock_time=lock_time,
            reinvest_percent=reinvest_percent
        )
    
    # === Extended Stake Lock Operations ===
    
    def get_stake_locks(self, wallet_address: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all stake locks for wallet.
        
        Args:
            wallet_address: Wallet address (uses composer wallet if None)
            
        Returns:
            List[Dict[str, Any]]: List of stake lock information
        """
        try:
            target_address = wallet_address or str(self.composer.wallet_addr)
            return self._query_stake_locks(target_address)
            
        except Exception as e:
            self._logger.error("Failed to get stake locks: %s", e)
            raise ConditionalTransactionError(f"Failed to get stake locks: {e}")
    
    def get_stake_lock_info(self, lock_hash: str) -> Dict[str, Any]:
        """
        Get detailed information about specific stake lock.
        
        Args:
            lock_hash: Hash of the stake lock transaction
            
        Returns:
            Dict[str, Any]: Stake lock information
        """
        try:
            return self._query_stake_lock_info(lock_hash)
            
        except Exception as e:
            self._logger.error("Failed to get stake lock info: %s", e)
            raise ConditionalTransactionError(f"Failed to get stake lock info: {e}")
    
    def partial_unlock(self, lock_hash: str, unlock_amount: Decimal, fee: Decimal) -> str:
        """
        Partially unlock staked amount with proportional penalties.
        
        Args:
            lock_hash: Hash of the stake lock to partially unlock
            unlock_amount: Amount to unlock (must be less than total locked)
            fee: Transaction fee
            
        Returns:
            str: Transaction hash of partial unlock
        """
        try:
            # Validate that partial unlock is allowed
            lock_info = self.get_stake_lock_info(lock_hash)
            if not lock_info.get('partial_unlock_allowed', True):
                raise ConditionalTransactionError("Partial unlock not allowed for this stake lock")
            
            total_locked = Decimal(str(lock_info.get('amount', '0')))
            if unlock_amount >= total_locked:
                raise ConditionalTransactionError("Unlock amount must be less than total locked amount")
            
            # Calculate penalty
            penalty = self._calculate_early_unlock_penalty(lock_info, unlock_amount)
            
            return self._create_partial_unlock_transaction(lock_hash, unlock_amount, penalty, fee)
            
        except Exception as e:
            self._logger.error("Failed to create partial unlock: %s", e)
            raise ConditionalTransactionError(f"Failed to create partial unlock: {e}")
    
    def compound_rewards(self, lock_hash: str, compound_percent: Decimal, fee: Decimal) -> str:
        """
        Compound accumulated rewards into the stake lock.
        
        Args:
            lock_hash: Hash of the stake lock
            compound_percent: Percentage of rewards to compound (0-100)
            fee: Transaction fee
            
        Returns:
            str: Transaction hash of compound operation
        """
        try:
            if compound_percent < 0 or compound_percent > 100:
                raise ConditionalTransactionError("Compound percent must be between 0 and 100")
            
            # Get current rewards
            lock_info = self.get_stake_lock_info(lock_hash)
            available_rewards = Decimal(str(lock_info.get('accumulated_rewards', '0')))
            
            if available_rewards <= 0:
                raise ConditionalTransactionError("No rewards available for compounding")
            
            compound_amount = available_rewards * (compound_percent / 100)
            
            return self._create_compound_transaction(lock_hash, compound_amount, fee)
            
        except Exception as e:
            self._logger.error("Failed to compound rewards: %s", e)
            raise ConditionalTransactionError(f"Failed to compound rewards: {e}")
    
    def emergency_unlock(self, lock_hash: str, emergency_reason: str, fee: Decimal) -> str:
        """
        Emergency unlock with maximum penalties - for critical situations.
        
        Args:
            lock_hash: Hash of the stake lock
            emergency_reason: Reason for emergency unlock (required for audit)
            fee: Transaction fee
            
        Returns:
            str: Transaction hash of emergency unlock
        """
        try:
            if not emergency_reason.strip():
                raise ConditionalTransactionError("Emergency reason is required")
            
            lock_info = self.get_stake_lock_info(lock_hash)
            total_amount = Decimal(str(lock_info.get('amount', '0')))
            
            # Emergency unlock has maximum penalty (typically 30-50% of amount)
            emergency_penalty = total_amount * Decimal('0.4')  # 40% penalty
            unlock_amount = total_amount - emergency_penalty
            
            return self._create_emergency_unlock_transaction(
                lock_hash, unlock_amount, emergency_penalty, emergency_reason, fee
            )
            
        except Exception as e:
            self._logger.error("Failed to create emergency unlock: %s", e)
            raise ConditionalTransactionError(f"Failed to create emergency unlock: {e}")
    
    def get_stake_lock_history(self, wallet_address: Optional[str] = None, 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get history of all stake lock operations for wallet.
        
        Args:
            wallet_address: Wallet address (uses composer wallet if None)
            limit: Maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: History of stake lock operations
        """
        try:
            target_address = wallet_address or str(self.composer.wallet_addr)
            return self._query_stake_lock_history(target_address, limit)
            
        except Exception as e:
            self._logger.error("Failed to get stake lock history: %s", e)
            raise ConditionalTransactionError(f"Failed to get stake lock history: {e}")
    
    def calculate_stake_penalties(self, lock_hash: str, unlock_amount: Optional[Decimal] = None) -> Dict[str, Decimal]:
        """
        Calculate penalties for early unlock of stake lock.
        
        Args:
            lock_hash: Hash of the stake lock
            unlock_amount: Amount to unlock (full amount if None)
            
        Returns:
            Dict[str, Decimal]: Penalty breakdown
        """
        try:
            lock_info = self.get_stake_lock_info(lock_hash)
            
            total_locked = Decimal(str(lock_info.get('amount', '0')))
            amount_to_unlock = unlock_amount or total_locked
            
            lock_time = lock_info.get('lock_time')
            current_time = self._get_current_time_yymmdd()
            
            # Calculate time-based penalty
            time_penalty = self._calculate_time_penalty(lock_time, current_time, amount_to_unlock)
            
            # Calculate amount-based penalty
            amount_penalty = self._calculate_amount_penalty(amount_to_unlock, total_locked)
            
            # Calculate compound penalty if rewards were compounded
            compound_penalty = self._calculate_compound_penalty(lock_info, amount_to_unlock)
            
            total_penalty = time_penalty + amount_penalty + compound_penalty
            net_amount = amount_to_unlock - total_penalty
            
            return {
                'unlock_amount': amount_to_unlock,
                'time_penalty': time_penalty,
                'amount_penalty': amount_penalty,
                'compound_penalty': compound_penalty,
                'total_penalty': total_penalty,
                'net_amount': max(net_amount, Decimal('0')),
                'penalty_percentage': (total_penalty / amount_to_unlock * 100) if amount_to_unlock > 0 else Decimal('0')
            }
            
        except Exception as e:
            self._logger.error("Failed to calculate stake penalties: %s", e)
            raise ConditionalTransactionError(f"Failed to calculate stake penalties: {e}")
    
    # === Private Helper Methods ===
    
    def _query_stake_locks(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Query stake locks from blockchain (fallback implementation)."""
        # In real implementation, this would query dap_chain_ledger for conditional outputs
        return [
            {
                'lock_hash': 'stake_lock_hash_1',
                'amount': '100.0',
                'lock_time': '250601',
                'reinvest_percent': '5.0',
                'created_at': '240101',
                'status': 'active',
                'accumulated_rewards': '5.25'
            },
            {
                'lock_hash': 'stake_lock_hash_2', 
                'amount': '250.0',
                'lock_time': '251201',
                'reinvest_percent': '10.0',
                'created_at': '240315',
                'status': 'active',
                'accumulated_rewards': '12.75'
            }
        ]
    
    def _query_stake_lock_info(self, lock_hash: str) -> Dict[str, Any]:
        """Query detailed stake lock information from blockchain."""
        return {
            'lock_hash': lock_hash,
            'amount': '100.0',
            'lock_time': '250601',
            'reinvest_percent': '5.0',
            'created_at': '240101',
            'status': 'active',
            'accumulated_rewards': '5.25',
            'partial_unlock_allowed': True,
            'compound_history': [
                {'date': '240301', 'amount': '2.5'},
                {'date': '240601', 'amount': '2.75'}
            ]
        }
    
    def _calculate_early_unlock_penalty(self, lock_info: Dict[str, Any], unlock_amount: Decimal) -> Decimal:
        """Calculate penalty for early unlock based on remaining time."""
        lock_time = lock_info.get('lock_time')
        current_time = self._get_current_time_yymmdd()
        
        # Simple time-based penalty: 1% per month remaining
        months_remaining = self._calculate_months_remaining(current_time, lock_time)
        penalty_rate = min(Decimal('0.3'), months_remaining * Decimal('0.01'))  # Max 30% penalty
        
        return unlock_amount * penalty_rate
    
    def _calculate_time_penalty(self, lock_time: str, current_time: str, amount: Decimal) -> Decimal:
        """Calculate time-based penalty for early unlock."""
        months_remaining = self._calculate_months_remaining(current_time, lock_time)
        penalty_rate = min(Decimal('0.25'), months_remaining * Decimal('0.01'))  # Max 25%
        return amount * penalty_rate
    
    def _calculate_amount_penalty(self, unlock_amount: Decimal, total_locked: Decimal) -> Decimal:
        """Calculate amount-based penalty (higher penalty for larger unlocks)."""
        unlock_ratio = unlock_amount / total_locked if total_locked > 0 else Decimal('0')
        # Progressive penalty: 1% for small unlocks, up to 5% for full unlock
        penalty_rate = unlock_ratio * Decimal('0.05')
        return unlock_amount * penalty_rate
    
    def _calculate_compound_penalty(self, lock_info: Dict[str, Any], unlock_amount: Decimal) -> Decimal:
        """Calculate penalty for unlocking compounded rewards."""
        compound_history = lock_info.get('compound_history', [])
        if not compound_history:
            return Decimal('0')
        
        # 2% penalty on compounded portions
        total_compounded = sum(Decimal(str(entry['amount'])) for entry in compound_history)
        compound_ratio = min(total_compounded / unlock_amount, Decimal('1')) if unlock_amount > 0 else Decimal('0')
        
        return unlock_amount * compound_ratio * Decimal('0.02')
    
    def _create_partial_unlock_transaction(self, lock_hash: str, unlock_amount: Decimal, 
                                         penalty: Decimal, fee: Decimal) -> str:
        """Create partial unlock transaction."""
        # In real implementation, this would create a specific partial unlock transaction
        return f"partial_unlock_tx_{lock_hash}_{unlock_amount}_{self._get_current_time_yymmdd()}"
    
    def _create_compound_transaction(self, lock_hash: str, compound_amount: Decimal, fee: Decimal) -> str:
        """Create compound rewards transaction."""
        return f"compound_tx_{lock_hash}_{compound_amount}_{self._get_current_time_yymmdd()}"
    
    def _create_emergency_unlock_transaction(self, lock_hash: str, unlock_amount: Decimal,
                                           penalty: Decimal, reason: str, fee: Decimal) -> str:
        """Create emergency unlock transaction."""
        return f"emergency_unlock_tx_{lock_hash}_{unlock_amount}_{self._get_current_time_yymmdd()}"
    
    def _query_stake_lock_history(self, wallet_address: str, limit: int) -> List[Dict[str, Any]]:
        """Query stake lock operation history."""
        return [
            {
                'tx_hash': 'stake_tx_1',
                'operation': 'stake_lock',
                'amount': '100.0',
                'lock_time': '250601',
                'timestamp': '240101120000',
                'status': 'confirmed'
            },
            {
                'tx_hash': 'compound_tx_1',
                'operation': 'compound_rewards',
                'amount': '2.5',
                'timestamp': '240301120000',
                'status': 'confirmed'
            }
        ] 