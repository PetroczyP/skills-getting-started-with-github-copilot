"""UI tests for language switching functionality.

Tests the bilingual (English/Hungarian) interface including:
- Language toggle functionality
- localStorage persistence
- Translation of all UI elements
- Participant synchronization across languages
"""

import pytest
from playwright.sync_api import expect
from tests.playwright.pages.activities_page import ActivitiesPage


@pytest.mark.test_id("TC-UI-LANG-001")
@pytest.mark.e2e
@pytest.mark.language
def test_language_switch_updates_page_title(activities_page: ActivitiesPage):
    """Test that switching language updates page title."""
    # Load page and verify default English
    activities_page.load()
    title = activities_page.page_title
    expect(title).to_have_text("Extracurricular Activities")
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    expect(title).to_have_text("Tanórán Kívüli Tevékenységek")
    
    # Switch back to English
    activities_page.switch_to_language("en")
    expect(title).to_have_text("Extracurricular Activities")


@pytest.mark.test_id("TC-UI-LANG-002")
@pytest.mark.e2e
@pytest.mark.language
def test_language_persists_in_localStorage(activities_page: ActivitiesPage):
    """Test that language preference is saved to localStorage."""
    activities_page.load()
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Verify localStorage
    lang = activities_page.get_current_language()
    assert lang == "hu"
    
    # Reload page
    activities_page.reload()
    activities_page.wait_for_activities_loaded()
    
    # Verify language persisted
    title = activities_page.page_title
    expect(title).to_have_text("Tanórán Kívüli Tevékenységek")
    assert activities_page.get_current_language() == "hu"


@pytest.mark.test_id("TC-UI-LANG-003")
@pytest.mark.e2e
@pytest.mark.language
def test_signup_syncs_across_languages(activities_page: ActivitiesPage):
    """Test signup in one language appears in the other."""
    activities_page.load()
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Signup for "Sakk Klub"
    activities_page.signup("bilingual@mergington.edu", "Sakk Klub")
    
    # Verify success message
    assert activities_page.is_success_message()
    
    # Verify in Hungarian
    assert activities_page.has_participant("Sakk Klub", "bilingual@mergington.edu")
    
    # Switch to English
    activities_page.switch_to_language("en")
    
    # Verify appears in "Chess Club"
    assert activities_page.has_participant("Chess Club", "bilingual@mergington.edu")


@pytest.mark.test_id("TC-UI-LANG-004")
@pytest.mark.e2e
@pytest.mark.language
def test_all_ui_elements_translated(activities_page: ActivitiesPage):
    """Test that all UI elements are translated when switching language."""
    activities_page.load()
    
    # Verify English elements
    expect(activities_page.page_title).to_have_text("Extracurricular Activities")
    expect(activities_page.signup_title).to_have_text("Sign Up for an Activity")
    
    # Check email label
    email_label = activities_page.page.locator('label[for="email"]')
    expect(email_label).to_have_text("Student Email:")
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Verify Hungarian elements
    expect(activities_page.page_title).to_have_text("Tanórán Kívüli Tevékenységek")
    expect(activities_page.signup_title).to_have_text("Jelentkezés Tevékenységre")
    expect(email_label).to_have_text("Diák Email címe:")


@pytest.mark.test_id("TC-UI-LANG-005")
@pytest.mark.e2e
@pytest.mark.language
def test_activity_names_update_in_dropdown(activities_page: ActivitiesPage):
    """Test that activity names in dropdown update when switching language."""
    activities_page.load()
    
    # Verify English activities in dropdown
    options = activities_page.get_activity_dropdown_options()
    assert "Chess Club" in options
    assert "Programming Class" in options
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Verify Hungarian activities in dropdown
    options_hu = activities_page.get_activity_dropdown_options()
    assert "Sakk Klub" in options_hu
    assert "Programozás Tanfolyam" in options_hu
    assert "Chess Club" not in options_hu


@pytest.mark.test_id("TC-UI-LANG-006")
@pytest.mark.e2e
@pytest.mark.language
def test_delete_syncs_across_languages(activities_page: ActivitiesPage):
    """Test that deleting in one language removes from the other."""
    activities_page.load()
    
    # Sign up in English
    activities_page.signup("delete_sync@mergington.edu", "Chess Club")
    assert activities_page.has_participant("Chess Club", "delete_sync@mergington.edu")
    
    # Switch to Hungarian
    activities_page.switch_to_language("hu")
    
    # Verify participant in Hungarian
    assert activities_page.has_participant("Sakk Klub", "delete_sync@mergington.edu")
    
    # Delete in Hungarian
    activities_page.delete_participant("delete_sync@mergington.edu", "Sakk Klub", confirm=True)
    
    # Verify removed in Hungarian
    assert not activities_page.has_participant("Sakk Klub", "delete_sync@mergington.edu")
    
    # Switch back to English
    activities_page.switch_to_language("en")
    
    # Verify removed in English
    assert not activities_page.has_participant("Chess Club", "delete_sync@mergington.edu")
