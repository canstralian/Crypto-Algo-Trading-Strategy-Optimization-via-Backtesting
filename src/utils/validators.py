"""Input validation utilities."""

from datetime import datetime
from typing import Any, Optional

from .exceptions import ValidationError


def validate_symbol(symbol: str) -> str:
    """Validate trading symbol format.

    Args:
        symbol: Trading symbol (e.g., BTC/USDT)

    Returns:
        Validated symbol

    Raises:
        ValidationError: If symbol is invalid
    """
    if not symbol:
        raise ValidationError("Symbol cannot be empty")

    if "/" not in symbol:
        raise ValidationError(f"Invalid symbol format: {symbol}. Expected format: BASE/QUOTE")

    parts = symbol.split("/")
    if len(parts) != 2:
        raise ValidationError(f"Invalid symbol format: {symbol}")

    base, quote = parts
    if not base or not quote:
        raise ValidationError(f"Invalid symbol format: {symbol}")

    return symbol.upper()


def validate_timeframe(timeframe: str) -> str:
    """Validate timeframe format.

    Args:
        timeframe: Timeframe string (e.g., 1m, 5m, 1h, 1d)

    Returns:
        Validated timeframe

    Raises:
        ValidationError: If timeframe is invalid
    """
    valid_timeframes = [
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "4h",
        "6h",
        "8h",
        "12h",
        "1d",
        "3d",
        "1w",
        "1M",
    ]

    if timeframe not in valid_timeframes:
        raise ValidationError(
            f"Invalid timeframe: {timeframe}. Valid options: {valid_timeframes}"
        )

    return timeframe


def validate_date(date_str: str) -> datetime:
    """Validate and parse date string.

    Args:
        date_str: Date string in ISO format (YYYY-MM-DD)

    Returns:
        Parsed datetime object

    Raises:
        ValidationError: If date format is invalid
    """
    try:
        return datetime.fromisoformat(date_str)
    except ValueError as e:
        raise ValidationError(f"Invalid date format: {date_str}. Expected ISO format (YYYY-MM-DD)")


def validate_positive_number(value: float, name: str = "Value") -> float:
    """Validate that a number is positive.

    Args:
        value: Number to validate
        name: Name of the value for error messages

    Returns:
        Validated value

    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got: {value}")
    return value


def validate_percentage(value: float, name: str = "Percentage") -> float:
    """Validate that a value is a valid percentage (0-1).

    Args:
        value: Percentage value (0-1)
        name: Name of the value for error messages

    Returns:
        Validated value

    Raises:
        ValidationError: If value is not in valid range
    """
    if not 0 <= value <= 1:
        raise ValidationError(f"{name} must be between 0 and 1, got: {value}")
    return value


def validate_integer_range(
    value: int, min_val: int, max_val: int, name: str = "Value"
) -> int:
    """Validate that an integer is within a specified range.

    Args:
        value: Integer to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Name of the value for error messages

    Returns:
        Validated value

    Raises:
        ValidationError: If value is out of range
    """
    if not min_val <= value <= max_val:
        raise ValidationError(f"{name} must be between {min_val} and {max_val}, got: {value}")
    return value


def validate_string_not_empty(value: str, name: str = "String") -> str:
    """Validate that a string is not empty.

    Args:
        value: String to validate
        name: Name of the value for error messages

    Returns:
        Validated string

    Raises:
        ValidationError: If string is empty
    """
    if not value or not value.strip():
        raise ValidationError(f"{name} cannot be empty")
    return value.strip()


def validate_config_dict(config: dict[str, Any], required_keys: list[str]) -> dict[str, Any]:
    """Validate that a configuration dictionary has all required keys.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys

    Returns:
        Validated config

    Raises:
        ValidationError: If required keys are missing
    """
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValidationError(f"Missing required configuration keys: {missing_keys}")
    return config


def validate_strategy_name(name: str) -> str:
    """Validate strategy name.

    Args:
        name: Strategy name

    Returns:
        Validated strategy name

    Raises:
        ValidationError: If strategy name is invalid
    """
    valid_strategies = [
        "ma_crossover",
        "moving_average",
        "rsi",
        "macd",
        "bollinger_bands",
        "bollinger",
        "multi_strategy",
    ]

    name_lower = name.lower()
    if name_lower not in valid_strategies:
        raise ValidationError(
            f"Invalid strategy: {name}. Valid strategies: {valid_strategies}"
        )

    return name_lower
