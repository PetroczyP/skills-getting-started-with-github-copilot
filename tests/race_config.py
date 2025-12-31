"""Configuration for race condition tests.

This module provides environment-configurable settings for concurrent signup
race condition testing, including timing parameters and alert thresholds.

Environment Variables:
    RACE_TEST_BARRIER_TIMEOUT: Timeout in seconds for barrier synchronization.
        Default: 30 seconds (CI recommended: 60 seconds for resource-constrained environments)

    RACE_TEST_METRICS: Enable JSON metrics collection and logging.
        Default: "true" (set to "false" to disable)

Alert Thresholds:
    MAX_BARRIER_WAIT_THRESHOLD: Maximum acceptable average barrier wait time.
        If exceeded, indicates potential CI resource constraints or deadlocks.
        Default: 45.0 seconds

    MIN_REQUEST_SPREAD_THRESHOLD: Minimum acceptable time spread between first/last request.
        If too low (< 5ms), indicates race condition is too deterministic to be meaningful.
        Default: 5.0 milliseconds

Constants:
    CONCURRENT_THREADS: Default number of concurrent threads for race testing.
        Chosen to match Playwright fixture ThreadPoolExecutor configuration.
        Default: 10 threads

    THREAD_CLEANUP_TIMEOUT: Maximum time to wait for threads to complete after test.
        Default: 5.0 seconds
"""

import os
from pathlib import Path


# Thread configuration
CONCURRENT_THREADS = 10
"""Default number of concurrent threads used in race condition tests.
Matches the ThreadPoolExecutor configuration in Playwright fixtures for consistency."""

# Timing configuration
BARRIER_TIMEOUT = int(os.getenv("RACE_TEST_BARRIER_TIMEOUT", "30"))
"""Timeout in seconds for threading.Barrier synchronization.
CI environments should use 60s: RACE_TEST_BARRIER_TIMEOUT=60"""

THREAD_CLEANUP_TIMEOUT = 5.0
"""Maximum time to wait for thread cleanup after test completion (seconds)."""


# Metrics configuration
def _parse_bool_env(value: str) -> bool:
    """Parse boolean environment variable with flexible value support.

    Accepts: true/yes/on/1 (case-insensitive) as True, anything else as False.
    """
    return value.lower() in ("true", "yes", "on", "1")


ENABLE_TIMING_METRICS = _parse_bool_env(os.getenv("RACE_TEST_METRICS", "true"))
"""Whether to collect and save detailed timing metrics to JSON files."""

METRICS_OUTPUT_DIR = Path("test_metrics/race_conditions")
"""Directory for storing JSON metrics files with timestamps."""

# Alert thresholds for CI metrics validation
MAX_BARRIER_WAIT_THRESHOLD = 45.0
"""Maximum acceptable barrier wait time in seconds (total, not average).
Exceeding this threshold may indicate CI resource constraints or deadlocks."""

MIN_REQUEST_SPREAD_THRESHOLD = 5.0
"""Minimum acceptable request spread in milliseconds (first to last request).
Values below this indicate race condition is too deterministic to be meaningful."""
