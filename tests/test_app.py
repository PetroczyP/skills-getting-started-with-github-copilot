"""
Tests for the Mergington High School API

This module contains pytest tests for all FastAPI endpoints including:
- Root endpoint redirection
- Activity listing
- Student signup
- Student unregistration
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
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
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_returns_participant_lists(self, client):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_existing_activity(self, client):
        """Test signing up for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            json={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            json={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_when_already_registered(self, client):
        """Test signing up when already registered for the activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            json={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"

    def test_multiple_students_can_signup(self, client):
        """Test that multiple students can sign up for the same activity"""
        # First student
        response1 = client.post(
            "/activities/Programming Class/signup",
            json={"email": "student1@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second student
        response2 = client.post(
            "/activities/Programming Class/signup",
            json={"email": "student2@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both students are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Programming Class"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants

    def test_signup_with_invalid_email(self, client):
        """Test signing up with an invalid email format"""
        response = client.post(
            "/activities/Chess Club/signup",
            json={"email": "not-an-email"}
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity(self, client):
        """Test unregistering from an activity"""
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister",
            json={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.request(
            "DELETE",
            "/activities/Nonexistent Club/unregister",
            json={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_when_not_registered(self, client):
        """Test unregistering when not registered for the activity"""
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister",
            json={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"

    def test_unregister_with_invalid_email(self, client):
        """Test unregistering with an invalid email format"""
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister",
            json={"email": "not-an-email"}
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_unregister_then_signup_again(self, client):
        """Test that a student can unregister and then sign up again"""
        # Unregister
        response1 = client.request(
            "DELETE",
            "/activities/Gym Class/unregister",
            json={"email": "john@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Gym Class/signup",
            json={"email": "john@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify the student is registered again
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "john@mergington.edu" in activities_data["Gym Class"]["participants"]
