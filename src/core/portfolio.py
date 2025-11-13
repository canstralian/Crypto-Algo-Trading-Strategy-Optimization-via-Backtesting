"""Portfolio management and tracking."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .order import Order, OrderSide
from ..utils.exceptions import PortfolioError
from ..utils.logger import LoggerMixin


@dataclass
class Position:
    """Represents a position in a trading symbol."""

    symbol: str
    quantity: float = 0.0
    average_price: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_cost: float = 0.0

    @property
    def market_value(self) -> float:
        """Calculate current market value."""
        return self.quantity * self.average_price

    def update_unrealized_pnl(self, current_price: float) -> None:
        """Update unrealized P&L based on current price.

        Args:
            current_price: Current market price
        """
        if self.quantity > 0:
            self.unrealized_pnl = (current_price - self.average_price) * self.quantity


class Portfolio(LoggerMixin):
    """Portfolio management system."""

    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,
    ) -> None:
        """Initialize portfolio.

        Args:
            initial_capital: Starting capital
            commission_rate: Commission rate per trade
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate

        self.positions: dict[str, Position] = {}
        self.orders: list[Order] = []
        self.equity_curve: list[dict] = []

        self.total_commission = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0

        self.logger.info(f"Initialized portfolio with ${initial_capital:,.2f}")

    def process_order(self, order: Order, current_price: float) -> bool:
        """Process and execute an order.

        Args:
            order: Order to process
            current_price: Current market price

        Returns:
            True if order was executed successfully

        Raises:
            PortfolioError: If order execution fails
        """
        # Calculate execution price
        execution_price = order.price if order.price else current_price

        # Calculate commission
        commission = execution_price * order.quantity * self.commission_rate

        # Check if we have enough cash for buy orders
        if order.is_buy:
            total_cost = (execution_price * order.quantity) + commission
            if total_cost > self.cash:
                raise PortfolioError(
                    f"Insufficient funds. Required: ${total_cost:,.2f}, Available: ${self.cash:,.2f}"
                )

        # Fill the order
        order.fill(filled_price=execution_price, commission=commission)

        # Update portfolio
        if order.is_buy:
            self._process_buy(order)
        else:
            self._process_sell(order)

        # Track order
        self.orders.append(order)
        self.total_commission += commission
        self.total_trades += 1

        self.logger.info(
            f"Executed {order.side.value.upper()} {order.quantity} {order.symbol} "
            f"@ ${execution_price:,.2f}"
        )

        return True

    def _process_buy(self, order: Order) -> None:
        """Process a buy order.

        Args:
            order: Filled buy order
        """
        if order.filled_price is None:
            raise PortfolioError("Order not filled")

        symbol = order.symbol

        # Create or update position
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)

        position = self.positions[symbol]

        # Update average price
        total_cost = position.average_price * position.quantity
        total_cost += order.filled_price * order.filled_quantity
        position.quantity += order.filled_quantity
        position.average_price = total_cost / position.quantity
        position.total_cost += order.total_cost

        # Update cash
        self.cash -= order.total_cost

    def _process_sell(self, order: Order) -> None:
        """Process a sell order.

        Args:
            order: Filled sell order
        """
        if order.filled_price is None:
            raise PortfolioError("Order not filled")

        symbol = order.symbol

        if symbol not in self.positions:
            raise PortfolioError(f"No position in {symbol} to sell")

        position = self.positions[symbol]

        if position.quantity < order.filled_quantity:
            raise PortfolioError(
                f"Insufficient position. Have: {position.quantity}, Want to sell: {order.filled_quantity}"
            )

        # Calculate P&L
        pnl = (order.filled_price - position.average_price) * order.filled_quantity
        position.realized_pnl += pnl

        # Update trade statistics
        if pnl > 0:
            self.winning_trades += 1
        elif pnl < 0:
            self.losing_trades += 1

        # Update position
        position.quantity -= order.filled_quantity

        # Remove position if fully closed
        if position.quantity == 0:
            del self.positions[symbol]

        # Update cash
        self.cash += order.total_value - order.commission

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Position or None if no position exists
        """
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        """Check if portfolio has a position in symbol.

        Args:
            symbol: Trading symbol

        Returns:
            True if position exists
        """
        return symbol in self.positions and self.positions[symbol].quantity > 0

    def update_equity(self, timestamp: datetime, prices: dict[str, float]) -> None:
        """Update portfolio equity curve.

        Args:
            timestamp: Current timestamp
            prices: Current prices for all symbols
        """
        # Update unrealized P&L for all positions
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.update_unrealized_pnl(prices[symbol])

        # Calculate total equity
        total_equity = self.cash
        total_unrealized_pnl = 0.0
        total_realized_pnl = 0.0

        for position in self.positions.values():
            if position.symbol in prices:
                market_value = position.quantity * prices[position.symbol]
                total_equity += market_value
                total_unrealized_pnl += position.unrealized_pnl
                total_realized_pnl += position.realized_pnl

        # Record equity point
        self.equity_curve.append(
            {
                "timestamp": timestamp,
                "equity": total_equity,
                "cash": self.cash,
                "realized_pnl": total_realized_pnl,
                "unrealized_pnl": total_unrealized_pnl,
                "total_pnl": total_realized_pnl + total_unrealized_pnl,
            }
        )

    @property
    def total_equity(self) -> float:
        """Get current total equity."""
        if self.equity_curve:
            return self.equity_curve[-1]["equity"]
        return self.cash

    @property
    def total_pnl(self) -> float:
        """Get total profit/loss."""
        return self.total_equity - self.initial_capital

    @property
    def total_return(self) -> float:
        """Get total return percentage."""
        return (self.total_equity / self.initial_capital - 1) * 100

    @property
    def win_rate(self) -> float:
        """Get win rate percentage."""
        total_closed_trades = self.winning_trades + self.losing_trades
        if total_closed_trades == 0:
            return 0.0
        return (self.winning_trades / total_closed_trades) * 100

    def get_summary(self) -> dict:
        """Get portfolio summary.

        Returns:
            Dictionary with portfolio metrics
        """
        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "total_equity": self.total_equity,
            "total_pnl": self.total_pnl,
            "total_return": self.total_return,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "total_commission": self.total_commission,
            "open_positions": len(self.positions),
            "positions": [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "average_price": p.average_price,
                    "realized_pnl": p.realized_pnl,
                    "unrealized_pnl": p.unrealized_pnl,
                }
                for p in self.positions.values()
            ],
        }
