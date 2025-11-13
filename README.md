# 🚀 Crypto Strategy Optimizer

> Professional cryptocurrency algorithmic trading strategy optimization via backtesting

A modern, user-friendly platform for developing, testing, and optimizing cryptocurrency trading strategies. Built with a focus on excellent UI/UX, intelligent error handling, and professional-grade capabilities.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

### 🎯 User-Friendly Interface
- **Interactive CLI** with rich formatting, progress bars, and color-coded output
- **Guided Wizards** for common workflows - no need to memorize commands
- **Real-time Progress** tracking for long-running operations
- **Contextual Help** with actionable error messages and solutions

### 📊 Powerful Backtesting
- Multiple strategy types (Moving Average, RSI, Bollinger Bands, MACD, custom)
- Realistic simulation with commission and slippage modeling
- Comprehensive performance metrics (Sharpe ratio, max drawdown, win rate, etc.)
- Visual equity curves and trade analysis

### ⚙️ Smart Optimization
- Multiple optimization methods (Grid Search, Genetic Algorithm, Bayesian)
- Parallel processing for faster results
- Walk-forward analysis to prevent overfitting
- Parameter range validation

### 🔐 Professional Features
- **Configuration Validation** with Pydantic - catch errors before runtime
- **Intelligent Error Handling** with suggested solutions
- **Secure Credential Management** using environment variables
- **Comprehensive Logging** with structured output

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-algo-trading-strategy-optimization.git
cd crypto-algo-trading-strategy-optimization

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python cli.py setup
```

### Your First Backtest (Interactive Mode)

The easiest way to get started:

```bash
python cli.py interactive
```

This launches a guided wizard that walks you through:
1. Downloading historical data
2. Creating or selecting a strategy
3. Running your first backtest
4. Viewing results

### Your First Backtest (Command Line)

If you prefer the command line:

```bash
# 1. Download historical data
python cli.py download --symbol BTC/USDT --timeframe 1h --days 365

# 2. Run backtest with a template strategy
python cli.py backtest --strategy ma_crossover --symbol BTC/USDT

# 3. View results (displayed automatically)
```

## 📖 Usage Guide

### Interactive Mode (Recommended for Beginners)

```bash
python cli.py interactive
```

Interactive mode provides a menu-driven interface with prompts and validation.

### Command Line Mode (For Advanced Users)

#### Download Data

```bash
# Download 1 year of BTC/USDT hourly data
python cli.py download --symbol BTC/USDT --timeframe 1h --days 365

# Download 6 months of ETH/USDT 15-minute data
python cli.py download --symbol ETH/USDT --timeframe 15m --days 180
```

#### Run Backtest

```bash
# Basic backtest
python cli.py backtest --strategy ma_crossover --symbol BTC/USDT

# Backtest with custom date range
python cli.py backtest \
  --strategy ma_crossover \
  --symbol BTC/USDT \
  --start 2023-01-01 \
  --end 2024-01-01

# Verbose output
python cli.py backtest --strategy ma_crossover --verbose
```

#### Optimize Parameters

```bash
# Optimize using genetic algorithm
python cli.py optimize \
  --strategy ma_crossover \
  --method genetic \
  --iterations 100

# Grid search optimization
python cli.py optimize \
  --strategy ma_crossover \
  --method grid \
  --iterations 50
```

### Configuration

#### Strategy Configuration

Strategies are configured in YAML files located in `config/`. Start with a template:

```yaml
# config/my_strategy.yaml
strategy:
  name: "My Custom Strategy"
  description: "Conservative moving average crossover"
  timeframe: "1h"

  # Indicator parameters
  ma_fast: 10
  ma_slow: 30

  # Risk management
  risk_per_trade: 0.02  # 2% of capital per trade
  stop_loss_pct: 0.02   # 2% stop loss
  take_profit_pct: 0.04 # 4% take profit

backtest:
  start_date: "2023-01-01T00:00:00"
  end_date: "2024-01-01T00:00:00"
  initial_capital: 10000
  commission: 0.001     # 0.1% per trade
  slippage: 0.0005      # 0.05% slippage
```

The system validates your configuration and provides helpful error messages if anything is wrong.

#### Exchange API Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API credentials:
   ```
   BINANCE_API_KEY=your_key_here
   BINANCE_API_SECRET=your_secret_here
   BINANCE_TESTNET=true  # Start with testnet!
   ```

3. **Never commit your `.env` file to version control!**

## 🎨 UI/UX Highlights

### 1. Rich CLI with Progress Visualization

```
🚀 Crypto Optimizer

