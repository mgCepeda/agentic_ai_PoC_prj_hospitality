#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_MODE=false

if [ "$1" = "--dev-mode" ]; then
  DEV_MODE=true
fi

echo "[1/4] Activando entorno SAM..."
source "$ROOT_DIR/.venv-sam/bin/activate"

if [ "$DEV_MODE" = true ]; then
  echo "[2/4] Modo dev activo: se omite Docker broker y se usará SOLACE_DEV_MODE=true"
else
  echo "[2/4] Verificando broker Solace local..."
  if ! docker ps --format '{{.Names}}' | grep -q '^solace-broker$'; then
    echo "No se detecta 'solace-broker'. Iniciando contenedor local..."
    docker run -d --rm -p 8080:8080 -p 55555:55555 -p 8008:8008 \
      -u 1004 --shm-size=2g \
      --env username_admin_globalaccesslevel=admin \
      --env username_admin_password=admin \
      --name=solace-broker solace/solace-pubsub-standard
  else
    echo "Broker ya está activo."
  fi
fi

echo "[3/4] Verificando datos de hoteles..."
if [ ! -f "$ROOT_DIR/bookings-db/output_files/hotels/hotels.json" ]; then
  echo "Generando datos sintéticos de hoteles..."
  (cd "$ROOT_DIR/bookings-db" && python src/gen_synthetic_hotels.py)
else
  echo "Datos sintéticos detectados."
fi

echo "[4/4] Ejecutando SAM..."
cd "$ROOT_DIR/sam_hospitality"
if [ "$DEV_MODE" = true ]; then
  SOLACE_DEV_MODE=true sam run configs
else
  sam run configs
fi
