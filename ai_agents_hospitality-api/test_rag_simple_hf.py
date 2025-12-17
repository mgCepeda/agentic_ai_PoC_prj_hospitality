#!/usr/bin/env python3
"""
Test RAG with HuggingFace Inference API (Free Tier)
Uses smaller, faster models that work without authentication
"""

import os
from agents.hotel_rag_agent import get_vectorstore
from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def test_rag_simple():
    """Test RAG with simple HuggingFace model."""
    
    print("=" * 80)
    print("🏨 Testing RAG with HuggingFace (Free API)")
    print("=" * 80)
    print()
    
    try:
        # Use HuggingFaceHub with free inference API
        print("🤗 Initializing HuggingFace model...")
        llm = HuggingFaceHub(
            repo_id="google/flan-t5-base",  # Smaller, faster model
            task="text2text-generation",
            model_kwargs={"temperature": 0.1, "max_length": 256},
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
        print("✅ Model initialized\n")
        
        # Get vector store
        print("📦 Loading vector store...")
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        print("✅ Vector store loaded\n")
        
        # Simple prompt
        prompt_template = """Context: {context}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate.from_template(prompt_template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content[:500] for doc in docs)  # Limit context size
        
        # Create chain
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Test with one simple query
        query = "What city is Obsidian Tower in?"
        print(f"Query: {query}")
        print("-" * 80)
        
        print("🔄 Generating answer (this may take 10-20 seconds)...")
        answer = chain.invoke(query)
        
        print(f"\n💡 Answer: {answer.strip()}\n")
        print("=" * 80)
        print("✅ RAG is working with real LLM!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: HuggingFace free API may require setting HUGGINGFACEHUB_API_TOKEN")
        print("Get a free token at: https://huggingface.co/settings/tokens")


if __name__ == "__main__":
    test_rag_simple()
