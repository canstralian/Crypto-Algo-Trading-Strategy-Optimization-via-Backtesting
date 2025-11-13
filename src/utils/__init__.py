"""Utility functions and error handling."""

from src.utils.errors import (
    CryptoOptimizerError,
    DataFetchError,
    StrategyError,
    BacktestError,
    ConfigurationError,
    OptimizationError,
    handle_cli_error,
)

__all__ = [
    "CryptoOptimizerError",
    "DataFetchError",
    "StrategyError",
    "BacktestError",
    "ConfigurationError",
    "OptimizationError",
    "handle_cli_error",
]
