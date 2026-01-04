# GitHub Copilot Instructions for Crypto Trading Platform

This is a Python-based cryptocurrency algorithmic trading and backtesting platform. It provides production-grade features for strategy development, backtesting, risk management, and real-time trading via REST API. Please follow these guidelines when contributing:

## Code Standards

### Required Before Each Commit
- Run `black src/ tests/` to format code
- Run `isort src/ tests/` to sort imports with Black profile
- Run `flake8 src/ tests/` to check code quality
- Run `mypy src/` for type checking
- Or use `pre-commit run --all-files` to run all checks at once

### Development Flow
- **Install dependencies**: `pip install -r requirements.txt` (production) or `pip install -r requirements-dev.txt` (development)
- **Run tests**: `pytest` or `pytest --cov=src --cov-report=html` for coverage report
- **Run unit tests only**: `pytest tests/unit/`
- **Run integration tests only**: `pytest tests/integration/`
- **Lint code**: `flake8 src/ tests/`
- **Type check**: `mypy src/`
- **Security scan**: `bandit -r src/`
- **Format code**: `black src/ tests/`
- **Sort imports**: `isort src/ tests/`
- **Run all quality checks**: `pre-commit run --all-files`

### API Server
- **Development**: `uvicorn src.api.main:app --reload` (binds to localhost:8000 by default)
- **Production**: `gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`
- **API docs**: http://localhost:8000/docs (Swagger UI) or http://localhost:8000/redoc

## Repository Structure
- `src/`: Main source code
  - `api/`: FastAPI REST API endpoints
  - `core/`: Core trading engine (backtester, portfolio, risk manager)
  - `strategies/`: Trading strategy implementations (MA crossover, RSI, MACD, Bollinger Bands)
  - `data/`: Data fetching, storage, and preprocessing (CCXT integration)
  - `analysis/`: Performance metrics and analytics
  - `utils/`: Utility functions and helpers
- `tests/`: Test suite
  - `unit/`: Unit tests
  - `integration/`: Integration tests
- `config/`: Configuration files (YAML)
- `docs/`: Documentation (architecture, API reference, user guides)
- `scripts/`: Helper scripts for running backtests and setup
- `cache/`: Cached data (gitignored)
- `data/`: Historical market data (gitignored)

## Key Guidelines

### Python Best Practices
1. **Type hints**: All functions must have type hints for parameters and return values
2. **Docstrings**: Use Google-style docstrings for all public functions and classes
3. **Error handling**: Use specific exception types, avoid bare `except:` clauses
4. **Async/await**: Use async functions for I/O operations (API calls, file operations)
5. **Pydantic models**: Use Pydantic for data validation and settings management
6. **Configuration**: Store sensitive data in `.env`, configuration in `config/config.yaml`

### Code Style
1. **Line length**: Maximum 100 characters
2. **Imports**: Group imports (standard library, third-party, local) using isort with Black profile
3. **String formatting**: Prefer f-strings over `.format()` or `%` formatting
4. **Naming**: 
   - Functions/variables: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Private members: `_leading_underscore`

### Testing Requirements
1. **Coverage target**: Maintain 90%+ test coverage
2. **Test structure**: Use pytest fixtures, parametrize tests when applicable
3. **Test organization**: Place unit tests in `tests/unit/`, integration tests in `tests/integration/`
4. **Mocking**: Use `pytest-mock` for mocking external dependencies
5. **Async tests**: Use `pytest-asyncio` for testing async functions
6. **Test markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow` appropriately

### Documentation
1. **README updates**: Update README.md when adding new features
2. **API documentation**: Document new API endpoints with OpenAPI/Swagger docstrings
3. **Code comments**: Add comments for complex algorithms or non-obvious logic
4. **Documentation files**: Update relevant docs in `docs/` when making architectural changes

### Security
1. **No secrets in code**: All API keys, passwords must be in `.env` file
2. **Input validation**: Validate all user inputs using Pydantic models
3. **SQL injection**: Use parameterized queries with SQLAlchemy ORM
4. **Dependencies**: Run `bandit -r src/` before committing to check for security issues
5. **CORS**: Be careful with CORS settings in FastAPI

### Strategy Development
1. **Base class**: All strategies must inherit from `BaseStrategy` class
2. **Required methods**: Implement `generate_signals()` method
3. **Parameters**: Use Pydantic models for strategy parameters
4. **Indicators**: Use the `ta` library for technical indicators
5. **Testing**: Add unit tests for each strategy with sample data

### Performance
1. **Vectorization**: Use numpy/pandas vectorized operations instead of loops when possible
2. **Caching**: Cache expensive computations (e.g., indicator calculations)
3. **Database**: Use async SQLAlchemy for database operations
4. **JSON serialization**: Use `orjson` for fast JSON serialization in API responses

### Git Workflow
1. **Commit messages**: Use clear, descriptive commit messages
2. **Branch naming**: Use feature/, bugfix/, hotfix/ prefixes
3. **Pre-commit hooks**: Ensure pre-commit hooks pass before pushing
4. **Pull requests**: Include tests and update documentation in PRs

## Common Development Tasks

### Adding a New Strategy
1. Create a new file in `src/strategies/` inheriting from `BaseStrategy`
2. Implement `generate_signals()` method
3. Add Pydantic model for strategy parameters
4. Add unit tests in `tests/unit/test_strategies/`
5. Update strategy documentation in `docs/STRATEGIES.md`

### Adding a New API Endpoint
1. Add endpoint in appropriate router in `src/api/`
2. Define request/response models using Pydantic
3. Add error handling and validation
4. Add integration tests in `tests/integration/test_api/`
5. API documentation will auto-generate from FastAPI

### Running a Backtest
```bash
python scripts/run_backtest.py --strategy ma_crossover --symbol BTC/USDT --timeframe 1h --start 2023-01-01 --end 2023-12-31
```

## Technology Stack
- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **Data**: pandas, numpy, ccxt (exchange connectivity)
- **Technical Analysis**: ta library
- **Database**: SQLAlchemy (async), aiosqlite
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Code Quality**: black, flake8, pylint, mypy, isort, bandit
- **API Documentation**: OpenAPI/Swagger (via FastAPI)
- **Logging**: structlog
- **Configuration**: PyYAML, python-dotenv, Pydantic Settings

## Environment Setup
1. Python 3.9+ required
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements-dev.txt`
5. Copy configuration: `cp config/config.example.yaml config/config.yaml`
6. Copy environment: `cp .env.example .env`
7. Install pre-commit hooks: `pre-commit install`

## Troubleshooting
- If tests fail due to missing dependencies, run `pip install -r requirements-dev.txt`
- If import errors occur, ensure the project root is in PYTHONPATH or install in editable mode: `pip install -e .`
- For type checking errors, check that all dependencies have type stubs installed
- For pre-commit hook issues, run `pre-commit clean` and `pre-commit install` again
