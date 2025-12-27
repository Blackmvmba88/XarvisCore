import os, glob
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLL = "hermes_docs"

vectors = []
payloads = []
ids = []

root = Path("data/docs")
files = list(root.rglob("*.txt")) + list(root.rglob("*.md"))
if not files:
    print("[INFO] No hay documentos en data/docs. Añade archivos .txt o .md.")
    exit(0)

print(f"[INGEST] {len(files)} archivos")
embedder = SentenceTransformer("BAAI/bge-m3")

texts = []
for fp in files:
    t = fp.read_text(errors="ignore")
    texts.append(t[:2000])  # simple chunk demo

embs = embedder.encode(texts).tolist()

client = QdrantClient(url=QDRANT_URL)
try:
    client.recreate_collection(
        collection_name=COLL,
        vectors_config=rest.VectorParams(size=len(embs[0]), distance=rest.Distance.COSINE)
    )
except Exception:
    pass

for i, (fp, vec) in enumerate(zip(files, embs)):
    ids.append(i)
    vectors.append(vec)
    payloads.append({"path": str(fp)})

client.upsert(collection_name=COLL, points=rest.Batch(points=rest.PointStruct.batch(ids=ids, vectors=vectors, payloads=payloads)))
print("[DONE] Ingesta completa.")
