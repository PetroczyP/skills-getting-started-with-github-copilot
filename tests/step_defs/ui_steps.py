"""BDD step definitions for Playwright UI tests.

This module provides pytest-bdd step definitions for UI testing scenarios.
"""

from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import Page, expect
from tests.playwright.pages.activities_page import ActivitiesPage
import requests


# Load all scenarios from UI feature files
scenarios('../features/ui/language_switching.feature')
scenarios('../features/ui/participant_management.feature')
scenarios('../features/ui/activity_display.feature')


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

@given("I am on the activities page")
def navigate_to_activities_page(activities_page: ActivitiesPage):
    """Navigate to the activities page."""
    activities_page.load()


@given("the page has loaded completely")
def page_loaded(activities_page: ActivitiesPage):
    """Ensure page has fully loaded."""
    activities_page.wait_for_activities_loaded()


@given(parsers.parse('the page is displayed in "{language}"'))
def set_page_language(activities_page: ActivitiesPage, language: str):
    """Set the page language."""
    activities_page.switch_to_language(language)


@given(parsers.parse('I have email "{email}"'))
def store_email(context, email: str):
    """Store email in context."""
    context["email"] = email


@given(parsers.parse('I can see "{activity}" in the activities list'))
def verify_activity_visible(activities_page: ActivitiesPage, activity: str):
    """Verify activity is visible in the list."""
    card = activities_page.get_activity_card(activity)
    expect(card).to_be_visible()


@given(parsers.parse('"{activity}" has participant "{email}"'))
def verify_participant_exists(activities_page: ActivitiesPage, activity: str, email: str):
    """Verify participant exists in activity."""
    assert activities_page.has_participant(activity, email)


@given(parsers.parse('I sign up for "{activity}" with email "{email}"'))
def signup_for_activity(activities_page: ActivitiesPage, activity: str, email: str):
    """Sign up for an activity."""
    activities_page.signup(email, activity)
    activities_page.wait_for_timeout(500)


@given(parsers.parse('"{activity}" is at full capacity'))
def fill_activity_to_capacity(activities_page: ActivitiesPage, activity: str):
    """Fill activity to maximum capacity using API."""
    # Get activity info
    response = requests.get(f"http://localhost:8000/activities?lang=en")
    activity_data = response.json()[activity]
    
    max_participants = activity_data["max_participants"]
    current_count = len(activity_data["participants"])
    slots_available = max_participants - current_count
    
    # Fill via API for speed
    for i in range(slots_available):
        requests.post(
            f"http://localhost:8000/activities/{activity}/signup?lang=en",
            json={"email": f"capacity_{i}@mergington.edu"}
        )
    
    # Reload page to show updated state
    activities_page.reload()
    activities_page.wait_for_activities_loaded()


@given(parsers.parse('"{activity}" has {count:d} participants'))
@given(parsers.parse('"{activity}" has {count:d} current participants'))
def verify_participant_count(activities_page: ActivitiesPage, activity: str, count: int):
    """Verify activity has specific participant count."""
    actual_count = activities_page.get_participant_count(activity)
    assert actual_count == count, f"Expected {count} participants, got {actual_count}"


@given(parsers.parse('"{activity}" has max participants of {max_count:d}'))
def verify_max_participants(activity: str, max_count: int):
    """Verify activity's max participant count."""
    response = requests.get(f"http://localhost:8000/activities?lang=en")
    activity_data = response.json()[activity]
    assert activity_data["max_participants"] == max_count


# ============================================================================
# When Steps - Actions
# ============================================================================

@when("I click the Hungarian flag button")
def click_hungarian_flag(activities_page: ActivitiesPage):
    """Click the Hungarian language button."""
    activities_page.language_hu_btn.click()
    activities_page.wait_for_timeout(200)


@when("I click the English flag button")
def click_english_flag(activities_page: ActivitiesPage):
    """Click the English language button."""
    activities_page.language_en_btn.click()
    activities_page.wait_for_timeout(200)


@when("I reload the page")
def reload_page(activities_page: ActivitiesPage):
    """Reload the current page."""
    activities_page.reload()
    activities_page.wait_for_activities_loaded()


@when("I enter my email in the signup form")
def enter_email(activities_page: ActivitiesPage, context):
    """Enter email in the signup form."""
    email = context.get("email", "test@mergington.edu")
    activities_page.email_input.fill(email)


@when(parsers.parse('I select "{activity}" from the activity dropdown'))
def select_activity(activities_page: ActivitiesPage, activity: str):
    """Select activity from dropdown."""
    activities_page.activity_select.select_option(activity)


