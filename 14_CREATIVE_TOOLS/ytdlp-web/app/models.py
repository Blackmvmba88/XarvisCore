from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class JobRequest(BaseModel):
    url: HttpUrl = Field(..., description="Enlace soportado por yt-dlp")
    pitch_semitones: float = Field(0.0, ge=-12.0, le=12.0, description="Ajuste de pitch en semitonos (-12 a 12)")


class JobMetadata(BaseModel):
    job_id: str
    title: Optional[str] = None
    duration: Optional[float] = Field(None, description="Duración en segundos")
    pitch_semitones: float
    source_file: str
    processed_file: str


class JobResponse(BaseModel):
    job_id: str
    title: Optional[str] = None
    duration: Optional[float] = None
    pitch_semitones: float
    download_url: str
