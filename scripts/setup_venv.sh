#!/bin/bash
#
# Virtual Environment Setup Script for Mergington High School Activities API
#
# This script:
# 1. Creates a Python virtual environment
# 2. Installs all project dependencies
# 3. Installs Playwright browsers (Chromium, Firefox, WebKit)
#
# Usage: ./scripts/setup_venv.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Mergington High School API - Virtual Environment Setup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo -e "${RED}ERROR: Python 3.10 or higher required. Found: $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $python_version detected${NC}"
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists at ./venv${NC}"
    echo -e "${YELLOW}Do you want to recreate it? (y/N): ${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${YELLOW}Removing existing venv...${NC}"
        rm -rf venv
    else
        echo -e "${BLUE}Using existing venv...${NC}"
    fi
fi

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}ERROR: Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment activated: $VIRTUAL_ENV${NC}"
echo ""

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install requirements
echo -e "${YELLOW}Installing Python dependencies from requirements.txt...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Install Playwright browsers
echo -e "${YELLOW}Installing Playwright browsers (Chromium, Firefox, WebKit)...${NC}"
echo -e "${BLUE}This may take several minutes and download ~500MB...${NC}"
playwright install chromium firefox webkit
echo -e "${GREEN}✓ Playwright browsers installed${NC}"
echo ""

# Install system dependencies for browsers (if needed)
echo -e "${YELLOW}Installing system dependencies for browsers...${NC}"
playwright install-deps chromium firefox webkit 2>/dev/null || echo -e "${YELLOW}⚠ Some system dependencies may require sudo. Run 'sudo playwright install-deps' if tests fail.${NC}"
echo ""

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
python -c "import playwright; print('Playwright version:', playwright.__version__)" || {
    echo -e "${RED}ERROR: Playwright import failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Installation verified${NC}"
echo ""

# Success message
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}To activate the virtual environment manually:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo -e "${BLUE}To run the application:${NC}"
echo -e "  ${YELLOW}cd src && uvicorn app:app --reload${NC}"
echo ""
echo -e "${BLUE}To run all tests:${NC}"
echo -e "  ${YELLOW}pytest${NC}"
echo ""
echo -e "${BLUE}To run Playwright UI tests:${NC}"
echo -e "  ${YELLOW}pytest tests/playwright/ --headed${NC}"
echo -e "  ${YELLOW}pytest tests/playwright/ --browser chromium${NC}"
echo -e "  ${YELLOW}./scripts/run_ui_tests.sh${NC}"
echo ""
echo -e "${BLUE}To deactivate the virtual environment:${NC}"
echo -e "  ${YELLOW}deactivate${NC}"
echo ""
