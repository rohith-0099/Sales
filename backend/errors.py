"""
Error handling utilities for consistent error responses and logging.
"""

import logging
from typing import Any, Tuple

from flask import jsonify


def create_error_response(
    success: bool,
    error: str,
    status_code: int = 500,
    additional_data: dict = None
) -> Tuple[dict, int]:
    """
    Create a standardized error response.
    
    Args:
        success: Boolean flag for success status
        error: Error message
        status_code: HTTP status code (default: 500)
        additional_data: Additional data to include in response
    
    Returns:
        Tuple of (jsonified response, status code)
    """
    response = {
        "success": success,
        "error": error,
    }
    
    if additional_data:
        response.update(additional_data)
    
    return jsonify(response), status_code


def handle_api_error(
    logger: logging.Logger,
    error: Exception,
    context: str = "",
    default_message: str = "An error occurred"
) -> Tuple[dict, int]:
    """
    Handle API errors with logging and consistent response format.
    
    Args:
        logger: Logger instance
        error: Exception instance
        context: Additional context for logging
        default_message: Default user-facing message
    
    Returns:
        Tuple of (jsonified response, status code)
    """
    error_msg = str(error)
    
    # Log the error with context
    if context:
        logger.error(f"{context}: {error_msg}")
    else:
        logger.error(f"API Error: {error_msg}")
    
    # Determine HTTP status code based on error type
    if isinstance(error, ValueError):
        status_code = 400
    elif isinstance(error, LookupError):
        status_code = 404
    elif isinstance(error, TypeError):
        status_code = 400
    else:
        status_code = 500
    
    return create_error_response(False, default_message, status_code)


def log_warning(
    logger: logging.Logger,
    message: str,
    context: str = "",
    error: Exception = None
):
    """
    Log a warning with optional error context.
    
    Args:
        logger: Logger instance
        message: Warning message
        context: Additional context
        error: Optional exception instance
    """
    if context:
        if error:
            logger.warning(f"{context}: {message} - {str(error)}")
        else:
            logger.warning(f"{context}: {message}")
    else:
        if error:
            logger.warning(f"{message} - {str(error)}")
        else:
            logger.warning(message)
