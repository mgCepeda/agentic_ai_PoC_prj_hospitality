# Ejercicio 1: Implementación RAG - Documentación Completa

## 📋 Resumen Ejecutivo

Este documento detalla la implementación del **Ejercicio 1: Hotel Details with RAG** del workshop de LangChain para aplicaciones de hospitalidad, incluyendo todos los pasos realizados y las mejoras implementadas para optimizar la precisión de las respuestas.

**Fecha de implementación**: Diciembre 18, 2025  
**Modelo de embeddings**: Google Gemini `text-embedding-004` (alternativa: HuggingFace `all-MiniLM-L6-v2`)  
**Modelo LLM**: Google Gemini `gemini-2.5-flash-lite` con fallback a Ollama `llama3.2:1b`  
**Documentos embedidos**: 183 documentos  
**Vector store**: ChromaDB con persistencia en disco

---

## 🎯 Objetivo del Ejercicio 1

Implementar un sistema RAG (Retrieval Augmented Generation) capaz de responder preguntas sobre hoteles y habitaciones utilizando un vector store con **10 hoteles** (aunque finalmente se trabajó con 10 hoteles generados).

### Diferencias con Ejercicio 0
- **Ejercicio 0**: 3 hoteles, contexto directo en prompt
- **Ejercicio 1**: 10 hoteles, RAG con vector store y retrieval eficiente

---

## 📝 Pasos de Implementación

### Fase 1: Configuración Inicial

#### 1.1 Generación de Datos Sintéticos
```bash
cd bookings-db
# Configuración: num_of_hotels: 10 en generate_hotels_param.yaml
python src/gen_synthetic_hotels.py
```

**Resultado**: 10 hoteles generados en `bookings-db/output_files/hotels/`:
- `hotels.json` (201KB) - Datos estructurados
- `hotel_details.md` (94KB) - Descripciones de hoteles
- `hotel_rooms.md` (29KB) - Información de habitaciones

**Hoteles generados**:
1. Obsidian Tower - Cannes, France
2. Royal Sovereign - Paris, France
3. Grand Victoria - Nice, France
4. Imperial Crown - Paris, France
5. Majestic Plaza - Cannes, France
6. Regal Chambers - Nice, France
7. Sovereign Suites - Nice, France
8. Noble Abode - Paris, France
9. Heritage House - Cannes, France
10. Legacy Lodge - Paris, France

#### 1.2 Instalación de Dependencias
```bash
pip install langchain langchain-google-genai langchain-community chromadb
pip install langchain-huggingface sentence-transformers
```

---

### Fase 2: Creación del Vector Store

#### 2.1 Archivo: `util/vectorstore_builder.py`

**Funcionalidad inicial**:
```python
def build_vectorstore_simple() -> Chroma:
    # Cargar JSON, Markdown (hotel_details.md, hotel_rooms.md)
    # Text splitting: chunk_size=1000, chunk_overlap=200
    # Embeddings: GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # Persistencia: vectorstore/chroma_db/
```

**Resultado inicial**: 1,427 documentos embedidos (con HuggingFace)

#### 2.2 Evolución de Modelos de Embeddings

| Intento | Modelo | Resultado | Problema |
|---------|--------|-----------|----------|
| 1 | Google `embedding-001` | ❌ Error | Cuota excedida |
| 2 | HuggingFace `all-MiniLM-L6-v2` | ✅ Funciona | Sin cuotas, 1,427 docs |
| 3 | Google `text-embedding-004` | ✅ Funciona | Sin errores de cuota, 289 docs |

**Comando para cambiar modelo**:
```python
# Cambio en vectorstore_builder.py
USE_HUGGINGFACE = False  # True para HuggingFace, False para Gemini
embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
```

---

### Fase 3: Implementación del RAG Chain

#### 3.1 Archivo: `agents/hotel_rag_agent.py`

**Componentes principales**:

1. **Vector Store Retriever**
```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Top 5 documentos relevantes
)
```

2. **Prompt Template**
```python
prompt_template = """You are a helpful hotel assistant...
Context: {context}
Question: {question}
Instructions:
- Be accurate and specific
- Format responses in markdown
..."""
```

