# 🏗️ Cellframe Python SDK Architecture v2.0

## 📁 Project Structure Overview

This document outlines the modern architecture of the Cellframe Python SDK, designed for clarity, maintainability, and developer experience.

### 🎯 Key Architecture Principles

1. **Clean Separation**: Low-level DAP operations (python-dap) vs High-level Cellframe SDK (python-cellframe-new)
2. **Exception Inheritance**: All exceptions inherit from DAP base exceptions for consistency
3. **No Duplication**: Configuration managed exclusively through python-dap
4. **Real C Integration**: Direct calls to cellframe-sdk C functions, no mock implementations

---

## 📦 Package Structure

### 🧬 python-dap (Separate Repository)
**Purpose**: Direct 1:1 wrappers over DAP SDK C functions
**Location**: Should be at `git@gitlab.demlabs.net:dap/python-dap`

```
python-dap/
├── setup.py                    # Package configuration
├── README.md                   # Documentation and examples
└── dap/
    ├── __init__.py             # Main exports
    ├── core/                   # MERGED: Core + Common functionality
    │   ├── __init__.py
    │   ├── core.py            # Dap class: init, malloc, free, logging, time utils
    │   └── exceptions.py      # Base DAP exceptions (DapException hierarchy)
    ├── config/                # DapConfig: dap_config_* functions
    │   ├── __init__.py
    │   └── config.py
    ├── events/                # DapEvents: dap_events_* functions
    │   ├── __init__.py
    │   └── events.py
    ├── crypto/                # DapCrypto: dap_crypto_*, dap_enc_* functions
    │   ├── __init__.py
    │   └── crypto.py
    └── network/               # DapNetwork: dap_client_*, dap_server_* functions
        ├── __init__.py
        └── network.py
```

**Key Classes**:
- `Dap`: Core functionality (memory, time, logging, system utils)
- `DapConfig`: Configuration management
- `DapEvents`: Event system
- `DapCrypto`: Cryptographic operations
- `DapNetwork`: Network operations
- `DapException`: Base exception hierarchy

### 🚀 python-cellframe-new (This Repository)
**Purpose**: High-level Cellframe SDK with modern Python patterns

```
python-cellframe-new/
├── ARCHITECTURE.md             # This file
├── README.md                   # Usage documentation
└── cellframe/
    ├── __init__.py            # Main SDK exports
    ├── core/                  # MERGED: Core + Chain functionality
    │   ├── __init__.py
    │   ├── cellframe.py      # CellframeNode, CellframeChain, CellframeComponent
    │   └── exceptions.py     # Cellframe exceptions (inherit from DAP)
    ├── types.py              # Common type definitions
    ├── crypto/               # High-level crypto operations
    ├── network/              # High-level network operations  
    ├── wallet/               # Wallet management
    ├── services/             # Blockchain services
    └── legacy/               # Backward compatibility
```

**Key Classes**:
- `CellframeNode`: Main node interface with integrated chain operations
- `CellframeChain`: Chain operations wrapper
- `CellframeComponent`: Base class for SDK components
- `CellframeException`: Inherits from `DapException`

---

## 🔄 Recent Architecture Changes

### ✅ Completed Refactoring

1. **🗑️ Removed Duplicates**:
   - ❌ `cellframe/core/config.py` → ✅ Use `dap.DapConfig`
   - ❌ `python-dap/dap/common/` → ✅ Merged into `python-dap/dap/core/`

2. **🏗️ Merged Modules**:
   - `python-dap/dap/core/` now includes common utilities (logging, time, string functions)
   - `cellframe/core/` combines core and chain functionality

3. **🛡️ Exception Hierarchy**:
   ```python
   DapException (python-dap)
   └── CellframeException (cellframe)
       ├── BlockchainException
       ├── NetworkException  
       ├── CryptoException
       └── ... (all others inherit from DAP base)
   ```

4. **🔧 Real C Integration**:
   - All TODO comments replaced with actual C function calls
   - Fallback implementations for development
   - Proper error handling with DAP exceptions

---

## 🎯 Usage Examples

### Low-Level DAP Operations
```python
from dap import Dap, DapConfig, DapCrypto, DapLogLevel

# Core operations
with Dap() as dap:
    dap.set_log_level(DapLogLevel.DEBUG)
    ptr = dap.malloc(1024)
    dap.free(ptr)

# Configuration
config = DapConfig()
config.init()
network = config.get_item_str("general", "network", "mainnet")
```

### High-Level Cellframe SDK
```python
from cellframe import CellframeNode

# Simple node creation
with CellframeNode.create(network="testnet") as node:
    chain = node.create_chain("my_chain")
    block_hash = chain.add_block(b"block_data")
    stats = node.get_node_stats()
```

### Exception Handling
```python
from dap import DapException
from cellframe import CellframeException, BlockchainException

try:
    # Some operation
    node.create_chain("invalid_chain")
except BlockchainException as e:
    # Cellframe-specific error
    print(f"Blockchain error: {e}")
    print(f"Suggestions: {e.suggestions}")
except DapException as e:
    # Low-level DAP error
    print(f"DAP error: {e.error_code}")
```

---

## 🔗 Dependencies

### python-dap Dependencies
- Direct C library bindings to `python_cellframe_common`
- No external Python dependencies
- Thread-safe singleton patterns

### python-cellframe-new Dependencies
- **Required**: `python-dap` package
- **Import**: `from dap import Dap, DapConfig, DapEvents, DapCrypto, DapNetwork`
- Modern Python features (typing, dataclasses, async/await)

---

## 🚀 Development Guidelines

### For DAP SDK Development
1. ✅ Add new functions to appropriate `python-dap/dap/*/` modules
2. ✅ Use direct C function calls with fallback implementations
3. ✅ Inherit all exceptions from `DapException`
4. ✅ Follow singleton patterns for global instances

### For Cellframe SDK Development  
1. ✅ Build high-level abstractions on top of python-dap
2. ✅ Use `CellframeException` and subclasses for errors
3. ✅ Combine related functionality (like core+chain)
4. ✅ Focus on developer experience and Python idioms

### Exception Guidelines
1. ✅ Always inherit from DAP base exceptions
2. ✅ Add context and suggestions to exceptions
3. ✅ Use proper error codes for programmatic handling
4. ✅ Chain exceptions to preserve error context

---

## 📈 Next Development Phases

### Phase 3: High-Level Modules (Ready to Start)
- [ ] `cellframe/crypto/` - High-level crypto operations
- [ ] `cellframe/network/` - Network client/server abstractions  
- [ ] `cellframe/wallet/` - Wallet management
- [ ] `cellframe/services/` - Blockchain services (staking, etc.)

### Phase 4: Advanced Features
- [ ] Async/await support for network operations
- [ ] Plugin system integration
- [ ] Advanced configuration management
- [ ] Monitoring and metrics

### Phase 5: Developer Experience
- [ ] Complete type hints coverage
- [ ] Comprehensive documentation
- [ ] Code generation tools
- [ ] Testing framework integration

---

## 🎉 Architecture Benefits

✅ **Clean Separation**: DAP vs Cellframe concerns clearly separated  
✅ **No Duplication**: Single source of truth for each functionality  
✅ **Consistent Errors**: Unified exception hierarchy  
✅ **Real Integration**: Direct C function calls, no mocks  
✅ **Developer Friendly**: Modern Python patterns and idioms  
✅ **Maintainable**: Clear module boundaries and responsibilities  

The architecture is now ready for implementing the remaining high-level Cellframe SDK modules! 🚀 