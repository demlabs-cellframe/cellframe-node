# DEX v2 CLI Reference

## Overview

DEX v2 (Decentralized Exchange) service provides a trustless token exchange mechanism within the Cellframe network. This document describes all available CLI commands for interacting with the DEX service.

## General Command Structure

All DEX commands follow this pattern:
```
srv_dex <command> -net <network_name> [options]
```

The `-net` parameter is mandatory for all commands and specifies the network where the operation will be executed.

## Commands

### 1. order create

Creates a new sell order on the DEX.

**Syntax:**
```
srv_dex order create -net <network> -token_sell <ticker> -token_buy <ticker> -w <wallet> -value <amount> -rate <rate> -fee <fee>
```

**Parameters:**
- `-net` - Network name (required)
- `-token_sell` - Ticker of the token you want to sell (required)
- `-token_buy` - Ticker of the token you want to receive (required)
- `-w` - Wallet name containing the tokens to sell (required)
- `-value` - Amount of tokens to sell in decimal format (required)
- `-rate` - Exchange rate: how many buy tokens per one sell token (required)
- `-fee` - Transaction fee in native tokens (required)

**Example:**
```
srv_dex order create -net riemann -token_sell CELL -token_buy KEL -w my_wallet -value 1000.0 -rate 0.5 -fee 0.1
```

This creates an order to sell 1000 CELL tokens in exchange for KEL tokens at a rate of 0.5 KEL per CELL (total 500 KEL).

**Response:**
Returns a transaction hash if successful, or an error code with description.

### 2. order remove

Cancels an existing order and returns the remaining tokens to the owner.

**Syntax:**
```
srv_dex order remove -net <network> -order <order_hash> -w <wallet> -fee <fee>
```

**Parameters:**
- `-net` - Network name (required)
- `-order` - Hash of the order to remove (can be root or tail hash) (required)
- `-w` - Wallet that created the order (required)
- `-fee` - Transaction fee in native tokens (required)

**Example:**
```
srv_dex order remove -net riemann -order 0x1234...abcd -w my_wallet -fee 0.1
```

**Notes:**
- Only the order owner can remove it
- The command automatically finds the tail (latest state) of the order chain
- All remaining tokens are returned to the owner's wallet

### 3. orders

Lists all active orders for a specific trading pair.

**Syntax:**
```
srv_dex orders -net <network> -pair <BASE/QUOTE>
```

**Parameters:**
- `-net` - Network name (required)
- `-pair` - Canonical pair BASE/QUOTE (order of tokens will be canonicalized automatically)

**Example:**
```
srv_dex orders -net riemann -pair CELL/KEL
```

**Response:**
Returns a JSON array of orders with the following fields for each order:
- `root` - Original order hash
- `tail` - Current state hash (use this for purchases)
- `rate` - Exchange rate
- `value_sell` - Remaining amount available for purchase

### 4. status

Shows summary statistics for a trading pair.

**Syntax:**
```
srv_dex status -net <network> -pair <BASE/QUOTE>
```

**Parameters:**
- `-net` - Network name (required)
- `-pair` - Canonical pair BASE/QUOTE (order of tokens will be canonicalized automatically)

**Example:**
```
srv_dex status -net riemann -pair CELL/KEL
```

**Response:**
Returns JSON with:
- `pair` - Trading pair in format "SELL/BUY"
- `count` - Number of active orders

### 5. history

Shows the transaction history of a specific order.

**Syntax:**
```
srv_dex history -net <network> -order <order_hash>
```

**Parameters:**
- `-net` - Network name (required)
- `-order` - Order hash (root or any transaction in the chain) (required)

**Example:**
```
srv_dex history -net riemann -order 0x1234...abcd
```

**Response:**
Returns a chronological list of all transactions related to this order, including:
- Order creation
- Partial or full exchanges
- Invalidation (if applicable)

### 6. purchase

Executes a purchase against a single specific order.

**Syntax:**
```
srv_dex purchase -net <network> -order <order_hash> -w <wallet> -value <amount> -fee <fee>
```

**Parameters:**
- `-net` - Network name (required)
- `-order` - Order hash to purchase from (use tail hash from orders list) (required)
- `-w` - Wallet containing buy tokens (required)
- `-value` - Amount of buy tokens to spend (required)
- `-fee` - Transaction fee in native tokens (required)

