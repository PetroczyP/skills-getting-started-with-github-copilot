# Playwright UI Testing - Quick Start Guide

**Last Updated:** December 20, 2025  
**Status:** ✅ Ready to use

---

## 🚀 Quick Start (3 steps)

### 1. Setup Virtual Environment & Playwright

```bash
./scripts/setup_venv.sh
```

This automatically:
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies
- ✅ Installs Chromium, Firefox, and WebKit browsers
- ✅ Verifies installation

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Run UI Tests

```bash
# All browsers, headless mode (default)
./scripts/run_ui_tests.sh

# Watch tests run (visible browser)
./scripts/run_ui_tests.sh --headed

# Debug mode (slow motion + visible)
./scripts/run_ui_tests.sh --debug
```

**That's it! 🎉**

---

## 📖 Common Commands

### Running Tests

```bash
# All UI tests (all browsers, headless)
./scripts/run_ui_tests.sh

# Specific browser
./scripts/run_ui_tests.sh --browser chromium
./scripts/run_ui_tests.sh --browser firefox
./scripts/run_ui_tests.sh --browser webkit

# Headed mode (see the browser)
./scripts/run_ui_tests.sh --headed

# Slow motion (500ms delay between actions)
./scripts/run_ui_tests.sh --slowmo

# Debug mode (headed + slow motion 1000ms)
./scripts/run_ui_tests.sh --debug

# Parallel execution (faster)
./scripts/run_ui_tests.sh --parallel

# Combine options
./scripts/run_ui_tests.sh --browser firefox --headed --slowmo
```

### Using pytest Directly

```bash
# All UI tests
pytest tests/playwright/ -v

# Specific test file
pytest tests/playwright/test_ui_language.py -v

# Specific test by marker
pytest -m e2e
pytest -m ui

# Specific browser
pytest tests/playwright/ --browser chromium

# Headed mode
pytest tests/playwright/ --headed

# Slowmo
pytest tests/playwright/ --slowmo 500
```

---

## 🧪 What Gets Tested?

### 30 UI Tests Across 5 Categories

| Category | Tests | Coverage |
|----------|-------|----------|
| **Language Switching** | 6 | EN/HU toggle, localStorage, translation sync |
| **Signup** | 6 | Form submission, validation, duplicates |
| **Unregister** | 6 | Delete confirmation, cancel, cross-language sync |
| **Capacity** | 5 | Full activity error, spots calculation |
| **Display** | 7 | Activity list, cards, dropdown, participants |

### All Tests Run On:
- ✅ Chromium (Chrome/Edge)
- ✅ Firefox
- ✅ WebKit (Safari)

---

## 🔧 Troubleshooting

### "Virtual environment not activated"

**Fix:**
```bash
source venv/bin/activate
```

### "Playwright not installed"

**Fix:**
```bash
pip install playwright
playwright install chromium firefox webkit
```

Or run the setup script again:
```bash
./scripts/setup_venv.sh
```

### Tests fail with "Server not running"

**Don't worry!** The tests start the server automatically via the `start_server` fixture.

If you need to start it manually:
```bash
cd src && uvicorn app:app --reload
```

### Test fails with "Element not found"

**Debug with headed mode:**
```bash
./scripts/run_ui_tests.sh --debug
```

This runs slowly with visible browser so you can see what's happening.

---

## 📁 Project Structure

```
tests/playwright/              # UI test files
├── conftest.py                # Fixtures (server, state reset, helpers)
├── test_ui_language.py        # Language switching tests
├── test_ui_signup.py          # Signup form tests
├── test_ui_unregister.py      # Delete participant tests
├── test_ui_capacity.py        # Capacity enforcement tests
├── test_ui_display.py         # Activity display tests
└── pages/                     # Page Object Model
    ├── base_page.py           # Base class with common methods
    └── activities_page.py     # Activities page specific methods

tests/features/ui/             # BDD Gherkin scenarios
├── language_switching.feature
├── participant_management.feature
└── activity_display.feature

tests/step_defs/
└── ui_steps.py                # BDD step definitions

scripts/
├── setup_venv.sh              # One-time setup script
└── run_ui_tests.sh            # Test execution script
```

---

## 📚 Learn More

- **[PLAYWRIGHT_IMPLEMENTATION.md](docs/PLAYWRIGHT_IMPLEMENTATION.md)** - Complete implementation guide
- **[TEST_STRATEGY.md](docs/testing/TEST_STRATEGY.md)** - Testing philosophy and approach
- **[TEST_CASES.md](docs/testing/TEST_CASES.md)** - All 91 test cases documented
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to add new UI tests

---

## 🎯 Next Steps

### Write Your First UI Test

1. **Determine test ID** (check TEST_CASES.md)
2. **Create test file** in `tests/playwright/`
3. **Use Page Object:**

```python
import pytest
from tests.playwright.pages.activities_page import ActivitiesPage

@pytest.mark.test_id("TC-UI-SIGNUP-007")
@pytest.mark.e2e
def test_my_feature(activities_page: ActivitiesPage):
    """Test description."""
    activities_page.load()
    activities_page.signup("test@mergington.edu", "Chess Club")
    assert activities_page.is_success_message()
```

4. **Run your test:**

```bash
pytest tests/playwright/test_ui_signup.py::test_my_feature -v --headed
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guide on adding UI tests.

---

**Happy Testing! 🚀**

