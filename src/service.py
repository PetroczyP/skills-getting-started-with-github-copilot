"""Service layer for activity management.

This module encapsulates business logic for:
- Activity management
- Student registration
- Language translation
"""

from typing import Dict, Any, List
from src.models import ActivityDetails
from src.exceptions import (
    ActivityNotFoundError,
    ActivityCapacityError,
    StudentAlreadyRegisteredError,
    StudentNotRegisteredError
)


class ActivityService:
    """Service class for managing activities and registrations."""
    
    def __init__(
        self,
        activities_en: Dict[str, Dict[str, Any]],
        activities_hu: Dict[str, Dict[str, Any]],
        activity_name_mapping: Dict[str, str],
        activity_name_mapping_reverse: Dict[str, str],
        participants_storage: Dict[str, List[str]]
    ):
        """Initialize the activity service.
        
        Args:
            activities_en: English activities dictionary
            activities_hu: Hungarian activities dictionary
            activity_name_mapping: English to Hungarian name mapping
            activity_name_mapping_reverse: Hungarian to English name mapping
            participants_storage: Shared participants storage
        """
        self.activities_en = activities_en
        self.activities_hu = activities_hu
        self.activity_name_mapping = activity_name_mapping
        self.activity_name_mapping_reverse = activity_name_mapping_reverse
        self.participants_storage = participants_storage
    
    def translate_activity_name(self, activity_name: str, lang: str) -> str:
        """Validate and normalize activity name to English for internal use.
        
        Translates Hungarian activity names to English when lang='hu', otherwise
        validates that the provided name exists in the English activity dictionary.
        
        Args:
            activity_name: Activity name in specified language
            lang: Language code ('en' or 'hu')
            
        Returns:
            Validated English activity name (translated from Hungarian if necessary,
            or the same as input if already a valid English name)
            
        Raises:
            ActivityNotFoundError: If activity doesn't exist in either language
        """
        if lang == "hu":
            if activity_name in self.activity_name_mapping_reverse:
                return self.activity_name_mapping_reverse[activity_name]
        
        # Verify activity exists in English dictionary
        if activity_name not in self.activities_en:
            raise ActivityNotFoundError("Activity not found", activity_name)
        
        return activity_name
    
    def get_activity_details(self, activity_name: str, lang: str) -> ActivityDetails:
        """Get activity details with current participants.
        
        Args:
            activity_name: Activity name in specified language
            lang: Language code
            
        Returns:
            ActivityDetails object
            
        Raises:
            ActivityNotFoundError: If activity doesn't exist
        """
        en_name = self.translate_activity_name(activity_name, lang)
        
        # Validate activity exists in participant storage for consistency
        if en_name not in self.participants_storage:
            raise ActivityNotFoundError("Activity not found", activity_name)
        
        activity_data = self.activities_en[en_name].copy()
        activity_data["participants"] = self.participants_storage[en_name]
        
        return ActivityDetails(**activity_data)
    
    def get_all_activities(self, lang: str = "en") -> Dict[str, Dict[str, Any]]:
        """Get all activities with participants in specified language.
        
        Args:
            lang: Language code
            
        Returns:
            Dictionary of activities with current participants
        """
        activities_dict = (
            self.activities_hu.copy() if lang == "hu"
            else self.activities_en.copy()
        )
        
        # Populate with current participants
        for name, activity_data in activities_dict.items():
            en_name = (
                self.activity_name_mapping_reverse.get(name, name)
                if lang == "hu"
                else name
            )
            activity_data["participants"] = self.participants_storage.get(en_name, [])
        
        return activities_dict
    
    def signup_student(self, activity_name: str, email: str, lang: str) -> str:
        """Sign up a student for an activity.
        
        Args:
            activity_name: Activity name in specified language
            email: Student email address
            lang: Language code
            
        Returns:
            English activity name
            
        Raises:
            ActivityNotFoundError: If activity doesn't exist
            StudentAlreadyRegisteredError: If student already registered
            ActivityCapacityError: If activity is full
        """
        en_name = self.translate_activity_name(activity_name, lang)
        
        # Validate activity exists in participant storage
        if en_name not in self.participants_storage:
            raise ActivityNotFoundError("Activity not found", activity_name)
        
        # Check if student already registered
        if email in self.participants_storage[en_name]:
            raise StudentAlreadyRegisteredError(
                "Student already signed up for this activity",
                email,
                activity_name
            )
        
        # Check capacity
        activity_details = self.get_activity_details(en_name, "en")
        if activity_details.is_full:
            raise ActivityCapacityError("Activity is full", activity_name)
        
        # Add student
        self.participants_storage[en_name].append(email)
        
        return en_name
    
    def unregister_student(self, activity_name: str, email: str, lang: str) -> str:
        """Unregister a student from an activity.
        
        Args:
            activity_name: Activity name in specified language
            email: Student email address
            lang: Language code
            
        Returns:
            English activity name
            
        Raises:
            ActivityNotFoundError: If activity doesn't exist
            StudentNotRegisteredError: If student not registered
        """
        en_name = self.translate_activity_name(activity_name, lang)
        
        # Validate activity exists
        if en_name not in self.participants_storage:
            raise ActivityNotFoundError("Activity not found", activity_name)
        
        # Check if student is registered
        if email not in self.participants_storage[en_name]:
            raise StudentNotRegisteredError(
                "Student is not signed up for this activity",
                email,
                activity_name
            )
        
        # Remove student
        self.participants_storage[en_name].remove(email)
        
        return en_name
