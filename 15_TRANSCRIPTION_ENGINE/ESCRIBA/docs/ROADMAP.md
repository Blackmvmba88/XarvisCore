# Roadmap ESCRIBA

## Fase 0 · Bootstrap (Semana 1)

- [ ] Inicializar repo, entorno (`uv`/`poetry`) y `pre-commit`.
- [ ] Configurar `ffmpeg` y dependencias base (`sounddevice`, `faster-whisper`).
- [ ] Esqueleto de paquetes (`capture`, `transcribe`, `writer`, `storage`, `ui`).

## Fase 1 · Captura & Normalización (Semanas 2-3)

- [ ] `CaptureService` para micrófono (streaming 16 kHz mono).
- [ ] Ingesta de archivos WAV/MP3 y extracción de audio desde video (`ffmpeg-python`).
- [ ] Sistema de colas priorizadas (mic live > archivo > batch) con `asyncio`.
- [ ] Tests de latencia y manejo de pérdida de paquetes.

## Fase 2 · Motor STT Local (Semanas 4-5)

- [ ] Integrar `faster-whisper` con selección dinámica de modelo (tiny/small/medium).
- [ ] API interna para emitir segmentos con timestamps, confianza y canal.
- [ ] Benchmarks CPU/GPU (Metal) y caching de modelos.
- [ ] Exportación rápida a `.srt` simple.

## Fase 3 · Escritor Inteligente (Semanas 6-7)

- [ ] Pipeline de limpieza (ruido, fillers), puntuación y capitalización contextual.
- [ ] Etiquetas temáticas / comandos (spaCy + reglas personalizadas).
- [ ] Hook opcional a modelo compacto de reescritura para estilo narrativo.
- [ ] Validadores y pruebas de calidad lingüística.

## Fase 4 · Persistencia Total (Semanas 8-9)

- [ ] Definir esquema SQLite (`sessions`, `segments`, `sources`, `tags`).
- [ ] Guardar texto crudo + refinado + metadatos + apuntes del usuario.
- [ ] Generar archivos Markdown/SRT/JSONL por sesión.
- [ ] Herramientas CLI para búsqueda y exportación.

## Fase 5 · Interfaces (Semanas 10-11)

- [ ] TUI (Rich/Textual) con vista live, comandos (bookmark, export, pausa).
- [ ] WebUI local (FastAPI + HTMX/Tailwind) con WebSockets.
- [ ] Edición ligera y sincronización con la base de datos.
- [ ] Tema oscuro/claro y soporte móvil.

## Fase 6 · Experimentos & Comercialización (Semanas 12+)

- [ ] Modo "canal oculto" para películas (selección de pista y canal).
- [ ] Plugins de análisis (resúmenes, tópicos, comandos especiales).
- [ ] Empaquetado (CLI, app desktop ligera) y licenciamiento.
- [ ] Documentación avanzada y demos para clientes.

## Métricas Clave

- Latencia de transcripción < 2s para mic live (modelo small).
- Precisión WER ≤ 10% en español general.
- Disponibilidad local (sin red) 100% durante sesiones.
- Sincronización TUI/WebUI con desfase < 300 ms.

## Riesgos & Mitigaciones

- **Consumo de GPU/CPU**: permitir degradar a modelos tiny y limitar FPS de video.
- **Ruido ambiental**: filtros de pre-procesado y perfiles por usuario.
- **Crecimiento de base**: rotar sesiones y ofrecer exportación/compresión.
- **Privacidad**: todo local, cifrado opcional de la base.
