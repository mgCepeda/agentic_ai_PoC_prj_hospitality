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
# Set to False to try Google Gemini text-embedding-004 first
USE_HUGGINGFACE = False


def build_vectorstore_simple() -> Chroma:
    global USE_HUGGINGFACE

    # Persist directory for vector store
    persist_dir = _project_root().parent / "bookings-db" / "vectorstore" / "chroma_db"
    
    # Select embeddings backend
    if USE_HUGGINGFACE:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    else:
        try:
            print("🔄 Trying Google Gemini text-embedding-004 model...")
            embeddings = GoogleGenerativeAIEmbeddings(
                model="text-embedding-004",
                google_api_key=os.getenv("AI_AGENTIC_API_KEY"),
            )
            print("✅ Using Google Gemini text-embedding-004")
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

    # Load JSON with enriched descriptions
    if json_path.exists():
        try:
            import json
            from langchain_core.documents import Document
            
            print(f"📖 Loading hotels from {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                hotels_data = json.load(f)
            
            hotels_list = hotels_data.get('Hotels', [])
            print(f"✅ Found {len(hotels_list)} hotels in JSON")
            
            # Create enriched documents for better semantic search
            for hotel in hotels_list:
                try:
                    hotel_name = hotel.get('Name', 'Unknown')
                    address = hotel.get('Address', {})
                    params = hotel.get('SyntheticParams', {})
                    
                    # Create descriptive text with multiple phrasings for better retrieval
                    enriched_text = f"""
=== Hotel: {hotel_name} ===
Location: {address.get('City', '')}, {address.get('Country', '')}
Full Address: {address.get('Address', '')}, {address.get('City', '')}, {address.get('ZipCode', '')}, {address.get('Country', '')}

**Pricing Policies and Charges:**
- Extra Bed Charge: {params.get('ExtraBedChargePercentage', 'N/A')}% surcharge/additional charge for extra bed
- Extra Bed Surcharge: {params.get('ExtraBedChargePercentage', 'N/A')}% extra cost when adding a bed
- Occupancy Discount: {params.get('OccupancyBaseDiscountPercentage', 'N/A')}% discount for reduced occupancy/fewer guests
- Promotion Discount: {params.get('PromotionPriceDiscount', 'N/A')}% discount on promotional prices

**Meal Plan Charges (Price Multipliers):**
"""
                    meal_prices = params.get('MealPlanPrices', {})
                    for plan, multiplier in meal_prices.items():
                        enriched_text += f"- {plan}: {multiplier}x base price\n"
                    
                    # Add room information
                    enriched_text += "\n**Available Rooms:**\n"
                    for room in hotel.get('Rooms', [])[:5]:  # First 5 rooms as sample
                        enriched_text += f"- Room {room.get('RoomId')}: {room.get('Category')} {room.get('Type')}, "
                        enriched_text += f"{room.get('Guests')} guests, Off-season: €{room.get('PriceOffSeason')}, Peak-season: €{room.get('PricePeakSeason')}\n"
                    
                    # Add original JSON for exact data
                    enriched_text += f"\n**Raw Data:**\n{json.dumps(hotel, ensure_ascii=False, indent=2)}"
                    
                    docs.append(Document(page_content=enriched_text, metadata={
                        "source": "hotels.json",
                        "hotel_name": hotel_name,
                        "city": address.get('City', ''),
                        "country": address.get('Country', '')
                    }))
                except Exception as e:
                    print(f"⚠️ Error processing hotel {hotel.get('Name', 'Unknown')}: {e}")
                    continue
            
            print(f"✅ Created {len(docs)} enriched hotel documents")
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            import traceback
            traceback.print_exc()

    if details_md.exists():
        docs += TextLoader(str(details_md), encoding="utf-8").load()
    if rooms_md.exists():
        docs += TextLoader(str(rooms_md), encoding="utf-8").load()

    # Split with larger chunks for better context
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
    chunks = text_splitter.split_documents(docs)

    # Vector store with persistence
    persist_dir.mkdir(parents=True, exist_ok=True)
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=str(persist_dir))
    print(f"✅ Vector store persisted to {persist_dir}")
    return vectorstore
