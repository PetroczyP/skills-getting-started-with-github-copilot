# Copilot Instructions - Mergington High School Activities API

## Project Overview

A bilingual (English/Hungarian) FastAPI application for managing high school extracurricular activities with a static frontend. Students can view activities and register/unregister via a web UI or REST API.

**Tech Stack:** FastAPI, Python 3.x, vanilla JavaScript, pytest

## Architecture

### Data Model - Dual Language Pattern

The application implements a **unique dual-language architecture** where:

1. **Separate activity dictionaries** (`activities_en`, `activities_hu` in [src/app.py](../src/app.py)) define localized content
2. **Shared participant storage** (`participants_storage`) uses English keys as the canonical identifier
3. **Bidirectional name mapping** (`activity_name_mapping`, `activity_name_mapping_reverse`) translates between languages

**Critical:** Participants MUST be synced across both languages. A signup in Hungarian appears in English and vice versa. All internal storage uses English activity names as keys.

### API Design - Request Body Pattern

**Breaking change implemented:** POST/DELETE endpoints use JSON request bodies instead of query parameters for security (see [API_MIGRATION.md](../API_MIGRATION.md)).

**Pattern:**
```python
# All signup/unregister endpoints require:
class SignupRequest(BaseModel):
    email: EmailStr  # Pydantic validates email format automatically

# Usage in endpoints:
@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    request: SignupRequest,  # Email in body
    lang: str = Query("en", pattern="^(en|hu)$")  # Language in query
) -> Dict[str, str]:
    email = request.email  # Extract from body
```

**Never use query parameters for email** - they expose sensitive data in logs.

### Language Translation Flow

1. **Frontend:** User selects language (🇬🇧/🇭🇺 flags), stored in `localStorage`
2. **API calls:** Include `?lang=en` or `?lang=hu` query parameter
3. **Backend lookup:**
   - If `lang=hu` and activity name is Hungarian → map to English key via `activity_name_mapping_reverse`
   - Fetch from `participants_storage` using English key
   - Return response with localized message from `messages` dict

**Example:** User signs up for "Sakk Klub" → backend maps to "Chess Club" → stores in `participants_storage["Chess Club"]` → returns Hungarian success message.

## Developer Workflows

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (dev mode with auto-reload)
cd src && uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Access:
# - Web UI: http://localhost:8000/
# - API docs: http://localhost:8000/docs
```

### Testing

#### ⚠️ CRITICAL: Test Prerequisites for AI Agents

**Before running ANY tests, understand the test architecture:**

1. **API Tests** (`tests/test_app.py`, `tests/test_infrastructure.py`)
   - ✅ **No special setup required** - can run directly with system Python
   - Run from workspace root: `pytest tests/test_app.py tests/test_infrastructure.py -v`
   - **Total:** 61 tests (21 functional + 40 infrastructure)

2. **UI Tests** (`tests/playwright/`)
   - ⚠️ **REQUIRES virtual environment setup** - WILL FAIL without it
   - **Why:** Playwright browsers must be installed in a venv (conftest.py enforces this)
   - **Setup once:** `./scripts/setup_venv.sh` (installs venv, dependencies, browsers ~500MB download)
   - **Run:** `source venv/bin/activate && pytest tests/playwright/ -v --browser chromium`
   - **Shortcut:** `./scripts/run_ui_tests.sh` (handles activation automatically)
   - **Total:** 30 tests (language, signup, unregister, capacity, display)

3. **BDD Tests** (`tests/features/`, `tests/step_defs/`)
   - ✅ **No special setup** - uses same fixtures as API tests
   - Run: `pytest -m bdd -v`

**Common AI Agent Mistakes to Avoid:**
- ❌ Running `pytest tests/playwright/` without venv → RuntimeError
- ❌ Assuming UI tests work if they import successfully → Must actually RUN them
- ❌ Skipping venv setup to "save time" → Tests will fail 100% of the time
- ✅ **ALWAYS run venv setup before touching UI tests**
- ✅ **Verify with actual test execution, not assumptions**

**Quick Test Commands:**

```bash
# API tests only (no venv needed)
pytest tests/test_app.py tests/test_infrastructure.py -v

# UI tests (requires venv setup first)
./scripts/setup_venv.sh  # One-time setup
source venv/bin/activate && pytest tests/playwright/ -v --browser chromium

