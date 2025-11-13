"""Configuration management using Pydantic settings."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError


class Settings(BaseSettings):
    """Application settings loaded from environment variables and config files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Application
    environment: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")
    api_reload: bool = Field(default=False, description="Auto-reload on code changes")

    # Security
    secret_key: str = Field(
        default="change-this-to-a-random-secret-key-in-production",
        description="Secret key for encryption",
    )
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Allowed CORS origins",
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./data/trading.db", description="Database connection URL"
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Rate limit per hour")

    # Backtesting
    default_initial_capital: float = Field(
        default=10000.0, description="Default initial capital"
    )
    default_commission: float = Field(default=0.001, description="Default commission rate")
    default_slippage: float = Field(default=0.0005, description="Default slippage")

    # Directories
    data_dir: str = Field(default="./data", description="Data directory")
    cache_dir: str = Field(default="./cache", description="Cache directory")
    log_dir: str = Field(default="./logs", description="Log directory")

    # Feature Flags
    enable_live_trading: bool = Field(default=False, description="Enable live trading")
    enable_paper_trading: bool = Field(default=True, description="Enable paper trading")
    enable_optimization: bool = Field(default=True, description="Enable optimization")

    # Config file path
    config_file: Optional[str] = Field(default=None, description="Path to YAML config file")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = ["development", "staging", "production"]
        v = v.lower()
        if v not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for directory in [self.data_dir, self.cache_dir, self.log_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def load_yaml_config(self, config_path: Optional[str] = None) -> dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML config file

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If config file cannot be loaded
        """
        if config_path is None:
            config_path = self.config_file or "config/config.yaml"

        config_file = Path(config_path)
        if not config_file.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML config: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file: {e}")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance
    """
    settings = Settings()
    settings.ensure_directories()
    return settings


def load_config(config_path: str = "config/config.yaml") -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    settings = get_settings()
    return settings.load_yaml_config(config_path)
