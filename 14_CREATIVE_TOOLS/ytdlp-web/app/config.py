from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_COOKIE_LOCATIONS = (
    Path.home() / ".config" / "yt-dlp" / "cookies.txt",
    Path.home() / ".config" / "ytdlp" / "cookies.txt",
    Path.home() / "Downloads" / "cookies.txt",
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Global application settings."""

    data_root: Path = Path("data")
    source_dir: Path = Path("data/source")
    processed_dir: Path = Path("data/processed")
    ffmpeg_path: str = "ffmpeg"
    keep_files: bool = False  # set True for debugging to keep processed files
    cookies_file: Optional[Path] = None
    direct_download_headers: Dict[str, str] = Field(default_factory=dict)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="YTDLP_", env_file_encoding="utf-8")

    def ensure_dirs(self) -> None:
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self._resolve_cookie_file()

    def _resolve_cookie_file(self) -> None:
        if self.cookies_file:
            expanded = Path(self.cookies_file).expanduser()
            if not expanded.exists():
                raise FileNotFoundError(f"No se encontró el archivo de cookies: {expanded}")
            self.cookies_file = expanded
            logger.info("Usando archivo de cookies definido por el usuario: %s", expanded)
            return

        for candidate in DEFAULT_COOKIE_LOCATIONS:
            expanded = candidate.expanduser()
            if expanded.exists():
                self.cookies_file = expanded
                logger.info("Detectado archivo de cookies en %s", expanded)
                return

        logger.info("No se detectó archivo de cookies; yt-dlp operará sin autenticación")


settings = Settings()
settings.ensure_dirs()
