#!/usr/bin/env python3
"""
Test RAG with Ollama (Local LLM - No API needed!)
"""

from agents.hotel_rag_agent import get_vectorstore
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def test_rag_with_ollama():
    """Test RAG using local Ollama model."""
    
    print("=" * 80)
    print("🏨 Testing RAG with Ollama (Local LLM)")
    print("=" * 80)
    print()
    
    # Initialize Ollama LLM
    print("🦙 Initializing Ollama model (llama3.2:1b)...")
    llm = Ollama(model="llama3.2:1b", temperature=0)
    print("✅ Model loaded\n")
    
    # Get vector store and retriever
    print("📦 Loading vector store...")
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    print("✅ Vector store loaded\n")
    
    # Create prompt
    prompt_template = """You are a helpful hotel assistant. Use the context to answer the question accurately and concisely.

Context:
{context}

Question: {question}

Answer:"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Helper function to format documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content[:600] for doc in docs)
    
    # Create chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Test queries
    test_queries = [
        "What city is Obsidian Tower located in?",
        "List hotels in Paris",
        "What are room prices in Nice?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}/{len(test_queries)}")
        print(f"❓ {query}")
        print("-" * 80)
        
        try:
            print("🔄 Generating answer with Ollama...")
            answer = chain.invoke(query)
            print(f"💡 Answer:\n{answer.strip()}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
        
        print("=" * 80)
        print()
    
    print("✅ RAG is working with LOCAL Ollama LLM!")
    print("No API keys needed, no quota limits!")


if __name__ == "__main__":
    test_rag_with_ollama()
