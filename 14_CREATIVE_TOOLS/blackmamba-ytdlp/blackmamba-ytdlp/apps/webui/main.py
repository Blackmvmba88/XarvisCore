from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path
import yt_dlp
import subprocess
import sys

from shared import get_manager, load_config

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Descargas yt-dlp (WebUI)", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.on_event("startup")
async def startup():
    # Asegurar que el gestor tenga workers activos
    get_manager().start()
    # Montar carpeta de descargas como media para reproducir
    cfg = load_config()
    media_dir = Path(cfg.get("download_root", str(BASE_DIR))).resolve()
    try:
        app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")
    except Exception:
        # Si ya estuviera montado, ignorar
        pass

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    manager = get_manager()
    return templates.TemplateResponse("index.html", {"request": request, "jobs": manager.list_jobs()})

@app.post("/jobs")
async def create_job(urls: str = Form(...), mode: str = Form("video")):
    manager = get_manager()
    url_list = [u.strip() for u in urls.replace("\r\n"," ").replace("\n"," ").split(" ") if u.strip()]
    manager.add_job(url_list, mode)
    return RedirectResponse("/", status_code=303)

@app.get("/jobs", response_class=HTMLResponse)
async def jobs_partial(request: Request):
    manager = get_manager()
    return templates.TemplateResponse("queue.html", {"request": request, "jobs": manager.list_jobs()})

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    manager = get_manager()
    return templates.TemplateResponse("history.html", {"request": request, "history": manager.get_history()})

