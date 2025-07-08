"""
💼 Service Payment Conditional Processor

Specialized processor for service payment conditional transactions.
Handles payments for network services with conditions and timeouts.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional

from .base import BaseConditionalProcessor
from ..core import TransactionOutput
from ..exceptions import ConditionalTransactionError
from ...chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class ServicePaymentProcessor(BaseConditionalProcessor):
    """
    💼 Service Payment Conditional Processor
    
    Handles service payment operations:
    - Conditional payments for network services
    - Service discovery and pricing
    - Payment timeouts and cancellation
    - Service execution tracking
    """
    
    def get_transaction_type(self):
        """Get the transaction type handled by this processor."""
        return TransactionType.SRV_PAY
    
    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """Validate service payment condition parameters."""
        required = ['service_uid', 'max_price_per_unit', 'unit_type']
        self._validate_required_params(required, **kwargs)
        
        return {
            'service_uid': kwargs['service_uid'],
            'max_price_per_unit': Decimal(str(kwargs['max_price_per_unit'])),
            'unit_type': kwargs['unit_type'],
            'timeout': kwargs.get('timeout'),
            'conditions': kwargs.get('conditions', {})
        }
    
    def create_conditional_output(self, value: Decimal, condition_params: Dict[str, Any]) -> TransactionOutput:
        """Create service payment conditional output."""
        return TransactionOutput(
            address=None,  # Service payments have no specific address
            value=value,
            token_ticker=self.composer._get_native_ticker(),
            output_type="conditional_service_payment",
            conditions={
                'service_uid': condition_params['service_uid'],
                'max_price_per_unit': condition_params['max_price_per_unit'],
                'unit_type': condition_params['unit_type'],
                'timeout': condition_params.get('timeout'),
                'additional_conditions': condition_params.get('conditions', {})
            }
        )
    
    # === Convenience Methods ===
    
    def create_service_payment(self, service_uid: str, max_price_per_unit: Decimal,
                             unit_type: str, amount: Decimal, fee: Decimal,
                             timeout: Optional[int] = None) -> str:
        """
        Create service payment conditional transaction.
        
        Args:
            service_uid: Unique identifier of the service
            max_price_per_unit: Maximum price per unit willing to pay
            unit_type: Type of units (e.g., "MB", "seconds", "requests")
            amount: Maximum amount to pay
            fee: Transaction fee
            timeout: Payment timeout in seconds (optional)
            
        Returns:
            str: Transaction hash
        """
        return self.create_conditional_transaction(
            value=amount,
            fee=fee,
            service_uid=service_uid,
            max_price_per_unit=max_price_per_unit,
            unit_type=unit_type,
            timeout=timeout
        )
    
    def create_storage_payment(self, storage_size_mb: Decimal, max_price_per_mb: Decimal,
                             duration_days: int, fee: Decimal) -> str:
        """
        Create payment for storage service.
        
        Args:
            storage_size_mb: Storage size in megabytes
            max_price_per_mb: Maximum price per MB
            duration_days: Storage duration in days
            fee: Transaction fee
            
        Returns:
            str: Transaction hash
        """
        total_amount = storage_size_mb * max_price_per_mb * Decimal(str(duration_days))
        
        return self.create_service_payment(
            service_uid="storage_service",
            max_price_per_unit=max_price_per_mb,
            unit_type="MB_per_day",
            amount=total_amount,
            fee=fee,
            timeout=86400 * duration_days  # Convert days to seconds
        )
    
    def create_compute_payment(self, compute_units: Decimal, max_price_per_unit: Decimal,
                             fee: Decimal, timeout: Optional[int] = None) -> str:
        """
        Create payment for compute service.
        
        Args:
            compute_units: Number of compute units needed
            max_price_per_unit: Maximum price per compute unit
            fee: Transaction fee
            timeout: Computation timeout in seconds (optional)
            
        Returns:
            str: Transaction hash
        """
        total_amount = compute_units * max_price_per_unit
        
        return self.create_service_payment(
            service_uid="compute_service",
            max_price_per_unit=max_price_per_unit,
            unit_type="compute_unit",
            amount=total_amount,
            fee=fee,
            timeout=timeout
        )
    
    def create_bandwidth_payment(self, bandwidth_gb: Decimal, max_price_per_gb: Decimal,
                                fee: Decimal, duration_hours: int = 1) -> str:
        """
        Create payment for bandwidth service.
        
        Args:
            bandwidth_gb: Bandwidth needed in GB
            max_price_per_gb: Maximum price per GB
            fee: Transaction fee
            duration_hours: Duration in hours
            
        Returns:
            str: Transaction hash
        """
        total_amount = bandwidth_gb * max_price_per_gb
        
        return self.create_service_payment(
            service_uid="bandwidth_service",
            max_price_per_unit=max_price_per_gb,
            unit_type="GB",
            amount=total_amount,
            fee=fee,
            timeout=3600 * duration_hours  # Convert hours to seconds
        )
    
    def get_service_payments(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all service payments for wallet.
        
        Args:
            wallet_address: Wallet address (uses composer wallet if None)
            
        Returns:
            Dict[str, Any]: Service payments information
        """
        try:
            target_address = wallet_address or str(self.composer.wallet_addr)
            return self._query_service_payments(target_address)
            
        except Exception as e:
            self._logger.error("Failed to get service payments: %s", e)
            raise ConditionalTransactionError(f"Failed to get service payments: {e}")
    
    def get_service_payment_status(self, payment_hash: str) -> Dict[str, Any]:
        """
        Get status of specific service payment.
        
        Args:
            payment_hash: Hash of the service payment
            
        Returns:
            Dict[str, Any]: Payment status information
        """
        try:
            return self._query_service_payment_status(payment_hash)
            
        except Exception as e:
            self._logger.error("Failed to get service payment status: %s", e)
            raise ConditionalTransactionError(f"Failed to get service payment status: {e}")
    
    def cancel_service_payment(self, payment_hash: str, fee: Decimal) -> str:
        """
        Cancel a pending service payment.
        
        Args:
            payment_hash: Hash of the service payment to cancel
            fee: Transaction fee for cancellation
            
        Returns:
            str: Transaction hash of cancellation
        """
        try:
            # In real implementation, this would create a cancellation transaction
            return f"cancel_service_payment_{payment_hash}_{self._get_current_time_yymmdd()}"
            
        except Exception as e:
            self._logger.error("Failed to cancel service payment: %s", e)
            raise ConditionalTransactionError(f"Failed to cancel service payment: {e}")
    
    # === Private Helper Methods ===
    
    def _query_service_payments(self, wallet_address: str) -> Dict[str, Any]:
        """Query service payments from blockchain."""
        # In real implementation, this would query the service payment system
        return {
            'active_payments': [
                {
                    'payment_hash': 'service_payment_1',
                    'service_uid': 'storage_service',
                    'amount': '50.0',
                    'max_price_per_unit': '0.1',
                    'unit_type': 'MB_per_day',
                    'status': 'pending',
                    'created_at': '240101',
                    'timeout': '250101'
                }
            ],
            'completed_payments': [
                {
                    'payment_hash': 'service_payment_2',
                    'service_uid': 'compute_service',
                    'amount': '25.0',
                    'max_price_per_unit': '0.5',
                    'unit_type': 'compute_unit',
                    'status': 'completed',
                    'created_at': '231215',
                    'completed_at': '231220'
                }
            ]
        }
    
    def _query_service_payment_status(self, payment_hash: str) -> Dict[str, Any]:
        """Query specific service payment status."""
        return {
            'payment_hash': payment_hash,
            'status': 'pending',
            'service_uid': 'storage_service',
            'amount': '50.0',
            'max_price_per_unit': '0.1',
            'unit_type': 'MB_per_day',
            'units_consumed': '150',
            'total_cost': '15.0',
            'remaining_budget': '35.0',
            'created_at': '240101',
            'last_update': '240315',
            'timeout': '250101',
            'is_expired': False,
            'can_cancel': True,
            'service_provider': 'provider_address_1'
        } 