#!/usr/bin/env python3
"""Script to run backtests from command line."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.backtester import Backtester
from src.data.fetcher import DataFetcher
from src.data.preprocessor import DataPreprocessor
from src.data.storage import DataStorage
from src.strategies import (
    MovingAverageCrossover,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
)
from src.utils.logger import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run cryptocurrency trading strategy backtest"
    )

    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        choices=["ma_crossover", "rsi", "macd", "bollinger_bands"],
        help="Trading strategy to backtest",
    )

    parser.add_argument(
        "--symbol",
        type=str,
        default="BTC/USDT",
        help="Trading symbol (e.g., BTC/USDT)",
    )

    parser.add_argument(
        "--timeframe",
        type=str,
        default="1h",
        help="Timeframe (1m, 5m, 1h, 1d, etc.)",
    )

    parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--capital",
        type=float,
        default=10000.0,
        help="Initial capital",
    )

    parser.add_argument(
        "--commission",
        type=float,
        default=0.001,
        help="Commission rate",
    )

    parser.add_argument(
        "--save",
        type=str,
        help="Save results to file (provide filename)",
    )

    return parser.parse_args()


def create_strategy(name: str) -> any:
    """Create strategy instance from name."""
    strategies = {
        "ma_crossover": MovingAverageCrossover(),
        "rsi": RSIStrategy(),
        "macd": MACDStrategy(),
        "bollinger_bands": BollingerBandsStrategy(),
    }
    return strategies[name]


def main() -> None:
    """Main function."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)

    # Parse arguments
    args = parse_args()

    logger.info(f"Starting backtest: {args.strategy} on {args.symbol}")
    logger.info(f"Period: {args.start} to {args.end}")

    try:
        # Parse dates
        start_date = datetime.fromisoformat(args.start)
        end_date = datetime.fromisoformat(args.end)

        # Fetch data
        logger.info("Fetching market data...")
        fetcher = DataFetcher(sandbox=True)
        data = fetcher.fetch_ohlcv_range(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=start_date,
            end_date=end_date,
        )

        logger.info(f"Fetched {len(data)} candles")

        # Preprocess data
        logger.info("Preprocessing data...")
        preprocessor = DataPreprocessor()
        data = preprocessor.add_technical_indicators(data)
        data = preprocessor.clean_data(data)

        # Create strategy
        logger.info(f"Creating {args.strategy} strategy...")
        strategy = create_strategy(args.strategy)

        # Create backtester
        backtester = Backtester(
            strategy=strategy,
            initial_capital=args.capital,
            commission=args.commission,
        )

        # Run backtest
        logger.info("Running backtest...")
        results = backtester.run(data, symbol=args.symbol)

        # Print results
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Strategy: {results['strategy']}")
        print(f"Symbol: {results['symbol']}")
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Equity: ${results['final_equity']:,.2f}")
        print(f"Total Return: {results['total_return']:.2f}%")
        print(f"Total P&L: ${results['total_pnl']:,.2f}")
        print("\nPerformance Metrics:")
        print(f"  Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
        print(f"  Sortino Ratio: {results['metrics']['sortino_ratio']:.2f}")
        print(f"  Max Drawdown: {results['metrics']['max_drawdown']:.2f}%")
        print(f"  Calmar Ratio: {results['metrics']['calmar_ratio']:.2f}")
        print("\nTrade Statistics:")
        print(f"  Total Trades: {results['metrics']['total_trades']}")
        print(f"  Winning Trades: {results['metrics']['winning_trades']}")
        print(f"  Losing Trades: {results['metrics']['losing_trades']}")
        print(f"  Win Rate: {results['metrics']['win_rate']:.2f}%")
        print(f"  Total Commission: ${results['metrics']['total_commission']:.2f}")
        print("="*60 + "\n")

        # Save results if requested
        if args.save:
            logger.info(f"Saving results to {args.save}...")
            storage = DataStorage()
            storage.save_backtest_results(results, args.save)
            logger.info("Results saved successfully")

    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
