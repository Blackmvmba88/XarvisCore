import os, yaml, subprocess, json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

class HermesCtl:
    def __init__(self, cfg):
        self.cfg = cfg
        self.embedder = SentenceTransformer(cfg["rag"]["embed_model"]) if cfg.get("rag") else None
        self.qdrant = QdrantClient(url=os.getenv("QDRANT_URL", cfg["rag"]["qdrant_url"])) if cfg.get("rag") else None

    @classmethod
    def from_yaml(cls, path):
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        return cls(cfg)

    def _ollama(self, prompt: str):
        model = self.cfg["runtime"]["llm"]
        # Usa Ollama si está instalado; fallback a eco
        if os.system("command -v ollama >/dev/null 2>&1") == 0:
            p = subprocess.run([
                "ollama", "run", model,
                ], input=prompt.encode(), capture_output=True)
            return p.stdout.decode() or p.stderr.decode()
        return f"[DEV] {prompt[:200]}"

    def chat(self, msg: str) -> str:
        # Hook para estrategias de dinero discretas en lenguaje natural
        system_hint = (
            "Responde con foco en ahorro, automatización y creación de valor. "
            "Da pasos accionables y discretos."
        )
        prompt = f"Sistema: {system_hint}\nUsuario: {msg}\nAsistente:"
        return self._ollama(prompt)
