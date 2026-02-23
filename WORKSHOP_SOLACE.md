# 🧭 Workshop de Hospitality con Solace Agent Mesh

Esta guía adapta el workshop de este repo para ejecutarlo con **Solace Agent Mesh (SAM)**.

## 1) Estado actual del repo

- Workshop original (LangChain): `WORKSHOP.md`
- API mock actual: `ai_agents_hospitality-api/`
- Base SAM creada en esta sesión: `sam_hospitality/`

## 2) Prerrequisitos

- Python 3.12+
- Un endpoint/modelo LLM compatible con SAM
- Docker (solo si vas a usar broker local en contenedor)

## 3) Preparación rápida

Desde la raíz del proyecto:

```bash
cd /home/marina/workshopSolace/agentic_ai_PoC_prj_hospitality

# activar venv de SAM
source .venv-sam/bin/activate

# revisar versión
sam --version
```

## 4) Configurar variables de entorno de SAM

Editar `sam_hospitality/.env` y completar al menos:

- `LLM_SERVICE_ENDPOINT`
- `LLM_SERVICE_API_KEY`
- `LLM_SERVICE_PLANNING_MODEL_NAME`
- `LLM_SERVICE_GENERAL_MODEL_NAME`

Valores Solace locales por defecto (modo broker externo/local) ya están definidos:

- `SOLACE_BROKER_URL=ws://localhost:8008`
- `SOLACE_BROKER_VPN=default`
- `SOLACE_BROKER_USERNAME=default`
- `SOLACE_BROKER_PASSWORD=default`

## 5) Levantar broker Solace local

> Este paso es **opcional** si usas `SOLACE_DEV_MODE=true`.

Si no tienes broker activo, ejecuta:

```bash
docker run -d --rm -p 8080:8080 -p 55555:55555 -p 8008:8008 \
  -u 1004 --shm-size=2g \
  --env username_admin_globalaccesslevel=admin \
  --env username_admin_password=admin \
  --name=solace-broker solace/solace-pubsub-standard
```

## 6) Generar datos sintéticos del workshop

```bash
cd bookings-db
python src/gen_synthetic_hotels.py
cd ..
```

Esto genera archivos en `bookings-db/output_files/hotels/`.

## 7) Ejecutar SAM para hospitality

Tienes dos formas válidas usando `sam run`:

### Opción A: `sam run` + broker local Docker

```bash
cd sam_hospitality
source ../.venv-sam/bin/activate
sam run configs
```

### Opción B: `sam run` sin Docker (dev mode)

```bash
cd sam_hospitality
source ../.venv-sam/bin/activate
SOLACE_DEV_MODE=true sam run configs
```

También puedes usar el script helper:

```bash
# modo con broker docker
./start-solace-workshop.sh

# modo sin docker broker
./start-solace-workshop.sh --dev-mode
```

Interfaz Web UI:

- `http://127.0.0.1:8010`

## 8) Qué se adaptó para hospitality

Se agregó una herramienta Python para responder preguntas de hoteles usando datos sintéticos:

- Tool module: `sam_hospitality/src/hospitality_tools.py`
- Agent config: `sam_hospitality/configs/agents/main_orchestrator.yaml`
- Tool function: `query_hospitality_data`

## 9) Preguntas de prueba

- "list hotels in France"
- "meal plans for hotels in Paris"
- "show hotel addresses"
- "list hotels in Nice"

## 10) Próximo paso recomendado

Para aproximarte al workshop completo (RAG + analytics SQL), crea dos tools adicionales:

1. `query_hotel_rooms_data` (lee `hotel_rooms.md`)
2. `query_bookings_sql` (consulta PostgreSQL de `bookings-db`)

Y luego enrútalas desde el mismo orquestador SAM.
