#!/usr/bin/env python3
"""API ligera para mem_manager
- GET /processes -> lista procesos clasificados por prioridad
- POST /mark -> {pid}
- POST /unmark -> {pid}
- POST /kill -> matar procesos marcados (requiere confirmación query param)
- Servir UI estática en / (archivo webui/index.html)
"""
from __future__ import annotations
import json
import os
import subprocess
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

BASE_DIR = os.path.dirname(__file__)
STATE_PATH = os.path.join(BASE_DIR, "state.json")
WEBUI_DIR = os.path.join(BASE_DIR, "webui")

app = FastAPI(title="mem_manager API")

# --- utilidades (basadas en identify_processes.py) ---

def run_ps() -> List[Dict]:
    out = subprocess.check_output(["ps", "-axo", "pid,rss,%cpu,comm"]).decode("utf-8", errors="ignore")
    lines = out.strip().splitlines()[1:]
    procs = []
    for l in lines:
        parts = l.strip().split(None, 3)
        if len(parts) < 4:
            continue
        pid, rss, pcpu, comm = parts
        try:
            procs.append({"pid": int(pid), "rss_kb": int(rss), "rss_mb": round(int(rss) / 1024), "pcpu": float(pcpu), "comm": comm})
        except Exception:
            continue
    procs.sort(key=lambda p: p["rss_kb"], reverse=True)
    return procs


def load_state() -> Dict:
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {"marked": []}
    return {"marked": []}


def save_state(state: Dict):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def classify(proc: Dict) -> str:
    """Clasifica por prioridad según RSS (MB) y reglas básicas"""
    rss = proc.get("rss_mb", 0)
    comm = proc.get("comm", "").lower()
    # excluir procesos críticos
    critical_names = ["windowserver", "kernel_task", "launchd", "loginwindow", "finder"]
    if any(c in comm for c in critical_names):
        return "critical"
    if rss >= 500:
        return "high"
    if rss >= 100:
        return "medium"
    return "low"


# Seguridad / configuración básica
WHITELIST = [
    # nombres parciales (minúsculas) que NO deben cerrarse nunca
    "windowserver",
]
BLACKLIST = [
    # si quieres forzar cierre automático de ciertas apps, añadir aquí
]

ACTIONS_LOG_KEY = "actions"


def log_action(entry: Dict):
    state = load_state()
    actions = state.get(ACTIONS_LOG_KEY, [])
    actions.insert(0, entry)  # LIFO
    # keep recent 200
    state[ACTIONS_LOG_KEY] = actions[:200]
    save_state(state)


def get_free_percent() -> float:
    try:
        pages = {}
        out = subprocess.check_output(["vm_stat"]).decode("utf-8", errors="ignore")
        for line in out.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                pages[k.strip()] = int(''.join(ch for ch in v if ch.isdigit()))
        pagesize = int(subprocess.check_output(["sysctl", "-n", "hw.pagesize"]).strip())
        total_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
        free_pages = pages.get('Pages free', 0) + pages.get('Pages speculative', 0) + pages.get('Pages purgeable', 0)
        free_bytes = free_pages * pagesize
        return round((free_bytes / total_bytes) * 100, 2)
    except Exception:
        return 0.0


# --- Monitor automático ---
import asyncio
from datetime import datetime

class Monitor:
    def __init__(self):
        self.task = None
        self.running = False
        self.config = {"threshold": 15.0, "interval": 5, "auto_kill": False}
        self.last_run = None

    async def _loop(self):
        while self.running:
            await self.run_once()
            await asyncio.sleep(self.config["interval"])

    async def run_once(self):
        """Ejecuta una sola iteración del monitor (útil para tests)."""
        free_pct = get_free_percent()
        self.last_run = {"time": datetime.utcnow().isoformat(), "free_pct": free_pct}
        if free_pct <= self.config["threshold"]:
            # encontrar candidatos
            procs = run_ps()
            for p in procs:
                p["priority"] = classify(p)
            # prefer marked processes first
            state = load_state()
            marked = {m["pid"] for m in state.get("marked", [])}
            candidates = [p for p in procs if (p["pid"] in marked or p["priority"] == 'high')]
            # filtrar críticos y whitelist
            candidates = [c for c in candidates if all(w not in c.get("comm","").lower() for w in WHITELIST) and c.get("priority") != 'critical']
            actions = []
            for c in candidates[:10]:
                cmd = suggest_command_for_comm(c.get("comm",""))
                action = {"time": datetime.utcnow().isoformat(), "pid": c["pid"], "comm": c.get("comm"), "cmd": cmd, "auto_kill": self.config["auto_kill"], "result": None}
                if self.config["auto_kill"]:
                    try:
                        # si es apple app command (osascript) ejecútalo, si no usa kill
                        if cmd.startswith('osascript'):
                            subprocess.check_call(cmd, shell=True)
                            action["result"] = "closed_soft"
                            action["reopen_cmd"] = suggest_reopen_for_comm(c.get("comm",""))
                        else:
                            os.kill(c["pid"], 15)
                            action["result"] = "killed"
                            action["reopen_cmd"] = None
                    except Exception as e:
                        action["result"] = f"error: {e}"
                else:
                    action["result"] = "would_close"
                actions.append(action)
                log_action(action)
            # if any actions, record a summary
            if actions:
                log_action({"time": datetime.utcnow().isoformat(), "summary": f"Monitor run: free={free_pct}%, actions={len(actions)}"})

    def start(self, threshold: float = None, interval: int = None, auto_kill: bool = None):
        if threshold is not None: self.config["threshold"] = float(threshold)
        if interval is not None: self.config["interval"] = int(interval)
        if auto_kill is not None: self.config["auto_kill"] = bool(auto_kill)
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._loop())
            return True
        return False

    def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            self.task = None
            return True
        return False

    def status(self):
        return {"running": self.running, "config": self.config, "last_run": self.last_run}
