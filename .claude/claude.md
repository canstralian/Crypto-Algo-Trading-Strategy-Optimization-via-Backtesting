# Crypto Strategy Optimizer - Claude AI Assistant Guide

This document helps Claude AI assistants understand the project structure, conventions, and guidelines when working with this codebase.

## Project Overview

**Project Name:** Crypto Strategy Optimizer
**Purpose:** Professional cryptocurrency algorithmic trading strategy optimization via backtesting
**Language:** Python 3.11+
**Focus:** Excellent UI/UX, intelligent error handling, user-friendly interface

## Core Principles

### 1. UI/UX First
- Every feature must have excellent user experience
- Use rich formatting in CLI (colors, tables, progress bars)
- Provide interactive wizards for complex workflows
- Show real-time progress for long operations
- Clear, actionable error messages with solutions

### 2. Progressive Disclosure
- Don't overwhelm users with all options at once
- Start simple, reveal complexity gradually
- Provide both interactive (beginner) and CLI (advanced) modes

### 3. Intelligent Validation
- Validate configuration before execution
- Use Pydantic models for type safety
- Provide helpful error messages with context and solutions
- Suggest fixes, don't just report errors

### 4. Security First
- API keys in .env files (never in code or config)
- Default to testnet for exchange connections
- Validate all user inputs
- Never log sensitive information

## Project Structure

```
crypto-optimizer/
├── cli.py                          # Main CLI entry point with Click
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
│
├── src/
│   ├── config/
│   │   └── schemas.py             # Pydantic config models
│   ├── data/
│   │   ├── fetcher.py             # Data downloading from exchanges
│   │   └── storage.py             # Database operations
│   ├── strategies/
│   │   ├── base.py                # BaseStrategy abstract class
│   │   ├── ma_crossover.py        # Moving average strategy
│   │   └── rsi_strategy.py        # RSI strategy
│   ├── backtesting/
│   │   ├── engine.py              # Backtest execution
│   │   └── metrics.py             # Performance calculations
│   ├── optimization/
│   │   └── optimizer.py           # Parameter optimization
│   └── utils/
│       ├── errors.py              # Custom exceptions
│       └── logging.py             # Structured logging
│
├── config/
│   └── strategy_templates.yaml    # Pre-configured strategies
│
├── tests/                         # Unit tests
├── docs/                          # User documentation
└── .github/                       # GitHub templates
```

## Code Conventions

### Python Style

- **Formatting:** Black (88 char line length)
- **Linting:** Ruff
- **Type Checking:** mypy
- **Docstrings:** Google style
- **Type Hints:** Required for all functions

### Example Function

```python
def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.0,
) -> float:
    """Calculate the Sharpe ratio for a return series.

    Args:
        returns: List of period returns as decimals.
        risk_free_rate: Annual risk-free rate (default: 0.0).

    Returns:
        The Sharpe ratio as a float.

    Raises:
        ValueError: If returns list is empty or has insufficient data.
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")

    # Implementation...
```

### Error Handling Pattern

Always use custom error classes with solutions:

```python
# ❌ DON'T DO THIS
if api_key is None:
    raise ValueError("API key missing")

# ✅ DO THIS
if api_key is None:
    raise ConfigurationError.file_not_found(
        config_path=".env"
    )
```

### CLI Command Pattern

```python
@cli.command()
@click.option('--symbol', default='BTC/USDT', help='Trading pair')
@click.option('--verbose', is_flag=True, help='Show detailed output')
def download(symbol: str, verbose: bool):
    """📥 Download historical cryptocurrency data"""

    # Show progress
    with Progress(...) as progress:
        task = progress.add_task("[cyan]Downloading...", total=100)
        # ... do work ...

    # Show success
    console.print("[bold green]✓ Download complete![/bold green]")
```

## Configuration System

### Schema Definition (Pydantic)

```python
class StrategyConfig(BaseModel):
    """Strategy configuration with validation."""

    ma_fast: int = Field(
        default=10,
        ge=2, le=200,
        description="Fast moving average period (2-200)"
    )
    ma_slow: int = Field(
        default=30,
        ge=2, le=200,
        description="Slow moving average period (2-200)"
    )

    @field_validator('ma_slow')
    @classmethod
    def validate_ma_order(cls, v: int, info) -> int:
        """Ensure slow MA > fast MA."""
        if 'ma_fast' in info.data and v <= info.data['ma_fast']:
            raise ValueError(
                f"Slow MA ({v}) must be greater than fast MA ({info.data['ma_fast']}). "
                "Typically, slow MA should be 2-3x the fast MA period."
            )
        return v
```

### YAML Configuration

```yaml
strategy:
  name: "My Strategy"
  timeframe: "1h"
  ma_fast: 10
  ma_slow: 30
  risk_per_trade: 0.02

backtest:
  start_date: "2023-01-01T00:00:00"
  end_date: "2024-01-01T00:00:00"
  initial_capital: 10000
```

## UI/UX Patterns

### Progress Indication

For any operation >2 seconds:

```python
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
) as progress:
    task = progress.add_task("[cyan]Processing...", total=100)

    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

### Result Display

Use rich tables for structured data:

```python
table = Table(title="Performance Metrics", box=box.ROUNDED)
table.add_column("Metric", style="cyan")
table.add_column("Value", style="magenta")
table.add_column("Status", justify="center")

table.add_row("Total Return", "+47.3%", "🟢")
table.add_row("Sharpe Ratio", "1.85", "🟢")

