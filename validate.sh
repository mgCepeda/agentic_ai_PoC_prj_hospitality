#!/bin/bash

# Automated Validation Script for AI Agentic Hospitality Workshop
# This script validates the complete installation and functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Log file
LOG_FILE="validation_$(date +%Y%m%d_%H%M%S).log"

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "✅ $1" >> "$LOG_FILE"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    echo "❌ $1" >> "$LOG_FILE"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    echo "ℹ️  $1" >> "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "⚠️  $1" >> "$LOG_FILE"
}

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" >> "$LOG_FILE" 2>&1; then
        print_success "PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_error "FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Header
echo "=================================================================="
echo "     AI AGENTIC HOSPITALITY - AUTOMATED VALIDATION"
echo "=================================================================="
echo ""
echo "Log file: $LOG_FILE"
echo ""

# Phase 1: Pre-requisites
echo "📋 Phase 1: Checking Pre-requisites"
echo "────────────────────────────────────────────────────────────────"

run_test "Docker installed" "command -v docker"
run_test "Docker Compose installed" "command -v docker compose"
run_test "Curl installed" "command -v curl"
run_test "API Key configured" "[ ! -z \"\$AI_AGENTIC_API_KEY\" ]"

echo ""

# Phase 2: Container Status
echo "🐳 Phase 2: Checking Container Status"
echo "────────────────────────────────────────────────────────────────"

run_test "PostgreSQL container running" "docker ps | grep -q bookings-db"
run_test "ChromaDB container running" "docker ps | grep -q vectorstore-db"
run_test "API container running" "docker ps | grep -q ai_agents_hospitality-api"

echo ""

# Phase 3: Service Health
echo "🏥 Phase 3: Checking Service Health"
echo "────────────────────────────────────────────────────────────────"

run_test "PostgreSQL connection" "docker exec bookings-db pg_isready -U postgres -d bookings_db"
run_test "ChromaDB API responding" "curl -sf http://localhost:8000/api/v1/heartbeat > /dev/null"
run_test "AI Agents API responding" "curl -sf http://localhost:8001 > /dev/null"

echo ""

# Phase 4: Database Content
echo "🗄️  Phase 4: Checking Database Content"
echo "────────────────────────────────────────────────────────────────"

run_test "Bookings table exists" "docker exec bookings-db psql -U postgres -d bookings_db -c '\dt bookings' | grep -q bookings"
run_test "Bookings data loaded" "docker exec bookings-db psql -U postgres -d bookings_db -t -c 'SELECT COUNT(*) FROM bookings' | grep -qv '^ *0'"

echo ""

# Phase 5: API Functionality Tests
echo "🧪 Phase 5: Testing API Functionality"
echo "────────────────────────────────────────────────────────────────"

# Create temporary test script
cat > /tmp/test_api.py << 'EOF'
import asyncio
import websockets
import json
import sys

async def test_query(query):
    try:
        async with websockets.connect('ws://localhost:8001/ws') as websocket:
            await websocket.send(query)
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            return len(response) > 50  # Response should be substantial
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

async def main():
    test_passed = await test_query("List all hotels")
    sys.exit(0 if test_passed else 1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

if command -v python3 &> /dev/null; then
    run_test "WebSocket query test" "python3 /tmp/test_api.py"
else
    print_warning "Python3 not found, skipping WebSocket test"
fi

# Cleanup
rm -f /tmp/test_api.py

echo ""

# Phase 6: Performance Checks
echo "⚡ Phase 6: Performance Checks"
echo "────────────────────────────────────────────────────────────────"

# Check memory usage
MEMORY_USAGE=$(docker stats --no-stream --format "{{.MemUsage}}" | awk '{print $1}' | head -1 | sed 's/GiB//')
if (( $(echo "$MEMORY_USAGE < 3" | bc -l) )); then
    print_success "Memory usage acceptable: ${MEMORY_USAGE}GB"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_warning "Memory usage high: ${MEMORY_USAGE}GB"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Check response time
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8001)
if (( $(echo "$RESPONSE_TIME < 5" | bc -l) )); then
    print_success "API response time acceptable: ${RESPONSE_TIME}s"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_warning "API response time slow: ${RESPONSE_TIME}s"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# Results Summary
echo "=================================================================="
echo "                    VALIDATION SUMMARY"
echo "=================================================================="
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

# Calculate percentage
PASS_RATE=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
echo "Pass Rate: ${PASS_RATE}%"
echo ""

# Final verdict
if [ "$FAILED_TESTS" -eq 0 ]; then
    print_success "ALL TESTS PASSED! ✨"
    echo ""
    echo "🎓 The workshop is fully validated and ready for use!"
    exit 0
elif (( $(echo "$PASS_RATE >= 80" | bc -l) )); then
    print_warning "MOSTLY PASSED (${PASS_RATE}%)"
    echo ""
    echo "⚠️  Some tests failed but the workshop is mostly functional."
    echo "   Check the log file for details: $LOG_FILE"
    exit 1
else
    print_error "VALIDATION FAILED (${PASS_RATE}%)"
    echo ""
    echo "❌ Too many tests failed. Please review the setup."
    echo "   Check the log file for details: $LOG_FILE"
    exit 2
fi
