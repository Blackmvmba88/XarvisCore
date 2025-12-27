"""services/assistant_client.py
Minimal assistant bridge that reads API key from Keyring (service 'openai', username 'api_key')
and forwards chat messages to OpenAI Chat Completions. Dry-run mode available.
"""
from typing import Dict, Any
import os
import requests

from .secret_store import get_secret


OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")


def _get_api_key() -> str:
    # Try keyring first
    key = get_secret("openai", "api_key", decrypt=True)
    if key:
        return key
    # fallback to env
    return os.environ.get("OPENAI_API_KEY", "")


def send_message(message: str, model: str = "gpt-3.5-turbo", dry_run: bool = True) -> Dict[str, Any]:
    """Send a single message; if dry_run True, returns a simulated response."""
    if dry_run:
        return {"ok": True, "model": model, "response": f"(dry-run) You said: {message}"}

    api_key = _get_api_key()
    if not api_key:
        return {"ok": False, "error": "No API key configured (set via Keyring or OPENAI_API_KEY)"}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 512,
    }

    resp = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        return {"ok": False, "status": resp.status_code, "text": resp.text}
    j = resp.json()
    # Extract assistant content
    try:
        content = j["choices"][0]["message"]["content"]
    except Exception:
        content = j
    return {"ok": True, "response": content, "raw": j}
