# Docker Testing Guide

**Last Updated:** December 28, 2025  
**Version:** 1.0  
**Audience:** Developers running cross-platform tests

---

## Table of Contents

1. [Overview](#overview)
2. [Why Docker for Testing](#why-docker-for-testing)
3. [Quick Start](#quick-start)
4. [Docker Configuration](#docker-configuration)
5. [Running Tests in Docker](#running-tests-in-docker)
6. [Comparing Results](#comparing-results)
7. [CI/CD Integration](#cicd-integration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Docker testing allows running tests in a consistent Linux environment, regardless of your local development platform (Windows, macOS, Linux). This is especially important for race condition tests where thread scheduling behavior differs significantly between operating systems.

**Test Docker Image:** `api-tests`  
**Base Image:** `python:3.13-slim`  
**Test Command:** `pytest -m concurrency -v`

---

## Why Docker for Testing

### Platform Differences

| Aspect | Windows | Linux (Docker/CI) | Impact |
|--------|---------|-------------------|--------|
| **Thread Scheduling** | Deterministic | Non-deterministic | Windows shows <5ms spread, Linux 5-50ms |
| **Barrier Timing** | Fast (30-70ms) | Slower (100-300ms) | Windows tests pass with 30s timeout, CI needs 60s |
| **Request Concurrency** | Predictable order | Variable order | Windows masks timing bugs |
| **Resource Contention** | Low (single dev) | High (shared runners) | CI tests more realistic |

### When to Use Docker

✅ **Use Docker when:**
- Validating race condition tests before CI
- Investigating CI-specific failures
- Testing on Windows/macOS (local environment != CI)
- Verifying Linux-specific behavior

❌ **Don't need Docker when:**
- Running quick functional tests
- Debugging application logic (not concurrency)
- Developing on Linux workstation matching CI

---

## Quick Start

### Build Test Image

```bash
# From project root
docker build -f Dockerfile.test -t api-tests .

# Output:
# [+] Building 45.2s (12/12) FINISHED
# => [1/7] FROM python:3.13-slim
# => [2/7] WORKDIR /app
# => [3/7] COPY requirements.txt .
# => [4/7] RUN pip install --no-cache-dir -r requirements.txt
# => [5/7] COPY src/ ./src/
# => [6/7] COPY tests/ ./tests/
# => [7/7] COPY scripts/ ./scripts/
# => exporting to image
```

### Run All Tests

```bash
# Run all tests
docker run --rm api-tests

# Run specific test markers
docker run --rm api-tests pytest -m concurrency -v

# Run with environment variables
docker run --rm -e RACE_TEST_BARRIER_TIMEOUT=120 api-tests pytest -m concurrency

# Run specific test
docker run --rm api-tests pytest tests/test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race -v
```

### Extract Metrics

```bash
# Run tests and copy metrics out
docker run --name test-run api-tests pytest -m concurrency
docker cp test-run:/app/test_metrics ./test_metrics_docker
docker rm test-run

# Analyze extracted metrics
python scripts/analyze_race_metrics.py --metrics-dir ./test_metrics_docker/race_conditions --verbose
```

---

## Docker Configuration

### Dockerfile.test

**Purpose:** Creates isolated test environment with all dependencies

```dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY pytest.ini .

# Set environment variables
ENV PYTHONPATH=/app
ENV RACE_TEST_BARRIER_TIMEOUT=60
ENV RACE_TEST_METRICS=true

# Run tests by default
CMD ["pytest", "-v"]
```

### .dockerignore

**Purpose:** Exclude unnecessary files from build context (faster builds)

```
# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/

# Test outputs
.pytest_cache/
htmlcov/
.coverage
test_metrics/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore

# Documentation (not needed in test image)
docs/
*.md
LICENSE

# Local configuration
.env
.env.local
```

---

## Running Tests in Docker

### Basic Commands

```bash
# Run all tests
docker run --rm api-tests

# Run specific markers
docker run --rm api-tests pytest -m infrastructure
docker run --rm api-tests pytest -m functional
docker run --rm api-tests pytest -m concurrency

# Run with verbose output
docker run --rm api-tests pytest -v -s

# Run specific test file
docker run --rm api-tests pytest tests/test_app.py -v
```

### Advanced Options

```bash
# Interactive shell for debugging
docker run --rm -it api-tests /bin/bash
# Inside container:
# pytest tests/test_app.py::TestRaceConditions::test_concurrent_signup_single_spot_race -v -s

# Mount local code for development
docker run --rm -v $(pwd)/src:/app/src -v $(pwd)/tests:/app/tests api-tests pytest -m concurrency

# Override environment variables
docker run --rm \
  -e RACE_TEST_BARRIER_TIMEOUT=120 \
  -e RACE_TEST_METRICS=true \
  api-tests pytest -m concurrency -v

# Limit container resources (simulate CI constraints)
docker run --rm \
  --cpus=1.0 \
  --memory=512m \
  api-tests pytest -m concurrency
```

### Automated Script

**scripts/run_docker_tests.sh:**

```bash
#!/bin/bash
set -e

# Build test image
echo "Building test image..."
docker build -f Dockerfile.test -t api-tests .

# Run tests
echo "Running tests in Docker..."
docker run --rm \
  -e RACE_TEST_BARRIER_TIMEOUT=60 \
  -e RACE_TEST_METRICS=true \
  api-tests pytest -m concurrency -v

# Extract and analyze metrics
echo "Extracting metrics..."
docker create --name temp-test api-tests
docker cp temp-test:/app/test_metrics ./test_metrics_docker
docker rm temp-test

echo "Analyzing metrics..."
python scripts/analyze_race_metrics.py --metrics-dir ./test_metrics_docker/race_conditions --verbose

echo "✅ Docker tests complete!"
```

**Usage:**
```bash
# Make executable
chmod +x scripts/run_docker_tests.sh

# Run
./scripts/run_docker_tests.sh
```

**Windows PowerShell equivalent:**

```powershell
# scripts/run_docker_tests.ps1

Write-Host "Building test image..." -ForegroundColor Cyan
docker build -f Dockerfile.test -t api-tests .

Write-Host "Running tests in Docker..." -ForegroundColor Cyan
docker run --rm `
  -e RACE_TEST_BARRIER_TIMEOUT=60 `
  -e RACE_TEST_METRICS=true `
  api-tests pytest -m concurrency -v

Write-Host "Extracting metrics..." -ForegroundColor Cyan
docker create --name temp-test api-tests
docker cp temp-test:/app/test_metrics ./test_metrics_docker
docker rm temp-test

Write-Host "Analyzing metrics..." -ForegroundColor Cyan
python scripts/analyze_race_metrics.py --metrics-dir ./test_metrics_docker/race_conditions --verbose

Write-Host "✅ Docker tests complete!" -ForegroundColor Green
```

---

## Comparing Results

### Local vs Docker Metrics

**Typical Windows Local:**
```json
{
  "test_id": "TC-RACE-001",
  "barrier_wait": {"duration_ms": 49},
  "statistics": {
    "request_spread_ms": 3.66,
    "avg_duration_ms": 11.2
  },
  "thresholds": {
    "barrier_wait_exceeded": false,
    "request_spread_too_low": true  // ⚠️ Expected on Windows
  }
}
```

**Typical Linux Docker:**
```json
{
  "test_id": "TC-RACE-001",
  "barrier_wait": {"duration_ms": 127},
  "statistics": {
    "request_spread_ms": 23.45,  // ✅ More realistic
    "avg_duration_ms": 15.8
  },
  "thresholds": {
    "barrier_wait_exceeded": false,
    "request_spread_too_low": false  // ✅ Pass
  }
}
```

### Side-by-Side Comparison

```bash
# Run locally
RACE_TEST_METRICS=true pytest -m concurrency -v
mv test_metrics test_metrics_local

# Run in Docker
docker run --rm -e RACE_TEST_METRICS=true api-tests pytest -m concurrency -v
docker cp <container>:/app/test_metrics ./test_metrics_docker

# Compare
python scripts/analyze_race_metrics.py --metrics-dir ./test_metrics_local/race_conditions
python scripts/analyze_race_metrics.py --metrics-dir ./test_metrics_docker/race_conditions
```

### Expected Differences

| Metric | Windows Local | Linux Docker | Explanation |
|--------|---------------|--------------|-------------|
| **Barrier Wait** | 30-70ms | 100-300ms | Linux thread creation slower |
| **Request Spread** | 1-5ms | 5-50ms | Linux scheduling less deterministic |
| **Test Duration** | 0.2-0.5s | 0.5-2s | Docker overhead + slower threads |
| **Threshold Warnings** | Common | Rare | Windows too predictable |

---

## CI/CD Integration

### GitHub Actions with Docker

```yaml
name: Docker Tests

on: [push, pull_request]

jobs:
  docker-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build test image
        run: docker build -f Dockerfile.test -t api-tests .
      
      - name: Run tests
        run: |
          docker run --rm \
            -e RACE_TEST_BARRIER_TIMEOUT=120 \
            -e RACE_TEST_METRICS=true \
            api-tests pytest -m concurrency -v
      
      - name: Extract metrics
        if: always()
        run: |
          docker create --name test-metrics api-tests
          docker cp test-metrics:/app/test_metrics ./test_metrics_ci
          docker rm test-metrics
      
      - name: Analyze metrics
        if: always()
        run: |
          python scripts/analyze_race_metrics.py \
            --metrics-dir ./test_metrics_ci/race_conditions \
            --verbose
      
      - name: Upload metrics
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: race-metrics-ci
          path: test_metrics_ci/race_conditions/*.json
```

### Multi-Platform Testing

```yaml
jobs:
  test-matrix:
    strategy:
      matrix:
        platform: [ubuntu-latest, windows-latest, macos-latest]
    
    runs-on: ${{ matrix.platform }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and run tests
        run: |
          docker build -f Dockerfile.test -t api-tests .
          docker run --rm api-tests pytest -m concurrency -v
      
      - name: Upload metrics
        uses: actions/upload-artifact@v3
        with:
          name: metrics-${{ matrix.platform }}
          path: test_metrics/race_conditions/*.json
```

---

## Troubleshooting

### Build Failures

**Error:** `failed to solve: python:3.13-slim: not found`

**Solution:** Check Docker Hub for correct Python version tag
```bash
docker pull python:3.13-slim
```

---

**Error:** `COPY failed: stat requirements.txt: no such file or directory`

**Solution:** Run from project root directory
```bash
cd /path/to/project
docker build -f Dockerfile.test -t api-tests .
```

---

### Runtime Failures

**Error:** `ModuleNotFoundError: No module named 'pytest'`

**Solution:** Rebuild image (dependencies not installed)
```bash
docker build --no-cache -f Dockerfile.test -t api-tests .
```

---

**Error:** `BrokenBarrierError: barrier timeout exceeded`

**Solution:** Increase timeout for Docker environment
```bash
docker run --rm -e RACE_TEST_BARRIER_TIMEOUT=120 api-tests pytest -m concurrency
```

---

### Permission Issues

**Error:** `docker: permission denied while trying to connect to Docker daemon`

**Solution (Linux):**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**Solution (Windows/Mac):**
- Ensure Docker Desktop is running
- Check Docker Desktop settings for permissions

---

### Performance Issues

**Symptom:** Tests run much slower in Docker than locally

**Causes:**
- Docker Desktop resource limits too low
- File system overhead (especially on Windows)
- Image not optimized

**Solutions:**
```bash
# Increase Docker resources
# Docker Desktop → Settings → Resources
# - CPUs: 4+
# - Memory: 4GB+

# Use multi-stage build for smaller image
# (See Dockerfile.test optimization below)

# Run without metrics collection
docker run --rm -e RACE_TEST_METRICS=false api-tests pytest -m concurrency
```

---

## Optimization Tips

### Faster Builds

```dockerfile
# Multi-stage build
FROM python:3.13-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY pytest.ini .
ENV PYTHONPATH=/app
CMD ["pytest", "-v"]
```

### Caching Dependencies

```bash
# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -f Dockerfile.test -t api-tests .
```

### Smaller Image

```dockerfile
# Use alpine for smaller size (if compatible)
FROM python:3.13-alpine
# Note: May need additional build dependencies
RUN apk add --no-cache gcc musl-dev
```

---

## Best Practices

✅ **DO:**
- Test in Docker before pushing to CI
- Use same Python version as production
- Set appropriate resource limits
- Compare local vs Docker metrics
- Use `.dockerignore` to speed up builds

❌ **DON'T:**
- Run resource-intensive tests with default limits
- Ignore Docker-specific timing differences
- Skip `.dockerignore` (slower builds)
- Use `latest` tag (not reproducible)
- Mount entire project directory (slow on Windows)

---

## Additional Resources

- [Docker Build Documentation](https://docs.docker.com/engine/reference/builder/)
- [Docker Run Reference](https://docs.docker.com/engine/reference/run/)
- [pytest in Docker](https://docs.pytest.org/en/stable/)
- [RACE_CONDITION_TESTING.md](RACE_CONDITION_TESTING.md) - Race test guide

---

**Questions or Issues?** Update this guide or open an issue!

**Last Updated:** December 28, 2025
