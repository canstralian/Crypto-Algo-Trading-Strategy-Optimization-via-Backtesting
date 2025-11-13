"""Logging configuration and utilities."""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

import structlog
import yaml

from .config import get_settings


def setup_logging(
    config_file: Optional[str] = None, log_level: Optional[str] = None
) -> None:
    """Setup logging configuration.

    Args:
        config_file: Path to logging config file
        log_level: Override log level
    """
    settings = get_settings()

    # Ensure log directory exists
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Load logging config from YAML if available
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        except Exception as e:
            print(f"Failed to load logging config: {e}", file=sys.stderr)
            _setup_basic_logging(log_level or settings.log_level)
    else:
        _setup_basic_logging(log_level or settings.log_level)

    # Setup structlog
    _setup_structlog()


def _setup_basic_logging(log_level: str = "INFO") -> None:
    """Setup basic logging configuration.

    Args:
        log_level: Logging level
    """
    settings = get_settings()

    # Create formatters
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, date_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # File handler
    log_file = Path(settings.log_dir) / "trading.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Error file handler
    error_file = Path(settings.log_dir) / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)


def _setup_structlog() -> None:
    """Setup structlog for structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capability to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)
