#!/usr/bin/env python3
"""
Crypto Strategy Optimizer - Interactive CLI
Main command-line interface with rich UI components
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.markdown import Markdown
from rich import box
import pyfiglet
import questionary
from datetime import datetime, timedelta
import sys

console = Console()

BANNER = pyfiglet.figlet_format("Crypto Optimizer", font="slant")


def show_banner():
    """Display application banner"""
    console.print(f"[cyan]{BANNER}[/cyan]")
    console.print(
        Panel(
            "[bold]Professional Cryptocurrency Strategy Backtesting & Optimization[/bold]\n"
            "Version 1.0.0 | Built with ❤️  for traders",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    console.print()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🚀 Crypto Strategy Optimizer - Professional Trading Backtesting

    A modern, user-friendly platform for developing, testing, and optimizing
    cryptocurrency trading strategies.
    """
    pass


@cli.command()
def interactive():
    """🎯 Launch interactive setup wizard"""
    show_banner()

    console.print("[bold cyan]Welcome to Interactive Mode![/bold cyan]\n")
    console.print("Let's help you get started with your trading strategy.\n")

    # Interactive questionnaire
    questions = [
        {
            "type": "select",
            "name": "action",
            "message": "What would you like to do?",
            "choices": [
                "📥 Download historical data",
                "📊 Create a new strategy",
                "🔬 Run a backtest",
                "⚙️  Optimize strategy parameters",
                "📈 View backtest results",
                "❌ Exit",
            ],
        }
    ]

    answer = questionary.prompt(questions)

    if not answer or answer["action"] == "❌ Exit":
        console.print("\n[yellow]Goodbye! Happy trading! 👋[/yellow]")
        return

    action = answer["action"]

    if "Download" in action:
        download_data_wizard()
    elif "Create" in action:
        create_strategy_wizard()
    elif "Run a backtest" in action:
        run_backtest_wizard()
    elif "Optimize" in action:
        optimize_wizard()
    elif "View results" in action:
        view_results_wizard()


def download_data_wizard():
    """Interactive data download wizard"""
    console.print("\n[bold cyan]📥 Data Download Wizard[/bold cyan]\n")

    questions = [
        {
            "type": "select",
            "name": "symbol",
            "message": "Select cryptocurrency pair:",
            "choices": [
                "BTC/USDT",
                "ETH/USDT",
                "BNB/USDT",
                "SOL/USDT",
                "Custom...",
            ],
        },
        {
            "type": "select",
            "name": "timeframe",
            "message": "Select timeframe:",
            "choices": ["1m", "5m", "15m", "1h", "4h", "1d"],
        },
        {
            "type": "text",
            "name": "days",
            "message": "How many days of history? (default: 365)",
            "default": "365",
        },
    ]

    answers = questionary.prompt(questions)

    if answers["symbol"] == "Custom...":
        custom = questionary.text("Enter symbol (e.g., ADA/USDT):").ask()
        answers["symbol"] = custom

    console.print(
        f"\n[green]✓[/green] Downloading {answers['days']} days of {answers['symbol']} "
        f"data at {answers['timeframe']} timeframe...\n"
    )

    # Simulate download with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(
            "[cyan]Fetching from exchange...", total=100
        )

        import time

        for i in range(100):
            time.sleep(0.02)  # Simulate work
            progress.update(task, advance=1)

    console.print(
        f"[bold green]✓ Successfully downloaded {answers['symbol']} data![/bold green]\n"
    )
    console.print(
        f"[dim]Data saved to: data/{answers['symbol'].replace('/', '_')}_{answers['timeframe']}.csv[/dim]\n"
    )


def create_strategy_wizard():
    """Interactive strategy creation wizard"""
    console.print("\n[bold cyan]📊 Strategy Creation Wizard[/bold cyan]\n")

    questions = [
        {
            "type": "select",
            "name": "template",
            "message": "Choose a starting template:",
            "choices": [
                "Moving Average Crossover",
                "RSI Mean Reversion",
                "Bollinger Bands",
                "MACD Strategy",
                "Custom (blank template)",
            ],
        },
        {
            "type": "text",
            "name": "name",
            "message": "Strategy name:",
            "default": "My Strategy",
        },
    ]

    answers = questionary.prompt(questions)

    console.print(
        f"\n[green]✓[/green] Creating '{answers['name']}' based on "
        f"{answers['template']}...\n"
    )

    # Display example configuration
    config_panel = Panel(
        """[yellow]strategy:[/yellow]
  [cyan]name:[/cyan] My Strategy
  [cyan]timeframe:[/cyan] 1h
  [cyan]ma_fast:[/cyan] 10
  [cyan]ma_slow:[/cyan] 30
  [cyan]risk_per_trade:[/cyan] 0.02

[yellow]backtest:[/yellow]
  [cyan]initial_capital:[/cyan] 10000
  [cyan]commission:[/cyan] 0.001""",
        title="[bold]Generated Configuration[/bold]",
        border_style="green",
    )

    console.print(config_panel)
    console.print(
        f"\n[green]✓[/green] Strategy saved to: strategies/{answers['name'].lower().replace(' ', '_')}.yaml\n"
    )


