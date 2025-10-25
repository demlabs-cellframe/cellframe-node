# Test Scenarios Tutorial

**Modern guide for writing declarative E2E tests for Cellframe Node**

Welcome! This tutorial teaches you to write automated tests using YAML-based scenario language. No programming knowledge required.

## 📚 Contents

1. [Introduction](#introduction)
2. [Lesson 1: First Test](#lesson-1-first-test)
3. [Lesson 2: Using Defaults](#lesson-2-using-defaults)
4. [Lesson 3: Variables and Data Extraction](#lesson-3-variables-and-data-extraction)
5. [Lesson 4: Token Operations](#lesson-4-token-operations)
6. [Lesson 5: Reliable Waiting with wait_for_datum](#lesson-5-reliable-waiting-with-wait_for_datum)
7. [Lesson 6: Reusing Components with Includes](#lesson-6-reusing-components-with-includes)
8. [Lesson 7: Test Suites](#lesson-7-test-suites)
9. [Best Practices](#best-practices)

---

## Introduction

### What is a Test Scenario?

A test scenario is a YAML file describing:
- **Metadata** - name, description, tags
- **Network** - topology (usually just `topology: default`)
- **Setup** - preparation steps (optional)
- **Test** - main test actions
- **Check** - result validation (optional)

### Minimal Example

```yaml
name: Version Check
description: Verify CLI responds to version command

network:
  topology: default

test:
  - cli: version
    contains: "Cellframe"
```

This scenario:
1. Uses default network topology (3 root + 3 master + 1 full node)
2. Executes `cellframe-node-cli version` on node1
3. Verifies output contains "Cellframe"

### How to Run?

```bash
# Single scenario
cd tests
./stage-env/stage-env run-tests e2e/my_test.yml

# Entire suite
./stage-env/stage-env run-tests e2e/token/

# Via run.sh (full cycle)
./run.sh
```

---

## Lesson 1: First Test

**Task:** Create a wallet and verify it exists.

**Solution** (`lesson1_wallet.yml`):

```yaml
name: Lesson 1 - Wallet Creation
description: Learn basic CLI commands
tags: [tutorial, lesson1, wallet]

# Use default topology (network is optional - defaults to 'topology: default')
network:
  topology: default

test:
  # Step 1: Create wallet
  - cli: wallet new -w my_first_wallet
    node: node1         # Execute on node1 (default)
    expect: success     # Expect successful result (default)
    wait: 1s            # Wait 1 second after command

  # Step 2: Verify it was created
  - cli: wallet list
    contains: my_first_wallet
```

**What happens:**
1. stage-env restores clean network state from snapshot (~2s)
2. `wallet new` executes via `docker exec node1 cellframe-node-cli wallet new -w my_first_wallet`
3. System waits 1 second
4. `wallet list` executes
5. Output checked for "my_first_wallet"

**💡 Key Points:**
- `node: node1` is default - can be omitted
- `expect: success` is default - can be omitted  
- `wait: 1s` gives time for operation to complete

---

## Lesson 2: Using Defaults

**Task:** Reduce repetition with hierarchical defaults.

**Without defaults:**

```yaml
test:
  - cli: token list
    node: node1
    wait: 3s
  
  - cli: wallet list
    node: node1
    wait: 3s
  
  - cli: version
    node: node1
    wait: 3s
```

**With defaults:**

```yaml
# Global defaults - apply to all steps
defaults:
  node: node1
  wait: 3s

test:
  - cli: token list
  - cli: wallet list
  - cli: version
  
  # Override for specific step
  - cli: token info -name TEST
    wait: 10s    # This step waits 10s instead of 3s
```

**Benefits:**
- Less repetition
- Easier to maintain
- Clear intent

**Defaults hierarchy:**
1. **Global** (`defaults:` at top level)
2. **Section** (`setup:` / `test:` / `check:` can have own defaults)
3. **Group** (group steps with local defaults)
4. **Step** (individual step params override everything)

---

## Lesson 3: Variables and Data Extraction

**Task:** Extract wallet address and use it in later steps.

**Modern approach with extract_to:**

```yaml
name: Lesson 3 - Data Extraction
description: Extract and use wallet address

network:
  topology: default

test:
  # Step 1: Create wallet
  - cli: wallet new -w test_wallet
  
  # Step 2: Get wallet address with automatic validation
  - cli: wallet info -w test_wallet
    extract_to:
      my_address:
        type: wallet_address  # Auto-pattern + validation!
  
  # Step 3: Use extracted address
  - cli: balance -addr {{my_address}}
    save: balance_result

check:
  - python: |
      addr = ctx.get_variable('my_address')
      assert addr, "Address should be extracted"
      assert addr.startswith('W'), "Cellframe addresses start with 'W'"
```

**Extract Types:**
- `wallet_address` - Cellframe wallet (base58, auto-validated)
- `node_address` - Node address (0x::format)
- `hash` - Transaction/token hash (0x[hex])
- `number` - Numeric values
- `token_name` - Token identifier
- `raw` - Custom regex pattern

---

## Lesson 4: Token Operations

**Task:** Create token, emit, and verify.

```yaml
name: Lesson 4 - Token Operations
description: Complete token workflow

# Include common components
includes:
  - common/create_test_cert.yml  # Creates test_cert for signing
  - common/set_net_default.yml   # Auto-adds -net parameter

setup:
  # Create wallet for receiving tokens
  - cli: wallet new -w my_wallet
  
  - cli: wallet info -w my_wallet
    extract_to:
      wallet_addr:
        type: wallet_address

test:
  # Step 1: Declare token
  - cli: token_decl -token LESSON4 -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
    save: token_hash
    wait: 3s
  
  # Step 2: Emit tokens
  - cli: token_emit -token LESSON4 -value 10000 -addr {{wallet_addr}} -certs test_cert
    save: emission_tx
    wait: 3s

check:
  # Verify token exists
  - cli: token info -name LESSON4
    contains: "LESSON4"
```

**💡 Key Points:**
- `create_test_cert.yml` creates certificate ONCE at suite level (not per scenario)
- `set_net_default.yml` adds `-net stagenet` automatically
- `-certs test_cert` explicitly used for signing operations
- `save:` stores hash automatically for token/emission commands

---

## Lesson 5: Reliable Waiting with wait_for_datum

**Task:** Wait for transaction to be processed in blockchain.

**❌ Old way (unreliable):**

```yaml
test:
  - cli: token_emit -token TEST -value 1000 -addr {{addr}} -certs test_cert
    save: tx_hash
  
  - wait: 30s  # How long? Too short = flaky test, too long = slow
```

**✅ Modern way:**

```yaml
test:
  - cli: token_emit -token TEST -value 1000 -addr {{addr}} -certs test_cert
    save: tx_hash
  
  # Intelligent waiting - monitors actual datum lifecycle
  - wait_for_datum: "{{tx_hash}}"
```

**How wait_for_datum works:**
1. **0.5s** - checks if datum appears in mempool (if not → REJECTED)
2. **30s** - waits for datum to be included in block
3. **60s** - waits for block to propagate across network
4. Returns immediately when done (no wasted time!)

**Example with multiple datums:**

```yaml
test:
  - cli: token_decl -token T1 -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
    save: token1
  
  - cli: token_decl -token T2 -total_supply 2000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
    save: token2
  
  # Wait for both tokens
  - wait_for_datum:
      - "{{token1}}"
      - "{{token2}}"
```

---

## Lesson 6: Reusing Components with Includes

**Task:** Use common components to reduce duplication.

**Common includes in `tests/common/`:**
- `create_test_cert.yml` - Creates temporary certificate for signing
- `set_net_default.yml` - Auto-adds `-net {{network_name}}`
- `wallets/create_wallet.yml` - Creates test wallet
- `networks/single_node.yml` - Minimal topology override

**Example:**

```yaml
name: Lesson 6 - Includes
description: Reusable components

includes:
  - common/create_test_cert.yml
  - common/set_net_default.yml
  - common/wallets/create_wallet.yml

# Now we have:
# - test_cert variable
# - wallet_addr variable
# - -net auto-added to CLI commands

test:
  # certificate and -net added automatically!
  - cli: token_decl -token INC -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
```

**Creating your own include:**

`tests/common/my_template.yml`:
```yaml
# Reusable template for token creation

setup:
  - cli: token_decl -token {{token_name}} -total_supply {{supply}} -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert

variables:
  token_created: true
```

Usage:
```yaml
includes:
  - common/my_template.yml

variables:
  token_name: MYTOKEN
  supply: 5000000

test:
  - cli: token list
    contains: "{{token_name}}"
```

---

## Lesson 7: Test Suites

**Task:** Organize related tests into suites with shared setup.

**Suite structure:**
```
tests/e2e/token/
├── token.yml              # Suite descriptor
├── 001_token_decl.yml     # Test scenario
├── 002_token_emit.yml     # Test scenario
└── 003_token_list.yml     # Test scenario
```

**Suite descriptor** (`token.yml`):

```yaml
suite: "Token Operations Suite"
description: "E2E tests for token lifecycle"
tags: [e2e, token]

# Default network for all scenarios in this suite
network:
  topology: default

# Common includes - applied to all scenarios
includes:
  - common/create_test_cert.yml
  - common/set_net_default.yml

# Suite-level setup - executes ONCE before all scenarios
setup:
  - wait: 5s
```

**Individual scenario** (`001_token_decl.yml`):

```yaml
name: Token Declaration
description: Test token creation

# NO includes needed! Inherited from suite descriptor
# NO network needed! Inherited from suite

test:
  - cli: token_decl -token TEST -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert
    save: token_hash

check:
  - cli: token info -name TEST
    contains: "TEST"
```

**Benefits:**
- Certificate created ONCE per suite (not per scenario)
- Common setup shared across scenarios
- Clean network state restored between suites (via snapshots)
- Logical grouping of related tests

---

## Best Practices

### 1. Use Defaults Effectively

```yaml
# ✅ Good
defaults:
  node: node1
  wait: 3s

test:
  - cli: token list
  - cli: wallet list
  - cli: version

# ❌ Bad - repetitive
test:
  - cli: token list
    node: node1
    wait: 3s
  - cli: wallet list
    node: node1
    wait: 3s
```

### 2. Use wait_for_datum Instead of Fixed Waits

```yaml
# ✅ Good - reliable and fast
- cli: token_emit -token TEST -value 1000 -addr {{addr}} -certs test_cert
  save: tx
- wait_for_datum: "{{tx}}"

# ❌ Bad - slow and unreliable
- cli: token_emit -token TEST -value 1000 -addr {{addr}} -certs test_cert
- wait: 30s  # Too long? Too short?
```

### 3. Extract Data Properly

```yaml
# ✅ Good - type-safe with validation
- cli: wallet info -w my_wallet
  extract_to:
    addr:
      type: wallet_address  # Auto-validates!

# ❌ Bad - saves entire output
- cli: wallet info -w my_wallet
  save: wallet_output
  # Now you need to parse it manually in Python
```

### 4. Use Includes for Common Setup

```yaml
# ✅ Good - reusable
includes:
  - common/create_test_cert.yml
  - common/set_net_default.yml

# ❌ Bad - duplicate setup in every test
setup:
  - tool: cert create test_cert sig_dil
# ... same in 50 tests
```

### 5. Group Tests into Suites

```yaml
# ✅ Good - suite descriptor
# tests/e2e/token.yml
suite: "Token Suite"
includes:
  - common/create_test_cert.yml

# Then individual tests don't need to repeat includes

# ❌ Bad - every test includes same things
# 001_test.yml, 002_test.yml, 003_test.yml all have:
includes:
  - common/create_test_cert.yml
```

### 6. Be Explicit with Required Parameters

```yaml
# ✅ Good - explicit and clear
- cli: token_decl -token TEST -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs test_cert

# ❌ Bad - relying on hidden defaults
- cli: token_decl -token TEST -total_supply 1000000
# Where are -decimals, -signs_total? Unclear!
```

### 7. Use Descriptive Names

```yaml
# ✅ Good
name: "Token Transfer Between Two Wallets"
description: "Create token, emit to wallet1, transfer to wallet2, verify balances"

# ❌ Bad
name: "Test 001"
description: "Token test"
```

---

## 🎓 Congratulations!

You now know:
- ✅ Basic scenario structure
- ✅ Using defaults to reduce duplication
- ✅ Extracting data with validation
- ✅ Token operations workflow
- ✅ Reliable waiting with wait_for_datum
- ✅ Reusing components with includes
- ✅ Organizing tests into suites

### What's Next?

1. **[Cookbook](Cookbook.md)** - Ready recipes for common patterns
2. **[Glossary](Glossary.md)** - Complete language reference
3. **[Examples](../../../examples/)** - Advanced examples

### Reference Materials

- **Real tests:** `tests/e2e/`, `tests/functional/`
- **Common includes:** `tests/common/`
- **Suite examples:** `tests/e2e/*.yml` (suite descriptors)

Good luck testing! 🚀

---

**Last updated:** 2025-10-25
**Language:** English | [Русский](../../ru/scenarios/Tutorial.md)
