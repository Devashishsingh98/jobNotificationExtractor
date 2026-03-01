"""Logging configuration for the application."""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Custom formatter with color for console
class ColoredFormatter(logging.Formatter):
    """Add colors to console logs."""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',   # Green
        'WARNING': '\033[33m', # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


def setup_logging(app_name: str = "job_notification_system"):
    """Configure application logging."""

    # Root logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    if logger.handlers:
        return logger

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # File handler for all logs
    log_file = logs_dir / f"{app_name}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Error file handler (errors only)
    error_file = logs_dir / f"{app_name}_errors.log"
    error_handler = logging.FileHandler(error_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


# Create default logger
logger = setup_logging()


def log_exception(exc: Exception, context: str = ""):
    """Log an exception with context."""
    logger.error(f"{context}: {type(exc).__name__}: {str(exc)}", exc_info=True)


def log_api_call(method: str, path: str, status_code: int, duration_ms: float):
    """Log an API call."""
    logger.info(f"{method} {path} - {status_code} ({duration_ms:.2f}ms)")
