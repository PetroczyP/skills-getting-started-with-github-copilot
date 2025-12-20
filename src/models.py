"""Data models for the Mergington High School API.

This module defines Pydantic models for:
- Activities
- API requests and responses
- Internal data structures
"""

from typing import List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class SignupRequest(BaseModel):
    """Request model for signing up for an activity.
    
    Attributes:
        email (EmailStr): The student's email address.
    """
    email: EmailStr


class UnregisterRequest(BaseModel):
    """Request model for unregistering from an activity.
    
    Attributes:
        email (EmailStr): The student's email address.
    """
    email: EmailStr


class ActivityDetails(BaseModel):
    """Model for activity details.
    
    Attributes:
        description: Activity description
        schedule: Activity schedule
        max_participants: Maximum number of participants
        participants: List of participant emails
    """
    model_config = ConfigDict(frozen=False)
    
    description: str = Field(..., min_length=1)
    schedule: str = Field(..., min_length=1)
    max_participants: int = Field(..., gt=0)
    participants: List[str] = Field(default_factory=list)
    
    @property
    def available_spots(self) -> int:
        """Calculate available spots."""
        return self.max_participants - len(self.participants)
    
    @property
    def is_full(self) -> bool:
        """Check if activity is at capacity."""
        return len(self.participants) >= self.max_participants


class MessageResponse(BaseModel):
    """Standard message response model.
    
    Attributes:
        message: Response message
    """
    message: str
