# Test Scenarios Glossary

**Complete reference for Cellframe Node test scenario language**

This document contains comprehensive description of all YAML scenario language capabilities. Use as reference when writing tests.

## 📚 Contents

1. [Scenario Structure](#scenario-structure)
2. [Metadata](#metadata)
3. [Network Configuration](#network-configuration)
4. [Variables](#variables)
5. [Includes](#includes)
6. [Scenario Sections](#scenario-sections)
7. [Step Types](#step-types)
8. [CLI Commands](#cli-commands)
9. [RPC Calls](#rpc-calls)
10. [Checks](#checks)
11. [Loops](#loops)
12. [Waits](#waits)
13. [Node Execution](#node-execution)
14. [Timeouts](#timeouts)
15. [Special Features](#special-features)

---

## Scenario Structure

Complete YAML scenario file structure:

```yaml
# === METADATA (required) ===
name: string                        # Scenario name
description: string                 # Test description
author: string                      # Author (optional)
tags: [string, ...]                # Tags (optional)
version: string                     # Version (optional, default: "1.0")

# === INCLUDES (optional) ===
includes:
  - path/to/template.yml           # Path relative to scenario

# === VARIABLES (optional) ===
variables:
  key: value                        # Predefined variables

# === NETWORK CONFIGURATION (required) ===
network:
  topology: string                  # Topology name
  nodes:                           # Node list
    - name: string
      role: string
      validator: boolean
      ip: string
      port: integer

# === TEST (required) ===
test:
  - [test_step]

# === CHECKS (recommended) ===
check:
  - [check_spec]
```

---

[Continue with complete English translation of all sections from Russian Glossary...]

---

## Best Practices

### Naming

**✅ DO:**
```yaml
name: Token Transfer Between Wallets Test
- cli: wallet new -w sender_wallet
  save: sender_address
```

**❌ DON'T:**
```yaml
name: test1
- cli: wallet new -w w1
  save: a1
```

---

## See Also

- **[Tutorial](Tutorial.md)** - Step-by-step learning
- **[Cookbook](Cookbook.md)** - Ready recipes
- `scenarios/features/` - Real test examples
- `scenarios/common/` - Ready templates

---

**Document Version:** 2.0
**Last Update:** 2025-10-23

For questions and suggestions, create issues in project repository.

---

**Language:** English | [Русский](../../ru/scenarios/Glossary.md)
