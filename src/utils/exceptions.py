"""Custom exceptions for the trading platform."""

from typing import Any, Optional


class TradingPlatformError(Exception):
    """Base exception for all trading platform errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(TradingPlatformError):
    """Raised when there's a configuration error."""

    pass


class DataFetchError(TradingPlatformError):
    """Raised when data fetching fails."""

    pass


class ValidationError(TradingPlatformError):
    """Raised when input validation fails."""

    pass


class StrategyError(TradingPlatformError):
    """Raised when there's an error in strategy execution."""

    pass


class BacktestError(TradingPlatformError):
    """Raised when backtesting fails."""

    pass


class OrderError(TradingPlatformError):
    """Raised when order execution fails."""

    pass


class RiskManagementError(TradingPlatformError):
    """Raised when risk management constraints are violated."""

    pass


class PortfolioError(TradingPlatformError):
    """Raised when there's a portfolio management error."""

    pass


class APIError(TradingPlatformError):
    """Raised when API operations fail."""

    pass


class DatabaseError(TradingPlatformError):
    """Raised when database operations fail."""

    pass
