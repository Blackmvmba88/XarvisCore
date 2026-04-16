from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from rich.console import Console
from rich.table import Table
from tqdm import tqdm

from .config import AUDIO_EXTS, DEFAULT_AUDIO_ROOTS, INDEX_CSV, INDEX_JSON, ScanOptions
from .fingerprint import fingerprint_chromaprint, has_fpcalc
from .metadata import AudioMeta, extract_audio_meta, is_suno_like
from .report import write_csv, write_json
from .utils.fs import walk_files
from .utils.hashing import sha256_file

console = Console()


@dataclass
class AudioRow:
    file_path: str
    file_name: str
    size_bytes: int
    duration_sec: Optional[float]
    sample_rate: Optional[int]
    channels: Optional[int]
    bitrate: Optional[int]
    codec: Optional[str]
    created_at: str
    modified_at: str
    suno_like: bool
    suno_reason: str
    file_sha256: Optional[str]
    fp_chromaprint: Optional[str]
    dup_group_id: Optional[str]
    pinned: bool = False


def _stat_dates(p: Path) -> tuple[str, str]:
    st = p.stat()
    created = datetime.fromtimestamp(getattr(st, "st_ctime", st.st_mtime))
    modified = datetime.fromtimestamp(st.st_mtime)
    return created.isoformat(timespec="seconds"), modified.isoformat(timespec="seconds")


def scan_audio(options: Optional[ScanOptions] = None) -> List[AudioRow]:
    if options is None:
        options = ScanOptions(roots=DEFAULT_AUDIO_ROOTS)
    roots = options.roots or DEFAULT_AUDIO_ROOTS

    rows: List[AudioRow] = []

    files = list(walk_files(roots, include_exts=AUDIO_EXTS))
    for p in tqdm(files, desc="Escaneando audio", unit="file"):
        try:
            meta = extract_audio_meta(p)
            size = p.stat().st_size
            created, modified = _stat_dates(p)
            is_suno, reason = is_suno_like(p, meta)

            fp = None
            if options.fingerprint:
                fpr = fingerprint_chromaprint(p)
                fp = fpr.fp

            file_hash = None
            # Podría ser costoso; opcionalmente calcular solo si fingerprint no está disponible
            if not fp:
                file_hash = sha256_file(p)

            row = AudioRow(
                file_path=str(p),
                file_name=p.name,
                size_bytes=size,
                duration_sec=meta.duration_sec,
                sample_rate=meta.sample_rate,
                channels=meta.channels,
                bitrate=meta.bitrate,
                codec=meta.codec,
                created_at=created,
                modified_at=modified,
                suno_like=is_suno,
                suno_reason=reason,
                file_sha256=file_hash,
                fp_chromaprint=fp,
                dup_group_id=None,
            )
            rows.append(row)
        except Exception as e:
            console.print(f"[yellow]Aviso[/]: error procesando {p}: {e}")
    return rows


def save_indexes(rows: List[AudioRow], json_path: Path = INDEX_JSON, csv_path: Path = INDEX_CSV) -> None:
    write_json(json_path, (asdict(r) for r in rows))
    fieldnames = [
        "file_path", "file_name", "size_bytes", "duration_sec", "sample_rate", "channels", "bitrate", "codec",
        "created_at", "modified_at", "suno_like", "suno_reason", "file_sha256", "fp_chromaprint", "dup_group_id", "pinned",
    ]
    write_csv(csv_path, (asdict(r) for r in rows), fieldnames)


def print_table(rows: List[AudioRow], limit: int = 50) -> None:
    t = Table(title=f"Audios (mostrando {min(limit, len(rows))}/{len(rows)})")
    t.add_column("Archivo")
    t.add_column("Duración", justify="right")
    t.add_column("Tamaño", justify="right")
    t.add_column("Fecha", justify="right")
    t.add_column("Suno?", justify="center")
    t.add_column("Pin", justify="center")

    def fmt_dur(d: Optional[float]) -> str:
        if d is None:
            return "?"
        s = int(d)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h>0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def fmt_sz(n: int) -> str:
        units = ["B", "KiB", "MiB", "GiB"]
        i = 0
        f = float(n)
        while f >= 1024 and i < len(units)-1:
            f /= 1024
            i += 1
        return f"{f:.1f} {units[i]}"

    for r in rows[:limit]:
        t.add_row(
            r.file_name,
            fmt_dur(r.duration_sec),
            fmt_sz(r.size_bytes),
            r.created_at.split("T")[0],
            "✅" if r.suno_like else "",
            "📌" if r.pinned else "",
        )
    console.print(t)


def group_duplicates(rows: List[AudioRow]) -> Dict[str, List[AudioRow]]:
    groups: Dict[str, List[AudioRow]] = {}
    # Preferir fingerprint; si no hay, usar sha256 de archivo
    for r in rows:
        key = r.fp_chromaprint or r.file_sha256
        if not key:
            continue
        groups.setdefault(key, []).append(r)
    # filtrar grupos con más de 1
    return {k: v for k, v in groups.items() if len(v) > 1}
