"""
Utility functions for datetime handling with timezone support
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """
    Return current UTC datetime with timezone info.
    This replaces the deprecated datetime.utcnow() function.
    """
    return datetime.now(timezone.utc)