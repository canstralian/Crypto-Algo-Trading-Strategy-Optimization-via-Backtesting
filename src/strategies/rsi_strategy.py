"""RSI (Relative Strength Index) Strategy."""

import pandas as pd
import ta

from ..core.strategy import Strategy


class RSIStrategy(Strategy):
    """RSI trading strategy.

    Generates buy signals when RSI crosses above oversold level,
    and sell signals when RSI crosses below overbought level.
    """

    def __init__(
        self,
        period: int = 14,
        overbought: float = 70,
        oversold: float = 30,
    ) -> None:
        """Initialize RSI strategy.

        Args:
            period: RSI calculation period
            overbought: Overbought threshold (0-100)
            oversold: Oversold threshold (0-100)
        """
        super().__init__(
            name="RSI",
            period=period,
            overbought=overbought,
            oversold=oversold,
        )

        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI indicator.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with RSI indicator
        """
        data = data.copy()

        # Calculate RSI
        data["rsi"] = ta.momentum.rsi(data["close"], window=self.period)

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on RSI.

        Args:
            data: DataFrame with RSI indicator

        Returns:
            DataFrame with signals
        """
        data = data.copy()

        # Initialize signal column
        data["signal"] = 0

        # Previous RSI for crossover detection
        data["rsi_prev"] = data["rsi"].shift(1)

        # Buy signal: RSI crosses above oversold level
        data.loc[
            (data["rsi"] > self.oversold) & (data["rsi_prev"] <= self.oversold),
            "signal",
        ] = 1

        # Sell signal: RSI crosses below overbought level
        data.loc[
            (data["rsi"] < self.overbought) & (data["rsi_prev"] >= self.overbought),
            "signal",
        ] = -1

        return data