# OR use the wrapper script
./scripts/run_ui_tests.sh  # Handles venv activation automatically

# All tests (API + UI)
pytest tests/test_app.py tests/test_infrastructure.py -v && ./scripts/run_ui_tests.sh
```

**Test fixture pattern:** `reset_participants` fixture (autouse=True) resets state before each test to ensure isolation.

**Race Condition Tests:**

```bash
# Run race condition tests (6 tests: TC-RACE-001 through TC-RACE-006)
pytest -m concurrency -v

# With metrics collection
RACE_TEST_METRICS=true pytest -m concurrency -v

# Analyze race metrics
python scripts/analyze_race_metrics.py --verbose

# Docker cross-platform testing
docker build -f Dockerfile.test -t api-tests .
docker run --rm api-tests pytest -m concurrency -v
```

See [docs/testing/RACE_CONDITION_TESTING.md](../docs/testing/RACE_CONDITION_TESTING.md) for comprehensive guide.

## Test Documentation Framework

### Overview

This project uses an **AI-discoverable BDD testing framework** with comprehensive documentation ensuring future AI agents and developers understand testing conventions.

**Documentation Structure:**
- [docs/testing/TEST_STRATEGY.md](../docs/testing/TEST_STRATEGY.md) - Overall testing approach and philosophy
- [docs/testing/TEST_CASES.md](../docs/testing/TEST_CASES.md) - Presentable test case registry with IDs
- [docs/testing/TRACEABILITY_MATRIX.md](../docs/testing/TRACEABILITY_MATRIX.md) - Requirements → test case mapping

### Test Organization

**Test Files:**
- [tests/test_app.py](../tests/test_app.py) - 21 functional tests for API endpoints
  - `TestRootEndpoint` - Static file redirect
  - `TestGetActivities` - Activity listing in both languages
  - `TestSignupForActivity` - Signup logic, capacity enforcement
  - `TestUnregisterFromActivity` - Unregistration logic
- [tests/test_infrastructure.py](../tests/test_infrastructure.py) - 40+ infrastructure tests
  - `TestModuleImports` - Verify all modules can be imported
  - `TestApplicationCreation` - FastAPI app creation
  - `TestDataStructures` - Data structure integrity
  - `TestDependencies` - Required packages available
  - `TestStaticFiles` - Frontend files exist
  - `TestServerStartup` - Server can start successfully
  - `TestCodeQuality` - Syntax and import validation
- [tests/conftest.py](../tests/conftest.py) - Shared fixtures and markers
- [tests/features/*.feature](../tests/features/) - BDD Gherkin scenarios
- [tests/step_defs/*.py](../tests/step_defs/) - BDD step definitions

### Test ID Convention

**CRITICAL:** All tests MUST have `@pytest.mark.test_id()` decorator.

**Format:** `TC-[AREA]-[NUMBER]`

**Area codes:**
- `SIGNUP` - Activity signup
- `UNREGISTER` - Activity unregistration
- `ACTIVITIES` - Activity listing
- `CAPACITY` - Capacity enforcement
- `LANGUAGE` - Bilingual functionality
- `RACE` - Race condition/concurrency tests
- `INFRA-IMPORT`, `INFRA-APP`, `INFRA-DATA`, etc. - Infrastructure tests

**Example:**
```python
@pytest.mark.test_id("TC-SIGNUP-001")
@pytest.mark.functional
@pytest.mark.capacity
def test_signup_rejected_when_activity_at_capacity_en(client):
    """Test that signup is rejected when activity has reached max_participants."""
    # Test implementation
```

### Pytest Markers

Use markers to categorize and run specific test subsets:

```bash
# Run only functional tests
pytest -m functional

# Run only capacity tests
pytest -m capacity

# Run infrastructure tests first (recommended)
pytest -m infrastructure && pytest -m functional

