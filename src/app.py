"""High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

This module provides REST API endpoints for:
    - Viewing available extracurricular activities
    - Signing up for activities
    - Unregistering from activities

The application uses an in-memory database for activity storage.
"""

from typing import Dict, List, Any
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr

from src.constants import (
    SupportedLanguage,
    DEFAULT_LANGUAGE,
    HTTP_NOT_FOUND,
    MSG_ACTIVITY_NOT_FOUND
)
from src.validators import (
    validate_and_translate_activity_name,
    validate_student_not_registered,
    validate_student_registered,
    validate_capacity_available
)


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


app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities"
)

# Mount the static files directory for serving HTML, CSS, and JavaScript files
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(current_dir, "static")),
    name="static"
)

# Translation dictionaries for activities
# English activities data
activities_en: Dict[str, Dict[str, Any]] = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": []
    },
    "Soccer Team": {
        "description": "Join the varsity soccer team for practices and competitive matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Swimming Club": {
        "description": "Swimming lessons and training for all skill levels",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Drama Club": {
        "description": "Perform in plays and learn acting techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": []
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and sculpture",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking skills through competitive debates",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Olympiad": {
        "description": "Compete in science competitions and conduct experiments",
        "schedule": "Fridays, 3:00 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    }
}

# Hungarian activities data
activities_hu: Dict[str, Dict[str, Any]] = {
    "Sakk Klub": {
        "description": "Tanulj stratégiákat és versenyezz sakk tornákon",
        "schedule": "Péntek, 15:30 - 17:00",
        "max_participants": 12,
        "participants": []
    },
    "Programozás Tanfolyam": {
        "description": "Tanuld meg a programozás alapjait és készíts szoftverprojekteket",
        "schedule": "Kedd és Csütörtök, 15:30 - 16:30",
        "max_participants": 20,
        "participants": []
    },
    "Tornaterem": {
        "description": "Testnevelés és sportolási lehetőségek",
        "schedule": "Hétfő, Szerda, Péntek, 14:00 - 15:00",
        "max_participants": 30,
        "participants": []
    },
    "Focicsapat": {
        "description": "Csatlakozz az iskolai foci csapathoz edzésekre és versenyekre",
        "schedule": "Hétfő és Szerda, 16:00 - 18:00",
        "max_participants": 22,
        "participants": []
    },
    "Úszó Klub": {
        "description": "Úszásoktatás és edzés minden szinten",
        "schedule": "Kedd és Csütörtök, 16:00 - 17:30",
        "max_participants": 15,
        "participants": []
    },
    "Drámakör": {
        "description": "Szerepelj színdarabokban és tanulj színészeti technikákat",
        "schedule": "Szerda, 15:30 - 17:30",
        "max_participants": 25,
        "participants": []
    },
    "Művészeti Stúdió": {
        "description": "Fedezd fel a festést, rajzolást és szobrászatot",
        "schedule": "Csütörtök, 15:30 - 17:00",
        "max_participants": 18,
        "participants": []
    },
    "Vitakör": {
        "description": "Fejleszd kritikus gondolkodásodat és nyilvános beszédkészségedet versenyszerű vitákon keresztül",
        "schedule": "Kedd, 16:00 - 17:30",
        "max_participants": 16,
        "participants": []
    },
    "Tudományos Olimpia": {
        "description": "Versenyezz tudományos versenyek és kísérletek során",
        "schedule": "Péntek, 15:00 - 17:00",
        "max_participants": 20,
        "participants": []
    }
}

# Activity name mappings (English -> Hungarian)
activity_name_mapping = {
    "Chess Club": "Sakk Klub",
    "Programming Class": "Programozás Tanfolyam",
    "Gym Class": "Tornaterem",
    "Soccer Team": "Focicsapat",
    "Swimming Club": "Úszó Klub",
    "Drama Club": "Drámakör",
    "Art Studio": "Művészeti Stúdió",
    "Debate Team": "Vitakör",
    "Science Olympiad": "Tudományos Olimpia"
}

# Reverse mapping (Hungarian -> English)
activity_name_mapping_reverse = {v: k for k, v in activity_name_mapping.items()}

# User-facing message translations
messages = {
    "en": {
        "signed_up": "Signed up {email} for {activity}",
        "unregistered": "Unregistered {email} from {activity}",
        "activity_full": "Activity is full"
    },
    "hu": {
        "signed_up": "{email} sikeresen jelentkezett: {activity}",
        "unregistered": "{email} sikeresen kijelentkezve: {activity}",
        "activity_full": "A tevékenység megtelt"
    }
}

# Shared participants list across languages
# This ensures participants are synced between English and Hungarian versions
participants_storage: Dict[str, List[str]] = {
    "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
    "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
    "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
    "Soccer Team": ["alex@mergington.edu", "sarah@mergington.edu"],
    "Swimming Club": ["ryan@mergington.edu"],
    "Drama Club": ["lily@mergington.edu", "james@mergington.edu"],
    "Art Studio": ["ava@mergington.edu"],
    "Debate Team": ["noah@mergington.edu", "mia@mergington.edu"],
    "Science Olympiad": ["ethan@mergington.edu", "isabella@mergington.edu"]
}


def get_activities_by_language(lang: str = "en") -> Dict[str, Dict[str, Any]]:
    """Get activities with participants in the specified language.
    
    Args:
        lang: Language code ("en" or "hu")
        
    Returns:
        Dictionary of activities with current participants
    """
    # Select the appropriate activities dictionary
    if lang == "hu":
        activities_dict = activities_hu.copy()
    else:
        activities_dict = activities_en.copy()
    
    # Get English activity keys for participant lookup
    if lang == "hu":
        # For Hungarian, we need to map back to English keys
        for hu_name, activity_data in activities_dict.items():
            en_name = activity_name_mapping_reverse.get(hu_name, hu_name)
            activity_data["participants"] = participants_storage.get(en_name, [])
    else:
        # For English, direct mapping
        for en_name, activity_data in activities_dict.items():
            activity_data["participants"] = participants_storage.get(en_name, [])
    
    return activities_dict


@app.get("/")
def root() -> RedirectResponse:
    """Redirect root URL to the static index page.
    
    Returns:
        RedirectResponse: A redirect response to the static index.html page.
    """
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(
    lang: str = Query(DEFAULT_LANGUAGE, pattern=f"^({SupportedLanguage.ENGLISH.value}|{SupportedLanguage.HUNGARIAN.value})$")
) -> Dict[str, Dict[str, Any]]:
    """Retrieve all available extracurricular activities in the specified language.
    
    Args:
        lang: Language code - "en" for English or "hu" for Hungarian (default: "en")
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary of all activities with their details,
            including description, schedule, max_participants, and current participants.
    
    Example:
        GET /activities?lang=en
        GET /activities?lang=hu
    """
    return get_activities_by_language(lang)


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    request: SignupRequest,
    lang: str = Query(DEFAULT_LANGUAGE, pattern=f"^({SupportedLanguage.ENGLISH.value}|{SupportedLanguage.HUNGARIAN.value})$")
) -> Dict[str, str]:
    """Sign up a student for an extracurricular activity.
    
    Args:
        activity_name (str): The name of the activity to sign up for (in the specified language).
        request (SignupRequest): Request body containing the student's email address.
        lang (str): Language code for response messages ("en" or "hu").
    
    Returns:
        Dict[str, str]: A success message confirming the signup in the specified language.
    
    Raises:
        HTTPException: 404 if the activity does not exist.
        HTTPException: 400 if the student is already signed up for the activity.
        HTTPException: 422 if the email format is invalid.
    
    Example:
        POST /activities/Chess%20Club/signup?lang=en
        Body: {"email": "student@mergington.edu"}
        
        POST /activities/Sakk%20Klub/signup?lang=hu
        Body: {"email": "student@mergington.edu"}
    """
    email = request.email
    
    # Validate and translate activity name to English
    en_activity_name = validate_and_translate_activity_name(
        activity_name, lang, activity_name_mapping_reverse, activities_en
    )
    
    # Validate activity exists in participant storage
    if en_activity_name not in participants_storage:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail=MSG_ACTIVITY_NOT_FOUND)
    
    # Get activity details
    activities_dict = get_activities_by_language(SupportedLanguage.ENGLISH.value)
    if en_activity_name not in activities_dict:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail=MSG_ACTIVITY_NOT_FOUND)
    
    activity = activities_dict[en_activity_name]
    
    # Validate student is not already signed up
    validate_student_not_registered(email, en_activity_name, participants_storage)

    # Validate activity has not reached maximum capacity
    validate_capacity_available(
        en_activity_name, activity, participants_storage, messages[lang]["activity_full"]
    )
    
    # Add student to the activity's participant list
    participants_storage[en_activity_name].append(email)
    
    # Return localized message
    return {"message": messages[lang]["signed_up"].format(email=email, activity=activity_name)}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    request: UnregisterRequest,
    lang: str = Query(DEFAULT_LANGUAGE, pattern=f"^({SupportedLanguage.ENGLISH.value}|{SupportedLanguage.HUNGARIAN.value})$")
) -> Dict[str, str]:
    """Unregister a student from an extracurricular activity.
    
    Args:
        activity_name (str): The name of the activity to unregister from (in the specified language).
        request (UnregisterRequest): Request body containing the student's email address.
        lang (str): Language code for response messages ("en" or "hu").
    
    Returns:
        Dict[str, str]: A success message confirming the unregistration in the specified language.
    
    Raises:
        HTTPException: 404 if the activity does not exist.
        HTTPException: 400 if the student is not signed up for the activity.
        HTTPException: 422 if the email format is invalid.
    
    Example:
        DELETE /activities/Chess%20Club/unregister?lang=en
        Body: {"email": "student@mergington.edu"}
        
        DELETE /activities/Sakk%20Klub/unregister?lang=hu
        Body: {"email": "student@mergington.edu"}
    """
    email = request.email
    
    # Validate and translate activity name to English
    en_activity_name = validate_and_translate_activity_name(
        activity_name, lang, activity_name_mapping_reverse, activities_en
    )
    
    # Validate activity exists
    if en_activity_name not in participants_storage:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail=MSG_ACTIVITY_NOT_FOUND)

    # Validate student is signed up for the activity
    validate_student_registered(email, en_activity_name, participants_storage)

    # Remove student from the activity's participant list
    participants_storage[en_activity_name].remove(email)
    
    # Return localized message
    return {"message": messages[lang]["unregistered"].format(email=email, activity=activity_name)}
