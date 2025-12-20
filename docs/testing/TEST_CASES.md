# Test Case Registry - Mergington High School Activities API

**Last Updated:** December 20, 2025  
**Total Test Cases:** 91  
**Automated:** 91 (100%)

---

## Table of Contents

1. [Root Endpoint Tests](#root-endpoint-tests)
2. [Activity Listing Tests](#activity-listing-tests)
3. [Activity Signup Tests](#activity-signup-tests)
4. [Activity Unregister Tests](#activity-unregister-tests)
5. [Capacity Management Tests](#capacity-management-tests)
6. [Language Support Tests](#language-support-tests)
7. [Infrastructure Tests](#infrastructure-tests)
8. [UI Language Switching Tests](#ui-language-switching-tests)
9. [UI Signup Tests](#ui-signup-tests)
10. [UI Unregister Tests](#ui-unregister-tests)
11. [UI Capacity Tests](#ui-capacity-tests)
12. [UI Display Tests](#ui-display-tests)

---

## Root Endpoint Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-ROOT-001 | Root endpoint redirects to static index.html | P1 | ✅ Active | ✅ Yes | [test_app.py::TestRootEndpoint::test_root_redirects_to_static](../../tests/test_app.py) |

### TC-ROOT-001: Root endpoint redirects to static index.html

**Description:** Verify that accessing the root URL (/) redirects to the static index.html page.

**Preconditions:**
- FastAPI application is running
- Static files are mounted at /static/

**Test Steps:**
1. Send GET request to `/`
2. Configure request to not follow redirects

**Expected Results:**
- Response status code: 307 (Temporary Redirect)
- Location header: `/static/index.html`

**Test Data:** None

**Tags:** `functional`, `navigation`

---

## Activity Listing Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-ACTIVITIES-001 | Get all activities in English | P1 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_returns_all_activities_en](../../tests/test_app.py) |
| TC-ACTIVITIES-002 | Get all activities in Hungarian | P1 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_returns_all_activities_hu](../../tests/test_app.py) |
| TC-ACTIVITIES-003 | Default language is English | P2 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_defaults_to_english](../../tests/test_app.py) |
| TC-ACTIVITIES-004 | Activities have correct structure | P1 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_returns_correct_structure](../../tests/test_app.py) |
| TC-ACTIVITIES-005 | Activities include participant lists | P1 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_returns_participant_lists](../../tests/test_app.py) |
| TC-LANGUAGE-001 | Participants synced across languages | P1 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_same_participants_both_languages](../../tests/test_app.py) |

### TC-ACTIVITIES-001: Get all activities in English

**Description:** Verify that GET /activities?lang=en returns all available activities in English.

**Preconditions:**
- Activities database is initialized with 9 activities
- Language parameter set to "en"

**Test Steps:**
1. Send GET request to `/activities?lang=en`
2. Parse JSON response

**Expected Results:**
- Response status code: 200
- Response contains: "Chess Club", "Programming Class", "Gym Class", "Soccer Team", "Swimming Club", "Drama Club", "Art Studio", "Debate Team", "Science Olympiad"
- All activity names in English

**Test Data:**
- Language: `en`

**Tags:** `functional`, `language`, `activities`

### TC-ACTIVITIES-002: Get all activities in Hungarian

**Description:** Verify that GET /activities?lang=hu returns all available activities in Hungarian.

**Preconditions:**
- Activities database is initialized with 9 activities
- Language parameter set to "hu"

**Test Steps:**
1. Send GET request to `/activities?lang=hu`
2. Parse JSON response

**Expected Results:**
- Response status code: 200
- Response contains: "Sakk Klub", "Programozás Tanfolyam", "Tornaterem", "Focicsapat", "Úszó Klub", "Drámakör", "Művészeti Stúdió", "Vitakör", "Tudományos Olimpia"
- All activity names in Hungarian

**Test Data:**
- Language: `hu`

**Tags:** `functional`, `language`, `activities`

---

## Activity Signup Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-SIGNUP-001 | Successful signup in English | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_signup_for_existing_activity_en](../../tests/test_app.py) |
| TC-SIGNUP-002 | Successful signup in Hungarian | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_signup_for_existing_activity_hu](../../tests/test_app.py) |
| TC-SIGNUP-003 | Signup for nonexistent activity | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_signup_for_nonexistent_activity](../../tests/test_app.py) |
| TC-SIGNUP-004 | Duplicate signup prevention | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_signup_when_already_registered](../../tests/test_app.py) |
| TC-SIGNUP-005 | Multiple students can signup | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_multiple_students_can_signup](../../tests/test_app.py) |

### TC-SIGNUP-001: Successful signup in English

**Description:** Verify that a new student can successfully sign up for an activity with available capacity (English).

**Preconditions:**
- Chess Club exists with capacity available
- Student email not already registered

**Test Steps:**
1. Send POST request to `/activities/Chess Club/signup?lang=en`
2. Include request body: `{"email": "newstudent@mergington.edu"}`
3. Verify response
4. Fetch activities list to confirm student added

**Expected Results:**
- Response status code: 200
- Response message: "Signed up newstudent@mergington.edu for Chess Club"
- Student appears in Chess Club participants list

**Test Data:**
- Activity: `Chess Club`
- Email: `newstudent@mergington.edu`
- Language: `en`

**Tags:** `functional`, `signup`, `language`

### TC-SIGNUP-002: Successful signup in Hungarian

**Description:** Verify that a new student can successfully sign up for an activity with available capacity (Hungarian).

**Preconditions:**
- Sakk Klub exists with capacity available
- Student email not already registered

**Test Steps:**
1. Send POST request to `/activities/Sakk Klub/signup?lang=hu`
2. Include request body: `{"email": "newstudent@mergington.edu"}`
3. Verify response
4. Fetch activities in both languages to confirm sync

**Expected Results:**
- Response status code: 200
- Response message: "newstudent@mergington.edu sikeresen jelentkezett: Sakk Klub"
- Student appears in both English (Chess Club) and Hungarian (Sakk Klub) participants

**Test Data:**
- Activity: `Sakk Klub`
- Email: `newstudent@mergington.edu`
- Language: `hu`

**Tags:** `functional`, `signup`, `language`

---

## Activity Unregister Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-UNREGISTER-001 | Successful unregister in English | P1 | ✅ Active | ✅ Yes | [test_app.py::TestUnregisterFromActivity::test_unregister_from_activity_en](../../tests/test_app.py) |
| TC-UNREGISTER-002 | Successful unregister in Hungarian | P1 | ✅ Active | ✅ Yes | [test_app.py::TestUnregisterFromActivity::test_unregister_from_activity_hu](../../tests/test_app.py) |
| TC-UNREGISTER-003 | Unregister from nonexistent activity | P1 | ✅ Active | ✅ Yes | [test_app.py::TestUnregisterFromActivity::test_unregister_from_nonexistent_activity](../../tests/test_app.py) |
| TC-UNREGISTER-004 | Unregister when not registered | P1 | ✅ Active | ✅ Yes | [test_app.py::TestUnregisterFromActivity::test_unregister_when_not_registered](../../tests/test_app.py) |
| TC-UNREGISTER-005 | Unregister then signup workflow | P2 | ✅ Active | ✅ Yes | [test_app.py::TestUnregisterFromActivity::test_unregister_then_signup_again](../../tests/test_app.py) |

### TC-UNREGISTER-001: Successful unregister in English

**Description:** Verify that a registered student can successfully unregister from an activity (English).

**Preconditions:**
- Student michael@mergington.edu is registered for Chess Club

**Test Steps:**
1. Send DELETE request to `/activities/Chess Club/unregister?lang=en`
2. Include request body: `{"email": "michael@mergington.edu"}`
3. Verify response
4. Fetch activities list to confirm student removed

**Expected Results:**
- Response status code: 200
- Response message: "Unregistered michael@mergington.edu from Chess Club"
- Student no longer in Chess Club participants list

**Test Data:**
- Activity: `Chess Club`
- Email: `michael@mergington.edu`
- Language: `en`

**Tags:** `functional`, `unregister`, `language`

---

## Capacity Management Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-CAPACITY-001 | Reject signup at capacity (English) | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_signup_rejected_when_activity_at_capacity_en](../../tests/test_app.py) |
| TC-CAPACITY-002 | Reject signup at capacity (Hungarian) | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_signup_rejected_when_activity_at_capacity_hu](../../tests/test_app.py) |
| TC-CAPACITY-003 | Allow signup one below capacity | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_signup_allowed_when_one_below_capacity](../../tests/test_app.py) |
| TC-CAPACITY-004 | Sequential signup capacity check | P1 | ✅ Active | ✅ Yes | [test_app.py::TestSignupForActivity::test_capacity_check_with_sequential_signups](../../tests/test_app.py) |

### TC-CAPACITY-001: Reject signup at capacity (English)

**Description:** Verify that signup is rejected when activity has reached max_participants (English).

**Preconditions:**
- Chess Club has max_participants = 12
- Chess Club has initial participants (from fixture)

**Test Steps:**
1. Fetch current Chess Club participant count
2. Calculate available slots: max_participants - initial_count
3. Fill all available slots with unique test emails (capacity_test_N@mergington.edu)
4. Verify activity is at capacity
5. Attempt to sign up one more student (capacity_overflow@mergington.edu)
6. Verify rejection

**Expected Results:**
- First N signups succeed (status 200)
- Final signup fails with status 400
- Error detail: "Activity is full"
- Overflow student NOT in participants list
- Participant count remains at max_participants

**Test Data:**
- Activity: `Chess Club` (max: 12)
- Fill emails: `capacity_test_0@mergington.edu` through `capacity_test_N@mergington.edu`
- Overflow email: `capacity_overflow@mergington.edu`
- Language: `en`

**Tags:** `functional`, `capacity`, `edge-case`

**Notes:**
- Test uses helper method `_get_activity_info()` to fetch current state
- Relies on `reset_participants` fixture for consistent initial state
- Guard assertion checks slots_available > 0

---

## Language Support Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-LANGUAGE-001 | Participants synced across languages | P1 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_same_participants_both_languages](../../tests/test_app.py) |
| TC-LANGUAGE-002 | English default language | P2 | ✅ Active | ✅ Yes | [test_app.py::TestGetActivities::test_get_activities_defaults_to_english](../../tests/test_app.py) |

---

## Infrastructure Tests

### Module Import Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-IMPORT-001 | Import app module | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_import_app_module](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-002 | Import constants module | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_import_constants_module](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-003 | Import validators module | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_import_validators_module](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-004 | Import models module | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_import_models_module](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-005 | Import service module | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_import_service_module](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-006 | Import exceptions module | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_import_exceptions_module](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-007 | All constants available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_all_constants_available](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-008 | All validators available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_all_validators_available](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-009 | All models available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_all_models_available](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-010 | All exceptions available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_all_exceptions_available](../../tests/test_infrastructure.py) |
| TC-INFRA-IMPORT-011 | Service class available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestModuleImports::test_service_class_available](../../tests/test_infrastructure.py) |

