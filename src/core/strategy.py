"""Base strategy class for trading strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import pandas as pd

from ..utils.logger import LoggerMixin


class Signal(Enum):
    """Trading signal enumeration."""

    BUY = 1
    SELL = -1
    HOLD = 0


@dataclass
class StrategyConfig:
    """Base configuration for strategies."""

    name: str
    params: dict[str, Any]


class Strategy(ABC, LoggerMixin):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str, **params: Any) -> None:
        """Initialize strategy.

        Args:
            name: Strategy name
            **params: Strategy parameters
        """
        self.name = name
        self.params = params
        self.signals: list[dict] = []

        self.logger.info(f"Initialized {name} strategy with params: {params}")

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals from market data.

        Args:
            data: DataFrame with OHLCV and indicator data

        Returns:
            DataFrame with signals column added
        """
        pass

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate strategy-specific indicators.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with indicators added
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data has required columns.

        Args:
            data: DataFrame to validate

        Returns:
            True if valid

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ["open", "high", "low", "close", "volume"]
        missing = [col for col in required_columns if col not in data.columns]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        if data.empty:
            raise ValueError("Data is empty")

        return True

    def get_signal_at(self, data: pd.DataFrame, index: int) -> Signal:
        """Get signal at specific index.

        Args:
            data: DataFrame with signals
            index: Index to get signal from

        Returns:
            Signal enum value
        """
        if "signal" not in data.columns:
            return Signal.HOLD

        signal_value = data.iloc[index]["signal"]

        if signal_value > 0:
            return Signal.BUY
        elif signal_value < 0:
            return Signal.SELL
        else:
            return Signal.HOLD

    def backtest(
        self,
        data: pd.DataFrame,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
    ) -> dict[str, Any]:
        """Simple backtest of the strategy.

        Args:
            data: Historical data
            initial_capital: Starting capital
            commission: Commission rate

        Returns:
            Dictionary with backtest results
        """
        self.validate_data(data)

        # Calculate indicators and generate signals
        data = self.calculate_indicators(data)
        data = self.generate_signals(data)

        # Simple equity curve calculation
        capital = initial_capital
        position = 0.0
        trades = []

        for i in range(len(data)):
            signal = self.get_signal_at(data, i)
            price = data.iloc[i]["close"]

            if signal == Signal.BUY and position == 0:
                # Buy
                shares = capital / price
                cost = shares * price * (1 + commission)
                if cost <= capital:
                    position = shares
                    capital -= cost
                    trades.append(
                        {"type": "buy", "price": price, "shares": shares, "index": i}
                    )

            elif signal == Signal.SELL and position > 0:
                # Sell
                proceeds = position * price * (1 - commission)
                capital += proceeds
                trades.append(
                    {"type": "sell", "price": price, "shares": position, "index": i}
                )
                position = 0

        # Close any open position
        if position > 0:
            final_price = data.iloc[-1]["close"]
            proceeds = position * final_price * (1 - commission)
            capital += proceeds
            trades.append(
                {
                    "type": "sell",
                    "price": final_price,
                    "shares": position,
                    "index": len(data) - 1,
                }
            )

        final_equity = capital
        total_return = (final_equity / initial_capital - 1) * 100

        return {
            "strategy": self.name,
            "initial_capital": initial_capital,
            "final_equity": final_equity,
            "total_return": total_return,
            "total_trades": len(trades),
            "trades": trades,
        }

    def optimize(
        self,
        data: pd.DataFrame,
        param_grid: dict[str, list[Any]],
    ) -> dict[str, Any]:
        """Optimize strategy parameters.

        Args:
            data: Historical data
            param_grid: Dictionary of parameter ranges

        Returns:
            Best parameters and results
        """
        # This is a placeholder for parameter optimization
        # In production, implement grid search or Bayesian optimization
        raise NotImplementedError("Parameter optimization not yet implemented")

    def get_config(self) -> StrategyConfig:
        """Get strategy configuration.

        Returns:
            StrategyConfig instance
        """
        return StrategyConfig(name=self.name, params=self.params)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name}({self.params})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Strategy(name='{self.name}', params={self.params})"
