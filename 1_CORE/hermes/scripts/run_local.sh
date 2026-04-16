#!/usr/bin/env bash
set -e

# Cargar .env si existe
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

# Activar venv
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
else
  echo "[WARN] .venv no encontrado. Ejecuta bootstrap o crea venv."
fi

# Idempotencia: matar procesos previos si quedan colgados
pkill -f "services/api/app.py" >/dev/null 2>&1 || true
pkill -f "services/webui/server.py" >/dev/null 2>&1 || true

# Gating de Qdrant (opt-in + chequeo de disco)
if command -v docker >/dev/null && [ "${START_QDRANT:-0}" = "1" ]; then
  DISK_THRESHOLD_GIB=${DISK_THRESHOLD_GIB:-15}
  FREE_KB=$(df -k . | tail -1 | awk '{print $4}')
  FREE_GIB=$((FREE_KB/1024/1024))
  if [ "$FREE_GIB" -lt "$DISK_THRESHOLD_GIB" ]; then
    echo "[WARN] Espacio libre ${FREE_GIB}GiB < umbral ${DISK_THRESHOLD_GIB}GiB. Saltando Qdrant."
  else
    docker compose up -d qdrant || true
  fi
fi

# Defaults seguros si vienen placeholders o vacíos
if [ -z "${HERMES_API_BIND}" ] || [ "${HERMES_API_BIND}" = "*******" ]; then
  # Usa IP de la interfaz Wi‑Fi/Ethernet como fallback para acceso LAN (o localhost si no hay)
  LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || true)"
  if [ -z "$LAN_IP" ]; then LAN_IP="$(ipconfig getifaddr en1 2>/dev/null || true)"; fi
  if [ -z "$LAN_IP" ]; then LAN_IP="localhost"; fi
  HERMES_API_BIND="$LAN_IP"
fi
if [ -z "${HERMES_API_PORT}" ]; then
  HERMES_API_PORT=8788
fi
if [ -z "${HERMES_API_HOST}" ] || [ "${HERMES_API_HOST}" = "*********" ]; then
  HERMES_API_HOST=localhost
fi
if [ -z "${HERMES_WEB_HOST}" ] || [ "${HERMES_WEB_HOST}" = "*********" ]; then
  HERMES_WEB_HOST=localhost
fi
if [ -z "${HERMES_WEB_PORT}" ]; then
  HERMES_WEB_PORT=8787
fi

# API (se expone en LAN si HERMES_API_BIND resuelve a IP LAN)
python services/api/app.py --host "${HERMES_API_BIND}" --port "${HERMES_API_PORT}" &
API_PID=$!

# WebUI (local por defecto)
python services/webui/server.py --host "${HERMES_WEB_HOST}" --port "${HERMES_WEB_PORT}" &
WEB_PID=$!

echo "API en http://${HERMES_API_HOST}:${HERMES_API_PORT}"
echo "WebUI en http://${HERMES_WEB_HOST}:${HERMES_WEB_PORT}"
echo "[Ctrl+C] para detener (o bash scripts/stop_local.sh)"
wait $API_PID $WEB_PID
