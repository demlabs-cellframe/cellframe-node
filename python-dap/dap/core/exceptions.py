"""
🛡️ DAP SDK Exception Hierarchy

Base exception classes for all DAP SDK operations with structured error context.

Exception Hierarchy:
    DapException (base)
    ├── DapInitializationError
    ├── DapTypeError
    ├── DapConfigError
    ├── DapEventError
    ├── DapCryptoError
    └── DapNetworkError
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import traceback


class DapException(Exception):
    """
    Base exception for all DAP SDK errors.
    
    Provides:
    - Structured error context
    - Error codes for programmatic handling
    - Chain of errors for debugging
    - Timestamp tracking
    - Suggestions for fixes
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "DAP_ERROR",
        context: Optional[Dict[str, Any]] = None,
        chain_error: Optional[Exception] = None,
        suggestions: Optional[List[str]] = None
    ):
        """Initialize DAP exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
            chain_error: Original exception that caused this error
            suggestions: List of suggested fixes
        """
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.chain_error = chain_error
        self.suggestions = suggestions or []
        self.timestamp = datetime.now()
        self.traceback_info = traceback.format_stack()
    
    def add_context(self, key: str, value: Any) -> 'DapException':
        """Add context information."""
        self.context[key] = value
        return self
    
    def add_suggestion(self, suggestion: str) -> 'DapException':
        """Add suggested fix."""
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)
        return self
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get complete error context."""
        return {
            'message': self.message,
            'error_code': self.error_code,
            'context': self.context,
            'suggestions': self.suggestions,
            'timestamp': self.timestamp.isoformat(),
            'chain_error': str(self.chain_error) if self.chain_error else None,
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"
    
    def __repr__(self) -> str:
        return f"DapException(message='{self.message}', error_code='{self.error_code}')"


class DapInitializationError(DapException):
    """DAP initialization error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_INIT_ERROR",
            **kwargs
        )
        self.add_suggestion("Check DAP SDK initialization sequence")
        self.add_suggestion("Verify system requirements")


class DapTypeError(DapException):
    """DAP type integration error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_TYPE_ERROR",
            **kwargs
        )
        self.add_suggestion("Check type conversion parameters")
        self.add_suggestion("Verify data format compatibility")


class DapLoggingError(DapException):
    """DAP logging system error."""
    
    def __init__(self, message: str, log_level: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_LOGGING_ERROR",
            **kwargs
        )
        
        if log_level:
            self.add_context("log_level", log_level)
        
        self.add_suggestion("Check log level configuration")
        self.add_suggestion("Verify logging system initialization")


class DapTimeError(DapException):
    """DAP time operations error."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_TIME_ERROR",
            **kwargs
        )
        
        if operation:
            self.add_context("time_operation", operation)
        
        self.add_suggestion("Check system time configuration")
        self.add_suggestion("Verify time format parameters")


class DapSystemError(DapException):
    """DAP system command error."""
    
    def __init__(self, message: str, command: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_SYSTEM_ERROR",
            **kwargs
        )
        
        if command:
            self.add_context("system_command", command)
        
        self.add_suggestion("Check command syntax and permissions")
        self.add_suggestion("Verify system command availability")


class DapCoreError(DapException):
    """DAP core coordination error."""
    
    def __init__(self, message: str, subsystem: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_CORE_ERROR",
            **kwargs
        )
        
        if subsystem:
            self.add_context("subsystem", subsystem)
        
        self.add_suggestion("Check DAP core initialization order")
        self.add_suggestion("Verify all dependencies are available")


class DapConfigError(DapException):
    """DAP configuration error."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_CONFIG_ERROR",
            **kwargs
        )
        
        if config_key:
            self.add_context("config_key", config_key)
        
        self.add_suggestion("Check configuration documentation")
        self.add_suggestion("Validate configuration values")


class DapEventError(DapException):
    """DAP event system error."""
    
    def __init__(self, message: str, event_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_EVENT_ERROR",
            **kwargs
        )
        
        if event_type:
            self.add_context("event_type", event_type)
        
        self.add_suggestion("Check event system initialization")
        self.add_suggestion("Verify event handler registration")


class DapCryptoError(DapException):
    """DAP crypto operation error."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_CRYPTO_ERROR",
            **kwargs
        )
        
        if operation:
            self.add_context("crypto_operation", operation)
        
        self.add_suggestion("Check cryptographic key validity")
        self.add_suggestion("Verify crypto system initialization")


class DapNetworkError(DapException):
    """DAP network operation error."""
    
    def __init__(self, message: str, endpoint: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DAP_NETWORK_ERROR",
            **kwargs
        )
        
        if endpoint:
            self.add_context("network_endpoint", endpoint)
        
        self.add_suggestion("Check network connectivity")
        self.add_suggestion("Verify network configuration")


def format_exception_context(exception: DapException) -> str:
    """Format exception with full context for debugging."""
    lines = [
        f"Error: {exception.message}",
        f"Code: {exception.error_code}",
        f"Time: {exception.timestamp.isoformat()}",
    ]
    
    if exception.context:
        lines.append("Context:")
        for key, value in exception.context.items():
            lines.append(f"  {key}: {value}")
    
    if exception.suggestions:
        lines.append("Suggestions:")
        for suggestion in exception.suggestions:
            lines.append(f"  - {suggestion}")
    
    if exception.chain_error:
        lines.append(f"Caused by: {exception.chain_error}")
    
    return "\n".join(lines)


def create_exception_from_error_code(
    error_code: str,
    message: str,
    **context
) -> DapException:
    """Create appropriate exception based on error code."""
    exception_map = {
        'DAP_INIT_ERROR': DapInitializationError,
        'DAP_TYPE_ERROR': DapTypeError,
        'DAP_LOGGING_ERROR': DapLoggingError,
        'DAP_TIME_ERROR': DapTimeError,
        'DAP_SYSTEM_ERROR': DapSystemError,
        'DAP_CORE_ERROR': DapCoreError,
        'DAP_CONFIG_ERROR': DapConfigError,
        'DAP_EVENT_ERROR': DapEventError,
        'DAP_CRYPTO_ERROR': DapCryptoError,
        'DAP_NETWORK_ERROR': DapNetworkError,
    }
    
    exception_class = exception_map.get(error_code, DapException)
    return exception_class(message=message, error_code=error_code, context=context)


__all__ = [
    'DapException', 'DapInitializationError', 'DapTypeError', 
    'DapLoggingError', 'DapTimeError', 'DapSystemError', 'DapCoreError',
    'DapConfigError', 'DapEventError', 'DapCryptoError', 'DapNetworkError',
    'format_exception_context', 'create_exception_from_error_code'
] 