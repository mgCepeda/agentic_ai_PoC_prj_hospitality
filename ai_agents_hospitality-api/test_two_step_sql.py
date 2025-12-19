#!/usr/bin/env python3
"""
Test Two-Step SQL Query Process
Step 1: Preview SQL without executing
Step 2: Execute confirmed SQL
"""
import asyncio
from agents.bookings_sql_agent import generate_sql_preview, execute_confirmed_sql

async def test_two_step_process():
    """Test the two-step query process"""
    
    print("=" * 80)
    print("🧪 TESTING TWO-STEP SQL QUERY PROCESS")
    print("=" * 80)
    print()
    
    # Test queries
    test_queries = [
        "How many total bookings are there?",
        "What is the total revenue for Royal Sovereign?",
        "Calculate the occupancy rate for Obsidian Tower in January 2025"
    ]
    
    for i, question in enumerate(test_queries, 1):
        print(f"📊 Test {i}/{len(test_queries)}")
        print(f"❓ Question: {question}")
        print("-" * 80)
        
        # STEP 1: Generate SQL preview
        print("🔍 Step 1: Generating SQL preview...")
        preview = await generate_sql_preview(question)
        
        print(f"📝 SQL Query:")
        print(f"   {preview['sql']}")
        print(f"💡 Explanation: {preview['explanation']}")
        print()
        
        # Simulate user confirmation
        print("✅ User confirms execution...")
        print()
        
        # STEP 2: Execute confirmed SQL
        print("⚙️  Step 2: Executing confirmed SQL...")
        result = await execute_confirmed_sql(preview['sql'])
        
        if result['success']:
            print(f"✅ Execution successful!")
            print(f"📊 Result: {result['result']}")
        else:
            print(f"❌ Execution failed: {result['error']}")
        
        print()
        print("=" * 80)
        print()
    
    print("✅ All two-step tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_two_step_process())