### Application Creation Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-APP-001 | App instance exists | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestApplicationCreation::test_app_instance_exists](../../tests/test_infrastructure.py) |
| TC-INFRA-APP-002 | App has routes | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestApplicationCreation::test_app_has_routes](../../tests/test_infrastructure.py) |
| TC-INFRA-APP-003 | Static files mounted | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestApplicationCreation::test_app_has_static_files_mounted](../../tests/test_infrastructure.py) |
| TC-INFRA-APP-004 | Pydantic models defined | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestApplicationCreation::test_pydantic_models_defined](../../tests/test_infrastructure.py) |

### Data Structure Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-DATA-001 | Activity data structures exist | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDataStructures::test_activities_data_structures_exist](../../tests/test_infrastructure.py) |
| TC-INFRA-DATA-002 | Activity mappings exist | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDataStructures::test_activity_mappings_exist](../../tests/test_infrastructure.py) |
| TC-INFRA-DATA-003 | Participants storage exists | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDataStructures::test_participants_storage_exists](../../tests/test_infrastructure.py) |
| TC-INFRA-DATA-004 | Messages dictionary exists | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDataStructures::test_messages_dictionary_exists](../../tests/test_infrastructure.py) |
| TC-INFRA-DATA-005 | Activity structure valid | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDataStructures::test_activity_structure_valid](../../tests/test_infrastructure.py) |
| TC-INFRA-DATA-006 | Bidirectional name mapping | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDataStructures::test_activity_name_mapping_bidirectional](../../tests/test_infrastructure.py) |

