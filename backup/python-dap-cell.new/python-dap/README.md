# Python DAP SDK

🧬 **Direct Python bindings for DAP SDK**

Python DAP SDK provides direct Python wrappers over DAP SDK (dap-sdk) functions, offering low-level access to the DAP ecosystem while maintaining pythonic interfaces.

## 🚀 Quick Start

```python
from dap import Dap, DapConfig, DapCrypto

# Initialize DAP core
dap = Dap()
dap.init()

# Work with configuration
dap_config = DapConfig()
network = dap_config.get_item_str("general", "network", "mainnet")

# Use cryptographic functions
dap_crypto = DapCrypto()
key_handle = dap_crypto.key_create("ed25519")
```

## 📦 Installation

```bash
# From source
git clone git@gitlab.demlabs.net:dap/python-dap.git
cd python-dap
pip install -e .

# For development
pip install -e ".[dev]"
```

## 🏗️ Architecture

Python DAP SDK is organized into modules that directly correspond to DAP SDK components:

### Core Modules

- **`dap.core`** - Core functions (`dap_malloc`, `dap_free`, `dap_core_init`, etc.)
- **`dap.config`** - Configuration management (`dap_config_*` functions)
- **`dap.events`** - Event system (`dap_events_*` functions)
- **`dap.crypto`** - Cryptographic operations (`dap_crypto_*` functions)
- **`dap.network`** - Network functions (`dap_network_*` functions)
- **`dap.common`** - Common utilities (logging, encoding, time functions)

### Design Principles

✅ **Direct Mapping** - Each Python function directly calls corresponding dap_* function
✅ **No Abstractions** - Minimal wrapping, maximum compatibility
✅ **Error Handling** - Proper exception handling for Python environment
✅ **Memory Safety** - Safe memory management for Python/C interaction
✅ **Type Hints** - Full type annotations for better development experience

## 📖 Usage Examples

### Core Functions

```python
from dap import get_dap

# Memory management
dap = get_dap()
dap.init()

ptr = dap.malloc(1024)
dap.free(ptr)
```

### Configuration

```python
from dap import get_dap_config

config = get_dap_config()

# Get configuration values
network = config.get_item_str("general", "network", "mainnet")
port = config.get_item_int32("server", "port", 8079)
debug = config.get_item_bool("general", "debug", False)
```

### Cryptography

```python
from dap import get_dap_crypto

crypto = get_dap_crypto()
crypto.init()

# Create and use cryptographic keys
key_handle = crypto.key_create("ed25519")
signature = crypto.key_sign(key_handle, b"Hello World")
is_valid = crypto.key_verify(key_handle, b"Hello World", signature)

crypto.key_destroy(key_handle)
```

### Events

```python
from dap import get_dap_events

events = get_dap_events()

def event_handler(event_data):
    print(f"Received event: {event_data}")

# Subscribe to events
callback_id = events.subscribe("system.startup", event_handler)

# Emit events
events.emit("custom.event", {"message": "Hello"})

# Unsubscribe
events.unsubscribe("system.startup", callback_id)
```

### Network Operations

```python
from dap import get_dap_network

network = get_dap_network()
network.init()

# Connect to peer
connection_id = network.connect("127.0.0.1", 8079)
if connection_id:
    # Send data
    network.send(connection_id, b"Hello peer")
    
    # Disconnect
    network.disconnect(connection_id)
```



## 🔧 Development

### Requirements

- Python 3.8+
- DAP SDK (dap-sdk) compiled and available
- C compiler for building extensions

### Setting up Development Environment

```bash
git clone git@gitlab.demlabs.net:dap/python-dap.git
cd python-dap

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Check code quality
black .
isort .
flake8 .
mypy .
```

### Project Structure

```
python-dap/
├── dap/                 # Main package
│   ├── __init__.py     # Package exports
│   ├── core/           # Core DAP functions
│   ├── config/         # Configuration functions
│   ├── events/         # Event system functions
│   ├── crypto/         # Cryptographic functions
│   ├── network/        # Network functions
│   └── common/         # Common utilities
├── tests/              # Test suite
├── docs/               # Documentation
├── setup.py           # Package setup
└── README.md          # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a merge request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- **[Cellframe Python SDK](https://gitlab.demlabs.net/cellframe/python-cellframe-new)** - High-level Cellframe blockchain SDK
- **[DAP SDK](https://gitlab.demlabs.net/dap/dap-sdk)** - Core DAP SDK in C
- **[Cellframe Node](https://gitlab.demlabs.net/cellframe/cellframe-node)** - Cellframe blockchain node

## 📞 Support

- **Issues**: [GitLab Issues](https://gitlab.demlabs.net/dap/python-dap/-/issues)
- **Documentation**: [docs.demlabs.net/python-dap](https://docs.demlabs.net/python-dap/)
- **Email**: support@demlabs.net 