console.print(table)
```

### Interactive Prompts

Use questionary for interactive mode:

```python
questions = [
    {
        'type': 'select',
        'name': 'action',
        'message': 'What would you like to do?',
        'choices': [
            '📥 Download data',
            '🔬 Run backtest',
            '⚙️  Optimize parameters',
        ]
    }
]

answers = questionary.prompt(questions)
```

## Error Handling

### Custom Error Classes

Located in `src/utils/errors.py`:

- `CryptoOptimizerError` - Base class
- `DataFetchError` - Data/API issues
- `StrategyError` - Strategy configuration/execution
- `BacktestError` - Backtest issues
- `ConfigurationError` - Config file problems
- `OptimizationError` - Optimization issues

### Usage

```python
# Data fetch error with solutions
raise DataFetchError.api_key_invalid(exchange="binance")

# Strategy error
raise StrategyError.invalid_parameters(
    strategy_name="ma_crossover",
    validation_errors={"ma_slow": "Must be > ma_fast"}
)

# Backtest error
raise BacktestError.insufficient_data(
    symbol="BTC/USDT",
    required_days=365,
    available_days=180,
    timeframe="1h"
)
```

## Testing Guidelines

### Test Structure

```python
def test_feature_description():
    """Test that feature works correctly."""
    # Arrange
    config = StrategyConfig(ma_fast=10, ma_slow=30)

    # Act
    result = calculate_something(config)

    # Assert
    assert result == expected_value
```

### Test Coverage Goals

- Unit tests: >80% coverage
- Critical paths: 100% coverage
- Error handling: Test both success and failure cases

## Common Tasks for Claude

### Adding a New Strategy

1. Create file in `src/strategies/new_strategy.py`
2. Extend `BaseStrategy` class
3. Implement `generate_signals()` method
4. Add configuration schema to `src/config/schemas.py`
5. Add template to `config/strategy_templates.yaml`
6. Add CLI command in `cli.py`
7. Write tests in `tests/test_new_strategy.py`
8. Update documentation

### Adding a CLI Command

1. Add command to `cli.py`:
```python
@cli.command()
@click.option('--param', help='Parameter description')
def new_command(param: str):
    """🎯 Command description"""
    # Implementation with progress bars and error handling
```

2. Test manually and with unit tests
3. Update README.md with usage example

### Improving Error Messages

1. Identify the error condition
2. Create/update error class in `src/utils/errors.py`
3. Provide context dictionary
4. List 2-3 actionable solutions
5. Test the error message

### Adding Configuration Options

1. Add field to appropriate schema in `src/config/schemas.py`
2. Add validation with `@field_validator`
3. Provide helpful description
4. Set sensible default
5. Update YAML template
6. Document in README.md

## Documentation Requirements

When adding features:

1. **Code Comments:** Explain "why", not "what"
2. **Docstrings:** All public functions/classes
3. **README.md:** User-facing features
4. **UI_UX_ANALYSIS.md:** UI/UX changes
5. **Type Hints:** All function parameters and returns

## Security Checklist

- [ ] No API keys/secrets in code
- [ ] Environment variables for sensitive data
- [ ] Input validation for user-provided data
- [ ] Safe file operations (path validation)
- [ ] No command injection vulnerabilities
- [ ] Proper error messages (don't leak sensitive info)

## Performance Guidelines

- Show progress for operations >2 seconds
- Use async/await for I/O operations (when applicable)
- Cache API responses where appropriate
- Optimize database queries
- Profile before optimizing

## Git Workflow

### Commit Messages

```
feat: Add RSI strategy template

- Implement RSI mean reversion strategy
- Add validation for RSI parameters
- Include example configuration

Closes #123
```

### Branch Naming

- `feat/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-changed` - Documentation
- `refactor/component` - Refactoring

## Resources

- **Rich Documentation:** https://rich.readthedocs.io/
- **Click Documentation:** https://click.palletsprojects.com/
- **Pydantic Documentation:** https://docs.pydantic.dev/
- **UI/UX Guidelines:** See `UI_UX_ANALYSIS.md`
- **Contributing Guide:** See `.github/CONTRIBUTING.md`

## Quick Reference

### Running the Application

```bash
# Interactive mode (recommended for beginners)
python cli.py interactive

# Download data
python cli.py download --symbol BTC/USDT --days 365

# Run backtest
python cli.py backtest --strategy ma_crossover

# Optimize parameters
python cli.py optimize --strategy ma_crossover --method genetic
```

### Development Commands

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Common Patterns to Follow

1. **Always show progress** for long operations
2. **Always validate input** before processing
3. **Always provide solutions** with error messages
4. **Always use type hints**
5. **Always write tests** for new features
6. **Always update documentation**

## Common Anti-Patterns to Avoid

1. ❌ Plain print statements → ✅ Use rich console
2. ❌ Generic error messages → ✅ Use custom error classes
3. ❌ No progress indication → ✅ Show progress bars
4. ❌ Silent failures → ✅ Explicit error messages
5. ❌ Missing type hints → ✅ Add type hints
6. ❌ Hardcoded values → ✅ Use configuration

## Questions to Ask Before Implementing

1. Does this improve user experience?
2. Is the error handling comprehensive?
3. Are there helpful error messages with solutions?
4. Is progress visible for long operations?
5. Is it accessible to beginners via interactive mode?
6. Is it efficient for advanced users via CLI?
7. Are edge cases handled?
8. Is it well documented?
9. Are there tests?
10. Does it follow the project conventions?

---

**Remember:** This project prioritizes user experience above all else. Every feature should be approachable for beginners yet powerful for experts.
