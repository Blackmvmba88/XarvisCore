#!/usr/bin/env python3
"""RAM Guardian daemon for macOS

Features:
- monitors free + inactive memory (vm_stat) and compares to total memory
- notifies user via macOS notification when memory is low
- optionally attempts graceful quits or kills heavy processes (disabled by default)
- safe defaults: dry-run enabled, actions disabled until explicitly allowed
- logging to /tmp/ram_guardian.log
"""

from __future__ import annotations
import argparse
import logging
import os
import signal
import subprocess
import sys
import time, json
import fcntl
import tempfile
from datetime import datetime
from typing import List, Tuple

PAGE_SIZE = 4096
LOG_PATH = "/tmp/ram_guardian.log"
RUNNING = True

logger = logging.getLogger("ram_guardian")


def setup_logging():
    handler = logging.FileHandler(LOG_PATH)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def run_cmd(cmd: List[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError:
        logger.exception("command failed: %s", cmd)
        raise
    except FileNotFoundError:
        logger.exception("command not found: %s", cmd)
        raise


def parse_vm_stat(vm_out: str) -> Tuple[int, int]:
    """Parse vm_stat output and return (free_pages, inactive_pages)"""
    free = inactive = 0
    for line in vm_out.splitlines():
        if "Pages free" in line:
            try:
                free = int(line.split(":")[1].strip().strip("."))
            except ValueError:
                logger.exception("Failed parsing free pages line: %s", line)
        elif "Pages inactive" in line:
            try:
                inactive = int(line.split(":")[1].strip().strip("."))
            except ValueError:
                logger.exception("Failed parsing inactive pages line: %s", line)
    return free, inactive


def validate_args(args) -> None:
    if args.interval < 5:
        raise SystemExit("--interval must be >= 5 seconds")
    if not (0.0 < args.threshold < 0.5):
        raise SystemExit("--threshold must be between 0 and 0.5")
    if args.measure_timeout < 1:
        raise SystemExit("--measure-timeout must be >= 1 second")


def is_action_approved(args) -> bool:
    """Check if actions are approved either by --enable-actions and optionally by an approval file existing."""
    if not args.enable_actions:
        return False
    if args.approval_file:
        return os.path.exists(args.approval_file)
    return True


def total_memory_bytes() -> int:
    out = run_cmd(["sysctl", "-n", "hw.memsize"]).strip()
    return int(out)


def free_inactive_bytes() -> int:
    vm = run_cmd(["vm_stat"])  # may raise
    free_pages, inactive_pages = parse_vm_stat(vm)
    return (free_pages + inactive_pages) * PAGE_SIZE


def available_fraction() -> float:
    try:
        return free_inactive_bytes() / total_memory_bytes()
    except Exception as e:
        logger.exception("Error checking memory: %s", e)
        return 0.0


def top_memory_procs(n: int = 5) -> List[Tuple[int, str, int]]:
    """Return list of (pid, comm, rss_bytes) sorted by RSS desc"""
    out = run_cmd(["ps", "-axo", "pid,comm,rss"])  # rss in KB
    rows = []
    for line in out.splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) >= 3:
            try:
                pid = int(parts[0])
                comm = parts[1]
                rss_kb = int(parts[2])
                rows.append((pid, comm, rss_kb * 1024))
            except ValueError:
                continue
    rows.sort(key=lambda r: r[2], reverse=True)
    return rows[:n]


def notify(msg: str) -> None:
    try:
        subprocess.call(["osascript", "-e", f'display notification "{msg}" with title "RAM Guardian"'])
    except Exception:
        logger.exception("notify failed")


def quit_app_by_name(name: str) -> None:
    try:
        subprocess.call(["osascript", "-e", f'tell application \"{name}\" to quit'])
    except Exception:
        logger.exception("quit_app failed for %s", name)


def kill_pid(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        os.kill(pid, signal.SIGKILL)
    except Exception:
        logger.exception("kill_pid failed for %s", pid)


def get_memory_snapshot_bytes() -> int:
    """Return free + inactive bytes snapshot"""
    try:
        return free_inactive_bytes()
    except Exception:
        logger.exception("get_memory_snapshot failed")
        return 0


def append_metric_entry(entry: dict, path: str = "/tmp/ram_guardian_metrics.jsonl") -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        # if dirname is empty or other error, proceed to open file directly
        pass
    try:
        with open(path, "a+", encoding="utf-8") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
            except Exception:
                logger.exception("Failed to acquire file lock for %s", path)
            f.seek(0, os.SEEK_END)
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
            try:
                fcntl.flock(f, fcntl.LOCK_UN)
            except Exception:
                logger.exception("Failed to release file lock for %s", path)
    except Exception:
        logger.exception("Failed to append metric entry")


def notify(msg: str) -> bool:
    try:
        subprocess.call(["osascript", "-e", f'display notification "{msg}" with title "RAM Guardian"'])
        return True
    except FileNotFoundError:
        logger.warning("osascript not found: skipping notification")
    except Exception:
        logger.exception("notify failed")
    return False


def perform_action_and_measure(action_callable, timeout: int = 10, poll_interval: float = 1.0) -> dict:
    """Perform action (callable) and measure memory before/after. Returns info dict."""
    pre = get_memory_snapshot_bytes()
    start = time.time()
    try:
        action_callable()
    except Exception:
        logger.exception("Action callable raised exception")
    elapsed = 0.0
    post = pre
    success = False
    while elapsed < timeout:
        post = get_memory_snapshot_bytes()
        if post != pre and post > pre:
            success = True
            break
        time.sleep(poll_interval)
        elapsed = time.time() - start
    delta = post - pre
    info = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "pre_free_bytes": pre,
        "post_free_bytes": post,
        "delta_bytes": delta,
        "duration_seconds": round(time.time() - start, 2),
        "success": success,
    }
    return info


def estimate_rss_sum(procs: List[Tuple[int, str, int]]) -> int:
    """Estimate sum of RSS bytes from process list"""
    return sum(p[2] for p in procs)


def handle_signals(_signum, _frame):
    global RUNNING
    RUNNING = False
    logger.info("Received signal to stop")


def main():
    parser = argparse.ArgumentParser(description="RAM Guardian daemon (macOS)")
    parser.add_argument("--interval", type=int, default=60, help="check interval in seconds")
    parser.add_argument("--threshold", type=float, default=0.15, help="available fraction threshold (e.g., 0.15 = 15%)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="do not kill/quit processes by default")
    parser.add_argument("--enable-actions", action="store_true", help="allow actions like quit/kill (use with care)")
    parser.add_argument("--aggressiveness", type=int, default=0, choices=[0, 1], help="0=conservative,1=aggressive")
    parser.add_argument("--metrics-path", default="/tmp/ram_guardian_metrics.jsonl", help="path to append JSON metrics")
    parser.add_argument("--measure-timeout", type=int, default=10, help="seconds to wait for memory change after action")
    parser.add_argument("--approval-file", default="", help="optional file path whose existence approves automatic actions")
    args = parser.parse_args()
    
    validate_args(args)
    setup_logging()
    logger.info("Starting ram_guardian (interval=%s threshold=%s dry_run=%s enable_actions=%s approval_file=%s)", args.interval, args.threshold, args.dry_run, args.enable_actions, args.approval_file)
    signal.signal(signal.SIGINT, handle_signals)

    consecutive = 0
    while RUNNING:
        frac = available_fraction()
        logger.info("available fraction: %.3f", frac)
        if frac < args.threshold:
            consecutive += 1
            msg = f"Memoria baja: {frac*100:.1f}% disponible (umbral {args.threshold*100:.0f}%)"
            logger.warning(msg)
            notify(msg)
            procs = top_memory_procs(5)
            logger.info("Top memory processes: %s", procs)
            if consecutive >= 2:
                # identify candidates: graceful app quits and potential aggressive kill
                candidates = []
                for name in ("Google Chrome", "Safari", "Firefox", "Chromium"):
                    if any(name.lower() in p[1].lower() for p in procs):
                        candidates.append(("app", name))
                if args.aggressiveness >= 1:
                    for pid, comm, rss in procs:
                        if "kernel" in comm.lower():
                            continue
                        candidates.append(("kill", pid, comm, rss))
                        break

                if args.dry_run or not args.enable_actions:
                    # dry-run: estimate potential freed memory from RSS of matching procs
                    matched = [p for p in procs if any(p[1].lower().find(name.lower()) != -1 for name in ("Google Chrome", "Safari", "Firefox", "Chromium"))]
                    est = estimate_rss_sum(matched)
                    logger.info("Dry-run mode: estimated potential freed bytes: %d", est)
                    notify(f"Estimated potential free: {est//1024} KB")
                else:
                    # perform actions and measure results
                    for c in candidates:
                        if c[0] == "app":
                            name = c[1]
                            logger.info("Attempting graceful quit of %s", name)
                            info = perform_action_and_measure(lambda: quit_app_by_name(name), timeout=args.measure_timeout)
                            info["action"] = "quit_app"
                            info["target"] = name
                            logger.info("Action result: %s", info)
                            append_metric_entry(info, path=args.metrics_path)
                            if info["success"]:
                                notify(f"Quit {name}: freed {info['delta_bytes']//1024} KB")
                        elif c[0] == "kill":
                            pid = c[1]; comm = c[2]; rss = c[3]
                            logger.info("Aggressive kill: pid=%s comm=%s rss=%s", pid, comm, rss)
                            info = perform_action_and_measure(lambda: kill_pid(pid), timeout=args.measure_timeout)
                            info["action"] = "kill_pid"
                            info["target"] = pid
                            logger.info("Action result: %s", info)
                            append_metric_entry(info, path=args.metrics_path)
                            if info["success"]:
                                notify(f"Killed pid {pid}: freed {info['delta_bytes']//1024} KB")
        else:
            consecutive = 0
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