# Run BDD scenarios
pytest -m bdd
```

**Available markers:**
- `@pytest.mark.test_id("TC-XXX-NNN")` - **Required** test identifier
- `@pytest.mark.functional` - Functional API tests
- `@pytest.mark.infrastructure` - Infrastructure validation tests
- `@pytest.mark.capacity` - Capacity enforcement tests
- `@pytest.mark.slow` - Tests taking >0.2s (race condition tests)
- `@pytest.mark.concurrency` - Concurrent execution tests
- `@pytest.mark.flaky(reruns=N)` - Retry on failure N times
- `@pytest.mark.language` - Bilingual functionality tests
- `@pytest.mark.bdd` - BDD scenario tests

### BDD Testing

**When to use Gherkin `.feature` files:**
- User-facing features requiring stakeholder review
- Complex business logic needing documentation
- Acceptance criteria validation

**Location:** [tests/features/](../tests/features/)
- `activity_signup.feature` - Signup scenarios
- `capacity_management.feature` - Capacity enforcement scenarios
- `language_support.feature` - Bilingual functionality scenarios

**Step definitions:** [tests/step_defs/](../tests/step_defs/)

### Test Execution Strategies

```bash
# Run all tests
pytest

# Run only functional tests
pytest tests/test_app.py

# Run only infrastructure tests (recommended before debugging)
pytest tests/test_infrastructure.py

# Run specific test class
pytest tests/test_app.py::TestSignupForActivity

# Run specific test by ID
pytest -k "TC_SIGNUP_001"

# Run with coverage report
pytest --cov=src --cov-report=html

# Stop on first failure
pytest -x
```

### Infrastructure Tests Purpose

**ALWAYS run infrastructure tests first** before debugging or starting the server:

```bash
pytest tests/test_infrastructure.py
```

These tests catch:
- `ModuleNotFoundError` (missing imports)
- Syntax errors in Python files
- Missing dependencies
- Data structure issues
- Server startup problems

This prevents common "run and debug" errors.

### Pre-Commit Hook

**Setup (required for contributors):**
```bash
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**The hook validates:**
1. All test functions have `@pytest.mark.test_id()` decorators
2. Test IDs follow `TC-[AREA]-[NUMBER]` format
3. No duplicate test IDs exist
4. All tests pass before commit
5. No syntax errors in code
6. Coverage threshold met (warning only)

**Bypass (not recommended):**
```bash
git commit --no-verify
```

### Adding New Tests

**Required steps:**

1. **Add test function with decorators:**
```python
@pytest.mark.test_id("TC-SIGNUP-006")
@pytest.mark.functional
def test_new_feature(client):
    """Test description."""
    # Implementation
```

2. **Update [docs/testing/TEST_CASES.md](../docs/testing/TEST_CASES.md):**
   - Add entry to appropriate section
   - Include: ID, title, description, preconditions, steps, expected results

3. **Update [docs/testing/TRACEABILITY_MATRIX.md](../docs/testing/TRACEABILITY_MATRIX.md):**
   - Link test to requirement/user story
   - Update coverage statistics

4. **For user-facing features, add BDD scenario:**
   - Create/update `.feature` file in `tests/features/`
   - Add step definitions in `tests/step_defs/`

5. **Run pre-commit hook to validate:**
```bash
.githooks/pre-commit
```

### Test Helper Patterns

**Helper methods in test classes:**
```python
def _get_activity_info(self, client, activity_name, lang="en"):
    """Fetch activity state from API."""
    return client.get(f"/activities?lang={lang}").json()[activity_name]
```

**Class constants for test parameters:**
```python
class TestSignupForActivity:
    OVERFLOW_TEST_COUNT = 3  # Number of overflow attempts
```

**Test-specific email patterns:**
```python
# Use unique patterns to avoid cross-test conflicts
emails = [f"capacity_test_{i}@mergington.edu" for i in range(N)]
```

### Coverage Requirements

**Minimum thresholds:**
- Overall: 80%
- Service layer: 90%
- API endpoints: 100%
- Critical paths (signup/capacity): 100%

**Generate coverage report:**
```bash
pytest --cov=src --cov-report=html --cov-report=term
open htmlcov/index.html
```

### Maintainability for AI Agents

**IMPORTANT:** When working as an AI agent on this codebase:

1. **Before adding tests:**
   - Read this section first
   - Review [docs/testing/TEST_STRATEGY.md](../docs/testing/TEST_STRATEGY.md)
   - Check [docs/testing/TEST_CASES.md](../docs/testing/TEST_CASES.md) for next available test ID

2. **When adding a test:**
   - Add `@pytest.mark.test_id("TC-AREA-NNN")` decorator
   - Add appropriate category markers
   - Update TEST_CASES.md with new entry
   - Update TRACEABILITY_MATRIX.md if implementing a requirement

3. **For user-facing features:**
   - Create `.feature` file in `tests/features/`
   - Add step definitions in `tests/step_defs/`

