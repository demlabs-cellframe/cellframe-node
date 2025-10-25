# Test Scenarios Glossary

**Complete reference for stage-env scenario language**

Comprehensive description of all YAML scenario language features. Use as reference when writing tests.

## 📚 Table of Contents

1. [File Types](#file-types)
2. [Scenario Structure](#scenario-structure)
3. [Step Types](#step-types)
4. [Check Types](#check-types)
5. [Defaults System](#defaults-system)
6. [Data Extraction](#data-extraction)
7. [Suite System](#suite-system)
8. [Advanced Features](#advanced-features)

---

## File Types

### Test Scenario
Marked by presence of `test:` field. Contains executable test steps.

```yaml
name: My Test
description: Test description

test:
  - cli: token list
```

### Suite Descriptor
Marked by presence of `suite:` field. Defines test suite metadata and shared setup.

```yaml
suite: "Token Operations Suite"
description: "E2E token tests"

includes:
  - common/create_test_cert.yml

setup:
  - wait: 5s
```

Located at same level as suite directory (e.g., `token.yml` alongside `token/`).

### Include Template
Reusable component in `tests/common/`. Contains setup, defaults, or variables.

```yaml
# common/set_net_default.yml
defaults:
  cli:
    net: "{{network_name}}"
```

---

## Scenario Structure

```yaml
# === METADATA (required) ===
name: string                    # Scenario name
description: string             # What this test does

# === METADATA (optional) ===
author: string                  # Author name
tags: [string, ...]            # Tags for filtering
version: string                 # Version (default: "1.0")

# === NETWORK (optional, defaults to topology: default) ===
network:
  topology: default             # Use predefined topology
  name: stagenet                # Network name (becomes {{network_name}})

# === INCLUDES (optional) ===
includes:
  - common/create_test_cert.yml  # Paths relative to tests/common/

# === VARIABLES (optional) ===
variables:
  my_var: value                  # Pre-defined variables

# === DEFAULTS (optional) ===
defaults:
  node: node1                    # Default node for all steps
  wait: 3s                       # Default wait after steps
  expect: success                # Default expected result
  timeout: 30                    # Default timeout (seconds)
  cli:                          # CLI auto-prefixes
    net: "{{network_name}}"

# === SETUP (optional) ===
setup:
  - cli: wallet new -w test      # Preparation steps

# === TEST (required) ===
test:
  - cli: token list              # Main test actions

# === CHECK (optional) ===
check:
  - cli: token info -name TEST   # Result validation
    contains: "TEST"
```

---

## Step Types

### CLIStep
Execute `cellframe-node-cli` command.

```yaml
- cli: token_decl -token TEST -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
  node: node1                    # Node to execute on (default: node1)
  save: full_output              # Save entire output
  save_hash: tx_hash             # Extract and validate hash (0x[hex])
  save_wallet: my_address        # Extract and validate wallet address (base58 + checksum)
  save_node: node_addr           # Extract node address (0x::format)
  wait: 3s                       # Wait after command
  expect: success                # Expected result (success/error/any)
  contains: "SUCCESS"            # Verify output contains string
  timeout: 30                    # Command timeout (seconds)
```

**Save helpers:**
- `save: var` - saves entire output (auto-extracts hash for token_decl/emit/tx_create)
- `save_hash: var` - extracts and validates hash (0x[hex]{64})
- `save_wallet: var` - extracts and validates wallet address (base58 + checksum)
- `save_node: var` - extracts node address (0x::format)

**Examples:**

```yaml
# Extract wallet address (one line!)
- cli: wallet info -w test
  save_wallet: addr

# Extract hash from token creation
- cli: token_decl -token TEST -total_supply 1000000 -certs test_cert
  save_hash: token_hash

# Extract node address
- cli: net get_cur_addr
  save_node: node_addr

# Save full output
- cli: token info -name TEST
  save: full_info
```

**CLI auto-defaults:** Parameters from `defaults.cli` automatically added if command supports them.

### ToolStep
Execute `cellframe-node-tool` command.

```yaml
- tool: cert create test_cert sig_dil
  node: node1
  save: cert_result
  expect: success
  timeout: 30
```

**Note:** Only provide certificate NAME, not path or extension. Tool adds `/opt/cellframe-node/var/lib/ca/` and `.dcert` automatically.

### RPCStep
JSON-RPC call to node.

```yaml
- rpc: net_get_cur_addr
  params: []                     # RPC parameters (list)
  node: node1
  save: rpc_result
  wait: 1s
  expect: success
  timeout: 30
```

**Endpoint:** `http://<node_ip>:8545` (base_rpc_port from config)

### WaitStep
Simple waiting.

```yaml
- wait: 5s                       # Duration: Ns, Nms (e.g., 5s, 500ms, 0s)
```

### WaitForDatumStep
Monitor datum lifecycle (mempool → block → propagation).

```yaml
# Minimal (recommended!)
- wait_for_datum: "{{tx_hash}}"

# Multiple datums
- wait_for_datum:
    - "{{hash1}}"
    - "{{hash2}}"

# With all options (usually not needed!)
- wait_for_datum: "{{tx_hash}}"
  node: node1                    # Node to check (default: node1)
  network: stagenet              # Network name (default: stagenet)
  chain: main                    # Chain name (default: main)
  check_master_nodes: true       # Check masters (default: true)
  timeout_total: 300             # Total timeout (default: 300s)
  timeout_mempool: 60            # Mempool timeout (DEPRECATED - hardcoded 0.5s)
  timeout_verification: 120      # After verification (default: 120s)
  timeout_in_blocks: 180         # After in blocks (default: 180s)
  check_interval: 2              # Check every N seconds (default: 2s)
  save_status: datum_status      # Save final status object
```

**Lifecycle:**
1. **0.5s** - Check mempool (if not found → REJECTED, fail fast!)
2. **30-120s** - Wait for inclusion in block
3. **60-180s** - Wait for propagation across network
4. Returns immediately when done (no wasted time)

**Best Practice:** Use minimal syntax. Defaults are tuned for real network behavior.

### PythonStep
Execute Python code with context access.

```yaml
- python: |
    addr = ctx.get_variable('wallet_addr')
    ctx.set_variable('validated_addr', addr)
    print(f"Processing: {addr}")
  save: python_result             # Save return value
```

**Context API:**
- `ctx.get_variable(name)` - get variable
- `ctx.set_variable(name, value)` - set variable
- `ctx.has_variable(name)` - check existence
- `print()` - output to log

### BashStep
Execute Bash script in node container.

```yaml
- bash: |
    echo "Test data" > /tmp/test.txt
    cat /tmp/test.txt
  node: node1
  save: bash_output
  expect: success
  timeout: 30
```

### StepGroup
Group steps with local defaults.

```yaml
- group: "Wallet Operations"
  defaults:
    node: node2
    wait: 1s
  steps:
    - cli: wallet new -w wallet1    # Uses node2, wait 1s
    - cli: wallet new -w wallet2    # Uses node2, wait 1s
```

---

## Check Types

Executed after `test` section to validate results.

### CLICheck

```yaml
check:
  - cli: token info -name TEST
    node: node1
    contains: "TEST"               # Output should contain
    not_contains: "ERROR"          # Output should NOT contain
    equals: "exact match"          # Exact output match
    timeout: 30
```

### PythonCheck

```yaml
check:
  - python: |
      balance = ctx.get_variable('balance')
      assert int(balance) > 0, "Balance must be positive"
      assert int(balance) < 1000000, "Balance too high"
```

Fails if AssertionError or any exception raised.

### BashCheck

```yaml
check:
  - bash: |
      test -f /tmp/output.txt
      grep -q "SUCCESS" /tmp/output.txt
      [ $(wc -l < /tmp/output.txt) -gt 10 ]
    node: node1
    timeout: 30
```

Fails if exit code != 0.

### RPCCheck

```yaml
check:
  - rpc: net_get_cur_addr
    params: []
    node: node1
    result_contains: "0x"          # Result should contain value
    result_equals: expected_value  # Exact result match
```

---

## Defaults System

Hierarchical defaults with inheritance: **global → section → group → step**

### Global Defaults

```yaml
defaults:
  node: node1
  wait: 3s
  expect: success
  timeout: 60
  cli:
    net: "{{network_name}}"
    token: MYTOKEN

test:
  - cli: token list               # Inherits all defaults
  - cli: wallet list
    node: node2                   # Overrides node
```

### Section Defaults

```yaml
test:
  defaults:                       # Applies only to test section
    node: node2
    wait: 1s
  steps:
    - cli: token list
    - cli: wallet list
```

**Modern syntax:** Use `SectionConfig` format for setup/test/check sections.

### Group Defaults

```yaml
- group: "Token Operations"
  defaults:
    wait: 5s
  steps:
    - cli: token_decl ...
    - cli: token_emit ...
```

### CLI Auto-Defaults

Special `cli:` field for automatic CLI parameter injection:

```yaml
defaults:
  cli:
    net: "{{network_name}}"       # Adds -net stagenet to all CLI commands
    token: MYTOKEN                # Adds -token MYTOKEN
```

**Mechanism:**
1. CLICommandParser parses `cellframe-node-cli help` at startup
2. Builds map of commands → supported options
3. Before executing CLI command, checks if command supports option
4. Adds `-option value` if not already present
5. Never duplicates existing options

**Typical use:** Via `common/set_net_default.yml` include.

---

## Data Extraction

Convenient `save_*` helpers for extracting and validating common data types.

### Save Helpers

```yaml
# Extract wallet address (one line - auto-validates!)
- cli: wallet info -w my_wallet
  save_wallet: wallet_addr

# Extract hash
- cli: token_decl -token TEST -total_supply 1000000 -certs test_cert
  save_hash: token_hash

# Extract node address
- cli: net get_cur_addr
  save_node: node_addr

# Save entire output
- cli: token info -name TEST
  save: full_info
```

### Helper Reference

| Helper | Extracts | Validation | Use Case |
|--------|----------|------------|----------|
| `save_hash` | 0x[hex]{64} | Format check | token_decl, token_emit, tx_create |
| `save_wallet` | Base58 address | Base58 + SHA3-256 checksum | wallet info |
| `save_node` | 0x::format | :: separator check | net get_cur_addr |
| `save` | Entire output | None (auto-hash for token/tx commands) | Any command |

### Examples

```yaml
test:
  # Create wallet and extract address
  - cli: wallet new -w test
  - cli: wallet info -w test
    save_wallet: addr              # ✅ Clean and clear!
  
  # Create token and extract hash
  - cli: token_decl -token T -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
    save_hash: token_hash          # ✅ One line!
  
  # Emit and extract hash
  - cli: token_emit -token T -value 1000 -addr {{addr}} -certs test_cert
    save_hash: emit_hash
  
  # Use extracted values
  - cli: tx_create -token T -from {{emit_hash}}:0 -value 500 -fee 0.1
    save_hash: tx_hash
```

---

## Suite System

Organize related tests into suites with shared setup.

### Structure

```
tests/e2e/token/
├── token.yml                    # Suite descriptor
├── 001_token_decl.yml           # Test scenario
├── 002_token_emit.yml           # Test scenario
└── 003_token_list.yml           # Test scenario
```

### Suite Descriptor

```yaml
suite: "Token Operations Suite"
description: "E2E tests for tokens"
tags: [e2e, token]
version: "1.0"

# Default network for all scenarios
network:
  topology: default

# Common includes - inherited by all scenarios
includes:
  - common/create_test_cert.yml
  - common/set_net_default.yml

# Suite-level setup - executes ONCE before all scenarios
setup:
  - wait: 5s
```

### Execution Flow

1. **Suite discovery** - by directory structure
2. **Snapshot restore** - clean state for suite
3. **Suite setup** - execute descriptor's includes + setup
4. **Scenario execution** - run all .yml files in directory
5. **Artifact collection** - gather logs per suite

### Benefits

- Certificate created once per suite (not per scenario)
- Common setup shared
- Clean state between suites (snapshots)
- Logical grouping

---

## Variable Substitution

**Syntax:** `{{variable_name}}`

**Usage:** Any string field (CLI commands, RPC params, checks, etc.)

**Built-in variables:**
- `{{network_name}}` - from network.name (default: "stagenet")

**Runtime variables:**
- Set via `save:` in steps
- Set via `ctx.set_variable()` in Python code
- Set in `variables:` section

**Example:**

```yaml
variables:
  token_name: MYTOKEN

test:
  - cli: token_decl -token {{token_name}} -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
    save: hash
  
  - cli: token info -name {{token_name}}
    contains: "{{token_name}}"
```

---

## Error Handling

### CLI Errors

Cellframe CLI returns exit code 0 even on errors!

**Detection:** Executor parses JSON/YAML output for `errors:` field.

**Example:**

```yaml
# This will be detected as error even with exit 0!
- cli: tx_create -token TEST -from {{blocked_utxo}}:0 -value 100
  expect: error                  # We WANT error here
  contains: "UTXO is blocked"
```

### Expected Errors

```yaml
- cli: wallet new -w existing_wallet
  expect: error                  # Test that it fails correctly
  contains: "already exists"
```

### Validation Errors

Pydantic validates YAML structure before execution.

**Common errors:**
- `Field required` - missing mandatory field
- `Invalid type` - wrong data type
- `Unknown step type` - typo in step type

---

## Includes System

**Search path:** `tests/common/`

**Merge strategy:** Deep merge, main file has priority, `None` values ignored.

**Common includes:**

```yaml
includes:
  - common/create_test_cert.yml       # Creates test_cert for signing
  - common/set_net_default.yml        # Auto-adds -net parameter
  - common/wallets/create_wallet.yml  # Creates test_wallet with wallet_addr
  - common/networks/single_node.yml   # Minimal topology override
```

**Creating custom include:**

`tests/common/my_include.yml`:
```yaml
setup:
  - cli: token_decl -token {{token_name}} -total_supply {{supply}} -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert

variables:
  token_created: true
```

---

## Best Practices

### ✅ DO

```yaml
# Use includes for common setup
includes:
  - common/create_test_cert.yml

# Use defaults to reduce repetition
defaults:
  node: node1
  wait: 3s

# Use wait_for_datum instead of fixed waits
- cli: token_emit -token TEST -value 1000 -addr {{addr}} -certs test_cert
  save: tx
- wait_for_datum: "{{tx}}"

# Use extract_to for data with validation
- cli: wallet info -w test
  extract_to:
    addr:
      type: wallet_address

# Organize into suites
tests/e2e/token/
├── token.yml                    # Suite descriptor
├── 001_test.yml
└── 002_test.yml
```

### ❌ DON'T

```yaml
# Don't repeat same setup in every test
setup:
  - tool: cert create test_cert sig_dil  # Use suite-level setup instead!

# Don't use fixed waits
- wait: 30s                      # How long? Use wait_for_datum!

# Don't save entire output when you need specific value
- cli: wallet info -w test
  save: full_output              # Use extract_to instead!

# Don't hardcode network name
- cli: token list -net stagenet  # Use -net {{network_name}} or auto-defaults
```

---

## Reference

### Step Type Quick Reference

| Step | Purpose | Key Field |
|------|---------|-----------|
| CLIStep | CLI command | `cli: command` |
| ToolStep | Tool command | `tool: command` |
| RPCStep | JSON-RPC call | `rpc: method` |
| WaitStep | Simple wait | `wait: 5s` |
| WaitForDatumStep | Smart datum wait | `wait_for_datum: hash` |
| PythonStep | Python code | `python: \|` |
| BashStep | Bash script | `bash: \|` |
| StepGroup | Group with defaults | `group: name` |

### Check Type Quick Reference

| Check | Purpose | Key Field |
|-------|---------|-----------|
| CLICheck | CLI output check | `cli: command` |
| PythonCheck | Python assertions | `python: \|` |
| BashCheck | Bash exit code | `bash: \|` |
| RPCCheck | RPC result check | `rpc: method` |

---

## See Also

- **[Tutorial](Tutorial.md)** - Step-by-step guide
- **[Cookbook](Cookbook.md)** - Ready recipes
- **[Examples](../../../examples/)** - Advanced examples
- **[SLC Modules](../../../../.context/modules/testing/)** - Complete technical reference

---

**Version:** 2.0  
**Last Updated:** 2025-10-25  
**Language:** English | [Русский](../../ru/scenarios/Glossary.md)
