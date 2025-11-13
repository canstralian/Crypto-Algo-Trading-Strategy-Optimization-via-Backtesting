"""Performance metrics calculation."""

import numpy as np
import pandas as pd
from typing import Optional


class PerformanceMetrics:
    """Calculate performance metrics for trading strategies."""

    def __init__(self, equity_curve: pd.Series, risk_free_rate: float = 0.02) -> None:
        """Initialize performance metrics calculator.

        Args:
            equity_curve: Series of equity values over time
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.equity_curve = equity_curve
        self.risk_free_rate = risk_free_rate
        self.returns = equity_curve.pct_change().dropna()

    def total_return(self) -> float:
        """Calculate total return percentage.

        Returns:
            Total return as percentage
        """
        if len(self.equity_curve) == 0:
            return 0.0

        initial = self.equity_curve.iloc[0]
        final = self.equity_curve.iloc[-1]

        return ((final / initial) - 1) * 100

    def annualized_return(self, periods_per_year: int = 252) -> float:
        """Calculate annualized return.

        Args:
            periods_per_year: Trading periods per year (252 for daily, 252*24 for hourly)

        Returns:
            Annualized return as percentage
        """
        if len(self.equity_curve) < 2:
            return 0.0

        total_return = self.total_return() / 100
        years = len(self.equity_curve) / periods_per_year

        if years <= 0:
            return 0.0

        annualized = ((1 + total_return) ** (1 / years)) - 1
        return annualized * 100

    def sharpe_ratio(self, periods_per_year: int = 252) -> float:
        """Calculate Sharpe ratio.

        Args:
            periods_per_year: Trading periods per year

        Returns:
            Sharpe ratio
        """
        if len(self.returns) == 0:
            return 0.0

        excess_returns = self.returns - (self.risk_free_rate / periods_per_year)

        if excess_returns.std() == 0:
            return 0.0

        sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)
        return sharpe

    def sortino_ratio(self, periods_per_year: int = 252) -> float:
        """Calculate Sortino ratio (uses downside deviation).

        Args:
            periods_per_year: Trading periods per year

        Returns:
            Sortino ratio
        """
        if len(self.returns) == 0:
            return 0.0

        excess_returns = self.returns - (self.risk_free_rate / periods_per_year)
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(periods_per_year)
        return sortino

    def max_drawdown(self) -> float:
        """Calculate maximum drawdown percentage.

        Returns:
            Maximum drawdown as percentage
        """
        if len(self.equity_curve) == 0:
            return 0.0

        cummax = self.equity_curve.expanding().max()
        drawdown = (self.equity_curve - cummax) / cummax
        max_dd = drawdown.min()

        return abs(max_dd) * 100

    def calmar_ratio(self) -> float:
        """Calculate Calmar ratio (annualized return / max drawdown).

        Returns:
            Calmar ratio
        """
        max_dd = self.max_drawdown()

        if max_dd == 0:
            return 0.0

        ann_return = self.annualized_return()
        return ann_return / max_dd

    def volatility(self, periods_per_year: int = 252) -> float:
        """Calculate annualized volatility.

        Args:
            periods_per_year: Trading periods per year

        Returns:
            Annualized volatility as percentage
        """
        if len(self.returns) == 0:
            return 0.0

        return self.returns.std() * np.sqrt(periods_per_year) * 100

    def value_at_risk(self, confidence: float = 0.95) -> float:
        """Calculate Value at Risk (VaR).

        Args:
            confidence: Confidence level (default: 95%)

        Returns:
            VaR as percentage
        """
        if len(self.returns) == 0:
            return 0.0

        var = np.percentile(self.returns, (1 - confidence) * 100)
        return abs(var) * 100

    def conditional_var(self, confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (CVaR/Expected Shortfall).

        Args:
            confidence: Confidence level (default: 95%)

        Returns:
            CVaR as percentage
        """
        if len(self.returns) == 0:
            return 0.0

        var = np.percentile(self.returns, (1 - confidence) * 100)
        cvar = self.returns[self.returns <= var].mean()

        return abs(cvar) * 100

    def get_all_metrics(self) -> dict:
        """Get all performance metrics.

        Returns:
            Dictionary with all metrics
        """
        return {
            "total_return": self.total_return(),
            "annualized_return": self.annualized_return(),
            "sharpe_ratio": self.sharpe_ratio(),
            "sortino_ratio": self.sortino_ratio(),
            "max_drawdown": self.max_drawdown(),
            "calmar_ratio": self.calmar_ratio(),
            "volatility": self.volatility(),
            "value_at_risk_95": self.value_at_risk(0.95),
            "conditional_var_95": self.conditional_var(0.95),
        }
