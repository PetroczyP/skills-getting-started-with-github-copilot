"""
Tests for the Mergington High School API

This module contains pytest tests for all FastAPI endpoints including:
- Root endpoint redirection
- Activity listing (with language support)
- Student signup (with language support)
- Student unregistration (with language support)
- Race condition tests for concurrent signups (thread-safety validation)
"""

import pytest
import threading
import time
import random

from src.app import activity_name_mapping
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from tests.race_config import CONCURRENT_THREADS, BARRIER_TIMEOUT
from tests.race_metrics import RaceMetricsCollector


logger = logging.getLogger(__name__)


@pytest.mark.functional
class TestRootEndpoint:
    """Tests for the root endpoint"""

    @pytest.mark.test_id("TC-ROOT-001")
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


@pytest.mark.functional
class TestGetActivities:
    """Tests for GET /activities endpoint"""

    @pytest.mark.test_id("TC-ACTIVITIES-001")
    def test_get_activities_returns_all_activities_en(self, client):
        """Test that GET /activities returns all available activities in English"""
        response = client.get("/activities?lang=en")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    @pytest.mark.test_id("TC-ACTIVITIES-002")
    def test_get_activities_returns_all_activities_hu(self, client):
        """Test that GET /activities returns all available activities in Hungarian"""
        response = client.get("/activities?lang=hu")
        assert response.status_code == 200
        data = response.json()
        assert "Sakk Klub" in data
        assert "Programozás Tanfolyam" in data
        assert "Tornaterem" in data

    @pytest.mark.test_id("TC-LANGUAGE-002")
    def test_get_activities_defaults_to_english(self, client):
        """Test that GET /activities defaults to English when no lang parameter"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data

    @pytest.mark.test_id("TC-ACTIVITIES-004")
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

    @pytest.mark.test_id("TC-ACTIVITIES-005")
    def test_get_activities_returns_participant_lists(self, client):
        """Test that activities include participant lists"""
        response = client.get("/activities?lang=en")
        data = response.json()

        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    @pytest.mark.test_id("TC-LANGUAGE-001")
    def test_get_activities_same_participants_both_languages(self, client):
        """Test that participants are synced across both language versions"""
        response_en = client.get("/activities?lang=en")
        response_hu = client.get("/activities?lang=hu")

        assert response_en.status_code == 200
        assert response_hu.status_code == 200

        data_en = response_en.json()
        data_hu = response_hu.json()

        # Check that Chess Club (en) and Sakk Klub (hu) have same participants
        assert (
            data_en["Chess Club"]["participants"]
            == data_hu["Sakk Klub"]["participants"]
        )


@pytest.mark.functional
class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    # Number of overflow attempts to test capacity enforcement
    OVERFLOW_TEST_COUNT = 3

    def _get_activity_info(self, client, activity_name, lang="en"):
        """Helper method to fetch activity information from API.

        Note: Relies on the reset_participants fixture to ensure consistent state.
        """
        return client.get(f"/activities?lang={lang}").json()[activity_name]

    @pytest.mark.test_id("TC-SIGNUP-001")
    def test_signup_for_existing_activity_en(self, client):
        """Test signing up for an existing activity in English"""
        response = client.post(
            "/activities/Chess Club/signup?lang=en",
            json={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]

        # Verify the student was added
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        assert (
            "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
        )

    @pytest.mark.test_id("TC-SIGNUP-002")
    def test_signup_for_existing_activity_hu(self, client):
        """Test signing up for an existing activity in Hungarian"""
        response = client.post(
            "/activities/Sakk Klub/signup?lang=hu",
            json={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            "newstudent@mergington.edu sikeresen jelentkezett: Sakk Klub"
            in data["message"]
        )

        # Verify the student was added (check both English and Hungarian versions)
        activities_response_en = client.get("/activities?lang=en")
        activities_response_hu = client.get("/activities?lang=hu")
        assert (
            "newstudent@mergington.edu"
            in activities_response_en.json()["Chess Club"]["participants"]
        )
        assert (
            "newstudent@mergington.edu"
            in activities_response_hu.json()["Sakk Klub"]["participants"]
        )

    @pytest.mark.test_id("TC-SIGNUP-003")
    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?lang=en",
            json={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    @pytest.mark.test_id("TC-SIGNUP-004")
    def test_signup_when_already_registered(self, client):
        """Test signing up when already registered for the activity"""
        response = client.post(
            "/activities/Chess Club/signup?lang=en",
            json={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"

    @pytest.mark.test_id("TC-SIGNUP-005")
    def test_multiple_students_can_signup(self, client):
        """Test that multiple students can sign up for the same activity"""
        # First student
        response1 = client.post(
            "/activities/Programming Class/signup?lang=en",
            json={"email": "student1@mergington.edu"},
        )
        assert response1.status_code == 200

        # Second student
        response2 = client.post(
            "/activities/Programming Class/signup?lang=en",
            json={"email": "student2@mergington.edu"},
        )
        assert response2.status_code == 200

        # Verify both students are registered
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        participants = activities_data["Programming Class"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants

    @pytest.mark.test_id("TC-CAPACITY-001")
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
        assert slots_available > 0, f"{activity_name} is already at capacity in fixture"

        # Fill all available slots with test-specific email pattern
        for i in range(slots_available):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"capacity_test_{i}@mergington.edu"},
            )
            assert (
                response.status_code == 200
            ), f"Failed to sign up capacity_test_{i} (signup {i+1}/{slots_available})"

        # Verify activity is now at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        current_count = len(activity["participants"])
        assert (
            current_count == max_participants
        ), f"Expected {max_participants} participants, got {current_count}"

        # Try to add one more student - should fail
        response = client.post(
            f"/activities/{activity_name}/signup?lang=en",
            json={"email": "capacity_overflow@mergington.edu"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Activity is full"

        # Verify student was not added and count remains at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        participants = activity["participants"]
        assert len(participants) == max_participants
        assert "capacity_overflow@mergington.edu" not in participants

    @pytest.mark.test_id("TC-CAPACITY-002")
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
                json={"email": f"capacity_test_hu_{i}@mergington.edu"},
            )
            assert response.status_code == 200

        # Try to add one more student - should fail with Hungarian message
        response = client.post(
            f"/activities/{activity_name_hu}/signup?lang=hu",
            json={"email": "capacity_overflow_hu@mergington.edu"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "A tevékenység megtelt"

    @pytest.mark.test_id("TC-CAPACITY-003")
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
        assert (
            slots_to_fill >= 0
        ), f"{activity_name} doesn't have enough capacity to test this scenario"

        # Fill slots leaving exactly one open with test-specific email pattern
        for i in range(slots_to_fill):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"onebellow_test_{i}@mergington.edu"},
            )
            assert (
                response.status_code == 200
            ), f"Failed to sign up onebellow_test_{i} (signup {i+1}/{slots_to_fill})"

        # Verify activity is one below capacity
        activity = self._get_activity_info(client, activity_name, "en")
        current_count = len(activity["participants"])
        expected_count = max_participants - 1
        assert (
            current_count == expected_count
        ), f"Expected {expected_count} participants, got {current_count}"

        # Add the last student - should succeed
        response = client.post(
            f"/activities/{activity_name}/signup?lang=en",
            json={"email": "onebellow_last@mergington.edu"},
        )
        assert response.status_code == 200

        # Verify student was added and activity is now at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        participants = activity["participants"]
        assert len(participants) == max_participants
        assert "onebellow_last@mergington.edu" in participants

    @pytest.mark.test_id("TC-CAPACITY-004")
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
        assert slots_available > 0, f"{activity_name} is already at capacity in fixture"

        # Fill all available slots with test-specific email pattern
        for i in range(slots_available):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"sequential_test_{i}@mergington.edu"},
            )
            assert (
                response.status_code == 200
            ), f"Failed to sign up sequential_test_{i} (signup {i+1}/{slots_available})"

        # Verify activity is at capacity
        activity = self._get_activity_info(client, activity_name, "en")
        current_count = len(activity["participants"])
        assert (
            current_count == max_participants
        ), f"Expected {max_participants} participants, got {current_count}"

        # Try to add more students - all should fail (using class constant)
        for i in range(self.OVERFLOW_TEST_COUNT):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"sequential_overflow_{i}@mergington.edu"},
            )
            assert (
                response.status_code == 400
            ), f"Expected 400 error for sequential_overflow_{i}, got {response.status_code}"
            assert response.json()["detail"] == "Activity is full"


@pytest.mark.functional
class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    @pytest.mark.test_id("TC-UNREGISTER-001")
    def test_unregister_from_activity_en(self, client):
        """Test unregistering from an activity in English"""
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister?lang=en",
            json={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]

        # Verify the student was removed
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        assert (
            "michael@mergington.edu"
            not in activities_data["Chess Club"]["participants"]
        )

    @pytest.mark.test_id("TC-UNREGISTER-002")
    def test_unregister_from_activity_hu(self, client):
        """Test unregistering from an activity in Hungarian"""
        response = client.request(
            "DELETE",
            "/activities/Sakk Klub/unregister?lang=hu",
            json={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            "michael@mergington.edu sikeresen kijelentkezve: Sakk Klub"
            in data["message"]
        )

        # Verify the student was removed from both language versions
        activities_response_en = client.get("/activities?lang=en")
        activities_response_hu = client.get("/activities?lang=hu")
        assert (
            "michael@mergington.edu"
            not in activities_response_en.json()["Chess Club"]["participants"]
        )
        assert (
            "michael@mergington.edu"
            not in activities_response_hu.json()["Sakk Klub"]["participants"]
        )

    @pytest.mark.test_id("TC-UNREGISTER-003")
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.request(
            "DELETE",
            "/activities/Nonexistent Club/unregister?lang=en",
            json={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    @pytest.mark.test_id("TC-UNREGISTER-004")
    def test_unregister_when_not_registered(self, client):
        """Test unregistering when not registered for the activity"""
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister?lang=en",
            json={"email": "notregistered@mergington.edu"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"

    @pytest.mark.test_id("TC-UNREGISTER-005")
    def test_unregister_then_signup_again(self, client):
        """Test that a student can unregister and then sign up again"""
        # Unregister
        response1 = client.request(
            "DELETE",
            "/activities/Gym Class/unregister?lang=en",
            json={"email": "john@mergington.edu"},
        )
        assert response1.status_code == 200

        # Sign up again
        response2 = client.post(
            "/activities/Gym Class/signup?lang=en",
            json={"email": "john@mergington.edu"},
        )
        assert response2.status_code == 200

        # Verify the student is registered again
        activities_response = client.get("/activities?lang=en")
        activities_data = activities_response.json()
        assert "john@mergington.edu" in activities_data["Gym Class"]["participants"]


class TestRaceConditions:
    """Tests for concurrent signup operations and race condition handling.

    These tests validate thread-safety and data integrity under concurrent load using
    threading.Barrier to synchronize thread start times, creating true race conditions
    where multiple requests arrive simultaneously.

    Critical for validating:
    - Capacity enforcement under concurrent load
    - No duplicate participants due to race conditions
    - Proper HTTP status codes for concurrent success/failure
    - Language-agnostic capacity enforcement
    - State consistency after mixed concurrent operations

    All tests use CONCURRENT_THREADS (10) for consistency with Playwright fixtures.
    """

    # Class constants
    CONCURRENT_THREADS = CONCURRENT_THREADS
    BARRIER_TIMEOUT = BARRIER_TIMEOUT

    def _concurrent_signup(
        self,
        client: TestClient,
        activity_name: str,
        emails: list,
        lang: str,
        barrier: threading.Barrier,
        race_metrics: RaceMetricsCollector,
    ):
        """Helper method to execute concurrent signups with barrier synchronization.

        Args:
            client: TestClient instance
            activity_name: Name of activity to sign up for
            emails: List of email addresses (one per thread)
            lang: Language code
            barrier: Threading barrier for synchronization
            race_metrics: Metrics collector instance

        Returns:
            Tuple of (success_responses, failure_responses) lists
        """
        results = []

        def signup_thread(thread_id, email):
            """Thread worker function that waits at barrier then signs up."""
            try:
                # Wait at barrier for all threads to be ready
                barrier.wait(timeout=self.BARRIER_TIMEOUT)

                # All threads release simultaneously - race condition begins
                start_time = time.time()
                response = client.post(
                    f"/activities/{activity_name}/signup?lang={lang}",
                    json={"email": email},
                )
                end_time = time.time()

                # Record metrics
                race_metrics.record_request(
                    thread_id=thread_id,
                    start_time=start_time,
                    end_time=end_time,
                    status_code=response.status_code,
                )

                return response
            except threading.BrokenBarrierError as e:
                logger.error(f"Thread {thread_id} barrier broken: {e}")
                raise

        # Start barrier wait timing
        race_metrics.start_barrier_wait()

        # Launch all threads
        with ThreadPoolExecutor(max_workers=len(emails)) as executor:
            futures = {
                executor.submit(signup_thread, i, email): (i, email)
                for i, email in enumerate(emails)
            }

            # Collect results
            for future in as_completed(futures):
                try:
                    response = future.result(timeout=self.BARRIER_TIMEOUT + 5)
                    results.append(response)
                except Exception as e:
                    logger.error(f"Thread failed: {e}")
                    raise

        # End barrier wait timing
        race_metrics.end_barrier_wait()

        # Separate success and failure responses
        success_responses = [r for r in results if r.status_code == 200]
        failure_responses = [r for r in results if r.status_code != 200]

        return success_responses, failure_responses

    def _verify_state_integrity(self, client: TestClient, activity_name: str):
        """Verify activity state consistency after concurrent operations.

        Args:
            client: TestClient instance
            activity_name: English name of activity to verify

        Raises:
            AssertionError: If state integrity violations detected
        """
        # Get activity data in both languages
        en_data = client.get("/activities?lang=en").json()[activity_name]

        # Get Hungarian name from centralized mapping
        hu_name = activity_name_mapping.get(activity_name, activity_name)
        hu_data = client.get("/activities?lang=hu").json()[hu_name]

        participants = en_data["participants"]
        max_participants = en_data["max_participants"]

        # Check for duplicates
        assert len(participants) == len(
            set(participants)
        ), f"Duplicate participants detected: {participants}"

        # Check capacity not exceeded
        assert (
            len(participants) <= max_participants
        ), f"Capacity exceeded: {len(participants)} > {max_participants}"

        # Check language sync
        assert (
            en_data["participants"] == hu_data["participants"]
        ), "Participants not synced across languages"

    @pytest.mark.test_id("TC-RACE-001")
    @pytest.mark.slow
    @pytest.mark.concurrency
    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_concurrent_signup_single_spot_race(self, client, race_metrics):
        """Validate exactly 1 success when 10 concurrent signups compete for 1 slot.

        Tests that when 10 simultaneous signup requests compete for the last available
        slot in an activity, exactly one succeeds and nine fail with proper error messages.
        Uses Barrier(10) to synchronize thread start times, ensuring true simultaneous arrival.

        This proves the system has no race condition that would allow capacity violations.
        """
        activity_name = "Chess Club"

        # Get activity info and fill to 1 remaining slot
        activity = client.get("/activities?lang=en").json()[activity_name]
        max_participants = activity["max_participants"]
        current_count = len(activity["participants"])
        slots_to_fill = max_participants - current_count - 1

        # Fill activity leaving exactly 1 slot
        for i in range(slots_to_fill):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"setup_{i}@mergington.edu"},
            )
            assert response.status_code == 200

        # Verify 1 slot remains
        activity = client.get("/activities?lang=en").json()[activity_name]
        assert len(activity["participants"]) == max_participants - 1

        # Prepare 10 concurrent signups for the last slot
        emails = [
            f"race_001_{i}@mergington.edu" for i in range(self.CONCURRENT_THREADS)
        ]
        barrier = threading.Barrier(
            self.CONCURRENT_THREADS, timeout=self.BARRIER_TIMEOUT
        )

        # Execute concurrent signups
        success_responses, failure_responses = self._concurrent_signup(
            client, activity_name, emails, "en", barrier, race_metrics
        )

        # Verify exactly 1 success and 9 failures
        assert (
            len(success_responses) == 1
        ), f"Expected 1 success, got {len(success_responses)}"
        assert (
            len(failure_responses) == 9
        ), f"Expected 9 failures, got {len(failure_responses)}"

        # Verify failures have correct error message
        for response in failure_responses:
            assert response.status_code == 400
            assert response.json()["detail"] == "Activity is full"

        # Verify final state
        activity = client.get("/activities?lang=en").json()[activity_name]
        assert len(activity["participants"]) == max_participants

        # Verify state integrity
        self._verify_state_integrity(client, activity_name)

        # Save metrics
        race_metrics.save_to_json("TC-RACE-001", self.CONCURRENT_THREADS)

    @pytest.mark.test_id("TC-RACE-002")
    @pytest.mark.slow
    @pytest.mark.concurrency
    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_concurrent_signup_multiple_spots_race(self, client, race_metrics):
        """Validate capacity counting accuracy when 10 threads compete for 3 slots.

        Tests that when 10 concurrent signups compete for 3 available slots, exactly
        3 succeed and 7 fail. Ensures atomic counter updates prevent overselling.
        """
        activity_name = "Gym Class"
        slots_available = 3

        # Get activity info and calculate slots to fill
        activity = client.get("/activities?lang=en").json()[activity_name]
        max_participants = activity["max_participants"]
        current_count = len(activity["participants"])
        slots_to_fill = max_participants - current_count - slots_available

        # Fill activity leaving exactly 3 slots
        for i in range(slots_to_fill):
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"setup_{i}@mergington.edu"},
            )
            assert response.status_code == 200

        # Verify correct number of slots remain
        activity = client.get("/activities?lang=en").json()[activity_name]
        assert len(activity["participants"]) == max_participants - slots_available

        # Prepare 10 concurrent signups for 3 slots
        emails = [
            f"race_002_{i}@mergington.edu" for i in range(self.CONCURRENT_THREADS)
        ]
        barrier = threading.Barrier(
            self.CONCURRENT_THREADS, timeout=self.BARRIER_TIMEOUT
        )

        # Execute concurrent signups
        success_responses, failure_responses = self._concurrent_signup(
            client, activity_name, emails, "en", barrier, race_metrics
        )

        # Verify exactly 3 successes and 7 failures
        assert (
            len(success_responses) == 3
        ), f"Expected 3 successes, got {len(success_responses)}"
        assert (
            len(failure_responses) == 7
        ), f"Expected 7 failures, got {len(failure_responses)}"

        # Verify final state
        activity = client.get("/activities?lang=en").json()[activity_name]
        assert len(activity["participants"]) == max_participants

        # Verify no duplicates
        participants = activity["participants"]
        assert len(participants) == len(
            set(participants)
        ), f"Duplicate participants found: {participants}"

        # Verify state integrity across languages
        self._verify_state_integrity(client, activity_name)

        # Save metrics
        race_metrics.save_to_json("TC-RACE-002", self.CONCURRENT_THREADS)

    @pytest.mark.test_id("TC-RACE-003")
    @pytest.mark.slow
    @pytest.mark.concurrency
    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_concurrent_signup_cross_language_race(self, client, race_metrics):
        """Validate language endpoints share same capacity enforcement.

        Tests that 5 signups via English endpoint and 5 via Hungarian endpoint
        compete for the same underlying slots (not separate limits per language).
        Single Barrier synchronizes all 10 threads regardless of endpoint.
        """
        activity_name_en = "Chess Club"
        activity_name_hu = "Sakk Klub"
        slots_available = 3

        # Fill to 3 remaining slots
        activity = client.get("/activities?lang=en").json()[activity_name_en]
        max_participants = activity["max_participants"]
        current_count = len(activity["participants"])
        slots_to_fill = max_participants - current_count - slots_available

        for i in range(slots_to_fill):
            response = client.post(
                f"/activities/{activity_name_en}/signup?lang=en",
                json={"email": f"setup_{i}@mergington.edu"},
            )
            assert response.status_code == 200

        # Prepare concurrent signups: 5 English + 5 Hungarian
        emails_en = [f"race_003_en_{i}@mergington.edu" for i in range(5)]
        emails_hu = [f"race_003_hu_{i}@mergington.edu" for i in range(5)]

        results = []
        barrier = threading.Barrier(10, timeout=self.BARRIER_TIMEOUT)

        def signup_worker(thread_id, email, lang, activity_name):
            """Worker for cross-language signup."""
            barrier.wait(timeout=self.BARRIER_TIMEOUT)
            start_time = time.time()
            response = client.post(
                f"/activities/{activity_name}/signup?lang={lang}", json={"email": email}
            )
            end_time = time.time()
            race_metrics.record_request(
                thread_id, start_time, end_time, response.status_code
            )
            return response

        race_metrics.start_barrier_wait()

        # Launch all threads (mixed languages)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            thread_id = 0

            # Submit English endpoint threads
            for email in emails_en:
                futures.append(
                    executor.submit(
                        signup_worker, thread_id, email, "en", activity_name_en
                    )
                )
                thread_id += 1

            # Submit Hungarian endpoint threads
            for email in emails_hu:
                futures.append(
                    executor.submit(
                        signup_worker, thread_id, email, "hu", activity_name_hu
                    )
                )
                thread_id += 1

            # Collect results
            for future in as_completed(futures):
                results.append(future.result())

        race_metrics.end_barrier_wait()

        # Verify exactly 3 total successes (language-agnostic)
        success_count = sum(1 for r in results if r.status_code == 200)
        failure_count = sum(1 for r in results if r.status_code != 200)

        assert success_count == 3, f"Expected 3 successes, got {success_count}"
        assert failure_count == 7, f"Expected 7 failures, got {failure_count}"

        # Verify participants synced across languages
        en_data = client.get("/activities?lang=en").json()[activity_name_en]
        hu_data = client.get("/activities?lang=hu").json()[activity_name_hu]

        assert (
            en_data["participants"] == hu_data["participants"]
        ), "Participants not synced across languages after concurrent operations"

        # Verify state integrity
        self._verify_state_integrity(client, activity_name_en)

        # Save metrics
        race_metrics.save_to_json("TC-RACE-003", 10)

    @pytest.mark.test_id("TC-RACE-004")
    @pytest.mark.slow
    @pytest.mark.concurrency
    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_concurrent_signup_and_unregister_chaos(self, client, race_metrics):
        """Validate state consistency during simultaneous signups and unregisters.

        Simulates real-world chaos where signups and unregisters happen simultaneously.
        Validates that state remains consistent despite operation interleaving and
        ensures no lost updates or corrupted participant lists.
        """
        activity_name = "Chess Club"

        # Start with activity at max capacity
        activity = client.get("/activities?lang=en").json()[activity_name]
        max_participants = activity["max_participants"]
        current_count = len(activity["participants"])

        # Fill to capacity if not already
        slots_to_fill = max_participants - current_count
        for i in range(slots_to_fill):
            client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"fill_{i}@mergington.edu"},
            )

        # Get fresh participant list
        activity = client.get("/activities?lang=en").json()[activity_name]
        participants_to_remove = activity["participants"][:5]

        # Prepare chaos: 5 unregisters + 10 signups (15 total operations)
        new_emails = [f"race_004_{i}@mergington.edu" for i in range(10)]
        barrier = threading.Barrier(15, timeout=self.BARRIER_TIMEOUT)
        results = []

        def unregister_worker(thread_id, email):
            """Worker for unregister operations."""
            barrier.wait(timeout=self.BARRIER_TIMEOUT)
            start_time = time.time()
            response = client.request(
                "DELETE",
                f"/activities/{activity_name}/unregister?lang=en",
                json={"email": email},
            )
            end_time = time.time()
            race_metrics.record_request(
                thread_id, start_time, end_time, response.status_code
            )
            return ("unregister", response)

        def signup_worker(thread_id, email):
            """Worker for signup operations."""
            barrier.wait(timeout=self.BARRIER_TIMEOUT)
            start_time = time.time()
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en", json={"email": email}
            )
            end_time = time.time()
            race_metrics.record_request(
                thread_id, start_time, end_time, response.status_code
            )
            return ("signup", response)

        race_metrics.start_barrier_wait()

        # Launch mixed operations
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            thread_id = 0

            # Submit unregister threads
            for email in participants_to_remove:
                futures.append(executor.submit(unregister_worker, thread_id, email))
                thread_id += 1

            # Submit signup threads
            for email in new_emails:
                futures.append(executor.submit(signup_worker, thread_id, email))
                thread_id += 1

            # Collect results
            for future in as_completed(futures):
                results.append(future.result())

        race_metrics.end_barrier_wait()

        # Verify final state
        activity = client.get("/activities?lang=en").json()[activity_name]
        final_participants = activity["participants"]

        # Check capacity not exceeded
        assert (
            len(final_participants) <= max_participants
        ), f"Capacity exceeded: {len(final_participants)} > {max_participants}"

        # Check no duplicates
        assert len(final_participants) == len(
            set(final_participants)
        ), f"Duplicate participants after chaos test: {final_participants}"

        # Verify successfully unregistered emails are not in final list
        for email in participants_to_remove:
            # Only check if unregister was successful (some may have failed due to timing)
            unregister_results = [r for op, r in results if op == "unregister"]
            successful_unregisters = [
                r.json().get("message", "")
                for r in unregister_results
                if r.status_code == 200
            ]
            if any(email in msg for msg in successful_unregisters):
                assert (
                    email not in final_participants
                ), f"Unregistered email {email} still in participants"

        # Verify state integrity
        self._verify_state_integrity(client, activity_name)

        # Save metrics
        race_metrics.save_to_json("TC-RACE-004", 15)

    @pytest.mark.test_id("TC-RACE-005")
    @pytest.mark.slow
    @pytest.mark.concurrency
    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_concurrent_signup_tight_timing_stress(self, client, race_metrics):
        """Validate capacity enforcement without perfect synchronization.

        Simulates real network jitter with random 10-50ms stagger between requests
        (no barrier). Validates capacity enforcement even with unpredictable timing.
        """
        activity_name = "Gym Class"
        slots_available = 2

        # Setup: leave 2 slots available
        activity = client.get("/activities?lang=en").json()[activity_name]
        max_participants = activity["max_participants"]
        current_count = len(activity["participants"])
        slots_to_fill = max_participants - current_count - slots_available

        for i in range(slots_to_fill):
            client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"setup_{i}@mergington.edu"},
            )

        # Prepare 10 concurrent signups with random stagger (no barrier)
        emails = [
            f"race_005_{i}@mergington.edu" for i in range(self.CONCURRENT_THREADS)
        ]
        results = []

        def staggered_signup_worker(thread_id, email):
            """Worker with random timing jitter."""
            # Random stagger 10-50ms
            time.sleep(random.uniform(0.01, 0.05))

            start_time = time.time()
            response = client.post(
                f"/activities/{activity_name}/signup?lang=en", json={"email": email}
            )
            end_time = time.time()

            race_metrics.record_request(
                thread_id, start_time, end_time, response.status_code
            )
            return response

        # Launch threads without barrier
        with ThreadPoolExecutor(max_workers=self.CONCURRENT_THREADS) as executor:
            futures = {
                executor.submit(staggered_signup_worker, i, email): (i, email)
                for i, email in enumerate(emails)
            }

            for future in as_completed(futures):
                results.append(future.result())

        # Verify exactly 2 successes despite unpredictable timing
        success_count = sum(1 for r in results if r.status_code == 200)
        failure_count = sum(1 for r in results if r.status_code != 200)

        assert success_count == 2, f"Expected 2 successes, got {success_count}"
        assert failure_count == 8, f"Expected 8 failures, got {failure_count}"

        # Verify final state
        activity = client.get("/activities?lang=en").json()[activity_name]
        assert len(activity["participants"]) == max_participants

        # Verify state integrity
        self._verify_state_integrity(client, activity_name)

        # Save metrics and log if true race achieved (spread < 100ms)
        stats = race_metrics.calculate_statistics()
        if stats["request_spread_ms"] < 100:
            logger.info(
                f"✓ True race condition achieved: {stats['request_spread_ms']:.2f}ms spread"
            )

        race_metrics.save_to_json("TC-RACE-005", self.CONCURRENT_THREADS)

    @pytest.mark.test_id("TC-RACE-006")
    @pytest.mark.slow
    @pytest.mark.concurrency
    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    @pytest.mark.parametrize("thread_count", [5, 10, 20])
    def test_concurrent_signup_parameterized_thread_count(
        self, client, race_metrics, thread_count
    ):
        """Validate scalability across different concurrency levels (5, 10, 20 threads).

        Ensures race protection works from light (5) to heavy (20) concurrent load.
        Uses Programming Class with 20 max capacity for thread count scaling.
        """
        activity_name = "Programming Class"

        # Dynamic slot calculation: leave thread_count // 2 slots available
        slots_available = thread_count // 2

        # Setup activity
        activity = client.get("/activities?lang=en").json()[activity_name]
        max_participants = activity["max_participants"]
        current_count = len(activity["participants"])
        slots_to_fill = max_participants - current_count - slots_available

        for i in range(slots_to_fill):
            client.post(
                f"/activities/{activity_name}/signup?lang=en",
                json={"email": f"setup_{thread_count}_{i}@mergington.edu"},
            )

        # Prepare concurrent signups with dynamic thread count
        emails = [
            f"race_006_{thread_count}_{i}@mergington.edu" for i in range(thread_count)
        ]
        barrier = threading.Barrier(thread_count, timeout=self.BARRIER_TIMEOUT)

        # Execute concurrent signups
        success_responses, failure_responses = self._concurrent_signup(
            client, activity_name, emails, "en", barrier, race_metrics
        )

        # Verify exactly slots_available successes
        assert (
            len(success_responses) == slots_available
        ), f"Thread count {thread_count}: Expected {slots_available} successes, got {len(success_responses)}"
        assert (
            len(failure_responses) == thread_count - slots_available
        ), f"Thread count {thread_count}: Expected {thread_count - slots_available} failures, got {len(failure_responses)}"

        # Verify state integrity
        self._verify_state_integrity(client, activity_name)

        # Save metrics with thread count in filename
        race_metrics.save_to_json(f"TC-RACE-006", thread_count)
