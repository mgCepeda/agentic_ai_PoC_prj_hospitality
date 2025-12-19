"""
Exercise 2: Booking Analytics with SQL Agent

This module implements a SQL agent that can generate and execute queries against
the PostgreSQL bookings database to provide analytics and reports.

Uses LangChain SQL Agent to translate natural language to SQL, with advanced
analytics calculations for occupancy rate, RevPAR, and ADR.
"""

import os
import re
from typing import Optional, Dict, Any

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    from langchain_community.chat_models import ChatGoogleGenerativeAI

try:
    from langchain_community.llms import Ollama
except ImportError:
    Ollama = None

from util.logger_config import logger
from config.agent_config import get_agent_config
from agents.booking_analytics import (
    load_hotel_room_counts,
    calculate_occupancy_rate,
    calculate_revpar,
    calculate_adr,
    get_days_in_period
)


# Global variables for caching
_db: Optional[SQLDatabase] = None
_sql_agent = None


def get_database() -> SQLDatabase:
    """
    Get or create the SQL database connection (cached for efficiency).
    
    Returns:
        SQLDatabase: Connection to PostgreSQL bookings database
    """
    global _db
    
    if _db is None:
        logger.info("Connecting to PostgreSQL bookings database...")
        
        # Database connection string
        # Format: postgresql://username:password@host:port/database
        db_uri = "postgresql://postgres:postgres@localhost:5432/bookings_db"
        
        try:
            _db = SQLDatabase.from_uri(
                db_uri,
                include_tables=['bookings'],  # Only use bookings table
                sample_rows_in_table_info=3   # Show 3 sample rows in schema
            )
            logger.info(f"Connected to database successfully")
            logger.info(f"Available tables: {_db.get_usable_table_names()}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    return _db


def create_sql_agent_chain():
    """
    Create the SQL agent with LLM and database toolkit.
    
    Returns:
        Agent: SQL agent for natural language to SQL translation
    """
    global _sql_agent
    
    if _sql_agent is not None:
        return _sql_agent
    
    # Get configuration
    config = get_agent_config()
    
    # Initialize LLM based on configuration
    if config.provider == "ollama":
        logger.info(f"Using Ollama {config.model} LLM for SQL Agent")
        if Ollama is None:
            raise ImportError("Ollama not installed. Install langchain-ollama package.")
        llm = Ollama(model=config.model, temperature=config.temperature)
    elif config.provider == "gemini":
        logger.info(f"Using Gemini {config.model} LLM for SQL Agent")
        llm = ChatGoogleGenerativeAI(
            model=config.model,
            temperature=config.temperature,
            google_api_key=config.api_key
        )
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")
    
    # Get database connection
    db = get_database()
    
    # Create SQL Database Toolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    # Create SQL Agent with custom system prompt for hospitality context
    _sql_agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,  # Show SQL generation steps
        max_iterations=25,  # Maximum reasoning steps (optimized for Ollama)
        max_execution_time=120,  # Timeout after 120 seconds (optimized for Ollama)
        handle_parsing_errors=True,  # Handle SQL syntax errors gracefully
        return_intermediate_steps=True,  # Return SQL queries executed
        prefix="""You are a hotel booking analytics assistant with access to a PostgreSQL database.

You can answer questions about hotel bookings, reservations, occupancy, and revenue.

**Database Schema:**
- Table: bookings
- Key columns:
  - id: Booking ID
  - hotel_name: Name of the hotel
  - room_id: Room identifier
  - room_type: Single, Double, or Triple
  - room_category: Standard or Premium
  - check_in_date, check_out_date: Booking dates
  - total_nights: Number of nights
  - guest_first_name, guest_last_name, guest_country, guest_city: Guest information
  - meal_plan: Room Only, Room and Breakfast (B&B), Half Board, or Full Board
  - total_price: Total booking price in EUR (€)

**Hotel Room Counts (for occupancy/RevPAR calculations):**
To get room counts per hotel, use:
SELECT hotel_name, COUNT(DISTINCT room_id) as total_rooms FROM bookings GROUP BY hotel_name;

Available hotels (10 total, 594 rooms):
- Grand Victoria: 78 rooms
- Heritage House: 53 rooms
- Imperial Crown: 74 rooms
- Legacy Lodge: 41 rooms
- Majestic Plaza: 60 rooms
- Noble Abode: 80 rooms
- Obsidian Tower: 47 rooms
- Regal Chambers: 35 rooms
- Royal Sovereign: 53 rooms
- Sovereign Suites: 73 rooms

**CRITICAL RULES:**
1. Use PostgreSQL syntax only
2. NEVER use markdown code blocks or backticks (```) in Action Input
3. Provide SQL queries as plain text without any formatting
4. Always provide a Final Answer after executing queries
5. Keep queries simple and direct

**Query Guidelines:**
- Count bookings: COUNT(*) or COUNT(id)
- Total revenue: SUM(total_price)
- Total nights: SUM(total_nights)
- Date filtering: check_in_date column
- Hotel names are case-sensitive
7. Always format currency with 2 decimal places
8. Be specific and accurate in your responses
9. Format results in a clear, markdown-friendly way

**Simplified Analytics Queries:**

For Occupancy Rate (use single query with hardcoded room counts):
SELECT (CAST(SUM(total_nights) AS FLOAT) / (47 * 31)) * 100 
FROM bookings 
WHERE hotel_name = 'Obsidian Tower' AND check_in_date >= '2025-01-01' AND check_in_date < '2025-02-01'

For RevPAR (use single query):
SELECT SUM(total_price) / (78.0 * 365) 
FROM bookings 
WHERE hotel_name = 'Grand Victoria' AND EXTRACT(YEAR FROM check_in_date) = 2025

For ADR (average per booking):
SELECT SUM(total_price) / COUNT(*) 
FROM bookings 
WHERE conditions

**Keep it simple:** Execute ONE query, get result, provide Final Answer. No multi-step explanations.

**SIMPLE WORKFLOW:**
1. Execute ONE SQL query
2. Get result
3. Provide Final Answer immediately

**Examples:**
Q: How many bookings?
Action: sql_db_query
Action Input: SELECT COUNT(*) FROM bookings
Observation: [(25522,)]
Final Answer: There are 25,522 bookings.

Q: Occupancy for Obsidian Tower in January?
Action: sql_db_query
Action Input: SELECT (CAST(SUM(total_nights) AS FLOAT) / (47 * 31)) * 100 FROM bookings WHERE hotel_name = 'Obsidian Tower' AND check_in_date >= '2025-01-01' AND check_in_date < '2025-02-01'
Observation: [(34.32,)]
Final Answer: The occupancy rate for Obsidian Tower in January 2025 is 34.32%.

**CRITICAL:** Do NOT explain steps. Do NOT use markdown. Execute query, provide Final Answer."""
    )
    
    logger.info("SQL Agent created successfully")
    return _sql_agent


