"""UI tests for unregister/delete functionality.

Tests participant deletion including:
- Delete button interaction
- Confirmation dialog handling
- Cancel confirmation behavior
- Participant list updates
"""

import pytest
from tests.playwright.pages.activities_page import ActivitiesPage


@pytest.mark.test_id("TC-UI-UNREG-001")
@pytest.mark.e2e
def test_delete_participant_with_confirmation(activities_page: ActivitiesPage):
    """Test delete participant flow with confirmation."""
    activities_page.load()
    
    # Verify participant exists
    assert activities_page.has_participant("Chess Club", "michael@mergington.edu")
    
    # Delete with confirmation
    activities_page.delete_participant("michael@mergington.edu", "Chess Club", confirm=True)
    
    # Verify success message
    assert activities_page.is_success_message()
    
    # Verify participant removed
    assert not activities_page.has_participant("Chess Club", "michael@mergington.edu")


@pytest.mark.test_id("TC-UI-UNREG-002")
@pytest.mark.e2e
def test_delete_participant_cancel_confirmation(activities_page: ActivitiesPage):
    """Test canceling delete keeps participant."""
    activities_page.load()
    
    # Verify participant exists
    assert activities_page.has_participant("Chess Club", "michael@mergington.edu")
    
    # Delete but cancel
    activities_page.delete_participant("michael@mergington.edu", "Chess Club", confirm=False)
    
    # Verify participant still present
    assert activities_page.has_participant("Chess Club", "michael@mergington.edu")


@pytest.mark.test_id("TC-UI-UNREG-003")
@pytest.mark.e2e
def test_delete_syncs_across_languages(activities_page: ActivitiesPage):
    """Test that delete in one language removes from the other."""
    activities_page.load()
    
    # Add participant via English
    activities_page.signup("delete_lang@mergington.edu", "Chess Club")
    assert activities_page.has_participant("Chess Club", "delete_lang@mergington.edu")
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Verify participant in Hungarian
    assert activities_page.has_participant("Sakk Klub", "delete_lang@mergington.edu")
    
    # Delete in Hungarian
    activities_page.delete_participant("delete_lang@mergington.edu", "Sakk Klub", confirm=True)
    
    # Verify removed in Hungarian
    assert not activities_page.has_participant("Sakk Klub", "delete_lang@mergington.edu")
    
    # Switch to English
    activities_page.switch_to_language("en")
    
    # Verify removed in English
    assert not activities_page.has_participant("Chess Club", "delete_lang@mergington.edu")


@pytest.mark.test_id("TC-UI-UNREG-004")
@pytest.mark.e2e
def test_unregister_then_signup_again(activities_page: ActivitiesPage):
    """Test that a student can unregister and then sign up again."""
    activities_page.load()
    
    # Unregister
    activities_page.delete_participant("john@mergington.edu", "Gym Class", confirm=True)
    assert not activities_page.has_participant("Gym Class", "john@mergington.edu")
    
    # Sign up again
    activities_page.signup("john@mergington.edu", "Gym Class")
    
    # Verify success
    assert activities_page.is_success_message()
    assert activities_page.has_participant("Gym Class", "john@mergington.edu")


@pytest.mark.test_id("TC-UI-UNREG-005")
@pytest.mark.e2e
def test_delete_in_hungarian(activities_page: ActivitiesPage):
    """Test delete functionality in Hungarian language."""
    activities_page.load()
    activities_page.switch_to_language("hu")
    
    # Verify participant exists
    assert activities_page.has_participant("Sakk Klub", "michael@mergington.edu")
    
    # Delete
    activities_page.delete_participant("michael@mergington.edu", "Sakk Klub", confirm=True)
    
    # Verify Hungarian success message
    assert activities_page.is_success_message()
    message = activities_page.get_success_message()
    assert "michael@mergington.edu sikeresen kijelentkezve" in message
    
    # Verify removed
    assert not activities_page.has_participant("Sakk Klub", "michael@mergington.edu")


@pytest.mark.test_id("TC-UI-UNREG-006")
@pytest.mark.e2e
def test_delete_last_participant_shows_no_participants_message(activities_page: ActivitiesPage):
    """Test that deleting last participant shows 'no participants' message."""
    activities_page.load()
    
    # Delete existing participant from Swimming Club (has only 1)
    activities_page.delete_participant("ryan@mergington.edu", "Swimming Club", confirm=True)
    
    # Verify "no participants" message appears
    card = activities_page.get_activity_card("Swimming Club")
    no_participants_msg = card.locator(".no-participants")
    expect(no_participants_msg).to_be_visible()
