"""
Input validation utilities for API requests.
"""

from typing import Any, Callable, Optional


def validate_required_fields(data: dict, required_fields: list[str]) -> Optional[str]:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
    
    Returns:
        Error message if validation fails, None if successful
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    
    return None


def validate_non_negative(value: Any, field_name: str) -> Optional[str]:
    """
    Validate that a value is non-negative.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
    
    Returns:
        Error message if validation fails, None if successful
    """
    try:
        num_value = float(value)
        if num_value < 0:
            return f"{field_name} must be non-negative"
    except (ValueError, TypeError):
        return f"{field_name} must be a number"
    
    return None


def validate_positive(value: Any, field_name: str) -> Optional[str]:
    """
    Validate that a value is positive.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
    
    Returns:
        Error message if validation fails, None if successful
    """
    try:
        num_value = float(value)
        if num_value <= 0:
            return f"{field_name} must be positive"
    except (ValueError, TypeError):
        return f"{field_name} must be a number"
    
    return None


def validate_in_choices(value: str, choices: list[str], field_name: str) -> Optional[str]:
    """
    Validate that a value is in a list of allowed choices.
    
    Args:
        value: Value to validate
        choices: List of allowed values
        field_name: Name of the field for error messages
    
    Returns:
        Error message if validation fails, None if successful
    """
    if value not in choices:
        return f"{field_name} must be one of: {', '.join(choices)}"
    
    return None


def validate_request_json(data: Any) -> Optional[str]:
    """
    Validate that request data is a dictionary.
    
    Args:
        data: Data to validate
    
    Returns:
        Error message if validation fails, None if successful
    """
    if not isinstance(data, dict):
        return "Request body must be valid JSON with key-value pairs"
    
    return None
