"""Metrics collection and analysis for race condition tests.

This module provides the RaceMetricsCollector class for capturing timing data
during concurrent race condition tests, saving results to JSON files, and
validating metrics against alert thresholds.

Usage:
    collector = RaceMetricsCollector()
    collector.start_barrier_wait()
    # ... wait for barrier ...
    collector.record_request(thread_id=1, start_time=t0, end_time=t1, status_code=200)
    stats = collector.calculate_statistics()
    collector.save_to_json("TC-RACE-001", thread_count=10)
    collector.check_thresholds()  # Logs warnings if thresholds violated
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tests.race_config import (
    METRICS_OUTPUT_DIR,
    MAX_BARRIER_WAIT_THRESHOLD,
    MIN_REQUEST_SPREAD_THRESHOLD,
)


logger = logging.getLogger(__name__)


class RaceMetricsCollector:
    """Collects and analyzes timing metrics for race condition tests.

    Attributes:
        barrier_wait_start: Timestamp when threads begin waiting at barrier
        barrier_wait_end: Timestamp when barrier releases all threads
        requests: List of (thread_id, start_time, end_time, status_code) tuples
    """

    def __init__(self):
        """Initialize empty metrics collector."""
        self.barrier_wait_start: Optional[float] = None
        self.barrier_wait_end: Optional[float] = None
        self.requests: List[Tuple[int, float, float, int]] = []

    def start_barrier_wait(self) -> None:
        """Record when threads begin waiting at barrier."""
        self.barrier_wait_start = time.time()

    def end_barrier_wait(self) -> None:
        """Record when barrier releases threads."""
        self.barrier_wait_end = time.time()

    def record_request(
        self, thread_id: int, start_time: float, end_time: float, status_code: int
    ) -> None:
        """Record timing data for a single request.

        Args:
            thread_id: Unique identifier for the thread
            start_time: Timestamp when request started
            end_time: Timestamp when request completed
            status_code: HTTP status code from response
        """
        self.requests.append((thread_id, start_time, end_time, status_code))

    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate aggregate statistics from collected metrics.

        Returns:
            Dictionary containing:
                - barrier_wait_ms: Time spent waiting at barrier (milliseconds)
                - request_spread_ms: Time from first to last request start (milliseconds)
                - min_duration_ms: Fastest request duration
                - max_duration_ms: Slowest request duration
                - avg_duration_ms: Average request duration
                - success_count: Number of HTTP 2xx responses
                - failure_count: Number of HTTP 4xx/5xx responses
                - total_requests: Total number of requests recorded
        """
        if not self.requests:
            return {
                "barrier_wait_ms": 0,
                "request_spread_ms": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
                "avg_duration_ms": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_requests": 0,
            }

        # Calculate barrier wait time
        barrier_wait_ms = 0
        if self.barrier_wait_start and self.barrier_wait_end:
            barrier_wait_ms = (self.barrier_wait_end - self.barrier_wait_start) * 1000

        # Extract timing data
        start_times = [req[1] for req in self.requests]
        durations_ms = [(req[2] - req[1]) * 1000 for req in self.requests]
        status_codes = [req[3] for req in self.requests]

        # Calculate request spread (first to last request start)
        request_spread_ms = (max(start_times) - min(start_times)) * 1000

        # Calculate success/failure counts
        success_count = sum(1 for code in status_codes if 200 <= code < 300)
        failure_count = len(status_codes) - success_count

        return {
            "barrier_wait_ms": round(barrier_wait_ms, 2),
            "request_spread_ms": round(request_spread_ms, 2),
            "min_duration_ms": round(min(durations_ms), 2),
            "max_duration_ms": round(max(durations_ms), 2),
            "avg_duration_ms": round(sum(durations_ms) / len(durations_ms), 2),
            "success_count": success_count,
            "failure_count": failure_count,
            "total_requests": len(self.requests),
        }

    def save_to_json(self, test_id: str, thread_count: int) -> Path:
        """Save metrics to timestamped JSON file.

        Args:
            test_id: Test case identifier (e.g., "TC-RACE-001")
            thread_count: Number of concurrent threads in test

        Returns:
            Path to created JSON file
        """
        METRICS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_id}_{thread_count}threads_{timestamp}.json"
        filepath = METRICS_OUTPUT_DIR / filename

        stats = self.calculate_statistics()

        # Create comprehensive metrics document
        metrics_doc = {
            "test_id": test_id,
            "thread_count": thread_count,
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "raw_requests": [
                {
                    "thread_id": req[0],
                    "start_time": req[1],
                    "end_time": req[2],
                    "duration_ms": round((req[2] - req[1]) * 1000, 2),
                    "status_code": req[3],
                }
                for req in self.requests
            ],
        }

        with open(filepath, "w") as f:
            json.dump(metrics_doc, f, indent=2)

        logger.info(f"Saved race condition metrics to {filepath}")
        return filepath

    def log_summary(self) -> None:
        """Log human-readable summary of metrics to console."""
        stats = self.calculate_statistics()

        logger.info("=" * 60)
        logger.info("RACE CONDITION TEST METRICS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Barrier Wait Time:     {stats['barrier_wait_ms']:>8.2f} ms")
        logger.info(f"Request Spread:        {stats['request_spread_ms']:>8.2f} ms")
        logger.info(f"Request Duration (min):{stats['min_duration_ms']:>8.2f} ms")
        logger.info(f"Request Duration (avg):{stats['avg_duration_ms']:>8.2f} ms")
        logger.info(f"Request Duration (max):{stats['max_duration_ms']:>8.2f} ms")
        logger.info(f"Successful Requests:   {stats['success_count']:>8}")
        logger.info(f"Failed Requests:       {stats['failure_count']:>8}")
        logger.info(f"Total Requests:        {stats['total_requests']:>8}")
        logger.info("=" * 60)

    def check_thresholds(self) -> None:
        """Validate metrics against alert thresholds and log warnings.

        Logs warnings (but does not fail tests) if:
        - Average barrier wait time exceeds MAX_BARRIER_WAIT_THRESHOLD
        - Request spread is below MIN_REQUEST_SPREAD_THRESHOLD
        """
        stats = self.calculate_statistics()

        # Check barrier wait threshold
        barrier_wait_seconds = stats["barrier_wait_ms"] / 1000
        if barrier_wait_seconds > MAX_BARRIER_WAIT_THRESHOLD:
            logger.warning(
                f"⚠️  Barrier wait time ({barrier_wait_seconds:.2f}s) exceeds threshold "
                f"({MAX_BARRIER_WAIT_THRESHOLD}s). This may indicate CI resource constraints "
                f"or potential deadlocks. Consider increasing RACE_TEST_BARRIER_TIMEOUT."
            )

        # Check request spread threshold
        if stats["request_spread_ms"] < MIN_REQUEST_SPREAD_THRESHOLD:
            logger.warning(
                f"⚠️  Request spread ({stats['request_spread_ms']:.2f}ms) is below threshold "
                f"({MIN_REQUEST_SPREAD_THRESHOLD}ms). Race condition may be too deterministic "
                f"to validate concurrent behavior effectively."
            )
