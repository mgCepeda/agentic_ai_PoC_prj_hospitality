#!/usr/bin/env python3
"""
Simple test - one query only
"""

import os
from agents.hotel_rag_agent import answer_hotel_question_rag_sync

print("Testing with ONE query...")
print("="*80)

try:
    question = "What hotels are in Paris?"
    print(f"Question: {question}")
    print("Calling RAG agent...")
    answer = answer_hotel_question_rag_sync(question)
    print(f"\nAnswer: {answer}")
except Exception as e:
    print(f"Error: {e}")
