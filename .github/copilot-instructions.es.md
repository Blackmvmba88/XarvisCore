# Instrucciones para Copilot — Xarvis Core (conciso)

**Propósito:** guía breve y accionable para que un agente IA o un desarrollador nuevo sea productivo rápidamente en este repositorio.

## Configuración rápida ✅
- Crea y activa un entorno virtual en la raíz del repo:
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && pip install -r dev-requirements.txt
```
- Versión objetivo de Python: **3.11** (CI/dev target).

## Ejecutar y depurar 🔧
- Levantar toda la plataforma (orquestador usa `venv/bin/python3`):
```bash
python3 xarvis_supervisor.py
```
- Levantar solo un servicio (desde su carpeta):
```bash
cd <dominio_dir>
venv/bin/python3 <servicio>.py
```
- Logs: `5_INFRA/logs/` (ej.: `master.log`, `core.log`). El supervisor reinicia dominios cada ~15s cuando salen.

## Patrones y arquitectura 🧭
- Dominios organizados 0..19; `xarvis_supervisor.py` orquesta `PROCESSES` / `EXTENDED_PROCESSES`.
- Patrón de proceso: `{ "path": <abs>, "log": <abs>, "proc": None, "priority": N, "enabled": Bool }`.
- Servicios largos: `*_engine.py`, `*_detector.py`, `*_protocol.py` (singletons como `gaia = GaiaProtocol()`).
- Integraciones locales usan a veces `sys.path.insert` (ver `1_CORE/xarvis_core.py`).

## Quickstarts (60s, copy-pasteable) ⚡
**Hermes — garganta (60s)**
- Propósito: mensajes, eventos, comandos, telemetría.
- Levantar (completo):
```bash
cd 1_CORE/hermes
bash scripts/bootstrap_macos.sh
bash scripts/run_local.sh
```
- Levantar solo API: `python services/api/app.py --host 0.0.0.0 --port 8788`
- Ping mínimo:
```bash
curl -s -X POST http://localhost:8788/chat -H 'Content-Type: application/json' -d '{"message":"ping"}'
# → {"reply":"[LLM no disponible aún: instala modelos...]"} (si no hay modelo)
```
- SSE: `curl -N 'http://localhost:8788/chat/stream?q=hola'` (recibe `data: {...}` y `event: done`).
- Telemetría: `curl -s -X POST http://localhost:8788/telemetry -H 'Content-Type: application/json' -d '{"event":"ping","source":"test"}'` => `data/memory/telemetry-YYYYMMDD.jsonl`.

**VPA — músculo operativo (60s)**
- Levantar: `cd 10_CULTURAL_RENAISSANCE && python3 vocal_performance_analyzer.py` (puerto 9000).
- Dashboard/API: `open vpa_dashboard.html` o `http://localhost:9000/status`.
- Dry-run: `vpa.current_song = {...}` y GET `/performance` para probar sin persistir.

**Suno Suite — artista (60s)**
- Data anchor: `~/Music/Suno` (no mover).
- Setup: `export SUNO_HOME=~/Music/Suno` y `cd 10_CULTURAL_RENAISSANCE/suno-suite`.
- Headless test: `python3 apps/suno-headless/main.py` (verifica Chrome/driver y credenciales).

## Tests & ejecución 🧪
- Tests globales: `pytest -q -m "not slow"`.
- Tests por dominio: `pytest path/to/domain/tests -q`.

## Seguridad & convenciones 🔒
- Muchos módulos usan `BASE_DIR` hardcodeado; preferir `.env` para overrides locales.
- No subir credenciales reales; utiliza `.env` y `dotenv`.

## PR checklist (práctico) ✅
- Pasos de reproducción exactos.
- Añadir o actualizar tests (marcar slow cuando corresponda).
- Actualizar `5_INFRA/setup_xarvis.sh` si agregas deps nativas.
- Añadir entrada en `xarvis_supervisor.py` y asegurar logs.

---

Si quieres, creo playbooks detallados por dominio (ej.: `1_CORE/hermes/PLAYBOOK.md`) con ejemplos curl, payloads y troubleshooting (recomendado). ¡Dime y lo genero! 🎯
