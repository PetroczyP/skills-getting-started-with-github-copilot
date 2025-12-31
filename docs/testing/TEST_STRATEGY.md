# Test Strategy - Mergington High School Activities API

**Last Updated:** December 28, 2025  
**Version:** 1.1  
**Maintainer:** Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Philosophy](#testing-philosophy)
3. [Test Organization](#test-organization)
4. [BDD Framework](#bdd-framework)
5. [UI Testing with Playwright](#ui-testing-with-playwright)
7. [Test Markers and Categories](#test-markers-and-categories)
8. [Test ID Convention](#test-id-convention)
9. [Maintainability for AI-Assisted Development](#maintainability-for-ai-assisted-development)
10. [Coverage Requirements](#coverage-requirements)
11. [Maintainability for AI-Assisted Development](#maintainability-for-ai-assisted-development)
8. [Coverage Requirements](#coverage-requirements)
9. [How to Maintain This Documentation](#how-to-maintain-this-documentation)

---

## Overview

The Mergington High School Activities API uses a **hybrid testing approach** combining traditional pytest tests with Behavior-Driven Development (BDD) using Gherkin scenarios and end-to-end UI testing with Playwright. This strategy ensures:

- **Technical validation** via comprehensive automated tests (90+ tests)
- **UI validation** via Playwright browser automation (30+ tests)
- **Stakeholder communication** via readable Gherkin feature files
- **AI discoverability** via structured documentation in [.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- **Quality enforcement** via pre-commit hooks

---

## Testing Philosophy

### Four-Tier Testing Approach

1. **Infrastructure Tests** (`tests/test_infrastructure.py`) - 40+ tests
   - **Purpose:** Catch setup and import errors before runtime
   - **Run First:** Execute before starting the dev server to prevent debugging failures
   - **Coverage:** Module imports, dependencies, data structures, static files, server startup, code quality

2. **Functional Tests** (`tests/test_app.py`) - 21+ tests
   - **Purpose:** Validate API endpoint behavior and business logic
   - **Focus:** CRUD operations, capacity enforcement, dual-language support, edge cases
   - **Pattern:** Class-based organization (TestRootEndpoint, TestGetActivities, TestSignupForActivity, TestUnregisterFromActivity)

3. **UI/E2E Tests** (`tests/playwright/`) - 30+ tests
   - **Purpose:** Validate end-user workflows via browser automation
   - **Focus:** Language switching, signup/unregister UI, capacity display, form validation
   - **Pattern:** Page Object Model with fixtures for state management
   - **Browsers:** Chromium, Firefox, WebKit

4. **BDD Tests** (`tests/features/*.feature`) - Living documentation
   - **Purpose:** Executable specifications readable by non-technical stakeholders
   - **Format:** Gherkin scenarios (Given/When/Then)
   - **Coverage:** Both API and UI critical flows
   - **Integration:** Maps to existing test logic via step definitions

### Key Testing Principles

- **Test Isolation:** Every test resets state via `reset_participants` autouse fixture
- **Test-Specific Data:** Use unique email patterns (e.g., `capacity_test_0@mergington.edu`) to avoid conflicts
- **Guard Assertions:** Capacity tests validate fixture state before testing
- **Dual-Language Testing:** All user-facing features tested in both English and Hungarian
- **Capacity Enforcement:** Explicit testing of max_participants limits with overflow scenarios

---

## Test Organization

### Directory Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and marker registration
├── test_app.py                    # 21 functional API tests
├── test_infrastructure.py         # 40+ infrastructure tests
├── playwright/                    # Playwright UI tests
│   ├── __init__.py
│   ├── conftest.py                # Playwright-specific fixtures
│   ├── test_ui_language.py        # Language switching tests
│   ├── test_ui_signup.py          # Signup form tests
│   ├── test_ui_unregister.py      # Delete participant tests
│   ├── test_ui_capacity.py        # Capacity enforcement tests
│   ├── test_ui_display.py         # Activity display tests
│   └── pages/                     # Page Object Model
│       ├── __init__.py
│       ├── base_page.py           # Base page with common methods
│       └── activities_page.py     # Activities page object
├── features/                      # BDD feature files (Gherkin)
│   ├── activity_signup.feature    # API signup scenarios
│   ├── capacity_management.feature # API capacity scenarios
│   ├── language_support.feature   # API language scenarios
│   └── ui/                        # UI BDD scenarios
│       ├── language_switching.feature
│       ├── participant_management.feature
│       └── activity_display.feature
└── step_defs/                     # BDD step definitions
    ├── __init__.py
    ├── signup_steps.py
    ├── capacity_steps.py
    ├── common_steps.py
    └── ui_steps.py                # UI scenario step definitions
```

### Test File Responsibilities

| File | Tests | Purpose |
|------|-------|---------|
| `test_app.py` | 21 | API endpoint functional tests |
| `test_infrastructure.py` | 40+ | Import, dependency, structure validation |
| `playwright/test_ui_*.py` | 30+ | UI end-to-end tests (multi-browser) |
| `features/*.feature` | N/A | Executable BDD specifications (API) |
| `features/ui/*.feature` | N/A | Executable BDD specifications (UI) |
| `step_defs/*.py` | N/A | Gherkin step implementations |

---

## BDD Framework

### When to Use BDD

**Use Gherkin .feature files for:**
- User-facing features (signup, unregister, activity listing)
- Features requiring stakeholder review
- Complex business logic needing documentation
- Acceptance criteria validation

**Use traditional pytest for:**
- Infrastructure tests (imports, dependencies)
- Internal API validation
- Edge cases and error handling
- Performance and load testing

### Feature File Structure

```gherkin
Feature: Activity Signup
  As a student
  I want to sign up for extracurricular activities
  So that I can participate in school programs

  Background:
    Given the activities database is initialized
    And the Chess Club has 2 existing participants

  Scenario: Successful signup for activity with available capacity
    Given I am a new student with email "student@mergington.edu"
    When I sign up for "Chess Club" in "English"
    Then the signup should succeed
    And I should see confirmation message "Signed up student@mergington.edu for Chess Club"
    And "Chess Club" should have 3 participants
```

### Step Definition Pattern

```python
from pytest_bdd import scenarios, given, when, then, parsers

scenarios('../features/activity_signup.feature')

@given(parsers.parse('I am a new student with email "{email}"'))
def student_email(email):
    return {"email": email}

@when(parsers.parse('I sign up for "{activity}" in "{language}"'))
def signup_for_activity(client, student_email, activity, language):
    # Call existing test logic - avoid duplication
    lang = "en" if language == "English" else "hu"
    response = client.post(
        f"/activities/{activity}/signup?lang={lang}",
        json=student_email
    )
    return response
```

---

## UI Testing with Playwright

### Overview

UI tests validate end-user workflows in real browsers using Playwright for browser automation. Tests run across **Chromium, Firefox, and WebKit** to ensure cross-browser compatibility.

### Critical Architecture: Subprocess Isolation

⚠️ **IMPORTANT**: Understanding the test architecture is essential for avoiding common pitfalls.

**How the Server Runs:**
```python
# tests/playwright/conftest.py
process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "src.app:app", ...],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
```

**Key Implications:**

1. **Separate Memory Spaces**
   - Test process: Runs pytest, fixtures, Page Objects
   - Server process: Runs FastAPI application
   - **They cannot share memory** (different Python processes)

2. **State Management Must Use API**
   ```python
   # ❌ WRONG - Only modifies test process memory
   from src.app import participants_storage
   participants_storage.clear()  # Server unchanged!
   
   # ✅ CORRECT - Modifies server state via HTTP API
   requests.delete(
       "http://localhost:8000/activities/Chess Club/unregister",
       json={"email": "student@example.com"}
   )
   ```

3. **Performance Requires Parallelization**
   - Sequential API calls: Too slow (~10+ minutes)
   - Parallel API calls: Acceptable (~2-3s overhead per test)
   - Solution: ThreadPoolExecutor with 10 workers

**Test Isolation Strategy:**

The `reset_participants` autouse fixture ensures each test starts with clean state:

```python
@pytest.fixture(autouse=True)
def reset_participants():
    # 1. Get current state from server (API call)
    response = requests.get("http://localhost:8000/activities?lang=en")
    
    # 2. Calculate minimal diff (who to add/remove)
    to_remove = current - desired
    to_add = desired - current
    
    # 3. Execute unregister in PARALLEL (fast)
    with ThreadPoolExecutor(max_workers=10) as executor:
        [executor.submit(DELETE, ...) for removal]
    
    # 4. Execute signup in PARALLEL (fast)
    with ThreadPoolExecutor(max_workers=10) as executor:
        [executor.submit(POST, ...) for addition]
```

**Why This Matters:**
- Tests that pass individually may fail in suite if state not properly reset
- Direct memory manipulation appears to work but doesn't affect server
- Performance degrades quickly with sequential API calls
- Understanding subprocess boundary is critical for debugging

### Page Object Model

Tests use the **Page Object Model (POM)** pattern to:
- Centralize selector definitions
- Encapsulate page interactions
- Reduce code duplication
- Improve test maintainability

**Example:**
```python
from tests.playwright.pages.activities_page import ActivitiesPage

def test_signup(activities_page: ActivitiesPage):
    activities_page.load()
    activities_page.signup("student@mergington.edu", "Chess Club")
    assert activities_page.is_success_message()
```

### Test Fixtures

Key Playwright fixtures in `tests/playwright/conftest.py`:

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `validate_venv` | session | Validates virtual environment active, Playwright installed |
| `start_server` | session | Starts FastAPI server, waits for health check, terminates after session |
| `activities_page` | function | Returns ActivitiesPage instance for test |
| `reset_participants` | function | Resets participants storage to default state (autouse) |
| `reset_localStorage` | function | Clears browser localStorage before each test (autouse) |
| `api_helper` | function | Provides API methods for fast test data setup |
| `fill_activity_to_capacity` | function | Fills activity to capacity via API |

### Browser Configuration

Tests run on all browsers by default:
```bash
# All browsers
./scripts/run_ui_tests.sh

# Specific browser only
./scripts/run_ui_tests.sh --browser chromium
./scripts/run_ui_tests.sh --browser firefox --headed

# Debug mode (visible browser, slow)
./scripts/run_ui_tests.sh --debug

# Parallel execution
./scripts/run_ui_tests.sh --parallel
```

**Viewport:** 1280x720  
**Locale:** en-US  
**Timezone:** UTC

### UI Test ID Convention

UI tests follow the same ID pattern with `TC-UI-` prefix:
- `TC-UI-LANG-NNN` - Language switching tests
- `TC-UI-SIGNUP-NNN` - Signup form tests
- `TC-UI-UNREG-NNN` - Unregister/delete tests
- `TC-UI-CAPACITY-NNN` - Capacity enforcement tests
- `TC-UI-DISPLAY-NNN` - Activity display tests

### State Management

**Critical:** UI tests require clean state for isolation.

Two autouse fixtures ensure this:
1. **`reset_participants`**: Resets API state (participants storage)
2. **`reset_localStorage`**: Clears browser localStorage

**API Helper for Fast Setup:**
```python
def test_capacity(activities_page, fill_activity_to_capacity):
    # Fast setup via API (not UI clicks)
    fill_activity_to_capacity("Chess Club", "en")
    
    # Reload UI to reflect state
    activities_page.reload()
    
    # Test UI behavior when full
    activities_page.signup("overflow@mergington.edu", "Chess Club")
    assert activities_page.is_error_message()
```

### Dialog Handling

For delete confirmations:
```python
activities_page.delete_participant(
    "michael@mergington.edu", 
    "Chess Club", 
    confirm=True  # Accept dialog
)

activities_page.delete_participant(
    "michael@mergington.edu", 
    "Chess Club", 
    confirm=False  # Dismiss dialog
)
```

### Running UI Tests

```bash
# Run all UI tests
pytest tests/playwright/ -v

# Run specific UI test file
pytest tests/playwright/test_ui_language.py -v

# Run by marker
pytest -m e2e
pytest -m ui

# Run on specific browser
pytest tests/playwright/ --browser chromium

# Run with visible browser (headed mode)
pytest tests/playwright/ --headed

# Run with slowmo (500ms delay between actions)
pytest tests/playwright/ --slowmo 500
```

### BDD for UI Tests

UI critical flows have Gherkin scenarios in `tests/features/ui/`:
- `language_switching.feature` - Bilingual UI workflows
- `participant_management.feature` - Signup/delete scenarios
- `activity_display.feature` - Activity list rendering

Step definitions in `tests/step_defs/ui_steps.py` use the same Page Objects.

---

## Concurrency Testing

### Overview

Race condition tests validate that the API correctly handles concurrent requests competing for limited resources (activity slots). These tests use **threading.Barrier** for precise synchronization and collect detailed timing metrics.

**Critical Business Risk:** Without race condition testing, concurrent signups can:
- Exceed max_participants capacity
- Create duplicate registrations
- Cause state corruption
- Fail silently under load

### Architecture

**Pattern:** ThreadPoolExecutor + threading.Barrier synchronization

```python
from concurrent.futures import ThreadPoolExecutor
import threading

def _concurrent_signup(client, activity_name, emails, lang, barrier, race_metrics):
    """Helper method for synchronized concurrent signups."""
    results = []
    
    def signup_thread(email):
        # Wait for all threads at barrier
        barrier.wait()
        
        # Execute signup simultaneously
        response = client.post(
            f"/activities/{activity_name}/signup?lang={lang}",
            json={"email": email}
        )
        return (email, response.status_code)
    
    with ThreadPoolExecutor(max_workers=len(emails)) as executor:
        futures = [executor.submit(signup_thread, email) for email in emails]
        results = [f.result() for f in futures]
    
    return results
```

**Key Components:**

1. **tests/race_config.py** - Environment configuration
   - CONCURRENT_THREADS = 10 (default thread count)
   - BARRIER_TIMEOUT = 30s (local), 60s (CI via env var)
   - Threshold constants for metrics validation

2. **tests/race_metrics.py** - Metrics collection
   - RaceMetricsCollector class
   - JSON export to test_metrics/race_conditions/
   - Threshold validation (barrier wait time, request spread)

3. **tests/conftest.py** - Shared fixtures
   - `race_metrics` fixture (yields RaceMetricsCollector)
   - `verify_thread_cleanup` autouse fixture (validates threads complete)
   - Marker registration for slow/concurrency tests

4. **scripts/analyze_race_metrics.py** - Post-test analysis
   - Aggregates metrics from JSON files
   - Validates thresholds
   - Generates summary reports

### Test Categories

| Test ID | Scenario | Threads | Purpose |
|---------|----------|---------|---------|
| TC-RACE-001 | Single spot race | 10 → 1 slot | Atomic capacity enforcement (worst case) |
| TC-RACE-002 | Multiple spots race | 10 → 3 slots | Multi-winner atomicity |
| TC-RACE-003 | Cross-language race | 5 EN + 5 HU | Language-agnostic capacity |
| TC-RACE-004 | Signup + unregister chaos | 15 mixed ops | State consistency under chaos |
| TC-RACE-005 | Tight timing stress | 10 (no barrier) | Real-world jitter handling |
| TC-RACE-006 | Parameterized threads | [5, 10, 20] | Scalability validation |

### Environment Configuration

**Environment Variables:**

```bash
# Barrier timeout (seconds)
RACE_TEST_BARRIER_TIMEOUT=30  # Local default
RACE_TEST_BARRIER_TIMEOUT=60  # CI recommended

# Enable/disable metrics collection
RACE_TEST_METRICS=true   # Collect timing data
RACE_TEST_METRICS=false  # Skip metrics (faster)

# Run race tests
pytest -m concurrency -v
pytest tests/test_app.py::TestRaceConditions -v
```

**Threshold Constants:**

| Threshold | Value | Purpose |
|-----------|-------|---------|
| MAX_BARRIER_WAIT_THRESHOLD | 45s | Detects CI resource exhaustion |
| MIN_REQUEST_SPREAD_THRESHOLD | 5ms | Validates true concurrency (not deterministic) |
| THREAD_CLEANUP_TIMEOUT | 5s | Maximum thread cleanup wait |

### Metrics Collection

**Automatic Metrics:** Each race test automatically collects:
- Barrier wait times (start, end, duration)
- Request execution times (per thread)
- Success/failure counts
- Request spread (time between first and last request)

**JSON Output:** Saved to `test_metrics/race_conditions/`

```json
{
  "test_id": "TC-RACE-001",
  "thread_count": 10,
  "timestamp": "20251228_204553",
  "barrier_wait": {
    "start": "2025-12-28T20:45:53.123",
    "end": "2025-12-28T20:45:53.172",
    "duration_ms": 49
  },
  "requests": [
    {"thread_id": 0, "start": "...", "end": "...", "duration_ms": 12},
    ...
  ],
  "statistics": {
    "total_requests": 10,
    "successful_requests": 1,
    "failed_requests": 9,
    "avg_duration_ms": 11.2,
    "request_spread_ms": 3.66
  }
}
```

**Analysis:**

```bash
# Analyze specific test metrics
python scripts/analyze_race_metrics.py --test-id TC-RACE-001 --verbose

# Analyze all metrics
python scripts/analyze_race_metrics.py --verbose

# Exit code: 0 = pass, 1 = threshold violations
```

### Test Execution

**Run All Race Tests:**
```bash
# All race condition tests (8 total: 6 base + 3 parameterized)
pytest tests/test_app.py::TestRaceConditions -v

# With metrics collection
RACE_TEST_METRICS=true pytest tests/test_app.py::TestRaceConditions -v

# Specific test
pytest tests/test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race -v
```

**Markers:**
- `@pytest.mark.slow` - Tests take 0.2-2s per test
- `@pytest.mark.concurrency` - Concurrent execution tests
- `@pytest.mark.flaky(reruns=2, reruns_delay=2)` - Retry on transient failures

**Exclude Race Tests (Faster CI):**
```bash
# Skip slow tests
pytest -m "not slow" -v

# Skip concurrency tests specifically
pytest -m "not concurrency" -v
```

### Validation Strategy

**State Integrity Checks (all tests):**
1. No duplicate participants
2. Participant count ≤ max_participants
3. Exactly expected number of successes
4. Language synchronization (cross-language tests)

**Metrics Validation (CI):**
1. Barrier wait < MAX_BARRIER_WAIT_THRESHOLD (45s)
2. Request spread > MIN_REQUEST_SPREAD_THRESHOLD (5ms)

**Flaky Test Handling:**
- pytest-rerunfailures plugin installed
- Tests marked with `@pytest.mark.flaky(reruns=2, reruns_delay=2)`
- Retries on transient failures (thread timing variance)

### Best Practices

**✅ DO:**
- Use barrier synchronization for true concurrent start
- Collect metrics to validate test effectiveness
- Verify state integrity after each race
- Use unique email patterns per test
- Test multiple thread counts for scalability

**❌ DON'T:**
- Assume deterministic timing (especially on Windows)
- Skip state verification after concurrent operations
- Ignore metrics threshold warnings
- Run race tests without proper cleanup fixtures
- Test only single thread count

### Docker Testing

For cross-platform race condition validation:

```bash
# Run in Linux container (more realistic CI timing)
docker build -f Dockerfile.test -t api-tests .
docker run --rm api-tests pytest -m concurrency -v

# See docs/testing/DOCKER_TESTING.md for details
```

**Why Docker Matters:**
- Windows has deterministic thread scheduling
- Linux scheduling closer to production
- CI environments (GitHub Actions) run on Linux
- Metrics differ significantly between platforms

### Common Issues

**Issue:** Request spread < 5ms threshold warning

**Cause:** Windows thread scheduling is too deterministic

**Solution:** Expected on local Windows. CI (Linux) will show realistic spread.

---

**Issue:** Barrier timeout after 30s

**Cause:** Slow CI resources, too many concurrent tests

**Solution:** Increase `RACE_TEST_BARRIER_TIMEOUT=60` or `RACE_TEST_BARRIER_TIMEOUT=120`

---

**Issue:** Capacity exceeded (e.g., 13 participants when max=12)

**Cause:** Race condition bug in application logic

**Solution:** Fix atomic capacity check in service layer

---

## Test Markers and Categories

### Custom Pytest Markers

All tests must use appropriate markers for categorization and selective execution.

| Marker | Description | Example Usage |
|--------|-------------|---------------|
| `@pytest.mark.test_id("TC-XXX-NNN")` | **Required** - Unique test identifier | `@pytest.mark.test_id("TC-SIGNUP-001")` |
| `@pytest.mark.functional` | Functional API tests | All tests in `test_app.py` |
| `@pytest.mark.infrastructure` | Infrastructure validation | All tests in `test_infrastructure.py` |
| `@pytest.mark.capacity` | Capacity enforcement tests | Capacity-related signup tests |
| `@pytest.mark.language` | Dual-language feature tests | Hungarian/English translation tests |
| `@pytest.mark.slow` | Tests taking >0.2s | Race condition tests, capacity fill tests |
| `@pytest.mark.concurrency` | Concurrent execution tests | All race condition tests |
| `@pytest.mark.flaky(reruns=N)` | Retry on failure N times | Race tests with timing variance |
| `@pytest.mark.bdd` | BDD scenario tests | Tests generated from `.feature` files |
| `@pytest.mark.e2e` | End-to-end UI tests | Playwright tests |
| `@pytest.mark.ui` | UI component tests | Playwright tests |
| `@pytest.mark.visual` | Visual regression tests | Screenshot comparison tests |

### Running Tests by Marker

```bash
# Run only functional tests
pytest -m functional

# Run only capacity tests
pytest -m capacity

# Run infrastructure tests first (recommended workflow)
pytest -m infrastructure && pytest -m functional

# Run race condition tests
pytest -m concurrency

# Run all tests except slow tests
pytest -m "not slow"

# Run BDD scenarios only
pytest -m bdd

# Run all UI tests
pytest -m e2e

# Run all tests except BDD
pytest -m "not bdd"

# Run API tests only (skip UI)
pytest tests/test_app.py tests/test_infrastructure.py

# Run UI tests only
pytest tests/playwright/

# Run specific test by ID (using -k for keyword matching)
pytest -k "TC_SIGNUP_001"
pytest -k "TC_UI_LANG"
pytest -k "TC_RACE"
```

---

## Test ID Convention
ROOT` | Root endpoint | `TC-ROOT-001` |
| `SIGNUP` | Activity signup functionality | `TC-SIGNUP-001` |
| `UNREGISTER` | Activity unregistration | `TC-UNREGISTER-001` |
| `ACTIVITIES` | Activity listing/retrieval | `TC-ACTIVITIES-001` |
| `CAPACITY` | Capacity enforcement | `TC-CAPACITY-001` |
| `LANGUAGE` | Bilingual functionality | `TC-LANGUAGE-001` |
| `RACE` | Race condition/concurrency tests | `TC-RACE-001` |
| `INFRA-IMPORT` | Module imports | `TC-INFRA-IMPORT-001` |
| `INFRA-APP` | App creation | `TC-INFRA-APP-001` |
| `INFRA-DATA` | Data structures | `TC-INFRA-DATA-001` |
| `INFRA-DEPS` | Dependencies | `TC-INFRA-DEPS-001` |
| `INFRA-FILES` | Static files | `TC-INFRA-FILES-001` |
| `INFRA-SERVER` | Server startup | `TC-INFRA-SERVER-001` |
| `INFRA-QUALITY` | Code quality | `TC-INFRA-QUALITY-001` |
| `INFRA-ENDPOINT` | Endpoint functions | `TC-INFRA-ENDPOINT-001` |
| `INFRA-VALIDATOR` | Validator functions | `TC-INFRA-VALIDATOR-001` |
| `UI-LANG` | UI language switching | `TC-UI-LANG-001` |
| `UI-SIGNUP` | UI signup forms | `TC-UI-SIGNUP-001` |
| `UI-UNREG` | UI unregister/delete | `TC-UI-UNREG-001` |
| `UI-CAPACITY` | UI capacity display/enforcement | `TC-UI-CAPACITY-001` |
| `UI-DISPLAY` | UI activity display | `TC-UI-DISPLAGE-001` |
| `INFRA-IMPORT` | Module imports | `TC-INFRA-IMPORT-001` |
| `INFRA-APP` | App creation | `TC-INFRA-APP-001` |
| `INFRA-DATA` | Data structures | `TC-INFRA-DATA-001` |
| `INFRA-DEPS` | Dependencies | `TC-INFRA-DEPS-001` |
| `INFRA-FILES` | Static files | `TC-INFRA-FILES-001` |
| `INFRA-SERVER` | Server startup | `TC-INFRA-SERVER-001` |
| `INFRA-QUALITY` | Code quality | `TC-INFRA-QUALITY-001` |

### Decorator Usage

```python
import pytest

@pytest.mark.test_id("TC-SIGNUP-001")
@pytest.mark.functional
@pytest.mark.capacity
def test_signup_rejected_when_activity_at_capacity_en(client):
    """Test that signup is rejected when activity has reached max_participants."""
    # Test implementation
```

### Enforcement

- **Pre-commit hook** validates all tests have `@pytest.mark.test_id()` decorators
- IDs must follow pattern `TC-[A-Z-]+[0-9]{3}`
- No duplicate IDs allowed
- See [TEST_CASES.md](TEST_CASES.md) for complete ID registry

---

## Maintainability for AI-Assisted Development

### Why This Matters

When using AI agents (GitHub Copilot, coding assistants), agents start with **empty context**. Without discoverable documentation, agents may:
- Create tests without following conventions
- Miss test ID requirements
- Duplicate test IDs
- Not update traceability documentation
- Break existing patterns

### Discovery Mechanisms

1. **Primary: [.github/copilot-instructions.md](../../.github/copilot-instructions.md)**
   - AI agents read this file first
   - Contains testing framework overview
   - Links to this strategy document
   - Includes quick reference examples

2. **Secondary: [CONTRIBUTING.md](../../CONTRIBUTING.md)**
   - Entry point for human developers
   - Links to testing documentation
   - Pre-commit hook setup instructions

3. **Automated: Pre-commit hooks**
   - Validates test ID decorators
   - Prevents non-compliant commits
   - Catches missing documentation updates

### Agent Guidelines

**For AI agents working on this codebase:**

1. **Before adding tests:**
   - Read [.github/copilot-instructions.md](../../.github/copilot-instructions.md) Testing section
   - Check [TEST_CASES.md](TEST_CASES.md) for next available test ID
   - Review this strategy document for patterns

2. **When adding a test:**
   - Add `@pytest.mark.test_id("TC-AREA-NNN")` decorator
   - Add appropriate category markers (`functional`, `capacity`, etc.)
   - Update [TEST_CASES.md](TEST_CASES.md) with new test entry
   - Update [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md) if implementing a requirement

3. **For user-facing features:**
   - Create `.feature` file in `tests/features/`
   - Add step definitions in `tests/step_defs/`
   - Link BDD scenario to test case in documentation

4. **Before committing:**
   - Run `pytest -v` to ensure all tests pass
   - Pre-commit hook will validate test IDs automatically

---

## Coverage Requirements

### Minimum Thresholds

- **Overall coverage:** 80%
- **Service layer:** 90%
- **API endpoints:** 100%
- **Critical paths (signup/capacity):** 100%

### Coverage Reporting

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Check coverage threshold (fails if below 80%)
pytest --cov=src --cov-fail-under=80
```

### Coverage Enforcement

- **Pre-commit hook:** Warns if coverage drops below threshold
- **CI/CD (future):** Blocks PRs with coverage regression
- **Report location:** `htmlcov/` (gitignored)

---

## How to Maintain This Documentation

### Update Triggers

Update this document when:

- [ ] Adding new test categories/markers
- [ ] Changing test ID convention
- [ ] Adding new test files or reorganizing structure
- [ ] Updating coverage requirements
- [ ] Adding new BDD features
- [ ] Changing testing philosophy or approach

### Update Process

1. **Edit this file** with changes
2. **Update last modified date** at the top
3. **Update [.github/copilot-instructions.md](../../.github/copilot-instructions.md)** Testing section with summary
4. **Update [CONTRIBUTING.md](../../CONTRIBUTING.md)** if workflow changes
5. **Announce changes** in team communication (if applicable)

### Ownership

- **Primary maintainer:** Development Team
- **Review frequency:** Quarterly or on major changes
- **Version control:** Track in Git with descriptive commit messages

### Related Documentation

- [TEST_CASES.md](TEST_CASES.md) - Test case registry
- [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md) - Requirements mapping
- [.github/copilot-instructions.md](../../.github/copilot-instructions.md) - AI agent guidance
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Developer onboarding

---

**Questions or suggestions?** Update this document and submit a PR!
