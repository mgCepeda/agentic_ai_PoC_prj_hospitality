"""
Vector Store (Workshop Simple)

Implementación mínima basada en el snippet del workshop:
- Carga JSON y Markdown
- Split con RecursiveCharacterTextSplitter
- Embeddings con GoogleGenerativeAIEmbeddings
- Vector store en memoria (Chroma)
"""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import JSONLoader, TextLoader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


def _project_root() -> Path:
    # Este archivo está en ai_agents_hospitality-api/util/
    return Path(__file__).parent.parent


def _hotels_dir() -> Path:
    return _project_root().parent / "bookings-db" / "output_files" / "hotels"


# Global flag to track embedding backend
# Set to True to use HuggingFace (free, no API quota) instead of Google (limited quota)
USE_HUGGINGFACE = True


def build_vectorstore_simple() -> Chroma:
    global USE_HUGGINGFACE

    # Persist directory for vector store
    persist_dir = _project_root() / "vectorstore" / "chroma_db"
    
    # Select embeddings backend
    if USE_HUGGINGFACE:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    else:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=os.getenv("AI_AGENTIC_API_KEY"),
            )
        except Exception as e:
            print(f"⚠️ Google embeddings unavailable: {e}. Switching to HuggingFace.")
            USE_HUGGINGFACE = True
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Check if vectorstore already exists
    if persist_dir.exists() and any(persist_dir.iterdir()):
        print("✅ Loading persisted vector store (no API calls needed)")
        vectorstore = Chroma(persist_directory=str(persist_dir), embedding_function=embeddings)
        return vectorstore
    
    # Build new vectorstore
    print("🔨 Building new vector store...")
    hotels_dir = _hotels_dir()
    json_path = hotels_dir / "hotels.json"
    details_md = hotels_dir / "hotel_details.md"
    rooms_md = hotels_dir / "hotel_rooms.md"

    # Cargar documentos (JSON + Markdown)
    docs: List = []

    if json_path.exists():
        json_loader = JSONLoader(
            file_path=str(json_path),
            jq_schema=".Hotels[]",
            text_content=False,
        )
        docs += json_loader.load()

    if details_md.exists():
        docs += TextLoader(str(details_md), encoding="utf-8").load()
    if rooms_md.exists():
        docs += TextLoader(str(rooms_md), encoding="utf-8").load()

    # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    # Vector store with persistence
    persist_dir.mkdir(parents=True, exist_ok=True)
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=str(persist_dir))
    print(f"✅ Vector store persisted to {persist_dir}")
    return vectorstore
