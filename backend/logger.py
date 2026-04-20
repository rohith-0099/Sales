"""
Logging utility module for structured logging throughout the application.
Replaces ad-hoc print statements with proper logging framework.
"""

import logging
import sys

# Create logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# Add handler to logger
if not logger.handlers:
    logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)


if __name__ == "__main__":
    test_logger = get_logger(__name__)
    test_logger.info("Logger initialized successfully")
    test_logger.warning("This is a test warning")
    test_logger.error("This is a test error")
