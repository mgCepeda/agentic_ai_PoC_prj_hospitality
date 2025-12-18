"""
Exercise 1: Hotel RAG Agent with Vector Store

This module implements a RAG (Retrieval Augmented Generation) agent that answers
questions about hotels and rooms by retrieving information from a vector store.

Uses the full dataset of 50 hotels with efficient retrieval via ChromaDB.
"""

import os
from typing import Optional

try:
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate, PromptTemplate

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    from langchain_community.chat_models import ChatGoogleGenerativeAI

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    HuggingFaceEndpoint = None

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma

from util.vectorstore_builder import build_vectorstore_simple
from util.logger_config import logger
from config.agent_config import get_agent_config


# Global variables for caching
_vectorstore: Optional[Chroma] = None
_rag_chain = None

# Use HuggingFace by default to avoid quota issues
USE_HUGGINGFACE_LLM = True


def get_vectorstore() -> Chroma:
    """
    Get or create the vector store (cached for efficiency).
    
    Returns:
        Chroma: Vector store with hotel and room data
    """
    global _vectorstore
    
    if _vectorstore is None:
        logger.info("Loading vector store for RAG agent...")
        _vectorstore = build_vectorstore_simple()
        logger.info(f"Vector store loaded with {_vectorstore._collection.count()} documents")
    
    return _vectorstore


def create_rag_chain():
    """
    Create the RAG chain with retrieval and generation.
    
    Returns:
        Runnable: Chain for retrieval-augmented generation
    """
    global _rag_chain
    
    if _rag_chain is not None:
        return _rag_chain
    
    # Get configuration
    config = get_agent_config()
    
    # Initialize LLM - Try Gemini first (gemini-2.5-flash-lite)
    try:
        logger.info("Using Gemini gemini-2.5-flash-lite LLM")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0,
            google_api_key=config.api_key
        )
    except Exception as e:
        logger.warning(f"Gemini not available: {e}, trying Ollama as fallback")
        try:
            from langchain_community.llms import Ollama
            logger.info("Using Ollama LLM (local, no quota limits)")
            llm = Ollama(model="llama3.2:1b", temperature=0)
        except Exception as e2:
            logger.error(f"Both Gemini and Ollama failed. Error: {e2}")
            raise Exception("No LLM available. Please configure Gemini API key or install Ollama.")
    
    # Get vector store
    vectorstore = get_vectorstore()
    
    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}  # Retrieve top 5 most relevant documents
    )
    
    # Create custom prompt template for hotel queries
    prompt_template = """You are a helpful hotel assistant with access to detailed information about hotels and rooms.

Use the following context to answer the question accurately and specifically.

**IMPORTANT - Data Field Terminology Guide:**
- When asked about "discount for extra bed" → Look for "ExtraBedChargePercentage" or "Extra Bed Charge" (this is a CHARGE/SURCHARGE, not a discount)
- When asked about "discount for fewer guests" → Look for "OccupancyBaseDiscountPercentage" or "Occupancy Discount"
- When asked about "promotion discount" → Look for "PromotionPriceDiscount"
- When asked about "meal charges" or "meal prices" → Look for "MealPlanPrices" or "Meal Plan Charges"
- Be flexible with terminology - "charge", "surcharge", "additional cost", and "extra fee" are synonyms

Context:
{context}

Question: {question}

Instructions:
- Be accurate and specific, referencing hotel names, locations, and details from the context
- If comparing multiple hotels, present the information in a clear, structured format
- Include relevant prices, room types, and other specific details when available
- Interpret the question flexibly - look for semantically related fields even if terminology differs
- If the information is not available in the context, say so clearly
- Format your response in markdown for readability

Answer:"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Helper function to format documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Create the RAG chain using LCEL (LangChain Expression Language)
    _rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    logger.info("RAG chain created successfully")
    return _rag_chain


async def answer_hotel_question_rag(question: str) -> str:
    """
    Answer a question about hotels using RAG with vector store retrieval.
    
    Args:
        question: Natural language question about hotels or rooms
        
    Returns:
        str: Answer generated by the RAG agent
        
    Example:
        >>> answer = await answer_hotel_question_rag("What is the address of Obsidian Tower?")
    """
    try:
        logger.info(f"Processing RAG query: {question}")
        
        # Get or create RAG chain
        chain = create_rag_chain()
        
        # Execute the query
        answer = chain.invoke(question)
        
        logger.info("RAG query processed successfully")
        return answer
        
    except Exception as e:
        logger.error(f"Error processing RAG query: {e}", exc_info=True)
        return f"Error processing query: {str(e)}"


# Synchronous wrapper for compatibility
def answer_hotel_question_rag_sync(question: str) -> str:
    """
    Synchronous version of answer_hotel_question_rag.
    
    Args:
        question: Natural language question about hotels or rooms
        
    Returns:
        str: Answer generated by the RAG agent
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(answer_hotel_question_rag(question))


if __name__ == "__main__":
    # Test the RAG agent
    test_queries = [
        "What is the full address of Obsidian Tower?",
        "What are the meal charges for Half Board in hotels in Paris?",
        "List all hotels in France with their cities",
        "Compare room prices between peak and off season for hotels in Nice",
    ]
    
    print("🏨 Testing Hotel RAG Agent\n")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 80)
        answer = answer_hotel_question_rag_sync(query)
        print(f"💡 Answer:\n{answer}\n")
        print("=" * 80)
