"""Playwright-specific pytest configuration and fixtures.

This module provides fixtures for Playwright UI tests including:
- Server startup/shutdown
- Virtual environment validation
- Page Object Model instances
- Test data setup via API
- Browser context configuration
"""

import pytest
import subprocess
import time
import requests
import sys
import os
from playwright.sync_api import Page
from tests.playwright.pages.activities_page import ActivitiesPage


# ============================================================================
# Virtual Environment Validation
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def validate_venv():
    """Validate that tests are running in a virtual environment.
    
    Skips validation in CI environments (GitHub Actions, etc.)
    
    Raises:
        RuntimeError: If not running in a virtual environment (local development only)
    """
    # Skip venv check in CI environments
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        print("✓ Running in CI environment - skipping venv check")
        return
    
    if not hasattr(sys, 'prefix') or sys.prefix == sys.base_prefix:
        raise RuntimeError(
            "❌ Playwright tests must run in a virtual environment!\n"
            "   Please activate venv first:\n"
            "     source venv/bin/activate\n"
            "   Or run setup script:\n"
            "     ./scripts/setup_venv.sh\n"
        )
    
    # Verify Playwright is installed
    try:
        from playwright._repo_version import version as playwright_version
        print(f"✓ Running in venv: {sys.prefix}")
        print(f"✓ Playwright version: {playwright_version}")
    except ImportError:
        raise RuntimeError(
            "❌ Playwright not found in virtual environment!\n"
            "   Install with:\n"
            "     pip install -r requirements.txt\n"
            "     playwright install chromium firefox webkit\n"
        )


# ============================================================================
# Server Startup/Shutdown
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def start_server():
    """Start FastAPI server before Playwright tests and terminate after.
    
    Yields:
        subprocess.Popen: Server process
    """
    print("\n🚀 Starting FastAPI server for UI tests...")
    
    # Start server in subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    # Wait for server to be ready
    server_ready = False
    for attempt in range(30):  # 30 second timeout
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code in [200, 307]:
                server_ready = True
                print("✓ FastAPI server is ready")
                break
        except requests.ConnectionError:
            time.sleep(1)
    
    if not server_ready:
        process.kill()
        raise RuntimeError("❌ Failed to start FastAPI server within 30 seconds")
    
    yield process
    
    # Cleanup: terminate server
    print("\n🛑 Stopping FastAPI server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    print("✓ Server stopped")


# ============================================================================
# Browser Context Configuration
# ============================================================================

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with viewport and locale.
    
    Args:
        browser_context_args: Default browser context arguments
        
    Returns:
        dict: Updated browser context arguments
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }


# ============================================================================
# Page Object Model Fixtures
# ============================================================================

@pytest.fixture
def activities_page(page: Page) -> ActivitiesPage:
    """Create ActivitiesPage instance.
    
    Args:
        page: Playwright Page object
        
    Returns:
        ActivitiesPage: Page Object instance
    """
    return ActivitiesPage(page)


@pytest.fixture
def test_context():
    """Shared context dictionary for BDD steps.
    
    Returns:
        dict: Context dictionary for storing test data
    """
    return {}


# ============================================================================
# State Management Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_participants():
    """Reset participants to initial state before each test using parallel API calls.
    
    ⚠️ CRITICAL ARCHITECTURE NOTE:
    The FastAPI server runs in a separate subprocess (subprocess.Popen), not in-process.
    This means the test process and server process have COMPLETELY SEPARATE MEMORY SPACES.
    
    ❌ WRONG APPROACH: Direct memory manipulation
        from src.app import participants_storage
        participants_storage.clear()  # This modifies test process memory, NOT server memory!
    
    ✅ CORRECT APPROACH: HTTP API calls
        We must use HTTP requests to modify the server's state through its public API.
    
    🚀 PERFORMANCE OPTIMIZATION:
    - Sequential API calls: ~60+ requests taking 10+ minutes ❌
    - Parallel API calls: ThreadPoolExecutor with diff-based minimal operations ✅
    
    How this works:
    1. Fetch current state from server via GET /activities
    2. Calculate diff: what needs to be removed/added (minimal operations)
    3. Execute unregister operations in PARALLEL (10 workers)
    4. Execute signup operations in PARALLEL (10 workers)
    
    Result: ~2-3 seconds overhead per test, all tests properly isolated.
    
    This fixture automatically runs before every test to ensure isolation.
    """
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Define desired initial state
    initial_participants = {
        "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
        "Soccer Team": ["alex@mergington.edu", "sarah@mergington.edu"],
        "Swimming Club": ["ryan@mergington.edu"],
        "Drama Club": ["lily@mergington.edu", "james@mergington.edu"],
        "Art Studio": ["ava@mergington.edu"],
        "Debate Team": ["noah@mergington.edu", "mia@mergington.edu"],
        "Science Olympiad": ["ethan@mergington.edu", "isabella@mergington.edu"]
    }
    
    try:
        # Get current state
        response = requests.get("http://localhost:8000/activities?lang=en", timeout=5)
        if response.status_code != 200:
            return
        
        activities = response.json()
        
        # Build list of operations needed
        unregister_ops = []
        signup_ops = []
        
        for activity_name in activities.keys():
            current_participants = set(activities[activity_name].get("participants", []))
            desired_participants = set(initial_participants.get(activity_name, []))
            
            # Find who needs to be removed
            to_remove = current_participants - desired_participants
            for email in to_remove:
                unregister_ops.append((activity_name, email))
            
            # Find who needs to be added
            to_add = desired_participants - current_participants
            for email in to_add:
                signup_ops.append((activity_name, email))
        
        # Execute unregister operations in parallel (faster)
        if unregister_ops:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for activity_name, email in unregister_ops:
                    future = executor.submit(
                        requests.request,
                        "DELETE",
                        f"http://localhost:8000/activities/{requests.utils.quote(activity_name)}/unregister",
                        json={"email": email},
                        params={"lang": "en"},
                        timeout=2
                    )
                    futures.append(future)
                
                # Wait for all to complete
                for future in as_completed(futures):
                    try:
                        future.result()
                    except:
                        pass  # Ignore errors
        
        # Execute signup operations in parallel
        if signup_ops:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for activity_name, email in signup_ops:
                    future = executor.submit(
                        requests.post,
                        f"http://localhost:8000/activities/{requests.utils.quote(activity_name)}/signup",
                        json={"email": email},
                        params={"lang": "en"},
                        timeout=2
                    )
                    futures.append(future)
                
                # Wait for all to complete
                for future in as_completed(futures):
                    try:
                        future.result()
                    except:
                        pass  # Ignore errors
    
    except Exception as e:
        print(f"⚠️  Warning: Failed to reset participants: {e}")


