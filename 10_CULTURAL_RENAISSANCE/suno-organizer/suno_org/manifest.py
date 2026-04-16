from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from .config import SUNO_ROOT
from .lyrics import extract_embedded_lyrics, transcribe_excerpt, suggest_title_from_text, lyrics_excerpt
from .report import write_csv, write_json
from .scan import AudioRow


def _detect_language_basic(text: str) -> str:
    t = text.lower()
    es_hits = sum(1 for w in [" el ", " la ", " de ", " que ", " y ", " mi ", " tu "] if w in f" {t} ")
    en_hits = sum(1 for w in [" the ", " and ", " my ", " your ", " love ", " baby "] if w in f" {t} ")
    if es_hits >= en_hits and es_hits > 0:
        return "es"
    if en_hits > 0:
        return "en"
    return ""


def genre_guess_basic(text: str) -> str:
    t = (text or "").lower()
    # Simple keyword-based genre detection
    GENRES = [
        ("psychedelic rock", ["psicodel", "psychedelic"]),
        ("metal", ["metal", "metalcore", "death", "black metal"]),
        ("rock", ["rock", "guitar", "punk"]),
        ("hip hop", ["hip-hop", "hip hop", "rap", "trap"]),
        ("edm", ["edm", "electronic", "dance", "club", "techno", "house", "trance"]),
        ("reggae", ["reggae", "dub"]),
        ("salsa", ["salsa"]),
        ("cumbia", ["cumbia"]),
        ("jazz", ["jazz", "swing"]),
        ("blues", ["blues"]),
        ("funk", ["funk"]),
        ("pop", ["pop"]),
        ("corridos", ["corridos", "regional", "banda"]),
    ]
    for g, keys in GENRES:
        if any(k in t for k in keys):
            return g
    return ""


def build_title_manifest(
    rows: List[AudioRow],
    use_lyrics: bool = False,
    max_duration_sec: int = 45,
    limit: Optional[int] = None,
) -> List[Dict]:
    out: List[Dict] = []
    count = 0
    for r in rows:
        if limit is not None and count >= limit:
            break
        p = Path(r.file_path)
        lyr = extract_embedded_lyrics(p)
        err = None
        if not lyr and use_lyrics:
            lyr, err = transcribe_excerpt(p, max_duration_sec=max_duration_sec)
        title = suggest_title_from_text(lyr) if lyr else None
        if not title:
            # fallback: use file stem
            title = p.stem
        lang = _detect_language_basic(lyr) if lyr else ""
        out.append({
            "file_path": r.file_path,
            "file_name": r.file_name,
            "proposed_title": title,
            "lyrics_excerpt": lyrics_excerpt(lyr),
            "language": lang,
            "genre_guess": "",
            "cover_image": "",
            "explicit": "no",
            "is_cover": "no",
            "notes": err or "",
        })
        count += 1
    return out


def write_title_manifest(rows: List[Dict], out_dir: Optional[Path] = None) -> Dict[str, Path]:
    out_dir = out_dir or (SUNO_ROOT / "manifests")
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "suno_manifest.json"
    csv_path = out_dir / "suno_manifest.csv"
    write_json(json_path, rows)
    if rows:
        write_csv(csv_path, rows, fieldnames=list(rows[0].keys()))
    else:
        write_csv(csv_path, [], fieldnames=["file_path","file_name","proposed_title","lyrics_excerpt","language","genre_guess","cover_image","explicit","is_cover","notes"])
    return {"json": json_path, "csv": csv_path}
