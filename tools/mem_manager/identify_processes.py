#!/usr/bin/env python3
"""Herramienta ligera para identificar y marcar procesos que consumen RAM.
Uso básico:
  python identify_processes.py --list --top 20
  python identify_processes.py --filter Spotify
  python identify_processes.py --mark 20566
  python identify_processes.py --show-marked
  python identify_processes.py --suggest-quit --show-marked

Nota: Esta herramienta NO mata procesos por defecto. Para matar, usar --kill-marked con confirmación explícita.
"""

from __future__ import annotations
import argparse
import json
import os
import shlex
import subprocess
import sys
from typing import List, Dict

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")


def run_ps() -> List[Dict]:
    # ps -axo pid,rss,%cpu,comm
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


def show_procs(procs: List[Dict], top: int = 20):
    print(f"{'PID':>6}  {'RSS(MB)':>7}  {'%CPU':>5}  COMMAND")
    for p in procs[:top]:
        print(f"{p['pid']:6}  {p['rss_mb']:7}  {p['pcpu']:5.1f}  {p['comm']}")


def filter_procs(procs: List[Dict], term: str) -> List[Dict]:
    term_low = term.lower()
    return [p for p in procs if term_low in p["comm"].lower()]


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


def mark_pid(pid: int, procs: List[Dict]):
    state = load_state()
    if any(m["pid"] == pid for m in state["marked"]):
        print(f"PID {pid} ya marcado")
        return
    match = next((p for p in procs if p["pid"] == pid), None)
    entry = {"pid": pid, "comm": match["comm"] if match else "(desconocido)"}
    state["marked"].append(entry)
    save_state(state)
    print(f"Marcado PID {pid} ({entry['comm']})")


def unmark_pid(pid: int):
    state = load_state()
    before = len(state["marked"])
    state["marked"] = [m for m in state["marked"] if m["pid"] != pid]
    save_state(state)
    if len(state["marked"]) < before:
        print(f"PID {pid} desmarcado")
    else:
        print(f"PID {pid} no estaba marcado")


def show_marked():
    state = load_state()
    if not state["marked"]:
        print("No hay procesos marcados.")
        return
    print("Procesos marcados para posible cierre:")
    for m in state["marked"]:
        print(f" - PID {m['pid']}: {m['comm']}")


def suggest_quit_command(comm: str) -> str:
    low = comm.lower()
    if "spotify" in low:
        return "osascript -e 'tell application \"Spotify\" to quit'"
    if "obs" in low or "obs" in comm.lower():
        return "osascript -e 'tell application \"OBS\" to quit'"
    if "code" in low or "visual studio" in low:
        return "osascript -e 'tell application \"Visual Studio Code\" to quit'"
    if "docker" in low:
        return "osascript -e 'tell application \"Docker\" to quit'"
    if "spotify" in low:
        return "osascript -e 'tell application \"Spotify\" to quit'"
    # default: gentle kill (SIGTERM)
    return "kill -TERM <PID>"


def suggest_for_marked():
    state = load_state()
    if not state["marked"]:
        print("No hay procesos marcados.")
        return
    print("Sugerencias para cerrar procesos marcados:")
    for m in state["marked"]:
        cmd = suggest_quit_command(m["comm"])
        cmd = cmd.replace("<PID>", str(m["pid"]))
        print(f" - PID {m['pid']} ({m['comm']}): {cmd}")


def kill_marked(force: bool = False):
    state = load_state()
    if not state["marked"]:
        print("No hay procesos marcados.")
        return
    print("Se eliminarán los siguientes procesos (SIGTERM):")
    for m in state["marked"]:
        print(f" - PID {m['pid']}: {m['comm']}")
    if not force:
        c = input("Escribe 'YES' para confirmar: ")
        if c.strip() != "YES":
            print("Cancelado por usuario.")
            return
    for m in state["marked"]:
        try:
            os.kill(m["pid"], 15)
            print(f"Enviado SIGTERM a {m['pid']}")
        except Exception as e:
            print(f"Error matando {m['pid']}: {e}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Identifica y marca procesos que consumen RAM")
    p.add_argument("--list", action="store_true", help="Listar procesos (top N por RSS)")
    p.add_argument("--top", type=int, default=20, help="Cuántos procesos mostrar")
    p.add_argument("--filter", type=str, help="Filtrar por texto en el comando")
    p.add_argument("--mark", type=int, help="Marcar PID para posible cierre")
    p.add_argument("--unmark", type=int, help="Desmarcar PID")
    p.add_argument("--show-marked", action="store_true", help="Mostrar marcados")
    p.add_argument("--suggest-quit", action="store_true", help="Sugerir comando para cerrar marcados")
    p.add_argument("--kill-marked", action="store_true", help="Enviar SIGTERM a todos los marcados (pide confirmación)")
    p.add_argument("--dry-run", action="store_true", help="No hace cambios, solo muestra lo que haría")
    args = p.parse_args(argv)

    procs = run_ps()

    if args.list:
        show_procs(procs, args.top)
        return
    if args.filter:
        matches = filter_procs(procs, args.filter)
        if not matches:
            print("No se encontraron procesos que coincidan.")
            return
        show_procs(matches, args.top)
        return
    if args.mark:
        mark_pid(args.mark, procs)
        return
    if args.unmark:
        unmark_pid(args.unmark)
        return
    if args.show_marked:
        show_marked()
        return
    if args.suggest_quit:
        suggest_for_marked()
        return
    if args.kill_marked:
        if args.dry_run:
            print("Dry-run: mostraría los procesos marcados y pediría confirmación")
            show_marked()
            return
        kill_marked(force=False)
        return

    p.print_help()


if __name__ == "__main__":
    main()
