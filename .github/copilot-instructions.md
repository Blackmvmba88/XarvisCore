# Xarvis Core — Instrucciones resumidas por componente (Orden / Función / README / Roadmap)

Propósito: cada componente tiene su Orden (cómo arrancar), su Función (qué hace), README (dónde leer más) y Roadmap (dónde encontrar planificación).

## Orquestador — `xarvis_supervisor.py`
- Orden: `python3 xarvis_supervisor.py` (desde la raíz del repo; prefiere `venv/bin/python3` si existe)
- Función: arranca y supervisa procesos; reinicia servicios caídos cada 15s; fija cwd de los procesos.
- README: ver `xarvis_supervisor.py` y comentarios en el archivo para convenciones de `PROCESSES`.
- Roadmap: `EpicRoadmap.md` (alineación global); cambios de arranque deben documentarse en PR y `5_INFRA/setup_xarvis.sh` si añaden prerequisitos.

## Core — `1_CORE/xarvis_core.py`
- Orden: `venv/bin/python3 1_CORE/xarvis_core.py` o `python3 1_CORE/xarvis_core.py` desde `1_CORE/`.
- Función: dashboard/servicio principal (Flask) que consume `*_protocol.py` y expone endpoints (p. ej. puerto 5050).
- README: revisar `1_CORE/` y el archivo fuente `1_CORE/xarvis_core.py` para endpoints y dependencias.
- Roadmap: `EpicRoadmap.md` + issues/notes en el directorio `1_CORE/` cuando existan cambios de API.

## Power — `3_POWER/` (p. ej. `xarvis_full_power.py`)
- Orden: `venv/bin/python3 3_POWER/xarvis_full_power.py`.
- Función: servicios de potencia/full stack (p. ej. puerto 8080), utilidades como `ram_guardian.py`.
- README: inspeccionar `3_POWER/` y comentarios en cada script.
- Roadmap: documentar cambios de recursos/pools en `EpicRoadmap.md` y notas de PR.

## Audio / Cultural — `10_CULTURAL_RENAISSANCE/`
- Orden: usar scripts provistos; ejemplo: `bash 10_CULTURAL_RENAISSANCE/start_vpa_detector.sh` o `venv/bin/python3 10_CULTURAL_RENAISSANCE/audio_detector.py` desde ese directorio.
- Función: detector de audio, pipelines VPA, generación/análisis de playlists y utilidades de música.
- README: `10_CULTURAL_RENAISSANCE/BLACKMAMBA_AUDIO_DETECTOR.md`, `MUSIC_WEBUI_README.md` y `PERFORMANCE_SUITE_README.md` dentro del directorio.
- Roadmap: `10_CULTURAL_RENAISSANCE/INTEGRATION_COMPLETE.md` y notas en `EpicRoadmap.md` para features mayores.

## Infra — `5_INFRA/`
- Orden: scripts de bootstrap (macOS): `bash 5_INFRA/setup_xarvis.sh`.
- Función: instalación de dependencias del sistema (Homebrew, Docker) y utilidades para desarrollar y desplegar.
- README: revisar `5_INFRA/setup_xarvis.sh` y `5_INFRA/` para instrucciones de entorno.
- Roadmap: cambios de infra deben ir con instrucciones de instalación en `5_INFRA/` y documentarse en PR.

## Dependencias nativas y herramientas del sistema
- Orden (instalación breve): si trabajas con audio, instala `fpcalc`/chromaprint y `sox` según `5_INFRA/setup_xarvis.sh`.
- Función: proveen huellas de audio y manipulación de audio necesarias por `10_CULTURAL_RENAISSANCE/audio_detector.py`.
- README: ver notas en `10_CULTURAL_RENAISSANCE/BLACKMAMBA_AUDIO_DETECTOR.md`.
- Roadmap: anotar herramientas nativas en `5_INFRA/setup_xarvis.sh` cuando se añadan nuevas dependencias.

## Convenciones rápidas (útiles al editar)
- Protocolos: `*_protocol.py` → clase + instancia singleton exportada al final.
- Engines: `*_engine.py` → procesos largos o intensivos.
- Detectores: `*_detector.py` → dependen de herramientas externas; usar `start_*.sh` para arrancar.
- Logs: centralizados en `5_INFRA/logs/` — consultar `master, core, full_power, ram_guardian`.

## Dónde encontrar el Roadmap y documentación global
- Roadmap principal: `EpicRoadmap.md`.
- Documentación adicional: `README.md`, `BLACKMAMBA_AUDIO_DETECTOR.md` (audio), `MUSIC_WEBUI_README.md`.

## Cómo proponer cambios (checklist breve)
1. Añade PR con: descripción, comando para arrancar localmente, archivos modificados y tests (si aplica).
2. Si añades dependencias nativas, actualiza `5_INFRA/setup_xarvis.sh` y documenta pasos en el PR.
3. Verifica arrancar con `python3 xarvis_supervisor.py` y revisa `5_INFRA/logs/master.log`.

-- Fin: cada componente ahora tiene Orden / Función / README / Roadmap — dime si quieres más componentes listados o una tabla de puertos.
