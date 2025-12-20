"""
Pytest configuration and shared fixtures

This module provides:
- Shared test fixtures (client, reset_participants)
- Custom pytest marker registration
- BDD scenario hooks
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, participants_storage


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "test_id(id): Test case identifier for traceability"
    )
    config.addinivalue_line(
        "markers", "functional: Functional API tests"
    )
    config.addinivalue_line(
        "markers", "infrastructure: Infrastructure and setup tests"
    )
    config.addinivalue_line(
        "markers", "capacity: Capacity enforcement tests"
    )
    config.addinivalue_line(
        "markers", "language: Bilingual functionality tests"
    )
    config.addinivalue_line(
        "markers", "bdd: BDD scenario tests (from .feature files)"
    )


# ============================================================================
# Shared Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI app.
    
    Returns:
        TestClient: A FastAPI test client for making HTTP requests
    
    Example:
        def test_endpoint(client):
            response = client.get("/activities")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_participants():
    """Reset participants to initial state before each test.
    
    This fixture automatically runs before every test to ensure isolation.
    It clears the participants_storage and resets it to the default state.
    
    Note:
        This is an autouse fixture, meaning it runs automatically without
        being explicitly requested in test function parameters.
    """
    participants_storage.clear()
    participants_storage.update({
        "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
        "Soccer Team": ["alex@mergington.edu", "sarah@mergington.edu"],
        "Swimming Club": ["ryan@mergington.edu"],
        "Drama Club": ["lily@mergington.edu", "james@mergington.edu"],
        "Art Studio": ["ava@mergington.edu"],
        "Debate Team": ["noah@mergington.edu", "mia@mergington.edu"],
        "Science Olympiad": ["ethan@mergington.edu", "isabella@mergington.edu"]
    })


# ============================================================================
# BDD-Specific Fixtures (for pytest-bdd integration)
# ============================================================================

@pytest.fixture
def test_context():
    """Shared context for BDD scenarios.
    
    Returns:
        dict: A dictionary to store shared state between BDD steps
    
    Example:
        @given("I have an email address")
        def set_email(test_context):
            test_context["email"] = "student@mergington.edu"
    """
    return {}


@pytest.fixture
def student_email():
    """Fixture for student email data.
    
    Returns:
        dict: A dictionary with email field for API requests
    """
    return {"email": ""}


@pytest.fixture
def activity_response(test_context):
    """Fixture to store API response in BDD context.
    
    Args:
        test_context: Shared context dictionary
    
    Returns:
        dict: Context dictionary for storing responses
    """
    return test_context


# ============================================================================
# Pytest Hooks for Test Validation
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Hook to validate test IDs and apply markers.
    
    This hook runs after test collection and:
    1. Validates that all tests (except infrastructure) have test_id markers
    2. Automatically applies category markers based on test location
    3. Warns about missing test IDs
    
    Args:
        config: Pytest configuration object
        items: List of collected test items
    """
    for item in items:
        # Skip infrastructure tests from test_id requirement (for now)
        if "test_infrastructure" in str(item.fspath):
            # Auto-apply infrastructure marker
            item.add_marker(pytest.mark.infrastructure)
            continue
        
        # Check for test_id marker in functional tests
        has_test_id = any(marker.name == "test_id" for marker in item.iter_markers())
        
        # Warn about missing test IDs (will be enforced by pre-commit hook)
        if not has_test_id and "test_app" in str(item.fspath):
            # For now, just apply functional marker
            # Pre-commit hook will enforce test_id requirement
            item.add_marker(pytest.mark.functional)


# ============================================================================
# Helper Functions for Tests
# ============================================================================

def get_activity_info(client, activity_name, lang="en"):
    """Helper function to fetch activity information.
    
    Args:
        client: TestClient instance
        activity_name: Name of the activity
        lang: Language code (default: "en")
    
    Returns:
        dict: Activity information including participants, max_participants, etc.
    
    Example:
        activity = get_activity_info(client, "Chess Club", "en")
        assert len(activity["participants"]) < activity["max_participants"]
    """
    response = client.get(f"/activities?lang={lang}")
    return response.json()[activity_name]
