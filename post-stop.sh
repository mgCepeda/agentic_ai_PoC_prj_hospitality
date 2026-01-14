#!/bin/bash

# ============================================================================
# POST-STOP SCRIPT: Restore environment after stopping Docker services
# ============================================================================

# Color definitions
COLOR_RED=$'\033[31m'
COLOR_GREEN=$'\033[32m'
COLOR_YELLOW=$'\033[33m'
COLOR_RESET=$'\033[0m'

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║        🔄  POST-STOP ENVIRONMENT RESTORATION  🔄              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# STEP 1: Restart local PostgreSQL service
# ============================================================================
echo "${COLOR_YELLOW}🔄 Step 1: Restarting local PostgreSQL service...${COLOR_RESET}"

if sudo systemctl start postgresql 2>/dev/null; then
  sleep 2
  
  if sudo lsof -i :5432 &>/dev/null; then
    echo "${COLOR_GREEN}✅ Local PostgreSQL restarted successfully${COLOR_RESET}"
    echo "   Service is listening on port 5432"
    
    # Show PostgreSQL status
    systemctl status postgresql --no-pager -l 2>/dev/null | head -n 5
  else
    echo "${COLOR_YELLOW}⚠️  PostgreSQL service started but not listening on port 5432${COLOR_RESET}"
    echo "   You may need to check the configuration"
  fi
else
  echo "${COLOR_YELLOW}⚠️  Could not restart PostgreSQL service${COLOR_RESET}"
  echo "   (may not be installed as systemd service)"
  echo ""
  echo "   If you need PostgreSQL, start it manually:"
  echo "   ${COLOR_YELLOW}sudo systemctl start postgresql${COLOR_RESET}"
fi
echo ""

# ============================================================================
# STEP 2: Deactivate virtual environment
# ============================================================================
echo "${COLOR_YELLOW}🐍 Step 2: Deactivating virtual environment...${COLOR_RESET}"

if [ -n "$VIRTUAL_ENV" ]; then
  echo "   Current virtual environment: $VIRTUAL_ENV"
  deactivate 2>/dev/null || true
  echo "${COLOR_GREEN}✅ Virtual environment deactivated${COLOR_RESET}"
else
  echo "   No active virtual environment detected"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              ✅  ENVIRONMENT RESTORED  ✅                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  ${COLOR_GREEN}✅${COLOR_RESET} Docker services stopped"
echo "  ${COLOR_GREEN}✅${COLOR_RESET} Local PostgreSQL restored"
echo "  ${COLOR_GREEN}✅${COLOR_RESET} Virtual environment deactivated"
echo ""
echo "👋 Goodbye!"
echo ""
