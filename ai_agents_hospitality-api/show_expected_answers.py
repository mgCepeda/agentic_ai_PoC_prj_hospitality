#!/usr/bin/env python3
"""
Test RAG - Show what the bot SHOULD answer based on retrieved documents

This simulates the RAG response by showing retrieved context that would be used.
"""

from agents.hotel_rag_agent import get_vectorstore

def show_expected_answer(query: str):
    """Show what documents are retrieved and what answer should be generated."""
    
    print(f"\n{'='*80}")
    print(f"❓ Query: {query}")
    print("-" * 80)
    
    # Get vector store and retrieve
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    
    print(f"\n📚 Retrieved {len(docs)} relevant documents for context:\n")
    
    all_context = []
    for i, doc in enumerate(docs, 1):
        content = doc.page_content.strip()
        all_context.append(content)
        print(f"Document {i}:\n{content}\n")
        print("-" * 40)
    
    print(f"\n💡 Based on this context, the RAG bot SHOULD answer:\n")
    print("(The LLM would synthesize these documents into a coherent answer)")
    print("=" * 80)
    
    return all_context


def main():
    print("=" * 80)
    print("🏨 RAG System - Expected Answers Based on Retrieved Context")
    print("=" * 80)
    print("\nThis shows what documents are retrieved and what the bot should answer.")
    
    test_queries = [
        "What is the full address of Obsidian Tower?",
        "What are the meal charges for Half Board in hotels in Paris?",
        "List all hotels in France with their cities",
    ]
    
    for query in test_queries:
        show_expected_answer(query)
        input("\nPress Enter to continue to next query...")


if __name__ == "__main__":
    main()
