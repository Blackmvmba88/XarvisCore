from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from pydantic import BaseModel

HOME = Path.home()
SUNO_INDEX = HOME / "Music" / "Suno" / "index.json"
DOWNLOADS = HOME / "Downloads"
AUDIO_EXTS = {".mp3", ".wav", ".m4a"}


class CatalogItem(BaseModel):
    id: str
    title: str
    source: str  # "suno" | "downloads"
    path: Path
    duration_sec: Optional[float] = None
    analysis_path: Optional[Path] = None


def _hash_id(p: Path) -> str:
    try:
        stat = p.stat()
        h = hashlib.sha1()
        h.update(str(p).encode("utf-8"))
        h.update(str(stat.st_mtime_ns).encode("utf-8"))
        h.update(str(stat.st_size).encode("utf-8"))
        return h.hexdigest()[:16]
    except FileNotFoundError:
        return hashlib.sha1(str(p).encode("utf-8")).hexdigest()[:16]


def _scan_dir_for_audio(d: Path) -> Iterable[Path]:
    if not d.exists():
        return []
    for root, _dirs, files in os.walk(d):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in AUDIO_EXTS:
                yield p


def load_from_suno_index(index_path: Path = SUNO_INDEX) -> List[CatalogItem]:
    items: List[CatalogItem] = []
    if not index_path.exists():
        return items
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return items
    for obj in data:
        fp = obj.get("file_path") or obj.get("path") or obj.get("audio_path")
        if not fp:
            continue
        p = Path(fp)
        if not p.exists():
            continue
        title = Path(fp).name
        duration = obj.get("duration_sec")
        items.append(
            CatalogItem(
                id=_hash_id(p),
                title=title,
                source="suno",
                path=p,
                duration_sec=duration,
            )
        )
    return items


def load_from_downloads(downloads_dir: Path = DOWNLOADS) -> List[CatalogItem]:
    items: List[CatalogItem] = []
    for p in _scan_dir_for_audio(downloads_dir):
        items.append(
            CatalogItem(
                id=_hash_id(p),
                title=p.name,
                source="downloads",
                path=p,
            )
        )
    return items


def build_catalog() -> List[CatalogItem]:
    suno = load_from_suno_index()
    dl = load_from_downloads()
    # De-duplicar por ruta absoluta
    seen = set()
    result: List[CatalogItem] = []
    for it in (*suno, *dl):
        key = str(it.path)
        if key in seen:
            continue
        seen.add(key)
        result.append(it)
    # Ordenar por nombre
    result.sort(key=lambda x: x.title.lower())
    return result
