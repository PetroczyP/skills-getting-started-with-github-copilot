"""Validation functions for activity management.

This module provides validation functions for:
- Activity existence
- Capacity checking
- Student registration status
- Activity name translation
"""

from typing import Dict, Any, Tuple
from fastapi import HTTPException

from src.constants import (
    HTTP_NOT_FOUND,
    HTTP_BAD_REQUEST,
    MSG_ACTIVITY_NOT_FOUND,
    MSG_STUDENT_ALREADY_REGISTERED,
    MSG_STUDENT_NOT_REGISTERED,
    SupportedLanguage
)


def validate_and_translate_activity_name(
    activity_name: str,
    lang: str,
    activity_name_mapping_reverse: Dict[str, str],
    activities_en: Dict[str, Dict[str, Any]]
) -> str:
    """Validate activity exists and translate name to English if needed.
    
    Args:
        activity_name: Activity name in the specified language
        lang: Language code ("en" or "hu")
        activity_name_mapping_reverse: Hungarian to English name mapping
        activities_en: English activities dictionary
        
    Returns:
        str: English activity name
        
    Raises:
        HTTPException: 404 if activity not found
    """
    en_activity_name = activity_name
    
    if lang == SupportedLanguage.HUNGARIAN.value and activity_name in activity_name_mapping_reverse:
        en_activity_name = activity_name_mapping_reverse[activity_name]
    elif lang == SupportedLanguage.ENGLISH.value and activity_name not in activities_en:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail=MSG_ACTIVITY_NOT_FOUND)
    
    # Final validation that activity exists in storage
    if en_activity_name not in activities_en:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail=MSG_ACTIVITY_NOT_FOUND)
    
    return en_activity_name


def validate_student_not_registered(
    email: str,
    activity_name: str,
    participants_storage: Dict[str, list]
) -> None:
    """Validate that student is not already registered for activity.
    
    Args:
        email: Student email address
        activity_name: English activity name
        participants_storage: Participant storage dictionary
        
    Raises:
        HTTPException: 400 if student already registered
    """
    if email in participants_storage[activity_name]:
        raise HTTPException(
            status_code=HTTP_BAD_REQUEST,
            detail=MSG_STUDENT_ALREADY_REGISTERED
        )


def validate_student_registered(
    email: str,
    activity_name: str,
    participants_storage: Dict[str, list]
) -> None:
    """Validate that student is registered for activity.
    
    Args:
        email: Student email address
        activity_name: English activity name
        participants_storage: Participant storage dictionary
        
    Raises:
        HTTPException: 400 if student not registered
    """
    if email not in participants_storage[activity_name]:
        raise HTTPException(
            status_code=HTTP_BAD_REQUEST,
            detail=MSG_STUDENT_NOT_REGISTERED
        )


def validate_capacity_available(
    activity_name: str,
    activity: Dict[str, Any],
    participants_storage: Dict[str, list],
    localized_message: str
) -> None:
    """Validate that activity has capacity for new participants.
    
    Args:
        activity_name: English activity name
        activity: Activity details dictionary
        participants_storage: Participant storage dictionary
        localized_message: Localized error message for full capacity
        
    Raises:
        HTTPException: 400 if activity at capacity
    """
    current_participants = len(participants_storage[activity_name])
    max_participants = activity["max_participants"]
    
    if current_participants >= max_participants:
        raise HTTPException(
            status_code=HTTP_BAD_REQUEST,
            detail=localized_message
        )
