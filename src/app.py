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

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities"
)

# Mount the static files directory for serving HTML, CSS, and JavaScript files
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static"
)

# In-memory activity database
# Structure: Dict[activity_name, Dict[str, Any]]
# Each activity contains: description, schedule, max_participants, and participants list
activities: Dict[str, Dict[str, Any]] = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the varsity soccer team for practices and competitive matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Swimming lessons and training for all skill levels",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["ryan@mergington.edu"]
    },
    "Drama Club": {
        "description": "Perform in plays and learn acting techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["lily@mergington.edu", "james@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and sculpture",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["ava@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking skills through competitive debates",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu", "mia@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Compete in science competitions and conduct experiments",
        "schedule": "Fridays, 3:00 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["ethan@mergington.edu", "isabella@mergington.edu"]
    }
}


@app.get("/")
def root() -> RedirectResponse:
    """Redirect root URL to the static index page.
    
    Returns:
        RedirectResponse: A redirect response to the static index.html page.
    """
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities() -> Dict[str, Dict[str, Any]]:
    """Retrieve all available extracurricular activities.
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary of all activities with their details,
            including description, schedule, max_participants, and current participants.
    
    Example:
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            ...
        }
    """
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str) -> Dict[str, str]:
    """Sign up a student for an extracurricular activity.
    
    Args:
        activity_name (str): The name of the activity to sign up for.
        email (str): The student's email address (must end with @mergington.edu).
    
    Returns:
        Dict[str, str]: A success message confirming the signup.
    
    Raises:
        HTTPException: 404 if the activity does not exist.
        HTTPException: 400 if the student is already signed up for the activity.
    
    Example:
        POST /activities/Chess%20Club/signup?email=student@mergington.edu
        Response: {"message": "Signed up student@mergington.edu for Chess Club"}
    """
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student already signed up for this activity"
        )

    # Add student to the activity's participant list
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str) -> Dict[str, str]:
    """Unregister a student from an extracurricular activity.
    
    Args:
        activity_name (str): The name of the activity to unregister from.
        email (str): The student's email address.
    
    Returns:
        Dict[str, str]: A success message confirming the unregistration.
    
    Raises:
        HTTPException: 404 if the activity does not exist.
        HTTPException: 400 if the student is not signed up for the activity.
    
    Example:
        DELETE /activities/Chess%20Club/unregister?email=student@mergington.edu
        Response: {"message": "Unregistered student@mergington.edu from Chess Club"}
    """
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up for the activity
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student from the activity's participant list
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}