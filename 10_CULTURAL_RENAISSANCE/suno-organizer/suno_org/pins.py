from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .config import SUNO_ROOT
from .scan import AudioRow

PINS_FILE = SUNO_ROOT / "pinned.json"


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_pins() -> Dict:
    if not PINS_FILE.exists():
        return {"entries": []}
    try:
        return json.loads(PINS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"entries": []}


def save_pins(data: Dict) -> None:
    PINS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = PINS_FILE.with_suffix(PINS_FILE.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(PINS_FILE)


def _row_key(r: AudioRow) -> str:
    # prefer sha256, fallback to fingerprint, then to absolute path
    return r.file_sha256 or r.fp_chromaprint or r.file_path


def _matches_pattern(text: str, pattern: str) -> bool:
    try:
        import re
        return re.search(pattern, text, flags=re.IGNORECASE) is not None
    except Exception:
        # treat as simple substring if regex fails
        return pattern.lower() in text.lower()


def annotate_pins(rows: List[AudioRow]) -> List[AudioRow]:
    pins = load_pins().get("entries", [])
    keys = set()
    paths = set()
    for e in pins:
        k = e.get("file_sha256") or e.get("fp_chromaprint") or e.get("file_path")
        if k:
            keys.add(k)
        p = e.get("file_path")
        if p:
            paths.add(p)
    for r in rows:
        k = _row_key(r)
        if k in keys or r.file_path in paths:
            r.pinned = True
    return rows


def add_pins_by_patterns(rows: List[AudioRow], patterns: List[str], all_suno: bool = False) -> int:
    data = load_pins()
    entries = data.get("entries", [])
    have = set()
    for e in entries:
        k = e.get("file_sha256") or e.get("fp_chromaprint") or e.get("file_path")
        if k:
            have.add(k)

    sel: List[AudioRow] = []
    if all_suno:
        sel = [r for r in rows if r.suno_like]
    else:
        if not patterns:
            return 0
        for r in rows:
            for pat in patterns:
                if _matches_pattern(r.file_path, pat) or _matches_pattern(r.file_name, pat):
                    sel.append(r)
                    break

    added = 0
    for r in sel:
        k = _row_key(r)
        if k in have:
            continue
        entries.append({
            "file_path": r.file_path,
            "file_name": r.file_name,
            "file_sha256": r.file_sha256,
            "fp_chromaprint": r.fp_chromaprint,
            "added_at": _now_iso(),
        })
        have.add(k)
        added += 1

    data["entries"] = entries
    save_pins(data)
    return added


def resolve_pins_to_rows(rows: List[AudioRow]) -> List[AudioRow]:
    # Return AudioRow subset corresponding to pins, preserving source order
    pinned_rows: List[AudioRow] = []
    pins = load_pins().get("entries", [])
    by_sha = {r.file_sha256: r for r in rows if r.file_sha256}
    by_fp = {r.fp_chromaprint: r for r in rows if r.fp_chromaprint}
    by_path = {r.file_path: r for r in rows}
    for e in pins:
        r = None
        if e.get("file_sha256") and e["file_sha256"] in by_sha:
            r = by_sha[e["file_sha256"]]
        elif e.get("fp_chromaprint") and e["fp_chromaprint"] in by_fp:
            r = by_fp[e["fp_chromaprint"]]
        elif e.get("file_path") and e["file_path"] in by_path:
            r = by_path[e["file_path"]]
        if r:
            r.pinned = True
            pinned_rows.append(r)
    return pinned_rows