4. **Before committing:**
   - Run `pytest -v` to ensure all tests pass
   - Pre-commit hook will validate automatically

## UI Testing Gotchas (Critical for AI Agents)

### Subprocess Isolation - MOST IMPORTANT

⚠️ **CRITICAL**: The FastAPI server runs in `subprocess.Popen`, creating a **separate Python process**.

**What this means:**
- Test process and server process have **completely separate memory spaces**
- Direct manipulation of `participants_storage` from tests **does not work**
- State reset **must use HTTP API calls**, not direct memory access

**Common Mistake (WRONG):**
```python
# This only modifies test process memory, NOT server memory!
from src.app import participants_storage
participants_storage["Chess Club"] = []  # Server unchanged!
```

**Correct Approach:**
```python
# Use HTTP API to modify server state
import requests
requests.delete(
    "http://localhost:8000/activities/Chess Club/unregister",
    json={"email": "student@example.com"}
)
```

### Performance: Sequential vs Parallel API Calls

**Problem:** Sequential API calls are too slow for test suite (10+ minutes)

**Solution:** Use ThreadPoolExecutor for parallel API calls (2-3s overhead)

```python
from concurrent.futures import ThreadPoolExecutor

# Calculate minimal diff first
to_remove = current_participants - desired_participants
to_add = desired_participants - current_participants

# Execute operations in PARALLEL
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(api_call, ...) for each operation]
    for future in as_completed(futures):
        future.result()  # Wait for completion
```

### Test Isolation Debugging

**Symptom:** Tests pass individually but fail in suite

**Root Cause:** State not properly reset between tests

**Diagnostic:**
```bash
# Test passes alone
pytest tests/playwright/test_ui_capacity.py::test_signup_shows_error_when_full -v  # ✅

# But fails in suite
pytest tests/playwright/test_ui_capacity.py -v  # ❌
```

**Solution:** Verify `reset_participants` autouse fixture uses API calls, not direct memory access

### Async UI Update Race Conditions

**Problem:** Tests check UI state before JavaScript finishes updating

**Solution:** Add wait/retry logic in Page Object methods

```python
def has_participant(self, activity_name: str, email: str, timeout: int = 5000) -> bool:
    self.page.wait_for_timeout(1000)  # Initial wait
    for attempt in range(3):  # Retry up to 3 times
        participants = self.get_participants(activity_name)
        if email in participants:
            return True
        if attempt < 2:
            self.page.wait_for_timeout(1000)  # Wait between retries
    return False
```

### localStorage Clearing

**Best Practice:** Clear localStorage in `ActivitiesPage.load()` method, not in separate fixture

```python
def load(self, clear_storage: bool = True) -> None:
    if clear_storage:
        self.navigate_to("/")
        self.page.evaluate("() => localStorage.clear()")
        self.page.reload()
    else:
        self.navigate_to("/")
    self.wait_for_activities_loaded()
```

### Server Health Check

**Always verify server is ready** before running tests:

```python
for attempt in range(30):
    try:
        response = requests.get("http://localhost:8000/activities", timeout=2)
        if response.status_code == 200:
            break
    except:
        if attempt == 29:
            raise RuntimeError("Server failed to start")
        time.sleep(1)
```

---

## Project-Specific Conventions

### Email Validation

- Use `pydantic[email]` package (installed via `requirements.txt`)
- Define models with `EmailStr` type: `email: EmailStr`
- FastAPI automatically returns 422 for invalid emails - **do not add manual regex validation**

### Capacity Enforcement

Activities have `max_participants` limits. **Always check capacity before adding:**

```python
if len(participants_storage[en_activity_name]) >= activity["max_participants"]:
    raise HTTPException(status_code=400, detail=messages[lang]["activity_full"])
```

Localized error messages are in `messages` dict keyed by language.

### Activity Name Handling

**Critical pattern for endpoints accepting `{activity_name}`:**

1. Check if `lang=hu` and name exists in `activity_name_mapping_reverse` → convert to English
2. If `lang=en`, verify name exists in `activities_en`
3. Use English name for all `participants_storage` operations
4. Use original (localized) name in response messages

Example from [src/app.py](../src/app.py):
```python
# Convert Hungarian activity name to English for internal storage
en_activity_name = activity_name
if lang == "hu" and activity_name in activity_name_mapping_reverse:
    en_activity_name = activity_name_mapping_reverse[activity_name]
```

