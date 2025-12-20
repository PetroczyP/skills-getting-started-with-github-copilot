# Contributing to Mergington High School Activities API

Thank you for your interest in contributing! This document provides guidelines for developers and AI agents working on this project.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Testing Strategy](#testing-strategy)
3. [Adding New Features](#adding-new-features)
4. [Adding New Tests](#adding-new-tests)
5. [Pre-Commit Hooks](#pre-commit-hooks)
6. [AI Agent Guidelines](#ai-agent-guidelines)
7. [Commit Message Conventions](#commit-message-conventions)
8. [Code Review Checklist](#code-review-checklist)

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/PetroczyP/skills-getting-started-with-github-copilot.git
   cd skills-getting-started-with-github-copilot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up pre-commit hook:**
   ```bash
   cp .githooks/pre-commit .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

4. **Verify installation:**
   ```bash
   pytest --version
   python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
   ```

### Running the Application

```bash
# Development server with auto-reload
cd src
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Access:
# - Web UI: http://localhost:8000/
# - API docs: http://localhost:8000/docs
```

### Running Tests

#### API Tests

```bash
# Run all API tests
pytest tests/test_app.py tests/test_infrastructure.py

# Run infrastructure tests first (recommended workflow)
pytest tests/test_infrastructure.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest -m functional
pytest -m capacity
```

#### UI Tests (Playwright)

**Setup (one-time):**
```bash
# Run automated setup script
./scripts/setup_venv.sh

# Or manual setup:
source venv/bin/activate
pip install playwright
playwright install chromium firefox webkit
```

**Running UI tests:**
```bash
# Run all UI tests (all browsers, headless)
./scripts/run_ui_tests.sh

# Headed mode (visible browser)
./scripts/run_ui_tests.sh --headed

# Specific browser only
./scripts/run_ui_tests.sh --browser chromium
./scripts/run_ui_tests.sh --browser firefox
./scripts/run_ui_tests.sh --browser webkit

# Debug mode (slow motion + visible)
./scripts/run_ui_tests.sh --debug

# Parallel execution
./scripts/run_ui_tests.sh --parallel

# Or use pytest directly
pytest tests/playwright/ -v
pytest tests/playwright/ --browser chromium --headed
pytest -m e2e
```

**See [docs/PLAYWRIGHT_IMPLEMENTATION.md](docs/PLAYWRIGHT_IMPLEMENTATION.md) for complete UI testing guide.**

---

## Testing Strategy

### Test Documentation

This project follows a **comprehensive test documentation framework**. Before adding tests, read:

- **[docs/testing/TEST_STRATEGY.md](docs/testing/TEST_STRATEGY.md)** - Overall approach and philosophy
- **[docs/testing/TEST_CASES.md](docs/testing/TEST_CASES.md)** - Test case registry with IDs
- **[docs/testing/TRACEABILITY_MATRIX.md](docs/testing/TRACEABILITY_MATRIX.md)** - Requirements mapping

### Test Organization

- **Functional tests** (`tests/test_app.py`) - API endpoint behavior
- **Infrastructure tests** (`tests/test_infrastructure.py`) - Setup and import validation
- **UI tests** (`tests/playwright/`) - End-to-end browser automation
- **BDD tests** (`tests/features/*.feature`) - Stakeholder-readable scenarios

### Why Run Infrastructure Tests First?

Infrastructure tests catch common errors early:
- Missing module imports
- Syntax errors
- Missing dependencies
- Data structure issues
- Server startup problems

**Always run before debugging:**
```bash
pytest tests/test_infrastructure.py
```

---

## Adding New Features

### Workflow

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement the feature:**
   - Follow existing patterns (see [.github/copilot-instructions.md](.github/copilot-instructions.md))
   - Maintain dual-language support (English/Hungarian)
   - Use request body pattern for POST/DELETE endpoints

3. **Add tests (REQUIRED):**
   - Add test ID decorator: `@pytest.mark.test_id("TC-AREA-NNN")`
   - Document in [docs/testing/TEST_CASES.md](docs/testing/TEST_CASES.md)
   - Update [docs/testing/TRACEABILITY_MATRIX.md](docs/testing/TRACEABILITY_MATRIX.md)

4. **Run tests:**
   ```bash
   pytest -v
   ```

5. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Pre-commit hook will automatically validate your changes.

6. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

---

## Adding New Tests

### Required Steps

#### 1. Determine Test ID

- Review [docs/testing/TEST_CASES.md](docs/testing/TEST_CASES.md) for existing IDs
- Use format: `TC-[AREA]-[NUMBER]`
- Area codes: `SIGNUP`, `UNREGISTER`, `ACTIVITIES`, `CAPACITY`, `LANGUAGE`, `INFRA-*`

#### 2. Write Test with Decorators

```python
import pytest

@pytest.mark.test_id("TC-SIGNUP-006")  # ← Required
@pytest.mark.functional                # ← Category marker
@pytest.mark.signup                    # ← Feature marker (optional)
def test_new_feature(client):
    """Brief description of what this tests."""
    # Test implementation
```

#### 3. Document Test Case

Add to [docs/testing/TEST_CASES.md](docs/testing/TEST_CASES.md):

```markdown
### TC-SIGNUP-006: Test Title

**Description:** What this test validates

**Preconditions:**
- Required setup state

**Test Steps:**
1. Step 1
2. Step 2

**Expected Results:**
- Result 1
- Result 2

**Test Data:**
- Data used in test

**Tags:** `functional`, `signup`
```

#### 4. Update Traceability Matrix

Link test to requirement in [docs/testing/TRACEABILITY_MATRIX.md](docs/testing/TRACEABILITY_MATRIX.md).

#### 5. Create BDD Scenario (if user-facing)

Create/update `.feature` file in `tests/features/`:

```gherkin
Scenario: New feature scenario
  Given precondition
  When action performed
  Then expected result
```

Add step definitions in `tests/step_defs/`.

#### 6. Validate

```bash
# Run new test
pytest -k "TC_SIGNUP_006" -v

# Run pre-commit checks
.githooks/pre-commit
```

---

## Adding UI Tests (Playwright)

### Overview

UI tests use Playwright for browser automation with the **Page Object Model** pattern. All UI tests:
- Run on all browsers (Chromium, Firefox, WebKit)
- Use Page Objects for maintainability
- Follow TC-UI-AREA-NNN ID convention
- Include @pytest.mark.e2e marker

### Setup

Ensure Playwright is installed:
```bash
./scripts/setup_venv.sh
```

### Writing a New UI Test

#### 1. Determine Test ID
- Check [docs/testing/TEST_CASES.md](docs/testing/TEST_CASES.md)
- Use format: `TC-UI-[AREA]-[NUMBER]`
- Area codes: `LANG`, `SIGNUP`, `UNREG`, `CAPACITY`, `DISPLAY`

#### 2. Create Test Using Page Object

```python
import pytest
from tests.playwright.pages.activities_page import ActivitiesPage

@pytest.mark.test_id("TC-UI-SIGNUP-007")
@pytest.mark.e2e
def test_new_ui_feature(activities_page: ActivitiesPage):
    """Test description."""
    # Load page
    activities_page.load()
    
    # Perform actions using Page Object methods
    activities_page.signup("test@mergington.edu", "Chess Club")
    
    # Verify results
    assert activities_page.is_success_message()
    assert activities_page.has_participant("Chess Club", "test@mergington.edu")
```

#### 3. Use Page Object Methods

Key methods available in `ActivitiesPage`:
- `load()` - Navigate to activities page
- `switch_to_language(lang)` - Toggle EN/HU
- `signup(email, activity)` - Fill and submit form
- `delete_participant(email, activity, confirm)` - Delete with dialog handling
- `has_participant(activity, email)` - Check participant exists
- `get_spots_left(activity)` - Get available spots
- `is_success_message()` / `is_error_message()` - Check message type

See [tests/playwright/pages/activities_page.py](tests/playwright/pages/activities_page.py) for all methods.

#### 4. Fast Test Data Setup with API Helper

Use `api_helper` or `fill_activity_to_capacity` fixtures for fast setup:

```python
@pytest.mark.test_id("TC-UI-CAPACITY-006")
@pytest.mark.e2e
def test_capacity_scenario(activities_page, fill_activity_to_capacity):
    """Test behavior when activity is full."""
    # Fast setup via API (not UI clicks)
    fill_activity_to_capacity("Chess Club", "en")
    
    # Reload UI to reflect state
    activities_page.reload()
    
    # Test UI behavior
    activities_page.signup("overflow@mergington.edu", "Chess Club")
    assert activities_page.is_error_message()
```

#### 5. Handling Dialogs

For confirmation dialogs (like delete):

```python
# Accept confirmation
activities_page.delete_participant(
    "michael@mergington.edu",
    "Chess Club",
    confirm=True
)

# Cancel confirmation
activities_page.delete_participant(
    "michael@mergington.edu",
    "Chess Club",
    confirm=False
)
```

#### 6. Multi-Browser Testing

Tests run on all browsers by default. To skip specific browsers:

```python
@pytest.mark.test_id("TC-UI-LANG-007")
@pytest.mark.e2e
@pytest.mark.skip_firefox  # Skip on Firefox only
def test_chrome_specific_feature(activities_page):
    """Test that only works on Chromium/WebKit."""
    # Test implementation
```

#### 7. Debugging UI Tests

**Headed mode (visible browser):**
```bash
./scripts/run_ui_tests.sh --headed
```

**Debug mode (slow motion + visible):**
```bash
./scripts/run_ui_tests.sh --debug
```

**Take screenshots:**
```python
activities_page.screenshot("debug.png")
```

#### 8. Adding BDD Scenarios for UI

For critical user flows, add Gherkin scenarios:

**Create feature file** in `tests/features/ui/`:
```gherkin
# tests/features/ui/new_feature.feature
Feature: New UI Feature
  As a user
  I want to perform some action
  So that I can achieve some goal

  Scenario: Success case
    Given I am on the activities page
    When I perform some action
    Then I should see expected result
```

**Add step definitions** in `tests/step_defs/ui_steps.py`:
```python
from pytest_bdd import scenarios, when, then

scenarios('../features/ui/new_feature.feature')

@when("I perform some action")
def perform_action(activities_page):
    activities_page.some_method()

@then("I should see expected result")
def verify_result(activities_page):
    assert activities_page.some_check()
```

#### 9. Document and Validate

1. **Update TEST_CASES.md** with test entry
2. **Run the test:**
   ```bash
   pytest tests/playwright/test_ui_newfile.py -v
   ```
3. **Run on all browsers:**
   ```bash
   ./scripts/run_ui_tests.sh
   ```
4. **Pre-commit validation:**
   ```bash
   .githooks/pre-commit
   ```

### Page Object Model Guidelines

**When to add new Page Object:**
- New page added to application
- Complex component with many interactions
- Reusable across multiple tests

**How to create Page Object:**

1. **Extend BasePage:**
   ```python
   from tests.playwright.pages.base_page import BasePage
   
   class NewPage(BasePage):
       def __init__(self, page):
           super().__init__(page)
           self.url = "/new-page"
   ```

2. **Define locators:**
   ```python
   # Selectors
   self.some_button = "button#submit"
   self.some_input = "input#email"
   ```

3. **Add interaction methods:**
   ```python
   def perform_action(self, value: str):
       """Perform some action on the page."""
       self.fill(self.some_input, value)
       self.click(self.some_button)
   ```

4. **Add verification methods:**
   ```python
   def has_expected_state(self) -> bool:
       """Check if page is in expected state."""
       return self.is_visible(self.some_element)
   ```

---

## Pre-Commit Hooks

### Setup

```bash
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### What It Checks

1. ✅ All test functions have `@pytest.mark.test_id()` decorators
2. ✅ Test IDs follow `TC-[AREA]-[NUMBER]` format
3. ✅ No duplicate test IDs
4. ✅ All tests pass
5. ✅ No syntax errors
6. ⚠️ Coverage threshold (warning only)

### Bypass (not recommended)

```bash
git commit --no-verify
```

**Only bypass when:**
- Documentation-only changes
- Non-code file updates (README, etc.)
- Emergency hotfixes (fix tests immediately after)

---

## AI Agent Guidelines

### For AI Agents Working on This Codebase

**CRITICAL: Read these files first:**

1. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Project patterns and conventions
2. **[docs/testing/TEST_STRATEGY.md](docs/testing/TEST_STRATEGY.md)** - Testing approach
3. **[docs/testing/TEST_CASES.md](docs/testing/TEST_CASES.md)** - Test case registry

### When Adding Code

1. **Check existing patterns:**
   - Dual-language architecture (English/Hungarian sync)
   - Request body pattern for POST/DELETE
   - Capacity enforcement logic
   - Email validation with Pydantic EmailStr

2. **Follow naming conventions:**
   - Test-specific emails: `feature_test_N@mergington.edu`
   - Helper methods: `_get_activity_info()`, `_helper_name()`
   - Class constants: `OVERFLOW_TEST_COUNT = 3`

3. **Update documentation:**
   - Add test IDs to all new tests
   - Update TEST_CASES.md
   - Update TRACEABILITY_MATRIX.md
   - Update copilot-instructions.md if patterns change

### When Debugging

1. **Run infrastructure tests first:**
   ```bash
   pytest tests/test_infrastructure.py
   ```

2. **Check for common issues:**
   - Missing `@pytest.mark.test_id()` decorator
   - Fixture state not reset (should use `reset_participants`)
   - Email conflicts between tests
   - Language sync issues (EN/HU participants)

---

## Commit Message Conventions

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding/updating tests
- `refactor`: Code refactoring
- `style`: Formatting changes
- `chore`: Build/tooling changes

### Examples

```
feat(api): add activity capacity waitlist feature

Implements waitlist functionality when activities reach capacity.
Students can join waitlist and are automatically registered when
spots become available.

Closes #42
```

```
test(capacity): add overflow signup test cases

Added TC-CAPACITY-005 through TC-CAPACITY-007 to verify waitlist
behavior when activities are at capacity.

Updated TEST_CASES.md and TRACEABILITY_MATRIX.md.
```

```
docs(testing): update TEST_STRATEGY.md with BDD guidelines

Added section on when to use BDD scenarios vs traditional tests.
Includes Gherkin template examples.
```

---

## Code Review Checklist

### For Reviewers

- [ ] Code follows project patterns (dual-language, request body, etc.)
- [ ] All tests have `@pytest.mark.test_id()` decorators
- [ ] Test IDs are unique and follow convention
- [ ] Tests documented in TEST_CASES.md
- [ ] Traceability matrix updated
- [ ] Pre-commit hook passes
- [ ] Coverage maintained/improved
- [ ] API documentation updated if endpoints changed
- [ ] BDD scenarios added for user-facing features
- [ ] Commit messages follow conventions

### For Contributors

Before requesting review:

1. **Run full test suite:**
   ```bash
   pytest -v
   ```

2. **Check coverage:**
   ```bash
   pytest --cov=src --cov-report=term
   ```

3. **Verify pre-commit hook:**
   ```bash
   .githooks/pre-commit
   ```

4. **Update documentation:**
   - [ ] copilot-instructions.md (if patterns changed)
   - [ ] TEST_CASES.md (new tests)
   - [ ] TRACEABILITY_MATRIX.md (new requirements)
   - [ ] API_MIGRATION.md (breaking changes)

---

## Questions?

- **Project patterns:** See [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Testing strategy:** See [docs/testing/TEST_STRATEGY.md](docs/testing/TEST_STRATEGY.md)
- **API documentation:** Visit http://localhost:8000/docs (when server running)

---

**Happy Contributing!** 🎉
