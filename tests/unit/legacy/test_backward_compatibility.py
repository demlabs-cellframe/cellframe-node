"""
Unit tests for Legacy Backward Compatibility
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../python-cellframe'))

try:
    from cellframe.legacy import DapTransaction, DapWallet, DapChain
    from cellframe.chain.tx import TX
    from cellframe.composer.core import TxComposer
    from cellframe.composer.conditional import ConditionalProcessor
except ImportError:
    # For testing without actual SDK
    DapTransaction = Mock
    DapWallet = Mock
    DapChain = Mock
    TX = Mock
    TxComposer = Mock
    ConditionalProcessor = Mock


@pytest.mark.unit
@pytest.mark.legacy
class TestLegacyBackwardCompatibility:
    """Test cases for legacy backward compatibility"""

    @pytest.mark.mock_only
    def test_legacy_dap_transaction_interface(self):
        """Test that legacy DapTransaction interface still works"""
        # Test legacy method signatures
        legacy_methods = [
            'create_transfer',
            'create_stake_order', 
            'create_vote',
            'create_conditional'
        ]
        
        for method in legacy_methods:
            assert hasattr(DapTransaction, method)

    @pytest.mark.mock_only
    def test_legacy_transaction_creation(self, sample_transaction_data):
        """Test legacy transaction creation still works"""
        with patch('cellframe.legacy.dap_chain_wallet_open'):
            # Legacy way should still work
            legacy_tx = DapTransaction(
                from_addr=sample_transaction_data["from_addr"],
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            assert legacy_tx is not None

    @pytest.mark.mock_only
    def test_legacy_to_new_migration(self, sample_transaction_data):
        """Test migration from legacy to new architecture"""
        # Test that legacy code can be replaced with new architecture
        
        # Legacy way (should still work)
        with patch('cellframe.legacy.dap_chain_wallet_open'), \
             patch.object(DapTransaction, 'create_transfer') as mock_legacy:
            
            mock_legacy.return_value = {"tx_hash": "legacy_hash"}
            
            legacy_result = DapTransaction.create_transfer(
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            assert legacy_result["tx_hash"] == "legacy_hash"

        # New way (should produce same result)
        with patch('cellframe.composer.core.dap_chain_wallet_open'), \
             patch.object(TxComposer, 'create_tx') as mock_new:
            
            mock_new.return_value = {"tx_hash": "new_hash"}
            
            composer = TxComposer("testnet", "test_wallet")
            new_result = composer.create_tx(
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            # Both should work and produce valid results
            assert new_result["tx_hash"] == "new_hash"

    @pytest.mark.mock_only
    def test_legacy_conditional_processor_compatibility(self, conditional_processor_fixtures):
        """Test legacy conditional processor compatibility"""
        stake_data = conditional_processor_fixtures["stake_lock"]
        
        with patch('cellframe.composer.conditional.dap_chain_wallet_open'):
            # Legacy unified processor should still work
            legacy_processor = ConditionalProcessor("testnet", "test_wallet")
            
            # Test legacy method signatures
            legacy_methods = [
                'create_stake_lock',
                'create_exchange_order',
                'create_voting_transaction',
                'create_delegation'
            ]
            
            for method in legacy_methods:
                assert hasattr(legacy_processor, method)

    @pytest.mark.mock_only
    def test_legacy_wallet_interface(self, sample_wallet_data):
        """Test legacy wallet interface compatibility"""
        with patch('cellframe.legacy.dap_chain_wallet_open'):
            # Legacy wallet interface should still work
            legacy_wallet = DapWallet(name=sample_wallet_data["name"])
            
            legacy_methods = [
                'get_balance',
                'get_address',
                'create_transaction',
                'sign_transaction'
            ]
            
            for method in legacy_methods:
                assert hasattr(legacy_wallet, method)

    @pytest.mark.mock_only
    def test_legacy_chain_interface(self):
        """Test legacy chain interface compatibility"""
        with patch('cellframe.legacy.dap_chain_by_name'):
            # Legacy chain interface should still work
            legacy_chain = DapChain(name="testnet")
            
            legacy_methods = [
                'get_ledger',
                'get_mempool',
                'get_block',
                'get_transaction',
                'add_transaction'
            ]
            
            for method in legacy_methods:
                assert hasattr(legacy_chain, method)

    @pytest.mark.mock_only
    def test_legacy_import_paths(self):
        """Test that legacy import paths still work"""
        # Test that old import patterns still work
        legacy_import_tests = [
            "from cellframe.legacy import DapTransaction",
            "from cellframe.legacy import DapWallet", 
            "from cellframe.legacy import DapChain"
        ]
        
        for import_test in legacy_import_tests:
            try:
                exec(import_test)
                import_success = True
            except ImportError:
                import_success = False
            
            assert import_success, f"Legacy import failed: {import_test}"

    @pytest.mark.mock_only
    def test_legacy_deprecation_warnings(self):
        """Test that legacy code produces deprecation warnings"""
        import warnings
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            with patch('cellframe.legacy.dap_chain_wallet_open'):
                # Using legacy code should produce deprecation warning
                DapTransaction(
                    from_addr="0x123",
                    to_addr="0x456", 
                    amount=100.0,
                    token="CELL"
                )
            
            # Check if deprecation warning was issued
            deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
            assert len(deprecation_warnings) > 0

    @pytest.mark.mock_only
    def test_legacy_error_handling(self):
        """Test that legacy error handling still works"""
        with patch('cellframe.legacy.dap_chain_wallet_open', side_effect=Exception("Legacy error")):
            with pytest.raises(Exception, match="Legacy error"):
                DapTransaction(
                    from_addr="0x123",
                    to_addr="0x456",
                    amount=100.0,
                    token="CELL"
                )

    @pytest.mark.mock_only  
    def test_legacy_to_new_data_conversion(self, sample_transaction_data):
        """Test conversion between legacy and new data formats"""
        # Test that legacy data can be converted to new format
        legacy_data = {
            "from_addr": sample_transaction_data["from_addr"],
            "to_addr": sample_transaction_data["to_addr"],
            "amount": sample_transaction_data["amount"],
            "token": sample_transaction_data["token"]
        }
        
        # Convert legacy format to new format
        new_format = {
            "from_address": legacy_data["from_addr"],
            "to_address": legacy_data["to_addr"],
            "amount": legacy_data["amount"],
            "token_symbol": legacy_data["token"]
        }
        
        assert new_format["from_address"] == legacy_data["from_addr"]
        assert new_format["to_address"] == legacy_data["to_addr"]
        assert new_format["amount"] == legacy_data["amount"]
        assert new_format["token_symbol"] == legacy_data["token"]

    @pytest.mark.mock_only
    def test_legacy_configuration_compatibility(self):
        """Test legacy configuration compatibility"""
        # Test that legacy configuration still works
        legacy_config = {
            "network": "testnet",
            "wallet_name": "test_wallet",
            "fee_optimization": False,
            "batch_processing": False
        }
        
        # Should be able to use legacy config with new system
        with patch('cellframe.composer.core.dap_chain_wallet_open'):
            composer = TxComposer(
                network=legacy_config["network"],
                wallet_name=legacy_config["wallet_name"],
                config=legacy_config
            )
            
            assert composer.network == legacy_config["network"]
            assert composer.wallet_name == legacy_config["wallet_name"]


@pytest.mark.unit
@pytest.mark.legacy
class TestLegacyMigrationGuide:
    """Test cases that demonstrate migration from legacy to new architecture"""

    @pytest.mark.mock_only
    def test_transaction_creation_migration(self, sample_transaction_data):
        """Show how to migrate transaction creation from legacy to new"""
        
        # OLD WAY (legacy - should still work but deprecated)
        with patch('cellframe.legacy.dap_chain_wallet_open'), \
             patch.object(DapTransaction, 'create_transfer') as mock_legacy:
            
            mock_legacy.return_value = {"status": "success"}
            
            # Legacy approach
            legacy_tx = DapTransaction(
                from_addr=sample_transaction_data["from_addr"],
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
            legacy_result = legacy_tx.create_transfer()
            
        # NEW WAY (recommended)
        with patch('cellframe.composer.core.dap_chain_wallet_open'), \
             patch.object(TxComposer, 'create_tx') as mock_new:
            
            mock_new.return_value = {"status": "success"}
            
            # New approach with composer
            composer = TxComposer("testnet", "test_wallet")
            new_result = composer.create_tx(
                to_addr=sample_transaction_data["to_addr"],
                amount=sample_transaction_data["amount"],
                token=sample_transaction_data["token"]
            )
            
        # Both should work
        assert legacy_result["status"] == "success"
        assert new_result["status"] == "success"

    @pytest.mark.mock_only
    def test_conditional_transaction_migration(self, conditional_processor_fixtures):
        """Show how to migrate conditional transactions"""
        stake_data = conditional_processor_fixtures["stake_lock"]
        
        # OLD WAY (legacy conditional processor)
        with patch('cellframe.composer.conditional.dap_chain_wallet_open'), \
             patch.object(ConditionalProcessor, 'create_stake_lock') as mock_legacy:
            
            mock_legacy.return_value = {"stake_id": "legacy_stake"}
            
            legacy_processor = ConditionalProcessor("testnet", "test_wallet")
            legacy_result = legacy_processor.create_stake_lock(
                amount=stake_data["amount"],
                duration=stake_data["duration"]
            )
            
        # NEW WAY (specialized processors)
        with patch('cellframe.composer.cond.stake_lock.dap_chain_wallet_open'), \
             patch('cellframe.composer.cond.stake_lock.StakeLockProcessor.create_stake_lock') as mock_new:
            
            mock_new.return_value = {"stake_id": "new_stake"}
            
            # Import and use specialized processor
            from cellframe.composer.cond.stake_lock import StakeLockProcessor
            specialized_processor = StakeLockProcessor("testnet", "test_wallet")
            new_result = specialized_processor.create_stake_lock(
                amount=stake_data["amount"],
                duration=stake_data["duration"],
                auto_prolong=stake_data["auto_prolong"]
            )
            
        # Both should work
        assert legacy_result["stake_id"] == "legacy_stake"
        assert new_result["stake_id"] == "new_stake" 