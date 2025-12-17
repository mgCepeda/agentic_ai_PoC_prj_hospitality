#!/usr/bin/env python3
"""
Test RAG with automatic model fallback

Tests the RAG system trying different Gemini models until one works.
"""

import asyncio
import os
from agents.hotel_rag_agent import get_vectorstore, answer_hotel_question_rag
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Models to try in order (different quota limits)
MODELS_TO_TRY = [
    "gemini-1.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-pro",
]

def test_with_model(model_name: str, question: str) -> str:
    """Try to answer a question with a specific model."""
    try:
        print(f"  🔄 Trying model: {model_name}...")
        
        # Initialize LLM with specific model
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=os.getenv("AI_AGENTIC_API_KEY")
        )
        
        # Get vector store and retriever
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        
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
        
        # Execute
        answer = chain.invoke(question)
        print(f"  ✅ Model {model_name} worked!")
        return answer
        
    except Exception as e:
        error_msg = str(e)
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            print(f"  ⚠️  Model {model_name} quota exceeded")
        else:
            print(f"  ❌ Model {model_name} error: {error_msg[:100]}")
        return None


async def test_rag_with_fallback():
    """Test RAG with automatic model fallback."""
    
    print("=" * 80)
    print("🏨 Testing RAG with Model Fallback")
    print("=" * 80)
    print()
    
    test_queries = [
        "What is the full address of Obsidian Tower?",
        "What are the meal charges for Half Board in hotels in Paris?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}/{len(test_queries)}")
        print(f"❓ {query}")
        print("-" * 80)
        
        answer = None
        for model in MODELS_TO_TRY:
            answer = test_with_model(model, query)
            if answer:
                break
        
        if answer:
            print(f"\n💡 Answer:\n{answer}\n")
        else:
            print(f"\n❌ All models failed or exceeded quota\n")
        
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_rag_with_fallback())
