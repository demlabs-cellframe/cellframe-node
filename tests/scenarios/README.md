# Test Scenarios

YAML-based test scenarios for Cellframe Node E2E testing.

## Directory Structure

```
scenarios/
├── common/              # Reusable templates
│   ├── network_minimal.yml    # Single node network
│   ├── network_full.yml       # 4-node network
│   └── wallet_setup.yml       # Wallet creation
├── features/            # Feature-specific tests
│   └── arbitrage_bypass_test.yml
└── templates/           # Additional templates (future)
```

## Template Library

### Network Templates

**`common/network_minimal.yml`**
- Single root node
- Minimal setup for basic tests
- Use when: Testing simple CLI commands

**`common/network_full.yml`**
- 4 nodes (3 validators + 1 full node)
- Complete network topology
- Use when: Testing consensus, networking, multi-node scenarios

### Setup Templates

**`common/wallet_setup.yml`**
- Creates `test_wallet`
- Exports address to `{{wallet_addr}}` variable
- Use when: Tests require wallet operations

## Writing Scenarios

### Basic Structure

```yaml
name: My Test
description: What this test does
author: Your Name
tags: [category, priority]

# Include reusable configs
includes:
  - common/network_minimal.yml
  - common/wallet_setup.yml

# Setup phase (optional)
setup:
  - cli: command1
    save: variable_name
  - cli: command2

# Test phase (required)
test:
  - cli: command_to_test
    expect: success
    contains: "expected output"

# Check phase (optional)
check:
  - cli: verification_command
    contains: "expected result"
```

### CLI Commands

Execute cellframe-node-cli commands:

```yaml
- cli: wallet new -w my_wallet
  save: wallet_addr    # Save output to variable
  wait: 3s             # Wait after command
  expect: success      # Expected result (success/error/any)
  contains: "Created"  # Check output contains text
  timeout: 30          # Command timeout in seconds
```

### JSON-RPC Calls

Call JSON-RPC methods:

```yaml
- rpc: eth_blockNumber
  params: []
  save: block_num
  expect: success
```

### Variables

Use variables with `{{variable_name}}` syntax:

```yaml
- cli: token_emit -value 1000 -addr {{wallet_addr}}
  save: tx_hash

- cli: tx_info -tx {{tx_hash}}
```

### Wait Steps

Wait for duration:

```yaml
- wait: 5s   # 5 seconds
- wait: 100ms  # 100 milliseconds
- wait: 2m   # 2 minutes
```

### Loops

Repeat steps multiple times:

```yaml
- loop: 10
  steps:
    - cli: tx_create -value {{i * 100}}
    - wait: 1s
```

Loop variables:
- `{{i}}` - iteration index (0-based)
- `{{iteration}}` - iteration number (1-based)

### Checks

Verify results:

```yaml
check:
  # Contains check
  - cli: wallet list
    contains: "my_wallet"
  
  # Not contains check
  - cli: token info -token TEST
    not_contains: "error"
  
  # Exact match
  - cli: net status
    equals: "connected"
```

## Running Scenarios

### Via stage-env

```bash
# Run all scenarios
./tests/stage-env/stage-env run-tests tests/scenarios

# Run specific feature
./tests/stage-env/stage-env run-tests tests/scenarios/features/arbitrage_bypass_test.yml
```

### Via tests/run.sh

```bash
# Run E2E tests (includes scenarios)
./tests/run.sh --e2e

# Run with cleanup
./tests/run.sh --e2e --clean
```

## Best Practices

1. **Use Templates**: Reuse common setups from `common/`
2. **Descriptive Names**: Use clear, self-explanatory scenario names
3. **Add Tags**: Tag scenarios by feature, priority, duration
4. **Document Steps**: Add comments explaining complex operations
5. **Variable Naming**: Use descriptive variable names
6. **Wait Times**: Add appropriate waits after state-changing operations
7. **Verify Results**: Always add checks to verify test outcomes

## Example: Complete Scenario

```yaml
name: Token Transfer Test
description: Create token, emit, and transfer between wallets
author: QA Team
tags: [tokens, transfer, basic]

includes:
  - common/network_minimal.yml

setup:
  - cli: wallet new -w wallet1
    save: addr1
  - cli: wallet new -w wallet2
    save: addr2
  - cli: token_decl -token TEST -total 1000000
    save: token_hash
    wait: 3s

test:
  - cli: token_emit -token TEST -value 10000 -addr {{addr1}}
    save: emission
    wait: 3s
  
  - cli: transfer -token TEST -to {{addr2}} -value 5000
    expect: success
    wait: 3s

check:
  - cli: balance -addr {{addr1}} -token TEST
    contains: "5000"
  
  - cli: balance -addr {{addr2}} -token TEST
    contains: "5000"
```

## Troubleshooting

### Scenario Not Found
Check file path relative to `tests/scenarios/`

### Variable Undefined
Ensure variable is defined in `setup` before use in `test`

### Command Timeout
Increase `timeout` parameter or check node status

### Include Not Found
Verify include path is relative to scenario file

## Contributing

When adding new scenarios:

1. Place in appropriate directory (`features/` for feature tests)
2. Follow naming convention: `feature_name_test.yml`
3. Add comprehensive description and tags
4. Include setup and cleanup steps
5. Add to this README if creating new templates

