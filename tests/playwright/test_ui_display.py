"""UI tests for activity display and rendering.

Tests the activity list rendering including:
- Activity cards display
- Participant lists
- Spots calculation
- Dropdown population
"""

import pytest
from playwright.sync_api import expect
from tests.playwright.pages.activities_page import ActivitiesPage


@pytest.mark.test_id("TC-UI-DISPLAY-001")
@pytest.mark.e2e
def test_all_activities_displayed(activities_page: ActivitiesPage):
    """Test that all 9 activities are displayed on page load."""
    activities_page.load()
    activities_page.wait_for_activities_loaded()
    
    # Verify all English activities visible
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Swimming Club",
        "Drama Club",
        "Art Studio",
        "Debate Team",
        "Science Olympiad"
    ]
    
    for activity in expected_activities:
        card = activities_page.get_activity_card(activity)
        expect(card).to_be_visible()


@pytest.mark.test_id("TC-UI-DISPLAY-002")
@pytest.mark.e2e
def test_activity_card_shows_all_information(activities_page: ActivitiesPage):
    """Test that activity cards display all required information."""
    activities_page.load()
    
    card = activities_page.get_activity_card("Chess Club")
    
    # Verify title
    title = card.locator("h4")
    expect(title).to_have_text("Chess Club")
    
    # Verify description
    description = card.locator("p").first
    expect(description).to_contain_text("Learn strategies and compete in chess tournaments")
    
    # Verify schedule
    schedule = card.locator("text=/Schedule:/")
    expect(schedule).to_be_visible()
    
    # Verify availability
    availability = card.locator("text=/Availability:/")
    expect(availability).to_be_visible()
    
    # Verify participants section
    participants_section = card.locator(".participants-section")
    expect(participants_section).to_be_visible()


@pytest.mark.test_id("TC-UI-DISPLAY-003")
@pytest.mark.e2e
def test_spots_left_calculation(activities_page: ActivitiesPage, api_helper):
    """Test that spots left is correctly calculated."""
    activities_page.load()
    
    # Get Chess Club data via API
    activities = api_helper.get_activities("en")
    chess_data = activities["Chess Club"]
    
    expected_spots = chess_data["max_participants"] - len(chess_data["participants"])
    
    # Verify UI shows correct spots
    spots = activities_page.get_spots_left("Chess Club")
    assert spots == expected_spots, f"Expected {expected_spots} spots, got {spots}"


@pytest.mark.test_id("TC-UI-DISPLAY-004")
@pytest.mark.e2e
def test_no_participants_message(activities_page: ActivitiesPage, api_helper):
    """Test that 'no participants' message shows when activity is empty."""
    activities_page.load()
    
    # Delete all from Swimming Club (has 1 participant)
    participants = api_helper.get_activities("en")["Swimming Club"]["participants"]
    for email in participants:
        api_helper.unregister("Swimming Club", email, "en")
    
    # Reload UI
    activities_page.reload()
    activities_page.wait_for_activities_loaded()
    
    # Verify message
    card = activities_page.get_activity_card("Swimming Club")
    no_participants_msg = card.locator(".no-participants")
    expect(no_participants_msg).to_be_visible()
    expect(no_participants_msg).to_contain_text("No participants yet")


@pytest.mark.test_id("TC-UI-DISPLAY-005")
@pytest.mark.e2e
def test_participant_count_updates_after_signup(activities_page: ActivitiesPage):
    """Test that participant count updates after signup."""
    activities_page.load()
    
    initial_count = activities_page.get_participant_count("Chess Club")
    
    # Sign up
    activities_page.signup("displaytest@mergington.edu", "Chess Club")
    
    # Wait for refresh
    activities_page.wait_for_timeout(1000)
    
    # Verify count increased
    new_count = activities_page.get_participant_count("Chess Club")
    assert new_count == initial_count + 1


@pytest.mark.test_id("TC-UI-DISPLAY-006")
@pytest.mark.e2e
def test_dropdown_contains_all_activities(activities_page: ActivitiesPage):
    """Test that activity dropdown contains all activities."""
    activities_page.load()
    
    # Get dropdown options
    options = activities_page.get_activity_dropdown_options()
    
    # Verify all activities present (excluding placeholder)
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Swimming Club",
        "Drama Club",
        "Art Studio",
        "Debate Team",
        "Science Olympiad"
    ]
    
    for activity in expected_activities:
        assert activity in options, f"{activity} not in dropdown"


@pytest.mark.test_id("TC-UI-DISPLAY-007")
@pytest.mark.e2e
def test_hungarian_activities_displayed(activities_page: ActivitiesPage):
    """Test that Hungarian activity names are displayed correctly."""
    activities_page.load()
    activities_page.switch_to_language("hu")
    
    # Verify Hungarian activities visible
    expected_hu_activities = [
        "Sakk Klub",
        "Programozás Tanfolyam",
        "Tornaterem",
        "Focicsapat",
        "Úszó Klub",
        "Drámakör",
        "Művészeti Stúdió",
        "Vitakör",
        "Tudományos Olimpia"
    ]
    
    for activity in expected_hu_activities:
        card = activities_page.get_activity_card(activity)
        expect(card).to_be_visible()
