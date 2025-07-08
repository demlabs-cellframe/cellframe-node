"""
📦 Batch Transaction Processor

Efficient batch processing engine for multiple transactions with optimization
and fee consolidation across token types.
"""

import logging
from decimal import Decimal
from typing import List, Dict, Any, Tuple

from .core import TransactionInput, TransactionOutput, Composer
from .fee_optimizer import FeeOptimizer
from .exceptions import BatchProcessingError, InsufficientFundsError
from ..chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    📦 Batch Transaction Processor
    
    Handles efficient processing of multiple transactions with optimization
    for fees, input selection, and resource utilization.
    
    Features:
    - Multi-token batch processing
    - Automatic fee optimization across batches
    - Input consolidation strategies
    - Error recovery and partial success handling
    - Detailed batch statistics and reporting
    """
    
    def __init__(self, composer: Composer, fee_optimizer: FeeOptimizer):
        """
        Initialize batch processor.
        
        Args:
            composer: Main composer instance
            fee_optimizer: Fee optimization engine
        """
        self.composer = composer
        self.fee_optimizer = fee_optimizer
        logger.debug("BatchProcessor initialized")
    
    def create_batch_transactions(self, transactions: List[Dict[str, Any]], 
                                optimize_fees: bool = True) -> Dict[str, Any]:
        """
        Create multiple transactions in an optimized batch.
        
        Args:
            transactions: List of transaction definitions
            optimize_fees: Whether to optimize fees across batch
            
        Returns:
            Dict[str, Any]: Batch results with transaction hashes and statistics
        """
        try:
            if optimize_fees:
                return self._create_optimized_batch(transactions)
            else:
                return self._create_simple_batch(transactions)
                
        except Exception as e:
            logger.error("Failed to create batch transactions: %s", e)
            raise BatchProcessingError(f"Failed to create batch transactions: {e}")
    
    def _create_optimized_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create batch with fee optimization and input consolidation."""
        results = {
            'transaction_hashes': [],
            'total_fees': Decimal('0'),
            'fee_savings': Decimal('0'),
            'successful_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        try:
            # Group transactions by token for optimization
            token_groups = self._group_transactions_by_token(transactions)
            
            for token_ticker, token_transactions in token_groups.items():
                batch_result = self._process_token_batch(token_ticker, token_transactions)
                
                # Merge results
                results['transaction_hashes'].extend(batch_result['hashes'])
                results['total_fees'] += batch_result['total_fees']
                results['fee_savings'] += batch_result['fee_savings']
                results['successful_count'] += batch_result['successful_count']
                results['failed_count'] += batch_result['failed_count']
                results['errors'].extend(batch_result['errors'])
            
            logger.info("Batch processed: %d successful, %d failed, savings: %s", 
                       results['successful_count'], results['failed_count'], 
                       results['fee_savings'])
                       
            return results
            
        except Exception as e:
            logger.error("Failed to create optimized batch: %s", e)
            results['errors'].append(str(e))
            return results
    
    def _create_simple_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create batch without optimization - process sequentially."""
        results = {
            'transaction_hashes': [],
            'total_fees': Decimal('0'),
            'fee_savings': Decimal('0'),
            'successful_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        for tx_def in transactions:
            try:
                tx_type = TransactionType(tx_def.get('type', TransactionType.TRANSFER_REGULAR))
                
                if tx_type == TransactionType.TRANSFER_REGULAR:
                    tx_hash = self.composer.create_tx(
                        tx_def['to_address'],
                        Decimal(str(tx_def['amount'])),
                        tx_def['token_ticker'],
                        Decimal(str(tx_def.get('fee', '0.01')))
                    )
                else:
                    # Handle conditional transactions
                    from .conditional import ConditionalProcessor
                    conditional_processor = ConditionalProcessor(self.composer)
                    tx_hash = conditional_processor.create_conditional_transaction(
                        condition_type=tx_type,
                        value=Decimal(str(tx_def.get('amount', '0'))),
                        fee=Decimal(str(tx_def.get('fee', '0.01'))),
                        **{k: v for k, v in tx_def.items() if k not in ['type', 'amount', 'fee']}
                    )
                
                results['transaction_hashes'].append(tx_hash)
                results['successful_count'] += 1
                
                # Estimate fees (rough calculation)
                estimated_fee = self.fee_optimizer.estimate_fee(
                    tx_type, 
                    tx_def.get('amount', Decimal('0')), 
                    tx_def.get('token_ticker', self.composer._get_native_ticker())
                )
                results['total_fees'] += estimated_fee.total_fee
                
            except Exception as e:
                error_msg = f"Failed to create transaction {len(results['transaction_hashes'])}: {e}"
                results['errors'].append(error_msg)
                results['failed_count'] += 1
                logger.error(error_msg)
        
        return results
    
    def _group_transactions_by_token(self, transactions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group transactions by token ticker for batch optimization."""
        token_groups = {}
        
        for tx in transactions:
            token_ticker = tx.get('token_ticker', self.composer._get_native_ticker())
            
            if token_ticker not in token_groups:
                token_groups[token_ticker] = []
            
            token_groups[token_ticker].append(tx)
        
        return token_groups
    
    def _process_token_batch(self, token_ticker: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of transactions for a specific token with optimization."""
        batch_result = {
            'hashes': [],
            'total_fees': Decimal('0'),
            'fee_savings': Decimal('0'),
            'successful_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        try:
            # Calculate total amount needed for all transactions
            total_required = self._calculate_batch_total_amount(transactions)
            
            # Get optimal input selection for the entire batch
            available_outputs = self.composer.get_available_outputs(token_ticker)
            
            if not available_outputs:
                error = f"No available outputs for token {token_ticker}"
                batch_result['errors'].append(error)
                batch_result['failed_count'] = len(transactions)
                return batch_result
            
            # Use optimal input selection
            inputs, total_value, fee_savings = self.fee_optimizer.calculate_optimal_input_selection(
                total_required, token_ticker, available_outputs
            )
            
            batch_result['fee_savings'] = fee_savings
            
            # Process each transaction in the batch
            remaining_value = total_value
            
            for tx_def in transactions:
                try:
                    # Process individual transaction with remaining inputs
                    tx_hash, used_amount, tx_fees = self._process_single_transaction_in_batch(
                        tx_def, token_ticker, remaining_value
                    )
                    
                    batch_result['hashes'].append(tx_hash)
                    batch_result['total_fees'] += tx_fees
                    batch_result['successful_count'] += 1
                    
                    remaining_value -= used_amount
                    
                except Exception as e:
                    error_msg = f"Failed transaction in batch: {e}"
                    batch_result['errors'].append(error_msg)
                    batch_result['failed_count'] += 1
                    logger.error(error_msg)
            
            return batch_result
            
        except Exception as e:
            logger.error("Failed to process token batch: %s", e)
            batch_result['errors'].append(str(e))
            batch_result['failed_count'] = len(transactions)
            return batch_result
    
    def _calculate_batch_total_amount(self, transactions: List[Dict[str, Any]]) -> Decimal:
        """Calculate total amount needed for batch of transactions."""
        total = Decimal('0')
        
        for tx in transactions:
            amount = tx.get('amount', Decimal('0'))
            if isinstance(amount, (int, float, str)):
                amount = Decimal(str(amount))
            
            fee = tx.get('fee', Decimal('0.01'))
            if isinstance(fee, (int, float, str)):
                fee = Decimal(str(fee))
            
            total += amount + fee
        
        return total
    
    def _process_single_transaction_in_batch(self, tx_def: Dict[str, Any], 
                                           token_ticker: str, available_value: Decimal) -> Tuple[str, Decimal, Decimal]:
        """Process a single transaction within a batch context."""
        tx_type = TransactionType(tx_def.get('type', TransactionType.TRANSFER_REGULAR))
        amount = Decimal(str(tx_def.get('amount', '0')))
        fee = Decimal(str(tx_def.get('fee', '0.01')))
        
        total_needed = amount + fee
        
        if available_value < total_needed:
            raise InsufficientFundsError(f"Insufficient funds in batch: need {total_needed}, have {available_value}")
        
        # Create transaction based on type
        if tx_type == TransactionType.TRANSFER_REGULAR:
            tx_hash = self.composer.create_tx(
                tx_def['to_address'],
                amount,
                token_ticker,
                fee
            )
        else:
            # Handle conditional transactions
            from .conditional import ConditionalProcessor
            conditional_processor = ConditionalProcessor(self.composer)
            tx_hash = conditional_processor.create_conditional_transaction(
                condition_type=tx_type,
                value=amount,
                fee=fee,
                **{k: v for k, v in tx_def.items() if k not in ['type', 'amount', 'fee']}
            )
        
        return tx_hash, total_needed, fee
    
    def create_multi_token_batch(self, token_operations: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Create batch operations across multiple tokens efficiently.
        
        Args:
            token_operations: Dict mapping token_ticker to list of operations
            
        Returns:
            Dict[str, Any]: Batch results grouped by token
        """
        try:
            results = {
                'token_results': {},
                'total_transactions': 0,
                'total_successful': 0,
                'total_failed': 0,
                'total_fees': Decimal('0'),
                'total_savings': Decimal('0')
            }
            
            for token_ticker, operations in token_operations.items():
                logger.info("Processing batch for token %s: %d operations", 
                           token_ticker, len(operations))
                
                token_result = self._process_token_batch(token_ticker, operations)
                results['token_results'][token_ticker] = token_result
                
                # Aggregate totals
                results['total_transactions'] += len(operations)
                results['total_successful'] += token_result['successful_count']
                results['total_failed'] += token_result['failed_count']
                results['total_fees'] += token_result['total_fees']
                results['total_savings'] += token_result['fee_savings']
            
            logger.info("Multi-token batch completed: %d/%d successful, total savings: %s",
                       results['total_successful'], results['total_transactions'], 
                       results['total_savings'])
            
            return results
            
        except Exception as e:
            logger.error("Failed to create multi-token batch: %s", e)
            raise BatchProcessingError(f"Failed to create multi-token batch: {e}") 