3. **RAG Chain (LCEL)**
```python
_rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

#### 3.2 Configuración de LLMs

**Prioridad de LLMs** (de mayor a menor):
1. **Gemini `gemini-2.5-flash-lite`** - Primaria, rápida, económica
2. **Ollama `llama3.2:1b`** - Fallback local, sin cuotas

**Instalación de Ollama** (para fallback):
```bash
curl -fsSL https://ollama.com/install.sh | sudo sh
ollama pull llama3.2:1b
```

---

### Fase 4: Integración con WebSocket API

#### 4.1 Modificaciones en `main.py`

**Prioridad de agentes**:
```python
if RAG_AGENT_AVAILABLE:
    # Use Exercise 1 RAG agent (mejor opción)
    response_content = await answer_hotel_question_rag(user_query)
elif EXERCISE_0_AVAILABLE:
    # Fallback a Exercise 0
    response_content = answer_hotel_question(user_query)
else:
    # Hardcoded responses
    response_content = find_matching_response(user_query)
```

**Logs de carga**:
```
✅ Exercise 1 RAG agent loaded successfully with 183 documents
```

---

### Fase 5: Testing y Validación

#### 5.1 Queries de Prueba

**Archivo**: `test_queries.txt` (20 consultas)

Categorías:
- **Hotel Details** (6): Direcciones, meal charges, descuentos
- **Room Pricing** (4): Precios por temporada
- **Room Distribution** (4): Cantidad de habitaciones
- **Complex Comparison** (4): Comparaciones entre hoteles
- **Aggregate** (2): Consultas agregadas

#### 5.2 Resultados Iniciales

**Queries exitosas**:
- ✅ "What is the full address of Obsidian Tower?"
- ✅ "What are the meal charges for Half Board in Royal Sovereign?"
- ✅ "List all hotels in Paris"

**Query problemática**:
- ❌ "What is the discount for extra bed in Grand Victoria?"
  - **Problema**: El bot no encontraba la información
  - **Causa**: Mismatch semántico entre "discount" y "ExtraBedChargePercentage"

---

## 🚀 Mejoras Implementadas

### Problema Identificado

**Query**: "What is the discount for extra bed in Grand Victoria?"  
**Esperado**: 21% (ExtraBedChargePercentage)  
**Resultado**: "Information not available"

**Análisis del problema**:
1. La pregunta usa "**discount**" (descuento)
2. El dato en JSON es "**ExtraBedChargePercentage**" (cargo/recargo)
3. El embedding no captura la relación semántica entre ambos términos

---

### Mejora 1: Enriquecimiento de Documentos JSON

**Objetivo**: Agregar descripciones en lenguaje natural con múltiples formas de referirse al mismo concepto.

**Implementación** en `vectorstore_builder.py`:

```python
# Antes: Solo cargar JSON crudo
json_loader = JSONLoader(file_path=str(json_path), jq_schema=".Hotels[]")
docs += json_loader.load()

# Después: Enriquecer con descripciones
for hotel in hotels_data.get('Hotels', []):
    enriched_text = f"""
=== Hotel: {hotel_name} ===
Location: {city}, {country}
Full Address: {address}, {city}, {zip}, {country}

**Pricing Policies and Charges:**
- Extra Bed Charge: {extra_bed}% surcharge/additional charge for extra bed
- Extra Bed Surcharge: {extra_bed}% extra cost when adding a bed
- Occupancy Discount: {occupancy_discount}% discount for reduced occupancy/fewer guests
- Promotion Discount: {promo_discount}% discount on promotional prices

**Meal Plan Charges (Price Multipliers):**
- Room Only: {room_only}x base price
- Half Board: {half_board}x base price
...

**Available Rooms:**
- Room 01-001: Premium Triple, 3 guests, Off-season: €233.59, Peak-season: €399.44
...

**Raw Data:**
{json.dumps(hotel, ensure_ascii=False, indent=2)}
"""
    docs.append(Document(page_content=enriched_text, metadata={...}))
