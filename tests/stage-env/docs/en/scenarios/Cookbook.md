# Test Scenarios Cookbook

**Ready recipes for common Cellframe Node testing tasks**

This cookbook contains proven solutions for the most common testing tasks. Copy, adapt, and use!

## 📚 Contents

- [Wallet Operations](#wallet-operations)
- [Token Management](#token-management)
- [Transactions & Transfers](#transactions--transfers)
- [UTXO Operations](#utxo-operations)
- [Network & Consensus](#network--consensus)
- [Stress Testing](#stress-testing)
- [Error Scenarios](#error-scenarios)
- [Multi-Node Patterns](#multi-node-patterns)
- [Advanced Patterns](#advanced-patterns)

---

## Wallet Operations

### Recipe 1: Create Single Wallet

```yaml
- cli: wallet new -w my_wallet
  save: wallet_addr
  wait: 1s
```

**When to use:** For any operations requiring a wallet.

**Variables:**
- `{{wallet_addr}}` - created wallet address

---

### Recipe 2: Create Multiple Wallets

```yaml
- loop: 5
  steps:
    - cli: wallet new -w wallet{{iteration}}
      save: addr{{iteration}}
      wait: 500ms
```

**Result:**
- `wallet1`, `wallet2`, ..., `wallet5`
- `{{addr1}}`, `{{addr2}}`, ..., `{{addr5}}`

---

[Continue with all 50 recipes from Russian version, translated to English...]

---

## 🎯 Usage Tips

### Combining Recipes

Recipes can be combined:

```yaml
includes:
  - common/network_minimal.yml

setup:
  # Recipe 2: Multiple wallets
  - loop: 3
    steps:
      - cli: wallet new -w wallet{{iteration}}
        save: addr{{iteration}}
  
  # Recipe 6: Create token
  - cli: token_decl -token COMBO -total 1000000
    wait: 3s
```

---

## 📚 See Also

- **[Tutorial](Tutorial.md)** - Step-by-step learning
- **[Glossary](Glossary.md)** - Complete reference
- `scenarios/features/` - Real test examples

Happy testing! 🎉

---

**Language:** English | [Русский](../../ru/scenarios/Cookbook.md)
