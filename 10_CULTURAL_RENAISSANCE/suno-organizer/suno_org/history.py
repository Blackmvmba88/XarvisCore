from __future__ import annotations

import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Iterable, List, Set

BROWSER_DB_PATHS = [
    # Defaults (we añadimos perfiles adicionales dinámicamente abajo)
    Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "History",
    Path.home() / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser" / "Default" / "History",
    Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "Default" / "History",
    Path.home() / "Library" / "Application Support" / "Chromium" / "Default" / "History",
    # Safari
    Path.home() / "Library" / "Safari" / "History.db",
]

# Firefox profiles
FIREFOX_PROFILES_DIR = Path.home() / "Library" / "Application Support" / "Firefox" / "Profiles"


def _query_chromium_history(db_path: Path) -> List[str]:
    # Preferir solo canciones para evitar ruido
    q = "SELECT url FROM urls WHERE url LIKE '%suno%/song/%' ORDER BY last_visit_time DESC"
    res = _query_sqlite_file(db_path, q)
    # Fallback amplio si no hay resultados (perfiles antiguos)
    if not res:
        q = "SELECT url FROM urls WHERE url LIKE '%suno%' ORDER BY last_visit_time DESC"
        res = _query_sqlite_file(db_path, q)
    return res


def _query_safari_history(db_path: Path) -> List[str]:
    # Safari schema: history_items(url), history_visits; basta leer items
    q = "SELECT url FROM history_items WHERE url LIKE '%suno%' ORDER BY id DESC"
    return _query_sqlite_file(db_path, q)


def _query_firefox_profiles() -> List[str]:
    out: List[str] = []
    if not FIREFOX_PROFILES_DIR.exists():
        return out
    for prof in FIREFOX_PROFILES_DIR.glob("*.default*"):
        db = prof / "places.sqlite"
        if db.exists():
            q = "SELECT url FROM moz_places WHERE url LIKE '%suno%' ORDER BY last_visit_date DESC"
            out.extend(_query_sqlite_file(db, q))
    return out


def _query_sqlite_file(path: Path, query: str) -> List[str]:
    if not path.exists():
        return []
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / path.name
            shutil.copy2(path, tmp)
            con = sqlite3.connect(str(tmp))
            cur = con.cursor()
            rows = cur.execute(query).fetchall()
            con.close()
            return [r[0] for r in rows if r and isinstance(r[0], str)]
    except Exception:
        return []


def collect_suno_urls_from_browsers() -> List[str]:
    urls: List[str] = []
    # Agregar perfiles adicionales dinámicamente (Chrome/Brave/Edge/Chromium)
    for vendor, sub in [
        ("Google/Chrome", "Profile *"),
        ("BraveSoftware/Brave-Browser", "Profile *"),
        ("Microsoft Edge", "Profile *"),
        ("Chromium", "Profile *"),
    ]:
        base = Path.home() / "Library" / "Application Support" / vendor
        if base.exists():
            for prof in base.glob(f"{sub}/History"):
                BROWSER_DB_PATHS.append(prof)
    # Leer cada DB
    for p in BROWSER_DB_PATHS:
        if 'Safari' in str(p):
            urls.extend(_query_safari_history(p))
        else:
            urls.extend(_query_chromium_history(p))
    urls.extend(_query_firefox_profiles())
    # dedup conservando orden
    seen: Set[str] = set(); out: List[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u); out.append(u)
    return out
