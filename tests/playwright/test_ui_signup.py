"""UI tests for signup functionality.

Tests the signup form including:
- Form submission and validation
- Success/error message display
- Participant list updates
- Form reset after successful signup
"""

import pytest
from playwright.sync_api import Page, expect
from tests.playwright.pages.activities_page import ActivitiesPage


@pytest.mark.test_id("TC-UI-SIGNUP-001")
@pytest.mark.e2e
def test_signup_form_submission(activities_page: ActivitiesPage):
    """Test successful signup via UI form."""
    activities_page.load()
    
    # Fill form
    activities_page.email_input.fill("uitest@mergington.edu")
    activities_page.activity_select.select_option("Chess Club")
    
    # Submit
    activities_page.signup_button.click()
    activities_page.wait_for_timeout(500)
    
    # Verify success message
    assert activities_page.is_success_message()
    message = activities_page.get_success_message()
    assert "Signed up uitest@mergington.edu for Chess Club" in message
    
    # Verify participant added to list
    assert activities_page.has_participant("Chess Club", "uitest@mergington.edu")
    
    # Verify form is reset
    assert activities_page.is_form_reset()


@pytest.mark.test_id("TC-UI-SIGNUP-002")
@pytest.mark.e2e
def test_signup_with_invalid_email(activities_page: ActivitiesPage):
    """Test that invalid email triggers HTML5 validation."""
    activities_page.load()
    
    # Fill form with invalid email
    activities_page.email_input.fill("not-an-email")
    activities_page.activity_select.select_option("Chess Club")
    
    # Attempt submit - HTML5 validation should prevent submission
    activities_page.signup_button.click()
    
    # Check validation state
    validity = activities_page.email_input.evaluate("el => el.validity.valid")
    assert not validity, "Email should be invalid"


@pytest.mark.test_id("TC-UI-SIGNUP-003")
@pytest.mark.e2e
def test_duplicate_signup_shows_error(activities_page: ActivitiesPage):
    """Test that duplicate signup shows error message."""
    activities_page.load()
    
    # First signup
    activities_page.signup("duplicate@mergington.edu", "Chess Club")
    assert activities_page.is_success_message()
    
    # Attempt duplicate signup
    activities_page.signup("duplicate@mergington.edu", "Chess Club")
    
    # Verify error message
    assert activities_page.is_error_message()
    message = activities_page.get_success_message()
    assert "already signed up" in message


@pytest.mark.test_id("TC-UI-SIGNUP-004")
@pytest.mark.e2e
def test_multiple_students_can_signup(activities_page: ActivitiesPage):
    """Test that multiple students can sign up for the same activity."""
    activities_page.load()
    
    initial_count = activities_page.get_participant_count("Programming Class")
    
    # First student
    activities_page.signup("student1@mergington.edu", "Programming Class")
    assert activities_page.is_success_message()
    
    # Second student
    activities_page.signup("student2@mergington.edu", "Programming Class")
    assert activities_page.is_success_message()
    
    # Verify both students in list
    assert activities_page.has_participant("Programming Class", "student1@mergington.edu")
    assert activities_page.has_participant("Programming Class", "student2@mergington.edu")
    
    # Verify count increased by 2
    final_count = activities_page.get_participant_count("Programming Class")
    assert final_count == initial_count + 2


@pytest.mark.test_id("TC-UI-SIGNUP-005")
@pytest.mark.e2e
def test_signup_in_hungarian(activities_page: ActivitiesPage):
    """Test signup form in Hungarian language."""
    activities_page.load()
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Sign up
    activities_page.signup("magyar@mergington.edu", "Sakk Klub")
    
    # Verify Hungarian success message
    assert activities_page.is_success_message()
    message = activities_page.get_success_message()
    assert "magyar@mergington.edu sikeresen jelentkezett" in message
    
    # Verify participant added
    assert activities_page.has_participant("Sakk Klub", "magyar@mergington.edu")


@pytest.mark.test_id("TC-UI-SIGNUP-006")
@pytest.mark.e2e
def test_activities_list_refreshes_after_signup(activities_page: ActivitiesPage):
    """Test that activities list refreshes after signup."""
    activities_page.load()
    
    # Get initial participant count
    initial_count = activities_page.get_participant_count("Chess Club")
    
    # Sign up
    activities_page.signup("refresh_test@mergington.edu", "Chess Club")
    
    # Wait for refresh
    activities_page.wait_for_timeout(1000)
    
    # Verify count increased
    new_count = activities_page.get_participant_count("Chess Club")
    assert new_count == initial_count + 1
    
    # Verify participant visible in UI
    participants = activities_page.get_participants("Chess Club")
    assert "refresh_test@mergington.edu" in participants