┌─────────────────────────────────────────────────────────┐
│ Professional Cryptocurrency Strategy Backtesting        │
│ Version 1.0.0 | Built with ❤️  for traders              │
└─────────────────────────────────────────────────────────┘

Running backtest for ma_crossover...

⠋ Running backtest... ━━━━━━━━━━━━━━━━━━━━━━━━━ 67% • ETA: 0:00:15
⠙ Loading data...      ━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
⠹ Calculating signals... ━━━━━━━━━━━━━━━━━━━━━━ 85%
```

### 2. Intelligent Error Messages

Instead of:
```
ValueError: slow_ma must be greater than fast_ma
```

You get:
```
┌─────────────────────────────────────────────────────────┐
│ ❌ Error: Strategy has invalid parameters               │
│                                                         │
│ 📋 Context:                                             │
│   • Slow MA (20) must be greater than Fast MA (30)     │
│                                                         │
│ 💡 Suggested Solutions:                                 │
│                                                         │
│ 1. Fix the parameter values                            │
│    Action: Set slow_ma > fast_ma (typically 2-3x)      │
│                                                         │
│ 2. Use a template configuration                        │
│    Action: crypto-optimizer config --template conservative│
└─────────────────────────────────────────────────────────┘
```

### 3. Beautiful Results Tables

```
┌─ Performance Metrics ─────────────────────────────┐
│ Metric            │ Value      │ Status          │
├───────────────────┼────────────┼─────────────────┤
│ Total Return      │ +47.3%     │ 🟢              │
│ Sharpe Ratio      │ 1.85       │ 🟢              │
│ Max Drawdown      │ -12.4%     │ 🟡              │
│ Win Rate          │ 62.5%      │ 🟢              │
│ Total Trades      │ 127        │ ℹ️               │
│ Profit Factor     │ 2.1        │ 🟢              │
└───────────────────┴────────────┴─────────────────┘
```

## 📚 Documentation

- **[UI/UX Analysis](UI_UX_ANALYSIS.md)** - Detailed UI/UX design philosophy and improvements
- **[Strategy Development Guide](docs/STRATEGY_GUIDE.md)** - How to create custom strategies
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## 🏗️ Project Structure

```
crypto-optimizer/
├── cli.py                      # Main CLI entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
│
├── src/
│   ├── config/
│   │   └── schemas.py         # Pydantic configuration schemas
│   ├── data/
│   │   ├── fetcher.py         # Data downloading
│   │   └── storage.py         # Database operations
│   ├── strategies/
│   │   ├── base.py            # Base strategy class
│   │   ├── ma_crossover.py    # Moving average strategy
│   │   └── rsi_strategy.py    # RSI strategy
│   ├── backtesting/
│   │   ├── engine.py          # Backtesting engine
│   │   └── metrics.py         # Performance calculations
│   ├── optimization/
│   │   └── optimizer.py       # Parameter optimization
│   └── utils/
│       ├── errors.py          # Error handling
│       └── logging.py         # Logging utilities
│
├── config/
│   └── strategy_templates.yaml # Strategy templates
│
├── tests/                     # Unit tests
├── docs/                      # Documentation
└── .github/                   # GitHub configuration
```

## 🔧 Advanced Features

### Custom Strategy Development

Create your own strategy by extending the base class:

```python
from src.strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        # Your custom logic here
        signals = []
        # ...
        return signals
```

### Web Dashboard (Coming Soon)

A responsive web interface with:
- Real-time backtest monitoring
- Interactive charts
- Strategy comparison
- Parameter optimization UI

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This software is for educational and research purposes only.**

- Cryptocurrency trading involves substantial risk of loss
- Past performance does not guarantee future results
- Always test strategies on paper trading/testnet before live trading
- Never invest more than you can afford to lose
- The authors are not responsible for any financial losses

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- Backtesting powered by [Backtrader](https://www.backtrader.com/)
- Exchange connectivity via [CCXT](https://github.com/ccxt/ccxt)

## 📧 Support

- **Documentation**: Check the [docs/](docs/) folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/crypto-optimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/crypto-optimizer/discussions)

---

**Happy Trading! 📈**

*Remember: The best strategy is the one you understand and can stick with through market cycles.*