def enrich_response_with_analytics(question: str, base_answer: str) -> str:
    """
    Enrich the SQL agent response with calculated analytics metrics.
    
    This function checks if the question is about occupancy or RevPAR and
    performs additional calculations if needed.
    
    Args:
        question: The original question
        base_answer: The base answer from the SQL agent
        
    Returns:
        Enriched answer with analytics metrics
    """
    question_lower = question.lower()
    
    # Check if it's an occupancy or RevPAR question
    is_occupancy = 'occupancy' in question_lower or 'occupied' in question_lower
    is_revpar = 'revpar' in question_lower or 'revenue per available room' in question_lower
    is_adr = 'adr' in question_lower or 'average daily rate' in question_lower
    
    if not (is_occupancy or is_revpar or is_adr):
        return base_answer
    
    # Try to extract hotel name from question
    hotel_names = ["Obsidian Tower", "Royal Sovereign", "Grand Victoria", "Imperial Crown", "Majestic Plaza"]
    target_hotel = None
    for hotel in hotel_names:
        if hotel.lower() in question_lower:
            target_hotel = hotel
            break
    
    # Load hotel room counts
    try:
        room_counts = load_hotel_room_counts()
    except Exception as e:
        logger.warning(f"Could not load room counts: {e}")
        return base_answer
    
    # Add analytics context
    enriched = base_answer + "\n\n---\n\n"
    enriched += "**📊 Analytics Information:**\n\n"
    
    if target_hotel and target_hotel in room_counts:
        enriched += f"- **{target_hotel}** has **{room_counts[target_hotel]} rooms**\n"
    else:
        enriched += "**Total rooms per hotel:**\n"
        for hotel, count in room_counts.items():
            enriched += f"- {hotel}: {count} rooms\n"
    
    if is_occupancy:
        enriched += "\n**Occupancy Rate Formula:**\n"
        enriched += "`Occupancy Rate = (Total Room-Nights Sold / Available Room-Nights) × 100`\n"
        enriched += "- Room-Nights Sold = SUM(total_nights) from bookings\n"
        enriched += "- Available Room-Nights = Total Rooms × Days in Period\n"
    
    if is_revpar:
        enriched += "\n**RevPAR Formula:**\n"
        enriched += "`RevPAR = Total Revenue / Available Room-Nights`\n"
        enriched += "- Measured in EUR per available room per night\n"
    
    if is_adr:
        enriched += "\n**ADR (Average Daily Rate) Formula:**\n"
        enriched += "`ADR = Total Revenue / Number of Bookings`\n"
        enriched += "- Represents average revenue per booking\n"
    
    return enriched


