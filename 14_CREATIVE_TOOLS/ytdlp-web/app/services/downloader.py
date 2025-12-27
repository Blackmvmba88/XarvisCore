from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

import requests
from yt_dlp import YoutubeDL

from app.config import settings

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {".mp3", ".aac", ".m4a", ".wav", ".flac", ".ogg", ".opus"}
STREAM_CHUNK_SIZE = 256 * 1024  # 256 KB


def download_audio(url: str, target_dir: Path, job_id: str) -> Tuple[Path, Dict[str, Any]]:
    """Download audio using yt-dlp and return the saved path plus metadata."""

    target_dir.mkdir(parents=True, exist_ok=True)

    if _looks_like_direct_audio(url):
        logger.info("Descargando archivo directo sin yt-dlp: %s", url)
        return _download_direct_audio(url, target_dir, job_id)

    return _download_with_yt_dlp(url, target_dir, job_id)


def _download_with_yt_dlp(url: str, target_dir: Path, job_id: str) -> Tuple[Path, Dict[str, Any]]:
    base_output = target_dir / f"{job_id}.%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": str(base_output),
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    if settings.cookies_file:
        ydl_opts["cookiefile"] = str(settings.cookies_file)

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    output_path = target_dir / f"{job_id}.mp3"
    if not output_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo descargado en {output_path}")

    logger.info("Audio descargado con yt-dlp: %s", output_path)
    return output_path, info


def _download_direct_audio(url: str, target_dir: Path, job_id: str) -> Tuple[Path, Dict[str, Any]]:
    headers = settings.direct_download_headers or None
    response = requests.get(url, stream=True, timeout=120, headers=headers)
    response.raise_for_status()

    suffix = _resolve_extension(url, response.headers.get("content-type"))
    output_path = target_dir / f"{job_id}{suffix}"

    with output_path.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
            if chunk:
                handle.write(chunk)

    parsed = urlparse(url)
    title = Path(parsed.path).stem or parsed.netloc or job_id
    metadata: Dict[str, Any] = {"title": title, "duration": None}

    logger.info("Descarga directa completada: %s", output_path)
    return output_path, metadata


def _looks_like_direct_audio(url: str) -> bool:
    parsed = urlparse(url)
    return Path(parsed.path).suffix.lower() in AUDIO_EXTENSIONS


def _resolve_extension(url: str, content_type: str | None) -> str:
    parsed_ext = Path(urlparse(url).path).suffix.lower()
    if parsed_ext in AUDIO_EXTENSIONS:
        return parsed_ext

    if content_type:
        guess = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if guess in AUDIO_EXTENSIONS:
            return guess

    return ".mp3"
