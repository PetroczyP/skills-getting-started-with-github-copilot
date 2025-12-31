# Race Condition Testing Guide

**Last Updated:** December 28, 2025  
**Version:** 1.0  
**Audience:** Developers adding/maintaining race condition tests

---

## Table of Contents

1. [Overview](#overview)
2. [When to Add Race Condition Tests](#when-to-add-race-condition-tests)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Environment Variables](#environment-variables)
6. [Metrics Collection](#metrics-collection)
7. [Writing New Race Tests](#writing-new-race-tests)
8. [Debugging Race Tests](#debugging-race-tests)
9. [CI/CD Integration](#cicd-integration)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Race condition tests validate that the API correctly handles concurrent requests competing for limited resources. These tests use **Python's threading.Barrier** for precise synchronization and collect detailed timing metrics to verify test effectiveness.

**Why Race Condition Tests Matter:**
- **Data Integrity:** Prevent capacity overflow (13 participants when max=12)
- **User Experience:** Prevent duplicate registrations
- **System Reliability:** Detect concurrency bugs before production
- **Compliance:** Meet audit requirements for capacity enforcement

**Test Coverage:**
- 6 base test scenarios (TC-RACE-001 through TC-RACE-006)
- 8 total tests including parameterized variations
- Thread counts: 5, 10, 15, 20

---

## When to Add Race Condition Tests

Add race condition tests when:

✅ **Implementing resource contention features**
- Limited capacity (activity slots, inventory, reservations)
- Unique constraints (email uniqueness, username availability)
- Counter increments (view counts, like counts)

✅ **Modifying concurrent access logic**
- Database transaction boundaries
- Lock acquisition/release
- Atomic operations

✅ **Identifying production concurrency bugs**
- Capacity exceeded in logs
- Duplicate entries found
- Data corruption under load

❌ **Don't add race tests for:**
- Read-only operations (GET endpoints)
- Single-user flows
- Stateless operations
- Non-contending resources

---

## Quick Start

### Run All Race Tests

```bash
# All race condition tests (8 total)
pytest tests/test_app.py::TestRaceConditions -v

# With metrics collection
RACE_TEST_METRICS=true pytest tests/test_app.py::TestRaceConditions -v

# Specific test
pytest tests/test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race -v

# Skip race tests (faster CI)
pytest -m "not concurrency" -v
```

### View Metrics

```bash
# Analyze all metrics
python scripts/analyze_race_metrics.py --verbose

# Analyze specific test
python scripts/analyze_race_metrics.py --test-id TC-RACE-001 --verbose

# Exit code 0 = pass, 1 = threshold violations
echo $LASTEXITCODE  # Windows PowerShell
echo $?             # Linux/Mac bash
```

---

## Architecture

### Components

```
tests/
├── race_config.py           # Environment configuration, constants
├── race_metrics.py          # RaceMetricsCollector class
├── conftest.py              # Shared fixtures (race_metrics, verify_thread_cleanup)
├── test_app.py              # TestRaceConditions class with 6 tests
└── test_metrics/            # JSON metrics output (gitignored)
    └── race_conditions/
        └── TC-RACE-001_10threads_20251228_204553.json

scripts/
└── analyze_race_metrics.py  # CLI tool for metrics analysis
```

### Execution Flow

```
1. pytest discovers test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race
2. conftest.py provides race_metrics fixture (RaceMetricsCollector instance)
3. Test creates ThreadPoolExecutor with N threads
4. Test creates threading.Barrier(N, timeout=BARRIER_TIMEOUT)
5. Each thread:
   - Waits at barrier (race_metrics.start_barrier_wait())
   - Barrier releases all threads simultaneously
   - Executes API request (race_metrics.record_request())
6. Test collects results, verifies state integrity
7. Metrics saved to JSON (race_metrics.save_to_json())
8. verify_thread_cleanup fixture ensures cleanup (5s timeout)
```

### Synchronization Pattern

```python
from concurrent.futures import ThreadPoolExecutor
import threading

# Create barrier for precise synchronization
barrier = threading.Barrier(CONCURRENT_THREADS, timeout=BARRIER_TIMEOUT)

def signup_thread(email):
    # All threads wait here
    barrier.wait()  # Releases simultaneously when all N threads arrive
    
    # True concurrent execution starts here
    response = client.post(f"/activities/{activity}/signup", json={"email": email})
    return (email, response.status_code)

# Spawn threads
with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
    futures = [executor.submit(signup_thread, email) for email in emails]
    results = [f.result() for f in futures]
```

---

## Environment Variables

### RACE_TEST_BARRIER_TIMEOUT

**Purpose:** Maximum wait time for barrier synchronization

**Default:** `30` seconds (local development)  
**Recommended CI:** `60` seconds (slower resources)  
**Maximum:** `120` seconds (heavy CI load)

**Usage:**
```bash
# Windows PowerShell
$env:RACE_TEST_BARRIER_TIMEOUT=60
pytest tests/test_app.py::TestRaceConditions -v

# Linux/Mac bash
RACE_TEST_BARRIER_TIMEOUT=60 pytest tests/test_app.py::TestRaceConditions -v
```

**Symptoms of too low:**
- `BrokenBarrierError` or `TimeoutError`
- Tests fail with "barrier timeout exceeded"
- CI logs show slow thread creation

**Symptoms of too high:**
- Tests hang indefinitely on failures
- Poor developer experience (long waits)

### RACE_TEST_METRICS

**Purpose:** Enable/disable metrics collection

**Default:** `true` (collect metrics)  
**Disable:** `false` (skip metrics, faster execution)

**Usage:**
```bash
# Collect metrics (default)
RACE_TEST_METRICS=true pytest -m concurrency

# Skip metrics (faster)
RACE_TEST_METRICS=false pytest -m concurrency
```

**When to disable:**
- Quick smoke tests
- Local development iterations
- CI runs focused on pass/fail (not performance)

**When to enable:**
- Analyzing test effectiveness
- Debugging timing issues
- Validating CI environment performance

---

## Metrics Collection

### Automatic Collection

Every race test automatically collects:

| Metric | Description | Purpose |
|--------|-------------|---------|
| **Barrier Wait** | Start/end/duration of barrier wait | Detect CI resource constraints |
| **Request Timing** | Per-thread request execution time | Identify slow threads |
| **Success/Failure Counts** | Status code distribution | Verify expected outcomes |
| **Request Spread** | Time between first and last request | Validate true concurrency |

### JSON Format

```json
{
  "test_id": "TC-RACE-001",
  "thread_count": 10,
  "timestamp": "20251228_204553",
  "barrier_wait": {
    "start": "2025-12-28T20:45:53.123456",
    "end": "2025-12-28T20:45:53.172345",
    "duration_ms": 48.889
  },
  "requests": [
    {
      "thread_id": 0,
      "start": "2025-12-28T20:45:53.173000",
      "end": "2025-12-28T20:45:53.185000",
      "duration_ms": 12.0
    }
  ],
  "statistics": {
    "total_requests": 10,
    "successful_requests": 1,
    "failed_requests": 9,
    "avg_duration_ms": 11.2,
    "min_duration_ms": 9.5,
    "max_duration_ms": 14.3,
    "request_spread_ms": 3.66
  },
  "thresholds": {
    "barrier_wait_exceeded": false,
    "request_spread_too_low": true
  }
}
```

### Threshold Validation

| Threshold | Value | Purpose | Violation Indicates |
|-----------|-------|---------|---------------------|
| **MAX_BARRIER_WAIT** | 45s | Detect slow CI | Barrier wait > 45s → CI resource starvation |
| **MIN_REQUEST_SPREAD** | 5ms | Validate concurrency | Spread < 5ms → Too deterministic (Windows local) |

**Important:** Threshold violations are **warnings**, not failures. Tests can pass with warnings.

### Analyzing Metrics

```bash
# View all metrics
python scripts/analyze_race_metrics.py --verbose

# Output:
# Analyzing 4 metrics files...
#
# Test ID: TC-RACE-001
#   Files analyzed: 1
#   Avg barrier wait: 49ms
#   Avg request spread: 3.66ms
#   ⚠️  WARNING: Request spread below 5ms threshold (too deterministic)
#
# Test ID: TC-RACE-006
#   Files analyzed: 3
#   Avg barrier wait: 69ms
#   Avg request spread: 1.85ms (min), 4.12ms (max)
#   ⚠️  WARNING: Request spread below 5ms threshold
#
# Exit code: 1 (warnings present, but tests passed)
```

---

## Writing New Race Tests

### Template

```python
import pytest
from tests.race_config import CONCURRENT_THREADS, BARRIER_TIMEOUT
import threading
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.test_id("TC-RACE-007")
@pytest.mark.slow
@pytest.mark.concurrency
@pytest.mark.flaky(reruns=2, reruns_delay=2)
def test_concurrent_my_operation(client, race_metrics):
    """
    Test that concurrent [operation] correctly [expected behavior].
    
    Given: [Initial state]
    When: [N threads perform operation simultaneously]
    Then: [Expected outcome with exact counts]
    """
    # 1. Setup: Create test data with known state
    activity_name = "Test Activity"
    available_slots = 2
    thread_count = CONCURRENT_THREADS  # 10
    
    # TODO: Setup activity with initial state
    # response = client.post(...)
    
    # 2. Verify preconditions
    info = _get_activity_info(client, activity_name)
    assert info['available_slots'] == available_slots
    
    # 3. Create barrier for synchronization
    barrier = threading.Barrier(thread_count, timeout=BARRIER_TIMEOUT)
    
    # 4. Execute concurrent operation
    emails = [f"race_test_{i}@example.com" for i in range(thread_count)]
    results = _concurrent_signup(
        client=client,
        activity_name=activity_name,
        emails=emails,
        lang="en",
        barrier=barrier,
        race_metrics=race_metrics
    )
    
    # 5. Verify results
    successes = sum(1 for (email, status) in results if status == 200)
    failures = sum(1 for (email, status) in results if status == 400)
    
    assert successes == available_slots, f"Expected {available_slots} successes, got {successes}"
    assert failures == (thread_count - available_slots)
    
    # 6. Verify state integrity
    _verify_state_integrity(client, activity_name)
    
    # 7. Save metrics (automatic if RACE_TEST_METRICS=true)
    race_metrics.save_to_json(
        test_id="TC-RACE-007",
        thread_count=thread_count,
        success_count=successes,
        fail_count=failures
    )

def _concurrent_signup(client, activity_name, emails, lang, barrier, race_metrics):
    """Helper for concurrent signups with barrier synchronization."""
    results = []
    
    # Start barrier wait timing
    race_metrics.start_barrier_wait()
    
    def signup_thread(thread_id, email):
        try:
            # Wait at barrier
            barrier.wait()
            
            # Record barrier release
            if thread_id == 0:
                race_metrics.end_barrier_wait()
            
            # Execute request with timing
            race_metrics.start_request(thread_id)
            response = client.post(
                f"/activities/{activity_name}/signup?lang={lang}",
                json={"email": email}
            )
            race_metrics.end_request(thread_id, response.status_code)
            
            return (email, response.status_code)
        except Exception as e:
            return (email, -1)  # Error sentinel
    
    with ThreadPoolExecutor(max_workers=len(emails)) as executor:
        futures = [
            executor.submit(signup_thread, i, email) 
            for i, email in enumerate(emails)
        ]
        results = [f.result() for f in futures]
    
    return results

def _verify_state_integrity(client, activity_name):
    """Verify no race-induced data corruption."""
    response = client.get(f"/activities?lang=en")
    activities = response.json()
    
    activity = next(a for a in activities if a['name'] == activity_name)
    participants = activity['participants']
    
    # No duplicates
    assert len(participants) == len(set(participants)), "Duplicate participants found!"
    
    # Capacity not exceeded
    assert len(participants) <= activity['max_participants'], "Capacity exceeded!"
```

### Helper Methods (Already Implemented)

Use these helper methods in `test_app.py::TestRaceConditions`:

```python
# Execute concurrent signups with barrier
results = self._concurrent_signup(client, activity, emails, lang, barrier, race_metrics)

# Verify state integrity
self._verify_state_integrity(client, activity)

# Get activity info
info = self._get_activity_info(client, activity)
print(f"Available slots: {info['available_slots']}")
```

---

## Debugging Race Tests

### Enable Verbose Output

```bash
# See real-time test output
pytest tests/test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race -v -s

# Output:
# tests/test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race 
# Setting up activity with 11 participants, leaving 1 slot
# Spawning 10 threads for concurrent signup
# Barrier released at 2025-12-28 20:45:53.172
# Thread 0: 200 (success)
# Thread 1: 400 (full)
# ...
# Verifying state integrity
# Final participant count: 12
# PASSED
```

### Common Failures

#### BrokenBarrierError or TimeoutError

**Symptom:**
```
tests/test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race FAILED
BrokenBarrierError: barrier timeout exceeded
```

**Causes:**
- CI resources overloaded
- Barrier timeout too low
- Thread creation slower than expected

**Solutions:**
```bash
# Increase timeout
RACE_TEST_BARRIER_TIMEOUT=120 pytest -m concurrency

# Check CI resource utilization
# (GitHub Actions: review runner metrics)
```

#### Capacity Exceeded

**Symptom:**
```
AssertionError: Expected max 12 participants, found 13
```

**Causes:**
- **CRITICAL BUG:** Race condition in application logic
- Missing atomic capacity check
- Database transaction isolation issue

**Solutions:**
1. Review capacity enforcement logic in `src/service.py`
2. Ensure atomic read-check-update operations
3. Add database-level constraints if using persistent storage

#### Wrong Success Count

**Symptom:**
```
AssertionError: Expected 1 successes, got 2
```

**Causes:**
- Capacity check not atomic
- State corruption between threads
- Fixture state not properly reset

**Solutions:**
1. Verify `reset_participants` fixture runs
2. Check barrier synchronization (all threads waiting?)
3. Review application concurrency control

### Metrics Analysis

```bash
# Check if tests are truly concurrent
python scripts/analyze_race_metrics.py --test-id TC-RACE-001 --verbose

# Look for:
# - Request spread < 5ms → Too deterministic (Windows local, expected)
# - Request spread > 100ms → Threads not synchronized (barrier issue)
# - Barrier wait > 45s → CI resource constraint
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run infrastructure tests
        run: pytest -m infrastructure -v
      
      - name: Run functional tests
        run: pytest -m functional -v
      
      - name: Run race condition tests
        env:
          RACE_TEST_BARRIER_TIMEOUT: 60  # CI needs longer timeout
          RACE_TEST_METRICS: true
        run: pytest -m concurrency -v
      
      - name: Analyze race metrics
        run: |
          python scripts/analyze_race_metrics.py --verbose
          # Continues even on threshold warnings (exit code 1)
        continue-on-error: true
      
      - name: Upload metrics as artifacts
        uses: actions/upload-artifact@v3
        with:
          name: race-metrics
          path: test_metrics/race_conditions/*.json
```

### Performance Expectations

| Environment | Thread Count | Barrier Wait | Test Duration |
|-------------|--------------|--------------|---------------|
| **Local Windows** | 10 | 30-70ms | 0.2-0.5s per test |
| **Local Linux** | 10 | 40-100ms | 0.3-0.6s per test |
| **GitHub Actions** | 10 | 100-300ms | 0.5-2s per test |
| **Heavy CI Load** | 10 | 300ms-5s | 1-10s per test |

---

## Troubleshooting

### Tests Pass Locally, Fail in CI

**Symptom:** All tests pass on Windows, fail on Linux CI

**Likely Cause:** Environment differences

**Solutions:**
1. Check barrier timeout: `RACE_TEST_BARRIER_TIMEOUT=120`
2. Review metrics: Request spread on CI vs local
3. Test in Docker locally: `docker run --rm api-tests pytest -m concurrency`

### Tests Are Flaky

**Symptom:** Tests pass/fail intermittently

**Expected Behavior:** Some flakiness is normal with concurrency tests

**Solutions:**
1. Verify `@pytest.mark.flaky(reruns=2)` decorator present
2. Increase reruns: `@pytest.mark.flaky(reruns=3, reruns_delay=5)`
3. Check metrics for timing anomalies

### Metrics Show "Too Deterministic" Warning

**Symptom:**
```
⚠️  WARNING: Request spread below 5ms threshold (too deterministic)
```

**Is This a Problem?** No, this is expected on Windows local development.

**Explanation:**
- Windows thread scheduling is very predictable
- Linux CI will show realistic timing variance
- Tests still validate capacity enforcement correctly

**Action:** None required. Ignore warning on local Windows.

### Thread Cleanup Timeout

**Symptom:**
```
WARNING: 2 threads still active after 5s cleanup timeout
```

**Causes:**
- Threads blocked waiting for response
- Deadlock in application logic
- Barrier timeout exceeded

**Solutions:**
1. Check for application-level deadlocks
2. Review server logs for hung requests
3. Increase cleanup timeout in `conftest.py` if needed

---

## Best Practices Summary

✅ **DO:**
- Use barrier synchronization for true concurrent start
- Collect metrics to validate test effectiveness
- Verify state integrity after each race
- Use unique email patterns per test
- Test multiple thread counts for scalability
- Mark tests with `@pytest.mark.slow`, `@pytest.mark.concurrency`, `@pytest.mark.flaky`

❌ **DON'T:**
- Assume deterministic timing (especially on Windows)
- Skip state verification after concurrent operations
- Ignore metrics threshold warnings completely
- Run race tests without proper cleanup fixtures
- Test only single thread count
- Share test data between race tests (use unique emails)

---

## Additional Resources

- [TEST_STRATEGY.md](TEST_STRATEGY.md) - Testing philosophy and patterns
- [TEST_CASES.md](TEST_CASES.md) - Complete test case registry
- [DOCKER_TESTING.md](DOCKER_TESTING.md) - Cross-platform testing guide
- [Python threading.Barrier Documentation](https://docs.python.org/3/library/threading.html#barrier-objects)
- [pytest-rerunfailures Plugin](https://github.com/pytest-dev/pytest-rerunfailures)

---

**Questions or Issues?** Open an issue or update this guide!

**Last Updated:** December 28, 2025
