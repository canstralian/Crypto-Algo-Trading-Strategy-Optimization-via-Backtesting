"""Unit tests for trading strategies."""

import pytest
import pandas as pd
import numpy as np

from src.strategies.moving_average import MovingAverageCrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.macd_strategy import MACDStrategy
from src.strategies.bollinger_bands import BollingerBandsStrategy


class TestMovingAverageCrossover:
    """Tests for MA Crossover strategy."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = MovingAverageCrossover(short_period=10, long_period=30)
        assert strategy.short_period == 10
        assert strategy.long_period == 30
        assert strategy.name == "MA_Crossover"

    def test_calculate_indicators(self, sample_ohlcv_data):
        """Test indicator calculation."""
        strategy = MovingAverageCrossover(short_period=10, long_period=20)
        result = strategy.calculate_indicators(sample_ohlcv_data)

        assert "ma_short" in result.columns
        assert "ma_long" in result.columns
        assert not result["ma_short"].isna().all()
        assert not result["ma_long"].isna().all()

    def test_generate_signals(self, sample_ohlcv_data):
        """Test signal generation."""
        strategy = MovingAverageCrossover(short_period=10, long_period=20)
        data = strategy.calculate_indicators(sample_ohlcv_data)
        result = strategy.generate_signals(data)

        assert "signal" in result.columns
        assert result["signal"].isin([-1, 0, 1]).all()

    def test_validate_data_raises_error_on_invalid_data(self):
        """Test that validation raises error on invalid data."""
        strategy = MovingAverageCrossover()
        invalid_data = pd.DataFrame({"invalid": [1, 2, 3]})

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(invalid_data)


class TestRSIStrategy:
    """Tests for RSI strategy."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = RSIStrategy(period=14, overbought=70, oversold=30)
        assert strategy.period == 14
        assert strategy.overbought == 70
        assert strategy.oversold == 30

    def test_calculate_indicators(self, sample_ohlcv_data):
        """Test RSI calculation."""
        strategy = RSIStrategy()
        result = strategy.calculate_indicators(sample_ohlcv_data)

        assert "rsi" in result.columns
        assert (result["rsi"] >= 0).all()
        assert (result["rsi"] <= 100).all()

    def test_generate_signals(self, sample_ohlcv_data):
        """Test signal generation."""
        strategy = RSIStrategy()
        data = strategy.calculate_indicators(sample_ohlcv_data)
        result = strategy.generate_signals(data)

        assert "signal" in result.columns
        assert result["signal"].isin([-1, 0, 1]).all()


class TestMACDStrategy:
    """Tests for MACD strategy."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
        assert strategy.fast_period == 12
        assert strategy.slow_period == 26
        assert strategy.signal_period == 9

    def test_calculate_indicators(self, sample_ohlcv_data):
        """Test MACD calculation."""
        strategy = MACDStrategy()
        result = strategy.calculate_indicators(sample_ohlcv_data)

        assert "macd" in result.columns
        assert "macd_signal" in result.columns
        assert "macd_diff" in result.columns

    def test_generate_signals(self, sample_ohlcv_data):
        """Test signal generation."""
        strategy = MACDStrategy()
        data = strategy.calculate_indicators(sample_ohlcv_data)
        result = strategy.generate_signals(data)

        assert "signal" in result.columns
        assert result["signal"].isin([-1, 0, 1]).all()


class TestBollingerBandsStrategy:
    """Tests for Bollinger Bands strategy."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = BollingerBandsStrategy(period=20, std_dev=2.0)
        assert strategy.period == 20
        assert strategy.std_dev == 2.0

    def test_calculate_indicators(self, sample_ohlcv_data):
        """Test Bollinger Bands calculation."""
        strategy = BollingerBandsStrategy()
        result = strategy.calculate_indicators(sample_ohlcv_data)

        assert "bb_upper" in result.columns
        assert "bb_middle" in result.columns
        assert "bb_lower" in result.columns
        assert (result["bb_upper"] >= result["bb_middle"]).all()
        assert (result["bb_middle"] >= result["bb_lower"]).all()

    def test_generate_signals(self, sample_ohlcv_data):
        """Test signal generation."""
        strategy = BollingerBandsStrategy()
        data = strategy.calculate_indicators(sample_ohlcv_data)
        result = strategy.generate_signals(data)

        assert "signal" in result.columns
        assert result["signal"].isin([-1, 0, 1]).all()
