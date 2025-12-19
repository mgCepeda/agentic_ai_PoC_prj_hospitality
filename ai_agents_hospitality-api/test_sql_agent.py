"""
Test script for SQL Agent - Exercise 2

Tests basic queries with the SQL Agent to verify it can:
1. Generate correct SQL from natural language
2. Execute queries against PostgreSQL
3. Format results appropriately
"""

import asyncio
from agents.bookings_sql_agent import answer_booking_question_sql


async def test_sql_agent():
    """
    Test the SQL agent with various booking analytics queries.
    """
    
    print("=" * 80)
    print("🧪 TESTING SQL AGENT - Exercise 2")
    print("=" * 80)
    print()
    
    # Test queries
    test_queries = [
        "How many bookings are there in total?",
        "Tell me the amount of bookings for Obsidian Tower in 2025",
        "What is the total revenue for all hotels?",
        "How many bookings does Royal Sovereign have?",
        "Show me the total revenue for Grand Victoria",
        "How many bookings are there in January 2025?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"📊 Query {i}/{len(test_queries)}")
        print(f"{'=' * 80}")
        print(f"❓ Question: {query}")
        print("-" * 80)
        
        try:
            answer = await answer_booking_question_sql(query)
            print(f"✅ Answer:\n{answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("=" * 80)
    print("✅ Testing complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_sql_agent())
