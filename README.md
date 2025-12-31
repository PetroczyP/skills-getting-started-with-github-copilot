# Getting Started with GitHub Copilot - Mergington High School Activities API

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

## Overview

A bilingual (English/Hungarian) FastAPI application for managing high school extracurricular activities. Students can view activities and register/unregister via a web UI or REST API.

**Tech Stack:** FastAPI, Python 3.10+, vanilla JavaScript, Playwright

---

## Quick Start

### Setup

```bash
# Clone repository
git clone https://github.com/PetroczyP/skills-getting-started-with-github-copilot.git
cd skills-getting-started-with-github-copilot

# Install dependencies
pip install -r requirements.txt

# Run server
cd src && uvicorn app:app --reload
```

Access:
- **Web UI:** http://localhost:8000/
- **API Docs:** http://localhost:8000/docs

---

## Testing

This project has **97 automated tests** covering API endpoints, UI workflows, and concurrent race conditions.

### Run API Tests
```bash
# All API tests
pytest tests/test_app.py tests/test_infrastructure.py -v

# Race condition tests
pytest -m concurrency -v

# With coverage
pytest --cov=src --cov-report=html
```

### Run UI Tests (Playwright)
```bash
# Setup (one-time)
./scripts/setup_venv.sh

# Run all UI tests (all browsers)
./scripts/run_ui_tests.sh

# Debug mode (visible browser, slow motion)
./scripts/run_ui_tests.sh --debug
```

### Docker Testing (Cross-Platform)
```bash
# Run tests in Linux container
docker build -f Dockerfile.test -t api-tests .
docker run --rm api-tests pytest -m concurrency -v

# Or use the automated script
./scripts/run_docker_tests.sh
```

**Test Documentation:**
- [Test Strategy](docs/testing/TEST_STRATEGY.md) - Overall approach
- [Test Cases](docs/testing/TEST_CASES.md) - 97 test case registry
- [Race Condition Testing](docs/testing/RACE_CONDITION_TESTING.md) - Concurrency test guide
- [Docker Testing](docs/testing/DOCKER_TESTING.md) - Cross-platform testing
- [Playwright Guide](docs/PLAYWRIGHT_IMPLEMENTATION.md) - UI testing setup
- [Contributing](CONTRIBUTING.md) - How to add tests

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Writing tests (API and UI)
- Page Object Model guidelines
- Pre-commit hooks
- Commit conventions

---

## Original Exercise

Hey PetroczyP!

Mona here. I'm done preparing your exercise. Hope you enjoy! 💚

Remember, it's self-paced so feel free to take a break! ☕️

[![](https://img.shields.io/badge/Go%20to%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/PetroczyP/skills-getting-started-with-github-copilot/issues/1)

---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)