monitor = Monitor()


def suggest_command_for_comm(comm: str) -> str:
    c = comm.lower()
    if 'spotify' in c:
        return "osascript -e 'tell application \"Spotify\" to quit'"
    if 'docker' in c:
        return "osascript -e 'tell application \"Docker\" to quit'"
    if 'obs' in c:
        return "osascript -e 'tell application \"OBS\" to quit'"
    if 'code' in c or 'visual studio' in c:
        return "osascript -e 'tell application \"Visual Studio Code\" to quit'"
    return 'kill -TERM <PID>'


def suggest_reopen_for_comm(comm: str) -> str:
    c = comm.lower()
    if 'spotify' in c:
        return "open -a Spotify"
    if 'docker' in c:
        return "open -a Docker"
    if 'obs' in c:
        return "open -a OBS"
    if 'code' in c or 'visual studio' in c:
        return "open -a 'Visual Studio Code'"
    return ''


# --- descripción / explicador de procesos ---
KNOWN_APPS = {
    'spotify': {
        'name': 'Spotify',
        'desc': 'Cliente de música en streaming. Cerrar detendrá reproducción y sesiones locales.',
        'close_effect': 'La reproducción se detiene. Las listas y sesión permanecerán en la cuenta.',
        'reopen_cmd': 'open -a Spotify'
    },
    'docker': {
        'name': 'Docker Desktop',
        'desc': 'Daemon de contenedores. Cerrar detendrá contenedores locales.',
        'close_effect': 'Contenedores activos pueden detenerse; servicios dependientes fallarán.',
        'reopen_cmd': 'open -a Docker'
    },
    'obs': {
        'name': 'OBS',
        'desc': 'Herramienta de streaming/recording. Cerrar detendrá grabaciones/transmisiones en curso.',
        'close_effect': 'Se interrumpen grabaciones/transmisiones; es posible pérdida de datos si no se guardó.',
        'reopen_cmd': 'open -a OBS'
    },
    'code': {
        'name': 'Visual Studio Code',
        'desc': 'Editor de código. Cerrar cerrará ventanas y procesos de helper.',
        'close_effect': 'Sesiones abiertas y tareas en memoria se perderán si no guardas cambios.',
        'reopen_cmd': "open -a 'Visual Studio Code'"
    },
    'windowserver': {
        'name': 'WindowServer',
        'desc': 'Componente del sistema que gestiona las ventanas gráficas. No se debe cerrar.',
        'close_effect': 'Cerrar puede dejar el sistema inestable; no se recomienda.',
        'reopen_cmd': ''
    }
}


def describe_process(proc: Dict) -> Dict:
    """Devuelve descripción y riesgos asociados a un proceso dado (por dict de proc: pid, comm, rss_mb)."""
    comm = (proc.get('comm') or '').lower()
    for k, v in KNOWN_APPS.items():
        if k in comm:
            risk = 'critical' if classify(proc) == 'critical' or k in WHITELIST else ('disruptive' if classify(proc) == 'high' else 'noticeable' if classify(proc) == 'medium' else 'low')
            return {'name': v['name'], 'description': v['desc'], 'close_effect': v['close_effect'], 'reopen_cmd': v['reopen_cmd'], 'risk': risk}
    # Predicción genérica
    risk = 'critical' if classify(proc) == 'critical' else ('disruptive' if classify(proc) == 'high' else 'noticeable' if classify(proc) == 'medium' else 'low')
    return {'name': proc.get('comm', ''), 'description': 'Proceso no identificado; revisar comando y documentación.', 'close_effect': 'Puede detener la funcionalidad relacionada con este proceso.', 'reopen_cmd': suggest_reopen_for_comm(proc.get('comm','')), 'risk': risk}


@app.get("/processes")
async def get_processes():
    procs = run_ps()
    for p in procs:
        p["priority"] = classify(p)
    state = load_state()
    marked_pids = {m["pid"] for m in state.get("marked", [])}
    for p in procs:
        p["marked"] = p["pid"] in marked_pids
    return JSONResponse(content={"processes": procs})


class PidPayload(BaseModel):
    pid: int


