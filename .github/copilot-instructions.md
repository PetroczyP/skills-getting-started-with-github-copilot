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

```bash
# Run all tests from workspace root
pytest

# Run specific test class
pytest tests/test_app.py::TestSignupForActivity

# Run with verbose output
pytest -v
```

**Test fixture pattern:** `reset_participants` fixture (autouse=True) resets state before each test to ensure isolation.

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

- [src/app.py](../src/app.py) - FastAPI application with dual-language logic
- [src/static/app.js](../src/static/app.js) - Frontend translation and API calls
- [tests/test_app.py](../tests/test_app.py) - Comprehensive test suite with capacity/language tests
- [API_MIGRATION.md](../API_MIGRATION.md) - Breaking changes documentation (query params → request body)
- [requirements.txt](../requirements.txt) - Dependencies including `pydantic[email]`
# Copilot Instructions for Mergington High School API

## Project Overview

This is a FastAPI-based High School Management System that allows students to view and sign up for extracurricular activities at Mergington High School. The application uses an in-memory database for activity storage.

## Code Structure

- **`src/app.py`**: Main FastAPI application with REST API endpoints
- **`tests/test_app.py`**: Pytest-based test suite for all endpoints
- **`src/static/`**: Static files (HTML, CSS, JavaScript) for the web interface
- **`requirements.txt`**: Python dependencies

## Coding Standards and Conventions

### Python Style

- Follow PEP 8 style guidelines for Python code
- Use type hints for function parameters and return values (see existing code)
- Use docstrings for all functions, classes, and modules following Google style
- Include detailed descriptions with Args, Returns, Raises, and Example sections in docstrings

### FastAPI Conventions

- Use Pydantic models for request/response validation (e.g., `SignupRequest`, `UnregisterRequest`)
- Use proper HTTP status codes in exceptions (404 for not found, 400 for bad requests, 422 for validation errors)
- Always validate input before processing requests
- Return clear error messages with `HTTPException`

### Testing

- All tests use pytest framework
- Tests are organized by class based on endpoints (e.g., `TestGetActivities`, `TestSignupForActivity`)
- Use fixtures for test setup (`client` fixture, `reset_activities` autouse fixture)
- Write descriptive test function names that clearly indicate what is being tested
- Each test should be self-contained and not rely on state from other tests
- Include docstrings for test methods explaining what is being tested

## Building and Testing

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
pytest
```

All tests should pass before committing changes.

### Run the Application

```bash
uvicorn src.app:app --reload
```

The API will be available at `http://localhost:8000`

## Key Implementation Details

### Data Structure

Activities are stored in an in-memory dictionary with the following structure:

```python
{
    "activity_name": {
        "description": str,
        "schedule": str,
        "max_participants": int,
        "participants": List[str]  # List of email addresses
    }
}
```

### Email Validation

All email addresses are validated using Pydantic's `EmailStr` type, which automatically validates email format.

### Capacity Management

When signing up for activities:
1. Check if activity exists (404 if not)
2. Check if student is already signed up (400 if yes)
3. Check if activity is at max capacity (400 if full)
4. Only then add student to participants list

## Common Tasks

### Adding a New Endpoint

1. Add the route function to `src/app.py`
2. Use appropriate HTTP method decorator (`@app.get`, `@app.post`, etc.)
3. Add type hints for parameters and return values
4. Add comprehensive docstring with Args, Returns, Raises, and Example sections
5. Add validation for inputs
6. Add corresponding tests in `tests/test_app.py`

### Adding a New Activity Field

1. Update the activity dictionary structure in `src/app.py`
2. Update test fixtures in `tests/test_app.py` (specifically `reset_activities`)
3. Update any affected tests
4. Ensure all existing tests still pass

## Important Notes

- The application uses in-memory storage, so all data is lost when the server restarts
- Email addresses must be valid format (validated by Pydantic)
- All participant emails are stored as lowercase strings for consistency
- The application serves static files from `src/static/` directory
