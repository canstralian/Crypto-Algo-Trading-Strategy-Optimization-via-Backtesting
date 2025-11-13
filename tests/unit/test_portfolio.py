"""Unit tests for portfolio management."""

import pytest
from datetime import datetime

from src.core.portfolio import Portfolio, Position
from src.core.order import Order, OrderSide, OrderType
from src.utils.exceptions import PortfolioError


class TestPosition:
    """Tests for Position class."""

    def test_position_initialization(self):
        """Test position initialization."""
        position = Position(symbol="BTC/USDT", quantity=1.0, average_price=50000)
        assert position.symbol == "BTC/USDT"
        assert position.quantity == 1.0
        assert position.average_price == 50000

    def test_market_value_calculation(self):
        """Test market value calculation."""
        position = Position(symbol="BTC/USDT", quantity=2.0, average_price=50000)
        assert position.market_value == 100000

    def test_update_unrealized_pnl(self):
        """Test unrealized P&L update."""
        position = Position(symbol="BTC/USDT", quantity=1.0, average_price=50000)
        position.update_unrealized_pnl(52000)
        assert position.unrealized_pnl == 2000


class TestPortfolio:
    """Tests for Portfolio class."""

    def test_portfolio_initialization(self):
        """Test portfolio initialization."""
        portfolio = Portfolio(initial_capital=10000)
        assert portfolio.initial_capital == 10000
        assert portfolio.cash == 10000
        assert len(portfolio.positions) == 0

    def test_process_buy_order(self):
        """Test processing buy order."""
        portfolio = Portfolio(initial_capital=10000, commission_rate=0.001)
        order = Order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.1,
        )

        portfolio.process_order(order, current_price=50000)

        assert portfolio.has_position("BTC/USDT")
        assert portfolio.cash < 10000
        assert portfolio.total_trades == 1

    def test_process_sell_order(self):
        """Test processing sell order."""
        portfolio = Portfolio(initial_capital=10000)

        # First buy
        buy_order = Order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.1,
        )
        portfolio.process_order(buy_order, current_price=50000)

        # Then sell
        sell_order = Order(
            symbol="BTC/USDT",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=0.1,
        )
        portfolio.process_order(sell_order, current_price=52000)

        assert not portfolio.has_position("BTC/USDT")
        assert portfolio.total_trades == 2

    def test_insufficient_funds_raises_error(self):
        """Test that insufficient funds raises error."""
        portfolio = Portfolio(initial_capital=1000)
        order = Order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=1.0,
        )

        with pytest.raises(PortfolioError, match="Insufficient funds"):
            portfolio.process_order(order, current_price=50000)

    def test_sell_without_position_raises_error(self):
        """Test that selling without position raises error."""
        portfolio = Portfolio(initial_capital=10000)
        order = Order(
            symbol="BTC/USDT",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=0.1,
        )

        with pytest.raises(PortfolioError, match="No position"):
            portfolio.process_order(order, current_price=50000)

    def test_win_rate_calculation(self):
        """Test win rate calculation."""
        portfolio = Portfolio(initial_capital=10000)

        # Winning trade
        buy1 = Order("BTC/USDT", OrderSide.BUY, OrderType.MARKET, 0.1)
        portfolio.process_order(buy1, 50000)
        sell1 = Order("BTC/USDT", OrderSide.SELL, OrderType.MARKET, 0.1)
        portfolio.process_order(sell1, 52000)

        # Losing trade
        buy2 = Order("BTC/USDT", OrderSide.BUY, OrderType.MARKET, 0.1)
        portfolio.process_order(buy2, 50000)
        sell2 = Order("BTC/USDT", OrderSide.SELL, OrderType.MARKET, 0.1)
        portfolio.process_order(sell2, 48000)

        assert portfolio.winning_trades == 1
        assert portfolio.losing_trades == 1
        assert portfolio.win_rate == 50.0