### Frontend Translation Pattern

JavaScript uses `data-i18n` attributes for automatic translation:

```html
<h1 data-i18n="page-title">Extracurricular Activities</h1>
```

`translatePage(lang)` function updates all `[data-i18n]` elements. Language preference persists in `localStorage`.

## Testing Conventions

### Fixture Usage

- `client`: TestClient instance for API calls
- `reset_participants`: Auto-applied to reset state (see [tests/test_app.py](../tests/test_app.py))

### Capacity Testing Pattern

Tests that fill activities to capacity use this pattern:

1. Get current participant count via `_get_activity_info` helper
2. Calculate slots available: `max_participants - initial_count`
3. Fill all slots with test-specific emails (e.g., `capacity_test_0@mergington.edu`)
4. Verify next signup returns 400 with localized error message

See [tests/test_app.py](../tests/test_app.py) for reference implementation.

### Language Sync Testing

**Always test participant synchronization:** Signing up in one language must appear in the other:

```python
# Sign up in Hungarian
client.post("/activities/Sakk Klub/signup?lang=hu", json={"email": "test@example.com"})

# Verify appears in English
activities_en = client.get("/activities?lang=en").json()
assert "test@example.com" in activities_en["Chess Club"]["participants"]
```

## Key Files

### Application Code
- [src/app.py](../src/app.py) - FastAPI application with dual-language logic
- [src/service.py](../src/service.py) - ActivityService business logic layer
- [src/models.py](../src/models.py) - Pydantic models for request/response
- [src/validators.py](../src/validators.py) - Validation utilities
- [src/exceptions.py](../src/exceptions.py) - Custom exception definitions
- [src/constants.py](../src/constants.py) - Application constants
- [src/static/app.js](../src/static/app.js) - Frontend translation and API calls
- [src/static/index.html](../src/static/index.html) - Web UI
- [src/static/styles.css](../src/static/styles.css) - Styling

### Testing
- [tests/test_app.py](../tests/test_app.py) - 27 functional API tests (21 base + 6 race condition tests)
- [tests/test_infrastructure.py](../tests/test_infrastructure.py) - 40+ infrastructure tests
- [tests/conftest.py](../tests/conftest.py) - Shared fixtures and markers
- [tests/race_config.py](../tests/race_config.py) - Race condition test configuration
- [tests/race_metrics.py](../tests/race_metrics.py) - RaceMetricsCollector for timing data
- [tests/features/*.feature](../tests/features/) - BDD Gherkin scenarios
- [tests/step_defs/*.py](../tests/step_defs/) - BDD step definitions
- [pytest.ini](../pytest.ini) - Pytest configuration
- [scripts/analyze_race_metrics.py](../scripts/analyze_race_metrics.py) - Metrics analysis tool
- [scripts/run_docker_tests.sh](../scripts/run_docker_tests.sh) - Docker test runner

### Documentation
- [docs/testing/RACE_CONDITION_TESTING.md](../docs/testing/RACE_CONDITION_TESTING.md) - Race condition test guide
- [docs/testing/DOCKER_TESTING.md](../docs/testing/DOCKER_TESTING.md) - Cross-platform Docker testing
- [docs/testing/TEST_STRATEGY.md](../docs/testing/TEST_STRATEGY.md) - Testing philosophy and approach
- [docs/testing/TEST_CASES.md](../docs/testing/TEST_CASES.md) - Test case registry with IDs
- [docs/testing/TRACEABILITY_MATRIX.md](../docs/testing/TRACEABILITY_MATRIX.md) - Requirements traceability
- [API_MIGRATION.md](../API_MIGRATION.md) - API breaking changes (query params → request body)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development setup and guidelines
- [README.md](../README.md) - Project overview

### Configuration
- [requirements.txt](../requirements.txt) - Python dependencies (pytest, pytest-rerunfailures)
- [pytest.ini](../pytest.ini) - Pytest markers and configuration
- [.githooks/pre-commit](../.githooks/pre-commit) - Pre-commit validation hook
- [.gitignore](../.gitignore) - Git ignore patterns
- [Dockerfile.test](../Dockerfile.test) - Docker image for cross-platform testing
- [.dockerignore](../.dockerignore) - Docker build context exclusions

**Last Updated:** December 31, 2025
