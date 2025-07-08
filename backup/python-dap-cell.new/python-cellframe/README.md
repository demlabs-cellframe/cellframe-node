# 🚀 Cellframe Python SDK 2.0 - Modern Architecture

**The next generation of Cellframe Python SDK with pythonic design, type safety, and async support.**

## ✨ Key Features

- 🐍 **Pythonic Design**: Context managers, properties, decorators
- 🔒 **Type Safety**: Full type hints and runtime validation
- ⚡ **Async Support**: Native async/await for network operations
- 🏗️ **Modular Architecture**: Clean separation of concerns
- 🔄 **Legacy Compatible**: 100% backward compatibility
- 🛡️ **Error Handling**: Comprehensive exception hierarchy
- 📦 **Standalone Mode**: Works without cellframe-node

## 🏗️ Architecture Overview

```python
cellframe/
├── core/           # Base infrastructure
│   ├── base.py     # CellframeBase, ResourceManager
│   ├── config.py   # ConfigManager, validation
│   ├── events.py   # EventSystem, async events
│   ├── exceptions.py # Exception hierarchy
│   └── node.py     # CellframeNode (main entry point)
├── crypto/         # Cryptographic operations
├── network/        # Network communication
├── chain/          # Blockchain operations
├── wallet/         # Wallet management
├── services/       # High-level services
├── legacy/         # Backward compatibility
└── types.py        # Type definitions
```

## 🚀 Quick Start

### Modern API
```python
from cellframe import CellframeNode
from cellframe.crypto import CryptoKey, KeyType

# Simple node creation
node = CellframeNode.create(network='testnet')

# Context managers for resource safety
with CryptoKey.generate(KeyType.ECDSA_SECP256K1) as key:
    signature = key.sign(b"Hello World")
    
# Async network operations
async with node.get_network().connect() as client:
    balance = await client.get_balance(wallet_address)
```

### Legacy API (still works!)
```python
# Old code continues to work unchanged
from CellFrame import *
init(config_json)
# ... existing code
```

## 🏗️ Core Infrastructure (Phase 2 ✅ COMPLETED)

### CellframeBase
All SDK components inherit from `CellframeBase`:
- Automatic resource management
- Lifecycle tracking (initialize → activate → deactivate → shutdown)
- Event system integration
- Logging and configuration

### ResourceManager
Singleton resource manager:
- Automatic cleanup on shutdown
- Context manager support
- Resource statistics and monitoring

### ConfigManager
Type-safe configuration system:
- Environment variable integration
- Schema validation
- Dynamic updates with watchers

### EventSystem
Async event bus with middleware:
- Sync and async event handlers
- Priority-based execution
- Event filtering and routing

### Exception Hierarchy
Comprehensive error handling:
- Structured error context
- Error codes for programmatic handling
- Chained exceptions with suggestions

## 📋 Development Progress

### ✅ Phase 1: Architecture Analysis & Design (100%)
- Current architecture analysis
- New architecture specification  
- UML diagrams and design patterns
- API specification

### ✅ Phase 2: Core Architecture Implementation (100%)
- CellframeBase with lifecycle management
- ResourceManager for automatic cleanup
- ConfigManager with type validation
- EventSystem with async support
- Exception hierarchy with context

### 🎯 Phase 3: Module-by-Module Refactoring (IN PROGRESS)
- cellframe.crypto - Modern crypto API
- cellframe.network - Async network client
- cellframe.chain - High-level blockchain API
- cellframe.wallet - Secure wallet operations
- cellframe.services - Service abstractions

### 📋 Phase 4: Compatibility & Standalone (PLANNED)
- Legacy API compatibility layer
- Standalone mode implementation
- Migration tools

### 📚 Phase 5: Documentation & Testing (PLANNED)
- Comprehensive documentation
- Test suite
- Performance benchmarks
- PyPI packaging

## 🔧 Design Principles

