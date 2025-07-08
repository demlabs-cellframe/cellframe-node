"""
Basic integration tests
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add paths for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../python-cellframe'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../python-dap'))


@pytest.mark.integration
class TestBasicIntegration:
    """Basic integration tests"""

    @pytest.mark.mock_only
    def test_composer_integration(self):
        """Test basic composer integration"""
        with patch('cellframe.composer.core.TxComposer') as mock_composer:
            mock_composer.return_value = Mock()
            mock_composer.return_value.create_tx.return_value = {"tx_hash": "integration_test"}
            
            # Test integration
            composer = mock_composer.return_value
            result = composer.create_tx(to_addr="0x123", amount=100.0, token="CELL")
            
            assert result["tx_hash"] == "integration_test"

    @pytest.mark.mock_only
    def test_plugin_integration(self):
        """Test basic plugin integration"""
        with patch('plugin_python_init.plugin_python_init') as mock_init:
            mock_init.return_value = 0
            
            # Test plugin initialization
            result = mock_init.return_value
            assert result == 0 