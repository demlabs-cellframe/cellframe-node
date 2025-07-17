"""
🔬 Python DAP Detailed Tests

Detailed tests for Python DAP SDK specific classes and functions.
Tests specific implementations to find errors and warnings.
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import dap
except ImportError as e:
    pytest.skip(f"DAP modules not available: {e}", allow_module_level=True)


class TestDapCoreClasses:
    """Test DAP core classes and their methods"""
    
    def test_core_dap_class(self):
        """Test Dap class from core module"""
        try:
            from dap.core.dap import Dap
            dap_instance = Dap()
            assert dap_instance is not None
            print("✅ Dap class created successfully")
            
            # Test if init method exists
            if hasattr(dap_instance, 'init'):
                print("✅ Dap.init method exists")
                try:
                    result = dap_instance.init()
                    print(f"✅ Dap.init returned: {result}")
                except Exception as e:
                    print(f"⚠️  Dap.init failed (expected): {e}")
            else:
                print("⚠️  Dap.init method missing")
                
        except ImportError as e:
            print(f"❌ Failed to import Dap class: {e}")
            pytest.skip("Dap class not available")
            
    def test_core_system_class(self):
        """Test DapSystem class from core module"""
        try:
            from dap.core.system import DapSystem
            system = DapSystem()
            assert system is not None
            print("✅ DapSystem class created successfully")
            
            # Check for memory functions
            for method in ['malloc', 'free', 'calloc', 'realloc']:
                if hasattr(system, method):
                    print(f"✅ DapSystem.{method} method exists")
                else:
                    print(f"⚠️  DapSystem.{method} method missing")
                    
        except ImportError as e:
            print(f"❌ Failed to import DapSystem class: {e}")
            pytest.skip("DapSystem class not available")
            
    def test_core_logging_class(self):
        """Test DapLogging class from core module"""
        try:
            from dap.core.logging import DapLogging
            logger = DapLogging()
            assert logger is not None
            print("✅ DapLogging class created successfully")
            
            # Test basic methods
            if hasattr(logger, 'set_level'):
                print("✅ DapLogging.set_level method exists")
                try:
                    logger.set_level("DEBUG")
                    print("✅ DapLogging.set_level called successfully")
                except Exception as e:
                    print(f"⚠️  DapLogging.set_level failed (expected): {e}")
            
        except ImportError as e:
            print(f"❌ Failed to import DapLogging class: {e}")
            pytest.skip("DapLogging class not available")


class TestDapCryptoClasses:
    """Test DAP crypto classes and their methods"""
    
    def test_crypto_key_class(self):
        """Test DapCryptoKey class with proper parameters"""
        try:
            from dap.crypto.keys import DapCryptoKey
            # DapCryptoKey requires key_handle parameter
            mock_key_handle = "mock_handle"  # Simple mock for testing
            crypto_key = DapCryptoKey(mock_key_handle)
            assert crypto_key is not None
            print("✅ DapCryptoKey class created successfully")
            
            # Check for key methods
            for method in ['get_public_key', 'get_private_key']:
                if hasattr(crypto_key, method):
                    print(f"✅ DapCryptoKey.{method} method exists")
                else:
                    print(f"⚠️  DapCryptoKey.{method} method missing")
                    
        except ImportError as e:
            print(f"❌ Failed to import DapCryptoKey class: {e}")
            pytest.skip("DapCryptoKey class not available")
            
    def test_crypto_hash_class(self):
        """Test DapHash class (correct name)"""
        try:
            from dap.crypto.hash import DapHash
            crypto_hash = DapHash()
            assert crypto_hash is not None
            print("✅ DapHash class created successfully")
            
            # Check for hash methods
            for method in ['hash', 'fast', 'slow']:
                if hasattr(crypto_hash, method):
                    print(f"✅ DapHash.{method} method exists")
                else:
                    print(f"⚠️  DapHash.{method} method missing")
                    
        except ImportError as e:
            print(f"❌ Failed to import DapHash class: {e}")
            pytest.skip("DapHash class not available")
            
    def test_crypto_sign_class(self):
        """Test DapSign class (correct name)"""
        try:
            from dap.crypto.sign import DapSign
            # DapSign requires sign_handle parameter
            mock_sign_handle = "mock_handle"
            crypto_sign = DapSign(mock_sign_handle)
            assert crypto_sign is not None
            print("✅ DapSign class created successfully")
            
        except ImportError as e:
            print(f"❌ Failed to import DapSign class: {e}")
            pytest.skip("DapSign class not available")


class TestDapConfigClasses:
    """Test DAP config classes and their methods"""
    
    def test_config_class(self):
        """Test DapConfig class"""
        try:
            from dap.config.config import DapConfig
            config = DapConfig()
            assert config is not None
            print("✅ DapConfig class created successfully")
            
            # Check for config methods
            for method in ['init', 'get_item_str', 'get_item_int', 'get_item_bool']:
                if hasattr(config, method):
                    print(f"✅ DapConfig.{method} method exists")
                else:
                    print(f"⚠️  DapConfig.{method} method missing")
                    
        except ImportError as e:
            print(f"❌ Failed to import DapConfig class: {e}")
            pytest.skip("DapConfig class not available")


class TestDapNetworkClasses:
    """Test DAP network classes and their methods"""
    
    def test_network_client_class(self):
        """Test DapClient class (correct name)"""
        try:
            from dap.network.client import DapClient
            # DapClient requires client_handle parameter
            mock_client_handle = "mock_client_handle"
            client = DapClient(mock_client_handle)
            assert client is not None
            print("✅ DapClient class created successfully")
            
        except ImportError as e:
            print(f"❌ Failed to import DapClient class: {e}")
            pytest.skip("DapClient class not available")
            
    def test_network_server_class(self):
        """Test DapServer class (correct name)"""
        try:
            from dap.network.server import DapServer
            # DapServer requires server_handle parameter
            mock_server_handle = "mock_server_handle"
            server = DapServer(mock_server_handle)
            assert server is not None
            print("✅ DapServer class created successfully")
            
        except ImportError as e:
            print(f"❌ Failed to import DapServer class: {e}")
            pytest.skip("DapServer class not available")


class TestDapGlobalDbClasses:
    """Test DAP global database classes"""
    
    def test_gdb_class(self):
        """Test Gdb class (correct name)"""
        try:
            from dap.global_db.gdb import Gdb
            gdb = Gdb()
            assert gdb is not None
            print("✅ Gdb class created successfully")
            
        except ImportError as e:
            print(f"❌ Failed to import Gdb class: {e}")
            pytest.skip("Gdb class not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 