#!/usr/bin/env python3
"""Analyze race condition test metrics and validate alert thresholds.

This script scans the test_metrics/race_conditions directory for JSON metrics files,
aggregates statistics, identifies anomalies, and validates against alert thresholds.

Usage:
    python scripts/analyze_race_metrics.py
    python scripts/analyze_race_metrics.py --directory test_metrics/race_conditions
    python scripts/analyze_race_metrics.py --test-id TC-RACE-001
    python scripts/analyze_race_metrics.py --since-date 2025-12-01

Exit Codes:
    0: All metrics pass thresholds
    1: One or more threshold violations detected (CI should fail)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


# Alert thresholds (match tests/race_config.py)
MAX_BARRIER_WAIT_THRESHOLD = 45.0  # seconds
MIN_REQUEST_SPREAD_THRESHOLD = 5.0  # milliseconds


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze race condition test metrics and validate thresholds"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("test_metrics/race_conditions"),
        help="Directory containing metrics JSON files (default: test_metrics/race_conditions)",
    )
    parser.add_argument(
        "--test-id", type=str, help="Filter by specific test ID (e.g., TC-RACE-001)"
    )
    parser.add_argument(
        "--since-date", type=str, help="Filter metrics since date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output for each metrics file",
    )
    return parser.parse_args()


def load_metrics_files(
    directory: Path, test_id_filter: str = None, since_date: str = None
) -> List[Tuple[Path, Dict]]:
    """Load and filter JSON metrics files.

    Args:
        directory: Path to metrics directory
        test_id_filter: Optional test ID to filter by
        since_date: Optional date string (YYYY-MM-DD) to filter by

    Returns:
        List of (filepath, metrics_dict) tuples
    """
    if not directory.exists():
        print(f"⚠️  Metrics directory not found: {directory}")
        print(
            "No metrics collected yet. Run race condition tests with RACE_TEST_METRICS=true"
        )
        return []

    metrics_files = []
    cutoff_date = None

    if since_date:
        try:
            cutoff_date = datetime.strptime(since_date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Invalid date format: {since_date}. Use YYYY-MM-DD")
            sys.exit(1)

    for json_file in directory.glob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)

            # Filter by test ID
            if test_id_filter and data.get("test_id") != test_id_filter:
                continue

            # Filter by date
            if cutoff_date:
                timestamp = datetime.fromisoformat(data.get("timestamp", ""))
                if timestamp < cutoff_date:
                    continue

            metrics_files.append((json_file, data))
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Skipping invalid file {json_file}: {e}")

    return sorted(metrics_files, key=lambda x: x[1].get("timestamp", ""))


def aggregate_statistics(metrics_files: List[Tuple[Path, Dict]]) -> Dict:
    """Aggregate statistics across all metrics files.

    Returns:
        Dictionary with aggregated statistics
    """
    if not metrics_files:
        return {}

    # Group by test ID
    by_test_id = defaultdict(list)
    for filepath, data in metrics_files:
        test_id = data.get("test_id")
        stats = data.get("statistics", {})
        by_test_id[test_id].append(stats)

    # Calculate aggregates
    aggregates = {}
    for test_id, stats_list in by_test_id.items():
        if not stats_list:
            continue

        barrier_waits = [s.get("barrier_wait_ms", 0) for s in stats_list]
        request_spreads = [s.get("request_spread_ms", 0) for s in stats_list]
        avg_durations = [s.get("avg_duration_ms", 0) for s in stats_list]
        success_counts = [s.get("success_count", 0) for s in stats_list]

        aggregates[test_id] = {
            "count": len(stats_list),
            "barrier_wait_avg_ms": sum(barrier_waits) / len(barrier_waits),
            "barrier_wait_max_ms": max(barrier_waits),
            "request_spread_avg_ms": sum(request_spreads) / len(request_spreads),
            "request_spread_min_ms": min(request_spreads),
            "avg_duration_ms": sum(avg_durations) / len(avg_durations),
            "success_count_avg": sum(success_counts) / len(success_counts),
        }

    return aggregates


def check_thresholds(aggregates: Dict) -> List[str]:
    """Check aggregated metrics against alert thresholds.

    Returns:
        List of threshold violation messages (empty if all pass)
    """
    violations = []

    for test_id, stats in aggregates.items():
        # Check barrier wait threshold
        barrier_wait_sec = stats["barrier_wait_avg_ms"] / 1000
        if barrier_wait_sec > MAX_BARRIER_WAIT_THRESHOLD:
            violations.append(
                f"❌ {test_id}: Average barrier wait ({barrier_wait_sec:.2f}s) exceeds "
                f"threshold ({MAX_BARRIER_WAIT_THRESHOLD}s). "
                f"This may indicate CI resource constraints."
            )

        # Check request spread threshold
        if stats["request_spread_min_ms"] < MIN_REQUEST_SPREAD_THRESHOLD:
            violations.append(
                f"❌ {test_id}: Minimum request spread ({stats['request_spread_min_ms']:.2f}ms) "
                f"below threshold ({MIN_REQUEST_SPREAD_THRESHOLD}ms). "
                f"Race condition may be too deterministic."
            )

    return violations


def print_summary(aggregates: Dict, metrics_files: List[Tuple[Path, Dict]]):
    """Print summary report of metrics."""
    print("=" * 80)
    print("RACE CONDITION METRICS ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total metrics files analyzed: {len(metrics_files)}")
    print(f"Unique test cases: {len(aggregates)}")
    print()

    if not aggregates:
        print("No metrics data to analyze.")
        return

    # Print per-test statistics
    for test_id in sorted(aggregates.keys()):
        stats = aggregates[test_id]
        print(f"Test ID: {test_id}")
        print(f"  Executions:              {stats['count']}")
        print(f"  Barrier Wait (avg):      {stats['barrier_wait_avg_ms']:>8.2f} ms")
        print(f"  Barrier Wait (max):      {stats['barrier_wait_max_ms']:>8.2f} ms")
        print(f"  Request Spread (avg):    {stats['request_spread_avg_ms']:>8.2f} ms")
        print(f"  Request Spread (min):    {stats['request_spread_min_ms']:>8.2f} ms")
        print(f"  Request Duration (avg):  {stats['avg_duration_ms']:>8.2f} ms")
        print(f"  Success Count (avg):     {stats['success_count_avg']:>8.1f}")
        print()


def print_detailed(metrics_files: List[Tuple[Path, Dict]]):
    """Print detailed information for each metrics file."""
    print("\n" + "=" * 80)
    print("DETAILED METRICS")
    print("=" * 80)

    for filepath, data in metrics_files:
        print(f"\nFile: {filepath.name}")
        print(f"Test ID: {data.get('test_id')}")
        print(f"Timestamp: {data.get('timestamp')}")
        print(f"Thread Count: {data.get('thread_count')}")

        stats = data.get("statistics", {})
        print(f"  Barrier Wait:     {stats.get('barrier_wait_ms', 0):>8.2f} ms")
        print(f"  Request Spread:   {stats.get('request_spread_ms', 0):>8.2f} ms")
        print(f"  Min Duration:     {stats.get('min_duration_ms', 0):>8.2f} ms")
        print(f"  Avg Duration:     {stats.get('avg_duration_ms', 0):>8.2f} ms")
        print(f"  Max Duration:     {stats.get('max_duration_ms', 0):>8.2f} ms")
        print(f"  Success Count:    {stats.get('success_count', 0):>8}")
        print(f"  Failure Count:    {stats.get('failure_count', 0):>8}")


def main():
    """Main entry point."""
    args = parse_args()

    # Load metrics files
    metrics_files = load_metrics_files(
        args.directory, test_id_filter=args.test_id, since_date=args.since_date
    )

    if not metrics_files:
        print("No metrics files found matching filters.")
        return 0

    # Aggregate statistics
    aggregates = aggregate_statistics(metrics_files)

    # Print summary
    print_summary(aggregates, metrics_files)

    # Print detailed if requested
    if args.verbose:
        print_detailed(metrics_files)

    # Check thresholds
    violations = check_thresholds(aggregates)

    if violations:
        print("\n" + "=" * 80)
        print("⚠️  THRESHOLD VIOLATIONS DETECTED")
        print("=" * 80)
        for violation in violations:
            print(violation)
        print("\nRecommendations:")
        print("  - For high barrier wait times: Increase RACE_TEST_BARRIER_TIMEOUT")
        print("  - For low request spread: Check test implementation and timing")
        print("  - Consider running tests locally vs CI for comparison")
        print("=" * 80)
        return 1  # Exit code 1 = threshold violations (fail CI)
    else:
        print("\n✅ All metrics pass alert thresholds")
        return 0  # Exit code 0 = all pass (CI success)


if __name__ == "__main__":
    sys.exit(main())
