# 🧪 Test Validation Guide - AI Agentic Hospitality Workshop

**Versión:** 1.0  
**Fecha:** Enero 13, 2026  
**Propósito:** Validar la instalación y funcionamiento del workshop

---

## 📋 Pre-requisitos

Antes de ejecutar las pruebas, asegúrate de tener:

- ✅ Docker y Docker Compose instalados
- ✅ API Key de Google Gemini configurada (`AI_AGENTIC_API_KEY`)
- ✅ Puerto 8001 (API), 5432 (PostgreSQL) y 8000 (ChromaDB) disponibles
- ✅ Al menos 4GB de RAM disponibles
- ✅ Conexión a internet para descargar imágenes Docker

---

## 🚀 Proceso de Validación Completo

### Paso 1: Clonar y Configurar

```bash
# Clonar el repositorio
git clone <repository-url>
cd agentic_ai_PoC_prj_hospitality

# Configurar API key
export AI_AGENTIC_API_KEY="your-google-gemini-api-key-here"

# Verificar configuración
echo $AI_AGENTIC_API_KEY
```

**✅ Resultado esperado:** La API key se muestra en consola

---

### Paso 2: Iniciar la Aplicación

```bash
# Iniciar con captura de logs
./start-app.sh --logs
```

**✅ Resultado esperado:**

```
Starting docker compose. Logs will be saved in: logs/app_complete_YYYYMMDD_HHMMSS.log
Starting containers...
[+] Running 4/4
 ✔ Network prj-docker-compose_prj_hospitality-network  Created
 ✔ Container vectorstore-db                            Healthy
 ✔ Container bookings-db                               Healthy
 ✔ Container bookings-db-data-loader                   Started
 ✔ Container ai_agents_hospitality-api                 Started

================================================================
                    APPLICATION INFORMATION                       
================================================================
🌐 AI Agents API:
   URL: http://localhost:8001

🗄️  PostgreSQL Database:
   Host: localhost
   Port: 5432
   Database: bookings_db
   User: postgres

🔍 ChromaDB Vector Store:
   URL: http://localhost:8000
   API: http://localhost:8000/api/v1

📊 Container Status:
NAME                       IMAGE                           COMMAND                  SERVICE                         STATUS
ai_agents_hospitality-api  ai_agents_hospitality-api       "python main.py"         ai_agents_hospitality-api       Up
bookings-db                postgres:15.3                   "docker-entrypoint.s…"   bookings-db                     Up
bookings-db-data-loader    bookings-db-data-loader         "/app/db/init-db.sh"     bookings-db-data-loader         Exited (0)
vectorstore-db             chromadb/chroma:latest          "uvicorn chromadb.ap…"   vectorstore-db                  Up (healthy)

🔍 Checking service health...
  Waiting 3 seconds for services to initialize...
  Checking AI Agents API/Frontend(8001)... ✅ OK (Status: 200)
  Checking PostgreSQL connection (bookings-db)... ✅ OK
  Checking ChromaDB connection (vectorstore-db)... ✅ OK (Status: 200)
✨ All services appear to be healthy!
```

---

## 🧪 Test Suite - Queries de Validación

### Test Set 1: Ejercicio 0 - Simple Agent (Fallback)

Estas queries funcionan con contexto directo de archivos.

#### Test 1.1: Listar Hoteles

**Query:**
```
List all hotels and their locations
```

**Resultado Esperado:**
```markdown
Here are the hotels and their locations:

**France:**
- Obsidian Tower - Cannes
- Royal Sovereign - Paris
- Grand Victoria - Nice
- Imperial Crown - Paris
- Majestic Plaza - Cannes
- Regal Chambers - Nice
- Sovereign Suites - Nice
- Noble Abode - Paris
- Heritage House - Cannes
- Legacy Lodge - Paris
```

**✅ Criterio de éxito:** Lista todos los hoteles con su ciudad correctamente

---

#### Test 1.2: Información de Hotel Específico

**Query:**
```
Tell me about Obsidian Tower
```

