"""
💰 Fee Optimization Engine

Advanced fee calculation and optimization algorithms for transaction composition.
Provides intelligent fee estimation based on network conditions, priority levels,
and input selection strategies.
"""

import logging
import random
from decimal import Decimal
from typing import List, Tuple, Optional, Dict, Any

from .core import FeeStructure, TransactionInput, ComposeConfig
from .exceptions import FeeCalculationError
from ..chain.wallet import TransactionType

logger = logging.getLogger(__name__)

# Try to import cellframe if available
try:
    import cellframe as cf
    _CELLFRAME_AVAILABLE = True
except ImportError:
    _CELLFRAME_AVAILABLE = False


class FeeOptimizer:
    """
    💰 Fee Optimization Engine
    
    Handles intelligent fee calculation and optimization for transactions.
    Provides multiple optimization strategies based on priority, network
    conditions, and input selection efficiency.
    
    Features:
    - Priority-based fee optimization (low, balanced, high, urgent)
    - Network congestion-aware fee adjustment
    - Input selection optimization for fee reduction
    - UTXO consolidation strategies
    - Fee limit enforcement
    """
    
    def __init__(self, config: ComposeConfig):
        """
        Initialize fee optimizer.
        
        Args:
            config: Composer configuration
        """
        self.config = config
        logger.debug("FeeOptimizer initialized for network '%s'", config.net_name)
    
    def optimize_fees(self, transaction_type: TransactionType, 
                     amount: Decimal, token_ticker: str,
                     priority: str = "balanced") -> FeeStructure:
        """
        Optimize transaction fees based on network conditions and priority.
        
        Args:
            transaction_type: Type of transaction
            amount: Transaction amount  
            token_ticker: Token ticker
            priority: Priority level ("low", "balanced", "high", "urgent")
            
        Returns:
            FeeStructure: Optimized fee structure
            
        Raises:
            FeeCalculationError: If fee optimization fails
        """
        try:
            # Get base fee estimation
            base_fee_structure = self.estimate_fee(transaction_type, amount, token_ticker)
            
            # Apply optimization based on priority
            optimization_factor = self._get_optimization_factor(priority)
            
            # Get network congestion factor
            congestion_factor = self._get_network_congestion_factor()
            
            # Calculate optimized fees
            optimized_validator_fee = base_fee_structure.validator_fee * optimization_factor * congestion_factor
            
            # Apply minimum and maximum limits
            optimized_validator_fee = self._apply_fee_limits(optimized_validator_fee, token_ticker)
            
            # Recalculate fee structure with optimized validator fee
            return FeeStructure(
                network_fee=base_fee_structure.network_fee,
                validator_fee=optimized_validator_fee,
                total_fee=base_fee_structure.network_fee + optimized_validator_fee,
                fee_address=base_fee_structure.fee_address
            )
            
        except Exception as e:
            logger.error("Failed to optimize fees: %s", e)
            # Fall back to base estimation
            return self.estimate_fee(transaction_type, amount, token_ticker)
    
    def estimate_fee(self, transaction_type: TransactionType,
                    amount: Decimal, token_ticker: str) -> FeeStructure:
        """
        Estimate transaction fee without creating transaction.
        
        Args:
            transaction_type: Type of transaction
            amount: Transaction amount
            token_ticker: Token ticker
            
        Returns:
            FeeStructure: Estimated fees
        """
        try:
            # Base validator fee estimation
            base_fee = Decimal("0.01")
            
            # Adjust based on transaction type
            fee_multipliers = {
                TransactionType.TRANSFER_REGULAR: Decimal("1.0"),
                TransactionType.TRANSFER_CROSSCHAIN: Decimal("2.0"),
                TransactionType.SRV_XCHANGE: Decimal("1.5"),
                TransactionType.SRV_STAKE_LOCK: Decimal("1.2"),
                TransactionType.DECREE_COMMON: Decimal("3.0"),
            }
            
            multiplier = fee_multipliers.get(transaction_type, Decimal("1.0"))
            estimated_validator_fee = base_fee * multiplier
            
            # Get network fee
            network_fee = self._estimate_network_fee(token_ticker)
            
            return FeeStructure(
                network_fee=network_fee,
                validator_fee=estimated_validator_fee,
                total_fee=network_fee + estimated_validator_fee
            )
            
        except Exception as e:
            logger.error("Failed to estimate fees: %s", e)
            raise FeeCalculationError(f"Failed to estimate fees: {e}")
    
    def _get_optimization_factor(self, priority: str) -> Decimal:
        """Get fee optimization factor based on priority."""
        optimization_factors = {
            "low": Decimal("0.5"),      # 50% of base fee for low priority
            "balanced": Decimal("1.0"),  # Standard fee
            "high": Decimal("1.5"),     # 150% for faster processing
            "urgent": Decimal("2.0")    # 200% for urgent transactions
        }
        
        return optimization_factors.get(priority, Decimal("1.0"))
    
    def _get_network_congestion_factor(self) -> Decimal:
        """Get network congestion factor for fee adjustment."""
        try:
            if _CELLFRAME_AVAILABLE and self.config:
                # This would query actual network congestion
                # For now, return a reasonable default
                return Decimal("1.0")
            else:
                # Development mode - simulate varying congestion
                # Random factor between 0.8 and 1.3
                factor = Decimal(str(0.8 + random.random() * 0.5))
                logger.debug("Simulated network congestion factor: %s", factor)
                return factor
                
        except Exception as e:
            logger.warning("Failed to get network congestion factor: %s", e)
            return Decimal("1.0")
    
    def _apply_fee_limits(self, fee: Decimal, token_ticker: str) -> Decimal:
        """Apply minimum and maximum fee limits."""
        # Define fee limits per token (these would come from network parameters)
        fee_limits = {
            'CELL': {'min': Decimal('0.001'), 'max': Decimal('10.0')},
            'mCELL': {'min': Decimal('0.01'), 'max': Decimal('100.0')},
            'tCELL': {'min': Decimal('0.001'), 'max': Decimal('5.0')},
            'KEL': {'min': Decimal('0.001'), 'max': Decimal('1.0')},
        }
        
        limits = fee_limits.get(token_ticker, {
            'min': Decimal('0.001'), 
            'max': Decimal('1.0')
        })
        
        # Apply limits
        if fee < limits['min']:
            logger.debug("Fee %s below minimum %s, adjusted", fee, limits['min'])
            return limits['min']
        elif fee > limits['max']:
            logger.debug("Fee %s above maximum %s, adjusted", fee, limits['max'])
            return limits['max']
        else:
            return fee
    
    def _estimate_network_fee(self, token_ticker: str) -> Decimal:
        """Estimate network fee for token."""
        # Network fees by token type
        network_fees = {
            'CELL': Decimal('0.001'),
            'mCELL': Decimal('0.01'), 
            'tCELL': Decimal('0.001'),
            'KEL': Decimal('0.0005'),
        }
        
        return network_fees.get(token_ticker, Decimal('0.001'))
    
    # === Input Selection Optimization ===
    
    def calculate_optimal_input_selection(self, required_amount: Decimal, 
                                        token_ticker: str,
                                        available_outputs: List[TransactionInput]) -> Tuple[List[TransactionInput], Decimal, Decimal]:
        """
        Calculate optimal input selection to minimize fees and UTXO fragmentation.
        
        Args:
            required_amount: Amount needed
            token_ticker: Token ticker
            available_outputs: Available outputs to choose from
            
        Returns:
            Tuple[List[TransactionInput], Decimal, Decimal]: (inputs, total_value, estimated_fee_savings)
        """
        try:
            if not available_outputs:
                raise FeeCalculationError("No available outputs")
            
            # Try different strategies
            strategies = [
                self._strategy_exact_match(available_outputs, required_amount),
                self._strategy_minimal_inputs(available_outputs, required_amount),
                self._strategy_consolidation(available_outputs, required_amount),
                self._strategy_balanced(available_outputs, required_amount)
            ]
            
            # Evaluate each strategy
            best_strategy = None
            best_score = float('-inf')
            
            for strategy in strategies:
                if strategy:
                    score = self._evaluate_input_strategy(*strategy, required_amount)
                    if score > best_score:
                        best_score = score
                        best_strategy = strategy
            
            if not best_strategy:
                # Fallback to simple greedy selection
                return self._fallback_input_selection(available_outputs, required_amount)
            
            inputs, total_value, fee_savings = best_strategy
            logger.debug("Optimal input selection: %d inputs, %s total, %s savings", 
                        len(inputs), total_value, fee_savings)
            return inputs, total_value, fee_savings
            
        except Exception as e:
            logger.error("Failed to calculate optimal input selection: %s", e)
            # Fallback to simple selection
            return self._fallback_input_selection(available_outputs, required_amount)
    
    def _strategy_exact_match(self, outputs: List[TransactionInput], 
                            required_amount: Decimal) -> Optional[Tuple[List[TransactionInput], Decimal, Decimal]]:
        """Strategy: Find exact match to avoid change output."""
        for output in outputs:
            if output.value == required_amount:
                # Perfect match - no change needed, saves fee
                fee_savings = Decimal("0.001")  # Estimated savings from no change output
                return [output], output.value, fee_savings
        return None
    
    def _strategy_minimal_inputs(self, outputs: List[TransactionInput], 
                               required_amount: Decimal) -> Optional[Tuple[List[TransactionInput], Decimal, Decimal]]:
        """Strategy: Use minimal number of inputs to reduce transaction size."""
        # Sort by value descending
        sorted_outputs = sorted(outputs, key=lambda x: x.value, reverse=True)
        
        selected = []
        total = Decimal("0")
        
        for output in sorted_outputs:
            selected.append(output)
            total += output.value
            
            if total >= required_amount:
                # Calculate fee savings from fewer inputs
                saved_inputs = len(outputs) - len(selected)
                fee_savings = Decimal(str(saved_inputs * 0.0001))  # Rough estimate
                return selected, total, fee_savings
        
        return None
    
    def _strategy_consolidation(self, outputs: List[TransactionInput], 
                              required_amount: Decimal) -> Optional[Tuple[List[TransactionInput], Decimal, Decimal]]:
        """Strategy: Use many small outputs to consolidate UTXOs."""
        # Sort by value ascending
        sorted_outputs = sorted(outputs, key=lambda x: x.value)
        
        selected = []
        total = Decimal("0")
        
        for output in sorted_outputs:
            if total >= required_amount:
                break
            selected.append(output)
            total += output.value
        
        if total >= required_amount:
            # Fee savings from UTXO consolidation (long-term benefit)
            consolidation_benefit = Decimal(str(len(selected) * 0.00005))
            return selected, total, consolidation_benefit
        
        return None
    
    def _strategy_balanced(self, outputs: List[TransactionInput], 
                         required_amount: Decimal) -> Optional[Tuple[List[TransactionInput], Decimal, Decimal]]:
        """Strategy: Balanced approach between minimal inputs and consolidation."""
        # Use medium-sized outputs when possible
        sorted_outputs = sorted(outputs, key=lambda x: abs(x.value - required_amount))
        
        selected = []
        total = Decimal("0")
        
        for output in sorted_outputs:
            selected.append(output)
            total += output.value
            
            if total >= required_amount:
                # Balanced fee savings
                fee_savings = Decimal("0.0002")
                return selected, total, fee_savings
            
            # Don't use too many inputs
            if len(selected) >= 5:
                break
        
        return None if total < required_amount else (selected, total, Decimal("0.0002"))
    
    def _evaluate_input_strategy(self, inputs: List[TransactionInput], 
                               total_value: Decimal, fee_savings: Decimal,
                               required_amount: Decimal) -> float:
        """Evaluate input selection strategy based on multiple criteria."""
        # Criteria weights
        WEIGHT_FEE_SAVINGS = 0.3
        WEIGHT_INPUT_COUNT = 0.2
        WEIGHT_CHANGE_SIZE = 0.3
        WEIGHT_UTXO_HEALTH = 0.2
        
        # Fee savings score
        fee_score = float(fee_savings) * 1000  # Normalize
        
        # Input count score (fewer is better)
        input_score = max(0, 10 - len(inputs))
        
        # Change size score (smaller change is better)
        change = total_value - required_amount
        change_score = max(0, 10 - float(change))
        
        # UTXO health score (balanced UTXO sizes are better)
        avg_input_size = float(total_value) / len(inputs) if inputs else 0
        health_score = 5.0 if 0.1 <= avg_input_size <= 1.0 else 1.0
        
        # Calculate weighted score
        total_score = (
            fee_score * WEIGHT_FEE_SAVINGS +
            input_score * WEIGHT_INPUT_COUNT +
            change_score * WEIGHT_CHANGE_SIZE +
            health_score * WEIGHT_UTXO_HEALTH
        )
        
        return total_score
    
    def _fallback_input_selection(self, outputs: List[TransactionInput], 
                                required_amount: Decimal) -> Tuple[List[TransactionInput], Decimal, Decimal]:
        """Fallback input selection when optimization fails."""
        # Simple greedy selection
        sorted_outputs = sorted(outputs, key=lambda x: x.value, reverse=True)
        
        selected = []
        total = Decimal("0")
        
        for output in sorted_outputs:
            selected.append(output)
            total += output.value
            
            if total >= required_amount:
                break
        
        return selected, total, Decimal("0") 