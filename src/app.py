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

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .constants import (
    SupportedLanguage,
    DEFAULT_LANGUAGE,
    HTTP_NOT_FOUND,
    HTTP_BAD_REQUEST,
)
from .models import SignupRequest, UnregisterRequest, MessageResponse
from .service import ActivityService
from .exceptions import (
    ActivityNotFoundError,
    ActivityCapacityError,
    StudentAlreadyRegisteredError,
    StudentNotRegisteredError,
)


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


# Initialize the activity service
def get_activity_service() -> ActivityService:
    """Dependency injection for ActivityService.
    
    Returns:
        ActivityService: Configured activity service instance
    """
    return ActivityService(
        activities_en=activities_en,
        activities_hu=activities_hu,
        activity_name_mapping=activity_name_mapping,
        activity_name_mapping_reverse=activity_name_mapping_reverse,
        participants_storage=participants_storage
    )


@app.get("/")
def root() -> RedirectResponse:
    """Redirect root URL to the static index page.
    
    Returns:
        RedirectResponse: A redirect response to the static index.html page.
    """
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(
    lang: str = Query(DEFAULT_LANGUAGE, pattern=f"^({SupportedLanguage.ENGLISH.value}|{SupportedLanguage.HUNGARIAN.value})$"),
    service: ActivityService = Depends(get_activity_service)
) -> Dict[str, Dict[str, Any]]:
    """Retrieve all available extracurricular activities in the specified language.
    
    Args:
        lang: Language code - "en" for English or "hu" for Hungarian (default: "en")
        service: Injected activity service
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary of all activities with their details,
            including description, schedule, max_participants, and current participants.
    
    Example:
        GET /activities?lang=en
        GET /activities?lang=hu
    """
    return service.get_all_activities(lang)


@app.post("/activities/{activity_name}/signup", response_model=MessageResponse)
def signup_for_activity(
    activity_name: str,
    request: SignupRequest,
    lang: str = Query(DEFAULT_LANGUAGE, pattern=f"^({SupportedLanguage.ENGLISH.value}|{SupportedLanguage.HUNGARIAN.value})$"),
    service: ActivityService = Depends(get_activity_service)
) -> MessageResponse:
    """Sign up a student for an extracurricular activity.
    
    Args:
        activity_name (str): The name of the activity to sign up for (in the specified language).
        request (SignupRequest): Request body containing the student's email address.
        lang (str): Language code for response messages ("en" or "hu").
        service: Injected activity service
    
    Returns:
        MessageResponse: A success message confirming the signup in the specified language.
    
    Raises:
        HTTPException: 404 if the activity does not exist.
        HTTPException: 400 if the student is already signed up for the activity.
        HTTPException: 400 if the activity is at capacity.
        HTTPException: 422 if the email format is invalid.
    
    Example:
        POST /activities/Chess%20Club/signup?lang=en
        Body: {"email": "student@mergington.edu"}
        
        POST /activities/Sakk%20Klub/signup?lang=hu
        Body: {"email": "student@mergington.edu"}
    """
    try:
        service.signup_student(activity_name, request.email, lang)
        message = messages[lang]["signed_up"].format(email=request.email, activity=activity_name)
        return MessageResponse(message=message)
    except ActivityNotFoundError:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail="Activity not found")
    except StudentAlreadyRegisteredError:
        raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="Student already signed up for this activity")
    except ActivityCapacityError:
        raise HTTPException(status_code=HTTP_BAD_REQUEST, detail=messages[lang]["activity_full"])


@app.delete("/activities/{activity_name}/unregister", response_model=MessageResponse)
def unregister_from_activity(
    activity_name: str,
    request: UnregisterRequest,
    lang: str = Query(DEFAULT_LANGUAGE, pattern=f"^({SupportedLanguage.ENGLISH.value}|{SupportedLanguage.HUNGARIAN.value})$"),
    service: ActivityService = Depends(get_activity_service)
) -> MessageResponse:
    """Unregister a student from an extracurricular activity.
    
    Args:
        activity_name (str): The name of the activity to unregister from (in the specified language).
        request (UnregisterRequest): Request body containing the student's email address.
        lang (str): Language code for response messages ("en" or "hu").
        service: Injected activity service
    
    Returns:
        MessageResponse: A success message confirming the unregistration in the specified language.
    
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
    try:
        service.unregister_student(activity_name, request.email, lang)
        message = messages[lang]["unregistered"].format(email=request.email, activity=activity_name)
        return MessageResponse(message=message)
    except ActivityNotFoundError:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail="Activity not found")
    except StudentNotRegisteredError:
        raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="Student is not signed up for this activity")
