# DEX v2 Documentation

This directory contains comprehensive documentation for the DEX v2 (Decentralized Exchange) service in Cellframe.

## Documentation Structure

### User Documentation

1. **[CLI Reference](DEX_v2_CLI_Reference.md)**
   - Complete command reference with syntax and parameters
   - Detailed explanation of each command
   - Error codes and their meanings

2. **[Usage Examples](DEX_v2_Usage_Examples.md)**
   - Practical scenarios and use cases
   - Step-by-step tutorials
   - Common patterns and best practices

### Technical Documentation

3. **[Technical Architecture](DEX_v2_Technical_Architecture.md)**
   - Internal implementation details
   - Data structures and algorithms
   - Security considerations
   - Verification rules

4. **[Implementation Plan](IMPLEMENTATION_PLAN.md)**
   - Original design specifications
   - Development roadmap
   - Testing requirements

### Visual Documentation

5. **[Architecture Diagrams](diagrams/)**
   - Transaction flow diagrams
   - Order lifecycle visualization
   - Multi-order execution scenarios

## Quick Start

For users who want to start trading:
1. Read the [Usage Examples](DEX_v2_Usage_Examples.md) for common scenarios
2. Refer to [CLI Reference](DEX_v2_CLI_Reference.md) for detailed command syntax

For developers:
1. Study the [Technical Architecture](DEX_v2_Technical_Architecture.md)
2. Review the [Implementation Plan](IMPLEMENTATION_PLAN.md) for design decisions

## Key Features

- **Decentralized Trading**: No central authority or order book
- **Partial Order Execution**: Orders can be filled incrementally
- **Multi-Order Transactions**: Purchase from multiple orders in one transaction
- **Automatic Matching**: Best rate selection with `purchase_auto` command
- **Order Chains**: Track order history through transaction chains
- **Flexible Fill Policies**: Support for partial fills, all-or-none, and minimum fill amounts

## Command Summary

Basic operations:
- `order create` - Create a new sell order
- `order remove` - Cancel an existing order
- `orders` - List orders for a trading pair
- `purchase` - Buy from a specific order
- `purchase_auto` - Automatically buy at best rates

Advanced operations:
- `purchase_multi` - Buy from multiple specific orders
- `history` - View order transaction history
- `status` - Get trading pair statistics

For detailed information on any command, see the [CLI Reference](DEX_v2_CLI_Reference.md).


