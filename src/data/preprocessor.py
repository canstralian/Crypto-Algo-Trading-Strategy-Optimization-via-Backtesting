"""Data preprocessing and feature engineering."""

from typing import Optional

import numpy as np
import pandas as pd
import ta

from ..utils.logger import LoggerMixin


class DataPreprocessor(LoggerMixin):
    """Preprocess and add technical indicators to OHLCV data."""

    @staticmethod
    def add_technical_indicators(
        df: pd.DataFrame, include_all: bool = False
    ) -> pd.DataFrame:
        """Add technical indicators to OHLCV data.

        Args:
            df: DataFrame with OHLCV data
            include_all: Include all available indicators

        Returns:
            DataFrame with added technical indicators
        """
        df = df.copy()

        # Moving Averages
        df["sma_10"] = ta.trend.sma_indicator(df["close"], window=10)
        df["sma_20"] = ta.trend.sma_indicator(df["close"], window=20)
        df["sma_50"] = ta.trend.sma_indicator(df["close"], window=50)
        df["ema_10"] = ta.trend.ema_indicator(df["close"], window=10)
        df["ema_20"] = ta.trend.ema_indicator(df["close"], window=20)

        # RSI
        df["rsi"] = ta.momentum.rsi(df["close"], window=14)

        # MACD
        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_diff"] = macd.macd_diff()

        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
        df["bb_upper"] = bollinger.bollinger_hband()
        df["bb_middle"] = bollinger.bollinger_mavg()
        df["bb_lower"] = bollinger.bollinger_lband()
        df["bb_width"] = bollinger.bollinger_wband()

        # ATR (Average True Range)
        df["atr"] = ta.volatility.average_true_range(
            df["high"], df["low"], df["close"], window=14
        )

        if include_all:
            # Stochastic Oscillator
            stoch = ta.momentum.StochasticOscillator(
                df["high"], df["low"], df["close"]
            )
            df["stoch_k"] = stoch.stoch()
            df["stoch_d"] = stoch.stoch_signal()

            # ADX (Average Directional Index)
            df["adx"] = ta.trend.adx(df["high"], df["low"], df["close"], window=14)

            # CCI (Commodity Channel Index)
            df["cci"] = ta.trend.cci(df["high"], df["low"], df["close"], window=20)

            # Williams %R
            df["williams_r"] = ta.momentum.williams_r(
                df["high"], df["low"], df["close"], lbp=14
            )

            # On-Balance Volume
            df["obv"] = ta.volume.on_balance_volume(df["close"], df["volume"])

            # Money Flow Index
            df["mfi"] = ta.volume.money_flow_index(
                df["high"], df["low"], df["close"], df["volume"], window=14
            )

        return df

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean data by handling missing values and outliers.

        Args:
            df: DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        df = df.copy()

        # Forward fill missing values
        df.fillna(method="ffill", inplace=True)

        # Backward fill any remaining NaN values
        df.fillna(method="bfill", inplace=True)

        # Remove any remaining NaN rows
        df.dropna(inplace=True)

        return df

    @staticmethod
    def resample_data(
        df: pd.DataFrame, target_timeframe: str
    ) -> pd.DataFrame:
        """Resample OHLCV data to a different timeframe.

        Args:
            df: DataFrame with OHLCV data
            target_timeframe: Target timeframe (e.g., '1H', '1D')

        Returns:
            Resampled DataFrame
        """
        resampled = df.resample(target_timeframe).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )

        # Remove any NaN values that might result from resampling
        resampled.dropna(inplace=True)

        return resampled

    @staticmethod
    def normalize_data(
        df: pd.DataFrame, columns: Optional[list[str]] = None
    ) -> pd.DataFrame:
        """Normalize data using min-max scaling.

        Args:
            df: DataFrame to normalize
            columns: Specific columns to normalize (default: all numeric)

        Returns:
            Normalized DataFrame
        """
        df = df.copy()

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in columns:
            if col in df.columns:
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df[f"{col}_normalized"] = (df[col] - min_val) / (max_val - min_val)

        return df

    @staticmethod
    def add_returns(df: pd.DataFrame) -> pd.DataFrame:
        """Add return calculations.

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with returns
        """
        df = df.copy()

        # Simple returns
        df["returns"] = df["close"].pct_change()

        # Log returns
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # Cumulative returns
        df["cumulative_returns"] = (1 + df["returns"]).cumprod()

        return df

    @staticmethod
    def add_lags(
        df: pd.DataFrame, column: str = "close", lags: int = 5
    ) -> pd.DataFrame:
        """Add lagged features.

        Args:
            df: DataFrame
            column: Column to create lags for
            lags: Number of lags to create

        Returns:
            DataFrame with lagged features
        """
        df = df.copy()

        for i in range(1, lags + 1):
            df[f"{column}_lag_{i}"] = df[column].shift(i)

        return df
