# Estación de sonido basada en yt-dlp

## Objetivos

- Permitir que el usuario ingrese cualquier URL soportada por yt-dlp.
- Descargar el audio (formato MP3 por defecto) desde la fuente remota.
- Aplicar un ajuste de pitch (±12 semitonos) sin necesidad de herramientas externas manuales.
- Entregar el archivo procesado mediante descarga directa desde la aplicación web.

## Stack propuesto

- **Backend**: FastAPI con Python 3.11 aprox.
- **Descarga**: Biblioteca `yt-dlp` ejecutada en modo audio-only y fallback HTTP directo para enlaces que ya apuntan a audio (`requests`). Soporta archivo de cookies Netscape (busca automáticamente en `~/.config/yt-dlp/cookies.txt`, `~/.config/ytdlp/cookies.txt` y `~/Downloads/cookies.txt`) y cabeceras adicionales para evitar bloqueos.
- **Procesamiento de audio**: `ffmpeg` (invocado mediante subprocess) para modificar pitch utilizando filtros `asetrate` y `aresample`.
- **Almacenamiento temporal**: Directorios `data/source/` y `data/processed/` gestionados con UUIDs y limpieza al vuelo.
- **Frontend**: HTML + Tailwind CDN + JavaScript ligero que consume los endpoints REST.

## Flujo de alto nivel

1. El usuario ingresa URL y el número de semitonos en la UI.
2. El frontend envía una solicitud `POST /api/jobs` con URL y pitch.
3. El backend descarga el audio a `data/source/{job_id}.ext` mediante yt-dlp, o via HTTP directo si la URL ya es un MP3/FLAC/etc.
4. El backend ejecuta ffmpeg para generar `data/processed/{job_id}_pitch.mp3` aplicando `asetrate`.
5. La API responde con un payload JSON que contiene metadatos y una URL firmada (`/api/jobs/{job_id}/file`).
6. El frontend permite descargar el resultado mediante un enlace directo.

## Endpoints planificados

- `POST /api/jobs`: crea un job, descarga y procesa el audio; retorna JSON `{job_id, title, duration, pitch, download_url}`.
- `GET /api/jobs/{job_id}`: devuelve metadatos del job si es necesario (opcional para ampliaciones futuras).
- `GET /api/jobs/{job_id}/file`: envía el archivo procesado como attachment.

## Dependencias clave

- `fastapi`, `uvicorn[standard]`
- `yt-dlp`
- `requests`
- `python-multipart` (para futuras ampliaciones con uploads)
- `pydantic-settings` para configuración

**Requisitos del sistema**: `ffmpeg` debe estar instalado y accesible en `$PATH`.