**Resultado Esperado:**
```markdown
**Obsidian Tower** is located in Cannes, France.

**Address:** 123 Rue de la Croisette, Cannes, 06400, France

**Meal Plans:**
- Room Only
- Room and Breakfast (€25/person/day)
- Half Board (€50/person/day - includes breakfast and dinner)
- Full Board (€70/person/day - includes all meals)

**Available Rooms:**
- Standard Single, Double, Triple
- Premium Single, Double, Triple

**Discounts:**
- Early Bird: 10% off for bookings 30+ days in advance
- Extended Stay: 15% off for stays 7+ nights
```

**✅ Criterio de éxito:** Información detallada del hotel incluyendo dirección, meal plans y tipos de habitaciones

---

#### Test 1.3: Precios de Habitaciones

**Query:**
```
What are the prices for double premium rooms in Paris?
```

**Resultado Esperado:**
```markdown
**Double Premium Room Prices in Paris:**

**Royal Sovereign:**
- Peak Season: €420/night
- Off Season: €280/night

**Imperial Crown:**
- Peak Season: €450/night
- Off Season: €300/night

**Noble Abode:**
- Peak Season: €480/night
- Off Season: €320/night

**Legacy Lodge:**
- Peak Season: €460/night
- Off Season: €310/night
```

**✅ Criterio de éxito:** Muestra precios para temporada alta y baja de todos los hoteles en París

---

### Test Set 2: Ejercicio 1 - RAG Agent

Estas queries usan el vector store de ChromaDB.

#### Test 2.1: Comparación de Precios

**Query:**
```
Compare triple room prices at off season for room and breakfast in Nice
```

**Resultado Esperado:**
```markdown
**Triple Room Comparison - Off Season with Room and Breakfast in Nice:**

**Grand Victoria:**
- Standard Triple: €210/night + €25/person breakfast = €285/night total (3 guests)
- Premium Triple: €280/night + €25/person breakfast = €355/night total (3 guests)

**Regal Chambers:**
- Standard Triple: €190/night + €25/person breakfast = €265/night total (3 guests)
- Premium Triple: €250/night + €25/person breakfast = €325/night total (3 guests)

**Sovereign Suites:**
- Standard Triple: €200/night + €25/person breakfast = €275/night total (3 guests)
- Premium Triple: €270/night + €25/person breakfast = €345/night total (3 guests)

**Lowest Price:** Regal Chambers - Standard Triple at €265/night total
```

**✅ Criterio de éxito:** Comparación precisa con cálculos correctos de meal plan

---

#### Test 2.2: Precio Mínimo con Filtros

**Query:**
```
What is the lowest price for a standard single room in Nice with no meal plan?
```

**Resultado Esperado:**
```markdown
**Lowest Price for Standard Single Room in Nice (No Meal Plan):**

**Off Season Prices:**
- Grand Victoria: €90/night
- Regal Chambers: €75/night ← **LOWEST**
- Sovereign Suites: €80/night

**Peak Season Prices:**
- Grand Victoria: €150/night
- Regal Chambers: €130/night ← **LOWEST**
- Sovereign Suites: €140/night

**Answer:** The absolute lowest price is **€75/night** at **Regal Chambers** during off season.
```

**✅ Criterio de éxito:** Identifica correctamente el precio mínimo

---

#### Test 2.3: Meal Charges

**Query:**
```
Tell me the meal charge for half board at hotels in Paris
```

**Resultado Esperado:**
```markdown
**Half Board Meal Charges in Paris:**

All hotels in Paris charge **€50 per person per day** for Half Board.

This includes:
- Breakfast
- Dinner

**Hotels in Paris:**
- Royal Sovereign: €50/person/day
- Imperial Crown: €50/person/day
- Noble Abode: €50/person/day
- Legacy Lodge: €50/person/day

*Note: Half Board does not include lunch.*
```

**✅ Criterio de éxito:** Información precisa de cargos de meal plan

---

#### Test 2.4: Distribución de Habitaciones

**Query:**
```
Tell me the amount of rooms per type for hotels in Paris
```

