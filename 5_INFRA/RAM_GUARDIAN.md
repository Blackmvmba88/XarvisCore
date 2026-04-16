# RAM Guardian (macOS)

Descripción breve
- Un daemon ligero que monitorea memoria libre + inactiva y toma acciones seguras en caso de baja memoria.
- Por diseño viene en *dry-run* (no mata ni cierra procesos) y requiere `--enable-actions` para realizar operaciones destructivas.

Instalación
1. Revisa `5_INFRA/ram_guardian.py` y `5_INFRA/com.blackmamba.ramguardian.plist.example`.
2. Ejecuta `bash scripts/install_ram_guardian.sh` como usuario y acepta la instalación.

Uso y configuración
- Cambia intervalos y umbral en el plist `ProgramArguments` (`--interval`, `--threshold`).
- Para activar acciones automáticas, añade `--enable-actions` y quita `--dry-run` (usar con extremo cuidado).

Pruebas
- El script está cubierto por tests básicos: `pytest tests/test_ram_guardian.py`.

Logs
- Salida estándar y errores: `/tmp/ram_guardian.out` y `/tmp/ram_guardian.err`
- Registro principal: `/tmp/ram_guardian.log`

Web UI
- Hay una interfaz web liviana incluida (`5_INFRA/ram_guardian_webui.py`) que expone un SPA en `5_INFRA/webui/`.
- Endpoints principales:
  - `GET /api/status` — disponible fracción, total, procesos principales
  - `GET /api/metrics` — últimas métricas (JSON lines)
  - `POST /api/action` — ejecutar `estimate`, `quit_app` o `kill_pid` (las acciones destructivas requieren autorización y un archivo de aprobación)
- Seguridad: si `RAM_GUARDIAN_WEB_SECRET` está configurado, las peticiones POST deben incluir `Authorization: Bearer <secret>`; además, por defecto las acciones destructivas exigen la existencia de `RAM_GUARDIAN_APPROVAL_FILE` (por defecto `/tmp/ram_guardian_approval`).
- Ejecuta la UI localmente: `python3 5_INFRA/ram_guardian_webui.py` y abre `http://localhost:8080`.

Precauciones
- No se recomienda habilitar agresiveness > 0 en máquinas de producción sin supervisión.
- Evita el uso de `sudo` o `purge` automáticos; el script prioriza cierres graciosos de aplicaciones.

Contact/Notes
- Si quieres, puedo añadir una opción para enviar reportes a un socket local o integrarlo con existing monitoring frameworks.
