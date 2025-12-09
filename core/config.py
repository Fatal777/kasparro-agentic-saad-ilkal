"""
Configuration Management - Centralized configuration for the system.

Production-grade configuration with environment variable support,
validation, and sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PathConfig(BaseModel):
    """Path configuration."""
    data_dir: Path = Field(default=Path("data"))
    templates_dir: Path = Field(default=Path("templates"))
    output_dir: Path = Field(default=Path("output"))
    logs_dir: Path = Field(default=Path("logs"))
    
    def ensure_dirs_exist(self):
        """Create directories if they don't exist."""
        for path in [self.data_dir, self.templates_dir, self.output_dir, self.logs_dir]:
            path.mkdir(parents=True, exist_ok=True)


class RetryConfig(BaseModel):
    """Retry configuration for fault tolerance (CAP: Availability)."""
    max_retries: int = Field(default=3, ge=1, le=10)
    retry_delay_seconds: float = Field(default=1.0, ge=0.1)
    exponential_backoff: bool = Field(default=True)


class ValidationConfig(BaseModel):
    """Validation configuration."""
    strict_mode: bool = Field(default=True, description="Fail on validation errors")
    min_faq_count: int = Field(default=5, ge=1)
    min_question_count: int = Field(default=15, ge=1)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_to_file: bool = Field(default=True)
    log_file_name: str = Field(default="pipeline.log")


class Settings(BaseSettings):
    """
    Main settings class with environment variable support.
    
    Environment variables:
        - PIPELINE_ENV: Environment name (development, staging, production)
        - PIPELINE_DEBUG: Enable debug mode
        - PIPELINE_LOG_LEVEL: Logging level
    """
    
    # Environment
    env: str = Field(default="development", alias="PIPELINE_ENV")
    debug: bool = Field(default=False, alias="PIPELINE_DEBUG")
    
    # Paths
    paths: PathConfig = Field(default_factory=PathConfig)
    
    # Retry settings
    retry: RetryConfig = Field(default_factory=RetryConfig)
    
    # Validation settings
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    
    # Logging settings
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Pipeline settings
    parallel_page_generation: bool = Field(default=False, description="Run page agents in parallel")
    validate_json_output: bool = Field(default=True)
    save_intermediate_state: bool = Field(default=True, description="Persist state between steps")
    
    model_config = {
        "env_prefix": "PIPELINE_",
        "env_nested_delimiter": "__"
    }
    
    @classmethod
    def for_environment(cls, env: str) -> "Settings":
        """Factory method for environment-specific settings."""
        if env == "production":
            return cls(
                env="production",
                debug=False,
                retry=RetryConfig(max_retries=5, exponential_backoff=True),
                validation=ValidationConfig(strict_mode=True),
                logging=LoggingConfig(level="WARNING", log_to_file=True)
            )
        elif env == "staging":
            return cls(
                env="staging",
                debug=False,
                retry=RetryConfig(max_retries=3),
                validation=ValidationConfig(strict_mode=True),
                logging=LoggingConfig(level="INFO", log_to_file=True)
            )
        else:  # development
            return cls(
                env="development",
                debug=True,
                retry=RetryConfig(max_retries=1),
                validation=ValidationConfig(strict_mode=False),
                logging=LoggingConfig(level="DEBUG", log_to_file=False)
            )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global _settings
    if _settings is None:
        env = os.getenv("PIPELINE_ENV", "development")
        _settings = Settings.for_environment(env)
    return _settings


def configure(settings: Settings) -> None:
    """Override global settings (for testing)."""
    global _settings
    _settings = settings
