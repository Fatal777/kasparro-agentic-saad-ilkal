"""
Logging Infrastructure - Structured logging for observability.

Provides consistent logging across all agents with support for
file output, log levels, and structured context.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from functools import wraps
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with additional context."""
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add any extra context
        if hasattr(record, "context"):
            context_str = json.dumps(record.context)
            return f"{self.formatTime(record)} - {record.name} - {record.levelname} - {record.getMessage()} | {context_str}"
        
        return super().format(record)


class PipelineLogger:
    """
    Custom logger for the pipeline with context support.
    
    Provides:
        - Structured logging with context
        - Agent-specific loggers
        - Step tracking
        - Error aggregation
    """
    
    _loggers: dict[str, logging.Logger] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(
        cls,
        level: str = "INFO",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_to_file: bool = False,
        log_file_path: Optional[Path] = None
    ) -> None:
        """Initialize logging configuration."""
        if cls._initialized:
            return
        
        # Root logger configuration
        root_logger = logging.getLogger("pipeline")
        root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter(log_format))
        root_logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_to_file and log_file_path:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setFormatter(StructuredFormatter(log_format))
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger for a specific component."""
        if not cls._initialized:
            cls.initialize()
        
        full_name = f"pipeline.{name}"
        if full_name not in cls._loggers:
            cls._loggers[full_name] = logging.getLogger(full_name)
        
        return cls._loggers[full_name]
    
    @classmethod
    def log_with_context(
        cls,
        logger: logging.Logger,
        level: int,
        message: str,
        context: Optional[dict[str, Any]] = None
    ) -> None:
        """Log a message with additional context."""
        record = logger.makeRecord(
            logger.name,
            level,
            "",
            0,
            message,
            None,
            None
        )
        if context:
            record.context = context
        logger.handle(record)


def get_agent_logger(agent_name: str) -> logging.Logger:
    """Convenience function to get logger for an agent."""
    return PipelineLogger.get_logger(f"agent.{agent_name}")


def get_block_logger(block_name: str) -> logging.Logger:
    """Convenience function to get logger for a logic block."""
    return PipelineLogger.get_logger(f"block.{block_name}")


def log_step(step_name: str):
    """
    Decorator for logging agent/block step execution.
    
    Usage:
        @log_step("process")
        def process(self, data):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger from first arg if it's a class method
            if args and hasattr(args[0], "__class__"):
                logger = get_agent_logger(args[0].__class__.__name__)
            else:
                logger = PipelineLogger.get_logger(func.__module__)
            
            logger.info(f"Starting {step_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {step_name}")
                return result
            except Exception as e:
                logger.error(f"Failed {step_name}: {e}")
                raise
        
        return wrapper
    return decorator


class StepTracker:
    """
    Tracks pipeline step execution for observability.
    
    Records:
        - Step start/end times
        - Step status
        - Error messages
    """
    
    def __init__(self):
        self.steps: list[dict] = []
        self._current_step: Optional[dict] = None
    
    def start_step(self, name: str) -> None:
        """Mark step as started."""
        self._current_step = {
            "name": name,
            "started_at": datetime.utcnow().isoformat(),
            "status": "running",
            "error": None
        }
        self.steps.append(self._current_step)
    
    def complete_step(self) -> None:
        """Mark current step as completed."""
        if self._current_step:
            self._current_step["completed_at"] = datetime.utcnow().isoformat()
            self._current_step["status"] = "completed"
            self._current_step = None
    
    def fail_step(self, error: str) -> None:
        """Mark current step as failed."""
        if self._current_step:
            self._current_step["completed_at"] = datetime.utcnow().isoformat()
            self._current_step["status"] = "failed"
            self._current_step["error"] = error
            self._current_step = None
    
    def get_summary(self) -> dict:
        """Get execution summary."""
        completed = sum(1 for s in self.steps if s["status"] == "completed")
        failed = sum(1 for s in self.steps if s["status"] == "failed")
        
        return {
            "total_steps": len(self.steps),
            "completed": completed,
            "failed": failed,
            "steps": self.steps
        }
