"""Infrastructure tests for the Mergington High School API

This module contains tests to ensure:
- All modules can be imported without errors
- The FastAPI application can be created
- Server can start successfully
- All dependencies are available

These tests prevent common "run and debug" errors by verifying:
1. Import Errors: All modules can be imported (catches ModuleNotFoundError)
2. Syntax Errors: All Python files compile successfully
3. Dependency Issues: Required packages are installed
4. Data Structure Issues: All required constants and data exist
5. Server Startup: The application can start and respond to requests
6. Static Files: All required frontend files exist
7. API Structure: Routes and models are properly configured

Running these tests before attempting to run the server will catch most
configuration and import issues early in the development cycle.
"""

import pytest
import sys
from pathlib import Path


class TestModuleImports:
    """Test that all modules can be imported without errors"""

    def test_import_app_module(self):
        """Test that the main app module can be imported"""
        try:
            from src import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import src.app: {e}")

    def test_import_constants_module(self):
        """Test that the constants module can be imported"""
        try:
            from src import constants
            assert constants is not None
        except ImportError as e:
            pytest.fail(f"Failed to import src.constants: {e}")

    def test_import_validators_module(self):
        """Test that the validators module can be imported"""
        try:
            from src import validators
            assert validators is not None
        except ImportError as e:
            pytest.fail(f"Failed to import src.validators: {e}")

    def test_import_models_module(self):
        """Test that the models module can be imported"""
        try:
            from src import models
            assert models is not None
        except ImportError as e:
            pytest.fail(f"Failed to import src.models: {e}")

    def test_import_service_module(self):
        """Test that the service module can be imported"""
        try:
            from src import service
            assert service is not None
        except ImportError as e:
            pytest.fail(f"Failed to import src.service: {e}")

    def test_import_exceptions_module(self):
        """Test that the exceptions module can be imported"""
        try:
            from src import exceptions
            assert exceptions is not None
        except ImportError as e:
            pytest.fail(f"Failed to import src.exceptions: {e}")

    def test_all_constants_available(self):
        """Test that all required constants are defined"""
        from src.constants import (
            SupportedLanguage,
            DEFAULT_LANGUAGE,
            HTTP_NOT_FOUND,
            HTTP_BAD_REQUEST,
            MSG_ACTIVITY_NOT_FOUND,
            MSG_STUDENT_ALREADY_REGISTERED,
            MSG_STUDENT_NOT_REGISTERED
        )
        
        assert SupportedLanguage is not None
        assert DEFAULT_LANGUAGE is not None
        assert HTTP_NOT_FOUND == 404
        assert HTTP_BAD_REQUEST == 400
        assert MSG_ACTIVITY_NOT_FOUND == "Activity not found"
        assert MSG_STUDENT_ALREADY_REGISTERED == "Student already signed up for this activity"
        assert MSG_STUDENT_NOT_REGISTERED == "Student is not signed up for this activity"

    def test_all_validators_available(self):
        """Test that all validator functions are available"""
        from src.validators import (
            validate_and_translate_activity_name,
            validate_student_not_registered,
            validate_student_registered,
            validate_capacity_available
        )
        
        assert callable(validate_and_translate_activity_name)
        assert callable(validate_student_not_registered)
        assert callable(validate_student_registered)
        assert callable(validate_capacity_available)

    def test_all_models_available(self):
        """Test that all model classes are available"""
        from src.models import (
            SignupRequest,
            UnregisterRequest,
            ActivityDetails,
            MessageResponse
        )
        
        assert SignupRequest is not None
        assert UnregisterRequest is not None
        assert ActivityDetails is not None
        assert MessageResponse is not None

    def test_all_exceptions_available(self):
        """Test that all exception classes are available"""
        from src.exceptions import (
            ActivityError,
            ActivityNotFoundError,
            ActivityCapacityError,
            StudentRegistrationError,
            StudentAlreadyRegisteredError,
            StudentNotRegisteredError
        )
        
        assert issubclass(ActivityNotFoundError, ActivityError)
        assert issubclass(ActivityCapacityError, ActivityError)
        assert issubclass(StudentAlreadyRegisteredError, StudentRegistrationError)
        assert issubclass(StudentNotRegisteredError, StudentRegistrationError)

    def test_service_class_available(self):
        """Test that the ActivityService class is available"""
        from src.service import ActivityService
        
        assert ActivityService is not None
        assert callable(ActivityService)


class TestApplicationCreation:
    """Test that the FastAPI application can be created successfully"""

    def test_app_instance_exists(self):
        """Test that the FastAPI app instance is created"""
        from src.app import app
        from fastapi import FastAPI
        
        assert isinstance(app, FastAPI)
        assert app.title == "Mergington High School API"

    def test_app_has_routes(self):
        """Test that the app has the expected routes"""
        from src.app import app
        
        routes = [route.path for route in app.routes]
        
        # Check for expected endpoints
        assert "/" in routes
        assert "/activities" in routes
        assert "/activities/{activity_name}/signup" in routes
        assert "/activities/{activity_name}/unregister" in routes

    def test_app_has_static_files_mounted(self):
        """Test that static files are mounted"""
        from src.app import app
        
        routes = [route.path for route in app.routes]
        assert any("/static" in path for path in routes)

    def test_pydantic_models_defined(self):
        """Test that Pydantic request models are properly defined"""
        from src.app import SignupRequest, UnregisterRequest
        from pydantic import BaseModel
        
        assert issubclass(SignupRequest, BaseModel)
        assert issubclass(UnregisterRequest, BaseModel)
        
        # Verify fields exist
        assert "email" in SignupRequest.model_fields
        assert "email" in UnregisterRequest.model_fields


