"""Custom exceptions for the Mergington High School API.

This module defines custom exception classes for better error handling.
"""

from typing import Optional


class ActivityError(Exception):
    """Base exception for activity-related errors."""
    
    def __init__(self, message: str, activity_name: Optional[str] = None):
        self.message = message
        self.activity_name = activity_name
        super().__init__(self.message)


class ActivityNotFoundError(ActivityError):
    """Raised when an activity is not found."""
    pass


class ActivityCapacityError(ActivityError):
    """Raised when an activity has reached maximum capacity."""
    pass


class StudentRegistrationError(ActivityError):
    """Base exception for student registration errors."""
    
    def __init__(self, message: str, email: str, activity_name: Optional[str] = None):
        self.email = email
        super().__init__(message, activity_name)


class StudentAlreadyRegisteredError(StudentRegistrationError):
    """Raised when a student is already registered for an activity."""
    pass


class StudentNotRegisteredError(StudentRegistrationError):
    """Raised when a student is not registered for an activity."""
    pass
