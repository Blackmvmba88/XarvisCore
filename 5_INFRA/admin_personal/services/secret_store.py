"""services/secret_store.py
Simple secret store using Keyring with optional Fernet encryption.
Stores an index at `data/secret_index.json` to allow listing entries.
"""
import json
import os
from pathlib import Path
from typing import List, Optional

try:
    import keyring
except Exception as e:
    raise RuntimeError("`keyring` is required. Install with `pip install keyring`") from e

try:
    from cryptography.fernet import Fernet
    _HAS_CRYPTO = True
except Exception:
    _HAS_CRYPTO = False

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INDEX_FILE = DATA_DIR / "secret_index.json"

os.makedirs(DATA_DIR, exist_ok=True)


def _load_index():
    if not INDEX_FILE.exists():
        return {}
    try:
        return json.loads(INDEX_FILE.read_text())
    except Exception:
        return {}


def _save_index(idx):
    INDEX_FILE.write_text(json.dumps(idx, indent=2))


def _add_index(service: str, username: str):
    idx = _load_index()
    idx.setdefault(service, [])
    if username not in idx[service]:
        idx[service].append(username)
    _save_index(idx)


def _remove_index(service: str, username: str):
    idx = _load_index()
    if service in idx and username in idx[service]:
        idx[service].remove(username)
        if not idx[service]:
            idx.pop(service)
        _save_index(idx)


# Fernet key helpers
def _get_fernet_key(service: str) -> Optional[bytes]:
    if not _HAS_CRYPTO:
        return None
    key = keyring.get_password(f"fernet_key:{service}", "key")
    return key.encode() if key else None


def _create_fernet_key(service: str) -> bytes:
    if not _HAS_CRYPTO:
        raise RuntimeError("cryptography not available; install `cryptography` to use encryption")
    key = Fernet.generate_key()
    keyring.set_password(f"fernet_key:{service}", "key", key.decode())
    return key


# Public API

def set_secret(service: str, username: str, secret: str, encrypt: bool = False):
    """Store secret for (service, username). If encrypt=True will use Fernet and
    store the encrypted blob in keyring. The Fernet key is stored in Keyring too.
    """
    if encrypt:
        key = _get_fernet_key(service) or _create_fernet_key(service)
        f = Fernet(key)
        token = f.encrypt(secret.encode())
        value = token.decode()
    else:
        value = secret

    keyring.set_password(service, username, value)
    _add_index(service, username)


def get_secret(service: str, username: str, decrypt: bool = False) -> Optional[str]:
    """Return secret or None. If decrypt=True will attempt Fernet decryption if possible."""
    val = keyring.get_password(service, username)
    if val is None:
        return None
    if decrypt:
        key = _get_fernet_key(service)
        if key and _HAS_CRYPTO:
            try:
                f = Fernet(key)
                return f.decrypt(val.encode()).decode()
            except Exception:
                # not encrypted or wrong key
                return val
    return val


def delete_secret(service: str, username: str):
    try:
        keyring.delete_password(service, username)
    except Exception:
        pass
    _remove_index(service, username)


def list_secrets(service: Optional[str] = None) -> dict:
    """Return index dict or service-specific list."""
    idx = _load_index()
    if service:
        return {service: idx.get(service, [])}
    return idx


if __name__ == "__main__":
    print("Index:", json.dumps(_load_index(), indent=2))
