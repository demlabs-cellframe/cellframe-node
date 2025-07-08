"""
🚨 Composer Exception Classes

Specialized exceptions for transaction composition operations.
Provides detailed error context for different failure scenarios.
"""


class ComposeError(Exception):
    """Base exception for transaction composition errors."""
    pass


class FeeCalculationError(ComposeError):
    """Raised when fee calculation fails."""
    pass


class InsufficientFundsError(ComposeError):
    """Raised when wallet has insufficient funds for transaction."""
    pass


class InputSelectionError(ComposeError):
    """Raised when optimal input selection fails."""
    pass


class OutputCreationError(ComposeError):
    """Raised when transaction output creation fails."""
    pass


class TemplateError(ComposeError):
    """Raised when transaction template processing fails."""
    pass


class BatchProcessingError(ComposeError):
    """Raised when batch transaction processing fails."""
    pass


class ConditionalTransactionError(ComposeError):
    """Raised when conditional transaction creation fails."""
    pass 