```

**Beneficios**:
- ✅ Múltiples términos para el mismo concepto ("charge", "surcharge", "extra cost")
- ✅ Formato legible que mejora la recuperación semántica
- ✅ Mantiene JSON crudo para datos exactos

---

### Mejora 2: Prompt con Guía de Terminología

**Objetivo**: Ayudar al LLM a interpretar preguntas con terminología flexible.

**Implementación** en `hotel_rag_agent.py`:

```python
prompt_template = """You are a helpful hotel assistant...

**IMPORTANT - Data Field Terminology Guide:**
- When asked about "discount for extra bed" → Look for "ExtraBedChargePercentage" 
  or "Extra Bed Charge" (this is a CHARGE/SURCHARGE, not a discount)
- When asked about "discount for fewer guests" → Look for "OccupancyBaseDiscountPercentage"
- When asked about "promotion discount" → Look for "PromotionPriceDiscount"
- When asked about "meal charges" → Look for "MealPlanPrices"
- Be flexible with terminology - "charge", "surcharge", "additional cost" are synonyms

Context: {context}
Question: {question}

Instructions:
- Interpret the question flexibly - look for semantically related fields
- Be accurate and specific, referencing hotel names and details
...
"""
```

**Beneficios**:
- ✅ El LLM entiende relaciones semánticas
- ✅ Maneja variaciones de terminología
- ✅ Mejora interpretación de queries ambiguas

---

### Mejora 3: Optimización de Chunks

**Cambios en `vectorstore_builder.py`**:

```python
# Antes
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=200
)

# Después
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,   # +100% más contexto
    chunk_overlap=400  # +100% más overlap
)
```

**Beneficios**:
- ✅ Mayor contexto por chunk
- ✅ Mejor recuperación de información relacionada
- ✅ Menos fragmentación de documentos importantes

---

### Mejora 4: Organización del Vector Store

**Cambio de ubicación**:
```bash
# Antes
ai_agents_hospitality-api/vectorstore/chroma_db/

