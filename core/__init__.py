"""
Core Package - Production-grade infrastructure components.

This package provides:
- Type-safe data models (Pydantic)
- Configuration management
- Structured logging
- Error handling with retry logic
- State persistence
"""

from core.models import (
    ProductModel,
    Price,
    QuestionCategory,
    BenefitsData,
    UsageData,
    IngredientData,
    ComparisonData,
    Question,
    QuestionSet,
    FAQ,
    FAQPageData,
    ProductPageData,
    ComparisonPageData,
    AgentResult
)

from core.config import (
    Settings,
    get_settings,
    configure
)

from core.logging import (
    PipelineLogger,
    get_agent_logger,
    get_block_logger,
    log_step,
    StepTracker
)

from core.errors import (
    PipelineError,
    ValidationError,
    AgentError,
    ConfigurationError,
    DataLoadError,
    ErrorSeverity,
    retry_with_backoff,
    CircuitBreaker,
    GracefulDegradation
)

from core.state import (
    PipelineState,
    StateManager
)

__all__ = [
    # Models
    "ProductModel",
    "Price",
    "QuestionCategory",
    "BenefitsData",
    "UsageData",
    "IngredientData",
    "ComparisonData",
    "Question",
    "QuestionSet",
    "FAQ",
    "FAQPageData",
    "ProductPageData",
    "ComparisonPageData",
    "AgentResult",
    
    # Config
    "Settings",
    "get_settings",
    "configure",
    
    # Logging
    "PipelineLogger",
    "get_agent_logger",
    "get_block_logger",
    "log_step",
    "StepTracker",
    
    # Errors
    "PipelineError",
    "ValidationError",
    "AgentError",
    "ConfigurationError",
    "DataLoadError",
    "ErrorSeverity",
    "retry_with_backoff",
    "CircuitBreaker",
    "GracefulDegradation",
    
    # State
    "PipelineState",
    "StateManager"
]
