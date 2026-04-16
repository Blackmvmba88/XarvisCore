from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


# Directorios por defecto para escanear audio
DEFAULT_AUDIO_ROOTS: List[Path] = [
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Music",
]

# Directorios a excluir del escaneo
EXCLUDED_DIR_NAMES = {
    "Library", ".git", ".venv", "venv", "node_modules", "__pycache__", ".Trash",
}

# Extensiones de audio
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac"}

# Extensiones de instaladores y scripts
INSTALLER_EXTS = {".dmg", ".pkg", ".zip"}
SCRIPT_EXTS = {".sh", ".py", ".js", ".zsh", ".command"}

# Destinos recomendados
SUNO_ROOT = (Path.home() / "Music" / "Suno").expanduser()
DUP_DIR = SUNO_ROOT / ".Duplicates"
INSTALLERS_DIR = (Path.home() / "Installers").expanduser()
SCRIPTS_DIR = (Path.home() / "scripts").expanduser()

# Archivos de índices
INDEX_JSON = SUNO_ROOT / "index.json"
INDEX_CSV = SUNO_ROOT / "index.csv"


@dataclass
class ScanOptions:
    roots: List[Path]
    exclude_hidden: bool = True
    include_exts: List[str] | None = None
    fingerprint: bool = False
    parallel: int = 4