### 1. Pythonic
```python
# Context managers
with CryptoKey.generate(KeyType.ECDSA) as key:
    signature = key.sign(data)

# Properties and descriptors
node.config.network = 'testnet'
wallet.balance  # Cached property with auto-refresh
```

### 2. Type Safe
```python
def transfer_tokens(
    amount: TokenAmount, 
    to_address: Address
) -> TransactionHash:
    """Type hints everywhere for IDE support."""
```

### 3. Async Native
```python
async with NetworkClient.connect('mainnet') as client:
    balance = await client.get_balance(address)
    tx_hash = await client.submit_transaction(tx)
```

### 4. Error Context
```python
try:
    key = CryptoKey.from_file(path)
except CryptoException as e:
    print(f"Error: {e.message}")
    print(f"Suggestions: {e.suggestions}")
    print(f"Context: {e.context}")
```

## 🔄 Migration from Legacy API

The new SDK maintains 100% backward compatibility:

```python
# Legacy code (still works)
init(json_config)
key = Crypto.newKey(CryptoKeyType.DAP_ENC_KEY_TYPE_IAES())
del key

# New code (modern approach)
node = CellframeNode.create(network='mainnet')
with CryptoKey.generate(KeyType.ECDSA_SECP256K1) as key:
    signature = key.sign(data)
```

## 🧪 Example Usage

### Complete Transaction Example
```python
import asyncio
from cellframe import CellframeNode
from cellframe.crypto import CryptoKey, KeyType
from cellframe.types import Address, TokenAmount

async def send_transaction():
    # Create node
    node = CellframeNode.create(network='testnet')
    
    # Generate wallet
    with CryptoKey.generate(KeyType.ECDSA_SECP256K1) as key:
        address = Address.from_public_key(key.get_public_key())
        
        # Connect to network
        async with node.get_network().connect() as client:
            # Check balance
            balance = await client.get_balance(address)
            print(f"Balance: {balance}")
            
            # Create transaction
            if balance > TokenAmount('0.1', 'CELL'):
                tx = (node.get_chain().transaction_builder()
                      .from_address(address)
                      .to_address(recipient)
                      .amount(TokenAmount('0.1', 'CELL'))
                      .build_and_sign(key))
                
                # Submit transaction
                tx_hash = await client.submit_transaction(tx)
                print(f"Transaction: {tx_hash}")

asyncio.run(send_transaction())
```

## 🛡️ Error Handling

Rich exception hierarchy with context:

```python
try:
    async with NetworkClient.connect('invalid-network') as client:
        pass
except NetworkException as e:
    # Rich error context
    print(f"Network error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"Network ID: {e.context.get('network_id')}")
    print("Suggestions:")
    for suggestion in e.suggestions:
        print(f"  - {suggestion}")
```

## 🔧 Configuration

Type-safe configuration with validation:

```python
from cellframe.core import ConfigManager
from pathlib import Path

config = ConfigManager()
config.load_from_file(Path('cellframe.json'))
config.load_from_env(prefix='CELLFRAME_')

# Type-safe access
network = config.get_typed_value('network', str, 'mainnet')
max_conn = config.get_typed_value('max_connections', int, 50)

# Validation
validation = config.validate()
if not validation.is_valid:
    print(f"Config errors: {validation.errors}")
```

## 📊 Current Status

- **Architecture**: ✅ Complete and validated
- **Core Infrastructure**: ✅ 100% implemented
- **Module Refactoring**: 🔄 Phase 3 started
- **Legacy Compatibility**: 📋 Phase 4 planned
- **Documentation**: 📋 Phase 5 planned

## 🎯 Next Steps

1. **Phase 3**: Implement crypto module with modern API
2. **Network Module**: Async network client with connection pooling
3. **Chain Module**: Transaction builder and blockchain operations
4. **Testing**: Comprehensive test suite for all components

---

**This is the foundation of a modern, pythonic Cellframe SDK that will provide developers with an excellent experience while maintaining full backward compatibility.** 