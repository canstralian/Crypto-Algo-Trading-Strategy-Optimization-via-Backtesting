# User Guide

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting.git
cd Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup configuration:
```bash
cp config/config.example.yaml config/config.yaml
cp .env.example .env
# Edit config.yaml and .env as needed
```

### Running Your First Backtest

#### Command Line

```bash
python scripts/run_backtest.py \
  --strategy ma_crossover \
  --symbol BTC/USDT \
  --timeframe 1h \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --capital 10000
```

#### Using the API

1. Start the API server:
```bash
uvicorn src.api.main:app --reload
```

2. Run a backtest via API:
```bash
curl -X POST http://localhost:8000/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "rsi",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 10000
  }'
```

## Available Strategies

### 1. Moving Average Crossover

Generates buy signals when short MA crosses above long MA.

**Parameters:**
- `short_period`: Short MA period (default: 10)
- `long_period`: Long MA period (default: 30)
- `ma_type`: Type of MA - 'sma' or 'ema' (default: 'sma')

**Example:**
```python
from src.strategies import MovingAverageCrossover

strategy = MovingAverageCrossover(
    short_period=10,
    long_period=30,
    ma_type='ema'
)
```

### 2. RSI Strategy

Buys when RSI crosses above oversold, sells when crosses below overbought.

**Parameters:**
- `period`: RSI period (default: 14)
- `overbought`: Overbought threshold (default: 70)
- `oversold`: Oversold threshold (default: 30)

**Example:**
```python
from src.strategies import RSIStrategy

strategy = RSIStrategy(
    period=14,
    overbought=70,
    oversold=30
)
```

### 3. MACD Strategy

Buys when MACD crosses above signal line.

**Parameters:**
- `fast_period`: Fast EMA period (default: 12)
- `slow_period`: Slow EMA period (default: 26)
- `signal_period`: Signal line period (default: 9)

**Example:**
```python
from src.strategies import MACDStrategy

strategy = MACDStrategy(
    fast_period=12,
    slow_period=26,
    signal_period=9
)
```

### 4. Bollinger Bands Strategy

Mean reversion or breakout strategy using Bollinger Bands.

**Parameters:**
- `period`: Moving average period (default: 20)
- `std_dev`: Standard deviations (default: 2.0)
- `use_breakout`: Breakout vs mean reversion (default: False)

**Example:**
```python
from src.strategies import BollingerBandsStrategy

strategy = BollingerBandsStrategy(
    period=20,
    std_dev=2.0,
    use_breakout=False
)
```

## Configuration

### config.yaml

Main configuration file for the platform.

```yaml
backtesting:
  initial_capital: 10000.0
  commission: 0.001
  slippage: 0.0005

risk_management:
  max_position_size: 0.1
  stop_loss_percentage: 0.02
  take_profit_percentage: 0.05
```

### Environment Variables

Set in `.env` file:

```bash
ENVIRONMENT=development
LOG_LEVEL=INFO
API_PORT=8000
```

## Understanding Results

### Performance Metrics

- **Total Return**: Overall percentage return
- **Annualized Return**: Return normalized to per year
- **Sharpe Ratio**: Risk-adjusted return (>1 is good, >2 is excellent)
- **Sortino Ratio**: Like Sharpe but only considers downside risk
- **Max Drawdown**: Maximum peak-to-trough decline
- **Calmar Ratio**: Annualized return / max drawdown
- **Win Rate**: Percentage of profitable trades

### Example Results Interpretation

```
Total Return: 25.5%
Sharpe Ratio: 1.85
Max Drawdown: 8.2%
Win Rate: 62.5%
```

This indicates a profitable strategy with:
- Strong risk-adjusted returns (Sharpe > 1.5)
- Moderate drawdown (<10%)
- Consistent winning percentage (>60%)

## Advanced Usage

### Custom Strategy Development

Create your own strategy by extending the `Strategy` base class:

```python
from src.core.strategy import Strategy
import pandas as pd

class MyCustomStrategy(Strategy):
    def __init__(self, param1=10, param2=20):
        super().__init__(
            name="MyCustom",
            param1=param1,
            param2=param2
        )
        self.param1 = param1
        self.param2 = param2

    def calculate_indicators(self, data):
        # Add your indicators
        data = data.copy()
        data['my_indicator'] = ...
        return data

    def generate_signals(self, data):
        # Generate buy/sell signals
        data = data.copy()
        data['signal'] = 0
        # Your logic here
        return data
```

### Docker Deployment

```bash
# Build image
docker build -t crypto-trading-platform .

# Run container
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config:ro \
  crypto-trading-platform

# Or use docker-compose
docker-compose up -d
```

## Troubleshooting

### Common Issues

**Issue**: Data fetch fails
```
Solution: Check internet connection and exchange API status
```

**Issue**: Low test coverage warning
```
Solution: Run: pytest --cov=src --cov-report=html
```

**Issue**: API won't start
```
Solution: Check if port 8000 is already in use:
lsof -i :8000
```

## Best Practices

1. **Always backtest** before live trading
2. **Use proper position sizing** to manage risk
3. **Monitor performance metrics** regularly
4. **Keep commission and slippage** realistic
5. **Test on different time periods** to avoid overfitting
6. **Implement stop-losses** for risk management
7. **Diversify strategies** to reduce risk

## Support

- Documentation: `/docs` directory
- API Docs: `http://localhost:8000/docs`
- Issues: GitHub Issues
