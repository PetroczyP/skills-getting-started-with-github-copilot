"""UI tests for capacity enforcement.

Tests the maximum participant limit including:
- Signup rejection when at capacity
- Error message display
- Capacity calculation and display
"""

import pytest
from tests.playwright.pages.activities_page import ActivitiesPage


@pytest.mark.test_id("TC-UI-CAPACITY-001")
@pytest.mark.e2e
@pytest.mark.capacity
def test_signup_shows_error_when_full(activities_page: ActivitiesPage, fill_activity_to_capacity):
    """Test UI displays error message when activity at capacity."""
    activities_page.load()
    
    # Fill via API (fast setup)
    fill_activity_to_capacity("Chess Club", "en")
    
    # Refresh to update UI
    activities_page.reload()
    activities_page.wait_for_activities_loaded()
    
    # Verify spots left shows 0
    spots = activities_page.get_spots_left("Chess Club")
    assert spots == 0, f"Expected 0 spots, got {spots}"
    
    # Attempt signup via UI
    activities_page.signup("overflow@mergington.edu", "Chess Club")
    
    # Verify error message
    assert activities_page.is_error_message()
    message = activities_page.get_success_message()
    assert "Activity is full" in message
    
    # Verify participant NOT added
    assert not activities_page.has_participant("Chess Club", "overflow@mergington.edu")


@pytest.mark.test_id("TC-UI-CAPACITY-002")
@pytest.mark.e2e
@pytest.mark.capacity
def test_signup_allowed_when_one_below_capacity(activities_page: ActivitiesPage, api_helper):
    """Test that signup is allowed when activity has 1 slot available."""
    activities_page.load()
    
    # Get Gym Class info
    activities = api_helper.get_activities("en")
    gym_data = activities["Gym Class"]
    max_participants = gym_data["max_participants"]
    current_count = len(gym_data["participants"])
    
    # Fill to one below capacity
    slots_to_fill = max_participants - current_count - 1
    for i in range(slots_to_fill):
        api_helper.signup("Gym Class", f"onebellow_{i}@mergington.edu", "en")
    
    # Reload UI
    activities_page.reload()
    activities_page.wait_for_activities_loaded()
    
    # Verify 1 spot left
    spots = activities_page.get_spots_left("Gym Class")
    assert spots == 1, f"Expected 1 spot, got {spots}"
    
    # Sign up for last spot
    activities_page.signup("laststudent@mergington.edu", "Gym Class")
    
    # Verify success
    assert activities_page.is_success_message()
    assert activities_page.has_participant("Gym Class", "laststudent@mergington.edu")
    
    # Reload and verify 0 spots left
    activities_page.reload()
    activities_page.wait_for_activities_loaded()
    spots = activities_page.get_spots_left("Gym Class")
    assert spots == 0, f"Expected 0 spots, got {spots}"


@pytest.mark.test_id("TC-UI-CAPACITY-003")
@pytest.mark.e2e
@pytest.mark.capacity
def test_capacity_error_in_hungarian(activities_page: ActivitiesPage, fill_activity_to_capacity):
    """Test capacity error message in Hungarian."""
    activities_page.load()
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Fill activity via API
    fill_activity_to_capacity("Chess Club", "en")  # Use EN name for API
    
    # Reload UI
    activities_page.reload()
    activities_page.wait_for_activities_loaded()
    activities_page.switch_to_language("hu")
    
    # Attempt signup in Hungarian
    activities_page.signup("overflow@mergington.edu", "Sakk Klub")
    
    # Verify Hungarian error message
    assert activities_page.is_error_message()
    message = activities_page.get_success_message()
    assert "A tevékenység megtelt" in message


@pytest.mark.test_id("TC-UI-CAPACITY-004")
@pytest.mark.e2e
@pytest.mark.capacity
def test_spots_remaining_updates_after_signup(activities_page: ActivitiesPage):
    """Test that spots remaining updates after signup."""
    activities_page.load()
    
    # Get initial spots
    initial_spots = activities_page.get_spots_left("Chess Club")
    
    # Sign up
    activities_page.signup("spottest@mergington.edu", "Chess Club")
    
    # Wait for refresh
    activities_page.wait_for_timeout(1000)
    
    # Verify spots decreased by 1
    new_spots = activities_page.get_spots_left("Chess Club")
    assert new_spots == initial_spots - 1, f"Expected {initial_spots - 1} spots, got {new_spots}"


@pytest.mark.test_id("TC-UI-CAPACITY-005")
@pytest.mark.e2e
@pytest.mark.capacity
def test_spots_remaining_updates_after_delete(activities_page: ActivitiesPage):
    """Test that spots remaining increases after deleting participant."""
    activities_page.load()
    
    # Get initial spots
    initial_spots = activities_page.get_spots_left("Chess Club")
    
    # Delete a participant
    activities_page.delete_participant("michael@mergington.edu", "Chess Club", confirm=True)
    
    # Wait for refresh
    activities_page.wait_for_timeout(1000)
    
    # Verify spots increased by 1
    new_spots = activities_page.get_spots_left("Chess Club")
    assert new_spots == initial_spots + 1, f"Expected {initial_spots + 1} spots, got {new_spots}"