@when("I click the signup button")
def click_signup(activities_page: ActivitiesPage):
    """Click the signup button."""
    activities_page.signup_button.click()
    activities_page.wait_for_timeout(500)


@when(parsers.parse('I sign up for "{activity}" with email "{email}"'))
def when_signup_for_activity(activities_page: ActivitiesPage, activity: str, email: str):
    """Sign up for an activity (when step)."""
    activities_page.signup(email, activity)


@when(parsers.parse('I delete participant "{email}" from "{activity}" and confirm'))
def delete_participant_confirm(activities_page: ActivitiesPage, email: str, activity: str):
    """Delete participant with confirmation."""
    activities_page.delete_participant(email, activity, confirm=True)


@when(parsers.parse('I delete participant "{email}" from "{activity}" and cancel'))
def delete_participant_cancel(activities_page: ActivitiesPage, email: str, activity: str):
    """Delete participant but cancel confirmation."""
    activities_page.delete_participant(email, activity, confirm=False)


@when(parsers.parse('I delete the last participant from "{activity}"'))
def delete_last_participant(activities_page: ActivitiesPage, activity: str):
    """Delete the last remaining participant."""
    participants = activities_page.get_participants(activity)
    if participants:
        activities_page.delete_participant(participants[0], activity, confirm=True)


@when(parsers.parse('I wait for {seconds:d} seconds'))
def wait_seconds(activities_page: ActivitiesPage, seconds: int):
    """Wait for specified seconds."""
    activities_page.wait_for_timeout(seconds * 1000)


# ============================================================================
# Then Steps - Assertions
# ============================================================================

@then(parsers.parse('the page should be displayed in "{language}"'))
def verify_page_language(activities_page: ActivitiesPage, language: str):
    """Verify page is in specified language."""
    current_lang = activities_page.get_current_language()
    expected_lang = "hu" if language.lower() == "hungarian" else "en"
    assert current_lang == expected_lang


@then(parsers.parse('the page title should be "{title}"'))
def verify_page_title(activities_page: ActivitiesPage, title: str):
    """Verify page title text."""
    actual_title = activities_page.get_page_title_text()
    assert actual_title == title, f"Expected '{title}', got '{actual_title}'"


@then(parsers.parse('the signup title should be "{title}"'))
def verify_signup_title(activities_page: ActivitiesPage, title: str):
    """Verify signup section title."""
    actual_title = activities_page.get_signup_title_text()
    assert actual_title == title, f"Expected '{title}', got '{actual_title}'"


@then(parsers.parse('the language preference should be "{lang}" in localStorage'))
def verify_localStorage_language(activities_page: ActivitiesPage, lang: str):
    """Verify language in localStorage."""
    current_lang = activities_page.get_current_language()
    assert current_lang == lang


@then(parsers.parse('I can see "{activity}" in the activities list'))
def then_verify_activity_visible(activities_page: ActivitiesPage, activity: str):
    """Verify activity is visible (then step)."""
    card = activities_page.get_activity_card(activity)
    expect(card).to_be_visible()


@then(parsers.parse('I cannot see "{activity}" in the activities list'))
def verify_activity_not_visible(activities_page: ActivitiesPage, activity: str):
    """Verify activity is not visible."""
    card = activities_page.get_activity_card(activity)
    expect(card).not_to_be_visible()


@then(parsers.parse('"{activity}" should have participant "{email}"'))
@then(parsers.parse('"{activity}" has participant "{email}"'))
def then_verify_participant(activities_page: ActivitiesPage, activity: str, email: str):
    """Verify participant is in activity (then step)."""
    assert activities_page.has_participant(activity, email), \
        f"Expected {email} in {activity} but not found"


@then(parsers.parse('"{activity}" should not have participant "{email}"'))
def verify_participant_not_in_activity(activities_page: ActivitiesPage, activity: str, email: str):
    """Verify participant is not in activity."""
    assert not activities_page.has_participant(activity, email), \
        f"Expected {email} NOT in {activity} but found"


@then("I should see a success message")
def verify_success_message(activities_page: ActivitiesPage):
    """Verify success message is displayed."""
    assert activities_page.is_message_visible()
    assert activities_page.is_success_message()


@then("I should see an error message")
def verify_error_message(activities_page: ActivitiesPage):
    """Verify error message is displayed."""
    assert activities_page.is_message_visible()
    assert activities_page.is_error_message()


@then(parsers.parse('I should see a success message containing "{text}"'))
def verify_success_message_contains(activities_page: ActivitiesPage, text: str):
    """Verify success message contains specific text."""
    message = activities_page.get_success_message()
    assert text in message, f"Expected '{text}' in message, got '{message}'"
    assert activities_page.is_success_message()


