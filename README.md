# Crypto Algorithmic Trading Strategy Optimization Platform

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-90%25+-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade cryptocurrency algorithmic trading and backtesting platform built with enterprise-level quality standards.

## Features

- **Multiple Trading Strategies**: MA Crossover, RSI, MACD, Bollinger Bands, and multi-strategy combinations
- **Advanced Backtesting Engine**: High-performance backtesting with realistic market simulation
- **Risk Management**: Position sizing, stop-loss, take-profit, and portfolio optimization
- **Real-time Data**: Integration with multiple cryptocurrency exchanges via CCXT
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, drawdown, win rate, etc.
- **REST API**: FastAPI-based API for programmatic access
- **Monitoring & Logging**: Structured logging and performance monitoring
- **Security**: Input validation, rate limiting, and secure configuration management
- **Docker Support**: Containerized deployment with docker-compose
- **90%+ Test Coverage**: Comprehensive unit and integration tests

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip or poetry for dependency management
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting.git
cd Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp config/config.example.yaml config/config.yaml
cp .env.example .env

# Edit configuration as needed
vim config/config.yaml
```

### Running a Backtest

```bash
# Run a simple backtest
python scripts/run_backtest.py --strategy ma_crossover --symbol BTC/USDT --timeframe 1h --start 2023-01-01 --end 2023-12-31

# Run with custom configuration
python scripts/run_backtest.py --config config/my_backtest.yaml
```

### Starting the API Server

```bash
# Development mode
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                   │
│  /backtest  /strategies  /data  /metrics  /health           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Core Trading Engine                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Backtester  │  │  Portfolio   │  │ Risk Manager │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Strategy Framework                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ MA Cross │  │   RSI    │  │   MACD   │  │ Bollinger│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Data Layer (CCXT)                         │
│  Fetching  │  Storage  │  Preprocessing  │  Validation      │
└─────────────────────────────────────────────────────────────┘
```

## Available Strategies

### 1. Moving Average Crossover
Generates signals when short-term MA crosses long-term MA.

### 2. RSI (Relative Strength Index)
Identifies overbought/oversold conditions.

### 3. MACD (Moving Average Convergence Divergence)
Signal line crossovers and histogram analysis.

### 4. Bollinger Bands
Price breakouts and mean reversion.

### 5. Multi-Strategy
Combines multiple strategies with configurable weights.

## Configuration

Configuration is managed through YAML files and environment variables:

```yaml
# config/config.yaml
exchange:
  name: binance
  sandbox: true

backtesting:
  initial_capital: 10000
  commission: 0.001
  slippage: 0.0005

risk_management:
  max_position_size: 0.1
  stop_loss: 0.02
  take_profit: 0.05
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Performance Metrics

The platform calculates comprehensive performance metrics:

- **Return Metrics**: Total return, annualized return, CAGR
- **Risk Metrics**: Sharpe ratio, Sortino ratio, maximum drawdown
- **Trade Metrics**: Win rate, profit factor, average trade duration
- **Statistical**: Alpha, beta, correlation with benchmark

## Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Development

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/
pylint src/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Strategy Development](docs/STRATEGIES.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [User Guide](docs/USER_GUIDE.md)
- [AI Telegram Bot & Taskade Integration](docs/AI_TELEGRAM_TASKADE_COPILOT_GUIDE.md) - Comprehensive guide for bot integration, troubleshooting, and best practices

## Security

- All API keys stored in environment variables
- Input validation on all endpoints
- Rate limiting implemented
- SQL injection prevention
- CORS configuration
- Security headers enabled

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/repo/issues)

## Acknowledgments

- CCXT library for exchange connectivity
- FastAPI for the web framework
- The open-source crypto trading community
