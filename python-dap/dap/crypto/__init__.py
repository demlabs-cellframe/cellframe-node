"""
🔐 DAP Crypto Module

Comprehensive cryptographic operations for DAP SDK.
All classes now properly wrap corresponding C structures.
"""

from .keys import (
    DapKey,
    DapKeyType,
    DapKeyError,
    DapKeyManager,
    generate_key,
    load_key,
    save_key
)

from .sign import (
    DapSign,
    DapSignError,
    DapHashType,
    DapSignatureAggregator,
    DapBatchVerifier,
    quick_sign,
    quick_verify
)

from .cert import (
    DapCert,
    DapCertError,
    DapCertMetaType,
    DapCertificateManager,
    create_certificate,
    load_certificate,
    find_certificate
)

from .hash import (
    DapHash,
    DapHashError,
    DapHashType as DapHashingType,
    quick_hash,
    quick_hash_fast
)

__all__ = [
    # Keys
    'DapKey',
    'DapKeyType',
    'DapKeyError',
    'DapKeyManager',
    'generate_key',
    'load_key',
    'save_key',
    
    # Digital Signatures
    'DapSign',
    'DapSignError',
    'DapHashType',
    'DapSignatureAggregator',
    'DapBatchVerifier',
    'quick_sign',
    'quick_verify',
    
    # Certificates
    'DapCert',
    'DapCertError',
    'DapCertMetaType',
    'DapCertificateManager',
    'create_certificate',
    'load_certificate',
    'find_certificate',
    
    # Hashing
    'DapHash',
    'DapHashError',
    'DapHashingType',
    'quick_hash',
    'quick_hash_fast'
]

# Version info
__version__ = "2.0.0"
__author__ = "Demlabs"
__description__ = "DAP SDK Crypto Module - Proper C structure wrapping"
