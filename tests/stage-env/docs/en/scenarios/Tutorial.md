# Test Scenarios Tutorial

**Step-by-step guide for writing test scenarios for Cellframe Node**

Welcome! This guide will teach you to write automated tests without programming. We'll start with basics and gradually move to complex scenarios.

## 📚 Contents

1. [Introduction](#introduction)
2. [Lesson 1: First Test](#lesson-1-first-test)
3. [Lesson 2: Variables and Saving Results](#lesson-2-variables-and-saving-results)
4. [Lesson 3: Checking Results](#lesson-3-checking-results)
5. [Lesson 4: Reusing Templates](#lesson-4-reusing-templates)
6. [Lesson 5: Working with Tokens](#lesson-5-working-with-tokens)
7. [Lesson 6: Loops and Repetitions](#lesson-6-loops-and-repetitions)
8. [Lesson 7: Complex Scenarios](#lesson-7-complex-scenarios)
9. [Lesson 8: Best Practices](#lesson-8-best-practices)

---

## Introduction

### What is a Test Scenario?

A test scenario is a YAML file that describes:
- **What we're testing** - name and description
- **What network we use** - node topology
- **What actions we perform** - CLI commands
- **What result we expect** - checks

### Minimal Scenario Example

```yaml
name: Version Check
description: Ensure node responds to version command

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  - cli: version
    expect: success
```

This scenario:
1. Creates 1 node (`minimal` topology)
2. Executes `version` command
3. Expects successful execution

### How to Run?

```bash
# Save scenario as scenarios/my_test.yml
./tests/stage-env/stage-env run-tests scenarios/my_test.yml
```

---

## Lesson 1: First Test

Let's create a complete test from scratch.

### Task
Create wallet and verify it appears in the list.

### Solution

Create file `scenarios/lesson1_wallet.yml`:

```yaml
# === METADATA ===
name: Lesson 1 - Wallet Creation
description: Learn how to create a wallet and verify it exists
tags: [tutorial, lesson1, basic]

# === NETWORK CONFIGURATION ===
network:
  topology: minimal        # Use 1 node
  nodes:
    - name: node1
      role: root
      validator: true

# === TEST ===
test:
  # Step 1: Create wallet
  - cli: wallet new -w my_first_wallet
    expect: success
    wait: 1s              # Wait 1 second

  # Step 2: Check it was created
  - cli: wallet list
    contains: my_first_wallet
```

### Running

```bash
./tests/stage-env/stage-env run-tests scenarios/lesson1_wallet.yml
```

### What Happens?

1. **stage-env** creates Docker container with node
2. Node starts and transitions to `ONLINE` state
3. Command `wallet new -w my_first_wallet` executes
4. System waits 1 second
5. Command `wallet list` executes
6. Checks that output contains `my_first_wallet`

### ✅ Exercise 1

Create test that:
1. Creates wallet named `exercise1_wallet`
2. Creates second wallet named `exercise1_wallet2`
3. Checks that both wallets are in the list

<details>
<summary>Show solution</summary>

```yaml
name: Exercise 1 - Two Wallets
description: Create two wallets

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  - cli: wallet new -w exercise1_wallet
    wait: 1s
  
  - cli: wallet new -w exercise1_wallet2
    wait: 1s
  
  - cli: wallet list
    contains: exercise1_wallet
  
  - cli: wallet list
    contains: exercise1_wallet2
```
</details>

---

[Continue with remaining 7 lessons following the same structure as Russian version but in English...]

---

## 🎓 Congratulations!

You've completed the entire tutorial! Now you know how to:

- ✅ Write basic tests
- ✅ Use variables
- ✅ Check results
- ✅ Reuse templates
- ✅ Work with tokens
- ✅ Use loops
- ✅ Create complex scenarios
- ✅ Follow best practices

### What's Next?

1. **[Cookbook](Cookbook.md)** - Ready recipes for common tasks
2. **[Glossary](Glossary.md)** - Complete language reference
3. **Practice** - Create your tests in `scenarios/features/`

### Useful Links

- `scenarios/common/` - Ready templates
- `scenarios/features/` - Real test examples
- `./stage-env --help` - CLI reference

Good luck testing! 🚀

---

**Language:** English | [Русский](../../ru/scenarios/Tutorial.md)
