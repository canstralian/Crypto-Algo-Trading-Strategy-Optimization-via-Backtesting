"""FastAPI main application."""

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models.schemas import (
    BacktestRequest,
    BacktestResponse,
    DataFetchRequest,
    ErrorResponse,
    HealthResponse,
    StrategyListResponse,
)
from ..core.backtester import Backtester
from ..core.risk_manager import RiskManager
from ..data.fetcher import DataFetcher
from ..data.preprocessor import DataPreprocessor
from ..strategies import (
    MovingAverageCrossover,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
)
from ..utils.config import get_settings
from ..utils.exceptions import TradingPlatformError
from ..utils.logger import setup_logging, get_logger
from ..utils.validators import validate_date

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Trading Platform API",
    description="Production-grade cryptocurrency algorithmic trading and backtesting platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TradingPlatformError)
async def trading_platform_error_handler(request: Any, exc: TradingPlatformError) -> JSONResponse:
    """Handle custom trading platform errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error=str(exc),
            detail=str(exc.details) if exc.details else None,
            timestamp=datetime.now(),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Any, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else None,
            timestamp=datetime.now(),
        ).model_dump(),
    )


@app.get("/", response_model=dict)
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "Crypto Trading Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
    )


@app.get("/strategies", response_model=StrategyListResponse)
async def list_strategies() -> StrategyListResponse:
    """List available trading strategies."""
    strategies = [
        {
            "name": "ma_crossover",
            "description": "Moving Average Crossover Strategy",
            "params": {"short_period": 10, "long_period": 30, "ma_type": "sma"},
        },
        {
            "name": "rsi",
            "description": "RSI (Relative Strength Index) Strategy",
            "params": {"period": 14, "overbought": 70, "oversold": 30},
        },
        {
            "name": "macd",
            "description": "MACD Strategy",
            "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
        },
        {
            "name": "bollinger_bands",
            "description": "Bollinger Bands Strategy",
            "params": {"period": 20, "std_dev": 2.0, "use_breakout": False},
        },
    ]

    return StrategyListResponse(strategies=strategies)


@app.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """Run a backtest with specified parameters."""
    try:
        logger.info(f"Starting backtest: {request.strategy} on {request.symbol}")

        # Parse dates
        start_date = validate_date(request.start_date)
        end_date = validate_date(request.end_date)

        # Fetch data
        fetcher = DataFetcher(sandbox=True)
        data = fetcher.fetch_ohlcv_range(
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=start_date,
            end_date=end_date,
        )

        # Add technical indicators
        preprocessor = DataPreprocessor()
        data = preprocessor.add_technical_indicators(data)
        data = preprocessor.clean_data(data)

        # Create strategy
        strategy = _create_strategy(request.strategy, request.strategy_params)

        # Create backtester
        backtester = Backtester(
            strategy=strategy,
            initial_capital=request.initial_capital,
            commission=request.commission,
            slippage=request.slippage,
        )

        # Run backtest
        results = backtester.run(
            data=data,
            symbol=request.symbol,
            position_sizing=request.position_sizing,
        )

        logger.info(
            f"Backtest complete: {results['total_return']:.2f}% return, "
            f"{results['metrics']['total_trades']} trades"
        )

        return BacktestResponse(
            strategy=results["strategy"],
            symbol=results["symbol"],
            initial_capital=results["initial_capital"],
            final_equity=results["final_equity"],
            total_return=results["total_return"],
            metrics=results["metrics"],
            config=results["config"],
            total_trades=results["metrics"]["total_trades"],
        )

    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest failed: {str(e)}",
        )


@app.post("/data/fetch")
async def fetch_data(request: DataFetchRequest) -> dict:
    """Fetch market data."""
    try:
        fetcher = DataFetcher(sandbox=True)

        if request.start_date and request.end_date:
            start_date = validate_date(request.start_date)
            end_date = validate_date(request.end_date)

            data = fetcher.fetch_ohlcv_range(
                symbol=request.symbol,
                timeframe=request.timeframe,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            data = fetcher.fetch_ohlcv(
                symbol=request.symbol,
                timeframe=request.timeframe,
                limit=request.limit,
            )

        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "rows": len(data),
            "data": data.reset_index().to_dict(orient="records")[:100],  # Limit response size
        }

    except Exception as e:
        logger.error(f"Data fetch failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data fetch failed: {str(e)}",
        )


def _create_strategy(name: str, params: dict[str, Any]) -> Any:
    """Create strategy instance from name and parameters."""
    strategies = {
        "ma_crossover": MovingAverageCrossover,
        "rsi": RSIStrategy,
        "macd": MACDStrategy,
        "bollinger_bands": BollingerBandsStrategy,
    }

    strategy_class = strategies.get(name)
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {name}")

    return strategy_class(**params) if params else strategy_class()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