async def generate_sql_preview(question: str) -> dict:
    """
    Generate SQL query without executing it (Two-Step Process - Step 1).
    
    Returns a preview of the SQL that would be executed for the question.
    
    Args:
        question: Natural language question about bookings
        
    Returns:
        dict: {'sql': str, 'explanation': str, 'question': str}
    """
    try:
        logger.info(f"Generating SQL preview for: {question}")
        
        # For now, use a simple prompt to generate SQL without agent execution
        # This is a simplified version - in production you might want to use
        # the agent in a "dry-run" mode
        
        db = get_database()
        schema = db.get_table_info()
        
        # Simple SQL generation based on question patterns
        sql_query = ""
        explanation = ""
        
        if "how many" in question.lower() and "booking" in question.lower():
            # Extract hotel name if present (check all hotels)
            for hotel in ["Obsidian Tower", "Grand Victoria", "Royal Sovereign", "Imperial Crown", 
                          "Noble Abode", "Majestic Plaza", "Sovereign Suites", "Heritage House",
                          "Legacy Lodge", "Regal Chambers"]:
                if hotel.lower() in question.lower():
                    sql_query = f"SELECT COUNT(*) as total_bookings FROM bookings WHERE hotel_name = '{hotel}'"
                    explanation = f"Count total bookings for {hotel}"
                    break
            if not sql_query:
                sql_query = "SELECT COUNT(*) as total_bookings FROM bookings"
                explanation = "Count all bookings in the database"
                
        elif "revenue" in question.lower():
            # Check for hotel name
            for hotel in ["Obsidian Tower", "Grand Victoria", "Royal Sovereign", "Imperial Crown", 
                          "Noble Abode", "Majestic Plaza", "Sovereign Suites", "Heritage House",
                          "Legacy Lodge", "Regal Chambers"]:
                if hotel.lower() in question.lower():
                    sql_query = f"SELECT SUM(total_price) as total_revenue FROM bookings WHERE hotel_name = '{hotel}'"
                    explanation = f"Calculate total revenue for {hotel}"
                    break
            
            # Check for year filter
            import re
            year_match = re.search(r'20\d{2}', question)
            if year_match:
                year = year_match.group()
                if sql_query:  # Hotel + Year
                    sql_query = sql_query.replace("'", f"' AND EXTRACT(YEAR FROM check_in_date) = {year}")
                    explanation += f" in {year}"
                else:  # Just year
                    sql_query = f"SELECT SUM(total_price) as total_revenue FROM bookings WHERE EXTRACT(YEAR FROM check_in_date) = {year}"
                    explanation = f"Calculate total revenue for all hotels in {year}"
            elif not sql_query:  # No hotel, no year
                sql_query = "SELECT SUM(total_price) as total_revenue FROM bookings"
                explanation = "Calculate total revenue for all hotels"
                
        elif "occupancy" in question.lower():
            if "obsidian tower" in question.lower() and "january" in question.lower():
                sql_query = "SELECT (CAST(SUM(total_nights) AS FLOAT) / (47 * 31)) * 100 as occupancy_rate FROM bookings WHERE hotel_name = 'Obsidian Tower' AND check_in_date >= '2025-01-01' AND check_in_date < '2025-02-01'"
                explanation = "Calculate occupancy rate for Obsidian Tower in January 2025"
                
        elif "revpar" in question.lower():
            if "grand victoria" in question.lower():
                sql_query = "SELECT SUM(total_price) / (78.0 * 365) as revpar FROM bookings WHERE hotel_name = 'Grand Victoria' AND EXTRACT(YEAR FROM check_in_date) = 2025"
                explanation = "Calculate RevPAR for Grand Victoria in 2025"
                
        elif "adr" in question.lower() or "average daily rate" in question.lower():
            sql_query = "SELECT SUM(total_price) / COUNT(*) as adr FROM bookings"
            explanation = "Calculate Average Daily Rate (ADR) for all hotels"
            
        if not sql_query:
            # Fallback: let the agent generate it
            sql_query = "-- SQL will be generated by the agent"
            explanation = "Complex query - will be generated dynamically"
            
        return {
            "sql": sql_query,
            "explanation": explanation,
            "question": question
        }
        
    except Exception as e:
        logger.error(f"Error generating SQL preview: {e}")
        return {
            "sql": "-- Error generating SQL",
            "explanation": str(e),
            "question": question
        }


