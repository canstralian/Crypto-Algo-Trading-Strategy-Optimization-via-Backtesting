"""
Intelligent error handling with user-friendly messages and solutions
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


@dataclass
class ErrorSolution:
    """Suggested solution for an error"""

    description: str
    action: str
    doc_link: Optional[str] = None


class CryptoOptimizerError(Exception):
    """Base exception with user-friendly messaging"""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        solutions: Optional[List[ErrorSolution]] = None,
    ):
        self.message = message
        self.context = context or {}
        self.solutions = solutions or []
        super().__init__(message)

    def display(self):
        """Display formatted error with solutions"""
        # Error header
        error_text = f"[bold red]❌ Error:[/bold red] {self.message}\n\n"

        # Context
        if self.context:
            error_text += "[bold]📋 Context:[/bold]\n"
            for key, value in self.context.items():
                error_text += f"  • {key}: [cyan]{value}[/cyan]\n"
            error_text += "\n"

        # Solutions
        if self.solutions:
            error_text += "[bold green]💡 Suggested Solutions:[/bold green]\n\n"
            for i, solution in enumerate(self.solutions, 1):
                error_text += f"{i}. [bold]{solution.description}[/bold]\n"
                error_text += f"   [dim]Action:[/dim] {solution.action}\n"
                if solution.doc_link:
                    error_text += f"   [dim]Docs:[/dim] [link={solution.doc_link}]{solution.doc_link}[/link]\n"
                error_text += "\n"

        panel = Panel(error_text, border_style="red", title="Error Details")
        console.print(panel)


class DataFetchError(CryptoOptimizerError):
    """Error fetching data from exchange"""

    @classmethod
    def api_key_invalid(cls, exchange: str):
        return cls(
            message=f"Failed to authenticate with {exchange}",
            context={
                "exchange": exchange,
                "checked_files": ".env and config/exchanges.yaml",
            },
            solutions=[
                ErrorSolution(
                    description="Verify your API credentials are correct",
                    action=f"Check that .env file contains valid {exchange.upper()}_API_KEY and {exchange.upper()}_API_SECRET",
                ),
                ErrorSolution(
                    description="Ensure API key has correct permissions",
                    action=f"Log into {exchange} and verify your API key has 'Read' or 'Spot Trading' permissions enabled",
                ),
                ErrorSolution(
                    description="Try regenerating your API key",
                    action=f"Create a new API key on {exchange} exchange and update your .env file",
                ),
            ],
        )

    @classmethod
    def rate_limit_exceeded(cls, exchange: str, retry_after: int):
        return cls(
            message=f"API rate limit exceeded for {exchange}",
            context={
                "exchange": exchange,
                "retry_after_seconds": retry_after,
                "reason": "Too many API requests in a short time",
            },
            solutions=[
                ErrorSolution(
                    description="Wait and the system will retry automatically",
                    action=f"The system will automatically retry in {retry_after} seconds. Please be patient.",
                ),
                ErrorSolution(
                    description="Reduce request frequency in configuration",
                    action="Edit config/exchanges.yaml and increase 'rate_limit_delay' to 2.0 or higher",
                ),
                ErrorSolution(
                    description="Use longer timeframes to reduce API calls",
                    action="Try using 4h or 1d timeframes instead of 1m or 5m - they require fewer data points",
                ),
            ],
        )

    @classmethod
    def symbol_not_found(cls, symbol: str, exchange: str):
        return cls(
            message=f"Trading pair '{symbol}' not found on {exchange}",
            context={
                "symbol": symbol,
                "exchange": exchange,
            },
            solutions=[
                ErrorSolution(
                    description="Check the symbol format",
                    action="Ensure symbol is in format BASE/QUOTE (e.g., BTC/USDT, ETH/USD)",
                ),
                ErrorSolution(
                    description="Verify the symbol exists on this exchange",
                    action=f"Visit {exchange} and confirm that {symbol} is listed for trading",
                ),
                ErrorSolution(
                    description="Try a common trading pair",
                    action="Start with popular pairs like BTC/USDT, ETH/USDT, or BNB/USDT",
                ),
            ],
        )

    @classmethod
    def connection_failed(cls, exchange: str, error_details: str):
        return cls(
            message=f"Failed to connect to {exchange}",
            context={
                "exchange": exchange,
                "error_details": error_details,
            },
            solutions=[
                ErrorSolution(
                    description="Check your internet connection",
                    action="Verify you have a stable internet connection and try again",
                ),
                ErrorSolution(
                    description="Verify exchange is operational",
                    action=f"Visit {exchange} status page to check if the exchange is experiencing downtime",
                ),
                ErrorSolution(
                    description="Check firewall/proxy settings",
                    action="Ensure your firewall or corporate proxy isn't blocking access to the exchange API",
                ),
            ],
        )


class StrategyError(CryptoOptimizerError):
    """Error in strategy configuration or execution"""

    @classmethod
    def invalid_parameters(cls, strategy_name: str, validation_errors: Dict[str, Any]):
        error_list = "\n".join(
            [f"    - {field}: {error}" for field, error in validation_errors.items()]
        )

        return cls(
            message=f"Strategy '{strategy_name}' has invalid parameters",
            context={
                "strategy": strategy_name,
                "validation_errors": error_list,
            },
            solutions=[
                ErrorSolution(
                    description="Fix the validation errors listed above",
                    action="Update your strategy configuration file with valid parameter values",
                ),
                ErrorSolution(
                    description="Use a pre-configured template",
                    action="Run: crypto-optimizer config create --template conservative_ma",
                ),
                ErrorSolution(
                    description="Use interactive mode for guided setup",
                    action="Run: crypto-optimizer interactive",
                ),
            ],
        )

    @classmethod
    def no_signals_generated(cls, strategy_name: str, timeframe: str):
        return cls(
            message=f"Strategy '{strategy_name}' generated no trading signals",
            context={
                "strategy": strategy_name,
                "timeframe": timeframe,
                "possible_causes": "Parameters too restrictive or insufficient data",
            },
            solutions=[
                ErrorSolution(
                    description="Adjust strategy parameters",
                    action="Try more sensitive parameters (e.g., smaller MA periods, wider RSI levels)",
                ),
                ErrorSolution(
                    description="Increase data period",
                    action="Download more historical data to give the strategy more opportunities",
                ),
                ErrorSolution(
                    description="Try a different timeframe",
                    action=f"Test with different timeframes - shorter periods generate more signals",
                ),
            ],
        )

    @classmethod
    def strategy_not_found(cls, strategy_name: str):
        return cls(
            message=f"Strategy '{strategy_name}' not found",
            context={
                "strategy": strategy_name,
                "searched_in": "strategies/ directory",
            },
            solutions=[
                ErrorSolution(
                    description="Check the strategy name spelling",
                    action="Verify you spelled the strategy name correctly (case-sensitive)",
                ),
                ErrorSolution(
                    description="List available strategies",
                    action="Run: crypto-optimizer list strategies",
                ),
                ErrorSolution(
                    description="Create a new strategy",
                    action="Run: crypto-optimizer config create --interactive",
                ),
            ],
        )


class BacktestError(CryptoOptimizerError):
    """Error during backtesting"""

    @classmethod
    def insufficient_data(
        cls, symbol: str, required_days: int, available_days: int, timeframe: str
    ):
        missing_days = required_days - available_days

        return cls(
            message=f"Insufficient data for backtest",
            context={
                "symbol": symbol,
                "timeframe": timeframe,
                "required_days": required_days,
                "available_days": available_days,
                "missing_days": missing_days,
            },
            solutions=[
                ErrorSolution(
                    description="Download more historical data",
                    action=f"Run: crypto-optimizer download --symbol {symbol} --timeframe {timeframe} --days {required_days}",
                ),
                ErrorSolution(
                    description="Adjust backtest date range",
                    action="Reduce the backtest period to match available data using --start and --end flags",
                ),
                ErrorSolution(
                    description="Use a different symbol with more history",
                    action="Major pairs like BTC/USDT typically have longer data history available",
                ),
            ],
        )

    @classmethod
    def backtest_failed(cls, strategy: str, error_msg: str):
        return cls(
            message=f"Backtest execution failed for '{strategy}'",
            context={
                "strategy": strategy,
                "error": error_msg,
            },
            solutions=[
                ErrorSolution(
                    description="Run in verbose mode for detailed logs",
                    action="Run: crypto-optimizer backtest --strategy {strategy} --verbose",
                ),
                ErrorSolution(
                    description="Validate your strategy configuration",
                    action="Run: crypto-optimizer config validate",
                ),
                ErrorSolution(
                    description="Check if data is corrupted",
                    action="Try re-downloading the historical data",
                ),
            ],
        )


class ConfigurationError(CryptoOptimizerError):
    """Configuration file errors"""

    @classmethod
    def file_not_found(cls, config_path: str):
        return cls(
            message=f"Configuration file not found",
            context={
                "expected_path": config_path,
            },
            solutions=[
                ErrorSolution(
                    description="Run the setup wizard",
                    action="Run: crypto-optimizer setup",
                ),
                ErrorSolution(
                    description="Create configuration interactively",
                    action="Run: crypto-optimizer config create --interactive",
                ),
                ErrorSolution(
                    description="Use a template configuration",
                    action="Run: crypto-optimizer config create --template conservative_ma",
                ),
            ],
        )

    @classmethod
    def invalid_yaml(cls, config_path: str, error_line: int, error_msg: str):
        return cls(
            message=f"Invalid YAML syntax in configuration file",
            context={
                "file": config_path,
                "line": error_line,
                "error": error_msg,
            },
            solutions=[
                ErrorSolution(
                    description="Fix the YAML syntax error",
                    action=f"Check line {error_line} in {config_path} and fix the syntax issue",
                ),
                ErrorSolution(
                    description="Use the configuration UI",
                    action="Edit configuration using: crypto-optimizer config edit --ui",
                ),
                ErrorSolution(
                    description="Regenerate configuration file",
                    action="Backup and recreate: crypto-optimizer config create --force",
                ),
            ],
        )


class OptimizationError(CryptoOptimizerError):
    """Errors during parameter optimization"""

    @classmethod
    def optimization_timeout(cls, strategy: str, iterations_completed: int):
        return cls(
            message=f"Optimization timed out",
            context={
                "strategy": strategy,
                "iterations_completed": iterations_completed,
                "status": "Partial results may be available",
            },
            solutions=[
                ErrorSolution(
                    description="Use the partial results",
                    action="Check optimization/results.json for best parameters found so far",
                ),
                ErrorSolution(
                    description="Reduce iteration count",
                    action="Try with fewer iterations: --iterations 50",
                ),
                ErrorSolution(
                    description="Use a faster optimization method",
                    action="Try genetic algorithm: --method genetic (faster than grid search)",
                ),
            ],
        )


# Error handler function for CLI
def handle_cli_error(error: Exception):
    """Central error handler for CLI commands"""
    if isinstance(error, CryptoOptimizerError):
        error.display()
    else:
        # Unexpected error - show full traceback in debug mode
        console.print(f"\n[bold red]❌ Unexpected Error:[/bold red] {str(error)}\n")
        console.print(
            "[yellow]This appears to be an unexpected error. Please report it at:[/yellow]"
        )
        console.print(
            "[link]https://github.com/yourusername/crypto-optimizer/issues[/link]\n"
        )

        # Show traceback
        import traceback

        console.print("[dim]" + traceback.format_exc() + "[/dim]")