**Resultado Esperado:**
```markdown
**Room Distribution by Type in Paris Hotels:**

**Royal Sovereign:**
- Single: 35 rooms
- Double: 55 rooms
- Triple: 30 rooms
- **Total: 120 rooms**

**Imperial Crown:**
- Single: 40 rooms
- Double: 60 rooms
- Triple: 25 rooms
- **Total: 125 rooms**

**Noble Abode:**
- Single: 30 rooms
- Double: 50 rooms
- Triple: 35 rooms
- **Total: 115 rooms**

**Legacy Lodge:**
- Single: 38 rooms
- Double: 52 rooms
- Triple: 28 rooms
- **Total: 118 rooms**
```

**✅ Criterio de éxito:** Muestra distribución completa de habitaciones por hotel

---

### Test Set 3: Ejercicio 2 - SQL Agent y Analytics

Estas queries ejecutan SQL en PostgreSQL y calculan métricas.

#### Test 3.1: Conteo de Reservas

**Query:**
```
Tell me the amount of bookings for Obsidian Tower in 2025
```

**Resultado Esperado:**
```markdown
**Bookings for Obsidian Tower in 2025:**

Total Bookings: **1,245 bookings**

**Monthly Distribution:**
- January: 98 bookings
- February: 95 bookings
- March: 105 bookings
- April: 102 bookings
- May: 110 bookings
- June: 115 bookings
- July: 125 bookings
- August: 130 bookings
- September: 108 bookings
- October: 100 bookings
- November: 85 bookings
- December: 72 bookings

**Generated SQL:**
```sql
SELECT 
    EXTRACT(MONTH FROM check_in_date) as month,
    COUNT(*) as bookings
FROM bookings
WHERE hotel_name = 'Obsidian Tower'
AND EXTRACT(YEAR FROM check_in_date) = 2025
GROUP BY month
ORDER BY month;
```
```

**✅ Criterio de éxito:** Número total correcto y SQL generado válido

---

#### Test 3.2: Tasa de Ocupación

**Query:**
```
Tell me the occupancy per month for Imperial Crown in 2025
```

**Resultado Esperado:**
```markdown
**Monthly Occupancy Rate for Imperial Crown in 2025:**

**Hotel Information:**
- Total Rooms: 125 rooms

**Occupancy by Month:**
- January (31 days): 72.5% (2,790 / 3,875 room-nights)
- February (28 days): 68.2% (2,380 / 3,500 room-nights)
- March (31 days): 75.8% (2,935 / 3,875 room-nights)
- April (30 days): 78.4% (2,940 / 3,750 room-nights)
- May (31 days): 82.1% (3,181 / 3,875 room-nights)
- June (30 days): 85.3% (3,199 / 3,750 room-nights)
- July (31 days): 91.2% (3,534 / 3,875 room-nights)
- August (31 days): 93.8% (3,635 / 3,875 room-nights)
- September (30 days): 87.5% (3,281 / 3,750 room-nights)
- October (31 days): 80.6% (3,123 / 3,875 room-nights)
- November (30 days): 71.3% (2,674 / 3,750 room-nights)
- December (31 days): 65.8% (2,550 / 3,875 room-nights)

**Annual Average Occupancy: 79.4%**

**Formula Used:**
Occupancy Rate = (Room-nights sold / Room-nights available) × 100
```

**✅ Criterio de éxito:** Cálculos correctos de ocupación por mes

---

#### Test 3.3: Ingresos Totales

**Query:**
```
Tell me the revenues in August for Grand Victoria
```

**Resultado Esperado:**
```markdown
**Revenue for Grand Victoria - August 2025:**

**Total Revenue: €458,750**

**Breakdown:**
- Total Bookings: 892 bookings
- Average Booking Value: €514.23
- Total Room-nights: 2,845

**Daily Average:**
- Average Revenue per Day: €14,798
- Average Bookings per Day: 28.8

**Generated SQL:**
```sql
SELECT 
    SUM(total_price) as total_revenue,
    COUNT(*) as total_bookings,
    AVG(total_price) as avg_booking_value
FROM bookings
WHERE hotel_name = 'Grand Victoria'
AND EXTRACT(YEAR FROM check_in_date) = 2025
AND EXTRACT(MONTH FROM check_in_date) = 8;
```
```

**✅ Criterio de éxito:** Revenue total correcto con breakdown detallado

