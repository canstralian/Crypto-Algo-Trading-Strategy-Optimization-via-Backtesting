"""Bollinger Bands Strategy."""

import pandas as pd
import ta

from ..core.strategy import Strategy


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands trading strategy.

    Generates buy signals when price crosses below lower band,
    and sell signals when price crosses above upper band.
    """

    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        use_breakout: bool = False,
    ) -> None:
        """Initialize Bollinger Bands strategy.

        Args:
            period: Moving average period
            std_dev: Number of standard deviations for bands
            use_breakout: If True, buy on upper breakout; if False, buy on lower bounce
        """
        super().__init__(
            name="Bollinger_Bands",
            period=period,
            std_dev=std_dev,
            use_breakout=use_breakout,
        )

        self.period = period
        self.std_dev = std_dev
        self.use_breakout = use_breakout

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with Bollinger Bands indicators
        """
        data = data.copy()

        # Calculate Bollinger Bands
        bollinger = ta.volatility.BollingerBands(
            data["close"], window=self.period, window_dev=self.std_dev
        )

        data["bb_upper"] = bollinger.bollinger_hband()
        data["bb_middle"] = bollinger.bollinger_mavg()
        data["bb_lower"] = bollinger.bollinger_lband()
        data["bb_width"] = bollinger.bollinger_wband()
        data["bb_pct"] = bollinger.bollinger_pband()

        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on Bollinger Bands.

        Args:
            data: DataFrame with Bollinger Bands indicators

        Returns:
            DataFrame with signals
        """
        data = data.copy()

        # Initialize signal column
        data["signal"] = 0

        # Previous close for crossover detection
        data["close_prev"] = data["close"].shift(1)

        if self.use_breakout:
            # Breakout strategy: buy on upper band breakout
            data.loc[
                (data["close"] > data["bb_upper"]) & (data["close_prev"] <= data["bb_upper"]),
                "signal",
            ] = 1

            # Sell on lower band breakout
            data.loc[
                (data["close"] < data["bb_lower"]) & (data["close_prev"] >= data["bb_lower"]),
                "signal",
            ] = -1

        else:
            # Mean reversion strategy: buy when price bounces from lower band
            data.loc[
                (data["close"] < data["bb_lower"]) & (data["close_prev"] >= data["bb_lower"]),
                "signal",
            ] = 1

            # Sell when price reaches upper band
            data.loc[
                (data["close"] > data["bb_upper"]) & (data["close_prev"] <= data["bb_upper"]),
                "signal",
            ] = -1

        return data
