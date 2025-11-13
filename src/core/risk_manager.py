"""Risk management module."""

from typing import Optional

from .order import Order, OrderSide
from .portfolio import Portfolio
from ..utils.config import load_config
from ..utils.exceptions import RiskManagementError
from ..utils.logger import LoggerMixin


class RiskManager(LoggerMixin):
    """Risk management system for position sizing and risk controls."""

    def __init__(
        self,
        max_position_size: float = 0.1,
        max_portfolio_risk: float = 0.02,
        stop_loss_pct: float = 0.02,
        take_profit_pct: float = 0.05,
        max_open_positions: int = 5,
    ) -> None:
        """Initialize risk manager.

        Args:
            max_position_size: Maximum position size as % of portfolio (0-1)
            max_portfolio_risk: Maximum risk per trade as % of portfolio (0-1)
            stop_loss_pct: Stop loss percentage (0-1)
            take_profit_pct: Take profit percentage (0-1)
            max_open_positions: Maximum number of open positions
        """
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_open_positions = max_open_positions

        self.logger.info(
            f"Initialized risk manager: max_position={max_position_size*100}%, "
            f"max_risk={max_portfolio_risk*100}%, stop_loss={stop_loss_pct*100}%"
        )

    @classmethod
    def from_config(cls, config_path: str = "config/config.yaml") -> "RiskManager":
        """Create risk manager from config file.

        Args:
            config_path: Path to config file

        Returns:
            RiskManager instance
        """
        config = load_config(config_path)
        risk_config = config.get("risk_management", {})

        return cls(
            max_position_size=risk_config.get("max_position_size", 0.1),
            max_portfolio_risk=risk_config.get("max_portfolio_risk", 0.02),
            stop_loss_pct=risk_config.get("stop_loss_percentage", 0.02),
            take_profit_pct=risk_config.get("take_profit_percentage", 0.05),
            max_open_positions=risk_config.get("max_open_positions", 5),
        )

    def calculate_position_size(
        self,
        portfolio: Portfolio,
        current_price: float,
        risk_per_trade: Optional[float] = None,
    ) -> float:
        """Calculate position size based on risk management rules.

        Args:
            portfolio: Portfolio instance
            current_price: Current price of the asset
            risk_per_trade: Optional custom risk per trade (0-1)

        Returns:
            Position size in units

        Raises:
            RiskManagementError: If calculation fails
        """
        if current_price <= 0:
            raise RiskManagementError("Invalid price for position sizing")

        # Use default risk if not specified
        risk_pct = risk_per_trade or self.max_portfolio_risk

        # Calculate maximum position value based on position size limit
        max_position_value = portfolio.total_equity * self.max_position_size

        # Calculate position size based on risk
        risk_amount = portfolio.total_equity * risk_pct
        stop_loss_price = current_price * (1 - self.stop_loss_pct)
        risk_per_unit = current_price - stop_loss_price

        if risk_per_unit <= 0:
            raise RiskManagementError("Invalid risk calculation")

        # Calculate position size
        position_size_by_risk = risk_amount / risk_per_unit
        position_size_by_limit = max_position_value / current_price

        # Use the smaller of the two
        position_size = min(position_size_by_risk, position_size_by_limit)

        # Ensure we have enough cash
        max_affordable = portfolio.cash / current_price * 0.95  # Leave 5% buffer
        position_size = min(position_size, max_affordable)

        self.logger.debug(
            f"Calculated position size: {position_size:.4f} units @ ${current_price:.2f}"
        )

        return position_size

    def validate_order(self, order: Order, portfolio: Portfolio) -> bool:
        """Validate order against risk management rules.

        Args:
            order: Order to validate
            portfolio: Portfolio instance

        Returns:
            True if order passes validation

        Raises:
            RiskManagementError: If order violates risk rules
        """
        # Check max open positions for buy orders
        if order.is_buy:
            if len(portfolio.positions) >= self.max_open_positions:
                raise RiskManagementError(
                    f"Maximum open positions ({self.max_open_positions}) reached"
                )

        # Validate sell orders have position
        if order.is_sell:
            position = portfolio.get_position(order.symbol)
            if position is None or position.quantity < order.quantity:
                raise RiskManagementError(
                    f"Insufficient position in {order.symbol} to sell"
                )

        # Check position size limits for buy orders
        if order.is_buy:
            price = order.price or order.filled_price
            if price:
                position_value = price * order.quantity
                max_position_value = portfolio.total_equity * self.max_position_size

                if position_value > max_position_value:
                    raise RiskManagementError(
                        f"Position size exceeds maximum limit. "
                        f"Value: ${position_value:.2f}, Limit: ${max_position_value:.2f}"
                    )

        # Check available cash for buy orders
        if order.is_buy:
            price = order.price or order.filled_price
            if price:
                required_cash = price * order.quantity * (1 + portfolio.commission_rate)
                if required_cash > portfolio.cash:
                    raise RiskManagementError(
                        f"Insufficient cash. Required: ${required_cash:.2f}, "
                        f"Available: ${portfolio.cash:.2f}"
                    )

        return True

    def calculate_stop_loss(self, entry_price: float, side: OrderSide) -> float:
        """Calculate stop loss price.

        Args:
            entry_price: Entry price
            side: Order side (buy/sell)

        Returns:
            Stop loss price
        """
        if side == OrderSide.BUY:
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)

    def calculate_take_profit(self, entry_price: float, side: OrderSide) -> float:
        """Calculate take profit price.

        Args:
            entry_price: Entry price
            side: Order side (buy/sell)

        Returns:
            Take profit price
        """
        if side == OrderSide.BUY:
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)

    def should_close_position(
        self,
        entry_price: float,
        current_price: float,
        side: OrderSide,
    ) -> tuple[bool, str]:
        """Check if position should be closed based on risk management.

        Args:
            entry_price: Position entry price
            current_price: Current market price
            side: Position side

        Returns:
            Tuple of (should_close, reason)
        """
        stop_loss = self.calculate_stop_loss(entry_price, side)
        take_profit = self.calculate_take_profit(entry_price, side)

        if side == OrderSide.BUY:
            if current_price <= stop_loss:
                return True, "stop_loss"
            if current_price >= take_profit:
                return True, "take_profit"
        else:
            if current_price >= stop_loss:
                return True, "stop_loss"
            if current_price <= take_profit:
                return True, "take_profit"

        return False, ""

    def get_risk_metrics(self, portfolio: Portfolio) -> dict:
        """Get current risk metrics.

        Args:
            portfolio: Portfolio instance

        Returns:
            Dictionary of risk metrics
        """
        total_exposure = sum(
            p.quantity * p.average_price for p in portfolio.positions.values()
        )

        return {
            "total_exposure": total_exposure,
            "exposure_ratio": total_exposure / portfolio.total_equity if portfolio.total_equity > 0 else 0,
            "cash_ratio": portfolio.cash / portfolio.total_equity if portfolio.total_equity > 0 else 0,
            "open_positions": len(portfolio.positions),
            "max_position_size": self.max_position_size,
            "max_open_positions": self.max_open_positions,
            "positions_used": len(portfolio.positions) / self.max_open_positions,
        }
