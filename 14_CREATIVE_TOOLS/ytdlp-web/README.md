# Estación de sonido con yt-dlp

Aplicación FastAPI que descarga audio desde cualquier enlace soportado por `yt-dlp`, permite ajustar el pitch ±12 semitonos mediante `ffmpeg` y expone un frontend mínimo para gestionar las descargas.

Si la URL ya apunta a un archivo de audio (`.mp3`, `.wav`, `.flac`, etc.) se usa una descarga HTTP directa antes de procesar el pitch, lo que evita depender de yt-dlp en esos casos.

## Requisitos

- Python 3.11+ (recomendado)
- `ffmpeg` disponible en el `PATH` (`brew install ffmpeg` en macOS)
- `yt-dlp` y dependencias de Python (se instalan vía `pip`)

## Puesta en marcha

```bash
cd /Users/blackmamba/Downloads/ytdlp_web
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Abre `http://127.0.0.1:8000` en el navegador para usar la interfaz.

## API

### `POST /api/jobs`

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "pitch_semitones": 3.5
}
```

Respuesta:

```json
{
  "job_id": "...",
  "title": "...",
  "duration": 240,
  "pitch_semitones": 3.5,
  "download_url": "http://127.0.0.1:8000/api/jobs/.../file"
}
```

### `GET /api/jobs/{job_id}`

Devuelve los metadatos almacenados en memoria.

### `GET /api/jobs/{job_id}/file`

Descarga el MP3 procesado.

## Ajustes opcionales

Crea un archivo `.env` en la raíz si necesitas personalizar rutas o el ejecutable de `ffmpeg`:

```
YTDLP_DATA_ROOT=data
YTDLP_FFMPEG_PATH=/usr/local/bin/ffmpeg
YTDLP_KEEP_FILES=true
YTDLP_COOKIES_FILE=/Users/blackmamba/Downloads/cookies.txt
YTDLP_DIRECT_DOWNLOAD_HEADERS={"User-Agent":"MyCustomUA"}
```

- `YTDLP_COOKIES_FILE`: archivo exportado desde tu navegador (formato Netscape) que `yt-dlp` utilizará para evitar bloqueos/403.
- `YTDLP_DIRECT_DOWNLOAD_HEADERS`: diccionario JSON con cabeceras personalizadas para las descargas HTTP directas (útil para endpoints protegidos).

Si no defines `YTDLP_COOKIES_FILE`, la app buscará automáticamente en:

1. `~/.config/yt-dlp/cookies.txt`
2. `~/.config/ytdlp/cookies.txt`
3. `~/Downloads/cookies.txt`

Cuando encuentre alguno, lo usará sin necesidad de configurar nada adicional.

## Limpieza

Por defecto los archivos temporales se eliminan después de cada job. Establece `YTDLP_KEEP_FILES=true` si prefieres conservarlos.

## Notas sobre descargas

- Para enlaces directos a audio la app descarga el archivo con `requests` y luego aplica `ffmpeg`; puedes añadir cabeceras mediante `YTDLP_DIRECT_DOWNLOAD_HEADERS`.
- Para plataformas cerradas (por ejemplo algunos videos de YouTube) puede que necesites aportar cookies o credenciales compatibles con `yt-dlp`; en pruebas locales usa fuentes abiertas como SoundHelix para validar el pipeline.
