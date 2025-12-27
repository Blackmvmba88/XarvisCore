from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Optional

from ..config import EXCLUDED_DIR_NAMES


def is_hidden_path(p: Path) -> bool:
    parts = p.parts
    return any(part.startswith(".") for part in parts)


def should_exclude_dir(p: Path) -> bool:
    name = p.name
    if name in EXCLUDED_DIR_NAMES:
        return True
    if name.startswith("."):
        return True
    return False


def walk_files(
    roots: List[Path],
    include_exts: Iterable[str],
    follow_symlinks: bool = False,
) -> Generator[Path, None, None]:
    include_exts = {e.lower() for e in include_exts}
    for root in roots:
        root = root.expanduser()
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
            # filtrar dirnames in-place para evitar descender a excluidos
            dirnames[:] = [d for d in dirnames if not should_exclude_dir(Path(dirpath) / d)]
            for fn in filenames:
                ext = Path(fn).suffix.lower()
                if ext in include_exts:
                    yield Path(dirpath) / fn


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def deconflict_name(dest_dir: Path, base_name: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    candidate = dest_dir / base_name
    if not candidate.exists():
        return candidate
    stem = Path(base_name).stem
    ext = Path(base_name).suffix
    i = 1
    while True:
        c = dest_dir / f"{stem} ({i}){ext}"
        if not c.exists():
            return c
        i += 1


def safe_move(src: Path, dst: Path, overwrite: bool = False) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        dst = deconflict_name(dst.parent, dst.name)
    shutil.move(str(src), str(dst))
    return dst
