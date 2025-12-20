#!/usr/bin/env python3
"""
Script to add test ID decorators to test functions.

This script scans test files and adds @pytest.mark.test_id() decorators
based on the test case mappings defined in TEST_CASES.md.
"""

import re
from pathlib import Path

# Test ID mappings from TEST_CASES.md
TEST_IDS = {
    # test_app.py mappings
    "test_root_redirects_to_static": "TC-ROOT-001",
    "test_get_activities_returns_all_activities_en": "TC-ACTIVITIES-001",
    "test_get_activities_returns_all_activities_hu": "TC-ACTIVITIES-002",
    "test_get_activities_defaults_to_english": "TC-LANGUAGE-002",
    "test_get_activities_returns_correct_structure": "TC-ACTIVITIES-004",
    "test_get_activities_returns_participant_lists": "TC-ACTIVITIES-005",
    "test_get_activities_same_participants_both_languages": "TC-LANGUAGE-001",
    "test_signup_for_existing_activity_en": "TC-SIGNUP-001",
    "test_signup_for_existing_activity_hu": "TC-SIGNUP-002",
    "test_signup_for_nonexistent_activity": "TC-SIGNUP-003",
    "test_signup_when_already_registered": "TC-SIGNUP-004",
    "test_multiple_students_can_signup": "TC-SIGNUP-005",
    "test_signup_rejected_when_activity_at_capacity_en": "TC-CAPACITY-001",
    "test_signup_rejected_when_activity_at_capacity_hu": "TC-CAPACITY-002",
    "test_signup_allowed_when_one_below_capacity": "TC-CAPACITY-003",
    "test_capacity_check_with_sequential_signups": "TC-CAPACITY-004",
    "test_unregister_from_activity_en": "TC-UNREGISTER-001",
    "test_unregister_from_activity_hu": "TC-UNREGISTER-002",
    "test_unregister_from_nonexistent_activity": "TC-UNREGISTER-003",
    "test_unregister_when_not_registered": "TC-UNREGISTER-004",
    "test_unregister_then_signup_again": "TC-UNREGISTER-005",
    
    # test_infrastructure.py mappings
    "test_import_app_module": "TC-INFRA-IMPORT-001",
    "test_import_constants_module": "TC-INFRA-IMPORT-002",
    "test_import_validators_module": "TC-INFRA-IMPORT-003",
    "test_import_models_module": "TC-INFRA-IMPORT-004",
    "test_import_service_module": "TC-INFRA-IMPORT-005",
    "test_import_exceptions_module": "TC-INFRA-IMPORT-006",
    "test_all_constants_available": "TC-INFRA-IMPORT-007",
    "test_all_validators_available": "TC-INFRA-IMPORT-008",
    "test_all_models_available": "TC-INFRA-IMPORT-009",
    "test_all_exceptions_available": "TC-INFRA-IMPORT-010",
    "test_service_class_available": "TC-INFRA-IMPORT-011",
    "test_app_instance_exists": "TC-INFRA-APP-001",
    "test_app_has_routes": "TC-INFRA-APP-002",
    "test_app_has_static_files_mounted": "TC-INFRA-APP-003",
    "test_pydantic_models_defined": "TC-INFRA-APP-004",
    "test_activities_data_structures_exist": "TC-INFRA-DATA-001",
    "test_activity_mappings_exist": "TC-INFRA-DATA-002",
    "test_participants_storage_exists": "TC-INFRA-DATA-003",
    "test_messages_dictionary_exists": "TC-INFRA-DATA-004",
    "test_activity_structure_valid": "TC-INFRA-DATA-005",
    "test_activity_name_mapping_bidirectional": "TC-INFRA-DATA-006",
    "test_fastapi_available": "TC-INFRA-DEPS-001",
    "test_pydantic_available": "TC-INFRA-DEPS-002",
    "test_pydantic_email_validator_available": "TC-INFRA-DEPS-003",
    "test_uvicorn_available": "TC-INFRA-DEPS-004",
    "test_pytest_available": "TC-INFRA-DEPS-005",
    "test_httpx_available": "TC-INFRA-DEPS-006",
    "test_static_directory_exists": "TC-INFRA-FILES-001",
    "test_static_files_exist": "TC-INFRA-FILES-002",
    "test_index_html_valid": "TC-INFRA-FILES-003",
    "test_app_js_valid": "TC-INFRA-FILES-004",
    "test_activity_service_get_all_activities": "TC-INFRA-ENDPOINT-001",
    "test_validate_and_translate_activity_name": "TC-INFRA-VALIDATOR-001",
    "test_validate_capacity_available": "TC-INFRA-VALIDATOR-002",
    "test_server_can_start_via_test_client": "TC-INFRA-SERVER-001",
    "test_server_responds_to_requests": "TC-INFRA-SERVER-002",
    "test_no_syntax_errors_in_app": "TC-INFRA-QUALITY-001",
    "test_no_syntax_errors_in_validators": "TC-INFRA-QUALITY-002",
    "test_no_syntax_errors_in_constants": "TC-INFRA-QUALITY-003",
    "test_all_imports_resolve": "TC-INFRA-QUALITY-004",
}


def add_test_id_decorator(file_path: Path):
    """Add @pytest.mark.test_id decorators to test functions."""
    
    content = file_path.read_text()
    lines = content.split('\n')
    modified_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a test function definition
        match = re.match(r'(\s*)def (test_\w+)\(', line)
        if match:
            indent = match.group(1)
            test_name = match.group(2)
            
            # Check if test ID decorator already exists
            prev_line_idx = i - 1
            has_test_id = False
            while prev_line_idx >= 0 and (lines[prev_line_idx].strip().startswith('@') or not lines[prev_line_idx].strip()):
                if '@pytest.mark.test_id' in lines[prev_line_idx]:
                    has_test_id = True
                    break
                prev_line_idx -= 1
            
            # Add test ID if not present and we have a mapping
            if not has_test_id and test_name in TEST_IDS:
                test_id = TEST_IDS[test_name]
                modified_lines.append(f'{indent}@pytest.mark.test_id("{test_id}")')
        
        modified_lines.append(line)
        i += 1
    
    # Write back
    file_path.write_text('\n'.join(modified_lines))
    print(f"✅ Updated {file_path}")


if __name__ == "__main__":
    # Add decorators to test files
    test_app = Path("tests/test_app.py")
    test_infra = Path("tests/test_infrastructure.py")
    
    if test_app.exists():
        add_test_id_decorator(test_app)
    
    if test_infra.exists():
        add_test_id_decorator(test_infra)
    
    print("\n✅ Test ID decorators added successfully!")
    print("Run 'pytest --collect-only' to verify test IDs.")