@then(parsers.parse('the error should contain "{text}"'))
def verify_error_contains(activities_page: ActivitiesPage, text: str):
    """Verify error message contains specific text."""
    message = activities_page.get_success_message()
    assert text in message, f"Expected '{text}' in error, got '{message}'"


@then("the signup form should be reset")
def verify_form_reset(activities_page: ActivitiesPage):
    """Verify signup form is reset."""
    assert activities_page.is_form_reset()


@then(parsers.parse('I should see {count:d} activities in the list'))
def verify_activity_count(activities_page: ActivitiesPage, count: int):
    """Verify number of activities displayed."""
    cards = activities_page.page.locator('.activity-card').count()
    assert cards == count, f"Expected {count} activities, got {cards}"


@then(parsers.parse('I should see activity "{activity}"'))
def then_verify_activity_exists(activities_page: ActivitiesPage, activity: str):
    """Verify specific activity exists."""
    card = activities_page.get_activity_card(activity)
    expect(card).to_be_visible()


@then(parsers.parse('"{activity}" should display a description'))
def verify_has_description(activities_page: ActivitiesPage, activity: str):
    """Verify activity has description."""
    card = activities_page.get_activity_card(activity)
    description = card.locator('p').first
    expect(description).to_be_visible()


@then(parsers.parse('"{activity}" should display a schedule'))
def verify_has_schedule(activities_page: ActivitiesPage, activity: str):
    """Verify activity has schedule."""
    card = activities_page.get_activity_card(activity)
    schedule = card.locator('p:has-text("Schedule:")')
    expect(schedule).to_be_visible()


@then(parsers.parse('"{activity}" should display spots remaining'))
def verify_has_spots(activities_page: ActivitiesPage, activity: str):
    """Verify activity displays spots remaining."""
    card = activities_page.get_activity_card(activity)
    availability = card.locator('p:has-text("Availability:")')
    expect(availability).to_be_visible()


@then(parsers.parse('"{activity}" should display current participants'))
def verify_has_participants_section(activities_page: ActivitiesPage, activity: str):
    """Verify activity has participants section."""
    card = activities_page.get_activity_card(activity)
    participants_header = card.locator('p:has-text("Current Participants:")')
    expect(participants_header).to_be_visible()


@then(parsers.parse('"{activity}" should show {spots:d} spots remaining'))
def verify_spots_remaining(activities_page: ActivitiesPage, activity: str, spots: int):
    """Verify correct number of spots remaining."""
    actual_spots = activities_page.get_spots_left(activity)
    assert actual_spots == spots, f"Expected {spots} spots, got {actual_spots}"


@then(parsers.parse('the activity dropdown should contain {count:d} activities'))
def verify_dropdown_count(activities_page: ActivitiesPage, count: int):
    """Verify dropdown has correct number of activities."""
    options = activities_page.get_activity_dropdown_options()
    assert len(options) == count, f"Expected {count} options, got {len(options)}"


@then(parsers.parse('the activity dropdown should include "{activity}"'))
def verify_dropdown_includes(activities_page: ActivitiesPage, activity: str):
    """Verify dropdown includes specific activity."""
    options = activities_page.get_activity_dropdown_options()
    assert activity in options, f"Expected '{activity}' in dropdown"


@then(parsers.parse('"{activity}" should show "No participants yet" message'))
def verify_no_participants_message(activities_page: ActivitiesPage, activity: str):
    """Verify 'no participants' message is shown."""
    card = activities_page.get_activity_card(activity)
    message = card.locator('.no-participants')
    expect(message).to_be_visible()


@then(parsers.parse('"{activity}" should have {count:d} participants'))
def then_verify_participant_count(activities_page: ActivitiesPage, activity: str, count: int):
    """Verify activity has specific participant count (then step)."""
    actual_count = activities_page.get_participant_count(activity)
    assert actual_count == count, f"Expected {count} participants, got {actual_count}"


@then("the participant count should be updated in the UI")
def verify_ui_updated(activities_page: ActivitiesPage):
    """Verify UI has been updated (general check)."""
    # Wait for any updates to complete
    activities_page.wait_for_timeout(300)


@then("the message should be visible")
def verify_message_visible(activities_page: ActivitiesPage):
    """Verify message is visible."""
    assert activities_page.is_message_visible()


@then("the message should not be visible")
def verify_message_hidden(activities_page: ActivitiesPage):
    """Verify message is hidden."""
    assert not activities_page.is_message_visible()