# Después
bookings-db/vectorstore/chroma_db/
```

**Beneficios**:
- ✅ Centraliza gestión de bases de datos (PostgreSQL + ChromaDB)
- ✅ Estructura más lógica del proyecto
- ✅ Facilita backups y versionado

**Actualización en `.gitignore`**:
```
# ChromaDB vector store
bookings-db/vectorstore/
ai_agents_hospitality-api/vectorstore/
```

---

## 📊 Resultados Finales

### Métricas del Sistema

| Métrica | Valor |
|---------|-------|
| **Hoteles en base de datos** | 10 |
| **Documentos embedidos** | 183 |
| **Modelo de embeddings** | Google `text-embedding-004` |
| **Modelo LLM principal** | Gemini `gemini-2.5-flash-lite` |
| **Chunk size** | 2000 caracteres |
| **Chunk overlap** | 400 caracteres |
| **Top-K retrieval** | 5 documentos |
| **Tiempo de respuesta** | 1-3 segundos (Gemini) |

### Validación de Queries

**Script de testing**: `test_rag_queries.py`

**Resultados de pruebas**:

| Query | Esperado | Resultado | Status |
|-------|----------|-----------|--------|
| Full address of Obsidian Tower | 43321 Brittany Bypass, Cannes, 84311, France | ✅ Correcto | ✅ |
| Meal charges Half Board Royal Sovereign | 1.42x multiplier | ✅ Correcto | ✅ |
| List hotels in Paris | 4 hotels (Noble Abode, Imperial Crown, Royal Sovereign, Legacy Lodge) | ✅ Correcto | ✅ |
| Extra bed charge Grand Victoria | 21% | ✅ Correcto (después de mejoras) | ✅ |
| Hotels in France | 10 hotels | ✅ Correcto | ✅ |

**Ejemplo de respuesta mejorada**:

**Query**: "What is the discount for extra bed in Grand Victoria?"

**Respuesta del bot**:
```
The Grand Victoria hotel charges a 21% surcharge for an extra bed. 
This is referred to as "Extra Bed Charge" and "Extra Bed Surcharge" 
in their pricing policies.
```

---

## 🔧 Configuración Técnica

### Archivo: `config/agent_config.yaml`

```yaml
provider: gemini
model: gemini-2.5-flash-lite
temperature: 0
api_key: ${AI_AGENTIC_API_KEY}
```

### Variables de Entorno

```bash
export AI_AGENTIC_API_KEY=your-gemini-api-key-here
# Opcional si usas HuggingFace para embeddings en lugar de Gemini:
# export HUGGINGFACE_API_TOKEN=your-hf-token-here
```

### Estructura Final del Proyecto

```
agentic_ai_PoC_prj_hospitality/
├── ai_agents_hospitality-api/
│   ├── agents/
│   │   ├── hotel_simple_agent.py      # Exercise 0
│   │   └── hotel_rag_agent.py         # Exercise 1 ✅
│   ├── util/
│   │   └── vectorstore_builder.py     # Vector store con mejoras ✅
│   ├── config/
│   │   └── agent_config.yaml
│   ├── test_queries.txt               # 20 queries de prueba ✅
│   ├── test_rag_queries.py            # Script de validación ✅
│   └── main.py                        # WebSocket API integrado ✅
├── bookings-db/
│   ├── vectorstore/
│   │   └── chroma_db/                 # 183 documentos persistidos ✅
│   ├── output_files/
│   │   └── hotels/
│   │       ├── hotels.json            # 10 hoteles
│   │       ├── hotel_details.md
│   │       └── hotel_rooms.md
│   └── config/
│       └── generate_hotels_param.yaml # num_of_hotels: 10
└── .gitignore                         # Excluye vectorstore/ ✅
```

---

## 📚 Lecciones Aprendidas

### 1. Gestión de Cuotas de API

**Problema**: Google Gemini tiene límites (20 requests/día para algunos modelos)

**Solución implementada**:
- Embeddings: Usar `text-embedding-004` (sin problemas de cuota)
- LLM: Gemini como principal + Ollama como fallback local
- Vector store persistente: Evita regenerar embeddings constantemente

### 2. Importancia del Enriquecimiento de Datos

**Insight**: El RAG funciona mejor cuando los documentos embedidos incluyen:
- Múltiples formas de referirse al mismo concepto
- Contexto en lenguaje natural
- Datos estructurados + descripciones legibles

### 3. Optimización de Chunks

**Regla general**:
- Chunks pequeños (500-1000): Mejor para búsquedas específicas
- Chunks grandes (1500-2500): Mejor para contexto amplio
- Overlap alto (20-30%): Previene pérdida de información en fronteras

### 4. Prompts Inteligentes

**El prompt debe**:
- Explicar terminología específica del dominio
- Guiar al LLM en interpretación flexible
- Incluir instrucciones de formato de salida

---

## 🔄 Mantenimiento y Actualización

### Cuándo Regenerar el Vector Store

**Necesario borrar `chroma_db/`** en estos casos:
1. ✅ Cambio de modelo de embeddings
2. ✅ Modificación del contenido fuente (JSON, MD)
3. ✅ Cambio en chunk_size o overlap
4. ✅ Actualización de datos de hoteles

**NO necesario** en estos casos:
- ❌ Cambio de modelo LLM (Gemini, Ollama)
- ❌ Modificación del prompt
- ❌ Ajustes de parámetros de retrieval (k=5→10)

### Comando de Regeneración

```bash
# Borrar vector store
rm -rf bookings-db/vectorstore/chroma_db/*

# Reiniciar servidor (regenera automáticamente)
cd ai_agents_hospitality-api
source ../.venv/bin/activate
python main.py
```

---

## ✅ Checklist de Completitud

### Exercise 1: Hotel Details with RAG

- [x] Vector store poblado con hotel y room data
- [x] RAG chain que retrieves información relevante
- [x] Agente que formatea respuestas apropiadamente
- [x] Integración con WebSocket API
- [x] Responde correctamente a queries de hotel details
- [x] Retrieves información precisa de room pricing
- [x] Maneja queries sobre meal plans y discounts
- [x] Provee respuestas en formato markdown
- [x] Performance < 10 segundos por query
- [x] Mejoras implementadas para problemas de terminología

---

## 🎯 Próximos Pasos

### Exercise 2: Booking Analytics with SQL Agent

**Objetivo**: Implementar SQL agent para analytics sobre PostgreSQL

**Componentes a implementar**:
1. Conexión a PostgreSQL (bookings database)
2. SQL agent con LangChain
3. Cálculos de métricas:
   - Bookings count
   - Occupancy rate
   - Total revenue
   - RevPAR (Revenue Per Available Room)
4. Integración con WebSocket API

---

## 📖 Referencias

- **LangChain Documentation**: https://python.langchain.com/
- **LangChain RAG Tutorial**: https://python.langchain.com/docs/tutorials/rag/
- **ChromaDB Documentation**: https://docs.trychroma.com/
- **Google Gemini API**: https://ai.google.dev/docs
- **Ollama**: https://ollama.com/

---

**Documento generado**: Diciembre 18, 2025  
**Autor**: Workshop Implementation Team  
**Versión**: 1.0