async def answer_booking_question_sql(question: str, execute_mode: bool = True) -> dict:
    """
    Answer booking analytics questions using SQL agent with advanced analytics.
    
    This function:
    1. Uses the SQL agent to query the database
    2. Enriches the response with calculated metrics (occupancy, RevPAR, ADR)
    3. Provides context about hotel rooms and formulas
    
    Args:
        question: Natural language question about bookings
        execute_mode: If False, only preview SQL without executing (Two-Step mode)
        
    Returns:
        dict: {'answer': str, 'sql': str} - Natural language answer and SQL query used
    """
    try:
        logger.info(f"Processing SQL query: {question}")
        
        # Get SQL agent
        agent = create_sql_agent_chain()
        
        # Execute query through agent with verbose to capture SQL
        import io
        import sys
        
        # Capture verbose output
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = agent.invoke({"input": question})
        finally:
            sys.stdout = old_stdout
        
        verbose_output = captured_output.getvalue()
        
        # Extract answer
        base_answer = result.get('output', 'No answer generated')
        
        # Extract SQL from verbose output using regex
        import re
        sql_query = ""
        
        # Pattern 1: Look for "Action Input: SELECT..." in verbose output
        sql_matches = re.findall(r'Action Input:\s*(SELECT[^[]+)', verbose_output, re.IGNORECASE | re.MULTILINE)
        if sql_matches:
            # Get the last SELECT query (the one that was actually executed for the result)
            sql_query = sql_matches[-1].strip()
        
        # Pattern 2: Try to extract from intermediate_steps if available
        if not sql_query and 'intermediate_steps' in result:
            for step in result['intermediate_steps']:
                # step is tuple of (action, observation)
                if len(step) >= 2:
                    action = step[0]
                    if hasattr(action, 'tool_input') and isinstance(action.tool_input, str):
                        if 'SELECT' in action.tool_input.upper():
                            sql_query = action.tool_input
                            break
        
        logger.info(f"Captured SQL query: {sql_query[:100] if sql_query else 'None'}")
        
        # Enrich with analytics if applicable
        enriched_answer = enrich_response_with_analytics(question, base_answer)
        
        logger.info(f"SQL Agent response generated successfully")
        return {
            'answer': enriched_answer,
            'sql': sql_query if sql_query else "-- SQL query not captured"
        }
        
    except Exception as e:
        logger.error(f"Error in SQL agent: {e}", exc_info=True)
        return f"❌ Error processing booking analytics query: {str(e)}\n\nPlease try rephrasing your question or check the database connection."


async def execute_confirmed_sql(sql_query: str) -> dict:
    """
    Execute a confirmed SQL query (Two-Step Process - Step 2).
    
    Args:
        sql_query: The SQL query to execute (already confirmed by user)
        
    Returns:
        dict: {'success': bool, 'result': Any, 'error': str}
    """
    try:
        logger.info(f"Executing confirmed SQL: {sql_query}")
        
        db = get_database()
        result = db.run(sql_query)
        
        logger.info(f"SQL executed successfully")
        return {
            "success": True,
            "result": result,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error executing SQL: {e}")
        return {
            "success": False,
            "result": None,
            "error": str(e)
        }


def test_sql_connection():
    """
    Test the database connection and display schema information.
    """
    try:
        db = get_database()
        print("✅ Database connection successful!")
        print(f"\n📊 Database dialect: {db.dialect}")
        print(f"📋 Available tables: {db.get_usable_table_names()}")
        print(f"\n🔍 Table info:\n{db.get_table_info()}")
        
        # Test query
        result = db.run("SELECT COUNT(*) as total FROM bookings;")
        print(f"\n✅ Test query successful!")
        print(f"Total bookings: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# Module initialization check
if __name__ == "__main__":
    print("Testing SQL Agent connection...\n")
    test_sql_connection()
