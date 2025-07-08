"""
🛠️ Composer Utility Functions

Convenience functions and context managers for transaction composition.
"""

import logging
from contextlib import contextmanager
from decimal import Decimal
from typing import Union, Any, Optional

from .core import Composer
from ..chain.wallet import WalletAddress

logger = logging.getLogger(__name__)


@contextmanager
def composer_context(net_name: str, wallet: Any, **kwargs):
    """
    Context manager for composer operations.
    
    Args:
        net_name: Network name
        wallet: Wallet object for signing
        **kwargs: Additional composer configuration
        
    Usage:
        from cellframe.chain.wallet import Wallet
        
        wallet = Wallet.open("/path/to/wallet", password="pass")
        with composer_context("mainnet", wallet) as composer:
            tx = composer.create_tx(to_addr, amount, "CELL", fee)
    """
    composer = None
    try:
        composer = Composer(net_name=net_name, wallet=wallet, **kwargs)
        yield composer
    finally:
        if composer:
            composer.cleanup()


def quick_transfer(net_name: str, wallet: Any, to_address: WalletAddress,
                  amount: Decimal, token_ticker: str, fee: Decimal) -> str:
    """
    Quick helper for simple transfers.
    
    Args:
        net_name: Network name
        wallet: Wallet object for signing  
        to_address: Destination address
        amount: Amount to transfer
        token_ticker: Token ticker
        fee: Transaction fee
        
    Returns:
        str: Transaction hash
        
    Usage:
        from cellframe.chain.wallet import Wallet
        
        wallet = Wallet.open("/path/to/wallet", password="pass")
        tx_hash = quick_transfer("mainnet", wallet, dest_addr, 
                                Decimal("10"), "CELL", Decimal("0.001"))
    """
    try:
        with composer_context(net_name, wallet) as composer:
            return composer.create_tx(to_address, amount, token_ticker, fee)
            
    except Exception as e:
        logger.error("Quick transfer failed: %s", e)
        raise


def quick_exchange(net_name: str, wallet: Any,
                  token_sell: str, token_buy: str, amount: Union[Decimal, str],
                  rate: Union[Decimal, str], fee: Union[Decimal, str] = "0.01") -> str:
    """
    Quick exchange order creation.
    
    Args:
        net_name: Network name
        wallet: Wallet object for signing
        token_sell: Token to sell
        token_buy: Token to buy
        amount: Amount to sell
        rate: Exchange rate
        fee: Transaction fee
        
    Returns:
        str: Transaction hash
    """
    amount = Decimal(str(amount))
    rate = Decimal(str(rate))
    fee = Decimal(str(fee))
    
    with composer_context(net_name, wallet) as composer:
        from .conditional import ConditionalProcessor
        conditional_processor = ConditionalProcessor(composer)
        return conditional_processor.create_exchange_order(
            token_sell, token_buy, amount, rate, fee
        )


def quick_stake_lock(net_name: str, wallet: Any,
                    amount: Union[Decimal, str], lock_time: str,
                    reinvest_percent: Union[Decimal, str] = "0",
                    fee: Union[Decimal, str] = "0.01") -> str:
    """
    Quick stake lock creation.
    
    Args:
        net_name: Network name
        wallet: Wallet object for signing
        amount: Amount to stake
        lock_time: Lock time in YYMMDD format
        reinvest_percent: Reinvestment percentage
        fee: Transaction fee
        
    Returns:
        str: Transaction hash
    """
    amount = Decimal(str(amount))
    reinvest_percent = Decimal(str(reinvest_percent))
    fee = Decimal(str(fee))
    
    with composer_context(net_name, wallet) as composer:
        from .conditional import ConditionalProcessor
        conditional_processor = ConditionalProcessor(composer)
        return conditional_processor.create_stake_lock_order(
            amount, lock_time, reinvest_percent, fee
        )


def quick_batch_transfers(net_name: str, wallet: Any,
                         recipients: list, token_ticker: str = "CELL",
                         fee_per_tx: Union[Decimal, str] = "0.01") -> dict:
    """
    Quick batch transfers to multiple recipients.
    
    Args:
        net_name: Network name
        wallet: Wallet object for signing
        recipients: List of {'address': addr, 'amount': amount} dicts
        token_ticker: Token ticker
        fee_per_tx: Fee per transaction
        
    Returns:
        dict: Batch results
    """
    fee_per_tx = Decimal(str(fee_per_tx))
    
    with composer_context(net_name, wallet) as composer:
        from .batch_processor import BatchProcessor
        from .fee_optimizer import FeeOptimizer
        
        fee_optimizer = FeeOptimizer(composer.config)
        batch_processor = BatchProcessor(composer, fee_optimizer)
        
        batch_transactions = []
        for recipient in recipients:
            batch_transactions.append({
                'to_address': recipient['address'],
                'amount': Decimal(str(recipient['amount'])),
                'token_ticker': token_ticker,
                'fee': fee_per_tx
            })
        
        return batch_processor.create_batch_transactions(batch_transactions)


def estimate_transaction_fee(net_name: str, transaction_type: str,
                           amount: Union[Decimal, str], token_ticker: str,
                           priority: str = "balanced") -> dict:
    """
    Estimate transaction fee without creating transaction.
    
    Args:
        net_name: Network name
        transaction_type: Type of transaction
        amount: Transaction amount
        token_ticker: Token ticker
        priority: Priority level
        
    Returns:
        dict: Fee estimation details
    """
    from .fee_optimizer import FeeOptimizer
    from .core import ComposeConfig
    from ..chain.wallet import TransactionType
    
    amount = Decimal(str(amount))
    config = ComposeConfig(net_name=net_name)
    fee_optimizer = FeeOptimizer(config)
    
    tx_type = TransactionType(transaction_type)
    fee_structure = fee_optimizer.optimize_fees(tx_type, amount, token_ticker, priority)
    
    return {
        'network_fee': str(fee_structure.network_fee),
        'validator_fee': str(fee_structure.validator_fee),
        'total_fee': str(fee_structure.total_fee),
        'priority': priority,
        'transaction_type': transaction_type
    } 