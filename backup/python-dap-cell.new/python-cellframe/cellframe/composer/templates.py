"""
📋 Transaction Templates

Predefined transaction templates for common operations.
Provides easy-to-use templates for transfers, staking, exchanges, and more.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional

from .core import Composer
from .exceptions import TemplateError
from ..chain.wallet import TransactionType

logger = logging.getLogger(__name__)


class TransactionTemplates:
    """
    📋 Transaction Templates Manager
    
    Manages predefined transaction templates for common operations.
    Provides validation, parameter merging, and batch creation capabilities.
    
    Available Templates:
    - simple_transfer: Basic token transfers
    - stake_lock_3_months/1_year: Staking with time locks
    - exchange_order_market/limit: Exchange operations
    - voting_simple/multiple_choice: Voting proposals
    - batch_payments: Multiple recipient payments
    - service_payment: Network service payments
    """
    
    def __init__(self, composer: Composer):
        """
        Initialize transaction templates.
        
        Args:
            composer: Main composer instance
        """
        self.composer = composer
        logger.debug("TransactionTemplates initialized")
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available transaction templates.
        
        Returns:
            Dict[str, Dict[str, Any]]: Template definitions
        """
        return {
            'simple_transfer': {
                'description': 'Simple token transfer between addresses',
                'required_params': ['to_address', 'amount', 'token_ticker'],
                'optional_params': ['fee'],
                'example': {
                    'to_address': 'mCellAddress123...',
                    'amount': '10.5',
                    'token_ticker': 'CELL',
                    'fee': '0.01'
                }
            },
            'stake_lock_3_months': {
                'description': '3-month stake lock with 5% reinvestment',
                'required_params': ['amount'],
                'optional_params': ['token_ticker', 'reinvest_percent'],
                'template_params': {
                    'lock_time': '250401',  # 3 months from now (example)
                    'reinvest_percent': '5'
                },
                'example': {
                    'amount': '100',
                    'token_ticker': 'CELL'
                }
            },
            'stake_lock_1_year': {
                'description': '1-year stake lock with 10% reinvestment',
                'required_params': ['amount'],
                'optional_params': ['token_ticker', 'reinvest_percent'],
                'template_params': {
                    'lock_time': '260101',  # 1 year from now (example)
                    'reinvest_percent': '10'
                },
                'example': {
                    'amount': '1000',
                    'token_ticker': 'CELL'
                }
            },
            'exchange_order_market': {
                'description': 'Market exchange order with current rates',
                'required_params': ['token_sell', 'token_buy', 'amount'],
                'optional_params': ['fee', 'expiration'],
                'example': {
                    'token_sell': 'CELL',
                    'token_buy': 'mCELL',
                    'amount': '50',
                    'rate': 'market'  # Will be calculated automatically
                }
            },
            'exchange_order_limit': {
                'description': 'Limit exchange order with specified rate',
                'required_params': ['token_sell', 'token_buy', 'amount', 'rate'],
                'optional_params': ['fee', 'expiration'],
                'example': {
                    'token_sell': 'CELL',
                    'token_buy': 'mCELL',
                    'amount': '50',
                    'rate': '1.05'
                }
            },
            'voting_simple': {
                'description': 'Simple yes/no voting proposal',
                'required_params': ['question'],
                'optional_params': ['expire_time', 'max_votes'],
                'template_params': {
                    'options': ['Yes', 'No'],
                    'max_votes': 1000,
                    'delegated_key_required': False,
                    'vote_changing_allowed': True
                },
                'example': {
                    'question': 'Should we implement feature X?',
                    'expire_time': 1640995200  # Unix timestamp
                }
            },
            'voting_multiple_choice': {
                'description': 'Multiple choice voting proposal',
                'required_params': ['question', 'options'],
                'optional_params': ['expire_time', 'max_votes'],
                'template_params': {
                    'max_votes': 1000,
                    'delegated_key_required': False,
                    'vote_changing_allowed': True
                },
                'example': {
                    'question': 'Which feature should we prioritize?',
                    'options': ['Feature A', 'Feature B', 'Feature C'],
                    'expire_time': 1640995200
                }
            },
            'batch_payments': {
                'description': 'Batch payments to multiple recipients',
                'required_params': ['recipients'],  # List of {address, amount} dicts
                'optional_params': ['token_ticker', 'fee_per_tx'],
                'example': {
                    'recipients': [
                        {'address': 'addr1...', 'amount': '10'},
                        {'address': 'addr2...', 'amount': '20'},
                        {'address': 'addr3...', 'amount': '15'}
                    ],
                    'token_ticker': 'CELL'
                }
            },
            'service_payment': {
                'description': 'Payment for network services',
                'required_params': ['service_uid', 'max_price_per_unit', 'unit_type'],
                'optional_params': ['timeout', 'conditions'],
                'example': {
                    'service_uid': 'storage_service_001',
                    'max_price_per_unit': '0.001',
                    'unit_type': 'MB',
                    'timeout': 3600
                }
            }
        }
    
    def create_from_template(self, template_name: str, **params) -> str:
        """
        Create transaction from template.
        
        Args:
            template_name: Name of the template to use
            **params: Template parameters
            
        Returns:
            str: Transaction hash
            
        Raises:
            TemplateError: If template creation fails
        """
        try:
            templates = self.get_available_templates()
            
            if template_name not in templates:
                available = ', '.join(templates.keys())
                raise TemplateError(f"Unknown template '{template_name}'. Available: {available}")
            
            template = templates[template_name]
            
            # Validate required parameters
            self._validate_template_params(template, params)
            
            # Merge template params with user params
            merged_params = self._merge_template_params(template, params)
            
            # Create transaction based on template
            return self._create_transaction_from_template(template_name, merged_params)
            
        except Exception as e:
            logger.error("Failed to create transaction from template '%s': %s", template_name, e)
            raise TemplateError(f"Failed to create transaction from template '{template_name}': {e}")
    
    def _validate_template_params(self, template: Dict[str, Any], params: Dict[str, Any]) -> None:
        """Validate that all required template parameters are provided."""
        required_params = template.get('required_params', [])
        
        for param in required_params:
            if param not in params:
                raise TemplateError(f"Missing required parameter: {param}")
    
    def _merge_template_params(self, template: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge template default parameters with user-provided parameters."""
        merged = {}
        
        # Start with template default parameters
        template_params = template.get('template_params', {})
        merged.update(template_params)
        
        # Override with user parameters
        merged.update(params)
        
        return merged
    
    def _create_transaction_from_template(self, template_name: str, params: Dict[str, Any]) -> str:
        """Create transaction based on template name and parameters."""
        
        if template_name == 'simple_transfer':
            return self.composer.create_tx(
                params['to_address'],
                Decimal(str(params['amount'])),
                params.get('token_ticker', 'CELL'),
                Decimal(str(params.get('fee', '0.01')))
            )
        
        elif template_name in ['stake_lock_3_months', 'stake_lock_1_year']:
            from .conditional import ConditionalProcessor
            conditional_processor = ConditionalProcessor(self.composer)
            return conditional_processor.create_stake_lock_order(
                amount=Decimal(str(params['amount'])),
                lock_time=params['lock_time'],
                reinvest_percent=Decimal(str(params.get('reinvest_percent', '0'))),
                fee=Decimal(str(params.get('fee', '0.01')))
            )
        
        elif template_name == 'exchange_order_market':
            # For market orders, get current rate
            if params.get('rate') == 'market':
                params['rate'] = self._get_market_rate(params['token_sell'], params['token_buy'])
            
            from .conditional import ConditionalProcessor
            conditional_processor = ConditionalProcessor(self.composer)
            return conditional_processor.create_exchange_order(
                token_sell=params['token_sell'],
                token_buy=params['token_buy'],
                amount=Decimal(str(params['amount'])),
                rate=Decimal(str(params['rate'])),
                fee=Decimal(str(params.get('fee', '0.01'))),
                expiration=params.get('expiration')
            )
        
        elif template_name == 'exchange_order_limit':
            from .conditional import ConditionalProcessor
            conditional_processor = ConditionalProcessor(self.composer)
            return conditional_processor.create_exchange_order(
                token_sell=params['token_sell'],
                token_buy=params['token_buy'],
                amount=Decimal(str(params['amount'])),
                rate=Decimal(str(params['rate'])),
                fee=Decimal(str(params.get('fee', '0.01'))),
                expiration=params.get('expiration')
            )
        
        elif template_name in ['voting_simple', 'voting_multiple_choice']:
            from .conditional import ConditionalProcessor
            conditional_processor = ConditionalProcessor(self.composer)
            return conditional_processor.create_voting_proposal(
                question=params['question'],
                options=params['options'],
                max_votes=int(params.get('max_votes', 1000)),
                fee=Decimal(str(params.get('fee', '0.01'))),
                expire_time=params.get('expire_time')
            )
        
        elif template_name == 'batch_payments':
            # Convert to batch transactions format
            from .batch_processor import BatchProcessor
            from .fee_optimizer import FeeOptimizer
            
            fee_optimizer = FeeOptimizer(self.composer.config)
            batch_processor = BatchProcessor(self.composer, fee_optimizer)
            
            batch_transactions = []
            for recipient in params['recipients']:
                batch_transactions.append({
                    'type': TransactionType.TRANSFER_REGULAR,
                    'to_address': recipient['address'],
                    'amount': Decimal(str(recipient['amount'])),
                    'token_ticker': params.get('token_ticker', self.composer._get_native_ticker()),
                    'fee': Decimal(str(params.get('fee_per_tx', '0.01')))
                })
            
            # Return first transaction hash from batch
            batch_result = batch_processor.create_batch_transactions(batch_transactions)
            if batch_result['transaction_hashes']:
                return batch_result['transaction_hashes'][0]
            else:
                raise TemplateError("Batch payment failed")
        
        elif template_name == 'service_payment':
            from .conditional import ConditionalProcessor
            conditional_processor = ConditionalProcessor(self.composer)
            return conditional_processor.create_conditional_transaction(
                condition_type=TransactionType.SRV_PAY,
                value=Decimal(str(params.get('amount', '0'))),
                fee=Decimal(str(params.get('fee', '0.01'))),
                service_uid=params['service_uid'],
                max_price_per_unit=params['max_price_per_unit'],
                unit_type=params['unit_type'],
                timeout=params.get('timeout'),
                conditions=params.get('conditions', {})
            )
        
        else:
            raise TemplateError(f"Template '{template_name}' not implemented")
    
    def _get_market_rate(self, token_sell: str, token_buy: str) -> Decimal:
        """Get current market rate for token pair."""
        try:
            # In development mode - simulate market rates
            import random
            # Random rate between 0.95 and 1.05
            rate = Decimal(str(0.95 + random.random() * 0.1))
            logger.debug("Simulated market rate for %s/%s: %s", token_sell, token_buy, rate)
            return rate
                
        except Exception as e:
            logger.warning("Failed to get market rate: %s", e)
            return Decimal("1.0")
    
    def create_batch_from_template(self, template_name: str, 
                                 batch_params: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create batch transactions from template.
        
        Args:
            template_name: Template to use for all transactions
            batch_params: List of parameter sets for each transaction
            
        Returns:
            Dict[str, Any]: Batch results
        """
        try:
            from .batch_processor import BatchProcessor
            from .fee_optimizer import FeeOptimizer
            
            fee_optimizer = FeeOptimizer(self.composer.config)
            batch_processor = BatchProcessor(self.composer, fee_optimizer)
            
            # Convert template calls to transaction definitions
            transactions = []
            
            for params in batch_params:
                # This would create transaction definition without executing
                tx_def = self._template_to_transaction_definition(template_name, params)
                transactions.append(tx_def)
            
            # Execute batch
            return batch_processor.create_batch_transactions(transactions)
            
        except Exception as e:
            logger.error("Failed to create batch from template: %s", e)
            raise TemplateError(f"Failed to create batch from template: {e}")
    
    def _template_to_transaction_definition(self, template_name: str, 
                                          params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert template parameters to transaction definition for batch processing."""
        templates = self.get_available_templates()
        template = templates[template_name]
        
        # Validate and merge parameters
        self._validate_template_params(template, params)
        merged_params = self._merge_template_params(template, params)
        
        # Create transaction definition based on template
        if template_name == 'simple_transfer':
            return {
                'type': TransactionType.TRANSFER_REGULAR,
                'to_address': merged_params['to_address'],
                'amount': merged_params['amount'],
                'token_ticker': merged_params['token_ticker'],
                'fee': merged_params.get('fee', '0.01')
            }
        
        elif template_name in ['stake_lock_3_months', 'stake_lock_1_year']:
            return {
                'type': TransactionType.SRV_STAKE_LOCK,
                'amount': merged_params['amount'],
                'lock_time': merged_params['lock_time'],
                'reinvest_percent': merged_params.get('reinvest_percent', '0'),
                'fee': merged_params.get('fee', '0.01')
            }
        
        # Add more template conversions as needed
        else:
            raise TemplateError(f"Batch conversion for template '{template_name}' not implemented") 