### Dependency Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-DEPS-001 | FastAPI available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDependencies::test_fastapi_available](../../tests/test_infrastructure.py) |
| TC-INFRA-DEPS-002 | Pydantic available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDependencies::test_pydantic_available](../../tests/test_infrastructure.py) |
| TC-INFRA-DEPS-003 | EmailStr validator available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDependencies::test_pydantic_email_validator_available](../../tests/test_infrastructure.py) |
| TC-INFRA-DEPS-004 | Uvicorn available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDependencies::test_uvicorn_available](../../tests/test_infrastructure.py) |
| TC-INFRA-DEPS-005 | Pytest available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDependencies::test_pytest_available](../../tests/test_infrastructure.py) |
| TC-INFRA-DEPS-006 | HTTPX available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestDependencies::test_httpx_available](../../tests/test_infrastructure.py) |

### Static Files Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-FILES-001 | Static directory exists | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestStaticFiles::test_static_directory_exists](../../tests/test_infrastructure.py) |
| TC-INFRA-FILES-002 | Required static files exist | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestStaticFiles::test_static_files_exist](../../tests/test_infrastructure.py) |
| TC-INFRA-FILES-003 | index.html valid | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestStaticFiles::test_index_html_valid](../../tests/test_infrastructure.py) |
| TC-INFRA-FILES-004 | app.js valid | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestStaticFiles::test_app_js_valid](../../tests/test_infrastructure.py) |

