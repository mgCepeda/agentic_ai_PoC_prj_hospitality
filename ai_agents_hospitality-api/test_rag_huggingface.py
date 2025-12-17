#!/usr/bin/env python3
"""
Test RAG with HuggingFace model (no quota limits)
"""

import os
from agents.hotel_rag_agent import get_vectorstore
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def test_rag_with_huggingface():
    """Test RAG using free HuggingFace models."""
    
    print("=" * 80)
    print("🏨 Testing RAG with HuggingFace (Free, No Quota)")
    print("=" * 80)
    print()
    
    # Initialize HuggingFace LLM (free tier with public inference)
    print("🤗 Loading HuggingFace model (google/flan-t5-large)...")
    print("Note: Using smaller model for better availability without API key")
    llm = HuggingFaceEndpoint(
        repo_id="google/flan-t5-large",
        temperature=0.1,
        max_new_tokens=256,
        timeout=120
    )
    print("✅ Model loaded\n")
    
    # Get vector store and retriever
    print("📦 Loading vector store...")
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    print("✅ Vector store loaded\n")
    
    # Create prompt (simplified for open-source models)
    prompt_template = """You are a hotel assistant. Use the context to answer the question accurately.

Context:
{context}

Question: {question}

Answer in a clear and concise way:"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Helper function to format documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Create chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Test queries
    test_queries = [
        "What is the address of Obsidian Tower?",
        "List hotels in Paris",
        "What meal plans are available?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}/{len(test_queries)}")
        print(f"❓ {query}")
        print("-" * 80)
        
        try:
            answer = chain.invoke(query)
            # Clean up the answer (remove extra whitespace)
            answer = answer.strip()
            print(f"💡 Answer:\n{answer}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
        
        print("=" * 80)
        print()


if __name__ == "__main__":
    test_rag_with_huggingface()
