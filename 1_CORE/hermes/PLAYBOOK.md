# PLAYBOOK — Hermes (rápido y práctico)

Propósito
- Hermes es la garganta del sistema: recibe y enruta mensajes, eventos, comandos, telemetría y consultas RAG. Un agente nuevo debe «aprender a hablar» aquí primero.

Cómo levantar (solo Hermes)
- Full (bootstrap + servicios):
```bash
cd 1_CORE/hermes
bash scripts/bootstrap_macos.sh
bash scripts/run_local.sh
```
- Solo API (útil para pruebas):
```bash
cd 1_CORE/hermes
python services/api/app.py --host 0.0.0.0 --port 8788
```

Endpoints esenciales (ejemplos mínimos)
- Health: GET /healthz  → {"ok": true}
- Chat (sincrónico): POST /chat
  - Payload: {"message": "hola"}
  - Respuesta: {"reply": "..."}
  - Ejemplo: curl -X POST http://localhost:8788/chat -H 'Content-Type: application/json' -d '{"message":"ping"}'
- Chat (stream SSE): GET /chat/stream?q=texto
  - Usa `curl -N` para ver tokens parciales: `curl -N 'http://localhost:8788/chat/stream?q=hola'`
  - Forma de stream: líneas `data: {"token":"..."}` y al final `event: done`.
- Ingest (RAG): POST /ingest  → lanza `python services/rag/ingest.py` (async wrapper)
- Telemetría: POST /telemetry (any JSON) → se guarda en `data/memory/telemetry-YYYYMMDD.jsonl` y en `telemetry.jsonl` (último)
  - Ejemplo: curl -X POST http://localhost:8788/telemetry -H 'Content-Type: application/json' -d '{"event":"ping","source":"agent-x"}'

Formas de prueba rápidas
- Ping básico: `curl -s -X POST http://localhost:8788/chat -H 'Content-Type: application/json' -d '{"message":"ping"}'`
- Stream: `curl -N 'http://localhost:8788/chat/stream?q=hola'`
- Telemetría: ver `tail -n 50 data/memory/telemetry-$(date -u +%Y%m%d).jsonl` después de enviar un POST

Comportamientos y notas internas
- Si no hay LLM disponible, `/chat` devuelve un mensaje de fallback: "[LLM no disponible aún: instala modelos o finaliza dependencias...]". Ver `hermesctl.HermesCtl._ollama()` para la integración con Ollama.
- `HermesCtl` se importa perezosamente; algunas rutas funcionan aun si faltan dependencias, pero ciertas funciones (chat avanzado, RAG) requieren instalaciones adicionales.

Logs y ubicación
- Log principal del dominio: `1_CORE/hermes/logs/hermes_run.log` (ver `services/api/logging_setup.py` para rotación/formatos).
- Telemetría diaria: `1_CORE/hermes/data/memory/telemetry-YYYYMMDD.jsonl`.

Depuración / fallos comunes
- "LLM no disponible": comprobar `command -v ollama` y que el modelo configurado exista.
- Problemas con Qdrant (RAG): revisar `configs/hermes.yaml` y la variable env `QDRANT_URL`.
- Si `/chat/stream` no emite tokens parciales: asegúrate de ejecutar con `curl -N` o un cliente SSE y revisa que `HermesCtl.chat()` devuelva texto.

Ejecutando tests locales
- Tests del API (si existen): `pytest 1_CORE/hermes/services/api -q` o probar `services/api` con curl manuales.

Consejos para agentes (prácticos)
- Comenzar con health → chat → stream para comprobar latencia y disponibilidad.
- Envío de telemetría en cada interacción útil para auditoría y diagnóstico.
- Para acciones críticas que cambian estado, pedir confirmación y usar dry-run cuando el dominio soporte (no todo lo hace por defecto).

Contacto y siguientes pasos
- Si quieres, genero un checklist de hardening y una sección "cómo añadir un nuevo endpoing seguro" para Hermes. ¿Lo agrego?
