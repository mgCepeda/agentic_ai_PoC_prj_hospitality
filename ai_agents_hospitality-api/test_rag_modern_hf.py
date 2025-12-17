#!/usr/bin/env python3
"""
Test RAG with HuggingFace using modern API
"""

import os
from agents.hotel_rag_agent import get_vectorstore
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def test_rag_modern_hf():
    """Test RAG with modern HuggingFace API."""
    
    print("=" * 80)
    print("🏨 Testing RAG with HuggingFace (Modern API)")
    print("=" * 80)
    print()
    
    try:
        # Use HuggingFaceEndpoint with modern API
        print("🤗 Initializing HuggingFace model...")
        llm = HuggingFaceEndpoint(
            repo_id="google/flan-t5-base",
            temperature=0.1,
            max_new_tokens=256,
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
        print("✅ Model initialized\n")
        
        # Get vector store
        print("📦 Loading vector store...")
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        print("✅ Vector store loaded\n")
        
        # Simple prompt for T5
        prompt_template = """Answer the question based on the context.

Context: {context}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate.from_template(prompt_template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content[:400] for doc in docs)
        
        # Create chain
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Test queries
        queries = [
            "What city is Obsidian Tower in?",
            "List hotels in Paris"
        ]
        
        for query in queries:
            print(f"Query: {query}")
            print("-" * 80)
            print("🔄 Generating answer...")
            
            answer = chain.invoke(query)
            print(f"💡 Answer: {answer.strip()}\n")
            print("=" * 80)
            print()
        
        print("✅ RAG is working with real LLM!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rag_modern_hf()
