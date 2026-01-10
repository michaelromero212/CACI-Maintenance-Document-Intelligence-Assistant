"""Logging configuration for MDIA backend."""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure and return the application logger.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("mdia")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a child logger for a specific module.
    
    Args:
        name: Module name (e.g., "api", "llm", "services")
    
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"mdia.{name}")
    return logging.getLogger("mdia")


# Initialize the root logger on import
logger = setup_logging()
