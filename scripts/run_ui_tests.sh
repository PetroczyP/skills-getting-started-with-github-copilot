#!/bin/bash
#
# Run UI tests with Playwright
#
# Usage:
#   ./scripts/run_ui_tests.sh                    # Run all UI tests (all browsers, headless)
#   ./scripts/run_ui_tests.sh --headed           # Run with visible browser
#   ./scripts/run_ui_tests.sh --browser chromium # Run on specific browser only
#   ./scripts/run_ui_tests.sh --parallel         # Run tests in parallel
#   ./scripts/run_ui_tests.sh --debug            # Run with debug mode (headed + slow)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
BROWSER="all"
HEADED=""
SLOWMO=""
PARALLEL=""
DEBUG=""
PYTEST_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --headed)
            HEADED="--headed"
            shift
            ;;
        --slowmo)
            SLOWMO="--slowmo 500"
            shift
            ;;
        --parallel)
            PARALLEL="-n auto"
            shift
            ;;
        --debug)
            DEBUG="yes"
            HEADED="--headed"
            SLOWMO="--slowmo 1000"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --browser <name>  Run on specific browser (chromium, firefox, webkit, all)"
            echo "  --headed          Run with visible browser window"
            echo "  --slowmo          Slow down operations (500ms delay)"
            echo "  --parallel        Run tests in parallel using pytest-xdist"
            echo "  --debug           Debug mode (headed + slowmo 1000ms)"
            echo "  --help            Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # All browsers, headless"
            echo "  $0 --headed                  # All browsers, visible"
            echo "  $0 --browser chromium        # Chromium only, headless"
            echo "  $0 --browser firefox --headed # Firefox only, visible"
            echo "  $0 --parallel                # Parallel execution"
            echo "  $0 --debug                   # Debug mode (slow, visible)"
            exit 0
            ;;
        *)
            PYTEST_ARGS="$PYTEST_ARGS $1"
            shift
            ;;
    esac
done

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  Mergington High School UI Tests${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# Check if virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}❌ ERROR: Virtual environment not activated${NC}"
    echo ""
    echo "Activate virtual environment first:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Or run setup script:"
    echo "  ./scripts/setup_venv.sh"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment: $VIRTUAL_ENV${NC}"

# Verify Playwright installation
if ! python -c "import playwright" 2>/dev/null; then
    echo -e "${RED}❌ ERROR: Playwright not installed${NC}"
    echo ""
    echo "Install Playwright:"
    echo "  pip install playwright"
    echo "  playwright install chromium firefox webkit"
    exit 1
fi

echo -e "${GREEN}✓ Playwright installed${NC}"

# Check if server is running
if ! curl -s http://localhost:8000/activities > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  WARNING: Server not running${NC}"
    echo ""
    echo "Server will be started automatically by tests."
    echo "Or start manually:"
    echo "  cd src && uvicorn app:app --reload"
    echo ""
fi

# Build pytest command
PYTEST_CMD="pytest tests/playwright/"

# Add browser selection
if [[ "$BROWSER" == "all" ]]; then
    PYTEST_CMD="$PYTEST_CMD --browser chromium --browser firefox --browser webkit"
else
    PYTEST_CMD="$PYTEST_CMD --browser $BROWSER"
fi

# Add headed/slowmo flags
if [[ ! -z "$HEADED" ]]; then
    PYTEST_CMD="$PYTEST_CMD $HEADED"
fi

if [[ ! -z "$SLOWMO" ]]; then
    PYTEST_CMD="$PYTEST_CMD $SLOWMO"
fi

# Add parallel execution
if [[ ! -z "$PARALLEL" ]]; then
    PYTEST_CMD="$PYTEST_CMD $PARALLEL"
fi

# Add verbose output
PYTEST_CMD="$PYTEST_CMD -v"

# Add any extra arguments
if [[ ! -z "$PYTEST_ARGS" ]]; then
    PYTEST_CMD="$PYTEST_CMD $PYTEST_ARGS"
fi

echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Browser: $BROWSER"
echo "  Mode: $([ -z "$HEADED" ] && echo "headless" || echo "headed")"
echo "  Slowmo: $([ -z "$SLOWMO" ] && echo "no" || echo "yes (1000ms)")"
echo "  Parallel: $([ -z "$PARALLEL" ] && echo "no" || echo "yes")"
echo "  Debug: $([ -z "$DEBUG" ] && echo "no" || echo "yes")"
echo ""
echo -e "${BLUE}Command:${NC}"
echo "  $PYTEST_CMD"
echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# Run tests
if $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ All UI tests passed!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo -e "${RED}❌ UI tests failed${NC}"
    echo -e "${RED}═══════════════════════════════════════${NC}"
    exit 1
fi
