"""
🗳️ Voting Conditional Processor

Specialized processor for voting conditional transactions.
Handles proposal creation, voting, and governance operations.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional

from .base import BaseConditionalProcessor
from ..core import TransactionOutput
from ..exceptions import ConditionalTransactionError
from ...chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class VotingProcessor(BaseConditionalProcessor):
    """
    🗳️ Voting Conditional Processor
    
    Handles voting and governance operations:
    - Voting proposal creation with options and expiration
    - Vote casting on existing proposals
    - Voting history and statistics
    - Governance parameter queries
    """
    
    def get_transaction_type(self):
        """Get the transaction type handled by this processor."""
        return TransactionType.SRV_VOTING
    
    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """Validate voting condition parameters."""
        # Different validation for proposals vs votes
        if 'question' in kwargs:
            # Creating a voting proposal
            required = ['question', 'options', 'max_votes']
            self._validate_required_params(required, **kwargs)
            
            return {
                'question': kwargs['question'],
                'options': kwargs['options'],
                'max_votes': int(kwargs['max_votes']),
                'expire_time': kwargs.get('expire_time'),
                'delegated_key_required': kwargs.get('delegated_key_required', False),
                'vote_changing_allowed': kwargs.get('vote_changing_allowed', False)
            }
        elif 'voting_hash' in kwargs:
            # Casting a vote
            required = ['voting_hash', 'vote_option']
            self._validate_required_params(required, **kwargs)
            
            return {
                'voting_hash': kwargs['voting_hash'],
                'vote_option': kwargs['vote_option'],
                'vote_weight': kwargs.get('vote_weight', 1)
            }
        else:
            raise ConditionalTransactionError("Either 'question' (for proposals) or 'voting_hash' (for votes) must be provided")
    
    def create_conditional_output(self, value: Decimal, condition_params: Dict[str, Any]) -> TransactionOutput:
        """Create voting conditional output."""
        if 'question' in condition_params:
            # Voting proposal output
            return TransactionOutput(
                address=None,  # Voting is system-wide
                value=value,
                token_ticker=self.composer._get_native_ticker(),
                output_type="conditional_voting_proposal",
                conditions={
                    'question': condition_params['question'],
                    'options': condition_params['options'],
                    'max_votes': condition_params['max_votes'],
                    'expire_time': condition_params.get('expire_time'),
                    'delegated_key_required': condition_params['delegated_key_required'],
                    'vote_changing_allowed': condition_params['vote_changing_allowed']
                }
            )
        else:
            # Vote casting output
            return TransactionOutput(
                address=None,  # Voting is system-wide
                value=value,
                token_ticker=self.composer._get_native_ticker(),
                output_type="conditional_vote",
                conditions={
                    'voting_hash': condition_params['voting_hash'],
                    'vote_option': condition_params['vote_option'],
                    'vote_weight': condition_params.get('vote_weight', 1)
                }
            )
    
    # === Convenience Methods ===
    
    def create_voting_proposal(self, question: str, options: List[str], 
                             max_votes: int, fee: Decimal,
                             expire_time: Optional[int] = None) -> str:
        """
        Create voting proposal (conditional transaction).
        
        Args:
            question: Voting question
            options: List of voting options
            max_votes: Maximum number of votes
            fee: Transaction fee
            expire_time: Voting expiration time (optional)
            
        Returns:
            str: Transaction hash
        """
        return self.create_conditional_transaction(
            value=Decimal("0"),  # Voting proposals don't require value
            fee=fee,
            question=question,
            options=options,
            max_votes=max_votes,
            expire_time=expire_time
        )
    
    def create_vote_transaction(self, voting_hash: str, vote_option: str, fee: Decimal,
                               vote_weight: Optional[int] = None) -> str:
        """
        Create vote transaction for existing proposal.
        
        Args:
            voting_hash: Hash of voting proposal to vote on
            vote_option: Selected voting option
            fee: Transaction fee
            vote_weight: Vote weight (optional, defaults to 1)
            
        Returns:
            str: Transaction hash
        """
        return self.create_conditional_transaction(
            value=Decimal("0"),  # Voting doesn't require value
            fee=fee,
            voting_hash=voting_hash,
            vote_option=vote_option,
            vote_weight=vote_weight or 1
        )
    
    def create_simple_voting(self, question: str, yes_no: bool = True, 
                           max_votes: int = 1000, fee: Decimal = Decimal("0.01")) -> str:
        """
        Create simple yes/no or approve/reject voting.
        
        Args:
            question: Voting question
            yes_no: If True, creates Yes/No options, otherwise Approve/Reject
            max_votes: Maximum number of votes
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        options = ['Yes', 'No'] if yes_no else ['Approve', 'Reject']
        
        return self.create_voting_proposal(
            question=question,
            options=options,
            max_votes=max_votes,
            fee=fee
        )
    
    def create_multiple_choice_voting(self, question: str, choices: List[str],
                                    max_votes: int = 1000, fee: Decimal = Decimal("0.01")) -> str:
        """
        Create multiple choice voting.
        
        Args:
            question: Voting question
            choices: List of choices
            max_votes: Maximum number of votes
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        return self.create_voting_proposal(
            question=question,
            options=choices,
            max_votes=max_votes,
            fee=fee
        )
    
    def get_voting_proposals(self, status: str = "active") -> List[Dict[str, Any]]:
        """
        Get voting proposals by status.
        
        Args:
            status: Proposal status ("active", "completed", "expired", "all")
            
        Returns:
            List[Dict[str, Any]]: List of voting proposals
        """
        try:
            return self._query_voting_proposals(status)
            
        except Exception as e:
            self._logger.error("Failed to get voting proposals: %s", e)
            raise ConditionalTransactionError(f"Failed to get voting proposals: {e}")
    
    def get_voting_results(self, voting_hash: str) -> Dict[str, Any]:
        """
        Get results for specific voting proposal.
        
        Args:
            voting_hash: Hash of the voting proposal
            
        Returns:
            Dict[str, Any]: Voting results and statistics
        """
        try:
            return self._query_voting_results(voting_hash)
            
        except Exception as e:
            self._logger.error("Failed to get voting results: %s", e)
            raise ConditionalTransactionError(f"Failed to get voting results: {e}")
    
    def get_user_votes(self, wallet_address: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all votes cast by a wallet.
        
        Args:
            wallet_address: Wallet address (uses composer wallet if None)
            
        Returns:
            List[Dict[str, Any]]: List of votes cast
        """
        try:
            target_address = wallet_address or str(self.composer.wallet_addr)
            return self._query_user_votes(target_address)
            
        except Exception as e:
            self._logger.error("Failed to get user votes: %s", e)
            raise ConditionalTransactionError(f"Failed to get user votes: {e}")
    
    # === Private Helper Methods ===
    
    def _query_voting_proposals(self, status: str) -> List[Dict[str, Any]]:
        """Query voting proposals from blockchain."""
        # In real implementation, this would query the voting service
        proposals = [
            {
                'voting_hash': 'voting_proposal_1',
                'question': 'Should we increase the block size?',
                'options': ['Yes', 'No'],
                'max_votes': 1000,
                'current_votes': 450,
                'status': 'active',
                'created_at': '240101',
                'expire_time': '250101',
                'creator': 'creator_address_1'
            },
            {
                'voting_hash': 'voting_proposal_2',
                'question': 'Which consensus algorithm should we use?',
                'options': ['PoS', 'PoW', 'DPoS'],
                'max_votes': 2000,
                'current_votes': 1750,
                'status': 'completed',
                'created_at': '230915',
                'completed_at': '231015',
                'creator': 'creator_address_2'
            }
        ]
        
        if status == "all":
            return proposals
        else:
            return [p for p in proposals if p['status'] == status]
    
    def _query_voting_results(self, voting_hash: str) -> Dict[str, Any]:
        """Query voting results for specific proposal."""
        return {
            'voting_hash': voting_hash,
            'question': 'Should we increase the block size?',
            'total_votes': 450,
            'results': {
                'Yes': {'votes': 280, 'percentage': 62.2},
                'No': {'votes': 170, 'percentage': 37.8}
            },
            'status': 'active',
            'quorum_reached': True,
            'winning_option': 'Yes',
            'created_at': '240101',
            'expire_time': '250101',
            'time_remaining': '45 days'
        }
    
    def _query_user_votes(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Query votes cast by specific wallet."""
        return [
            {
                'vote_hash': 'vote_tx_1',
                'voting_hash': 'voting_proposal_1',
                'vote_option': 'Yes',
                'vote_weight': 1,
                'timestamp': '240315',
                'status': 'confirmed'
            },
            {
                'vote_hash': 'vote_tx_2',
                'voting_hash': 'voting_proposal_2',
                'vote_option': 'PoS',
                'vote_weight': 1,
                'timestamp': '230920',
                'status': 'confirmed'
            }
        ] 