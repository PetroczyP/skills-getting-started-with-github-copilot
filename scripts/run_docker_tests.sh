#!/bin/bash
# Run tests in Docker container
# Purpose: Cross-platform testing in consistent Linux environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="api-tests"
METRICS_DIR="./test_metrics_docker"
BARRIER_TIMEOUT=60
ENABLE_METRICS=true
TEST_MARKER="concurrency"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --marker)
      TEST_MARKER="$2"
      shift 2
      ;;
    --timeout)
      BARRIER_TIMEOUT="$2"
      shift 2
      ;;
    --no-metrics)
      ENABLE_METRICS=false
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --marker MARKER      Pytest marker to run (default: concurrency)"
      echo "  --timeout SECONDS    Barrier timeout in seconds (default: 60)"
      echo "  --no-metrics         Disable metrics collection"
      echo "  --help               Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0                                    # Run race condition tests"
      echo "  $0 --marker functional                # Run functional tests"
      echo "  $0 --timeout 120 --no-metrics         # Custom timeout, no metrics"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Docker Test Runner${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Step 1: Build test image
echo -e "${CYAN}Step 1: Building test image...${NC}"
docker build -f Dockerfile.test -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
  echo -e "${RED}❌ Docker build failed${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Image built successfully${NC}"
echo ""

# Step 2: Run tests
echo -e "${CYAN}Step 2: Running tests in Docker...${NC}"
echo -e "${YELLOW}Marker: ${TEST_MARKER}${NC}"
echo -e "${YELLOW}Barrier Timeout: ${BARRIER_TIMEOUT}s${NC}"
echo -e "${YELLOW}Metrics Enabled: ${ENABLE_METRICS}${NC}"
echo ""

docker run --rm \
  -e RACE_TEST_BARRIER_TIMEOUT=$BARRIER_TIMEOUT \
  -e RACE_TEST_METRICS=$ENABLE_METRICS \
  $IMAGE_NAME pytest -m $TEST_MARKER -v

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
  echo -e "${RED}❌ Tests failed with exit code $TEST_EXIT_CODE${NC}"
  exit $TEST_EXIT_CODE
fi

echo -e "${GREEN}✅ All tests passed${NC}"
echo ""

# Step 3: Extract metrics (if enabled)
if [ "$ENABLE_METRICS" = true ]; then
  echo -e "${CYAN}Step 3: Extracting metrics...${NC}"
  
  # Create temporary container
  docker create --name temp-test-metrics $IMAGE_NAME > /dev/null
  
  # Copy metrics out
  docker cp temp-test-metrics:/app/test_metrics $METRICS_DIR 2>/dev/null || true
  
  # Remove temporary container
  docker rm temp-test-metrics > /dev/null
  
  if [ -d "$METRICS_DIR/race_conditions" ]; then
    METRICS_COUNT=$(find "$METRICS_DIR/race_conditions" -name "*.json" 2>/dev/null | wc -l)
    if [ $METRICS_COUNT -gt 0 ]; then
      echo -e "${GREEN}✅ Extracted $METRICS_COUNT metrics file(s) to $METRICS_DIR${NC}"
      echo ""
      
      # Step 4: Analyze metrics
      echo -e "${CYAN}Step 4: Analyzing metrics...${NC}"
      python scripts/analyze_race_metrics.py --metrics-dir "$METRICS_DIR/race_conditions" --verbose
      
      ANALYZE_EXIT_CODE=$?
      if [ $ANALYZE_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ All metrics within thresholds${NC}"
      else
        echo -e "${YELLOW}⚠️  Some metrics outside thresholds (warnings only)${NC}"
      fi
    else
      echo -e "${YELLOW}⚠️  No metrics files found${NC}"
    fi
  else
    echo -e "${YELLOW}⚠️  No metrics directory found (tests may not have generated metrics)${NC}"
  fi
else
  echo -e "${YELLOW}Step 3: Skipped (metrics disabled)${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Docker tests complete!${NC}"
echo -e "${GREEN}========================================${NC}"
