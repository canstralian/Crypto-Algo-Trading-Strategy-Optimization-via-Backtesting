"""Advanced backtesting engine with realistic market simulation."""

from datetime import datetime
from typing import Any, Optional

import pandas as pd

from .order import Order, OrderSide, OrderType
from .portfolio import Portfolio
from .risk_manager import RiskManager
from .strategy import Strategy, Signal
from ..analysis.metrics import PerformanceMetrics
from ..utils.config import load_config
from ..utils.exceptions import BacktestError
from ..utils.logger import LoggerMixin


class Backtester(LoggerMixin):
    """Advanced backtesting engine."""

    def __init__(
        self,
        strategy: Strategy,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005,
        risk_manager: Optional[RiskManager] = None,
    ) -> None:
        """Initialize backtester.

        Args:
            strategy: Trading strategy to backtest
            initial_capital: Starting capital
            commission: Commission rate per trade
            slippage: Slippage rate
            risk_manager: Optional risk manager
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        self.portfolio = Portfolio(
            initial_capital=initial_capital, commission_rate=commission
        )
        self.risk_manager = risk_manager or RiskManager()

        self.trades: list[dict] = []
        self.signals_history: list[dict] = []

        self.logger.info(
            f"Initialized backtester for {strategy.name} with "
            f"${initial_capital:,.2f} capital"
        )

    @classmethod
    def from_config(
        cls, strategy: Strategy, config_path: str = "config/config.yaml"
    ) -> "Backtester":
        """Create backtester from config file.

        Args:
            strategy: Trading strategy
            config_path: Path to config file

        Returns:
            Backtester instance
        """
        config = load_config(config_path)
        backtest_config = config.get("backtesting", {})

        return cls(
            strategy=strategy,
            initial_capital=backtest_config.get("initial_capital", 10000.0),
            commission=backtest_config.get("commission", 0.001),
            slippage=backtest_config.get("slippage", 0.0005),
            risk_manager=RiskManager.from_config(config_path),
        )

    def run(
        self,
        data: pd.DataFrame,
        symbol: str = "BTC/USDT",
        position_sizing: str = "fixed",
    ) -> dict[str, Any]:
        """Run backtest.

        Args:
            data: Historical OHLCV data
            symbol: Trading symbol
            position_sizing: Position sizing method ('fixed', 'risk_based')

        Returns:
            Dictionary with backtest results

        Raises:
            BacktestError: If backtest fails
        """
        try:
            self.logger.info(f"Starting backtest for {symbol} with {len(data)} bars")

            # Validate data
            self.strategy.validate_data(data)

            # Calculate indicators and generate signals
            data = self.strategy.calculate_indicators(data)
            data = self.generate_signals(data)

            # Run simulation
            self._simulate(data, symbol, position_sizing)

            # Calculate performance metrics
            metrics = self._calculate_metrics()

            # Compile results
            results = {
                "strategy": self.strategy.name,
                "symbol": symbol,
                "initial_capital": self.initial_capital,
                "final_equity": self.portfolio.total_equity,
                "total_return": self.portfolio.total_return,
                "total_pnl": self.portfolio.total_pnl,
                "metrics": metrics,
                "portfolio_summary": self.portfolio.get_summary(),
                "trades": self.trades,
                "equity_curve": self.portfolio.equity_curve,
                "config": {
                    "commission": self.commission,
                    "slippage": self.slippage,
                    "initial_capital": self.initial_capital,
                    "position_sizing": position_sizing,
                },
            }

            self.logger.info(
                f"Backtest complete. Return: {self.portfolio.total_return:.2f}%, "
                f"Trades: {self.portfolio.total_trades}"
            )

            return results

        except Exception as e:
            raise BacktestError(f"Backtest failed: {e}")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals.

        Args:
            data: DataFrame with indicators

        Returns:
            DataFrame with signals
        """
        data = self.strategy.generate_signals(data)

        # Record signals for analysis
        for idx in data.index:
            if "signal" in data.columns:
                signal_value = data.loc[idx, "signal"]
                if signal_value != 0:
                    self.signals_history.append(
                        {
                            "timestamp": idx,
                            "signal": "BUY" if signal_value > 0 else "SELL",
                            "price": data.loc[idx, "close"],
                        }
                    )

        return data

    def _simulate(
        self, data: pd.DataFrame, symbol: str, position_sizing: str
    ) -> None:
        """Simulate trading based on signals.

        Args:
            data: DataFrame with signals
            symbol: Trading symbol
            position_sizing: Position sizing method
        """
        for i in range(len(data)):
            timestamp = data.index[i]
            row = data.iloc[i]

            # Get current signal
            signal = self.strategy.get_signal_at(data, i)

            # Get price with slippage
            close_price = row["close"]
            buy_price = close_price * (1 + self.slippage)
            sell_price = close_price * (1 - self.slippage)

            # Check risk management for existing positions
            if self.portfolio.has_position(symbol):
                position = self.portfolio.get_position(symbol)
                if position:
                    should_close, reason = self.risk_manager.should_close_position(
                        entry_price=position.average_price,
                        current_price=close_price,
                        side=OrderSide.BUY,
                    )

                    if should_close:
                        self._execute_sell(
                            symbol, position.quantity, sell_price, timestamp, reason
                        )

            # Process signals
            if signal == Signal.BUY and not self.portfolio.has_position(symbol):
                # Calculate position size
                if position_sizing == "risk_based":
                    quantity = self.risk_manager.calculate_position_size(
                        self.portfolio, buy_price
                    )
                else:
                    # Fixed size: use 95% of available cash
                    quantity = (self.portfolio.cash * 0.95) / buy_price

                if quantity > 0:
                    self._execute_buy(symbol, quantity, buy_price, timestamp)

            elif signal == Signal.SELL and self.portfolio.has_position(symbol):
                position = self.portfolio.get_position(symbol)
                if position:
                    self._execute_sell(
                        symbol, position.quantity, sell_price, timestamp, "signal"
                    )

            # Update equity curve
            self.portfolio.update_equity(timestamp, {symbol: close_price})

    def _execute_buy(
        self, symbol: str, quantity: float, price: float, timestamp: datetime
    ) -> None:
        """Execute buy order.

        Args:
            symbol: Trading symbol
            quantity: Quantity to buy
            price: Execution price
            timestamp: Order timestamp
        """
        try:
            order = Order(
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=quantity,
                timestamp=timestamp,
            )

            # Validate with risk manager
            self.risk_manager.validate_order(order, self.portfolio)

            # Execute order
            self.portfolio.process_order(order, price)

            # Record trade
            self.trades.append(
                {
                    "timestamp": timestamp,
                    "type": "BUY",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": price,
                    "total_cost": order.total_cost,
                    "commission": order.commission,
                }
            )

        except Exception as e:
            self.logger.warning(f"Failed to execute buy order: {e}")

    def _execute_sell(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: datetime,
        reason: str = "signal",
    ) -> None:
        """Execute sell order.

        Args:
            symbol: Trading symbol
            quantity: Quantity to sell
            price: Execution price
            timestamp: Order timestamp
            reason: Reason for selling
        """
        try:
            order = Order(
                symbol=symbol,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                quantity=quantity,
                timestamp=timestamp,
            )

            # Execute order
            self.portfolio.process_order(order, price)

            # Record trade
            self.trades.append(
                {
                    "timestamp": timestamp,
                    "type": "SELL",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": price,
                    "total_value": order.total_value,
                    "commission": order.commission,
                    "reason": reason,
                }
            )

        except Exception as e:
            self.logger.warning(f"Failed to execute sell order: {e}")

    def _calculate_metrics(self) -> dict[str, Any]:
        """Calculate performance metrics.

        Returns:
            Dictionary of performance metrics
        """
        if not self.portfolio.equity_curve:
            return {}

        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(self.portfolio.equity_curve)
        equity_df.set_index("timestamp", inplace=True)

        # Calculate metrics using PerformanceMetrics
        metrics_calculator = PerformanceMetrics(equity_df["equity"])

        return {
            "total_return": metrics_calculator.total_return(),
            "annualized_return": metrics_calculator.annualized_return(),
            "sharpe_ratio": metrics_calculator.sharpe_ratio(),
            "sortino_ratio": metrics_calculator.sortino_ratio(),
            "max_drawdown": metrics_calculator.max_drawdown(),
            "calmar_ratio": metrics_calculator.calmar_ratio(),
            "win_rate": self.portfolio.win_rate,
            "total_trades": self.portfolio.total_trades,
            "winning_trades": self.portfolio.winning_trades,
            "losing_trades": self.portfolio.losing_trades,
            "total_commission": self.portfolio.total_commission,
        }

    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as DataFrame.

        Returns:
            DataFrame with all trades
        """
        if not self.trades:
            return pd.DataFrame()

        df = pd.DataFrame(self.trades)
        if "timestamp" in df.columns:
            df.set_index("timestamp", inplace=True)

        return df
