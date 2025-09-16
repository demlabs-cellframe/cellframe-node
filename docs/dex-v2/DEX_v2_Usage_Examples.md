# DEX v2 Usage Examples

This document provides practical examples and scenarios for using the DEX v2 service.

## Basic Trading Scenarios

### Scenario 1: Create and list orders (canonical pairs)

```bash
# Create a sell order: SELL -> BUY
srv_dex order create -net riemann -token_sell CELL -token_buy KEL -w alice_wallet -value 1000.0 -rate 0.5 -fee 0.1

# List orders by canonical pair (BASE/QUOTE)
srv_dex orders -net riemann -pair CELL/KEL
```

### Scenario 2: Buy from a specific order

```bash
# Purchase by tail hash
srv_dex purchase -net riemann -order 0xAAAA...1111 -w bob_wallet -value 250.0 -fee 0.1
```

### Scenario 3: Auto-purchase by pair

```bash
# Purchase automatically from best orders with minimum acceptable rate
srv_dex purchase_auto -net riemann -token_sell CELL -token_buy KEL -w charlie_wallet -value 1000.0 -min_rate 0.4 -fee 0.1
```

## Advanced Scenarios

### Scenario 4: Multi-order purchase with optional leftover

```bash
# Purchase from multiple chosen orders
srv_dex purchase_multi -net riemann -orders 0xHHHH...8888,0xIIII...9999 -w frank_wallet -value 1500.0 -fee 0.1
# Or automatic selection with leftover order creation
srv_dex purchase_auto -net riemann -token_sell CELL -token_buy KEL -w david_wallet -value 2000.0 -fee 0.1 -create_leftover_order 1 -min_rate 0.4
```

### Scenario 5: 1‑TX Order Update (owner)

```bash
# Update order parameters in a single transaction (tail is resolved internally)
srv_dex order update -net riemann -order 0xEEEE...5555 -w eve_wallet -rate 0.55 -fee 0.1
# Notes: no payouts to seller in update; only native (network/validator) fees are used.
```

### Scenario 6: Seller-centric views

```bash
# List orders by seller
srv_dex orders_by_seller -net riemann -seller <ADDR>
# Status aggregation by seller
srv_dex status_by_seller -net riemann -seller <ADDR>
# History by seller
srv_dex history_by_seller -net riemann -seller <ADDR> -limit 50
```

## Market Data

```bash
# Order book with summaries and binning
a) srv_dex orderbook -net riemann -pair CELL/KEL -depth 20
b) srv_dex orderbook -net riemann -pair CELL/KEL -depth 20 -tick_price 0.01 -cum 1

# Market rate (SPOT/VWAP) and OHLC buckets
srv_dex market_rate -net riemann -pair CELL/KEL -from 1710000000 -to 1710086400 -bucket 300

# Total volume and bucketed series
srv_dex volume -net riemann -pair CELL/KEL -from 1710000000 -to 1710086400 -bucket 300

# TVL and spread
srv_dex tvl -net riemann -token CELL
srv_dex spread -net riemann -pair CELL/KEL

# Slippage
srv_dex slippage -net riemann -pair CELL/KEL -value 1000.0 -side buy
srv_dex slippage -net riemann -pair CELL/KEL -value 250.0 -side sell
```

## Important Notes

1. Pairs are canonical (BASE/QUOTE); input is auto-canonicalized.
2. Order updates (owner) are single-transaction; in case of race (tail spent) re-run update on the latest tail.
3. If selling native token, buyer’s payout in sell is reduced by native + validator + service_native fees; otherwise payout equals ΣS.
4. Auto-matching uses price ASC then FIFO by ts_created.
