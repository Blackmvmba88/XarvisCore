# Hermes — IA local para crear valor en silencio

Hermes es un asistente local, discreto y modular. Su finalidad práctica es optimizar gastos, automatizar trabajo creativo y convertir conocimiento en valor.

## Requisitos (macOS Apple Silicon)
- Homebrew
- Python 3.11+
- Ollama (opcional para modelos)
- Docker (opcional: Qdrant/Grafana)

## Inicio rápido
```bash
cd hermes
bash scripts/bootstrap_macos.sh
bash scripts/run_local.sh
# WebUI: http://*********:8787
# API:   http://*********:8788
```

## Flujo base

1. Ingesta documentos a `data/docs/`.
2. `python services/rag/ingest.py` (crea embeddings en `data/vectors/`).
3. Usa `hermesctl` para chatear/consultar o el WebUI minimal.

## Modo Termux (cliente sensores)

```bash
bash scripts/termux_client.sh
```