### Endpoint Function Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-ENDPOINT-001 | ActivityService.get_all_activities | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestEndpointFunctions::test_activity_service_get_all_activities](../../tests/test_infrastructure.py) |

### Validator Function Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-VALIDATOR-001 | Validate and translate activity name | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestValidatorFunctions::test_validate_and_translate_activity_name](../../tests/test_infrastructure.py) |
| TC-INFRA-VALIDATOR-002 | Validate capacity available | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestValidatorFunctions::test_validate_capacity_available](../../tests/test_infrastructure.py) |

### Server Startup Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-SERVER-001 | Server can start via TestClient | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestServerStartup::test_server_can_start_via_test_client](../../tests/test_infrastructure.py) |
| TC-INFRA-SERVER-002 | Server responds to requests | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestServerStartup::test_server_responds_to_requests](../../tests/test_infrastructure.py) |

### Code Quality Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-INFRA-QUALITY-001 | No syntax errors in app.py | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestCodeQuality::test_no_syntax_errors_in_app](../../tests/test_infrastructure.py) |
| TC-INFRA-QUALITY-002 | No syntax errors in validators.py | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestCodeQuality::test_no_syntax_errors_in_validators](../../tests/test_infrastructure.py) |
| TC-INFRA-QUALITY-003 | No syntax errors in constants.py | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestCodeQuality::test_no_syntax_errors_in_constants](../../tests/test_infrastructure.py) |
| TC-INFRA-QUALITY-004 | All imports resolve | P1 | ✅ Active | ✅ Yes | [test_infrastructure.py::TestCodeQuality::test_all_imports_resolve](../../tests/test_infrastructure.py) |

---

