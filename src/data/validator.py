"""Data validation utilities."""

from typing import Any

import pandas as pd

from ..utils.exceptions import ValidationError
from ..utils.logger import LoggerMixin


class DataValidator(LoggerMixin):
    """Validate market data integrity and quality."""

    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> bool:
        """Validate OHLCV DataFrame structure and data quality.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        # Check required columns
        required_columns = ["open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValidationError(
                f"Missing required columns: {missing_columns}",
                details={"missing": missing_columns, "present": df.columns.tolist()},
            )

        # Check for empty DataFrame
        if df.empty:
            raise ValidationError("DataFrame is empty")

        # Check for negative values
        for col in ["open", "high", "low", "close", "volume"]:
            if (df[col] < 0).any():
                raise ValidationError(
                    f"Negative values found in column: {col}",
                    details={"column": col, "min_value": df[col].min()},
                )

        # Check OHLC relationship: high >= low
        if (df["high"] < df["low"]).any():
            invalid_rows = df[df["high"] < df["low"]]
            raise ValidationError(
                "Invalid OHLC data: high < low",
                details={"invalid_rows": len(invalid_rows)},
            )

        # Check OHLC relationship: high >= open, close
        if ((df["high"] < df["open"]) | (df["high"] < df["close"])).any():
            invalid_rows = df[(df["high"] < df["open"]) | (df["high"] < df["close"])]
            raise ValidationError(
                "Invalid OHLC data: high < open or close",
                details={"invalid_rows": len(invalid_rows)},
            )

        # Check OHLC relationship: low <= open, close
        if ((df["low"] > df["open"]) | (df["low"] > df["close"])).any():
            invalid_rows = df[(df["low"] > df["open"]) | (df["low"] > df["close"])]
            raise ValidationError(
                "Invalid OHLC data: low > open or close",
                details={"invalid_rows": len(invalid_rows)},
            )

        # Check for duplicate timestamps
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].tolist()
            raise ValidationError(
                "Duplicate timestamps found",
                details={"duplicate_count": len(duplicates)},
            )

        return True

    @staticmethod
    def check_data_gaps(df: pd.DataFrame, expected_freq: str = "1H") -> dict[str, Any]:
        """Check for gaps in time series data.

        Args:
            df: DataFrame with datetime index
            expected_freq: Expected frequency of data

        Returns:
            Dictionary with gap information
        """
        if len(df) < 2:
            return {"has_gaps": False, "gap_count": 0, "gaps": []}

        # Create expected index
        expected_index = pd.date_range(
            start=df.index.min(), end=df.index.max(), freq=expected_freq
        )

        # Find missing timestamps
        missing_timestamps = expected_index.difference(df.index)

        gaps = []
        if len(missing_timestamps) > 0:
            gaps = [ts.isoformat() for ts in missing_timestamps[:10]]  # Limit to first 10

        return {
            "has_gaps": len(missing_timestamps) > 0,
            "gap_count": len(missing_timestamps),
            "gaps": gaps,
            "completeness": (len(df) / len(expected_index)) * 100,
        }

    @staticmethod
    def detect_outliers(
        df: pd.DataFrame, column: str = "close", threshold: float = 3.0
    ) -> dict[str, Any]:
        """Detect outliers using z-score method.

        Args:
            df: DataFrame
            column: Column to check for outliers
            threshold: Z-score threshold

        Returns:
            Dictionary with outlier information
        """
        if column not in df.columns:
            raise ValidationError(f"Column not found: {column}")

        mean = df[column].mean()
        std = df[column].std()

        if std == 0:
            return {"has_outliers": False, "outlier_count": 0, "outliers": []}

        z_scores = abs((df[column] - mean) / std)
        outliers = df[z_scores > threshold]

        return {
            "has_outliers": len(outliers) > 0,
            "outlier_count": len(outliers),
            "outliers": outliers.index.tolist()[:10],  # Limit to first 10
            "percentage": (len(outliers) / len(df)) * 100,
        }

    @staticmethod
    def validate_data_quality(df: pd.DataFrame) -> dict[str, Any]:
        """Comprehensive data quality check.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary with quality metrics
        """
        quality_report = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "null_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicate_rows": df.duplicated().sum(),
        }

        # Add basic statistics
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        if len(numeric_cols) > 0:
            quality_report["statistics"] = df[numeric_cols].describe().to_dict()

        return quality_report
