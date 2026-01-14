#!/bin/bash

# ============================================================================
# PRE-START SCRIPT: Prepare environment before starting Docker services
# ============================================================================

# Color definitions
COLOR_RED=$'\033[31m'
COLOR_GREEN=$'\033[32m'
COLOR_YELLOW=$'\033[33m'
COLOR_RESET=$'\033[0m'

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║        🔧  PRE-START ENVIRONMENT PREPARATION  🔧              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# STEP 1: Stop local PostgreSQL
# ============================================================================
echo "${COLOR_YELLOW}🔍 Step 1: Checking for local PostgreSQL service...${COLOR_RESET}"
if sudo lsof -i :5432 &>/dev/null; then
  echo "${COLOR_YELLOW}⚠️  Local PostgreSQL is running on port 5432${COLOR_RESET}"
  echo "   Stopping local PostgreSQL service..."
  sudo systemctl stop postgresql
  sleep 2
  
  if sudo lsof -i :5432 &>/dev/null; then
    echo "${COLOR_RED}❌ Failed to stop PostgreSQL on port 5432${COLOR_RESET}"
    echo "   Please stop it manually:"
    echo "   ${COLOR_YELLOW}sudo systemctl stop postgresql${COLOR_RESET}"
    exit 1
  else
    echo "${COLOR_GREEN}✅ Local PostgreSQL stopped successfully${COLOR_RESET}"
  fi
else
  echo "${COLOR_GREEN}✅ Port 5432 is available (no local PostgreSQL running)${COLOR_RESET}"
fi
echo ""

# ============================================================================
# STEP 2: Activate Python virtual environment
# ============================================================================
echo "${COLOR_YELLOW}🐍 Step 2: Setting up Python virtual environment...${COLOR_RESET}"
VENV_PATH="${BASE_DIR}/.venv"

if [ -d "${VENV_PATH}" ]; then
  echo "   Virtual environment found at ${VENV_PATH}"
  source "${VENV_PATH}/bin/activate"
  echo "${COLOR_GREEN}✅ Virtual environment activated${COLOR_RESET}"
  echo "   Python: $(which python)"
  echo "   Version: $(python --version)"
else
  echo "${COLOR_YELLOW}⚠️  Virtual environment not found${COLOR_RESET}"
  echo "   Creating virtual environment at ${VENV_PATH}..."
  python3 -m venv "${VENV_PATH}"
  
  if [ $? -eq 0 ]; then
    source "${VENV_PATH}/bin/activate"
    echo "${COLOR_GREEN}✅ Virtual environment created and activated${COLOR_RESET}"
    echo "   Python: $(which python)"
  else
    echo "${COLOR_RED}❌ Failed to create virtual environment${COLOR_RESET}"
    exit 1
  fi
fi
echo ""

# ============================================================================
# STEP 3: Install/update dependencies (optional)
# ============================================================================
echo "${COLOR_YELLOW}📦 Step 3: Checking Python dependencies...${COLOR_RESET}"
if [ -f "${BASE_DIR}/requirements.txt" ]; then
  echo "   Found requirements.txt"
  read -p "   Install/update dependencies? (y/N): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install -r "${BASE_DIR}/requirements.txt"
    echo "${COLOR_GREEN}✅ Dependencies installed${COLOR_RESET}"
  else
    echo "   Skipped dependency installation"
  fi
else
  echo "   No requirements.txt found - skipping"
fi
echo ""

# ============================================================================
# STEP 4: Verify environment variables
# ============================================================================
echo "${COLOR_YELLOW}🔑 Step 4: Checking environment variables...${COLOR_RESET}"

if [ -z "$AI_AGENTIC_API_KEY" ]; then
  echo "${COLOR_RED}❌ AI_AGENTIC_API_KEY is not set${COLOR_RESET}"
  echo "   Please set your API key:"
  echo "   ${COLOR_YELLOW}export AI_AGENTIC_API_KEY=\"your-api-key\"${COLOR_RESET}"
  echo ""
  echo "   Or add it to your ~/.bashrc or ~/.zshrc:"
  echo "   ${COLOR_YELLOW}echo 'export AI_AGENTIC_API_KEY=\"your-api-key\"' >> ~/.bashrc${COLOR_RESET}"
  exit 1
else
  # Mask the API key for security
  masked_key="${AI_AGENTIC_API_KEY:0:8}...${AI_AGENTIC_API_KEY: -4}"
  echo "${COLOR_GREEN}✅ AI_AGENTIC_API_KEY is set${COLOR_RESET}"
  echo "   Key: ${masked_key}"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                  ✅  ENVIRONMENT READY  ✅                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "You can now start the Docker services:"
echo "${COLOR_GREEN}  ./start-app.sh --logs${COLOR_RESET}"
echo ""
echo "Or run the validation script:"
echo "${COLOR_GREEN}  ./validate.sh${COLOR_RESET}"
echo ""
