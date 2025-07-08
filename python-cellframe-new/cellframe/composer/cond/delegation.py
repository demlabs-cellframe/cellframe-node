"""
🤝 Delegation Conditional Processor

Specialized processor for delegation conditional transactions.
Handles stake delegation to validators and delegation rewards management.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List

from .base import BaseConditionalProcessor
from ..core import TransactionOutput
from ..exceptions import ConditionalTransactionError
from ...chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class DelegationProcessor(BaseConditionalProcessor):
    """
    🤝 Delegation Conditional Processor
    
    Handles delegation operations:
    - Stake delegation to validators
    - Delegation rewards tracking
    - Undelegation with cooldown periods
    - Validator performance monitoring
    """
    
    def get_transaction_type(self):
        """Get the transaction type handled by this processor."""
        return TransactionType.SRV_STAKE_POS_DELEGATE
    
    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """Validate delegation condition parameters."""
        required = ['signing_addr', 'node_addr']
        self._validate_required_params(required, **kwargs)
        
        return {
            'signing_addr': kwargs['signing_addr'],
            'node_addr': kwargs['node_addr'],
            'sovereign_addr': kwargs.get('sovereign_addr'),
            'sovereign_tax': kwargs.get('sovereign_tax', Decimal('0'))
        }
    
    def create_conditional_output(self, value: Decimal, condition_params: Dict[str, Any]) -> TransactionOutput:
        """Create delegation conditional output."""
        return TransactionOutput(
            address=condition_params['signing_addr'],
            value=value,
            token_ticker=self.composer._get_native_ticker(),
            output_type="conditional_delegation",
            conditions={
                'signing_addr': condition_params['signing_addr'],
                'node_addr': condition_params['node_addr'],
                'sovereign_addr': condition_params.get('sovereign_addr'),
                'sovereign_tax': condition_params.get('sovereign_tax')
            }
        )
    
    # === Convenience Methods ===
    
    def create_delegation(self, node_addr: str, amount: Decimal, fee: Decimal,
                         sovereign_addr: Optional[str] = None,
                         sovereign_tax: Optional[Decimal] = None) -> str:
        """
        Create delegation to validator node.
        
        Args:
            node_addr: Address of the validator node
            amount: Amount to delegate
            fee: Transaction fee
            sovereign_addr: Sovereign address (optional)
            sovereign_tax: Sovereign tax percentage (optional)
            
        Returns:
            str: Transaction hash
        """
        return self.create_conditional_transaction(
            value=amount,
            fee=fee,
            signing_addr=str(self.composer.wallet_addr),
            node_addr=node_addr,
            sovereign_addr=sovereign_addr,
            sovereign_tax=sovereign_tax or Decimal('0')
        )
    
    def create_undelegation(self, delegation_hash: str, amount: Decimal, fee: Decimal) -> str:
        """
        Create undelegation transaction.
        
        Args:
            delegation_hash: Hash of the original delegation
            amount: Amount to undelegate
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        try:
            # In real implementation, this would create an undelegation transaction
            return f"undelegate_tx_{delegation_hash}_{amount}_{self._get_current_time_yymmdd()}"
            
        except Exception as e:
            self._logger.error("Failed to create undelegation: %s", e)
            raise ConditionalTransactionError(f"Failed to create undelegation: {e}")
    
    def redelegate(self, current_node_addr: str, new_node_addr: str, 
                   amount: Decimal, fee: Decimal) -> str:
        """
        Redelegate stake from one validator to another.
        
        Args:
            current_node_addr: Current validator address
            new_node_addr: New validator address
            amount: Amount to redelegate
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        try:
            # In real implementation, this would handle redelegation logic
            return f"redelegate_tx_{current_node_addr}_to_{new_node_addr}_{amount}_{self._get_current_time_yymmdd()}"
            
        except Exception as e:
            self._logger.error("Failed to create redelegation: %s", e)
            raise ConditionalTransactionError(f"Failed to create redelegation: {e}")
    
    def claim_delegation_rewards(self, delegation_hash: str, fee: Decimal) -> str:
        """
        Claim accumulated delegation rewards.
        
        Args:
            delegation_hash: Hash of the delegation
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        try:
            # In real implementation, this would claim delegation rewards
            return f"claim_rewards_tx_{delegation_hash}_{self._get_current_time_yymmdd()}"
            
        except Exception as e:
            self._logger.error("Failed to claim delegation rewards: %s", e)
            raise ConditionalTransactionError(f"Failed to claim delegation rewards: {e}")
    
    def get_delegations(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all delegations for wallet.
        
        Args:
            wallet_address: Wallet address (uses composer wallet if None)
            
        Returns:
            Dict[str, Any]: Delegations information
        """
        try:
            target_address = wallet_address or str(self.composer.wallet_addr)
            return self._query_delegations(target_address)
            
        except Exception as e:
            self._logger.error("Failed to get delegations: %s", e)
            raise ConditionalTransactionError(f"Failed to get delegations: {e}")
    
    def get_delegation_rewards(self, delegation_hash: str) -> Dict[str, Any]:
        """
        Get accumulated rewards for specific delegation.
        
        Args:
            delegation_hash: Hash of the delegation
            
        Returns:
            Dict[str, Any]: Delegation rewards information
        """
        try:
            return self._query_delegation_rewards(delegation_hash)
            
        except Exception as e:
            self._logger.error("Failed to get delegation rewards: %s", e)
            raise ConditionalTransactionError(f"Failed to get delegation rewards: {e}")
    
    def get_validator_info(self, node_addr: str) -> Dict[str, Any]:
        """
        Get information about validator node.
        
        Args:
            node_addr: Address of the validator node
            
        Returns:
            Dict[str, Any]: Validator information
        """
        try:
            return self._query_validator_info(node_addr)
            
        except Exception as e:
            self._logger.error("Failed to get validator info: %s", e)
            raise ConditionalTransactionError(f"Failed to get validator info: {e}")
    
    def get_all_validators(self) -> List[Dict[str, Any]]:
        """
        Get list of all active validators.
        
        Returns:
            List[Dict[str, Any]]: List of validator information
        """
        try:
            return self._query_all_validators()
            
        except Exception as e:
            self._logger.error("Failed to get validators list: %s", e)
            raise ConditionalTransactionError(f"Failed to get validators list: {e}")
    
    # === Private Helper Methods ===
    
    def _query_delegations(self, wallet_address: str) -> Dict[str, Any]:
        """Query delegations from blockchain."""
        # In real implementation, this would query the delegation system
        return {
            'active_delegations': [
                {
                    'delegation_hash': 'delegation_1',
                    'node_addr': 'validator_node_1',
                    'amount': '1000.0',
                    'accumulated_rewards': '25.5',
                    'created_at': '240101',
                    'status': 'active',
                    'apr': '5.2%'
                }
            ],
            'undelegating': [
                {
                    'delegation_hash': 'delegation_2',
                    'node_addr': 'validator_node_2',
                    'amount': '500.0',
                    'completion_time': '240401',
                    'status': 'undelegating'
                }
            ],
            'total_delegated': '1000.0',
            'total_rewards': '25.5'
        }
    
    def _query_delegation_rewards(self, delegation_hash: str) -> Dict[str, Any]:
        """Query delegation rewards information."""
        return {
            'delegation_hash': delegation_hash,
            'accumulated_rewards': '25.5',
            'last_claim': '240201',
            'next_reward_date': '240401',
            'estimated_monthly_reward': '8.5',
            'current_apr': '5.2%',
            'can_claim': True,
            'min_claim_amount': '1.0'
        }
    
    def _query_validator_info(self, node_addr: str) -> Dict[str, Any]:
        """Query validator node information."""
        return {
            'node_addr': node_addr,
            'name': 'Cellframe Validator 1',
            'commission': '5.0%',
            'total_stake': '50000.0',
            'delegator_count': 125,
            'uptime': '99.8%',
            'apr': '5.2%',
            'status': 'active',
            'created_at': '230101',
            'last_activity': '240315',
            'slashing_events': 0
        }
    
    def _query_all_validators(self) -> List[Dict[str, Any]]:
        """Query all active validators."""
        return [
            {
                'node_addr': 'validator_node_1',
                'name': 'Cellframe Validator 1',
                'commission': '5.0%',
                'total_stake': '50000.0',
                'apr': '5.2%',
                'uptime': '99.8%',
                'status': 'active'
            },
            {
                'node_addr': 'validator_node_2',
                'name': 'Secure Validator',
                'commission': '3.0%',
                'total_stake': '75000.0',
                'apr': '4.8%',
                'uptime': '99.9%',
                'status': 'active'
            }
        ] 