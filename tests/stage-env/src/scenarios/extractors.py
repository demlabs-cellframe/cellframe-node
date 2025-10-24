"""
Built-in extractors and validators for scenario data extraction.

Provides robust extraction and validation of common data types
from CLI output, with helpful error messages.
"""

import re
import struct
import hashlib
from typing import Optional, Tuple, Dict, Any
import base58

from .schema import ExtractType


class ExtractionError(Exception):
    """Raised when data extraction or validation fails."""
    pass


class WalletAddressComponents:
    """Parsed wallet address components."""
    def __init__(self, addr_ver: int, net_id: int, sig_type: int, key_hash: bytes, checksum: bytes):
        self.addr_ver = addr_ver
        self.net_id = net_id
        self.sig_type = sig_type
        self.key_hash = key_hash
        self.checksum = checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for debugging."""
        return {
            'addr_ver': self.addr_ver,
            'net_id': hex(self.net_id),
            'sig_type': hex(self.sig_type),
            'key_hash': self.key_hash.hex(),
            'checksum': self.checksum.hex()
        }


class DataExtractor:
    """Built-in data extractors with type validation."""
    
    # Validation patterns
    WALLET_ADDRESS_PATTERN = r'^[A-Za-z0-9]{75,105}$'  # Base58, variable length
    NODE_ADDRESS_PATTERN = r'^[A-Fa-f0-9:]{10,}$'      # Hex with :: separators (e.g., A1B2::C3D4::E5F6)
    HASH_PATTERN = r'^(0x)?[A-Fa-f0-9]{64}$'           # Optional 0x prefix
    TOKEN_NAME_PATTERN = r'^[A-Z0-9_]{1,16}$'          # Uppercase alphanumeric
    
    # Cellframe address structure (from dap_chain_common.h)
    # sizeof(dap_chain_addr_t) = 1 (addr_ver) + 8 (net_id) + 2 (sig_type) + 32 (hash) + 32 (checksum) = 75 bytes
    ADDR_STRUCT_FORMAT = '<BQH32s32s'  # little-endian: byte, uint64, uint16, 32 bytes, 32 bytes
    ADDR_SIZE = struct.calcsize(ADDR_STRUCT_FORMAT)
    
    @staticmethod
    def _validate_wallet_address_checksum(address_bytes: bytes) -> Tuple[bool, Optional[WalletAddressComponents], Optional[str]]:
        """
        Validate wallet address structure and checksum (Cellframe format).
        
        Returns:
            Tuple of (is_valid, components_or_None, error_message_or_None)
        """
        if len(address_bytes) != DataExtractor.ADDR_SIZE:
            return (False, None, f"Invalid address size: {len(address_bytes)} bytes (expected {DataExtractor.ADDR_SIZE})")
        
        try:
            # Unpack address components
            addr_ver, net_id, sig_type_raw, key_hash, stored_checksum = struct.unpack(
                DataExtractor.ADDR_STRUCT_FORMAT, address_bytes
            )
            
            # Calculate checksum (SHA3-256 of first 43 bytes: everything except checksum)
            data_to_hash = address_bytes[:-32]  # All except last 32 bytes (checksum)
            calculated_checksum = hashlib.sha3_256(data_to_hash).digest()
            
            # Compare checksums
            if stored_checksum != calculated_checksum:
                return (
                    False, 
                    None,
                    f"Checksum mismatch: stored={stored_checksum.hex()[:16]}..., calculated={calculated_checksum.hex()[:16]}..."
                )
            
            components = WalletAddressComponents(
                addr_ver=addr_ver,
                net_id=net_id,
                sig_type=sig_type_raw,
                key_hash=key_hash,
                checksum=stored_checksum
            )
            
            return (True, components, None)
            
        except struct.error as e:
            return (False, None, f"Failed to parse address structure: {e}")
    
    @staticmethod
    def extract_and_validate(
        output: str,
        pattern: str,
        extract_type: ExtractType,
        group: int = 1,
        required: bool = True,
        default: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract data from output using regex and validate against type.
        
        Args:
            output: Command output to extract from
            pattern: Regex pattern to match
            extract_type: Type of data to validate
            group: Regex capture group number
            required: Whether extraction failure should raise error
            default: Default value if extraction fails (only if not required)
            
        Returns:
            Tuple of (extracted_value, error_message)
            If successful: (value, None)
            If failed: (None, error_message) or (default, None)
            
        Raises:
            ExtractionError: If extraction/validation fails and required=True
        """
        # Try to extract using pattern
        match = re.search(pattern, output, re.MULTILINE)
        
        if not match:
            error_msg = f"Pattern '{pattern}' not found in output (searched {len(output)} characters)"
            print(f"[EXTRACT_DEBUG] Pattern match FAILED")
            print(f"[EXTRACT_DEBUG] Pattern: {pattern}")
            print(f"[EXTRACT_DEBUG] Output preview (first 200 chars): {output[:200]}")
            if required:
                raise ExtractionError(error_msg)
            return (default, error_msg if default is None else None)
        
        print(f"[EXTRACT_DEBUG] ✓ Pattern matched at position {match.start()}-{match.end()}")
        print(f"[EXTRACT_DEBUG] Matched text: '{match.group(0)}'")
        
        try:
            extracted_value = match.group(group)
            print(f"[EXTRACT_DEBUG] ✓ Captured group {group}: '{extracted_value}'")
        except IndexError:
            error_msg = f"Capture group {group} not found in pattern '{pattern}'"
            print(f"[EXTRACT_DEBUG] ✗ Capture group {group} NOT FOUND (pattern has {match.lastindex} groups)")
            if required:
                raise ExtractionError(error_msg)
            return (default, error_msg if default is None else None)
        
        # Validate extracted value against type
        print(f"[EXTRACT_DEBUG] Validating extracted value against type: {extract_type}")
        error_msg = DataExtractor._validate_type(extracted_value, extract_type)
        
        if error_msg:
            if required:
                raise ExtractionError(error_msg)
            return (default, error_msg if default is None else None)
        
        return (extracted_value, None)
    
    @staticmethod
    def _validate_type(value: str, extract_type: ExtractType) -> Optional[str]:
        """
        Validate extracted value against expected type.
        
        Returns:
            None if valid, error message string if invalid
        """
        if extract_type == ExtractType.RAW:
            return None  # No validation for raw strings
        
        if extract_type == ExtractType.WALLET_ADDRESS:
            # Basic format check
            print(f"[WALLET_ADDR_DEBUG] Validating: '{value}'")
            print(f"[WALLET_ADDR_DEBUG] Length: {len(value)} characters")
            
            if not re.match(DataExtractor.WALLET_ADDRESS_PATTERN, value):
                error_msg = (
                    f"Invalid wallet address format: '{value}' "
                    f"(expected base58, 75-105 characters, got {len(value)})"
                )
                print(f"[WALLET_ADDR_DEBUG] ✗ Format check FAILED: {error_msg}")
                return error_msg
            
            print(f"[WALLET_ADDR_DEBUG] ✓ Format check passed (base58, length OK)")
            
            # Decode base58 and validate structure + checksum
            try:
                decoded = base58.b58decode(value)
                print(f"[WALLET_ADDR_DEBUG] ✓ Base58 decode successful, decoded length: {len(decoded)} bytes")
                
                is_valid, components, error = DataExtractor._validate_wallet_address_checksum(decoded)
                
                if not is_valid:
                    error_msg = (
                        f"Invalid wallet address: {error}\n"
                        f"Address: {value}\n"
                        f"Decoded length: {len(decoded)} bytes"
                    )
                    print(f"[WALLET_ADDR_DEBUG] ✗ Checksum validation FAILED: {error}")
                    return error_msg
                
                print(f"[WALLET_ADDR_DEBUG] ✓ Checksum validation PASSED")
                print(f"[WALLET_ADDR_DEBUG] Address components: addr_ver={components.addr_ver}, net_id={components.net_id}, sig_type={components.sig_type}")
                
            except Exception as e:
                # base58 decoding can fail for invalid characters
                error_msg = (
                    f"Failed to decode wallet address (invalid base58): {str(e)}\n"
                    f"Address: {value}"
                )
                print(f"[WALLET_ADDR_DEBUG] ✗ Base58 decode FAILED: {str(e)}")
                return error_msg
        
        elif extract_type == ExtractType.NODE_ADDRESS:
            if not re.match(DataExtractor.NODE_ADDRESS_PATTERN, value):
                return (
                    f"Invalid node address format: '{value}' "
                    f"(expected hex format with :: separators, e.g., A1B2::C3D4::E5F6)"
                )
        
        elif extract_type == ExtractType.HASH:
            if not re.match(DataExtractor.HASH_PATTERN, value):
                return (
                    f"Invalid hash format: '{value}' "
                    f"(expected 64 hex characters, optionally prefixed with 0x)"
                )
        
        elif extract_type == ExtractType.NUMBER:
            try:
                # Try to parse as number (int or float)
                float(value)
            except ValueError:
                return f"Invalid number format: '{value}'"
        
        elif extract_type == ExtractType.TOKEN_NAME:
            if not re.match(DataExtractor.TOKEN_NAME_PATTERN, value):
                return (
                    f"Invalid token name format: '{value}' "
                    f"(expected 1-16 uppercase alphanumeric characters)"
                )
        
        elif extract_type == ExtractType.BOOL:
            valid_true = {'true', '1', 'yes', 'on', 'enabled'}
            valid_false = {'false', '0', 'no', 'off', 'disabled'}
            if value.lower() not in valid_true and value.lower() not in valid_false:
                return (
                    f"Invalid boolean format: '{value}' "
                    f"(expected: true/false, 1/0, yes/no, on/off, enabled/disabled)"
                )
        
        return None  # Valid
    
    @staticmethod
    def get_default_pattern(extract_type: ExtractType) -> str:
        """
        Get default regex pattern for common extraction types.
        
        Useful for scenarios where user wants to extract by type
        without specifying a custom pattern.
        """
        defaults = {
            ExtractType.WALLET_ADDRESS: r'addr:\s+(\S+)',
            ExtractType.NODE_ADDRESS: r'(?:node[_-]?addr|address):\s*([A-Fa-f0-9:]+)',
            ExtractType.HASH: r'(?:hash|tx):\s*((?:0x)?[A-Fa-f0-9]{64})',
            ExtractType.TOKEN_NAME: r'token:\s*([A-Z0-9_]+)',
            ExtractType.NUMBER: r'(\d+(?:\.\d+)?)',
            ExtractType.BOOL: r'(true|false|yes|no|1|0|on|off|enabled|disabled)',
            ExtractType.RAW: r'(.+)',
        }
        return defaults.get(extract_type, r'(.+)')


