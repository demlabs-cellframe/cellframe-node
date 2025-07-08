"""
💱 Exchange Conditional Processor

Specialized processor for exchange conditional transactions.
Handles token exchange orders with market/limit pricing, expiration, and cancellation.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional

from .base import BaseConditionalProcessor
from ..core import TransactionOutput
from ..exceptions import ConditionalTransactionError
from ...chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class ExchangeProcessor(BaseConditionalProcessor):
    """
    💱 Exchange Conditional Processor
    
    Handles token exchange operations:
    - Market orders with current market rates
    - Limit orders with custom rates and expiration
    - Order cancellation and modification
    - Exchange history and status tracking
    """
    
    def get_transaction_type(self):
        """Get the transaction type handled by this processor."""
        return TransactionType.SRV_XCHANGE
    
    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """Validate exchange condition parameters."""
        required = ['token_buy', 'rate']
        self._validate_required_params(required, **kwargs)
        
        return {
            'token_buy': kwargs['token_buy'],
            'token_sell': kwargs.get('token_sell', self.composer._get_native_ticker()),
            'rate': Decimal(str(kwargs['rate'])),
            'expiration': kwargs.get('expiration'),
            'min_amount': kwargs.get('min_amount')
        }
    
    def create_conditional_output(self, value: Decimal, condition_params: Dict[str, Any]) -> TransactionOutput:
        """Create exchange conditional output."""
        return TransactionOutput(
            address=self.composer.wallet_addr,  # Exchange orders belong to creator
            value=value,
            token_ticker=condition_params['token_sell'],
            output_type="conditional_exchange",
            conditions={
                'token_buy': condition_params['token_buy'],
                'token_sell': condition_params['token_sell'],
                'rate': condition_params['rate'],
                'expiration': condition_params.get('expiration'),
                'min_amount': condition_params.get('min_amount')
            }
        )
    
    # === Convenience Methods ===
    
    def create_exchange_order(self, token_sell: str, token_buy: str, 
                            amount: Decimal, rate: Decimal, fee: Decimal,
                            expiration: Optional[int] = None) -> str:
        """
        Create exchange order (conditional transaction).
        
        Args:
            token_sell: Token to sell
            token_buy: Token to buy  
            amount: Amount to sell
            rate: Exchange rate
            fee: Transaction fee
            expiration: Order expiration time (optional)
            
        Returns:
            str: Transaction hash
        """
        return self.create_conditional_transaction(
            value=amount,
            fee=fee,
            token_sell=token_sell,
            token_buy=token_buy,
            rate=rate,
            expiration=expiration
        )
    
    def create_market_order(self, token_sell: str, token_buy: str,
                           amount: Decimal, fee: Decimal) -> str:
        """
        Create market order at current market rate.
        
        Args:
            token_sell: Token to sell
            token_buy: Token to buy
            amount: Amount to sell
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        # Get current market rate
        market_rate = self._get_market_rate(token_sell, token_buy)
        
        return self.create_exchange_order(
            token_sell=token_sell,
            token_buy=token_buy,
            amount=amount,
            rate=market_rate,
            fee=fee
        )
    
    def create_limit_order(self, token_sell: str, token_buy: str,
                          amount: Decimal, limit_rate: Decimal, fee: Decimal,
                          expiration: Optional[int] = None) -> str:
        """
        Create limit order with custom rate and expiration.
        
        Args:
            token_sell: Token to sell
            token_buy: Token to buy
            amount: Amount to sell
            limit_rate: Limit exchange rate
            fee: Transaction fee
            expiration: Order expiration timestamp (optional)
            
        Returns:
            str: Transaction hash
        """
        return self.create_exchange_order(
            token_sell=token_sell,
            token_buy=token_buy,
            amount=amount,
            rate=limit_rate,
            fee=fee,
            expiration=expiration
        )
    
    def cancel_exchange_order(self, order_hash: str, fee: Decimal) -> str:
        """
        Cancel an existing exchange order.
        
        Args:
            order_hash: Hash of the exchange order to cancel
            fee: Transaction fee for cancellation
            
        Returns:
            str: Transaction hash of cancellation
        """
        try:
            # In real implementation, this would create a cancellation transaction
            return f"cancel_exchange_{order_hash}_{self._get_current_time_yymmdd()}"
            
        except Exception as e:
            self._logger.error("Failed to cancel exchange order: %s", e)
            raise ConditionalTransactionError(f"Failed to cancel exchange order: {e}")
    
    def get_exchange_orders(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all exchange orders for wallet.
        
        Args:
            wallet_address: Wallet address (uses composer wallet if None)
            
        Returns:
            Dict[str, Any]: Exchange orders information
        """
        try:
            target_address = wallet_address or str(self.composer.wallet_addr)
            return self._query_exchange_orders(target_address)
            
        except Exception as e:
            self._logger.error("Failed to get exchange orders: %s", e)
            raise ConditionalTransactionError(f"Failed to get exchange orders: {e}")
    
    def get_exchange_order_status(self, order_hash: str) -> Dict[str, Any]:
        """
        Get status of specific exchange order.
        
        Args:
            order_hash: Hash of the exchange order
            
        Returns:
            Dict[str, Any]: Order status information
        """
        try:
            return self._query_exchange_order_status(order_hash)
            
        except Exception as e:
            self._logger.error("Failed to get exchange order status: %s", e)
            raise ConditionalTransactionError(f"Failed to get exchange order status: {e}")
    
    # === Private Helper Methods ===
    
    def _get_market_rate(self, token_sell: str, token_buy: str) -> Decimal:
        """Get current market rate for token pair."""
        # In real implementation, this would query the exchange for current rates
        # For now, return a mock rate
        mock_rates = {
            ('CELL', 'USDT'): Decimal('1.25'),
            ('USDT', 'CELL'): Decimal('0.8'),
            ('CELL', 'BTC'): Decimal('0.00001'),
            ('BTC', 'CELL'): Decimal('100000'),
        }
        
        pair = (token_sell, token_buy)
        return mock_rates.get(pair, Decimal('1.0'))
    
    def _query_exchange_orders(self, wallet_address: str) -> Dict[str, Any]:
        """Query exchange orders from blockchain."""
        # In real implementation, this would query the exchange service
        return {
            'active_orders': [
                {
                    'order_hash': 'exchange_order_1',
                    'token_sell': 'CELL',
                    'token_buy': 'USDT',
                    'amount': '100.0',
                    'rate': '1.25',
                    'filled': '45.0',
                    'status': 'partially_filled',
                    'created_at': '240101',
                    'expiration': '250101'
                }
            ],
            'completed_orders': [
                {
                    'order_hash': 'exchange_order_2',
                    'token_sell': 'USDT',
                    'token_buy': 'CELL',
                    'amount': '50.0',
                    'rate': '0.8',
                    'filled': '50.0',
                    'status': 'completed',
                    'created_at': '231215',
                    'completed_at': '231220'
                }
            ]
        }
    
    def _query_exchange_order_status(self, order_hash: str) -> Dict[str, Any]:
        """Query specific exchange order status."""
        return {
            'order_hash': order_hash,
            'status': 'active',
            'token_sell': 'CELL',
            'token_buy': 'USDT',
            'original_amount': '100.0',
            'filled_amount': '45.0',
            'remaining_amount': '55.0',
            'average_rate': '1.25',
            'created_at': '240101',
            'last_update': '240315',
            'expiration': '250101',
            'is_expired': False,
            'can_cancel': True
        } 