**Example:**
```
srv_dex purchase -net riemann -order 0x5678...efgh -w my_wallet -value 250.0 -fee 0.1
```

**Notes:**
- The order can be partially filled if the requested amount is less than available
- The system automatically calculates how many sell tokens you'll receive based on the order's rate

### 7. purchase_multi

Executes a purchase against multiple orders simultaneously.

**Syntax:**
```
srv_dex purchase_multi -net <network> -orders <hash1,hash2,...> -w <wallet> -value <amount> -fee <fee> [-create_leftover_order 0|1] [-leftover_rate <rate>]
```

**Parameters:**
- `-net` - Network name (required)
- `-orders` - Comma-separated list of order hashes (required)
- `-w` - Wallet containing buy tokens (required)
- `-value` - Total amount of buy tokens to spend (required)
- `-fee` - Transaction fee in native tokens (required)
- `-create_leftover_order` - If 1, creates a new buy order with any leftover funds (optional, default: 0)
- `-leftover_rate` - Rate for the new buyer order if created (optional, uses last order's rate if not specified)

**Example:**
```
srv_dex purchase_multi -net riemann -orders 0x1111...aaaa,0x2222...bbbb,0x3333...cccc -w my_wallet -value 1000.0 -fee 0.1 -create_leftover_order 1
```

**Notes:**
- Orders are filled in the sequence provided
- Only the last order can be partially filled
- All orders must be for the same trading pair
- If leftover order creation is enabled, it only works when all seller orders are fully consumed

### 8. purchase_auto

Automatically finds and executes purchases against the best available orders for a trading pair.

**Syntax:**
```
srv_dex purchase_auto -net <network> -token_sell <ticker> -token_buy <ticker> -w <wallet> -value <amount> [-min_rate <rate>] [-fee <fee>] [-create_leftover_order 0|1]
```

**Parameters:**
- `-net` - Network name (required)
- `-token_sell` - Token you want to receive (required)
- `-token_buy` - Token you want to spend (required)
- `-w` - Wallet containing buy tokens (required)
- `-value` - Amount of buy tokens to spend (required)
- `-min_rate` - Minimum acceptable exchange rate (optional, accepts any rate if not specified)
- `-fee` - Transaction fee in native tokens (optional, default: 0)
- `-create_leftover_order` - If 1, creates a new buy order with leftover funds (optional, default: 0)

**Example:**
```
srv_dex purchase_auto -net riemann -token_sell CELL -token_buy KEL -w my_wallet -value 1000.0 -min_rate 0.45 -fee 0.1
```

**Response:**
Returns detailed JSON with:
- `tx_hash` - Transaction hash
- `matches` - Array of matched orders with execution details
- `totals` - Summary of total tokens exchanged

**Notes:**
- Orders are selected by best rate first, then by creation time (FIFO)
- Maximum 128 orders can be matched in a single transaction
- Only orders meeting the minimum rate requirement are considered

## Order Fill Policies

When creating orders, the system uses fill policies to control partial execution:

1. **PARTIAL_OK** (default) - Order can be partially filled
2. **AON (All-or-None)** - Order must be filled completely or not at all
3. **MIN_FILL** - Partial fills must meet a minimum amount threshold

Currently, all orders are created with PARTIAL_OK policy.

## Fee Structure

DEX transactions involve several types of fees:

1. **Network Fee** - Paid to the network validators (in native tokens)
2. **Service Fee** - DEX service fee (configurable by network)
3. **Validator Fee** - Additional validator incentive (specified in `-fee` parameter)

When the sell token is the native token, fees are deducted from the transaction amount. Otherwise, fees are paid separately.

## Error Codes

Common error codes returned by DEX commands:

- `INVALID_ARGUMENT` - Missing or invalid parameters
- `TOKEN_TICKER_NOT_FOUND` - Specified token doesn't exist on the network
- `NOT_ENOUGH_CASH` - Insufficient balance for the operation
- `NOT_OWNER` - Attempting to remove an order you don't own
- `COMPOSE_TX` - Transaction composition failed
- `MEMPOOL_PUT` - Failed to submit transaction to mempool

## Best Practices

1. Always use the tail hash from `orders` command when purchasing
2. Check order rates and amounts before executing purchases
3. Consider using `purchase_auto` for best rates when buying common pairs
4. Set appropriate fees based on network congestion
5. Use `history` command to track order execution status