class TestDataStructures:
    """Test that all required data structures are properly initialized"""

    def test_activities_data_structures_exist(self):
        """Test that activity dictionaries are defined"""
        from src.app import activities_en, activities_hu
        
        assert isinstance(activities_en, dict)
        assert isinstance(activities_hu, dict)
        assert len(activities_en) > 0
        assert len(activities_hu) > 0

    def test_activity_mappings_exist(self):
        """Test that activity name mappings are defined"""
        from src.app import activity_name_mapping, activity_name_mapping_reverse
        
        assert isinstance(activity_name_mapping, dict)
        assert isinstance(activity_name_mapping_reverse, dict)
        assert len(activity_name_mapping) > 0
        assert len(activity_name_mapping_reverse) > 0

    def test_participants_storage_exists(self):
        """Test that participant storage is initialized"""
        from src.app import participants_storage
        
        assert isinstance(participants_storage, dict)

    def test_messages_dictionary_exists(self):
        """Test that message translations are defined"""
        from src.app import messages
        
        assert isinstance(messages, dict)
        assert "en" in messages
        assert "hu" in messages
        
        # Check required message keys
        for lang in ["en", "hu"]:
            assert "signed_up" in messages[lang]
            assert "unregistered" in messages[lang]
            assert "activity_full" in messages[lang]

    def test_activity_structure_valid(self):
        """Test that activities have the correct structure"""
        from src.app import activities_en
        
        for activity_name, activity_data in activities_en.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_activity_name_mapping_bidirectional(self):
        """Test that activity name mappings are bidirectional"""
        from src.app import activity_name_mapping, activity_name_mapping_reverse
        
        # Every English name should map to Hungarian and back
        for en_name, hu_name in activity_name_mapping.items():
            assert activity_name_mapping_reverse[hu_name] == en_name


class TestDependencies:
    """Test that all required dependencies are available"""

    def test_fastapi_available(self):
        """Test that FastAPI is installed"""
        try:
            import fastapi
            assert fastapi is not None
        except ImportError:
            pytest.fail("FastAPI is not installed")

    def test_pydantic_available(self):
        """Test that Pydantic is installed"""
        try:
            import pydantic
            assert pydantic is not None
        except ImportError:
            pytest.fail("Pydantic is not installed")

    def test_pydantic_email_validator_available(self):
        """Test that Pydantic email validator is available"""
        try:
            from pydantic import EmailStr
            assert EmailStr is not None
        except ImportError:
            pytest.fail("Pydantic EmailStr is not available. Install with: pip install pydantic[email]")

    def test_uvicorn_available(self):
        """Test that Uvicorn is installed"""
        try:
            import uvicorn
            assert uvicorn is not None
        except ImportError:
            pytest.fail("Uvicorn is not installed")

    def test_pytest_available(self):
        """Test that pytest is installed"""
        try:
            import pytest
            assert pytest is not None
        except ImportError:
            pytest.fail("pytest is not installed")

    def test_httpx_available(self):
        """Test that httpx is installed (required for TestClient)"""
        try:
            import httpx
            assert httpx is not None
        except ImportError:
            pytest.fail("httpx is not installed")


class TestStaticFiles:
    """Test that static files exist and are accessible"""

    def test_static_directory_exists(self):
        """Test that the static directory exists"""
        from pathlib import Path
        
        static_dir = Path(__file__).parent.parent / "src" / "static"
        assert static_dir.exists(), f"Static directory not found at {static_dir}"
        assert static_dir.is_dir(), f"{static_dir} is not a directory"

    def test_static_files_exist(self):
        """Test that required static files exist"""
        from pathlib import Path
        
        static_dir = Path(__file__).parent.parent / "src" / "static"
        
        required_files = ["index.html", "app.js", "styles.css"]
        
        for file_name in required_files:
            file_path = static_dir / file_name
            assert file_path.exists(), f"Required static file not found: {file_name}"
            assert file_path.is_file(), f"{file_name} is not a file"

    def test_index_html_valid(self):
        """Test that index.html contains required elements"""
        from pathlib import Path
        
        static_dir = Path(__file__).parent.parent / "src" / "static"
        index_path = static_dir / "index.html"
        
        content = index_path.read_text()
        
        # Check for basic HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        
        # Check for app-specific elements
        assert "activities-list" in content
        assert "signup-form" in content

    def test_app_js_valid(self):
        """Test that app.js contains required functionality"""
        from pathlib import Path
        
        static_dir = Path(__file__).parent.parent / "src" / "static"
        js_path = static_dir / "app.js"
        
        content = js_path.read_text()
        
        # Check for key functions and structures
        assert "translations" in content
        assert "fetchActivities" in content
        assert "signup" in content or "signup-form" in content