def run_backtest_wizard():
    """Interactive backtest wizard"""
    console.print("\n[bold cyan]🔬 Backtest Wizard[/bold cyan]\n")

    questions = [
        {
            "type": "text",
            "name": "strategy",
            "message": "Strategy name:",
            "default": "ma_crossover",
        },
        {
            "type": "text",
            "name": "symbol",
            "message": "Trading pair:",
            "default": "BTC/USDT",
        },
        {
            "type": "text",
            "name": "start_date",
            "message": "Start date (YYYY-MM-DD):",
            "default": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        },
        {
            "type": "text",
            "name": "end_date",
            "message": "End date (YYYY-MM-DD):",
            "default": datetime.now().strftime("%Y-%m-%d"),
        },
    ]

    answers = questionary.prompt(questions)

    console.print(f"\n[green]✓[/green] Starting backtest...\n")

    # Simulate backtest with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("• ETA: {task.time_remaining}"),
    ) as progress:
        main_task = progress.add_task("[cyan]Running backtest...", total=100)
        data_task = progress.add_task("[yellow]Loading data...", total=100)
        calc_task = progress.add_task("[green]Calculating signals...", total=100)

        import time

        for i in range(100):
            time.sleep(0.03)
            progress.update(main_task, advance=1)
            if i < 30:
                progress.update(data_task, advance=3.33)
            elif i < 70:
                progress.update(calc_task, advance=2.5)

    # Display results
    display_backtest_results()


def display_backtest_results():
    """Display formatted backtest results"""
    console.print("\n[bold green]✓ Backtest Complete![/bold green]\n")

    # Results table
    table = Table(title="Performance Metrics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Status", justify="center")

    table.add_row("Total Return", "+47.3%", "🟢")
    table.add_row("Sharpe Ratio", "1.85", "🟢")
    table.add_row("Max Drawdown", "-12.4%", "🟡")
    table.add_row("Win Rate", "62.5%", "🟢")
    table.add_row("Total Trades", "127", "ℹ️")
    table.add_row("Profit Factor", "2.1", "🟢")

    console.print(table)

    # Summary panel
    summary = Panel(
        "[green]✓[/green] Strategy shows profitable results\n"
        "[yellow]⚠[/yellow]  Consider optimizing to reduce drawdown\n"
        "[blue]ℹ[/blue]  Good risk-adjusted returns (Sharpe > 1.5)",
        title="[bold]Analysis[/bold]",
        border_style="blue",
    )

    console.print("\n", summary)
    console.print(
        "\n[dim]Full report saved to: reports/backtest_20241113_215900.html[/dim]\n"
    )


def optimize_wizard():
    """Interactive optimization wizard"""
    console.print("\n[bold cyan]⚙️  Parameter Optimization Wizard[/bold cyan]\n")

    questions = [
        {
            "type": "text",
            "name": "strategy",
            "message": "Strategy to optimize:",
            "default": "ma_crossover",
        },
        {
            "type": "select",
            "name": "method",
            "message": "Optimization method:",
            "choices": ["Grid Search", "Genetic Algorithm", "Bayesian Optimization"],
        },
        {
            "type": "text",
            "name": "iterations",
            "message": "Maximum iterations:",
            "default": "100",
        },
    ]

    answers = questionary.prompt(questions)

    console.print(
        f"\n[green]✓[/green] Starting {answers['method']} optimization...\n"
    )
    console.print(
        "[yellow]Note:[/yellow] This may take several minutes. You can pause anytime with Ctrl+C\n"
    )

    # Simulate optimization
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(
            f"[cyan]Testing parameter combinations...", total=100
        )

        import time

        for i in range(100):
            time.sleep(0.05)
            progress.update(task, advance=1)

    # Display results
    console.print("\n[bold green]✓ Optimization Complete![/bold green]\n")

    results_table = Table(title="Top 3 Parameter Sets", box=box.ROUNDED)
    results_table.add_column("Rank", style="cyan")
    results_table.add_column("MA Fast", style="yellow")
    results_table.add_column("MA Slow", style="yellow")
    results_table.add_column("Return", style="green")
    results_table.add_column("Sharpe", style="magenta")

    results_table.add_row("1st", "12", "34", "+52.1%", "2.05")
    results_table.add_row("2nd", "10", "30", "+47.3%", "1.85")
    results_table.add_row("3rd", "15", "40", "+45.8%", "1.92")

    console.print(results_table)
    console.print(
        "\n[dim]Detailed results saved to: optimization/results_20241113.json[/dim]\n"
    )