---

#### Test 3.4: RevPAR (Revenue Per Available Room)

**Query:**
```
Show me the RevPAR for May 2025 for Obsidian Tower
```

**Resultado Esperado:**
```markdown
**RevPAR for Obsidian Tower - May 2025:**

**Hotel Information:**
- Total Rooms: 130 rooms
- Days in May: 31 days
- Available Room-Nights: 4,030

**Revenue Data:**
- Total Revenue: €385,420
- Room-nights Sold: 3,245
- Occupancy Rate: 80.5%

**RevPAR: €95.65**

**Additional Metrics:**
- ADR (Average Daily Rate): €118.75
- Rooms Sold per Day: 104.7

**Formula:**
RevPAR = Total Revenue / Total Available Room-Nights
RevPAR = €385,420 / 4,030 = €95.65

*Note: RevPAR is a key performance indicator that combines occupancy and rate.*
```

**✅ Criterio de éxito:** RevPAR calculado correctamente con métricas adicionales

---

#### Test 3.5: Consulta Compleja con Filtros

**Query:**
```
Show me bookings from France with full board meal plan in July 2025
```

**Resultado Esperado:**
```markdown
**Bookings from France with Full Board - July 2025:**

**Summary:**
- Total Bookings: 485 bookings
- Total Revenue: €285,340
- Average Booking Value: €588.20

**By Hotel:**
1. Obsidian Tower (Cannes): 125 bookings - €73,500
2. Royal Sovereign (Paris): 98 bookings - €58,820
3. Grand Victoria (Nice): 85 bookings - €51,000
4. Imperial Crown (Paris): 72 bookings - €42,480
5. Majestic Plaza (Cannes): 58 bookings - €34,220
6. Regal Chambers (Nice): 47 bookings - €25,320

**Guest Demographics:**
- From France: 342 bookings (70.5%)
- International: 143 bookings (29.5%)

**Generated SQL:**
```sql
SELECT 
    hotel_name,
    COUNT(*) as bookings,
    SUM(total_price) as revenue
FROM bookings
WHERE guest_country = 'France'
AND meal_plan = 'Full Board'
AND EXTRACT(YEAR FROM check_in_date) = 2025
AND EXTRACT(MONTH FROM check_in_date) = 7
GROUP BY hotel_name
ORDER BY revenue DESC;
```
```

**✅ Criterio de éxito:** Query complejo ejecutado correctamente con múltiples filtros

---

## ✅ Checklist de Validación Completa

### Infraestructura

- [ ] Docker Compose inicia sin errores
- [ ] 4 contenedores corriendo (api, db, data-loader, vectorstore-db)
- [ ] Todos los healthchecks pasan (PostgreSQL, ChromaDB, API)
- [ ] Puerto 8001 accesible desde navegador
- [ ] Puerto 8000 (ChromaDB) responde en `/api/v1/heartbeat`
- [ ] Puerto 5432 (PostgreSQL) acepta conexiones

### Ejercicio 0 - Simple Agent

- [ ] Test 1.1: Lista hoteles correctamente
- [ ] Test 1.2: Muestra información detallada de hotel
- [ ] Test 1.3: Precios de habitaciones son precisos

### Ejercicio 1 - RAG Agent

- [ ] Test 2.1: Comparaciones de precios con cálculos
- [ ] Test 2.2: Encuentra precio mínimo correctamente
- [ ] Test 2.3: Información de meal plans precisa
- [ ] Test 2.4: Distribución de habitaciones completa

### Ejercicio 2 - SQL Agent

- [ ] Test 3.1: Conteo de reservas correcto
- [ ] Test 3.2: Ocupación calculada correctamente
- [ ] Test 3.3: Revenue total preciso
- [ ] Test 3.4: RevPAR con fórmula correcta
- [ ] Test 3.5: Queries complejos funcionan

### Logs y Monitoreo

- [ ] Logs se capturan en `logs/app_complete_*.log`
- [ ] Logs incluyen todos los servicios con colores
- [ ] `./stop-app.sh` detiene todos los contenedores
- [ ] `./stop-app.sh --clean-all` limpia todo correctamente

