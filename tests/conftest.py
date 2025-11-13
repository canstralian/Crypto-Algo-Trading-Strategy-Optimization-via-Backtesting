"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_ohlcv_data() -> pd.DataFrame:
    """Create sample OHLCV data for testing."""
    np.random.seed(42)

    dates = pd.date_range(start="2023-01-01", periods=100, freq="1H")
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)

    data = pd.DataFrame(
        {
            "open": close_prices + np.random.randn(100) * 0.5,
            "high": close_prices + abs(np.random.randn(100)) * 1.5,
            "low": close_prices - abs(np.random.randn(100)) * 1.5,
            "close": close_prices,
            "volume": np.random.randint(1000, 10000, 100),
        },
        index=dates,
    )

    # Ensure OHLC relationships are correct
    data["high"] = data[["open", "high", "close"]].max(axis=1)
    data["low"] = data[["open", "low", "close"]].min(axis=1)

    return data


@pytest.fixture
def sample_equity_curve() -> pd.Series:
    """Create sample equity curve for testing metrics."""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="1D")
    equity = pd.Series(
        10000 + np.cumsum(np.random.randn(100) * 100),
        index=dates,
    )
    return equity


@pytest.fixture
def test_config() -> dict:
    """Create test configuration."""
    return {
        "initial_capital": 10000.0,
        "commission": 0.001,
        "slippage": 0.0005,
        "symbol": "BTC/USDT",
        "timeframe": "1h",
    }
