#!/usr/bin/env python3
"""
Minimal SQL Agent Test - 3 consultas incluyendo analytics
"""
import asyncio
from agents.bookings_sql_agent import answer_booking_question_sql

async def test_queries():
    queries = [
        "How many total bookings?",
        "What is the revenue for Royal Sovereign?",
        "Calculate the occupancy rate for Obsidian Tower in January 2025"
    ]
    
    print("=" * 80)
    print("🧪 MINIMAL SQL AGENT TEST - 3 QUERIES")
    print("=" * 80)
    print()
    
    for i, question in enumerate(queries, 1):
        print(f"📊 Query {i}/{len(queries)}")
        print(f"❓ {question}")
        print("-" * 80)
        
        try:
            answer = await answer_booking_question_sql(question)
            print(f"✅ Answer:\n{answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        if i < len(queries):
            print("⏳ Waiting 5 seconds...\n")
            await asyncio.sleep(5)
    
    print("=" * 80)
    print("✅ Test complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_queries())
