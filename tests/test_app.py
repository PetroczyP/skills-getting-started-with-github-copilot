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
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
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
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_when_already_registered(self, client):
        """Test signing up when already registered for the activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"

    def test_multiple_students_can_signup(self, client):
        """Test that multiple students can sign up for the same activity"""
        # First student
        response1 = client.post(
            "/activities/Programming Class/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second student
        response2 = client.post(
            "/activities/Programming Class/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both students are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Programming Class"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants

    def test_signup_rejected_when_activity_at_capacity(self, client):
        """Test that signup is rejected when activity has reached max_participants"""
        # Chess Club has max_participants=12 and starts with 2 participants
        # Add 10 more students to fill it to capacity
        for i in range(10):
            response = client.post(
                f"/activities/Chess Club/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Verify activity is now at capacity (12 participants)
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Chess Club"]["participants"]) == 12
        
        # Try to add one more student - should fail
        response = client.post(
            "/activities/Chess Club/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Activity is full"
        
        # Verify student was not added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "overflow@mergington.edu" not in activities_data["Chess Club"]["participants"]
        assert len(activities_data["Chess Club"]["participants"]) == 12

    def test_signup_allowed_when_one_below_capacity(self, client):
        """Test that signup is allowed when activity is one below capacity"""
        # Chess Club has max_participants=12 and starts with 2 participants
        # Add 9 students (total 11, one below capacity)
        for i in range(9):
            response = client.post(
                f"/activities/Chess Club/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Verify activity is one below capacity (11 participants)
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Chess Club"]["participants"]) == 11
        
        # Add the last student - should succeed
        response = client.post(
            "/activities/Chess Club/signup?email=laststudent@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify student was added and activity is now at capacity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "laststudent@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert len(activities_data["Chess Club"]["participants"]) == 12

    def test_capacity_check_with_sequential_signups(self, client):
        """Test that capacity checking works correctly with multiple sequential signups"""
        # Use Programming Class which has max_participants=20 and starts with 2 participants
        initial_count = 2
        max_participants = 20
        slots_available = max_participants - initial_count
        
        # Fill all available slots
        for i in range(slots_available):
            response = client.post(
                f"/activities/Programming Class/signup?email=programmer{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Verify activity is at capacity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Programming Class"]["participants"]) == max_participants
        
        # Try to add more students - all should fail
        for i in range(3):
            response = client.post(
                f"/activities/Programming Class/signup?email=extra{i}@mergington.edu"
            )
            assert response.status_code == 400
            assert response.json()["detail"] == "Activity is full"


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity(self, client):
        """Test unregistering from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
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
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_when_not_registered(self, client):
        """Test unregistering when not registered for the activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"

    def test_unregister_then_signup_again(self, client):
        """Test that a student can unregister and then sign up again"""
        # Unregister
        response1 = client.delete(
            "/activities/Gym Class/unregister?email=john@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Gym Class/signup?email=john@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify the student is registered again
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "john@mergington.edu" in activities_data["Gym Class"]["participants"]
