"""
🔀 Base Conditional Transaction Processor

Abstract base class for all conditional transaction processors.
Provides common functionality and interfaces for specialized processors.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BaseConditionalProcessor(ABC):
    """
    🔀 Base Conditional Transaction Processor
    
    Abstract base class that defines the interface and common functionality
    for all conditional transaction processors.
    
    Each specialized processor handles a specific type of conditional transaction:
    - Service payments (SRV_PAY)
    - Token exchanges (SRV_XCHANGE)  
    - Stake locks (SRV_STAKE_LOCK)
    - Voting operations (SRV_VOTING)
    - Delegation operations (SRV_STAKE_POS_DELEGATE)
    """
    
    def __init__(self, composer):
        """
        Initialize base conditional processor.
        
        Args:
            composer: Main composer instance
        """
        self.composer = composer
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._logger.debug(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """
        Validate and prepare condition-specific parameters.
        
        Args:
            **kwargs: Condition-specific parameters
            
        Returns:
            Dict[str, Any]: Validated parameters
            
        Raises:
            ConditionalTransactionError: If validation fails
        """
        pass
    
    @abstractmethod
    def create_conditional_output(self, value: Decimal, condition_params: Dict[str, Any]):
        """
        Create conditional output for this transaction type.
        
        Args:
            value: Amount to lock in condition
            condition_params: Validated condition parameters
            
        Returns:
            TransactionOutput: Conditional output
            
        Raises:
            OutputCreationError: If output creation fails
        """
        pass
    
    @abstractmethod
    def get_transaction_type(self):
        """
        Get the transaction type handled by this processor.
        
        Returns:
            TransactionType: Type of conditional transaction
        """
        pass
    
    def create_conditional_transaction(self, value: Decimal, fee: Decimal, **kwargs) -> str:
        """
        Create conditional transaction of this processor's type.
        
        Args:
            value: Amount to lock in condition
            fee: Transaction fee
            **kwargs: Condition-specific parameters
            
        Returns:
            str: Transaction hash
            
        Raises:
            ConditionalTransactionError: If transaction creation fails
        """
        from ..exceptions import ConditionalTransactionError
        
        try:
            with self.composer._lock:
                # Validate condition-specific parameters
                condition_params = self.validate_params(**kwargs)
                
                # Calculate fees
                fee_structure = self.composer.calculate_fees(
                    kwargs.get('token_ticker', self.composer._get_native_ticker()), 
                    fee
                )
                
                # Create conditional output
                conditional_output = self.create_conditional_output(value, condition_params)
                
                # Compose transaction
                return self._compose_conditional_transaction(
                    conditional_output, fee_structure, **kwargs
                )
                
        except Exception as e:
            self._logger.error("Failed to create conditional transaction: %s", e)
            raise ConditionalTransactionError(f"Failed to create conditional transaction: {e}")
    
    def _compose_conditional_transaction(self, conditional_output, fee_structure, **kwargs) -> str:
        """
        Compose transaction with conditional output.
        
        Args:
            conditional_output: Conditional transaction output
            fee_structure: Fee calculation structure
            **kwargs: Additional parameters
            
        Returns:
            str: Transaction hash
        """
        from ..core import TransactionOutput
        from ..exceptions import ConditionalTransactionError
        
        try:
            token_ticker = kwargs.get('token_ticker', self.composer._get_native_ticker())
            
            # Calculate total required amount (value + fees)
            total_required = conditional_output.value + fee_structure.total_fee
            
            # Select inputs
            inputs, total_value = self.composer.select_inputs(total_required, token_ticker)
            
            # Create outputs list
            outputs = [conditional_output]
            
            # Add fee outputs
            if fee_structure.network_fee > 0:
                outputs.append(TransactionOutput(
                    address=fee_structure.fee_address,
                    value=fee_structure.network_fee,
                    token_ticker=token_ticker,
                    output_type="network_fee"
                ))
            
            if fee_structure.validator_fee > 0:
                outputs.append(TransactionOutput(
                    address=None,
                    value=fee_structure.validator_fee,
                    token_ticker=token_ticker,
                    output_type="validator_fee"
                ))
            
            # Add coin back if needed
            coin_back = total_value - total_required
            if coin_back > 0:
                outputs.append(TransactionOutput(
                    address=self.composer.wallet_addr,
                    value=coin_back,
                    token_ticker=token_ticker,
                    output_type="coin_back"
                ))
            
            # Compose transaction
            transaction_type = self.get_transaction_type()
            return self.composer._compose_transaction(
                inputs=inputs,
                outputs=outputs,
                transaction_type=str(transaction_type).split('.')[-1].lower()
            )
            
        except Exception as e:
            self._logger.error("Failed to compose conditional transaction: %s", e)
            raise ConditionalTransactionError(f"Failed to compose conditional transaction: {e}")
    
    def _validate_required_params(self, required_params: List[str], **kwargs):
        """
        Validate that all required parameters are present.
        
        Args:
            required_params: List of required parameter names
            **kwargs: Provided parameters
            
        Raises:
            ConditionalTransactionError: If required parameters are missing
        """
        from ..exceptions import ConditionalTransactionError
        
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            raise ConditionalTransactionError(
                f"Missing required parameters for {self.__class__.__name__}: {missing_params}"
            )
    
    def _get_current_time_yymmdd(self) -> str:
        """Get current time in YYMMDD format."""
        from datetime import datetime
        now = datetime.now()
        return now.strftime('%y%m%d')
    
    def _calculate_months_remaining(self, current_time: str, target_time: str) -> Decimal:
        """Calculate months remaining between two YYMMDD formatted dates."""
        try:
            # Parse YYMMDD format
            current_year = int('20' + current_time[:2])
            current_month = int(current_time[2:4])
            current_day = int(current_time[4:6])
            
            target_year = int('20' + target_time[:2])
            target_month = int(target_time[2:4])
            target_day = int(target_time[4:6])
            
            # Simple month calculation
            months_diff = (target_year - current_year) * 12 + (target_month - current_month)
            if target_day < current_day:
                months_diff -= 1
            
            return max(Decimal(str(months_diff)), Decimal('0'))
            
        except Exception:
            return Decimal('0') 