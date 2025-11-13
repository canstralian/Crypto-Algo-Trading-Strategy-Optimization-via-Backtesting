"""Order management and execution."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from ..utils.exceptions import OrderError, ValidationError
from ..utils.validators import validate_positive_number


class OrderSide(Enum):
    """Order side enumeration."""

    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration."""

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(Enum):
    """Order status enumeration."""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order."""

    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    timestamp: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    filled_quantity: float = 0.0
    commission: float = 0.0
    order_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate order after initialization."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

        # Validate quantity
        try:
            validate_positive_number(self.quantity, "Quantity")
        except ValidationError as e:
            raise OrderError(str(e))

        # Validate price for limit orders
        if self.order_type == OrderType.LIMIT and self.price is None:
            raise OrderError("Limit orders require a price")

        # Validate stop price for stop orders
        if self.order_type in [OrderType.STOP_LOSS, OrderType.TAKE_PROFIT]:
            if self.stop_price is None:
                raise OrderError(f"{self.order_type.value} orders require a stop price")

    def fill(
        self, filled_price: float, filled_quantity: Optional[float] = None, commission: float = 0.0
    ) -> None:
        """Fill the order.

        Args:
            filled_price: Price at which order was filled
            filled_quantity: Quantity filled (defaults to order quantity)
            commission: Commission charged
        """
        self.filled_price = filled_price
        self.filled_quantity = filled_quantity or self.quantity
        self.commission = commission
        self.status = OrderStatus.FILLED

    def cancel(self) -> None:
        """Cancel the order."""
        if self.status == OrderStatus.FILLED:
            raise OrderError("Cannot cancel a filled order")
        self.status = OrderStatus.CANCELLED

    def reject(self, reason: str = "") -> None:
        """Reject the order.

        Args:
            reason: Rejection reason
        """
        self.status = OrderStatus.REJECTED

    @property
    def is_filled(self) -> bool:
        """Check if order is filled."""
        return self.status == OrderStatus.FILLED

    @property
    def is_buy(self) -> bool:
        """Check if order is a buy order."""
        return self.side == OrderSide.BUY

    @property
    def is_sell(self) -> bool:
        """Check if order is a sell order."""
        return self.side == OrderSide.SELL

    @property
    def total_cost(self) -> float:
        """Calculate total cost including commission."""
        if not self.is_filled or self.filled_price is None:
            return 0.0
        return (self.filled_price * self.filled_quantity) + self.commission

    @property
    def total_value(self) -> float:
        """Calculate total value (excluding commission)."""
        if not self.is_filled or self.filled_price is None:
            return 0.0
        return self.filled_price * self.filled_quantity

    def to_dict(self) -> dict:
        """Convert order to dictionary."""
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "stop_price": self.stop_price,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status.value,
            "filled_price": self.filled_price,
            "filled_quantity": self.filled_quantity,
            "commission": self.commission,
            "total_cost": self.total_cost,
        }

    def __repr__(self) -> str:
        """String representation of order."""
        return (
            f"Order({self.side.value.upper()} {self.quantity} {self.symbol} "
            f"@ {self.price or 'MARKET'}, status={self.status.value})"
        )
