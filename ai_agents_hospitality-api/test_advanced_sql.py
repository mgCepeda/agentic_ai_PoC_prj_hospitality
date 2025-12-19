#!/usr/bin/env python3
"""
Advanced SQL Agent Testing - Phase 6
Complex analytics queries with date ranges, comparisons, and aggregations
"""
import asyncio
from agents.bookings_sql_agent import answer_booking_question_sql

async def test_advanced_queries():
    """Test complex analytics queries"""
    
    print("=" * 80)
    print("🧪 ADVANCED SQL AGENT TESTING - PHASE 6")
    print("=" * 80)
    print()
    
    # Advanced test queries
    test_queries = [
        {
            "category": "Date Range Analysis",
            "question": "How many bookings were made in Q1 2025 (January to March)?",
            "expected": "Should filter by check_in_date between Jan 1 and Mar 31"
        },
        {
            "category": "Comparison Query",
            "question": "Which hotel has more bookings: Grand Victoria or Obsidian Tower?",
            "expected": "Should compare counts between two hotels"
        },
        {
            "category": "Guest Country Analysis",
            "question": "How many bookings are from Italy?",
            "expected": "Should filter by guest_country"
        },
        {
            "category": "Meal Plan Analysis",
            "question": "What is the total revenue from Full Board meal plans?",
            "expected": "Should filter by meal_plan and sum total_price"
        },
        {
            "category": "Room Type Analysis",
            "question": "How many Premium category rooms were booked?",
            "expected": "Should filter by room_category = Premium"
        },
        {
            "category": "Revenue per Hotel",
            "question": "Show me revenue for each hotel sorted from highest to lowest",
            "expected": "Should GROUP BY hotel_name with SUM and ORDER BY DESC"
        },
        {
            "category": "Average Calculation",
            "question": "What is the average number of nights per booking?",
            "expected": "Should calculate AVG(total_nights)"
        },
        {
            "category": "Multiple Conditions",
            "question": "How many Double room bookings does Noble Abode have?",
            "expected": "Should filter by hotel_name AND room_type"
        },
        {
            "category": "Top N Query",
            "question": "Show me the top 3 hotels by total bookings",
            "expected": "Should use LIMIT 3 with ORDER BY"
        },
        {
            "category": "Complex Analytics",
            "question": "What is the RevPAR for all hotels combined in 2025?",
            "expected": "Should calculate total revenue / (total rooms × days)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"📊 Test {i}/{len(test_queries)}: {test['category']}")
        print(f"❓ Question: {test['question']}")
        print(f"🎯 Expected: {test['expected']}")
        print("-" * 80)
        
        try:
            answer = await answer_booking_question_sql(test['question'])
            
            # Check if we got a meaningful answer (not an error)
            if "❌" in answer or "Error" in answer:
                print(f"❌ FAILED - Error in response")
                print(f"Response: {answer[:200]}...")
                failed += 1
            else:
                print(f"✅ PASSED")
                print(f"Answer: {answer[:300]}...")
                passed += 1
                
        except Exception as e:
            print(f"❌ FAILED - Exception: {e}")
            failed += 1
        
        print()
        print("=" * 80)
        print()
        
        # Small delay between queries for Ollama
        if i < len(test_queries):
            await asyncio.sleep(3)
    
    # Summary
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{len(test_queries)}")
    print(f"❌ Failed: {failed}/{len(test_queries)}")
    print(f"📈 Success Rate: {(passed/len(test_queries)*100):.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_advanced_queries())