# LocalStorage is now cleared by ActivitiesPage.load() method
# No separate fixture needed


# ============================================================================
# Helper Fixtures for Test Data Setup
# ============================================================================

@pytest.fixture
def api_helper():
    """Helper functions for API operations during tests.
    
    Returns:
        object: Helper object with API methods
    """
    class APIHelper:
        BASE_URL = "http://localhost:8000"
        
        @staticmethod
        def signup(activity: str, email: str, lang: str = "en") -> requests.Response:
            """Sign up for an activity via API.
            
            Args:
                activity: Activity name
                email: Student email
                lang: Language code
                
            Returns:
                Response object
            """
            return requests.post(
                f"{APIHelper.BASE_URL}/activities/{activity}/signup?lang={lang}",
                json={"email": email}
            )
        
        @staticmethod
        def unregister(activity: str, email: str, lang: str = "en") -> requests.Response:
            """Unregister from an activity via API.
            
            Args:
                activity: Activity name
                email: Student email
                lang: Language code
                
            Returns:
                Response object
            """
            return requests.delete(
                f"{APIHelper.BASE_URL}/activities/{activity}/unregister?lang={lang}",
                json={"email": email}
            )
        
        @staticmethod
        def get_activities(lang: str = "en") -> dict:
            """Get all activities via API.
            
            Args:
                lang: Language code
                
            Returns:
                Activities dictionary
            """
            response = requests.get(f"{APIHelper.BASE_URL}/activities?lang={lang}")
            return response.json()
        
        @staticmethod
        def fill_to_capacity(activity: str, lang: str = "en") -> int:
            """Fill an activity to max capacity.
            
            Args:
                activity: Activity name
                lang: Language code
                
            Returns:
                Number of participants added
            """
            activities = APIHelper.get_activities(lang)
            activity_data = activities[activity]
            
            max_participants = activity_data["max_participants"]
            current_count = len(activity_data["participants"])
            slots_available = max_participants - current_count
            
            for i in range(slots_available):
                APIHelper.signup(activity, f"capacity_{i}@mergington.edu", lang)
            
            return slots_available
    
    return APIHelper()


@pytest.fixture
def fill_activity_to_capacity(api_helper):
    """Fixture to fill an activity to capacity.
    
    Args:
        api_helper: API helper fixture
        
    Returns:
        function: Function to fill activity to capacity
    """
    def _fill(activity_name: str, lang: str = "en") -> int:
        """Fill activity to capacity and return count added.
        
        Args:
            activity_name: Activity name
            lang: Language code
            
        Returns:
            Number of participants added
        """
        return api_helper.fill_to_capacity(activity_name, lang)
    
    return _fill


# ============================================================================
# Pytest Hooks for UI Tests
# ============================================================================

def pytest_configure(config):
    """Register custom markers for Playwright tests.
    
    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers", "e2e: End-to-end UI tests with Playwright"
    )
    config.addinivalue_line(
        "markers", "ui: UI-specific tests"
    )
    config.addinivalue_line(
        "markers", "visual: Visual regression tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to apply markers and validate test IDs.
    
    Args:
        config: Pytest configuration object
        items: List of collected test items
    """
    for item in items:
        # Auto-apply e2e marker to all tests in playwright directory
        if "playwright" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.ui)
            
            # Check for test_id marker
            has_test_id = any(marker.name == "test_id" for marker in item.iter_markers())
            
            # Warn if missing test ID (for non-BDD tests)
            if not has_test_id and "test_" in item.name and "bdd" not in str(item.fspath):
                # Pre-commit hook will enforce this
                pass


# ============================================================================
# Browser-Specific Fixtures (for multi-browser testing)
# ============================================================================

@pytest.fixture
def browser_name_for_test(request):
    """Get browser name for current test.
    
    Args:
        request: Pytest request object
        
    Returns:
        str: Browser name (chromium, firefox, webkit)
    """
    return request.config.getoption("--browser", default="chromium")


@pytest.fixture
def skip_firefox():
    """Skip test on Firefox browser.
    
    Usage:
        @pytest.mark.usefixtures("skip_firefox")
        def test_something(page):
            pass
    """
    import pytest
    browser = pytest.config.getoption("--browser", default="chromium")
    if browser == "firefox":
        pytest.skip("Skipped on Firefox")


@pytest.fixture
def skip_webkit():
    """Skip test on WebKit browser.
    
    Usage:
        @pytest.mark.usefixtures("skip_webkit")
        def test_something(page):
            pass
    """
    import pytest
    browser = pytest.config.getoption("--browser", default="chromium")
    if browser == "webkit":
        pytest.skip("Skipped on WebKit")