class TestEndpointFunctions:
    """Test that endpoint handler functions work correctly"""

    def test_activity_service_get_all_activities(self):
        """Test the ActivityService.get_all_activities method"""
        from src.app import get_activity_service
        
        service = get_activity_service()
        
        # Test English
        activities_en = service.get_all_activities("en")
        assert isinstance(activities_en, dict)
        assert len(activities_en) > 0
        
        # Test Hungarian
        activities_hu = service.get_all_activities("hu")
        assert isinstance(activities_hu, dict)
        assert len(activities_hu) > 0
        
        # Verify participants are synced
        for en_name, en_data in activities_en.items():
            if en_name in ["Chess Club"]:  # Test a specific activity
                en_participants = en_data["participants"]
                
                # Find corresponding Hungarian activity
                from src.app import activity_name_mapping
                hu_name = activity_name_mapping.get(en_name)
                if hu_name:
                    hu_participants = activities_hu[hu_name]["participants"]
                    assert en_participants == hu_participants, \
                        f"Participants not synced for {en_name}/{hu_name}"


class TestValidatorFunctions:
    """Test that validator functions work as expected"""

    def test_validate_and_translate_activity_name(self):
        """Test activity name validation and translation"""
        from src.validators import validate_and_translate_activity_name
        from src.app import activity_name_mapping_reverse, activities_en
        from fastapi import HTTPException
        
        # Test valid English name
        result = validate_and_translate_activity_name(
            "Chess Club", "en", activity_name_mapping_reverse, activities_en
        )
        assert result == "Chess Club"
        
        # Test valid Hungarian name
        result = validate_and_translate_activity_name(
            "Sakk Klub", "hu", activity_name_mapping_reverse, activities_en
        )
        assert result == "Chess Club"
        
        # Test invalid name should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_and_translate_activity_name(
                "Nonexistent Activity", "en", activity_name_mapping_reverse, activities_en
            )
        assert exc_info.value.status_code == 404

    def test_validate_capacity_available(self):
        """Test capacity validation"""
        from src.validators import validate_capacity_available
        from fastapi import HTTPException
        
        # Create test data
        activity = {"max_participants": 5}
        participants_storage = {"Test Activity": ["user1@test.com", "user2@test.com"]}
        
        # Should not raise when capacity available
        validate_capacity_available(
            "Test Activity", activity, participants_storage, "Activity is full"
        )
        
        # Fill to capacity
        participants_storage["Test Activity"] = [
            f"user{i}@test.com" for i in range(5)
        ]
        
        # Should raise when at capacity
        with pytest.raises(HTTPException) as exc_info:
            validate_capacity_available(
                "Test Activity", activity, participants_storage, "Activity is full"
            )
        assert exc_info.value.status_code == 400


class TestServerStartup:
    """Test that the server can be started (using TestClient as proxy)"""

    def test_server_can_start_via_test_client(self):
        """Test that the server can be started using TestClient"""
        from fastapi.testclient import TestClient
        from src.app import app
        
        try:
            client = TestClient(app)
            assert client is not None
        except Exception as e:
            pytest.fail(f"Failed to create TestClient (server startup simulation failed): {e}")

    def test_server_responds_to_requests(self):
        """Test that the server responds to basic requests"""
        from fastapi.testclient import TestClient
        from src.app import app
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Redirect
        
        # Test activities endpoint
        response = client.get("/activities")
        assert response.status_code == 200
        
        # Test OpenAPI docs are available
        response = client.get("/docs")
        assert response.status_code == 200


class TestCodeQuality:
    """Test code quality and best practices"""

    def test_no_syntax_errors_in_app(self):
        """Test that app.py has no syntax errors"""
        from pathlib import Path
        import py_compile
        
        app_path = Path(__file__).parent.parent / "src" / "app.py"
        
        try:
            py_compile.compile(str(app_path), doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Syntax error in app.py: {e}")

    def test_no_syntax_errors_in_validators(self):
        """Test that validators.py has no syntax errors"""
        from pathlib import Path
        import py_compile
        
        validators_path = Path(__file__).parent.parent / "src" / "validators.py"
        
        try:
            py_compile.compile(str(validators_path), doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Syntax error in validators.py: {e}")

    def test_no_syntax_errors_in_constants(self):
        """Test that constants.py has no syntax errors"""
        from pathlib import Path
        import py_compile
        
        constants_path = Path(__file__).parent.parent / "src" / "constants.py"
        
        try:
            py_compile.compile(str(constants_path), doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Syntax error in constants.py: {e}")

    def test_all_imports_resolve(self):
        """Test that all imports in modules can be resolved"""
        # This test will fail if there are circular imports or missing modules
        try:
            from src import app
            from src import validators
            from src import constants
        except ImportError as e:
            pytest.fail(f"Import resolution failed: {e}")
