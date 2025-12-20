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
