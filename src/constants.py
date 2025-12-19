"""Application constants and configuration.

This module defines constants used throughout the application including:
- Supported languages
- Default values
- HTTP status codes
- Error messages
"""

from enum import Enum
from typing import Final


class SupportedLanguage(str, Enum):
    """Supported languages for the application."""
    ENGLISH: str = "en"
    HUNGARIAN: str = "hu"


# Default language
DEFAULT_LANGUAGE: Final[str] = SupportedLanguage.ENGLISH.value

# HTTP Status Codes (for clarity)
HTTP_OK: Final[int] = 200
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_NOT_FOUND: Final[int] = 404
HTTP_UNPROCESSABLE_ENTITY: Final[int] = 422

# Activity validation messages (language-agnostic keys)
MSG_ACTIVITY_NOT_FOUND: Final[str] = "Activity not found"
MSG_STUDENT_ALREADY_REGISTERED: Final[str] = "Student already signed up for this activity"
MSG_STUDENT_NOT_REGISTERED: Final[str] = "Student is not signed up for this activity"

# Rate limiting (future use)
RATE_LIMIT_PER_MINUTE: Final[int] = 60
RATE_LIMIT_PER_HOUR: Final[int] = 1000