## UI Language Switching Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-UI-LANG-001 | Language switch updates page title | P1 | ✅ Active | ✅ Yes | [test_ui_language.py::test_language_switch_updates_page_title](../../tests/playwright/test_ui_language.py) |
| TC-UI-LANG-002 | Language persists in localStorage | P1 | ✅ Active | ✅ Yes | [test_ui_language.py::test_language_persists_in_localStorage](../../tests/playwright/test_ui_language.py) |
| TC-UI-LANG-003 | Signup syncs across languages | P1 | ✅ Active | ✅ Yes | [test_ui_language.py::test_signup_syncs_across_languages](../../tests/playwright/test_ui_language.py) |
| TC-UI-LANG-004 | All UI elements translated | P1 | ✅ Active | ✅ Yes | [test_ui_language.py::test_all_ui_elements_translated](../../tests/playwright/test_ui_language.py) |
| TC-UI-LANG-005 | Activity names update in dropdown | P1 | ✅ Active | ✅ Yes | [test_ui_language.py::test_activity_names_update_in_dropdown](../../tests/playwright/test_ui_language.py) |
| TC-UI-LANG-006 | Delete syncs across languages | P1 | ✅ Active | ✅ Yes | [test_ui_language.py::test_delete_syncs_across_languages](../../tests/playwright/test_ui_language.py) |

---

## UI Signup Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-UI-SIGNUP-001 | Signup form submission | P1 | ✅ Active | ✅ Yes | [test_ui_signup.py::test_signup_form_submission](../../tests/playwright/test_ui_signup.py) |
| TC-UI-SIGNUP-002 | Invalid email validation | P1 | ✅ Active | ✅ Yes | [test_ui_signup.py::test_signup_with_invalid_email](../../tests/playwright/test_ui_signup.py) |
| TC-UI-SIGNUP-003 | Duplicate signup error | P1 | ✅ Active | ✅ Yes | [test_ui_signup.py::test_duplicate_signup_shows_error](../../tests/playwright/test_ui_signup.py) |
| TC-UI-SIGNUP-004 | Multiple students can signup | P1 | ✅ Active | ✅ Yes | [test_ui_signup.py::test_multiple_students_can_signup](../../tests/playwright/test_ui_signup.py) |
| TC-UI-SIGNUP-005 | Signup in Hungarian | P1 | ✅ Active | ✅ Yes | [test_ui_signup.py::test_signup_in_hungarian](../../tests/playwright/test_ui_signup.py) |
| TC-UI-SIGNUP-006 | Activities list refreshes after signup | P1 | ✅ Active | ✅ Yes | [test_ui_signup.py::test_activities_list_refreshes_after_signup](../../tests/playwright/test_ui_signup.py) |

---

## UI Unregister Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-UI-UNREG-001 | Delete with confirmation | P1 | ✅ Active | ✅ Yes | [test_ui_unregister.py::test_delete_participant_with_confirmation](../../tests/playwright/test_ui_unregister.py) |
| TC-UI-UNREG-002 | Cancel delete confirmation | P1 | ✅ Active | ✅ Yes | [test_ui_unregister.py::test_delete_participant_cancel_confirmation](../../tests/playwright/test_ui_unregister.py) |
| TC-UI-UNREG-003 | Delete syncs across languages | P1 | ✅ Active | ✅ Yes | [test_ui_unregister.py::test_delete_syncs_across_languages](../../tests/playwright/test_ui_unregister.py) |
| TC-UI-UNREG-004 | Unregister then signup workflow | P1 | ✅ Active | ✅ Yes | [test_ui_unregister.py::test_unregister_then_signup_again](../../tests/playwright/test_ui_unregister.py) |
| TC-UI-UNREG-005 | Delete in Hungarian | P1 | ✅ Active | ✅ Yes | [test_ui_unregister.py::test_delete_in_hungarian](../../tests/playwright/test_ui_unregister.py) |
| TC-UI-UNREG-006 | Delete last participant message | P1 | ✅ Active | ✅ Yes | [test_ui_unregister.py::test_delete_last_participant_shows_no_participants_message](../../tests/playwright/test_ui_unregister.py) |

---