@app.post('/monitor/start')
async def monitor_start(payload: dict):
    thr = payload.get('threshold')
    interval = payload.get('interval')
    auto_kill = payload.get('auto_kill')
    started = monitor.start(thr, interval, auto_kill)
    log_action({"time": datetime.utcnow().isoformat(), "monitor": "start", "config": monitor.config})
    return {"status": "started" if started else "already_running", "config": monitor.config}


@app.post('/monitor/stop')
async def monitor_stop():
    stopped = monitor.stop()
    log_action({"time": datetime.utcnow().isoformat(), "monitor": "stop"})
    return {"status": "stopped" if stopped else "not_running"}


@app.get('/monitor/status')
async def monitor_status():
    return monitor.status()


@app.get('/actions')
async def get_actions():
    state = load_state()
    return JSONResponse(content={"actions": state.get(ACTIONS_LOG_KEY, [])})


@app.get('/describe')
async def describe(pid: int):
    procs = run_ps()
    match = next((p for p in procs if p['pid'] == pid), None)
    if not match:
        raise HTTPException(status_code=404, detail='PID no encontrado')
    desc = describe_process(match)
    return JSONResponse(content=desc)

@app.post("/mark")
async def mark(payload: PidPayload):
    procs = run_ps()
    pid = payload.pid
    match = next((p for p in procs if p["pid"] == pid), None)
    if not match:
        raise HTTPException(status_code=404, detail="PID no encontrado")
    state = load_state()
    if any(m["pid"] == pid for m in state["marked"]):
        return {"status": "already"}
    state["marked"].append({"pid": pid, "comm": match["comm"]})
    save_state(state)
    return {"status": "marked"}


@app.post("/unmark")
async def unmark(payload: PidPayload):
    pid = payload.pid
    state = load_state()
    state["marked"] = [m for m in state["marked"] if m["pid"] != pid]
    save_state(state)
    return {"status": "unmarked"}


@app.get("/show_marked")
async def show_marked():
    state = load_state()
    return JSONResponse(content=state)


@app.post("/kill")
async def kill(request: Request):
    params = await request.json()
    force = params.get("force", False)
    state = load_state()
    if not state.get("marked"):
        return {"status": "no_marked"}
    results = []
    for m in state["marked"]:
        pid = m["pid"]
        try:
            os.kill(pid, 15)
            results.append({"pid": pid, "killed": True})
        except Exception as e:
            results.append({"pid": pid, "killed": False, "error": str(e)})
    # limpiar marcados que fueron matados
    state["marked"] = [m for m, r in zip(state["marked"], results) if not r.get("killed")]
    save_state(state)
    return JSONResponse(content={"results": results})


@app.post("/kill_single")
async def kill_single(payload: PidPayload, force: bool = False):
    pid = payload.pid
    procs = run_ps()
    target = next((p for p in procs if p["pid"] == pid), None)
    if not target:
        raise HTTPException(status_code=404, detail="PID no encontrado")
    # seguridad: no cerrar críticos ni whitelisted a menos que force=True
    pcomm = (target.get("comm") or "").lower()
    if any(w in pcomm for w in WHITELIST) and not force:
        raise HTTPException(status_code=403, detail="Proceso está en whitelist, requiere force=true")
    if classify(target) == "critical" and not force:
        raise HTTPException(status_code=403, detail="Proceso crítico — operación bloqueada")
    # intentar cierre suave si posible
    cmd = suggest_command_for_comm(target.get("comm",""))
    action = {"time": datetime.utcnow().isoformat(), "pid": pid, "comm": target.get("comm"), "cmd": cmd, "result": None}
    try:
        if cmd.startswith('osascript'):
            subprocess.check_call(cmd, shell=True)
            action["result"] = "closed_soft"
            action["reopen_cmd"] = suggest_reopen_for_comm(target.get("comm",""))
        else:
            os.kill(pid, 15)
            action["result"] = "killed"
            action["reopen_cmd"] = None
        # eliminar de marcados si existía
        state = load_state()
        state["marked"] = [m for m in state.get("marked", []) if m["pid"] != pid]
        save_state(state)
        log_action(action)
        return action
    except Exception as e:
        action["result"] = f"error: {e}"
        log_action(action)
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/reopen')
async def reopen(payload: dict):
    cmd = payload.get('cmd')
    if not cmd:
        raise HTTPException(status_code=400, detail='cmd required')
    try:
        subprocess.check_call(cmd, shell=True)
        log_action({"time": datetime.utcnow().isoformat(), "reopen_cmd": cmd, "result": "ok"})
        return {"status": "ok"}
    except Exception as e:
        log_action({"time": datetime.utcnow().isoformat(), "reopen_cmd": cmd, "result": f"error: {e}"})
        raise HTTPException(status_code=500, detail=str(e))


# --- servir UI estática simple ---
@app.get("/")
async def index():
    index_path = os.path.join(WEBUI_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="UI no encontrada")

@app.get("/webui/{file_path}")
async def webui_file(file_path: str):
    p = os.path.join(WEBUI_DIR, file_path)
    if os.path.exists(p):
        return FileResponse(p)
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8088)
