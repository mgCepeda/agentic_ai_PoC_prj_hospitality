"""
Quick Test - SQL Agent with Key Analytics Queries
"""

import asyncio
from agents.bookings_sql_agent import answer_booking_question_sql


async def test_key_queries():
    """Test SQL Agent with 3 key queries."""
    
    queries = [
        "How many total bookings are there?",
        "What is the total revenue for all hotels in 2025?",
        "How many bookings does Obsidian Tower have?"
    ]
    
    print("\n" + "="*80)
    print("🧪 QUICK TEST - SQL AGENT")
    print("="*80)
    
    for i, question in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"📊 Query {i}/{len(queries)}")
        print("="*80)
        print(f"❓ {question}")
        print("-"*80)
        
        try:
            answer = await answer_booking_question_sql(question)
            print(f"\n✅ Answer:\n{answer}\n")
        except Exception as e:
            print(f"\n❌ Error: {str(e)[:200]}\n")
        
        if i < len(queries):
            print(f"⏳ Waiting 15 seconds...")
            await asyncio.sleep(15)
    
    print("\n" + "="*80)
    print("✅ Test complete!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_key_queries())
