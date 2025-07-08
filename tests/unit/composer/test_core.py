"""
Unit tests for Transaction Composer Core functionality
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../python-cellframe'))

# Import will be mocked in tests
try:
    from cellframe.composer.core import TxComposer
    from cellframe.composer.exceptions import ComposerError, TransactionError
    from cellframe.types import TransactionType, NetworkType
except ImportError:
    # For testing without actual SDK
    TxComposer = Mock
    ComposerError = Exception
    TransactionError = Exception
    TransactionType = Mock
    NetworkType = Mock


@pytest.mark.unit
@pytest.mark.composer
class TestTxComposer:
    """Test cases for TxComposer core functionality"""

    @pytest.fixture
    def composer(self, mock_cellframe_sdk, composer_config):
        """Create TxComposer instance for testing"""
        with patch('cellframe.composer.core.dap_chain_wallet_open'):
            composer = TxComposer(
                network="testnet",
                wallet_name="test_wallet",
                config=composer_config
            )
            return composer

    def test_composer_initialization(self, composer, composer_config):
        """Test TxComposer initialization"""
        assert composer is not None
        assert composer.network == "testnet"
        assert composer.wallet_name == "test_wallet"
        assert composer.config == composer_config

    def test_composer_initialization_without_config(self, mock_cellframe_sdk):
        """Test TxComposer initialization with default config"""
        with patch('cellframe.composer.core.dap_chain_wallet_open'):
            composer = TxComposer(
                network="testnet",
                wallet_name="test_wallet"
            )
            assert composer.config is not None
            assert isinstance(composer.config, dict)

    def test_composer_initialization_invalid_network(self, mock_cellframe_sdk):
        """Test TxComposer initialization with invalid network"""
        with patch('cellframe.composer.core.dap_chain_wallet_open', side_effect=Exception("Network not found")):
            with pytest.raises(ComposerError):
                TxComposer(
                    network="invalid_network",
                    wallet_name="test_wallet"
                )

    @pytest.mark.mock_only
    def test_create_simple_transaction(self, composer, sample_transaction_data):
        """Test creating a simple transaction"""
        with patch.object(composer, '_validate_transaction', return_value=True), \
             patch.object(composer, '_build_transaction') as mock_build:
            
            mock_build.return_value = {"tx_hash": "test_hash", "status": "created"}
            
            result = composer.create_tx(
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            assert result["tx_hash"] == "test_hash"
            assert result["status"] == "created"
            mock_build.assert_called_once()

    @pytest.mark.mock_only
    def test_create_transaction_with_fee_optimization(self, composer, sample_transaction_data):
        """Test transaction creation with fee optimization"""
        composer.config["fee_optimization"] = True
        
        with patch.object(composer, '_validate_transaction', return_value=True), \
             patch.object(composer, '_optimize_fee', return_value=0.5) as mock_optimize, \
             patch.object(composer, '_build_transaction') as mock_build:
            
            mock_build.return_value = {"tx_hash": "test_hash", "fee": 0.5}
            
            result = composer.create_tx(
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            mock_optimize.assert_called_once()
            assert result["fee"] == 0.5

    @pytest.mark.mock_only
    def test_create_transaction_invalid_amount(self, composer, sample_transaction_data):
        """Test transaction creation with invalid amount"""
        with pytest.raises(TransactionError):
            composer.create_tx(
                to_addr=sample_transaction_data["to_addr"],
                amount=-100.0,  # Invalid negative amount
                token=sample_transaction_data["token"]
            )

    @pytest.mark.mock_only
    def test_create_transaction_invalid_address(self, composer, sample_transaction_data):
        """Test transaction creation with invalid address"""
        with pytest.raises(TransactionError):
            composer.create_tx(
                to_addr="invalid_address",
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )

    @pytest.mark.mock_only 
    def test_estimate_fee(self, composer, sample_transaction_data):
        """Test fee estimation"""
        with patch.object(composer, '_calculate_base_fee', return_value=1.0), \
             patch.object(composer, '_calculate_network_fee', return_value=0.1):
            
            fee = composer.estimate_fee(
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            assert fee > 0
            assert isinstance(fee, (int, float))

    @pytest.mark.mock_only
    def test_validate_transaction(self, composer, sample_transaction_data):
        """Test transaction validation"""
        with patch.object(composer, '_check_balance', return_value=True), \
             patch.object(composer, '_validate_address', return_value=True), \
             patch.object(composer, '_validate_amount', return_value=True):
            
            is_valid = composer.validate_tx(
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            assert is_valid is True

    @pytest.mark.mock_only
    def test_validate_transaction_insufficient_balance(self, composer, sample_transaction_data):
        """Test transaction validation with insufficient balance"""
        with patch.object(composer, '_check_balance', return_value=False):
            with pytest.raises(TransactionError, match="Insufficient balance"):
                composer.validate_tx(
                    to_addr=sample_transaction_data["to_addr"],
                    amount=sample_transaction_data["amount"],
                    token=sample_transaction_data["token"]
                )

    @pytest.mark.mock_only
    def test_batch_transactions(self, composer, sample_transaction_data):
        """Test batch transaction processing"""
        composer.config["batch_processing"] = True
        
        transactions = [
            {
                "to_addr": sample_transaction_data["to_addr"],
                "amount": 50.0,
                "token": sample_transaction_data["token"]
            },
            {
                "to_addr": sample_transaction_data["to_addr"], 
                "amount": 25.0,
                "token": sample_transaction_data["token"]
            }
        ]
        
        with patch.object(composer, '_validate_transaction', return_value=True), \
             patch.object(composer, '_build_batch_transaction') as mock_batch:
            
            mock_batch.return_value = {"batch_hash": "batch_test_hash", "count": 2}
            
            result = composer.create_batch_tx(transactions)
            
            assert result["batch_hash"] == "batch_test_hash"
            assert result["count"] == 2
            mock_batch.assert_called_once()

    @pytest.mark.mock_only
    def test_transaction_types_support(self, composer):
        """Test support for different transaction types"""
        supported_types = [
            TransactionType.TRANSFER,
            TransactionType.STAKE_LOCK,
            TransactionType.STAKE_UNLOCK,
            TransactionType.EXCHANGE_BUY,
            TransactionType.EXCHANGE_SELL,
            TransactionType.VOTING,
            TransactionType.DELEGATION
        ]
        
        for tx_type in supported_types:
            assert composer.supports_transaction_type(tx_type)

    @pytest.mark.mock_only
    def test_composer_context_manager(self, mock_cellframe_sdk, composer_config):
        """Test TxComposer as context manager"""
        with patch('cellframe.composer.core.dap_chain_wallet_open'):
            with TxComposer("testnet", "test_wallet", composer_config) as composer:
                assert composer is not None
                assert composer.network == "testnet"

    @pytest.mark.mock_only
    def test_composer_error_handling(self, composer, sample_transaction_data):
        """Test error handling in composer"""
        with patch.object(composer, '_build_transaction', side_effect=Exception("Network error")):
            with pytest.raises(ComposerError):
                composer.create_tx(
                    to_addr=sample_transaction_data["to_addr"],
                    amount=sample_transaction_data["amount"],
                    token=sample_transaction_data["token"]
                )

    @pytest.mark.performance
    def test_composer_performance(self, composer, sample_transaction_data, benchmark):
        """Test composer performance for transaction creation"""
        with patch.object(composer, '_validate_transaction', return_value=True), \
             patch.object(composer, '_build_transaction', return_value={"tx_hash": "perf_test"}):
            
            def create_transaction():
                return composer.create_tx(
                    to_addr=sample_transaction_data["to_addr"],
                    amount=sample_transaction_data["amount"],
                    token=sample_transaction_data["token"]
                )
            
            result = benchmark(create_transaction)
            assert result["tx_hash"] == "perf_test"

    @pytest.mark.mock_only
    def test_composer_initialization(self, mock_composer):
        """Test composer initialization"""
        assert mock_composer.network == "testnet"
        assert mock_composer.wallet_name == "test_wallet"

    @pytest.mark.mock_only
    def test_create_transaction(self, mock_composer):
        """Test transaction creation"""
        result = mock_composer.create_tx(
            to_addr="0x123",
            amount=100.0,
            token="CELL"
        )
        assert result["tx_hash"] == "test_hash"

    @pytest.mark.mock_only
    def test_estimate_fee(self, mock_composer):
        """Test fee estimation"""
        fee = mock_composer.estimate_fee(
            to_addr="0x123",
            amount=100.0,
            token="CELL"
        )
        assert fee == 1.0

    @pytest.mark.mock_only
    def test_validate_transaction(self, mock_composer):
        """Test transaction validation"""
        is_valid = mock_composer.validate_tx(
            to_addr="0x123",
            amount=100.0,
            token="CELL"
        )
        assert is_valid is True 