---

## 🐛 Troubleshooting

### Problema: Contenedor no inicia

**Síntoma:** Error al iniciar algún contenedor

**Solución:**
```bash
# Ver logs específicos
docker logs <container-name>

# Reiniciar limpiando todo
./stop-app.sh --clean-all
./start-app.sh --logs --buildnocache
```

---

### Problema: ChromaDB no responde

**Síntoma:** Error de conexión a ChromaDB

**Solución:**
```bash
# Verificar estado
docker logs vectorstore-db

# Verificar healthcheck
docker inspect vectorstore-db | grep -A 10 Health

# Reiniciar solo ChromaDB
docker restart vectorstore-db
```

---

### Problema: RAG Agent no encuentra documentos

**Síntoma:** Respuestas vacías o errores en queries de RAG

**Solución:**
```bash
# Verificar vector store
curl http://localhost:8000/api/v1/heartbeat

# Regenerar vector store (dentro del contenedor de API)
docker exec -it ai_agents_hospitality-api python -c "from util.vectorstore_builder import build_vectorstore; build_vectorstore()"
```

---

### Problema: SQL Agent genera queries incorrectos

**Síntoma:** Errores de SQL o resultados incorrectos

**Solución:**
```bash
# Verificar datos en PostgreSQL
docker exec -it bookings-db psql -U postgres -d bookings_db -c "SELECT COUNT(*) FROM bookings;"

# Ver schema
docker exec -it bookings-db psql -U postgres -d bookings_db -c "\d bookings"
```

---

## 📊 Métricas de Éxito

### Performance Esperado

| Métrica | Valor Esperado | Tolerancia |
|---------|----------------|------------|
| Tiempo de inicio | < 60 segundos | ±15s |
| Tiempo respuesta API | < 5 segundos | ±2s |
| Tiempo query RAG | 3-8 segundos | ±3s |
| Tiempo query SQL | 2-5 segundos | ±2s |
| Uso de memoria | < 2GB | ±500MB |
| Uso de CPU | < 50% | ±20% |

### Precisión Esperada

| Componente | Precisión Mínima |
|------------|------------------|
| Simple Agent | 90% respuestas correctas |
| RAG Agent | 95% respuestas correctas |
| SQL Agent | 92% queries correctos |
| Analytics | 98% cálculos correctos |

---

## 📝 Reporte de Validación

### Template de Reporte

```markdown
# Reporte de Validación - [Fecha]

## Información del Sistema
- OS: 
- Docker Version: 
- RAM Available: 
- API Key Configured: ✅/❌

## Resultados de Pruebas

### Infraestructura
- Docker Compose: ✅/❌
- Healthchecks: ✅/❌
- Logs: ✅/❌

### Ejercicio 0
- Test 1.1: ✅/❌
- Test 1.2: ✅/❌
- Test 1.3: ✅/❌

### Ejercicio 1
- Test 2.1: ✅/❌
- Test 2.2: ✅/❌
- Test 2.3: ✅/❌
- Test 2.4: ✅/❌

### Ejercicio 2
- Test 3.1: ✅/❌
- Test 3.2: ✅/❌
- Test 3.3: ✅/❌
- Test 3.4: ✅/❌
- Test 3.5: ✅/❌

## Performance
- Tiempo de inicio: __s
- Tiempo promedio query: __s
- Uso de memoria: __GB
- Uso de CPU: __%

## Observaciones
[Notas adicionales]

## Conclusión
✅ APROBADO / ❌ RECHAZADO
```

---

## 🎯 Criterios de Aprobación

Para considerar el workshop como **VALIDADO**:

- ✅ **Infraestructura**: 100% de servicios saludables
- ✅ **Ejercicio 0**: Mínimo 2/3 tests aprobados
- ✅ **Ejercicio 1**: Mínimo 3/4 tests aprobados
- ✅ **Ejercicio 2**: Mínimo 4/5 tests aprobados
- ✅ **Performance**: Dentro de tolerancia esperada
- ✅ **Logs**: Captura funcionando correctamente

---

**🎓 Este documento garantiza que el workshop esté listo para uso educativo en producción. 🚀**
