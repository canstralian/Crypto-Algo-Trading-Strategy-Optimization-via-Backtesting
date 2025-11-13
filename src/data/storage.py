"""Data storage module for caching and persistence."""

import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from ..utils.config import get_settings
from ..utils.exceptions import DatabaseError
from ..utils.logger import LoggerMixin


class DataStorage(LoggerMixin):
    """Store and retrieve market data."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        """Initialize data storage.

        Args:
            storage_path: Path to data storage directory
        """
        settings = get_settings()
        self.storage_path = Path(storage_path or settings.data_dir)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized data storage at: {self.storage_path}")

    def save_ohlcv(
        self, df: pd.DataFrame, symbol: str, timeframe: str, format: str = "parquet"
    ) -> None:
        """Save OHLCV data to disk.

        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            timeframe: Timeframe
            format: Storage format (parquet, csv, feather)

        Raises:
            DatabaseError: If save operation fails
        """
        try:
            # Create filename
            safe_symbol = symbol.replace("/", "_")
            filename = f"{safe_symbol}_{timeframe}.{format}"
            filepath = self.storage_path / filename

            # Save based on format
            if format == "parquet":
                df.to_parquet(filepath, compression="gzip")
            elif format == "csv":
                df.to_csv(filepath)
            elif format == "feather":
                df.reset_index().to_feather(filepath)
            else:
                raise ValueError(f"Unsupported format: {format}")

            self.logger.info(f"Saved {len(df)} rows to {filepath}")

        except Exception as e:
            raise DatabaseError(f"Failed to save OHLCV data: {e}")

    def load_ohlcv(
        self, symbol: str, timeframe: str, format: str = "parquet"
    ) -> Optional[pd.DataFrame]:
        """Load OHLCV data from disk.

        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            format: Storage format

        Returns:
            DataFrame with OHLCV data or None if not found

        Raises:
            DatabaseError: If load operation fails
        """
        try:
            safe_symbol = symbol.replace("/", "_")
            filename = f"{safe_symbol}_{timeframe}.{format}"
            filepath = self.storage_path / filename

            if not filepath.exists():
                self.logger.debug(f"Data file not found: {filepath}")
                return None

            # Load based on format
            if format == "parquet":
                df = pd.read_parquet(filepath)
            elif format == "csv":
                df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            elif format == "feather":
                df = pd.read_feather(filepath)
                df.set_index("timestamp", inplace=True)
            else:
                raise ValueError(f"Unsupported format: {format}")

            self.logger.info(f"Loaded {len(df)} rows from {filepath}")
            return df

        except Exception as e:
            raise DatabaseError(f"Failed to load OHLCV data: {e}")

    def save_backtest_results(
        self, results: dict[str, Any], name: str
    ) -> None:
        """Save backtest results.

        Args:
            results: Backtest results dictionary
            name: Name for the results file

        Raises:
            DatabaseError: If save operation fails
        """
        try:
            filename = f"backtest_{name}.json"
            filepath = self.storage_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)

            self.logger.info(f"Saved backtest results to {filepath}")

        except Exception as e:
            raise DatabaseError(f"Failed to save backtest results: {e}")

    def load_backtest_results(self, name: str) -> Optional[dict[str, Any]]:
        """Load backtest results.

        Args:
            name: Name of the results file

        Returns:
            Backtest results dictionary or None if not found

        Raises:
            DatabaseError: If load operation fails
        """
        try:
            filename = f"backtest_{name}.json"
            filepath = self.storage_path / filename

            if not filepath.exists():
                self.logger.debug(f"Results file not found: {filepath}")
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                results = json.load(f)

            self.logger.info(f"Loaded backtest results from {filepath}")
            return results

        except Exception as e:
            raise DatabaseError(f"Failed to load backtest results: {e}")

    def list_available_data(self) -> list[dict[str, str]]:
        """List all available data files.

        Returns:
            List of dictionaries with file information
        """
        files = []

        for filepath in self.storage_path.glob("*"):
            if filepath.is_file():
                files.append(
                    {
                        "name": filepath.name,
                        "path": str(filepath),
                        "size": filepath.stat().st_size,
                    }
                )

        return files

    def delete_data(self, symbol: str, timeframe: str, format: str = "parquet") -> bool:
        """Delete OHLCV data file.

        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            format: Storage format

        Returns:
            True if deleted, False if not found
        """
        try:
            safe_symbol = symbol.replace("/", "_")
            filename = f"{safe_symbol}_{timeframe}.{format}"
            filepath = self.storage_path / filename

            if filepath.exists():
                filepath.unlink()
                self.logger.info(f"Deleted {filepath}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to delete data file: {e}")
            return False
