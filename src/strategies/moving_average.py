"""Moving Average Crossover Strategy."""

import pandas as pd
import ta

from ..core.strategy import Strategy


class MovingAverageCrossover(Strategy):
    """Moving Average Crossover trading strategy.

    Generates buy signals when short MA crosses above long MA,
    and sell signals when short MA crosses below long MA.
    """

    def __init__(
        self,
        short_period: int = 10,
        long_period: int = 30,
        ma_type: str = "sma",
    ) -> None:
        """Initialize MA Crossover strategy.

        Args:
            short_period: Short moving average period
            long_period: Long moving average period
            ma_type: Type of moving average ('sma' or 'ema')
        """
        super().__init__(
            name="MA_Crossover",
            short_period=short_period,
            long_period=long_period,
            ma_type=ma_type,
        )

        self.short_period = short_period
        self.long_period = long_period
        self.ma_type = ma_type.lower()

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with MA indicators
        """
        data = data.copy()

        if self.ma_type == "ema":
            data["ma_short"] = ta.trend.ema_indicator(
                data["close"], window=self.short_period
            )
            data["ma_long"] = ta.trend.ema_indicator(
                data["close"], window=self.long_period
            )
        else:  # sma
            data["ma_short"] = ta.trend.sma_indicator(
                data["close"], window=self.short_period
            )
            data["ma_long"] = ta.trend.sma_indicator(
                data["close"], window=self.long_period
            )

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MA crossover.

        Args:
            data: DataFrame with MA indicators

        Returns:
            DataFrame with signals
        """
        data = data.copy()

        # Initialize signal column
        data["signal"] = 0

        # Calculate crossover
        data["ma_diff"] = data["ma_short"] - data["ma_long"]
        data["ma_diff_prev"] = data["ma_diff"].shift(1)

        # Buy signal: short MA crosses above long MA
        data.loc[
            (data["ma_diff"] > 0) & (data["ma_diff_prev"] <= 0), "signal"
        ] = 1

        # Sell signal: short MA crosses below long MA
        data.loc[
            (data["ma_diff"] < 0) & (data["ma_diff_prev"] >= 0), "signal"
        ] = -1

        return data
