"""
Configuration schemas with Pydantic validation
Implements intelligent validation with helpful error messages
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List
from datetime import datetime
from enum import Enum


class TimeFrame(str, Enum):
    """Supported timeframes"""

    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"


class ExchangeName(str, Enum):
    """Supported exchanges"""

    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"


class ExchangeConfig(BaseModel):
    """Exchange API configuration with validation"""

    name: ExchangeName = Field(description="Exchange name")
    api_key: str = Field(description="API key (store in .env file)")
    api_secret: str = Field(description="API secret (store in .env file)")
    testnet: bool = Field(default=True, description="Use testnet for safety")
    rate_limit_delay: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Delay between API calls in seconds"
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError(
                "API key appears too short. Please verify you've copied the complete key from your exchange."
            )
        return v

    @field_validator("api_secret")
    @classmethod
    def validate_api_secret(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError(
                "API secret appears too short. Please verify you've copied the complete secret from your exchange."
            )
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "binance",
                    "api_key": "your_api_key_here",
                    "api_secret": "your_api_secret_here",
                    "testnet": True,
                    "rate_limit_delay": 1.0,
                }
            ]
        }


class StrategyConfig(BaseModel):
    """Base strategy configuration with common parameters"""

    name: str = Field(description="Strategy identifier")
    description: Optional[str] = Field(
        default="", description="Strategy description"
    )
    timeframe: TimeFrame = Field(
        default=TimeFrame.ONE_HOUR, description="Candlestick timeframe"
    )

    # Moving Average parameters
    ma_fast: int = Field(
        default=10, ge=2, le=200, description="Fast moving average period (2-200)"
    )
    ma_slow: int = Field(
        default=30, ge=2, le=200, description="Slow moving average period (2-200)"
    )

    # RSI parameters
    rsi_period: int = Field(
        default=14, ge=2, le=100, description="RSI calculation period (2-100)"
    )
    rsi_oversold: float = Field(
        default=30.0, ge=0.0, le=50.0, description="RSI oversold level (0-50)"
    )
    rsi_overbought: float = Field(
        default=70.0, ge=50.0, le=100.0, description="RSI overbought level (50-100)"
    )

    # Risk management
    risk_per_trade: float = Field(
        default=0.02,
        gt=0.0,
        le=0.1,
        description="Risk per trade as percentage of capital (0-10%)",
    )
    max_positions: int = Field(
        default=1, ge=1, le=10, description="Maximum concurrent positions (1-10)"
    )
    stop_loss_pct: float = Field(
        default=0.02,
        gt=0.0,
        le=0.2,
        description="Stop loss percentage (0-20%)",
    )
    take_profit_pct: float = Field(
        default=0.04,
        gt=0.0,
        le=0.5,
        description="Take profit percentage (0-50%)",
    )

    @field_validator("ma_slow")
    @classmethod
    def validate_ma_order(cls, v: int, info) -> int:
        """Ensure slow MA is greater than fast MA"""
        if "ma_fast" in info.data and v <= info.data["ma_fast"]:
            raise ValueError(
                f"Slow MA ({v}) must be greater than fast MA ({info.data['ma_fast']}). "
                "Typically, slow MA should be 2-3x the fast MA period."
            )
        return v

    @field_validator("rsi_overbought")
    @classmethod
    def validate_rsi_levels(cls, v: float, info) -> float:
        """Ensure overbought > oversold"""
        if "rsi_oversold" in info.data and v <= info.data["rsi_oversold"]:
            raise ValueError(
                f"RSI overbought level ({v}) must be greater than oversold level ({info.data['rsi_oversold']}). "
                "Common values: oversold=30, overbought=70"
            )
        return v

    @field_validator("take_profit_pct")
    @classmethod
    def validate_risk_reward(cls, v: float, info) -> float:
        """Warn if risk-reward ratio is unfavorable"""
        if "stop_loss_pct" in info.data:
            ratio = v / info.data["stop_loss_pct"]
            if ratio < 1.5:
                raise ValueError(
                    f"Take profit ({v:.1%}) / Stop loss ({info.data['stop_loss_pct']:.1%}) "
                    f"ratio is {ratio:.2f}. Recommended: at least 1.5 for profitable trading. "
                    "Consider increasing take_profit_pct or reducing stop_loss_pct."
                )
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Conservative MA Crossover",
                    "description": "Low-risk moving average crossover strategy",
                    "timeframe": "1h",
                    "ma_fast": 10,
                    "ma_slow": 30,
                    "risk_per_trade": 0.01,
                    "stop_loss_pct": 0.02,
                    "take_profit_pct": 0.04,
                }
            ]
        }


class BacktestConfig(BaseModel):
    """Backtesting configuration"""

    start_date: datetime = Field(description="Backtest start date")
    end_date: datetime = Field(description="Backtest end date")
    initial_capital: float = Field(
        default=10000.0, gt=0, description="Starting capital in USD"
    )
    commission: float = Field(
        default=0.001,
        ge=0,
        le=0.01,
        description="Trading commission as percentage (0-1%)",
    )
    slippage: float = Field(
        default=0.0005,
        ge=0,
        le=0.01,
        description="Price slippage as percentage (0-1%)",
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: datetime, info) -> datetime:
        """Ensure end date is after start date"""
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError(
                f"End date ({v.date()}) must be after start date ({info.data['start_date'].date()}). "
                "Please adjust your backtest period."
            )

        # Check if dates are in the future
        if v > datetime.now():
            raise ValueError(
                f"End date ({v.date()}) is in the future. "
                "Backtesting requires historical data only."
            )

        # Check if period is reasonable
        if "start_date" in info.data:
            days = (v - info.data["start_date"]).days
            if days < 7:
                raise ValueError(
                    f"Backtest period is only {days} days. "
                    "Minimum recommended: 30 days for meaningful results."
                )
            if days > 1825:  # 5 years
                raise ValueError(
                    f"Backtest period is {days} days ({days/365:.1f} years). "
                    "Consider splitting into smaller periods for better performance."
                )

        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "start_date": "2023-01-01T00:00:00",
                    "end_date": "2024-01-01T00:00:00",
                    "initial_capital": 10000.0,
                    "commission": 0.001,
                    "slippage": 0.0005,
                }
            ]
        }


class OptimizationConfig(BaseModel):
    """Parameter optimization configuration"""

    method: Literal["grid", "genetic", "bayesian"] = Field(
        default="genetic", description="Optimization method"
    )
    max_iterations: int = Field(
        default=100, ge=10, le=10000, description="Maximum iterations (10-10000)"
    )
    optimization_metric: Literal[
        "sharpe_ratio", "total_return", "profit_factor", "calmar_ratio"
    ] = Field(default="sharpe_ratio", description="Metric to optimize")

    # Parameter ranges for optimization
    ma_fast_range: List[int] = Field(
        default=[5, 20], description="Range for fast MA [min, max]"
    )
    ma_slow_range: List[int] = Field(
        default=[20, 50], description="Range for slow MA [min, max]"
    )

    @field_validator("ma_fast_range", "ma_slow_range")
    @classmethod
    def validate_ranges(cls, v: List[int]) -> List[int]:
        """Ensure range has exactly 2 values [min, max]"""
        if len(v) != 2:
            raise ValueError(
                f"Range must have exactly 2 values [min, max], got {len(v)} values."
            )
        if v[0] >= v[1]:
            raise ValueError(
                f"Range minimum ({v[0]}) must be less than maximum ({v[1]})."
            )
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "method": "genetic",
                    "max_iterations": 100,
                    "optimization_metric": "sharpe_ratio",
                    "ma_fast_range": [5, 20],
                    "ma_slow_range": [20, 50],
                }
            ]
        }


class ApplicationConfig(BaseModel):
    """Main application configuration"""

    exchange: ExchangeConfig
    strategy: StrategyConfig
    backtest: BacktestConfig
    optimization: Optional[OptimizationConfig] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "exchange": {
                        "name": "binance",
                        "api_key": "your_key",
                        "api_secret": "your_secret",
                        "testnet": True,
                    },
                    "strategy": {
                        "name": "MA Crossover",
                        "timeframe": "1h",
                        "ma_fast": 10,
                        "ma_slow": 30,
                    },
                    "backtest": {
                        "start_date": "2023-01-01T00:00:00",
                        "end_date": "2024-01-01T00:00:00",
                        "initial_capital": 10000,
                    },
                }
            ]
        }
