"""
Test SQL Agent with Analytics Queries

This script tests the SQL Agent with advanced analytics queries including
occupancy rate, RevPAR, and ADR calculations.
"""

import asyncio
from agents.bookings_sql_agent import answer_booking_question_sql


async def test_analytics_queries():
    """Test SQL Agent with analytics queries."""
    
    queries = [
        # Basic queries
        {
            "question": "How many total bookings are there in the database?",
            "description": "Basic COUNT query"
        },
        {
            "question": "What is the total revenue for all hotels in 2025?",
            "description": "Basic SUM aggregation"
        },
        
        # Hotel-specific queries
        {
            "question": "How many bookings does Obsidian Tower have?",
            "description": "Hotel-specific count"
        },
        {
            "question": "What is the total revenue for Royal Sovereign?",
            "description": "Hotel-specific revenue"
        },
        
        # Analytics calculations
        {
            "question": "Calculate the occupancy rate for Obsidian Tower in January 2025",
            "description": "Occupancy rate calculation"
        },
        {
            "question": "What is the RevPAR for Grand Victoria in 2025?",
            "description": "RevPAR calculation"
        },
        {
            "question": "Show me the ADR (average daily rate) for all hotels",
            "description": "ADR calculation"
        },
        
        # Comparative queries
        {
            "question": "Which hotel has the highest revenue?",
            "description": "Comparison query"
        },
        {
            "question": "Show me total bookings per hotel ordered by count",
            "description": "Aggregation with ordering"
        },
    ]
    
    print("\n" + "="*80)
    print("🧪 TESTING SQL AGENT WITH ANALYTICS QUERIES")
    print("="*80)
    
    for i, query_info in enumerate(queries, 1):
        question = query_info["question"]
        description = query_info["description"]
        
        print(f"\n\n{'='*80}")
        print(f"📊 Query {i}/{len(queries)}: {description}")
        print("="*80)
        print(f"❓ Question: {question}")
        print("-"*80)
        
        try:
            answer = await answer_booking_question_sql(question)
            print(f"\n✅ Answer:\n{answer}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        # Wait between queries to avoid rate limits (10 seconds)
        if i < len(queries):
            print(f"\n⏳ Waiting 10 seconds before next query...")
            await asyncio.sleep(10)
    
    print("\n\n" + "="*80)
    print("✅ All analytics queries tested!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_analytics_queries())
