# Python DAP SDK

Python bindings for DAP SDK - low-level access to network protocols and cryptographic functions.

## Overview

Python DAP SDK provides direct Python wrappers over DAP SDK functions, offering access to:

- **Network protocols**: DAP stream protocol with channel multiplexing, HTTP client functionality, WebSocket support
- **Cryptographic operations**: Key generation, digital signatures, hashing, encryption
- **Core utilities**: Configuration management, logging, memory operations
- **Global database**: Distributed storage operations

## Features

### Network Module
- **DAP Stream Protocol**: Native request-response protocol with session management
- **Channel Multiplexing**: Multiple logical channels over single stream connection  
- **HTTP Client**: HTTP/HTTPS requests with async callback support
- **WebSocket**: WebSocket client for real-time communication
- **Server**: TCP, HTTP, JSON-RPC, WebSocket server implementations

### Cryptographic Module
- **Digital Signatures**: DILITHIUM (quantum-safe), FALCON, Tesla, Picnic, Bliss
- **Encryption**: AES, OAES, IAES, Salsa20/12, Blowfish, GOST
- **Hashing**: KECCAK (default), SHA-2, SHA-3, BLAKE2
- **Key Management**: Key generation, serialization, certificate handling

### Core Module
- **Configuration**: INI-style configuration file management
- **Logging**: Multi-level logging with file output
- **Memory**: Safe memory allocation and management utilities
- **Events**: Asynchronous event processing system

## Installation

### Build Requirements

```bash
# Debian/Ubuntu
sudo apt-get install build-essential cmake python3-dev

# macOS  
brew install cmake python3
```

### Build from Source

```bash
mkdir build && cd build
cmake .. -DBUILD_SHARED=ON
  make -j$(nproc)
  ```

### Install Package

```bash
# Create wheel package
make python_package

# Install in virtual environment
make install_venv

# System install
sudo make install
```

## Usage

### Basic Network Operations

```python
import python_dap as dap

# Initialize network subsystem
dap.dap_network_init()

# Create HTTP client
client = dap.dap_http_client_new()

# Make HTTP request
response = dap.dap_http_client_request("http://example.com", "GET")

# Get response data
data = dap.dap_http_client_get_response_data(response)
code = dap.dap_http_client_get_response_code(response)

print(f"Status: {code}, Data: {data}")
```

### Stream Protocol Example

```python
import python_dap as dap

# Create stream session
session = dap.dap_stream_session_new()

# Create channel
channel_id = dap.dap_stream_ch_new(session, "my_channel")

# Send data over channel
dap.dap_stream_ch_pkt_write(session, channel_id, 0x01, b"Hello DAP")
dap.dap_stream_ch_pkt_send(session, channel_id)
```

### Cryptographic Operations

```python
import python_dap as dap

# Generate DILITHIUM key pair
key = dap.dap_enc_key_new(dap.DAP_ENC_KEY_TYPE_SIG_DILITHIUM)
dap.dap_enc_key_generate(key, b"", 0, b"seed", 4)

# Create signature
signature = dap.dap_sign_create(key, b"message", 7, 0)

# Verify signature
is_valid = dap.dap_sign_verify(signature, key)
print(f"Signature valid: {is_valid}")
```

### Configuration Management

```python
import python_dap as dap

# Load configuration file
config = dap.dap_config_open("app.conf")

# Read values
host = dap.dap_config_get_item_str(config, "server", "host")
port = dap.dap_config_get_item_int(config, "server", "port")

print(f"Server: {host}:{port}")
```

## Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test categories  
python3 -m pytest tests/unit/ -v
python3 -m pytest tests/integration/ -v
python3 -m pytest tests/regression/ -v

# CMake test runner
make test_setup
make python_tests
```

## API Reference

### Network Functions
- `dap_network_init()` - Initialize network subsystem
- `dap_http_client_*()` - HTTP client operations
- `dap_stream_*()` - Stream protocol functions
- `dap_client_*()` - Generic client operations
- `dap_server_*()` - Server management

### Cryptographic Functions  
- `dap_enc_key_*()` - Key management
- `dap_sign_*()` - Digital signatures
- `dap_hash_*()` - Hashing operations
- `dap_cert_*()` - Certificate handling

### Core Functions
- `dap_config_*()` - Configuration management
- `dap_log_*()` - Logging operations
- `dap_memory_*()` - Memory utilities

### Constants
- `DAP_ENC_KEY_TYPE_*` - Key type constants
- `DAP_HASH_TYPE_*` - Hash algorithm constants  
- `DAP_HTTP_METHOD_*` - HTTP method constants
- `DAP_STREAM_STATE_*` - Stream state constants

## Architecture

```
python_dap.so
├── Network Layer
│   ├── HTTP Client (dap_client_http_*)
│   ├── Stream Protocol (dap_stream_*)
│   ├── WebSocket Client (dap_websocket_*)
│   └── Server Framework (dap_server_*)
├── Crypto Layer  
│   ├── Digital Signatures (dap_sign_*)
│   ├── Encryption (dap_enc_*)
│   └── Hashing (dap_hash_*)
├── Core Layer
│   ├── Configuration (dap_config_*)
│   ├── Logging (dap_log_*)
│   └── Memory (dap_memory_*)
└── C Extension Interface
```

## License

Licensed under the same terms as DAP SDK.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## Links

- [DAP SDK Repository](https://gitlab.demlabs.net/dap/dap-sdk)
- [Documentation](https://wiki.cellframe.net/en/soft)
- [Issue Tracker](https://gitlab.demlabs.net/dap/dap-sdk/-/issues)