@app.get("/history_recent", response_class=HTMLResponse)
async def history_recent(request: Request, limit: int = 10):
    manager = get_manager()
    hist = manager.get_history() or []
    items = list(reversed(hist[-limit:])) if hist else []
    return templates.TemplateResponse("history_recent.html", {"request": request, "items": items})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = Query("") ):
    q = (q or "").strip()
    results = []
    artists = []
    if q:
        ydl_opts = {"quiet": True, "noplaylist": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{q}", download=False)
            for e in (info.get("entries") or []):
                if not e:
                    continue
                results.append({
                    "title": e.get("title"),
                    "uploader": e.get("uploader"),
                    "duration": e.get("duration"),
                    "url": e.get("webpage_url"),
                    "thumb": ((e.get("thumbnails") or [{}])[-1] or {}).get("url"),
                })
        # Artistas sugeridos por uploader únicos
        seen = set()
        for r in results:
            up = r.get("uploader")
            if up and up not in seen:
                artists.append(up)
                seen.add(up)
    return templates.TemplateResponse("search.html", {"request": request, "q": q, "results": results, "artists": artists})

@app.get("/play", response_class=HTMLResponse)
async def play(request: Request, rel: str = Query("")):
    cfg = load_config()
    root = Path(cfg.get("download_root", ".")).resolve()
    rel_path = Path(rel)
    file_path = (root / rel_path).resolve()
    # Seguridad: evitar traversal y exigir existencia
    if not str(file_path).startswith(str(root)) or not file_path.exists():
        return HTMLResponse("Archivo no disponible", status_code=404)
    ext = file_path.suffix.lower().lstrip(".")
    is_audio = ext in ["mp3","m4a","aac","opus","ogg","wav","flac"]
    is_video = ext in ["mp4","mkv","webm","mov"]
    file_url = "/media/" + rel_path.as_posix()
    return templates.TemplateResponse("play.html", {"request": request, "file_url": file_url, "file_name": file_path.name, "is_audio": is_audio, "is_video": is_video})

@app.get("/videos", response_class=HTMLResponse)
async def videos(request: Request):
    cfg = load_config()
    root = Path(cfg.get("download_root", ".")).resolve()
    video_dir = (root / "video")
    patterns = ["*.mp4", "*.mkv", "*.webm", "*.mov"]
    items = []
    if video_dir.exists():
        for pat in patterns:
            for p in video_dir.rglob(pat):
                try:
                    rel = p.resolve().relative_to(root)
                except Exception:
                    continue
                items.append({
                    "name": p.name,
                    "rel": rel.as_posix(),
                    "url": "/media/" + rel.as_posix(),
                    "size": p.stat().st_size,
                    "mtime": p.stat().st_mtime,
                })
    # ordenar por fecha reciente
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return templates.TemplateResponse("videos.html", {"request": request, "items": items})

@app.get("/meta_for")
async def meta_for(rel: str = Query("")):
    cfg = load_config()
    root = Path(cfg.get("download_root", ".")).resolve()
    rel = (rel or "").strip()
    if not rel:
        return JSONResponse({"found": False})
    # Buscar en historial por coincidencia de ruta relativa
    mgr = get_manager()
    history = mgr.get_history() or []
    found = None
    for item in history:
        for p in (item.get("output_paths") or []):
            try:
                abs_p = Path(p).resolve()
                rel_p = abs_p.relative_to(root).as_posix()
            except Exception:
                continue
            if rel_p == rel:
                found = item
                break
        if found:
            break
    if not found:
        return JSONResponse({"found": False})
    # Construir respuesta con campos útiles
    title = None
    uploader = None
    duration = None
    # Intentar extraer de nombre
    try:
        title = Path(found["output_paths"][0]).stem
    except Exception:
        title = None
    data = {
        "found": True,
        "id": found.get("id"),
        "mode": found.get("mode"),
        "status": found.get("status"),
        "title": title,
        "uploader": uploader,
        "duration": duration,
        "created_at": found.get("created_at"),
        "finished_at": found.get("finished_at"),
        "rel": rel,
    }
    return JSONResponse(data)

@app.get("/last_media")
async def last_media():
    """Devuelve el último medio completado del historial (prefiere video)."""
    mgr = get_manager()
    history = mgr.get_history() or []
    if not history:
        return JSONResponse({"found": False})
    # recorrer desde el final
    video_ext = {".mp4",".mkv",".webm",".mov"}
    audio_ext = {".mp3",".m4a",".aac",".opus",".ogg",".wav",".flac"}
    last_video = None
    last_audio = None
    for item in reversed(history):
        for p in (item.get("output_paths") or []):
            ext = Path(p).suffix.lower()
            if not last_video and ext in video_ext:
                last_video = (item, p)
            if not last_audio and ext in audio_ext:
                last_audio = (item, p)
        if last_video and last_audio:
            break
    chosen = last_video or last_audio
    if not chosen:
        return JSONResponse({"found": False})
    item, path = chosen
    cfg = load_config()
    root = Path(cfg.get("download_root", ".")).resolve()
    try:
        rel = Path(path).resolve().relative_to(root).as_posix()
    except Exception:
        rel = None
    kind = "video" if Path(path).suffix.lower() in video_ext else "audio"
    title = Path(path).stem
    return JSONResponse({"found": True, "rel": rel, "title": title, "kind": kind})

@app.post("/reveal")
async def reveal(rel: str = Form(...)):
    cfg = load_config()
    root = Path(cfg.get("download_root", ".")).resolve()
    file_path = (root / rel).resolve()
    if not str(file_path).startswith(str(root)) or not file_path.exists():
        return JSONResponse({"ok": False, "error": "not_found"}, status_code=404)
    if sys.platform == "darwin":
        try:
            subprocess.run(["open", "-R", str(file_path)], check=False)
            return JSONResponse({"ok": True})
        except Exception:
            return JSONResponse({"ok": False}, status_code=500)
    return JSONResponse({"ok": False, "error": "unsupported"}, status_code=400)

@app.post("/open_folder")
async def open_folder(rel: str = Form("")):
    cfg = load_config()
    root = Path(cfg.get("download_root", ".")).resolve()
    target = root if not rel else (root / rel).resolve().parent
    if not str(target).startswith(str(root)) or not target.exists():
        return JSONResponse({"ok": False, "error": "not_found"}, status_code=404)
    if sys.platform == "darwin":
        try:
            subprocess.run(["open", str(target)], check=False)
            return JSONResponse({"ok": True})
        except Exception:
            return JSONResponse({"ok": False}, status_code=500)
    return JSONResponse({"ok": False, "error": "unsupported"}, status_code=400)
