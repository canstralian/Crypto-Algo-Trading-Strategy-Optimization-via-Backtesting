"""Integration tests for complete backtest flow."""

import pytest
import pandas as pd

from src.core.backtester import Backtester
from src.strategies.moving_average import MovingAverageCrossover
from src.strategies.rsi_strategy import RSIStrategy
from src.data.preprocessor import DataPreprocessor


class TestBacktestFlow:
    """Integration tests for backtesting workflow."""

    def test_complete_backtest_ma_strategy(self, sample_ohlcv_data):
        """Test complete backtest with MA strategy."""
        # Prepare data
        preprocessor = DataPreprocessor()
        data = preprocessor.add_technical_indicators(sample_ohlcv_data)
        data = preprocessor.clean_data(data)

        # Create strategy and backtester
        strategy = MovingAverageCrossover(short_period=10, long_period=20)
        backtester = Backtester(
            strategy=strategy,
            initial_capital=10000,
            commission=0.001,
            slippage=0.0005,
        )

        # Run backtest
        results = backtester.run(data, symbol="BTC/USDT")

        # Verify results structure
        assert "strategy" in results
        assert "initial_capital" in results
        assert "final_equity" in results
        assert "total_return" in results
        assert "metrics" in results
        assert "trades" in results
        assert "equity_curve" in results

        # Verify metrics
        assert isinstance(results["metrics"]["total_return"], float)
        assert isinstance(results["metrics"]["sharpe_ratio"], float)
        assert isinstance(results["metrics"]["max_drawdown"], float)
        assert results["metrics"]["total_trades"] >= 0

    def test_complete_backtest_rsi_strategy(self, sample_ohlcv_data):
        """Test complete backtest with RSI strategy."""
        preprocessor = DataPreprocessor()
        data = preprocessor.add_technical_indicators(sample_ohlcv_data)
        data = preprocessor.clean_data(data)

        strategy = RSIStrategy(period=14, overbought=70, oversold=30)
        backtester = Backtester(
            strategy=strategy,
            initial_capital=10000,
        )

        results = backtester.run(data, symbol="BTC/USDT")

        assert results["initial_capital"] == 10000
        assert "final_equity" in results
        assert len(results["equity_curve"]) > 0

    def test_backtest_with_risk_based_position_sizing(self, sample_ohlcv_data):
        """Test backtest with risk-based position sizing."""
        preprocessor = DataPreprocessor()
        data = preprocessor.add_technical_indicators(sample_ohlcv_data)
        data = preprocessor.clean_data(data)

        strategy = MovingAverageCrossover()
        backtester = Backtester(strategy=strategy, initial_capital=10000)

        results = backtester.run(
            data,
            symbol="BTC/USDT",
            position_sizing="risk_based",
        )

        assert "metrics" in results
        assert results["metrics"]["total_trades"] >= 0

    def test_equity_curve_generation(self, sample_ohlcv_data):
        """Test that equity curve is properly generated."""
        preprocessor = DataPreprocessor()
        data = preprocessor.add_technical_indicators(sample_ohlcv_data)
        data = preprocessor.clean_data(data)

        strategy = MovingAverageCrossover()
        backtester = Backtester(strategy=strategy, initial_capital=10000)
        results = backtester.run(data, symbol="BTC/USDT")

        equity_curve = results["equity_curve"]
        assert len(equity_curve) > 0
        assert all("equity" in point for point in equity_curve)
        assert all("timestamp" in point for point in equity_curve)
