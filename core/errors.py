"""
Error Handling & Retry Logic - Fault tolerance infrastructure.

Implements CAP theorem principles:
- Availability: Retry logic with exponential backoff
- Partition Tolerance: Graceful degradation when agents fail
"""

import time
from functools import wraps
from typing import TypeVar, Callable, Optional, Type
from enum import Enum

from core.logging import get_agent_logger


class ErrorSeverity(Enum):
    """Error severity levels for handling decisions."""
    LOW = "low"           # Retry and continue
    MEDIUM = "medium"     # Retry with backoff
    HIGH = "high"         # Fail fast, no retry
    CRITICAL = "critical" # Stop entire pipeline


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recoverable: bool = True,
        context: Optional[dict] = None
    ):
        super().__init__(message)
        self.severity = severity
        self.recoverable = recoverable
        self.context = context or {}


class ValidationError(PipelineError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            recoverable=False,
            context={"field": field}
        )


class AgentError(PipelineError):
    """Raised when an agent fails to process."""
    
    def __init__(self, agent_name: str, message: str, recoverable: bool = True):
        super().__init__(
            f"Agent '{agent_name}' failed: {message}",
            severity=ErrorSeverity.MEDIUM,
            recoverable=recoverable,
            context={"agent": agent_name}
        )


class ConfigurationError(PipelineError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            recoverable=False
        )


class DataLoadError(PipelineError):
    """Raised when data file loading fails."""
    
    def __init__(self, file_path: str, message: str):
        super().__init__(
            f"Failed to load '{file_path}': {message}",
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            context={"file_path": file_path}
        )


T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential: bool = True,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Implements CAP: Availability - keeps trying to maintain service.
    
    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay between retries in seconds.
        exponential: Whether to use exponential backoff.
        exceptions: Tuple of exception types to catch.
        on_retry: Optional callback called on each retry.
    
    Usage:
        @retry_with_backoff(max_retries=3)
        def flaky_function():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_agent_logger(func.__name__)
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt if exponential else 1)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        if on_retry:
                            on_retry(e, attempt)
                        
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed: {e}")
            
            raise last_exception
        
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.
    
    Implements CAP: Partition Tolerance - isolates failing components.
    
    States:
        - CLOSED: Normal operation
        - OPEN: Failing, reject requests
        - HALF_OPEN: Testing if service recovered
    """
    
    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        self._state = self.State.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._logger = get_agent_logger(f"circuit_breaker.{name}")
    
    @property
    def state(self) -> State:
        """Get current circuit state."""
        if self._state == self.State.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = self.State.HALF_OPEN
                self._logger.info(f"Circuit {self.name} entering HALF_OPEN state")
        
        return self._state
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to wrap function with circuit breaker."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if self.state == self.State.OPEN:
                raise PipelineError(
                    f"Circuit breaker '{self.name}' is OPEN",
                    severity=ErrorSeverity.HIGH,
                    recoverable=True
                )
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self._failure_count = 0
        if self._state == self.State.HALF_OPEN:
            self._state = self.State.CLOSED
            self._logger.info(f"Circuit {self.name} recovered to CLOSED state")
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.failure_threshold:
            self._state = self.State.OPEN
            self._logger.warning(
                f"Circuit {self.name} opened after {self._failure_count} failures"
            )


class GracefulDegradation:
    """
    Provides fallback behavior when primary operations fail.
    
    Implements CAP: Availability - returns degraded response instead of failure.
    """
    
    def __init__(
        self,
        fallback_value: T = None,
        fallback_func: Optional[Callable[..., T]] = None
    ):
        self.fallback_value = fallback_value
        self.fallback_func = fallback_func
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for graceful degradation."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_agent_logger(func.__name__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Primary operation failed, using fallback: {e}")
                
                if self.fallback_func:
                    return self.fallback_func(*args, **kwargs)
                return self.fallback_value
        
        return wrapper