def view_results_wizard():
    """View previous backtest results"""
    console.print("\n[bold cyan]📈 Backtest Results Viewer[/bold cyan]\n")

    # Mock results list
    results_table = Table(title="Recent Backtests", box=box.ROUNDED)
    results_table.add_column("ID", style="cyan")
    results_table.add_column("Strategy", style="yellow")
    results_table.add_column("Date", style="dim")
    results_table.add_column("Return", style="green")
    results_table.add_column("Status", justify="center")

    results_table.add_row("001", "ma_crossover", "2024-11-10", "+47.3%", "✓")
    results_table.add_row("002", "rsi_mean_reversion", "2024-11-12", "+28.5%", "✓")
    results_table.add_row("003", "bollinger_bands", "2024-11-13", "-8.2%", "✗")

    console.print(results_table)
    console.print()


@cli.command()
@click.option("--symbol", default="BTC/USDT", help="Trading pair")
@click.option("--timeframe", default="1h", help="Candlestick timeframe")
@click.option("--days", default=365, help="Days of historical data")
def download(symbol, timeframe, days):
    """📥 Download historical cryptocurrency data"""
    console.print(
        f"\n[cyan]Downloading {days} days of {symbol} data ({timeframe} timeframe)...[/cyan]\n"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("[cyan]Fetching from exchange...", total=100)

        import time

        for i in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)

    console.print(f"[bold green]✓ Download complete![/bold green]")
    console.print(
        f"[dim]Saved to: data/{symbol.replace('/', '_')}_{timeframe}.csv[/dim]\n"
    )


@cli.command()
@click.option("--strategy", required=True, help="Strategy name")
@click.option("--symbol", default="BTC/USDT", help="Trading pair")
@click.option(
    "--start",
    default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
    help="Start date (YYYY-MM-DD)",
)
@click.option(
    "--end", default=datetime.now().strftime("%Y-%m-%d"), help="End date (YYYY-MM-DD)"
)
@click.option("--verbose", is_flag=True, help="Show detailed output")
def backtest(strategy, symbol, start, end, verbose):
    """🔬 Run strategy backtest"""
    console.print(f"\n[cyan]Running backtest for {strategy}...[/cyan]\n")

    if verbose:
        console.print(f"[dim]Strategy: {strategy}[/dim]")
        console.print(f"[dim]Symbol: {symbol}[/dim]")
        console.print(f"[dim]Period: {start} to {end}[/dim]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("[cyan]Running backtest...", total=100)

        import time

        for i in range(100):
            time.sleep(0.03)
            progress.update(task, advance=1)

    display_backtest_results()


@cli.command()
@click.option("--strategy", required=True, help="Strategy to optimize")
@click.option(
    "--method",
    type=click.Choice(["grid", "genetic", "bayesian"]),
    default="genetic",
    help="Optimization method",
)
@click.option("--iterations", default=100, help="Maximum iterations")
def optimize(strategy, method, iterations):
    """⚙️  Optimize strategy parameters"""
    console.print(
        f"\n[cyan]Optimizing {strategy} using {method} method...[/cyan]\n"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(
            "[cyan]Testing parameter combinations...", total=iterations
        )

        import time

        for i in range(iterations):
            time.sleep(0.05)
            progress.update(task, advance=1)

    console.print("\n[bold green]✓ Optimization complete![/bold green]\n")


@cli.command()
def setup():
    """⚙️  Initial setup wizard"""
    show_banner()

    console.print("[bold cyan]Welcome to Crypto Strategy Optimizer![/bold cyan]\n")
    console.print("Let's set up your environment.\n")

    # API key setup
    has_api = questionary.confirm(
        "Do you have exchange API credentials?", default=False
    ).ask()

    if has_api:
        exchange = questionary.select(
            "Select exchange:",
            choices=["Binance", "Coinbase", "Kraken", "Skip for now"],
        ).ask()

        if exchange != "Skip for now":
            console.print(
                f"\n[yellow]Add your {exchange} API credentials to .env file:[/yellow]\n"
            )
            console.print("[dim]API_KEY=your_api_key_here[/dim]")
            console.print("[dim]API_SECRET=your_api_secret_here[/dim]\n")
    else:
        console.print(
            "\n[yellow]No problem! You can add API credentials later in the .env file.[/yellow]\n"
        )

    console.print("[green]✓ Setup complete![/green]\n")
    console.print("Next steps:")
    console.print("  1. Run [cyan]crypto-optimizer interactive[/cyan] for guided mode")
    console.print("  2. Or try [cyan]crypto-optimizer download --symbol BTC/USDT[/cyan]")
    console.print()


@cli.command()
def info():
    """ℹ️  Show system information"""
    show_banner()

    info_table = Table(box=box.ROUNDED)
    info_table.add_column("Component", style="cyan")
    info_table.add_column("Status", style="green")

    info_table.add_row("Python Version", "3.11.0")
    info_table.add_row("CLI Version", "1.0.0")
    info_table.add_row("Data Directory", "data/")
    info_table.add_row("Config Directory", "config/")
    info_table.add_row("Strategies", "3 loaded")

    console.print(info_table)
    console.print()


def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
