mem_manager — Identificación y gestión ligera de procesos (RAM)

Propósito
- Identificar procesos que consumen RAM en macOS y marcarlos para cierre seguro luego.
- No mata procesos por defecto: las acciones de cierre deben confirmarse explícitamente.

Archivos
- `identify_processes.py` — script principal (Python, sin deps externas).
- `mem_manager.sh` — wrapper de shell para invocar el script.
- `state.json` — almacenará procesos marcados (creado por el script cuando sea necesario).

Comandos útiles
- `./mem_manager.sh --list --top 30`  -> Lista top 30 por uso de memoria
- `./mem_manager.sh --filter Spotify`  -> Busca procesos que contengan "Spotify"
- `./mem_manager.sh --mark 20566` -> Marca PID 20566 para cierre posterior
- `./mem_manager.sh --show-marked` -> Muestra procesos marcados
- `./mem_manager.sh --suggest-quit` -> Sugiere comandos (osascript o kill) para los marcados
- `./mem_manager.sh --kill-marked` -> Envía SIGTERM a todos los marcados (pide confirmación)

Notas de seguridad
- El script evita matar procesos sin confirmación.
- Se sugiere usar `--suggest-quit` para ejecutar comandos de cierre más suaves (p. ej. AppleScript para apps GUI).

Próximos pasos
- Añadir comando `monitor` que vigile porcentaje libre y ejecute cierres cuando baje de un umbral.
- Añadir opción para reabrir apps cerradas (guardar lista de apps cerradas).
- Añadir API ligera (FastAPI) y UI web para mostrar procesos por prioridad y acciones rápidas. (server: `server.py`, UI: `webui/index.html`).
- Monitor automático: vigila % memoria libre y, según configuración, sugiere o ejecuta cierres de procesos de prioridad alta. Configuración: umbral (%), intervalo (s), modo `auto_kill` (true/false).
- Seguridad: whitelist/blacklist y protección contra cierre de procesos críticos (WindowServer, kernel_task, Finder, etc.). Las operaciones que cierran procesos usan comandos suaves cuando es posible (AppleScript `tell application "X" to quit`) y registran `reopen_cmd` para poder reabrir la app.
- API y UI: `server.py` expone `/processes`, `/mark`, `/unmark`, `/kill`, `/kill_single`, `/monitor/*`, `/actions` y `/reopen`. La UI (`webui/index.html`) muestra procesos por prioridad con iconos, permite buscar, marcar, cerrar individual, cerrar marcados y controlar el monitor.
- Registro de acciones: todas las acciones (incluyendo comandos ejecutados) quedan en `state.json` bajo la clave `actions` y se muestran en la UI como código para que cualquiera vea exactamente el comando que se ejecutó.
- Empaquetado: `package_dmg.sh` genera un binario y DMG (requiere `pyinstaller` y `create-dmg`).

Si quieres, pruebo la UI localmente (ejecuta `python3 tools/mem_manager/server.py` y abre http://127.0.0.1:8088/) o puedo intentar generar el DMG cuando confirmes que tienes `pyinstaller` y `create-dmg` instalados.