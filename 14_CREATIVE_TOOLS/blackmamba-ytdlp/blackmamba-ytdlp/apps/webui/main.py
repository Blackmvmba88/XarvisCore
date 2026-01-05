#!/usr/bin/env python3
"""
🎬 BlackMamba YTDLP WebUI - Robustecido y Validado
Arquitecto: Iyari Cancino Gomez
Fecha: 1 de Enero, 2026
"""

from fastapi import FastAPI, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path
import yt_dlp
import subprocess
import sys
import logging
from typing import Optional
from urllib.parse import urlparse

from shared import get_manager, load_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

# Validar que el directorio de templates exista
if not (BASE_DIR / "templates").exists():
    logger.error(f"❌ Directorio de templates no encontrado: {BASE_DIR / 'templates'}")
    raise FileNotFoundError("Templates directory missing")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="BlackMamba YTDLP WebUI",
    description="Sistema de descargas inteligente",
    version="2.0.0",
    docs_url=None,
    redoc_url=None
)

# Validar que static existe antes de montar
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning(f"⚠️ Directorio static no encontrado: {static_dir}")

# URLs válidas para descargas
VALID_DOMAINS = {
    'youtube.com', 'youtu.be', 'soundcloud.com', 'vimeo.com',
    'dailymotion.com', 'twitch.tv', 'twitter.com', 'x.com',
    'instagram.com', 'facebook.com', 'tiktok.com'
}

# Extensiones permitidas
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv'}
AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.aac', '.opus', '.ogg', '.wav', '.flac'}
ALLOWED_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

def validate_url(url: str) -> bool:
    """Valida que la URL sea segura y de un dominio permitido"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        return any(allowed in domain for allowed in VALID_DOMAINS)
    except Exception as e:
        logger.error(f"Error validando URL {url}: {e}")
        return False

def sanitize_path(base: Path, rel_path: str) -> Optional[Path]:
    """Sanitiza y valida rutas para prevenir path traversal"""
    try:
        rel_path = rel_path.strip()
        if not rel_path:
            return None
        
        full_path = (base / rel_path).resolve()
        
        # Verificar que esté dentro del directorio base
        if not str(full_path).startswith(str(base)):
            logger.warning(f"⚠️ Path traversal attempt: {rel_path}")
            return None
        
        if not full_path.exists():
            return None
        
        # Verificar extensión si es archivo
        if full_path.is_file() and full_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            logger.warning(f"⚠️ Invalid file extension: {full_path.suffix}")
            return None
        
        return full_path
    except Exception as e:
        logger.error(f"Error sanitizando path {rel_path}: {e}")
        return None

@app.on_event("startup")
async def startup():
    """Inicialización robusta del sistema"""
    logger.info("🚀 Iniciando BlackMamba YTDLP WebUI...")
    
    try:
        manager = get_manager()
        manager.start()
        logger.info("✅ Manager de descargas iniciado")
        
        cfg = load_config()
        media_dir = Path(cfg.get("download_root", str(BASE_DIR))).resolve()
        media_dir.mkdir(parents=True, exist_ok=True)
        
        if not media_dir.is_dir():
            logger.error(f"❌ Media dir no es directorio válido: {media_dir}")
            raise ValueError("Invalid media directory")
        
        try:
            app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")
            logger.info(f"✅ Media directory montado: {media_dir}")
        except RuntimeError:
            logger.info("⚠️ Media directory ya estaba montado")
        
        logger.info("✅ Sistema iniciado correctamente")
    except Exception as e:
        logger.error(f"❌ Error crítico en startup: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con validación"""
    try:
        manager = get_manager()
        jobs = manager.list_jobs() or []
        return templates.TemplateResponse("index.html", {
            "request": request,
            "jobs": jobs
        })
    except Exception as e:
        logger.error(f"Error en index: {e}")
        raise HTTPException(status_code=500, detail="Error cargando página principal")

@app.post("/jobs")
async def create_job(urls: str = Form(...), mode: str = Form("video")):
    """Crear trabajo de descarga con validación robusta"""
    try:
        if mode not in ['video', 'audio']:
            raise HTTPException(status_code=400, detail="Modo inválido")
        
        url_list = [
            u.strip() 
            for u in urls.replace("\r\n", " ").replace("\n", " ").split(" ") 
            if u.strip()
        ]
        
        if not url_list:
            raise HTTPException(status_code=400, detail="No se proporcionaron URLs válidas")
        
        valid_urls = []
        invalid_urls = []
        
        for url in url_list:
            if validate_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
                logger.warning(f"⚠️ URL inválida: {url}")
        
        if not valid_urls:
            raise HTTPException(status_code=400, detail="Ninguna URL válida")
        
        manager = get_manager()
        manager.add_job(valid_urls, mode)
        
        logger.info(f"✅ {len(valid_urls)} URLs agregadas ({mode})")
        return RedirectResponse("/", status_code=303)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando trabajo: {e}")
        raise HTTPException(status_code=500, detail="Error procesando descarga")

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
    """Reproductor con validación de seguridad robusta"""
    try:
        if not rel:
            raise HTTPException(status_code=400, detail="Ruta no especificada")
        
        cfg = load_config()
        root = Path(cfg.get("download_root", ".")).resolve()
        
        file_path = sanitize_path(root, rel)
        if not file_path or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Archivo no disponible")
        
        ext = file_path.suffix.lower().lstrip(".")
        is_audio = ext in ["mp3","m4a","aac","opus","ogg","wav","flac"]
        is_video = ext in ["mp4","mkv","webm","mov","avi","flv"]
        
        if not (is_audio or is_video):
            raise HTTPException(status_code=400, detail="Tipo no soportado")
        
        rel_path = file_path.relative_to(root)
        file_url = "/media/" + rel_path.as_posix()
        
        logger.info(f"🎬 Reproduciendo: {file_path.name}")
        
        return templates.TemplateResponse("play.html", {
            "request": request,
            "file_url": file_url,
            "file_name": file_path.name,
            "is_audio": is_audio,
            "is_video": is_video
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reproductor: {e}")
        raise HTTPException(status_code=500, detail="Error cargando reproductor")

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
