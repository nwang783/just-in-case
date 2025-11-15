"""
Logging utilities using Loguru for structured, colorful logging.
"""

import sys
from loguru import logger
from typing import Optional


def setup_logger(log_level: str = "INFO", environment: str = "development") -> None:
    """
    Configure the application logger with appropriate settings.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment name (development, staging, production)
    """
    # Remove default logger
    logger.remove()

    # Development: Colorful, detailed logs to stderr
    if environment.lower() == "development":
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True,
        )
    # Production: JSON-formatted logs for better parsing
    else:
        logger.add(
            sys.stderr,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            serialize=False,  # Set to True for JSON output
        )

    # Optional: Add file logging for production
    if environment.lower() == "production":
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            rotation="500 MB",
            retention="10 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        )

    logger.info(f"Logger initialized with level: {log_level}, environment: {environment}")


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance.

    Args:
        name: Optional name for the logger (typically __name__)

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger
