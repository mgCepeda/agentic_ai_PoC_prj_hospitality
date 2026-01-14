# 🚀 Quick Start Guide - Local Development Setup

**Para desarrolladores con PostgreSQL local y entorno virtual Python**

---

## 🎯 Método Recomendado: Script All-in-One

El script `workshop.sh` combina todos los pasos en comandos simples:

```bash
# Iniciar todo (detiene PostgreSQL local, activa venv, inicia Docker)
./workshop.sh start

# Iniciar con logs en vivo
./workshop.sh start --logs

# Ver estado de servicios
./workshop.sh status

# Ejecutar validación
./workshop.sh validate

# Ver logs
./workshop.sh logs

# Detener todo (para Docker, restaura PostgreSQL local)
./workshop.sh stop

# Limpieza completa
./workshop.sh clean --all
```

**Ventajas:**
- ✅ Un solo comando para todo
- ✅ Ejecuta automáticamente pre-start checks (detiene PostgreSQL local, verifica API key)
- ✅ Maneja automáticamente post-stop
- ✅ Comandos memorables y consistentes
- ✅ Mensajes claros de estado
- ✅ Help integrado: `./workshop.sh help`

---

## 📋 Método Manual: Scripts Individuales

Si prefieres control paso a paso:

```
pre-start.sh → start-app.sh → [Desarrollo/Testing] → stop-app.sh → post-stop.sh
```

---

## 1️⃣ Preparación del Entorno (Una sola vez o cuando cambies de sesión)

### Script: `pre-start.sh`

Este script prepara tu entorno local para ejecutar los servicios Docker:

```bash
./pre-start.sh
```

**¿Qué hace?**

1. **Detiene PostgreSQL local**
   - Verifica si hay un PostgreSQL corriendo en el puerto 5432
   - Lo detiene con `sudo systemctl stop postgresql`
   - Esto libera el puerto para el contenedor Docker de PostgreSQL

2. **Activa el entorno virtual Python**
   - Busca `.venv/` en el directorio del proyecto
   - Lo activa automáticamente
   - Si no existe, lo crea automáticamente

3. **Instala dependencias (opcional)**
   - Pregunta si quieres instalar/actualizar dependencias desde `requirements.txt`
   - Útil cuando hay nuevas dependencias

4. **Verifica API Key**
   - Confirma que `AI_AGENTIC_API_KEY` está configurada
   - Si no está, muestra instrucciones para configurarla

**Salida esperada:**

```
╔═══════════════════════════════════════════════════════════════╗
║        🔧  PRE-START ENVIRONMENT PREPARATION  🔧              ║
╚═══════════════════════════════════════════════════════════════╝

🔍 Step 1: Checking for local PostgreSQL service...
✅ Local PostgreSQL stopped successfully

🐍 Step 2: Setting up Python virtual environment...
✅ Virtual environment activated
   Python: /home/marina/workshop/agentic_ai_PoC_prj_hospitality/.venv/bin/python

📦 Step 3: Checking Python dependencies...
   Found requirements.txt
   Install/update dependencies? (y/N): n
   Skipped dependency installation

🔑 Step 4: Checking environment variables...
✅ AI_AGENTIC_API_KEY is set
   Key: sk-proj-...xyz

╔═══════════════════════════════════════════════════════════════╗
║                  ✅  ENVIRONMENT READY  ✅                     ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 2️⃣ Iniciar Aplicación Docker

### Script: `start-app.sh`

Una vez preparado el entorno, inicia los servicios Docker:

```bash
# Inicio normal
./start-app.sh

# Inicio con logs en vivo (recomendado para debugging)
./start-app.sh --logs
```

**¿Qué hace?**

1. Verifica si hay contenedores corriendo
2. Comprueba variables de entorno necesarias
3. Inicia Docker Compose con todos los servicios:
   - PostgreSQL (bookings-db)
   - ChromaDB (vectorstore-db)
   - Data Loader (carga datos iniciales)
   - AI Agents API (puerto 8001)

4. Monitorea la salud de los servicios
5. Muestra información de acceso
6. (Opcional) Captura logs en tiempo real

**Servicios Iniciados:**

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **PostgreSQL** | 5432 | Base de datos de reservas |
| **ChromaDB** | 8000 | Vector store para RAG |
| **AI Agents API** | 8001 | API WebSocket para agentes |

**Acceso a la aplicación:**

```
🌐 Web Interface: http://localhost:8001
📡 WebSocket API: ws://localhost:8001/ws
🗄️ PostgreSQL: localhost:5432
🔍 ChromaDB: http://localhost:8000
```

---

## 3️⃣ Desarrollo y Testing

Con los servicios corriendo, puedes:

### A) Usar la Interfaz Web

```bash
# Abrir en navegador
xdg-open http://localhost:8001
```

### B) Ejecutar Tests

```bash
# Validación automatizada completa
./validate.sh

# Tests específicos de ejercicios
cd ai_agents_hospitality-api
python test_exercise_0.py  # Simple Agent
python test_rag_queries.py # RAG Agent
python test_sql_agent.py   # SQL Agent
```

### C) Consultar Logs

```bash
# Ver logs capturados (si usaste --logs)
tail -f logs/app_complete_*.log

# Ver logs de un servicio específico
docker logs -f ai_agents_hospitality-api
docker logs -f bookings-db
docker logs -f vectorstore-db
```

### D) Acceder a las Bases de Datos

**PostgreSQL:**

```bash
docker exec -it bookings-db psql -U admin -d hospitality_db
```

**ChromaDB:**

```bash
# API REST
curl http://localhost:8000/api/v1/heartbeat
```

---

## 4️⃣ Detener Aplicación Docker

### Script: `stop-app.sh`

Cuando termines de trabajar:

```bash
# Detener servicios (mantener datos)
./stop-app.sh

# Detener y eliminar volúmenes (borra datos)
./stop-app.sh --remove-volumes

# Limpieza completa (contenedores, volúmenes, imágenes)
./stop-app.sh --clean-all
```

**Opciones:**

| Opción | Descripción |
|--------|-------------|
| (sin opciones) | Detiene contenedores, mantiene datos |
| `--remove-volumes` `-v` | Elimina volúmenes (⚠️ borra datos) |
| `--remove-images` `-i` | Elimina imágenes Docker |
| `--clean-all` `-ca` | Limpieza completa |

---

## 5️⃣ Restauración del Entorno Local

### Script: `post-stop.sh`

Después de detener Docker, restaura tu entorno local:

```bash
./post-stop.sh
```

**¿Qué hace?**

1. **Reinicia PostgreSQL local**
   - Ejecuta `sudo systemctl start postgresql`
   - Verifica que esté corriendo en el puerto 5432
   - Muestra el estado del servicio

2. **Desactiva el entorno virtual**
   - Ejecuta `deactivate` para salir del venv
   - Vuelve al Python del sistema

**Salida esperada:**

```
╔═══════════════════════════════════════════════════════════════╗
║        🔄  POST-STOP ENVIRONMENT RESTORATION  🔄              ║
╚═══════════════════════════════════════════════════════════════╝

🔄 Step 1: Restarting local PostgreSQL service...
✅ Local PostgreSQL restarted successfully
   Service is listening on port 5432

🐍 Step 2: Deactivating virtual environment...
✅ Virtual environment deactivated

╔═══════════════════════════════════════════════════════════════╗
║              ✅  ENVIRONMENT RESTORED  ✅                      ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🔄 Flujo Completo - Ejemplo de Sesión

### Primera vez (instalación completa)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd agentic_ai_PoC_prj_hospitality

# 2. Configurar API Key
export AI_AGENTIC_API_KEY="tu-api-key-aqui"
# O agregar a ~/.bashrc para persistencia

# 3. Preparar entorno
./pre-start.sh
# Responde 'y' para instalar dependencias la primera vez

# 4. Iniciar aplicación
./start-app.sh --logs

# 5. Validar (en otra terminal)
./validate.sh

# 6. Desarrollar/probar...
# (tu trabajo aquí)

# 7. Detener aplicación
./stop-app.sh

# 8. Restaurar entorno local
./post-stop.sh
```

### Sesiones posteriores (día a día)

```bash
# Inicio rápido (si API Key ya está configurada)
./pre-start.sh
./start-app.sh --logs

# Tu trabajo aquí...

# Finalización
./stop-app.sh
./post-stop.sh
```

### Testing rápido (sin preparación manual)

Si ya ejecutaste `pre-start.sh` en la sesión actual:

```bash
./start-app.sh
./validate.sh
./stop-app.sh
./post-stop.sh
```

---

## ⚙️ Variables de Entorno Importantes

### Requeridas

```bash
export AI_AGENTIC_API_KEY="tu-api-key"  # OBLIGATORIA
```

### Opcionales (con valores por defecto)

```bash
export POSTGRES_HOST=bookings-db
export POSTGRES_PORT=5432
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=adminpass
export POSTGRES_DB=hospitality_db

export CHROMA_HOST=vectorstore-db
export CHROMA_PORT=8000

export API_PORT=8001
```

Para hacerlas permanentes, agrégalas a `~/.bashrc` o `~/.zshrc`:

```bash
echo 'export AI_AGENTIC_API_KEY="tu-api-key"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🔍 Troubleshooting

### Error: "Port 5432 already in use"

**Causa:** PostgreSQL local sigue corriendo

**Solución:**
```bash
sudo systemctl stop postgresql
# O ejecutar pre-start.sh de nuevo
```

### Error: "AI_AGENTIC_API_KEY is not set"

**Solución:**
```bash
export AI_AGENTIC_API_KEY="tu-api-key"
# Luego ejecutar start-app.sh de nuevo
```

### Error: "Virtual environment not found"

**Solución:**
```bash
python3 -m venv .venv
source .venv/bin/activate
# O ejecutar pre-start.sh que lo crea automáticamente
```

### Error: "Docker Compose not found"

**Solución:**
```bash
# Instalar Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### Los servicios no arrancan correctamente

**Solución:**
```bash
# Limpieza completa
./stop-app.sh --clean-all

# Reiniciar desde cero
./pre-start.sh
./start-app.sh --logs
```

---

## 📊 Verificación del Estado

### Verificar servicios Docker

```bash
docker ps
# Deberías ver: bookings-db, vectorstore-db, ai_agents_hospitality-api
```

### Verificar PostgreSQL local

```bash
sudo systemctl status postgresql
# Debe estar "inactive" mientras Docker corre
```

### Verificar entorno virtual

```bash
which python
# Debería mostrar: /home/marina/workshop/.../venv/bin/python
```

### Verificar puertos

```bash
sudo lsof -i :5432  # PostgreSQL Docker
sudo lsof -i :8000  # ChromaDB
sudo lsof -i :8001  # API
```

---

## 🎯 Checklist Pre-Inicio

Antes de cada sesión de desarrollo, verifica:

- [ ] PostgreSQL local detenido (`sudo systemctl stop postgresql`)
- [ ] Entorno virtual activado (prompt muestra `(.venv)`)
- [ ] API Key configurada (`echo $AI_AGENTIC_API_KEY`)
- [ ] Docker corriendo (`docker ps`)
- [ ] Puertos libres: 5432, 8000, 8001

**Tip:** Todo esto lo hace `pre-start.sh` automáticamente 🚀

---

## 📝 Comandos de Referencia Rápida

```bash
# Ciclo completo
./pre-start.sh && ./start-app.sh --logs
# [trabajo aquí]
./stop-app.sh && ./post-stop.sh

# Solo Docker (si entorno ya preparado)
./start-app.sh
./stop-app.sh

# Validación completa
./validate.sh

# Ver logs en vivo
tail -f logs/app_complete_*.log

# Acceso a bases de datos
docker exec -it bookings-db psql -U admin -d hospitality_db
curl http://localhost:8000/api/v1/heartbeat

# Limpieza profunda
./stop-app.sh --clean-all
docker system prune -a
```

---

**🎓 ¡Listo para empezar el workshop!** 🚀
