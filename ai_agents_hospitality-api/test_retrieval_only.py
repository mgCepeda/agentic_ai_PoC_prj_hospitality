#!/usr/bin/env python3
"""
Test Script for RAG - Document Retrieval Verification

This script tests the retrieval part of the RAG system without calling the LLM.
It shows what documents are being retrieved for each query.
"""

from agents.hotel_rag_agent import get_vectorstore

def test_retrieval():
    """Test the document retrieval without LLM."""
    
    print("=" * 80)
    print("🔍 Testing RAG Document Retrieval")
    print("=" * 80)
    print()
    
    # Get vector store
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    # Test queries
    test_queries = [
        "What is the full address of Obsidian Tower?",
        "What are the meal charges for Half Board in hotels in Paris?",
        "List all hotels in France with their cities",
        "What is the discount for extra bed in Grand Victoria?",
        "Compare room prices between peak and off season for hotels in Nice"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(test_queries)}")
        print(f"❓ {query}")
        print("-" * 80)
        
        # Retrieve relevant documents
        docs = retriever.invoke(query)
        
        print(f"\n✅ Retrieved {len(docs)} relevant documents:\n")
        
        for j, doc in enumerate(docs, 1):
            print(f"📄 Document {j}:")
            print(f"Content preview: {doc.page_content[:300]}...")
            if len(doc.page_content) > 300:
                print(f"(... {len(doc.page_content) - 300} more characters)")
            print()
        
        print("-" * 80)


if __name__ == "__main__":
    test_retrieval()
