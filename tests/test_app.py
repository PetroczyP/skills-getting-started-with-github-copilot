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
    
    # Number of overflow attempts to test capacity enforcement
    OVERFLOW_TEST_COUNT = 3

    def _get_activity_info(self, client, activity_name):
        """Helper method to fetch activity information from API.
        
        Note: Relies on the reset_activities fixture to ensure consistent state.
        """
        return client.get("/activities").json()[activity_name]

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

    def test_signup_rejected_when_activity_at_capacity(self, client):
        """Test that signup is rejected when activity has reached max_participants.
        
        Note: This test relies on the reset_activities fixture for consistent initial state.
        """
        activity_name = "Chess Club"
        activity = self._get_activity_info(client, activity_name)
        
        initial_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        slots_available = max_participants - initial_count
        
        # Guard against edge case where activity is already at capacity
        assert slots_available > 0, \
            f"{activity_name} is already at capacity in fixture"
        
        # Fill all available slots with test-specific email pattern
        for i in range(slots_available):
            response = client.post(
                f"/activities/{activity_name}/signup",
                json={"email": f"capacity_test_{i}@mergington.edu"}
            )
            assert response.status_code == 200, \
                f"Failed to sign up capacity_test_{i} (signup {i+1}/{slots_available})"
        
        # Verify activity is now at capacity
        activity = self._get_activity_info(client, activity_name)
        current_count = len(activity["participants"])
        assert current_count == max_participants, \
            f"Expected {max_participants} participants, got {current_count}"
        
        # Try to add one more student - should fail
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": "capacity_overflow@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Activity is full"
        
        # Verify student was not added and count remains at capacity
        activity = self._get_activity_info(client, activity_name)
        participants = activity["participants"]
        assert len(participants) == max_participants
        assert "capacity_overflow@mergington.edu" not in participants

    def test_signup_allowed_when_one_below_capacity(self, client):
        """Test that signup is allowed when activity is one below capacity.
        
        Note: Uses Gym Class to avoid test data overlap with other capacity tests.
        This test relies on the reset_activities fixture for consistent initial state.
        """
        activity_name = "Gym Class"
        activity = self._get_activity_info(client, activity_name)
        
        initial_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        slots_to_fill = max_participants - initial_count - 1  # Leave one slot open
        
        # Guard against edge case where we can't test the scenario
        assert slots_to_fill >= 0, \
            f"{activity_name} doesn't have enough capacity to test this scenario"
        
        # Fill slots leaving exactly one open with test-specific email pattern
        for i in range(slots_to_fill):
            response = client.post(
                f"/activities/{activity_name}/signup",
                json={"email": f"onebelow_test_{i}@mergington.edu"}
            )
            assert response.status_code == 200, \
                f"Failed to sign up onebelow_test_{i} (signup {i+1}/{slots_to_fill})"
        
        # Verify activity is one below capacity
        activity = self._get_activity_info(client, activity_name)
        current_count = len(activity["participants"])
        expected_count = max_participants - 1
        assert current_count == expected_count, \
            f"Expected {expected_count} participants, got {current_count}"
        
        # Add the last student - should succeed
        response = client.post(
            f"/activities/{activity_name}/signup",
            json={"email": "onebelow_last@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify student was added and activity is now at capacity
        activity = self._get_activity_info(client, activity_name)
        participants = activity["participants"]
        assert len(participants) == max_participants
        assert "onebelow_last@mergington.edu" in participants

    def test_capacity_check_with_sequential_signups(self, client):
        """Test that capacity checking works correctly with multiple sequential signups.
        
        Note: This test relies on the reset_activities fixture for consistent initial state.
        """
        activity_name = "Programming Class"
        activity = self._get_activity_info(client, activity_name)
        
        initial_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        slots_available = max_participants - initial_count
        
        # Guard against edge case where activity is already at capacity
        assert slots_available > 0, \
            f"{activity_name} is already at capacity in fixture"
        
        # Fill all available slots with test-specific email pattern
        for i in range(slots_available):
            response = client.post(
                f"/activities/{activity_name}/signup",
                json={"email": f"sequential_test_{i}@mergington.edu"}
            )
            assert response.status_code == 200, \
                f"Failed to sign up sequential_test_{i} (signup {i+1}/{slots_available})"
        
        # Verify activity is at capacity
        activity = self._get_activity_info(client, activity_name)
        current_count = len(activity["participants"])
        assert current_count == max_participants, \
            f"Expected {max_participants} participants, got {current_count}"
        
        # Try to add more students - all should fail (using class constant)
        for i in range(self.OVERFLOW_TEST_COUNT):
            response = client.post(
                f"/activities/{activity_name}/signup",
                json={"email": f"sequential_overflow_{i}@mergington.edu"}
            )
            assert response.status_code == 400, \
                f"Expected 400 error for sequential_overflow_{i}, got {response.status_code}"
            assert response.json()["detail"] == "Activity is full"


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
