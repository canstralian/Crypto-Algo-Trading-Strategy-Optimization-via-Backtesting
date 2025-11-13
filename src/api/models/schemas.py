"""Pydantic models for API request/response validation."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class BacktestRequest(BaseModel):
    """Backtest request model."""

    strategy: str = Field(..., description="Strategy name")
    symbol: str = Field(..., description="Trading symbol (e.g., BTC/USDT)")
    timeframe: str = Field(default="1h", description="Timeframe (1m, 5m, 1h, 1d, etc.)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(default=10000.0, gt=0, description="Initial capital")
    commission: float = Field(default=0.001, ge=0, le=0.1, description="Commission rate")
    slippage: float = Field(default=0.0005, ge=0, le=0.1, description="Slippage rate")
    strategy_params: dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")
    position_sizing: str = Field(default="fixed", description="Position sizing method")

    @field_validator("strategy")
    @classmethod
    def validate_strategy(cls, v: str) -> str:
        """Validate strategy name."""
        valid_strategies = ["ma_crossover", "rsi", "macd", "bollinger_bands"]
        if v.lower() not in valid_strategies:
            raise ValueError(f"Invalid strategy. Must be one of: {valid_strategies}")
        return v.lower()


class BacktestResponse(BaseModel):
    """Backtest response model."""

    strategy: str
    symbol: str
    initial_capital: float
    final_equity: float
    total_return: float
    metrics: dict[str, Any]
    config: dict[str, Any]
    total_trades: int


class DataFetchRequest(BaseModel):
    """Data fetch request model."""

    symbol: str = Field(..., description="Trading symbol")
    timeframe: str = Field(default="1h", description="Timeframe")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    limit: int = Field(default=1000, gt=0, le=5000, description="Number of candles")


class StrategyListResponse(BaseModel):
    """Strategy list response model."""

    strategies: list[dict[str, Any]]


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    timestamp: datetime
