"""
BDD Step Definitions for Activity Signup Feature

Maps Gherkin steps from activity_signup.feature to test code.
"""

from pytest_bdd import scenarios, given, when, then, parsers


# Load all scenarios from the feature file
scenarios('../features/activity_signup.feature')


# ============================================================================
# Given Steps (Preconditions)
# ============================================================================

@given("the activities database is initialized")
def activities_initialized(client):
    """Verify activities database is ready (implicit via fixture)."""
    response = client.get("/activities")
    assert response.status_code == 200
    return response.json()


@given(parsers.parse('the {activity} has {count:d} existing participants'))
def activity_has_participants(client, activity, count):
    """Verify activity has expected number of initial participants."""
    response = client.get("/activities?lang=en")
    activities = response.json()
    # Map Hungarian names to English if needed
    activity_key = activity.replace("Chess Club", "Chess Club")
    assert len(activities[activity_key]["participants"]) == count


@given(parsers.parse('I am a new student with email "{email}"'))
def new_student_email(context, email):
    """Set student email in context."""
    context["email"] = email
    return email


@given(parsers.parse('student "{email}" is already registered for "{activity}"'))
def student_already_registered(client, email, activity):
    """Verify student is already in activity participants."""
    response = client.get("/activities?lang=en")
    activities = response.json()
    assert email in activities[activity]["participants"]


@given(parsers.parse('"{activity}" has capacity available'))
def activity_has_capacity(client, activity):
    """Verify activity has available spots."""
    response = client.get("/activities?lang=en")
    activities = response.json()
    current = len(activities[activity]["participants"])
    maximum = activities[activity]["max_participants"]
    assert current < maximum


# ============================================================================
# When Steps (Actions)
# ============================================================================

@when(parsers.parse('I sign up for "{activity}" in "{language}"'))
def signup_for_activity(client, context, activity, language):
    """Execute signup request."""
    lang = "en" if language == "English" else "hu"
    email = context.get("email", "test@mergington.edu")
    response = client.post(
        f"/activities/{activity}/signup?lang={lang}",
        json={"email": email}
    )
    context["response"] = response
    context["activity"] = activity
    context["language"] = language
    return response


@when(parsers.parse('I sign up for "{activity}" in "{language}" with email "{email}"'))
def signup_with_specific_email(client, context, activity, language, email):
    """Execute signup with specific email."""
    lang = "en" if language == "English" else "hu"
    response = client.post(
        f"/activities/{activity}/signup?lang={lang}",
        json={"email": email}
    )
    context["response"] = response
    context["email"] = email
    return response


@when(parsers.parse('student "{email}" signs up for "{activity}" in "{language}"'))
def student_signs_up(client, context, email, activity, language):
    """Student signs up for activity."""
    lang = "en" if language == "English" else "hu"
    response = client.post(
        f"/activities/{activity}/signup?lang={lang}",
        json={"email": email}
    )
    # Store in context list for multiple signups
    if "responses" not in context:
        context["responses"] = []
    context["responses"].append({"email": email, "response": response})
    return response


# ============================================================================
# Then Steps (Assertions)
# ============================================================================

@then(parsers.parse('the signup should succeed with status code {code:d}'))
def signup_succeeds(context, code):
    """Verify signup succeeded."""
    response = context.get("response")
    assert response.status_code == code


@then(parsers.parse('the signup should fail with status code {code:d}'))
def signup_fails(context, code):
    """Verify signup failed with expected status."""
    response = context.get("response")
    assert response.status_code == code


@then(parsers.parse('I should see confirmation message containing "{message}"'))
def see_confirmation_message(context, message):
    """Verify confirmation message contains expected text."""
    response = context.get("response")
    data = response.json()
    assert message in data.get("message", "")


@then(parsers.parse('I should see error message "{message}"'))
def see_error_message(context, message):
    """Verify error message matches expected."""
    response = context.get("response")
    data = response.json()
    assert message == data.get("detail", "")


@then(parsers.parse('"{activity}" in "{language}" should have {count:d} participants'))
def activity_has_participant_count(client, activity, language, count):
    """Verify activity has expected participant count."""
    lang = "en" if language == "English" else "hu"
    response = client.get(f"/activities?lang={lang}")
    activities = response.json()
    assert len(activities[activity]["participants"]) == count


@then(parsers.parse('"{email}" should be in "{activity}" participants'))
def email_in_participants(client, email, activity):
    """Verify email is in activity participants list."""
    response = client.get("/activities?lang=en")
    activities = response.json()
    # Map Hungarian activity names to English
    activity_map = {"Sakk Klub": "Chess Club"}
    activity_key = activity_map.get(activity, activity)
    assert email in activities[activity_key]["participants"]


@then("both signups should succeed")
def both_signups_succeed(context):
    """Verify all signups in responses list succeeded."""
    for item in context.get("responses", []):
        assert item["response"].status_code == 200


@then(parsers.parse('"{activity}" should include both "{email1}" and "{email2}"'))
def activity_includes_both_emails(client, activity, email1, email2):
    """Verify both emails are in activity participants."""
    response = client.get("/activities?lang=en")
    activities = response.json()
    participants = activities[activity]["participants"]
    assert email1 in participants
    assert email2 in participants


@then(parsers.parse('"{email}" should be in "{activity}" participants in "{language}"'))
def email_in_participants_lang(client, email, activity, language):
    """Verify email in participants for specific language."""
    lang = "en" if language == "English" else "hu"
    response = client.get(f"/activities?lang={lang}")
    activities = response.json()
    assert email in activities[activity]["participants"]
