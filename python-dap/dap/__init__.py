"""
🔗 DAP SDK - Comprehensive Python SDK for DAP Protocol

This is the complete DAP SDK providing all necessary components for blockchain development:
- Core utilities and exceptions
- Crypto operations (signing, certificates)
- Network operations (client, server, streaming, HTTP)
- Chain operations (wallet, transactions, ledger)
- Configuration management
- Event handling

Example:
    # Crypto operations
    from dap.crypto import DapSign, DapCert
    signature = DapSign.create_from_key_and_data(key, data)
    
    # Network operations
    from dap.network import DapClient, DapServer, DapStream
    client = DapClient.create_and_connect("192.168.1.100", 8080)
    
    # Chain operations
    from dap.chain import DapWallet, DapTransaction, DapLedger
    wallet = DapWallet.create_wallet("my-wallet", DapWalletType.HD)
"""

# Core modules
from . import core
from . import config
from . import events

# Main functional modules
from . import crypto
from . import network
from . import chain

# Re-export main classes for convenience
from .crypto import (
    DapSign, DapCert, DapSignError, DapCertError
)

from .network import (
    DapClient, DapServer, DapStream, DapHttp,
    DapClientError, DapServerError, DapStreamError, DapHttpError
)

from .chain import (
    DapWallet, DapTransaction, DapLedger,
    DapWalletError, DapTransactionError, DapLedgerError
)

from .core.exceptions import DapException

__all__ = [
    # Modules
    'core',
    'config', 
    'events',
    'crypto',
    'network',
    'chain',
    
    # Core exceptions
    'DapException',
    
    # Crypto classes
    'DapSign',
    'DapCert',
    'DapSignError',
    'DapCertError',
    
    # Network classes
    'DapClient',
    'DapServer', 
    'DapStream',
    'DapHttp',
    'DapClientError',
    'DapServerError',
    'DapStreamError',
    'DapHttpError',
    
    # Chain classes
    'DapWallet',
    'DapTransaction',
    'DapLedger',
    'DapWalletError',
    'DapTransactionError',
    'DapLedgerError'
]

# Version info
__version__ = "2.0.0"
__author__ = "Demlabs"
__description__ = "DAP SDK - Complete Python SDK for DAP Protocol with proper C structure wrapping" 