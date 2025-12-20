"""
Tests for the Mergington High School API

This module contains pytest tests for all FastAPI endpoints including:
- Root endpoint redirection
- Activity listing (with language support)
- Student signup (with language support)
- Student unregistration (with language support)
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, participants_storage


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_participants():
    """Reset participants to initial state before each test"""
    participants_storage.clear()
    participants_storage.update({
        "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
        "Soccer Team": ["alex@mergington.edu", "sarah@mergington.edu"],
        "Swimming Club": ["ryan@mergington.edu"],
        "Drama Club": ["lily@mergington.edu", "james@mergington.edu"],
        "Art Studio": ["ava@mergington.edu"],
        "Debate Team": ["noah@mergington.edu", "mia@mergington.edu"],
        "Science Olympiad": ["ethan@mergington.edu", "isabella@mergington.edu"]
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

    def test_get_activities_returns_all_activities_en(self, client):
        """Test that GET /activities returns all available activities in English"""
        response = client.get("/activities?lang=en")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_all_activities_hu(self, client):
        """Test that GET /activities returns all available activities in Hungarian"""
        response = client.get("/activities?lang=hu")
        assert response.status_code == 200
        data = response.json()
        assert "Sakk Klub" in data
        assert "Programozás Tanfolyam" in data
        assert "Tornaterem" in data

    def test_get_activities_defaults_to_english(self, client):
        """Test that GET /activities defaults to English when no lang parameter"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities?lang=en")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_returns_participant_lists(self, client):
        """Test that activities include participant lists"""
        response = client.get("/activities?lang=en")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_same_participants_both_languages(self, client):
        """Test that participants are synced across both language versions"""
        response_en = client.get("/activities?lang=en")
        response_hu = client.get("/activities?lang=hu")
        
        assert response_en.status_code == 200
        assert response_hu.status_code == 200
        
        data_en = response_en.json()
        data_hu = response_hu.json()
        
        # Check that Chess Club (en) and Sakk Klub (hu) have same participants
        assert data_en["Chess Club"]["participants"] == data_hu["Sakk Klub"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    # Number of overflow attempts to test capacity enforcement
    OVERFLOW_TEST_COUNT = 3

    def _get_activity_info(self, client, activity_name, lang="en"):
        """Helper method to fetch activity information from API.
        
        Note: Relies on the reset_participants fixture to ensure consistent state.
        """
        return client.get(f"/activities?lang={lang}").json()[activity_name]

    def test_signup_for_existing_activity_en(self, client):
        """Test signing up for an existing activity in English"""
        response = client.post(
            "/activities/Chess Club/signup?lang=en",
            json={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_for_existing_activity_hu(self, client):
        """Test signing up for an existing activity in Hungarian"""
        response = client.post(
            "/activities/Sakk Klub/signup?lang=hu",
            json={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu sikeresen jelentkezett: Sakk Klub" in data["message"]
        
        # Verify the student was added (check both English and Hungarian versions)
        activities_response_en = client.get("/activities?lang=en")
        activities_response_hu = client.get("/activities?lang=hu")
        assert "newstudent@mergington.edu" in activities_response_en.json()["Chess Club"]["participants"]
        assert "newstudent@mergington.edu" in activities_response_hu.json()["Sakk Klub"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?lang=en",
            json={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_when_already_registered(self, client):
        """Test signing up when already registered for the activity"""
        response = client.post(
            "/activities/Chess Club/signup?lang=en",
            json={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"

    def test_multiple_students_can_signup(self, client):
        """Test that multiple students can sign up for the same activity"""
        # First student
        response1 = client.post(
            "/activities/Programming Class/signup?lang=en",
            json={"email": "student1@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second student
        response2 = client.post(
            "/activities/Programming Class/signup?lang=en",
            json={"email": "student2@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both students are registered
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        participants = activities_data["Programming Class"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants

    def test_signup_rejected_when_activity_at_capacity_en(self, client):
        """Test that signup is rejected when activity has reached max_participants (English).
        
        Note: This test relies on the reset_participants fixture for consistent initial state.
        """
        activity_name = "Chess Club"
        activity = self._get_activity_info(client, activity_name, "en")
        
        initial_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        slots_available = max_participants - initial_count
        
        # Guard against edge case where activity is already at capacity
        assert slots_available > 0, \
            f"{activity_name} is already at capacity in fixture"
        
        # Fill all available slots with test-specific email pattern
        for i in range(slots_available):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"capacity_test_{i}@mergington.edu"}
            )
            assert response.status_code == 200, \
                f"Failed to sign up capacity_test_{i} (signup {i+1}/{slots_available})"
        
        # Verify activity is now at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        current_count = len(activity["participants"])
        assert current_count == max_participants, \
            f"Expected {max_participants} participants, got {current_count}"
        
        # Try to add one more student - should fail
        response = client.post(
            f"/activities/{activity_name}/signup?lang=en",
            json={"email": "capacity_overflow@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Activity is full"
        
        # Verify student was not added and count remains at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        participants = activity["participants"]
        assert len(participants) == max_participants
        assert "capacity_overflow@mergington.edu" not in participants

    def test_signup_rejected_when_activity_at_capacity_hu(self, client):
        """Test that signup is rejected when activity has reached max_participants (Hungarian)."""
        activity_name_hu = "Sakk Klub"
        activity = self._get_activity_info(client, activity_name_hu, "hu")
        
        initial_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        slots_available = max_participants - initial_count
        
        # Fill all available slots
        for i in range(slots_available):
            response = client.post(
                f"/activities/{activity_name_hu}/signup?lang=hu",
                json={"email": f"capacity_test_hu_{i}@mergington.edu"}
            )
            assert response.status_code == 200
        
        # Try to add one more student - should fail with Hungarian message
        response = client.post(
            f"/activities/{activity_name_hu}/signup?lang=hu",
            json={"email": "capacity_overflow_hu@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "A tevékenység megtelt"

    def test_signup_allowed_when_one_below_capacity(self, client):
        """Test that signup is allowed when activity is one below capacity.
        
        Note: Uses Gym Class to avoid test data overlap with other capacity tests.
        This test relies on the reset_participants fixture for consistent initial state.
        """
        activity_name = "Gym Class"
        activity = self._get_activity_info(client, activity_name, "en")
        
        initial_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        slots_to_fill = max_participants - initial_count - 1  # Leave one slot open
        
        # Guard against edge case where we can't test the scenario
        assert slots_to_fill >= 0, \
            f"{activity_name} doesn't have enough capacity to test this scenario"
        
        # Fill slots leaving exactly one open with test-specific email pattern
        for i in range(slots_to_fill):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"onebellow_test_{i}@mergington.edu"}
            )
            assert response.status_code == 200, \
                f"Failed to sign up onebellow_test_{i} (signup {i+1}/{slots_to_fill})"
        
        # Verify activity is one below capacity
        activity = self._get_activity_info(client, activity_name, "en")
        current_count = len(activity["participants"])
        expected_count = max_participants - 1
        assert current_count == expected_count, \
            f"Expected {expected_count} participants, got {current_count}"
        
        # Add the last student - should succeed
        response = client.post(
            f"/activities/{activity_name}/signup?lang=en",
            json={"email": "onebellow_last@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify student was added and activity is now at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        participants = activity["participants"]
        assert len(participants) == max_participants
        assert "onebellow_last@mergington.edu" in participants

    def test_capacity_check_with_sequential_signups(self, client):
        """Test that capacity checking works correctly with multiple sequential signups.
        
        Note: This test relies on the reset_participants fixture for consistent initial state.
        """
        activity_name = "Programming Class"
        activity = self._get_activity_info(client, activity_name, "en")
        
        initial_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        slots_available = max_participants - initial_count
        
        # Guard against edge case where activity is already at capacity
        assert slots_available > 0, \
            f"{activity_name} is already at capacity in fixture"
        
        # Fill all available slots with test-specific email pattern
        for i in range(slots_available):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"sequential_test_{i}@mergington.edu"}
            )
            assert response.status_code == 200, \
                f"Failed to sign up sequential_test_{i} (signup {i+1}/{slots_available})"
        
        # Verify activity is at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        current_count = len(activity["participants"])
        assert current_count == max_participants, \
            f"Expected {max_participants} participants, got {current_count}"
        
        # Try to add more students - all should fail (using class constant)
        for i in range(self.OVERFLOW_TEST_COUNT):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"sequential_overflow_{i}@mergington.edu"}
            )
            assert response.status_code == 400, \
                f"Expected 400 error for sequential_overflow_{i}, got {response.status_code}"
            assert response.json()["detail"] == "Activity is full"


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity_en(self, client):
        """Test unregistering from an activity in English"""
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister?lang=en",
            json={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_from_activity_hu(self, client):
        """Test unregistering from an activity in Hungarian"""
        response = client.request(
            "DELETE",
            "/activities/Sakk Klub/unregister?lang=hu",
            json={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu sikeresen kijelentkezve: Sakk Klub" in data["message"]
        
        # Verify the student was removed from both language versions
        activities_response_en = client.get("/activities?lang=en")
        activities_response_hu = client.get("/activities?lang=hu")
        assert "michael@mergington.edu" not in activities_response_en.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in activities_response_hu.json()["Sakk Klub"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.request(
            "DELETE",
            "/activities/Nonexistent Club/unregister?lang=en",
            json={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_when_not_registered(self, client):
        """Test unregistering when not registered for the activity"""
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister?lang=en",
            json={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"

    def test_unregister_then_signup_again(self, client):
        """Test that a student can unregister and then sign up again"""
        # Unregister
        response1 = client.request(
            "DELETE",
            "/activities/Gym Class/unregister?lang=en",
            json={"email": "john@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Gym Class/signup?lang=en",
            json={"email": "john@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify the student is registered again
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        assert "john@mergington.edu" in activities_data["Gym Class"]["participants"]
