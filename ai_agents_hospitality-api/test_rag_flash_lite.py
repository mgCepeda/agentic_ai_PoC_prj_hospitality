#!/usr/bin/env python3
"""
Test RAG with Gemini 2.0 Flash-Lite
"""

import asyncio
import os
from agents.hotel_rag_agent import get_vectorstore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

async def test_rag_gemini_flash_lite():
    """Test RAG with Gemini 2.0 Flash-Lite."""
    
    print("=" * 80)
    print("🏨 Testing RAG with Gemini 2.0 Flash-Lite")
    print("=" * 80)
    print()
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0,
        google_api_key=os.getenv("AI_AGENTIC_API_KEY")
    )
    
    # Get vector store and retriever
    print("📦 Loading vector store...")
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    print("✅ Vector store loaded\n")
    
    # Create prompt
    prompt_template = """You are a helpful hotel assistant with access to detailed information about hotels and rooms.

Use the following context to answer the question accurately and specifically.

Context:
{context}

Question: {question}

Instructions:
- Be accurate and specific, referencing hotel names, locations, and details from the context
- If comparing multiple hotels, present the information in a clear, structured format
- Include relevant prices, room types, and other specific details when available
- If the information is not available in the context, say so clearly
- Format your response in markdown for readability

Answer:"""
    
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
        "What is the full address of Obsidian Tower?",
        "What are the meal charges for Half Board in hotels in Paris?",
        "List all hotels in France with their cities"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}/{len(test_queries)}")
        print(f"❓ {query}")
        print("-" * 80)
        
        try:
            answer = chain.invoke(query)
            print(f"💡 Answer:\n{answer}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
        
        print("=" * 80)
        print()


if __name__ == "__main__":
    asyncio.run(test_rag_gemini_flash_lite())
