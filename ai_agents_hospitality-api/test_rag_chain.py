#!/usr/bin/env python3
"""
Test Script for Exercise 1 - Step 3: RAG Chain

This script tests the RAG chain implementation with sample hotel queries.
"""

import asyncio
from agents.hotel_rag_agent import answer_hotel_question_rag

async def test_rag_chain():
    """Test the RAG chain with various hotel queries."""
    
    print("=" * 80)
    print("🏨 Testing RAG Chain - Exercise 1 Step 3")
    print("=" * 80)
    print()
    
    # Test queries from the workshop
    test_queries = [
        "What is the full address of Obsidian Tower?",
        "What are the meal charges for Half Board in hotels in Paris?",
        "List all hotels in France with their cities",
        "What is the discount for extra bed in Grand Victoria?",
        "Compare room prices between peak and off season for hotels in Nice"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}/{len(test_queries)}")
        print(f"❓ {query}")
        print("-" * 80)
        
        try:
            answer = await answer_hotel_question_rag(query)
            print(f"💡 Answer:\n{answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        print("=" * 80)
        print()


if __name__ == "__main__":
    asyncio.run(test_rag_chain())
