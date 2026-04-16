from __future__ import annotations
r que

import logging
import uuid
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .models import JobMetadata, JobRequest, JobResponse
from .services.audio import shift_pitch
from .services.downloader import download_audio

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Estación de Sonido yt-dlp", version="0.1.0")
logger = logging.getLogger("ytdlp.web")
logger.setLevel(logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs: Dict[str, JobMetadata] = {}

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_index():  # type: ignore[override]
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="UI no encontrada")
    return FileResponse(index_path)


@app.post("/api/jobs", response_model=JobResponse)
def create_job(payload: JobRequest, request: Request) -> JobResponse:
    job_id = uuid.uuid4().hex
    source_path: Path | None = None
    processed_path: Path | None = None

    try:
        source_path, info = download_audio(str(payload.url), settings.source_dir, job_id)
        processed_path = settings.processed_dir / f"{job_id}_pitch.mp3"
        shift_pitch(source_path, processed_path, payload.pitch_semitones, settings.ffmpeg_path)
    except Exception as exc:  # noqa: BLE001
        _cleanup_temp_files(job_id, source_path, processed_path)
        logger.exception("Fallo al procesar el job %s", job_id)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    metadata = JobMetadata(
        job_id=job_id,
        title=info.get("title"),
        duration=info.get("duration"),
        pitch_semitones=payload.pitch_semitones,
        source_file=str(source_path),
        processed_file=str(processed_path),
    )
    jobs[job_id] = metadata

    download_url = request.url_for("download_job_file", job_id=job_id)
    return JobResponse(
        job_id=job_id,
        title=metadata.title,
        duration=metadata.duration,
        pitch_semitones=metadata.pitch_semitones,
        download_url=str(download_url),
    )


@app.get("/api/jobs/{job_id}", response_model=JobMetadata)
def get_job(job_id: str) -> JobMetadata:
    metadata = jobs.get(job_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return metadata


@app.get("/api/jobs/{job_id}/file")
def download_job_file(job_id: str):  # type: ignore[override]
    metadata = jobs.get(job_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    processed_path = Path(metadata.processed_file)
    if not processed_path.exists():
        raise HTTPException(status_code=410, detail="Archivo expirado")

    return FileResponse(processed_path, filename=f"{metadata.title or job_id}_pitch.mp3")


def _cleanup_temp_files(job_id: str, source_path: Path | None = None, processed_path: Path | None = None) -> None:
    if settings.keep_files:
        return
    candidates: List[Path] = []
    if source_path:
        candidates.append(Path(source_path))
    else:
        candidates.extend(settings.source_dir.glob(f"{job_id}.*"))

    if processed_path:
        candidates.append(Path(processed_path))
    else:
        candidates.append(settings.processed_dir / f"{job_id}_pitch.mp3")

    for target in candidates:
        try:
            if target.exists():
                target.unlink()
        except OSError:
            logger.warning("No se pudo eliminar %s", target)
