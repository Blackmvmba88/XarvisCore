# Hermes Session Notes

Timestamp: 2025-10-05
Location: /Users/blackmamba/projects/hermes

Summary of what we did
- Created the full Hermes Starter Kit structure under a single root (no hay desorden).
- Configured models and embeddings:
  - runtime.llm: llama3.1:8b
  - rag.embed_model: BAAI/bge-m3
- Implemented .env with LAN-friendly defaults (API bind via HERMES_API_BIND, WebUI local).
- Made Qdrant startup opt-in (START_QDRANT=1) to save disk.
- Added lazy initialization for HermesCtl and graceful chat fallback when LLM isn’t available.
- Created venv and installed minimal deps so API health and telemetry work.
- Started API (LAN) and WebUI (localhost). Verified health and telemetry persistence.

Known constraints
- Ollama model pull failed due to low disk space (~8.4 GiB free): pulling 4.9 GB model (llama3.1:8b) returned “no space left on device”.
- RAG ingestion and Qdrant container are deferred until space is available.

How to run
- Start without Qdrant: START_QDRANT=0 bash scripts/run_local.sh
- Stop: bash scripts/stop_local.sh
- Logs: tail -f /tmp/hermes_run.log

Termux telemetry
1) On Mac: ./scripts/lan_ip.sh
2) On Termux:
   curl -X POST http://LAN_IP_MAC:8788/telemetry \
     -H 'Content-Type: application/json' \
     -d '{"device":"termux","acc":[0.1,0.0,9.8]}'

Next steps (when you free 15–20 GiB)
- Start Ollama and pull model:
  /opt/homebrew/bin/ollama serve >/tmp/ollama_serve.log 2>&1 &
  /opt/homebrew/bin/ollama pull llama3.1:8b
- Install full deps and run ingestion:
  . .venv/bin/activate
  pip install -r services/api/requirements.txt
  pip install -r services/rag/requirements.txt
  START_QDRANT=1 bash scripts/run_local.sh
  python services/rag/ingest.py

Attached excerpt from plan (for archival)
Here’s what I’m going to do next: finish bringing Hermes up locally (API + WebUI) with LAN-ready telemetry, while deferring heavy downloads (LLM/model and Qdrant) due to low disk space. I’ve already created the full project structure and files exactly under /Users/blackmamba/projects/hermes, aligned the model names (llama3.1:8b) and embeddings (BAAI/bge-m3), wired a safe fallback for chat when the LLM isn’t ready, and verified the telemetry endpoint writes to data/memory/telemetry.jsonl.

Why deferred
- Ollama model pull failed: “no space left on device” pulling ~4.9 GB.
- To keep system responsive, deferred model download, Qdrant start, and RAG ingestion.
