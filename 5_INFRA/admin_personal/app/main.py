"""app/main.py
FastAPI app exposing minimal endpoints to manage secrets and talk to the assistant.
Requires an admin API key stored in Keyring under service 'app' username 'admin_api_key'.
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

from services import secret_store, assistant_client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Personal Manager (MVP)")

# Allow local frontend dev server (Vite default at http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecretIn(BaseModel):
    service: str
    username: str
    secret: str
    encrypt: Optional[bool] = False


class MessageIn(BaseModel):
    message: str
    dry_run: Optional[bool] = True


def _require_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-KEY header")
    admin_key = secret_store.get_secret("app", "admin_api_key")
    if not admin_key or x_api_key != admin_key:
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/secrets")
def create_secret(payload: SecretIn, _=Depends(_require_api_key)):
    secret_store.set_secret(payload.service, payload.username, payload.secret, encrypt=payload.encrypt)
    return {"ok": True}


@app.get("/secrets/{service}/{username}")
def read_secret(service: str, username: str, decrypt: Optional[bool] = True, _=Depends(_require_api_key)):
    val = secret_store.get_secret(service, username, decrypt=decrypt)
    if val is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"service": service, "username": username, "secret": val}


@app.get("/secrets")
def list_secrets(_=Depends(_require_api_key)):
    """Return the indexed secrets (service -> usernames)."""
    return secret_store.list_secrets()


@app.post("/assistant/message")
def assistant_message(payload: MessageIn, _=Depends(_require_api_key)):
    res = assistant_client.send_message(payload.message, dry_run=payload.dry_run)
    if not res.get("ok"):
        raise HTTPException(status_code=500, detail=res)
    return res
