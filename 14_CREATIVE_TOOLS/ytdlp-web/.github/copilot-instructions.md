# Copilot Instructions for ytdlp_web

## Project Overview

FastAPI-based audio processing service that downloads audio from any yt-dlp-supported URL, applies pitch shifting (±12 semitones) via ffmpeg, and serves processed files through a minimal web UI.

## Architecture

```
app/
├── main.py          # FastAPI app, routes, in-memory job store
├── config.py        # Pydantic settings with YTDLP_ env prefix
├── models.py        # Pydantic models: JobRequest, JobMetadata, JobResponse
└── services/
    ├── downloader.py # yt-dlp + direct HTTP download logic
    └── audio.py      # ffmpeg pitch shifting via subprocess
static/               # Single-page Tailwind UI
data/source/          # Downloaded originals (cleaned up by default)
data/processed/       # Pitch-shifted MP3s
```

## Key Patterns

### Download Strategy (`app/services/downloader.py`)
- **Direct HTTP**: URLs ending in `.mp3/.wav/.flac` etc bypass yt-dlp and use `requests`
- **yt-dlp**: All other URLs use yt-dlp with FFmpegExtractAudio postprocessor
- Cookie file auto-discovery: `~/.config/yt-dlp/cookies.txt`, `~/.config/ytdlp/cookies.txt`, `~/Downloads/cookies.txt`

### Pitch Shifting (`app/services/audio.py`)
- Uses ffmpeg filter chain: `asetrate` → `aresample` → `atempo` to shift pitch while preserving duration
- Formula: `pitch_factor = 2^(semitones/12)`
- Zero semitones = simple file copy (optimization)

### Job Lifecycle
1. Request: `POST /api/jobs` with `{url, pitch_semitones}`
2. Download to `data/source/{job_id}.mp3`
3. Process to `data/processed/{job_id}_pitch.mp3`
4. Store metadata in in-memory `jobs` dict
5. Return `download_url` pointing to `/api/jobs/{job_id}/file`

## Configuration (`.env`)

```bash
YTDLP_DATA_ROOT=data
YTDLP_FFMPEG_PATH=/usr/local/bin/ffmpeg
YTDLP_KEEP_FILES=true          # Debug: preserve temp files
YTDLP_COOKIES_FILE=/path/to/cookies.txt
YTDLP_DIRECT_DOWNLOAD_HEADERS='{"User-Agent":"Custom"}'
```

## Development Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run (with hot reload)
uvicorn app.main:app --reload --port 8000

# Test (open http://127.0.0.1:8000)
```

## Critical Dependencies

- **ffmpeg**: Must be in PATH (`brew install ffmpeg` on macOS)
- **yt-dlp**: For platform-specific extractors; may need cookies for auth-required sites
- **requests**: For direct audio URL downloads with custom headers

## Code Conventions

- Spanish UI/logs (`"Job no encontrado"`, `"Procesando..."`)
- Type hints with `from __future__ import annotations`
- Pydantic models for all API request/response schemas
- Error cleanup: temp files deleted on failure unless `YTDLP_KEEP_FILES=true`
- Logging via `logging.getLogger("ytdlp.web")`

## When Adding Features

- New download sources: extend `AUDIO_EXTENSIONS` in `downloader.py` or add to yt-dlp handling
- New audio filters: modify `filter_chain` in `audio.py`
- API changes: update models in `models.py`, keep API responses backward-compatible
- UI changes: edit `static/index.html` (Tailwind CDN, vanilla JS)
