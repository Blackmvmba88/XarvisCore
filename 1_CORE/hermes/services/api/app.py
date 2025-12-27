import os, json, argparse
from datetime import datetime, timezone
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from pathlib import Path

from logging_setup import configure_logging

# Configure rotating logs on import
configure_logging()

# Import hermesctl de forma perezosa para tolerar instalaciones mínimas
HermesCtl = None
try:
    from hermesctl import HermesCtl as _HermesCtl
    HermesCtl = _HermesCtl
except Exception as e:
    HermesCtl = None

CFG_PATH = Path("configs/hermes.yaml")

app = FastAPI(title="Hermes API", version="1.0")
hermes = None
if HermesCtl is not None:
    try:
        hermes = HermesCtl.from_yaml(CFG_PATH)
    except Exception:
        hermes = None

class ChatIn(BaseModel):
    message: str

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/chat")
def chat(inp: ChatIn):
    if hermes is None:
        return {"reply": "[LLM no disponible aún: instala modelos o finaliza dependencias. Telemetry y health operativos.]"}
    return {"reply": hermes.chat(inp.message)}

# SSE endpoint opcional sin websockets
@app.get("/chat/stream")
async def chat_stream(q: str):
    if hermes is None:
        async def gen_err():
            yield "data: {\"token\": \"LLM no disponible\"}\n\n"
            yield "event: done\ndata: {}\n\n"
        return StreamingResponse(gen_err(), media_type="text/event-stream")

    # Nota: HermesCtl.chat devuelve respuesta completa; simulamos stream en trozos
    async def gen():
        text = hermes.chat(q)
        for chunk in text.split():
            yield f"data: {{\"token\": \"{chunk}\"}}\n\n"
        yield "event: done\ndata: {}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.post("/ingest")
def ingest():
    # Simple wrapper para lanzar ingest local
    os.system("python services/rag/ingest.py")
    return {"status": "ingest_started"}

@app.post("/telemetry")
def telemetry(data: dict = Body(...)):
    # Guarda telemetría con rotación diaria: telemetry-YYYYMMDD.jsonl
    mem_dir = Path("data/memory"); mem_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    daily = mem_dir / f"telemetry-{stamp}.jsonl"
    line = json.dumps(data, ensure_ascii=False)
    with open(daily, "a") as f:
        f.write(line + "\n")
    # Mantener compatibilidad escribiendo también a telemetry.jsonl (último)
    with open(mem_dir / "telemetry.jsonl", "a") as f:
        f.write(line + "\n")
    return {"stored": True, "file": str(daily)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.getenv("HERMES_API_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("HERMES_API_PORT", "8788")))
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
