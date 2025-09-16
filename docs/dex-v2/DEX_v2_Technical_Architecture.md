# DEX v2 Technical Architecture

## Overview

DEX v2 implements a decentralized exchange mechanism using conditional outputs (OUT_COND) with a new subtype SRV_DEX. This document describes the technical implementation details.

## Core Concepts

### Order Structure

Each DEX order is represented as a conditional output with the following data stored in the union:

```c
struct srv_dex {
    dap_chain_net_id_t sell_net_id;      // Network ID for sell token
    dap_chain_net_id_t buy_net_id;       // Network ID for buy token
    char buy_token[DAP_CHAIN_TICKER_SIZE_MAX]; // Token ticker to buy
    uint256_t rate;                       // Exchange rate (buy per sell)
    dap_chain_addr_t seller_addr;        // Seller's address
    dap_hash_fast_t order_root_hash;     // Root of order chain
    uint256_t min_fill;                   // Minimum fill amount
    uint16_t fill_policy;                 // Fill policy flags
    uint16_t version;                     // Protocol version
    uint32_t flags;                       // Additional flags
}
```

The `header.value` field contains the remaining sell amount.

### Transaction Types

1. **ORDER** - Creates initial sell order
   - Has OUT_COND(SRV_DEX) output
   - No IN_COND inputs

2. **EXCHANGE** - Executes purchase against orders
   - Has IN_COND inputs consuming previous OUT_COND(SRV_DEX)
   - May have residual OUT_COND(SRV_DEX) for partial fills

3. **INVALIDATE** - Cancels order by owner
   - Has IN_COND consuming OUT_COND(SRV_DEX)
   - No SRV_DEX outputs

### Order Chains

Orders form chains of transactions:
- **Head**: First transaction creating the order (order_root_hash is empty)
- **Tail**: Latest transaction in chain (current state)
- Each exchange transaction consumes previous tail and may create new tail

## Partial Execution Rules

### Single Order Partial Fill
- Buyer requests less than available amount
- Transaction creates residual OUT_COND with remaining amount
- Residual OUT_COND references original order via order_root_hash

### Multi-Order Execution (M:1)
Multiple seller orders can be consumed in one transaction:
- Orders filled sequentially in full amounts
- Only the first input (IN_COND[0]) can be partial
- Maximum one residual OUT_COND allowed
- Partial input must be added first in transaction

### Buyer Leftover Orders
When all seller orders are consumed but buyer has remaining funds:
- New OUT_COND(SRV_DEX) created for buyer's leftover
- Only allowed when NO partial inputs exist
- Prevents N:M complexity

## Verification Rules

The verificator enforces these invariants:

1. **Unique Trading Pair**: All inputs must be for same sell/buy token pair
2. **Exact Payouts**: Each seller receives exactly S_i × rate_i
3. **Single Residual**: Maximum one residual OUT_COND per transaction
4. **Partial Position**: Only IN[0] can be partial
5. **Fill Policies**: Respect AON, MIN_FILL constraints
6. **Expiry Check**: Expired orders cannot be used
7. **Owner Only**: Invalidation requires owner signature

## Fee Handling

Three types of fees are supported:

1. **Network Fee**: Paid to network address in native token
2. **Service Fee**: DEX service fee with four modes:
   - NATIVE_FIXED: Fixed amount in native token
   - NATIVE_PERCENT: Percentage of trade in native
   - OWN_FIXED: Fixed amount in buy token
   - OWN_PERCENT: Percentage of trade in buy token
3. **Validator Fee**: Additional incentive via FEE output

### Single vs Dual Channel

**Single Channel** (sell_token == native):
- All fees deducted from sell amount
- Buyer receives: sell_amount - total_fees

**Dual Channel** (sell_token != native):
- Fees paid from separate inputs
- Buyer receives full sell amount

## Order Matching Algorithm

The cache maintains orders indexed by:
- Trading pair (sell_token, buy_token, networks)
- Tail hash for quick lookup
- Rate for sorted access

Matching process:
1. Filter by trading pair and minimum rate
2. Sort by rate (best first)
3. Within same rate, use FIFO (earliest first)
4. Fill orders sequentially until budget exhausted

## Cache Management

Orders cached with:
```c
struct order_cache_entry {
    dap_hash_fast_t root;          // Original order hash
    dap_hash_fast_t tail;          // Current tail hash
    uint256_t value;               // Current amount
    uint256_t rate;                // Exchange rate
    dap_chain_addr_t seller_addr;  // Seller address
    uint16_t fill_policy;          // Fill constraints
    dap_time_t ts_created;         // Creation time
    dap_time_t ts_expires;         // Expiration time
}
```

Cache updates on:
- New order creation
- Order execution (partial or full)
- Order invalidation
- Chain reorganization

## Security Considerations

1. **DoS Protection**:
   - Limited to 128 orders per purchase_auto
   - Enforces single residual OUT_COND rule
   - Validates all arithmetic operations

2. **Economic Security**:
   - Exact value verification prevents fund loss
   - Rate immutability prevents manipulation
   - Owner-only cancellation prevents griefing

3. **Consensus Safety**:
   - Deterministic order matching
   - No reliance on external data
   - Verificator ensures all rules enforced

## Implementation Limits

- Maximum IN_COND per transaction: Should be limited (recommended: 16)
- Maximum transaction size: Should be enforced
- Order cache size: Automatically managed
- Decimal precision: uint256_t with fixed point arithmetic


