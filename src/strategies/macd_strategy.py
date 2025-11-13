"""MACD (Moving Average Convergence Divergence) Strategy."""

import pandas as pd
import ta

from ..core.strategy import Strategy


class MACDStrategy(Strategy):
    """MACD trading strategy.

    Generates buy signals when MACD line crosses above signal line,
    and sell signals when MACD line crosses below signal line.
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> None:
        """Initialize MACD strategy.

        Args:
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
        """
        super().__init__(
            name="MACD",
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
        )

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicators.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with MACD indicators
        """
        data = data.copy()

        # Calculate MACD
        macd = ta.trend.MACD(
            data["close"],
            window_slow=self.slow_period,
            window_fast=self.fast_period,
            window_sign=self.signal_period,
        )

        data["macd"] = macd.macd()
        data["macd_signal"] = macd.macd_signal()
        data["macd_diff"] = macd.macd_diff()

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MACD.

        Args:
            data: DataFrame with MACD indicators

        Returns:
            DataFrame with signals
        """
        data = data.copy()

        # Initialize signal column
        data["signal"] = 0

        # Calculate MACD difference and previous difference
        data["macd_histogram"] = data["macd"] - data["macd_signal"]
        data["macd_histogram_prev"] = data["macd_histogram"].shift(1)

        # Buy signal: MACD crosses above signal line
        data.loc[
            (data["macd_histogram"] > 0) & (data["macd_histogram_prev"] <= 0),
            "signal",
        ] = 1

        # Sell signal: MACD crosses below signal line
        data.loc[
            (data["macd_histogram"] < 0) & (data["macd_histogram_prev"] >= 0),
            "signal",
        ] = -1

        return data
