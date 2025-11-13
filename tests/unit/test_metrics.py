"""Unit tests for performance metrics."""

import pytest
import pandas as pd
import numpy as np

from src.analysis.metrics import PerformanceMetrics


class TestPerformanceMetrics:
    """Tests for performance metrics calculations."""

    def test_total_return(self, sample_equity_curve):
        """Test total return calculation."""
        metrics = PerformanceMetrics(sample_equity_curve)
        total_return = metrics.total_return()

        assert isinstance(total_return, float)
        assert total_return != 0  # Should have some return

    def test_sharpe_ratio(self, sample_equity_curve):
        """Test Sharpe ratio calculation."""
        metrics = PerformanceMetrics(sample_equity_curve)
        sharpe = metrics.sharpe_ratio()

        assert isinstance(sharpe, float)

    def test_max_drawdown(self, sample_equity_curve):
        """Test maximum drawdown calculation."""
        metrics = PerformanceMetrics(sample_equity_curve)
        max_dd = metrics.max_drawdown()

        assert isinstance(max_dd, float)
        assert max_dd >= 0  # Drawdown is always positive

    def test_sortino_ratio(self, sample_equity_curve):
        """Test Sortino ratio calculation."""
        metrics = PerformanceMetrics(sample_equity_curve)
        sortino = metrics.sortino_ratio()

        assert isinstance(sortino, float)

    def test_volatility(self, sample_equity_curve):
        """Test volatility calculation."""
        metrics = PerformanceMetrics(sample_equity_curve)
        vol = metrics.volatility()

        assert isinstance(vol, float)
        assert vol >= 0

    def test_empty_equity_curve(self):
        """Test metrics with empty equity curve."""
        empty_curve = pd.Series([], dtype=float)
        metrics = PerformanceMetrics(empty_curve)

        assert metrics.total_return() == 0.0
        assert metrics.max_drawdown() == 0.0

    def test_get_all_metrics(self, sample_equity_curve):
        """Test getting all metrics at once."""
        metrics = PerformanceMetrics(sample_equity_curve)
        all_metrics = metrics.get_all_metrics()

        assert isinstance(all_metrics, dict)
        assert "total_return" in all_metrics
        assert "sharpe_ratio" in all_metrics
        assert "max_drawdown" in all_metrics
        assert "volatility" in all_metrics