## UI Capacity Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-UI-CAPACITY-001 | Error when activity full | P1 | ✅ Active | ✅ Yes | [test_ui_capacity.py::test_signup_shows_error_when_full](../../tests/playwright/test_ui_capacity.py) |
| TC-UI-CAPACITY-002 | Signup allowed one below capacity | P1 | ✅ Active | ✅ Yes | [test_ui_capacity.py::test_signup_allowed_when_one_below_capacity](../../tests/playwright/test_ui_capacity.py) |
| TC-UI-CAPACITY-003 | Capacity error in Hungarian | P1 | ✅ Active | ✅ Yes | [test_ui_capacity.py::test_capacity_error_in_hungarian](../../tests/playwright/test_ui_capacity.py) |
| TC-UI-CAPACITY-004 | Spots update after signup | P1 | ✅ Active | ✅ Yes | [test_ui_capacity.py::test_spots_remaining_updates_after_signup](../../tests/playwright/test_ui_capacity.py) |
| TC-UI-CAPACITY-005 | Spots update after delete | P1 | ✅ Active | ✅ Yes | [test_ui_capacity.py::test_spots_remaining_updates_after_delete](../../tests/playwright/test_ui_capacity.py) |

---

## UI Display Tests

| Test ID | Title | Priority | Status | Automated | Location |
|---------|-------|----------|--------|-----------|----------|
| TC-UI-DISPLAY-001 | All activities displayed | P1 | ✅ Active | ✅ Yes | [test_ui_display.py::test_all_activities_displayed](../../tests/playwright/test_ui_display.py) |
| TC-UI-DISPLAY-002 | Activity card shows all info | P1 | ✅ Active | ✅ Yes | [test_ui_display.py::test_activity_card_shows_all_information](../../tests/playwright/test_ui_display.py) |
| TC-UI-DISPLAY-003 | Spots left calculation | P1 | ✅ Active | ✅ Yes | [test_ui_display.py::test_spots_left_calculation](../../tests/playwright/test_ui_display.py) |
| TC-UI-DISPLAY-004 | No participants message | P1 | ✅ Active | ✅ Yes | [test_ui_display.py::test_no_participants_message](../../tests/playwright/test_ui_display.py) |
| TC-UI-DISPLAY-005 | Participant count updates | P1 | ✅ Active | ✅ Yes | [test_ui_display.py::test_participant_count_updates_after_signup](../../tests/playwright/test_ui_display.py) |
| TC-UI-DISPLAY-006 | Dropdown contains all activities | P1 | ✅ Active | ✅ Yes | [test_ui_display.py::test_dropdown_contains_all_activities](../../tests/playwright/test_ui_display.py) |
| TC-UI-DISPLAY-007 | Hungarian activities displayed | P1 | ✅ Active | ✅ Yes | [test_ui_display.py::test_hungarian_activities_displayed](../../tests/playwright/test_ui_display.py) |

---

## Test Execution Summary

### By Priority

| Priority | Count | Percentage |
|----------|-------|------------|
| P1 (Critical) | 88 | 97% |
| P2 (High) | 3 | 3% |
| P3 (Medium) | 0 | 0% |

### By Status

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Active | 91 | 100% |
| 🚧 Pending | 0 | 0% |
| ❌ Deprecated | 0 | 0% |

### By Automation

| Type | Count | Percentage |
|------|-------|------------|
| ✅ Automated | 91 | 100% |
| ⚠️ Manual | 0 | 0% |

---

## How to Add New Test Cases

### 1. Determine Next Test ID

- Review this document for existing IDs in your area
- Use next sequential number: `TC-[AREA]-XXX`
- Check for gaps from deprecated tests (can reuse)

### 2. Add Test to Code

```python
import pytest

@pytest.mark.test_id("TC-SIGNUP-006")  # ← Add test ID decorator
@pytest.mark.functional
@pytest.mark.signup
def test_new_feature(client):
    """Brief description of what this tests."""
    # Test implementation
```

### 3. Document in This File

Add entry to appropriate section with:
- Test ID
- Title
- Priority (P1/P2/P3)
- Status (Active/Pending/Deprecated)
- Automation status
- Location (file::class::function)

Add detailed section with:
- Description
- Preconditions
- Test steps
- Expected results
- Test data
- Tags

### 4. Update Traceability Matrix

Link test case to requirement in [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md).

### 5. Run Pre-Commit Hook

Hook will validate:
- Test ID decorator exists
- ID follows correct format
- No duplicate IDs
- All tests pass

---

**Last Review:** December 20, 2025  
**Next Review:** March 20, 2026
