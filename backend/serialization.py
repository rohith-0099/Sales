"""
Data serialization utilities for safe JSON handling.
"""

import json
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class SafeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles pandas/numpy types safely."""
    
    def default(self, obj: Any) -> Any:
        """Convert non-serializable objects to serializable types."""
        # Pandas types
        if isinstance(obj, (pd.Series, pd.Index)):
            return obj.tolist()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict("records")
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Nat.__class__):
            return None
        
        # NumPy types
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        
        # Python standard types
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        
        # Fallback
        try:
            return super().default(obj)
        except TypeError:
            logger.warning(f"Could not serialize object of type {type(obj).__name__}")
            return str(obj)


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize object to JSON string.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments to json.dumps()
    
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, cls=SafeJSONEncoder, **kwargs)
    except Exception as e:
        logger.error(f"JSON serialization failed: {str(e)}")
        raise


def safe_convert_to_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Float value or default
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, (float, int)):
            return float(value)
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        if isinstance(value, str):
            return float(value)
        return default
    except (ValueError, TypeError):
        return default


def safe_convert_to_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Integer value or default
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, (np.integer, np.floating)):
            return int(value)
        if isinstance(value, str):
            return int(float(value))
        return default
    except (ValueError, TypeError):
        return default
