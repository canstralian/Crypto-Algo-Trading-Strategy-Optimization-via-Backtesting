"""Data fetching module using CCXT."""

from datetime import datetime, timedelta
from typing import Any, Optional

import ccxt
import pandas as pd

from ..utils.exceptions import DataFetchError
from ..utils.logger import LoggerMixin
from ..utils.validators import validate_symbol, validate_timeframe


class DataFetcher(LoggerMixin):
    """Fetch cryptocurrency data from exchanges using CCXT."""

    def __init__(
        self,
        exchange_name: str = "binance",
        sandbox: bool = True,
        rate_limit: bool = True,
        timeout: int = 30000,
    ) -> None:
        """Initialize data fetcher.

        Args:
            exchange_name: Name of the exchange (binance, coinbase, etc.)
            sandbox: Use testnet/sandbox mode
            rate_limit: Enable rate limiting
            timeout: Request timeout in milliseconds
        """
        self.exchange_name = exchange_name
        self.sandbox = sandbox

        try:
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange: ccxt.Exchange = exchange_class(
                {
                    "enableRateLimit": rate_limit,
                    "timeout": timeout,
                }
            )

            if sandbox and hasattr(self.exchange, "set_sandbox_mode"):
                self.exchange.set_sandbox_mode(True)

            self.logger.info(
                f"Initialized {exchange_name} exchange (sandbox: {sandbox})"
            )

        except AttributeError:
            raise DataFetchError(f"Exchange '{exchange_name}' not supported by CCXT")
        except Exception as e:
            raise DataFetchError(f"Failed to initialize exchange: {e}")

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: Optional[datetime] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """Fetch OHLCV (candlestick) data.

        Args:
            symbol: Trading pair symbol (e.g., BTC/USDT)
            timeframe: Timeframe for candles (1m, 5m, 1h, 1d, etc.)
            since: Start date for historical data
            limit: Maximum number of candles to fetch

        Returns:
            DataFrame with OHLCV data

        Raises:
            DataFetchError: If data fetching fails
        """
        try:
            symbol = validate_symbol(symbol)
            timeframe = validate_timeframe(timeframe)

            # Convert datetime to timestamp in milliseconds
            since_ts = None
            if since:
                since_ts = int(since.timestamp() * 1000)

            self.logger.info(
                f"Fetching {symbol} {timeframe} data (limit: {limit})"
            )

            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, timeframe=timeframe, since=since_ts, limit=limit
            )

            if not ohlcv:
                raise DataFetchError(f"No data returned for {symbol}")

            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

            self.logger.info(f"Fetched {len(df)} candles for {symbol}")

            return df

        except Exception as e:
            raise DataFetchError(f"Failed to fetch OHLCV data: {e}")

    def fetch_ohlcv_range(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """Fetch OHLCV data for a date range.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe for candles
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with OHLCV data

        Raises:
            DataFetchError: If data fetching fails
        """
        all_data = []
        current_date = start_date
        limit = 1000  # Maximum per request

        try:
            while current_date < end_date:
                df = self.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=current_date,
                    limit=limit,
                )

                if df.empty:
                    break

                all_data.append(df)

                # Move to next batch
                current_date = df.index[-1].to_pydatetime() + timedelta(seconds=1)

                # Break if we've reached the end date
                if current_date >= end_date:
                    break

            if not all_data:
                raise DataFetchError(
                    f"No data available for {symbol} between {start_date} and {end_date}"
                )

            # Combine all data
            result = pd.concat(all_data)

            # Filter to exact date range
            result = result[
                (result.index >= start_date) & (result.index <= end_date)
            ]

            # Remove duplicates
            result = result[~result.index.duplicated(keep="first")]

            self.logger.info(
                f"Fetched {len(result)} candles for {symbol} "
                f"from {start_date} to {end_date}"
            )

            return result

        except Exception as e:
            raise DataFetchError(f"Failed to fetch data range: {e}")

    def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        """Fetch current ticker information.

        Args:
            symbol: Trading pair symbol

        Returns:
            Ticker information dictionary

        Raises:
            DataFetchError: If ticker fetch fails
        """
        try:
            symbol = validate_symbol(symbol)
            ticker = self.exchange.fetch_ticker(symbol)
            self.logger.debug(f"Fetched ticker for {symbol}: {ticker['last']}")
            return ticker

        except Exception as e:
            raise DataFetchError(f"Failed to fetch ticker: {e}")

    def fetch_order_book(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        """Fetch order book data.

        Args:
            symbol: Trading pair symbol
            limit: Depth of order book

        Returns:
            Order book dictionary

        Raises:
            DataFetchError: If order book fetch fails
        """
        try:
            symbol = validate_symbol(symbol)
            order_book = self.exchange.fetch_order_book(symbol, limit=limit)
            return order_book

        except Exception as e:
            raise DataFetchError(f"Failed to fetch order book: {e}")

    def get_available_symbols(self) -> list[str]:
        """Get list of available trading symbols.

        Returns:
            List of available symbols

        Raises:
            DataFetchError: If markets fetch fails
        """
        try:
            self.exchange.load_markets()
            symbols = list(self.exchange.symbols)
            self.logger.info(f"Found {len(symbols)} available symbols")
            return symbols

        except Exception as e:
            raise DataFetchError(f"Failed to fetch available symbols: {e}")

    def get_exchange_info(self) -> dict[str, Any]:
        """Get exchange information.

        Returns:
            Exchange information dictionary
        """
        return {
            "name": self.exchange.name,
            "id": self.exchange.id,
            "has_fetch_ohlcv": self.exchange.has["fetchOHLCV"],
            "has_fetch_ticker": self.exchange.has["fetchTicker"],
            "has_fetch_order_book": self.exchange.has["fetchOrderBook"],
            "timeframes": self.exchange.timeframes if hasattr(self.exchange, "timeframes") else None,
            "sandbox": self.sandbox,
        }
