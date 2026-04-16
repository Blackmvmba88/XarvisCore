from pathlib import Path

def expand_user(p: str | Path) -> str:
    return str(Path(p).expanduser())

def ensure_dir(p: str | Path):
    Path(p).expanduser().mkdir(parents=True, exist_ok=True)

def validate_dir(p: str | Path) -> bool:
    return Path(p).expanduser().is_dir()
