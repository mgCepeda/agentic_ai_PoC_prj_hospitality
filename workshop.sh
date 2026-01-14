#!/bin/bash

# Workshop script - Simple wrapper to manage the hospitality workshop
# According to WORKSHOP.md, only databases should run in Docker
# The AI Agents API runs locally with: python main.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$SCRIPT_DIR/ai_agents_hospitality-api"
COMPOSE_DIR="$SCRIPT_DIR/prj-docker-compose"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to show help
show_help() {
    echo "Usage: ./workshop.sh {start|stop|status|restart|logs}"
    echo ""
    echo "Commands:"
    echo "  start    - Start PostgreSQL and ChromaDB containers, then run API locally"
    echo "  stop     - Stop API and all database containers"
    echo "  status   - Show status of all services"
    echo "  restart  - Restart all services"
    echo "  logs     - Show logs from database containers"
    echo ""
    exit 0
}

# Function to check if API is running
check_api_running() {
    pgrep -f "uvicorn main:app" > /dev/null 2>&1
    return $?
}

# Function to start services
start_services() {
    echo -e "${GREEN}🚀 Starting Hospitality Workshop Services...${NC}"
    echo ""
    
    # 0. Run pre-start checks (stop local PostgreSQL, verify API key, etc.)
    if [ -f "$SCRIPT_DIR/pre-start.sh" ]; then
        echo -e "${YELLOW}🔧 Running pre-start environment checks...${NC}"
        bash "$SCRIPT_DIR/pre-start.sh"
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Pre-start checks failed${NC}"
            exit 1
        fi
        echo ""
    fi
    
    # 1. Start database containers
    echo -e "${YELLOW}📦 Starting database containers...${NC}"
    cd "$COMPOSE_DIR" || exit 1
    
    sudo -E docker-compose up -d
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to start database containers${NC}"
        exit 1
    fi
    
    # Wait for databases to be ready
    echo ""
    echo -e "${YELLOW}⏳ Waiting for databases to be ready...${NC}"
    sleep 5
    
    # Check PostgreSQL
    echo -n "Checking PostgreSQL... "
    for i in {1..10}; do
        if sudo docker exec bookings-db pg_isready -U postgres > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${RED}✗ (timeout)${NC}"
            echo -e "${YELLOW}PostgreSQL may still be starting. Check with: docker logs bookings-db${NC}"
        fi
        sleep 2
    done
    
    # Check ChromaDB
    echo -n "Checking ChromaDB... "
    for i in {1..10}; do
        if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${YELLOW}⚠ (not responding but may be OK)${NC}"
        fi
        sleep 2
    done
    
    # 2. Check if virtual environment exists
    if [ ! -d "$SCRIPT_DIR/.venv" ]; then
        echo ""
        echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
        cd "$SCRIPT_DIR"
        python3 -m venv .venv
    fi
    
    # 3. Activate venv and install dependencies
    echo ""
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    cd "$API_DIR"
    source "$SCRIPT_DIR/.venv/bin/activate"
    pip install -q -r requirements.txt
    
    # 4. Start API locally
    echo ""
    echo -e "${YELLOW}🌐 Starting AI Agents API locally...${NC}"
    
    # Check if already running
    if check_api_running; then
        echo -e "${YELLOW}⚠️  API is already running${NC}"
        echo "Use './workshop.sh stop' first if you want to restart it"
    else
        # Export environment variables
        export AI_AGENTIC_API_KEY="${AI_AGENTIC_API_KEY}"
        export POSTGRES_HOST="localhost"
        export POSTGRES_PORT="5432"
        export POSTGRES_USER="postgres"
        export POSTGRES_PASSWORD="postgres"
        export POSTGRES_DB="bookings_db"
        export CHROMA_HOST="localhost"
        export CHROMA_PORT="8000"
        export API_HOST="0.0.0.0"
        export API_PORT="8001"
        
        # Create logs directory if it doesn't exist
        mkdir -p "$SCRIPT_DIR/logs"
        
        # Start API in background
        nohup python main.py > "$SCRIPT_DIR/logs/api.log" 2>&1 &
        API_PID=$!
        echo $API_PID > "$SCRIPT_DIR/logs/api.pid"
        
        echo -e "${GREEN}✓ API started (PID: $API_PID)${NC}"
        
        # Wait for API to be fully ready (loads agents, vector store, etc.)
        echo -n "Waiting for API to initialize"
        for i in {1..15}; do
            sleep 2
            echo -n "."
            if curl -s http://localhost:8001 > /dev/null 2>&1; then
                echo ""
                echo -e "${GREEN}✓ API is ready${NC}"
                break
            fi
            if [ $i -eq 15 ]; then
                echo ""
                echo -e "${RED}✗ API failed to start. Check logs/api.log${NC}"
                tail -20 "$SCRIPT_DIR/logs/api.log"
                exit 1
            fi
        done
    fi
    
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Workshop is ready!${NC}"
    echo ""
    echo -e "${GREEN}🌐 AI Agents API:${NC} http://localhost:8001"
    echo -e "${GREEN}🗄️  PostgreSQL:${NC}    localhost:5432 (database: bookings_db)"
    echo -e "${GREEN}📊 ChromaDB:${NC}       localhost:8000"
    echo ""
    echo -e "📝 API logs: ${YELLOW}tail -f logs/api.log${NC}"
    echo -e "🛑 Stop all:  ${YELLOW}./workshop.sh stop${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}🛑 Stopping Hospitality Workshop Services...${NC}"
    echo ""
    
    # 1. Stop API
    if [ -f "$SCRIPT_DIR/logs/api.pid" ]; then
        API_PID=$(cat "$SCRIPT_DIR/logs/api.pid")
        echo -n "Stopping API (PID: $API_PID)... "
        if kill $API_PID 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}⚠ (not running)${NC}"
        fi
        rm -f "$SCRIPT_DIR/logs/api.pid"
    else
        echo -n "Stopping API... "
        # Try to kill any running uvicorn process
        pkill -f "uvicorn main:app" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}⚠ (not running)${NC}"
        fi
    fi
    
    # 2. Stop database containers
    echo ""
    echo -e "${YELLOW}📦 Stopping database containers...${NC}"
    cd "$COMPOSE_DIR" || exit 1
    sudo -E docker-compose down
    
    echo ""
    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Function to show status
show_status() {
    echo -e "${GREEN}📊 Workshop Services Status${NC}"
    echo ""
    
    # Check API
    echo -n "🌐 AI Agents API: "
    if check_api_running; then
        PID=$(pgrep -f "uvicorn main:app")
        echo -e "${GREEN}✓ Running (PID: $PID)${NC}"
        echo "   URL: http://localhost:8001"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi
    
    echo ""
    echo "🗄️  Database Containers:"
    cd "$COMPOSE_DIR" || exit 1
    sudo -E docker-compose ps
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}📝 Container Logs (Ctrl+C to exit)${NC}"
    echo ""
    cd "$COMPOSE_DIR" || exit 1
    sudo -E docker-compose logs -f
}

# Main script logic
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    logs)
        show_logs
        ;;
    *)
        show_help
        ;;
esac
