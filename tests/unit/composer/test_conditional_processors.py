"""
Unit tests for Conditional Processors
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../python-cellframe'))

try:
    from cellframe.composer.cond.stake_lock import StakeLockProcessor
    from cellframe.composer.cond.exchange import ExchangeProcessor
    from cellframe.composer.cond.voting import VotingProcessor
    from cellframe.composer.cond.delegation import DelegationProcessor
    from cellframe.composer.cond.base import BaseConditionalProcessor
    from cellframe.composer.exceptions import ConditionalError
except ImportError:
    # For testing without actual SDK
    StakeLockProcessor = Mock
    ExchangeProcessor = Mock
    VotingProcessor = Mock
    DelegationProcessor = Mock
    BaseConditionalProcessor = Mock
    ConditionalError = Exception


@pytest.mark.unit
@pytest.mark.conditional
class TestStakeLockProcessor:
    """Test cases for StakeLock conditional processor"""

    @pytest.fixture
    def stake_processor(self, mock_cellframe_sdk):
        """Create StakeLockProcessor instance"""
        with patch('cellframe.composer.cond.stake_lock.dap_chain_wallet_open'):
            processor = StakeLockProcessor("testnet", "test_wallet")
            return processor

    @pytest.mark.mock_only
    def test_create_stake_lock(self, stake_processor, conditional_processor_fixtures):
        """Test creating stake lock transaction"""
        stake_data = conditional_processor_fixtures["stake_lock"]
        
        with patch.object(stake_processor, '_validate_stake_params', return_value=True), \
             patch.object(stake_processor, '_build_stake_lock_tx') as mock_build:
            
            mock_build.return_value = {"tx_hash": "stake_hash", "locked_amount": 1000.0}
            
            result = stake_processor.create_stake_lock(
                amount=stake_data["amount"],
                duration=stake_data["duration"],
                auto_prolong=stake_data["auto_prolong"]
            )
            
            assert result["tx_hash"] == "stake_hash"
            assert result["locked_amount"] == 1000.0

    @pytest.mark.mock_only
    def test_calculate_stake_penalties(self, stake_processor):
        """Test stake penalty calculation"""
        with patch.object(stake_processor, '_get_lock_info') as mock_info:
            mock_info.return_value = {
                "locked_amount": 1000.0,
                "lock_time": 1000000,  # timestamp
                "duration": 30,  # days
                "penalty_rate": 0.1
            }
            
            penalties = stake_processor.calculate_stake_penalties("test_lock_id")
            
            assert "time_penalty" in penalties
            assert "amount_penalty" in penalties
            assert "total_penalty" in penalties
            assert penalties["total_penalty"] >= 0

    @pytest.mark.mock_only
    def test_partial_unlock(self, stake_processor):
        """Test partial stake unlock with penalties"""
        with patch.object(stake_processor, '_get_lock_info') as mock_info, \
             patch.object(stake_processor, '_build_unlock_tx') as mock_unlock:
            
            mock_info.return_value = {
                "locked_amount": 1000.0,
                "available_amount": 800.0
            }
            mock_unlock.return_value = {
                "tx_hash": "unlock_hash",
                "unlocked_amount": 500.0,
                "penalty_applied": 50.0
            }
            
            result = stake_processor.partial_unlock("test_lock_id", 500.0)
            
            assert result["unlocked_amount"] == 500.0
            assert result["penalty_applied"] == 50.0

    @pytest.mark.mock_only
    def test_compound_rewards(self, stake_processor):
        """Test compounding stake rewards"""
        with patch.object(stake_processor, '_get_rewards_info') as mock_rewards, \
             patch.object(stake_processor, '_build_compound_tx') as mock_compound:
            
            mock_rewards.return_value = {"available_rewards": 100.0}
            mock_compound.return_value = {
                "tx_hash": "compound_hash",
                "compounded_amount": 100.0,
                "new_stake_amount": 1100.0
            }
            
            result = stake_processor.compound_rewards("test_lock_id")
            
            assert result["compounded_amount"] == 100.0
            assert result["new_stake_amount"] == 1100.0


@pytest.mark.unit
@pytest.mark.conditional
class TestExchangeProcessor:
    """Test cases for Exchange conditional processor"""

    @pytest.fixture
    def exchange_processor(self, mock_cellframe_sdk):
        """Create ExchangeProcessor instance"""
        with patch('cellframe.composer.cond.exchange.dap_chain_wallet_open'):
            processor = ExchangeProcessor("testnet", "test_wallet")
            return processor

    @pytest.mark.mock_only
    def test_create_limit_order(self, exchange_processor, conditional_processor_fixtures):
        """Test creating limit order"""
        exchange_data = conditional_processor_fixtures["exchange"]
        
        with patch.object(exchange_processor, '_validate_order_params', return_value=True), \
             patch.object(exchange_processor, '_build_limit_order_tx') as mock_build:
            
            mock_build.return_value = {
                "tx_hash": "order_hash",
                "order_id": "order_123",
                "order_type": "limit"
            }
            
            result = exchange_processor.create_limit_order(
                token_from=exchange_data["token_from"],
                token_to=exchange_data["token_to"],
                amount=exchange_data["amount"],
                rate=exchange_data["rate"]
            )
            
            assert result["order_id"] == "order_123"
            assert result["order_type"] == "limit"

    @pytest.mark.mock_only
    def test_create_market_order(self, exchange_processor, conditional_processor_fixtures):
        """Test creating market order"""
        exchange_data = conditional_processor_fixtures["exchange"]
        
        with patch.object(exchange_processor, '_get_market_rate', return_value=0.0001), \
             patch.object(exchange_processor, '_build_market_order_tx') as mock_build:
            
            mock_build.return_value = {
                "tx_hash": "market_hash",
                "order_id": "market_123",
                "executed_rate": 0.0001
            }
            
            result = exchange_processor.create_market_order(
                token_from=exchange_data["token_from"],
                token_to=exchange_data["token_to"],
                amount=exchange_data["amount"]
            )
            
            assert result["executed_rate"] == 0.0001

    @pytest.mark.mock_only
    def test_cancel_order(self, exchange_processor):
        """Test canceling exchange order"""
        with patch.object(exchange_processor, '_validate_order_exists', return_value=True), \
             patch.object(exchange_processor, '_build_cancel_order_tx') as mock_cancel:
            
            mock_cancel.return_value = {
                "tx_hash": "cancel_hash",
                "cancelled_order_id": "order_123",
                "refunded_amount": 100.0
            }
            
            result = exchange_processor.cancel_order("order_123")
            
            assert result["cancelled_order_id"] == "order_123"
            assert result["refunded_amount"] == 100.0

    @pytest.mark.mock_only
    def test_get_order_history(self, exchange_processor):
        """Test getting order history"""
        with patch.object(exchange_processor, '_fetch_order_history') as mock_history:
            mock_history.return_value = [
                {"order_id": "order_1", "status": "completed"},
                {"order_id": "order_2", "status": "cancelled"}
            ]
            
            history = exchange_processor.get_order_history(limit=10)
            
            assert len(history) == 2
            assert history[0]["order_id"] == "order_1"


@pytest.mark.unit
@pytest.mark.conditional
class TestVotingProcessor:
    """Test cases for Voting conditional processor"""

    @pytest.fixture
    def voting_processor(self, mock_cellframe_sdk):
        """Create VotingProcessor instance"""
        with patch('cellframe.composer.cond.voting.dap_chain_wallet_open'):
            processor = VotingProcessor("testnet", "test_wallet")
            return processor

    @pytest.mark.mock_only
    def test_create_vote(self, voting_processor, conditional_processor_fixtures):
        """Test creating vote transaction"""
        voting_data = conditional_processor_fixtures["voting"]
        
        with patch.object(voting_processor, '_validate_proposal_exists', return_value=True), \
             patch.object(voting_processor, '_validate_voting_power', return_value=True), \
             patch.object(voting_processor, '_build_vote_tx') as mock_vote:
            
            mock_vote.return_value = {
                "tx_hash": "vote_hash",
                "proposal_id": "test_proposal",
                "vote": "yes",
                "weight": 100.0
            }
            
            result = voting_processor.create_vote(
                proposal_id=voting_data["proposal_id"],
                vote=voting_data["vote"],
                weight=voting_data["weight"]
            )
            
            assert result["proposal_id"] == "test_proposal"
            assert result["vote"] == "yes"

    @pytest.mark.mock_only
    def test_create_proposal(self, voting_processor):
        """Test creating governance proposal"""
        proposal_data = {
            "title": "Test Proposal",
            "description": "Test proposal description",
            "voting_period": 30,  # days
            "quorum_required": 0.5
        }
        
        with patch.object(voting_processor, '_validate_proposal_params', return_value=True), \
             patch.object(voting_processor, '_build_proposal_tx') as mock_proposal:
            
            mock_proposal.return_value = {
                "tx_hash": "proposal_hash",
                "proposal_id": "new_proposal_123",
                "voting_deadline": 1234567890
            }
            
            result = voting_processor.create_proposal(**proposal_data)
            
            assert result["proposal_id"] == "new_proposal_123"

    @pytest.mark.mock_only
    def test_get_voting_power(self, voting_processor):
        """Test getting wallet voting power"""
        with patch.object(voting_processor, '_calculate_voting_power') as mock_power:
            mock_power.return_value = 150.0
            
            power = voting_processor.get_voting_power()
            
            assert power == 150.0


@pytest.mark.unit
@pytest.mark.conditional  
class TestDelegationProcessor:
    """Test cases for Delegation conditional processor"""

    @pytest.fixture
    def delegation_processor(self, mock_cellframe_sdk):
        """Create DelegationProcessor instance"""
        with patch('cellframe.composer.cond.delegation.dap_chain_wallet_open'):
            processor = DelegationProcessor("testnet", "test_wallet")
            return processor

    @pytest.mark.mock_only
    def test_create_delegation(self, delegation_processor, conditional_processor_fixtures):
        """Test creating delegation transaction"""
        delegation_data = conditional_processor_fixtures["delegation"]
        
        with patch.object(delegation_processor, '_validate_validator', return_value=True), \
             patch.object(delegation_processor, '_validate_delegation_params', return_value=True), \
             patch.object(delegation_processor, '_build_delegation_tx') as mock_delegate:
            
            mock_delegate.return_value = {
                "tx_hash": "delegate_hash",
                "validator": "test_validator",
                "delegated_amount": 500.0,
                "expected_rewards": 50.0
            }
            
            result = delegation_processor.create_delegation(
                validator=delegation_data["validator"],
                amount=delegation_data["amount"],
                duration=delegation_data["duration"]
            )
            
            assert result["validator"] == "test_validator"
            assert result["delegated_amount"] == 500.0

    @pytest.mark.mock_only
    def test_undelegate(self, delegation_processor):
        """Test undelegating from validator"""
        with patch.object(delegation_processor, '_validate_delegation_exists', return_value=True), \
             patch.object(delegation_processor, '_build_undelegate_tx') as mock_undelegate:
            
            mock_undelegate.return_value = {
                "tx_hash": "undelegate_hash",
                "undelegated_amount": 500.0,
                "rewards_claimed": 25.0
            }
            
            result = delegation_processor.undelegate("test_validator", 500.0)
            
            assert result["undelegated_amount"] == 500.0
            assert result["rewards_claimed"] == 25.0

    @pytest.mark.mock_only
    def test_claim_delegation_rewards(self, delegation_processor):
        """Test claiming delegation rewards"""
        with patch.object(delegation_processor, '_get_delegation_rewards') as mock_rewards, \
             patch.object(delegation_processor, '_build_claim_rewards_tx') as mock_claim:
            
            mock_rewards.return_value = {"available_rewards": 75.0}
            mock_claim.return_value = {
                "tx_hash": "claim_hash",
                "claimed_rewards": 75.0
            }
            
            result = delegation_processor.claim_rewards("test_validator")
            
            assert result["claimed_rewards"] == 75.0

    @pytest.mark.mock_only
    def test_get_delegations_info(self, delegation_processor):
        """Test getting delegation information"""
        with patch.object(delegation_processor, '_fetch_delegations_info') as mock_info:
            mock_info.return_value = [
                {
                    "validator": "validator_1",
                    "delegated_amount": 500.0,
                    "rewards": 25.0,
                    "status": "active"
                },
                {
                    "validator": "validator_2", 
                    "delegated_amount": 300.0,
                    "rewards": 15.0,
                    "status": "active"
                }
            ]
            
            delegations = delegation_processor.get_delegations_info()
            
            assert len(delegations) == 2
            assert delegations[0]["validator"] == "validator_1"


@pytest.mark.unit
@pytest.mark.conditional
class TestBaseConditionalProcessor:
    """Test cases for BaseConditionalProcessor abstract class"""

    @pytest.mark.mock_only
    def test_base_processor_interface(self):
        """Test that BaseConditionalProcessor defines required interface"""
        required_methods = [
            '_validate_network',
            '_validate_wallet', 
            '_build_conditional_tx',
            'get_supported_conditions'
        ]
        
        for method in required_methods:
            assert hasattr(BaseConditionalProcessor, method)

    @pytest.mark.mock_only
    def test_base_processor_cannot_be_instantiated(self):
        """Test that BaseConditionalProcessor cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseConditionalProcessor("testnet", "test_wallet") 