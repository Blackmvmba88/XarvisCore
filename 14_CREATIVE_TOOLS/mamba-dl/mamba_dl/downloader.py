from __future__ import annotations

import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import yt_dlp as ytdlp

from .metrics import DownloadMetrics, write_metrics


def is_url(s: str) -> bool:
    if not s:
        return False
    s = s.strip()
    if "://" in s:
        return True
    if s.startswith("www."):
        return True
    parsed = urlparse(s)
    return bool(parsed.scheme) or bool(parsed.netloc)


def format_bytes(n: Optional[float]) -> str:
    if not n:
        return "0 B"
    n = float(n)
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    i = 0
    while n >= 1024 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f"{n:.2f} {units[i]}"


def format_time(seconds: Optional[float]) -> str:
    if seconds is None:
        return "--:--"
    seconds = int(seconds)
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def parse_rate(rate: Optional[str]) -> Optional[int]:
    """
    Parse human-friendly rate like '500K', '5M', '1.5M', '2G' into bytes/sec.
    Returns None if empty.
    """
    if not rate:
        return None
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([kKmMgG]?)\s*$", rate)
    if not m:
        raise ValueError(f"Invalid rate: {rate}")
    val = float(m.group(1))
    suffix = m.group(2).lower()
    mult = 1
    if suffix == "k":
        mult = 1024
    elif suffix == "m":
        mult = 1024 ** 2
    elif suffix == "g":
        mult = 1024 ** 3
    bps = int(val * mult)
    return max(bps, 1)


@dataclass
class _Tracker:
    id: str = ""
    title: str = ""
    filename: str = ""
    url: str = ""
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    peak_speed: float = 0.0

    # info fields to stash
    duration: Optional[float] = None
    format_id: Optional[str] = None
    container: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    abr: Optional[float] = None


def _build_outtmpl(output_dir: Path) -> str:
    # yt-dlp will join directory in the template path
    return str(output_dir / "%(title).200B [%(id)s].%(ext)s")


def _make_common_opts(
    output_dir: Path,
    noplaylist: bool,
    overwrite: bool,
    ratelimit_bps: Optional[int],
    progress_hook,
) -> Dict[str, Any]:
    opts: Dict[str, Any] = {
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": _build_outtmpl(output_dir),
        "noplaylist": noplaylist,
        "continuedl": True,
        "retries": 3,
        "fragment_retries": 3,
        "progress_hooks": [progress_hook],
        "quiet": True,              # suppress yt-dlp progress; we'll print our own
        "no_warnings": True,
        "noprogress": True,
    }
    if overwrite:
        opts["overwrites"] = True
        opts["nooverwrites"] = False
    else:
        opts["overwrites"] = False
        opts["nooverwrites"] = True
    if ratelimit_bps:
        opts["ratelimit"] = ratelimit_bps
    return opts


def _print_progress_line(prefix: str, downloaded: int, total: Optional[int], speed: Optional[float], eta: Optional[float], peak: float) -> None:
    pct = ""
    if total and total > 0:
        pct_val = 100.0 * downloaded / total
        pct = f"{pct_val:6.2f}%"
    else:
        pct = "  --.--%"
    line = f"{prefix} {pct} {format_bytes(downloaded)}"
    if total:
        line += f"/{format_bytes(total)}"
    if speed:
        line += f" at {format_bytes(speed)}/s"
    if peak:
        line += f" (peak {format_bytes(peak)}/s)"
    if eta:
        line += f" ETA {format_time(eta)}"
    print(line, end="\r", flush=True)


def download(
    query_or_url: str,
    output_dir: Path,
    noplaylist: bool = False,
    overwrite: bool = False,
    limit_rate: Optional[str] = None,
) -> List[Path]:
    """
    Download the provided URL or search term.
    Returns a list of metric JSON paths (one per item).
    """
    output_dir = output_dir.expanduser()
    logs_dir = output_dir / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    ratelimit_bps = parse_rate(limit_rate) if limit_rate else None

    metric_paths: List[Path] = []

    def process_one(video_page_url: str) -> Optional[Path]:
        tracker = _Tracker(url=video_page_url)

        def hook(data: Dict[str, Any]) -> None:
            nonlocal tracker
            status = data.get("status")
            info = data.get("info_dict") or {}
            # stash basics
            tracker.id = tracker.id or info.get("id") or ""
            tracker.title = tracker.title or info.get("title") or ""
            tracker.duration = tracker.duration or info.get("duration")
            tracker.format_id = info.get("format_id") or tracker.format_id
            tracker.container = info.get("ext") or tracker.container
            tracker.width = info.get("width") or tracker.width
            tracker.height = info.get("height") or tracker.height
            tracker.fps = info.get("fps") or tracker.fps
            tracker.vcodec = info.get("vcodec") or tracker.vcodec
            tracker.acodec = info.get("acodec") or tracker.acodec
            tracker.abr = info.get("abr") or tracker.abr

            filename = data.get("filename") or info.get("_filename")
            if filename:
                tracker.filename = filename

            if status == "downloading":
                if tracker.start_ts is None:
                    tracker.start_ts = time.time()
                downloaded = int(data.get("downloaded_bytes") or 0)
                tracker.downloaded_bytes = downloaded
                total = data.get("total_bytes") or data.get("total_bytes_estimate")
                tracker.total_bytes = int(total) if total else None
                speed = data.get("speed") or 0.0
                if speed and speed > tracker.peak_speed:
                    tracker.peak_speed = float(speed)
                eta = data.get("eta")
                prefix = f"[{tracker.title or tracker.id or 'downloading'}]"
                _print_progress_line(prefix, downloaded, tracker.total_bytes, speed, eta, tracker.peak_speed)
            elif status == "finished":
                tracker.end_ts = time.time()
                # ensure newline after progress line
                print(" " * 120, end="\r")
                print(f"Finished: {tracker.title or tracker.id} -> {os.path.basename(tracker.filename) if tracker.filename else ''}")

        opts = _make_common_opts(output_dir, noplaylist=False, overwrite=overwrite, ratelimit_bps=ratelimit_bps, progress_hook=hook)

        with ytdlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(video_page_url, download=True)

        # Build metrics after download completes
        start_ts = tracker.start_ts or time.time()
        end_ts = tracker.end_ts or time.time()
        elapsed = max(end_ts - start_ts, 1e-6)
        avg_speed = tracker.downloaded_bytes / elapsed if tracker.downloaded_bytes else None

        # Confirm actual file size on disk
        filesize = None
        try:
            if tracker.filename:
                p = Path(tracker.filename)
                if p.exists():
                    filesize = p.stat().st_size
        except Exception:
            pass

        resolution = None
        if tracker.width and tracker.height:
            resolution = f"{tracker.width}x{tracker.height}"

        metrics = DownloadMetrics(
            id=tracker.id or (info.get("id") if isinstance(info, dict) else ""),
            title=tracker.title or (info.get("title") if isinstance(info, dict) else ""),
            url=video_page_url,
            filename=tracker.filename or "",
            filesize=filesize,
            duration=tracker.duration,
            downloaded_bytes=tracker.downloaded_bytes or (filesize or 0),
            average_speed=avg_speed,
            peak_speed=tracker.peak_speed or None,
            start_ts=start_ts,
            end_ts=end_ts,
            format_id=tracker.format_id,
            container=tracker.container,
            resolution=resolution,
            fps=tracker.fps,
            vcodec=tracker.vcodec,
            acodec=tracker.acodec,
            abr=tracker.abr,
            extra={},
        )
        metrics_path = write_metrics(metrics, logs_dir=logs_dir, info_dict=info if isinstance(info, dict) else None)
        print(f"Metrics written: {metrics_path}")
        return metrics_path

    # First, resolve if input is a playlist or single and expand entries
    # Use a separate extract pass (no downloads)
    def no_download_hook(_):  # dummy
        return

    pre_opts = _make_common_opts(output_dir, noplaylist=noplaylist, overwrite=overwrite, ratelimit_bps=ratelimit_bps, progress_hook=no_download_hook)
    with ytdlp.YoutubeDL(pre_opts) as ydl:
        pre_info = ydl.extract_info(query_or_url, download=False)

    entry_urls: List[str] = []
    if isinstance(pre_info, dict) and pre_info.get("_type") in {"playlist", "multi_video"}:
        entries = [e for e in pre_info.get("entries") or [] if e]
        if noplaylist:
            entries = entries[:1]
        for e in entries:
            # Prefer webpage_url, fallback to url
            u = e.get("webpage_url") or e.get("url")
            if u:
                entry_urls.append(u)
    else:
        # Single video
        # If pre_info is URL-like, use its webpage_url if present
        if isinstance(pre_info, dict):
            u = pre_info.get("webpage_url") or pre_info.get("original_url") or pre_info.get("url") or query_or_url
        else:
            u = query_or_url
        entry_urls.append(u)

    # Process each item sequentially for clean per-item metrics
    for idx, u in enumerate(entry_urls, 1):
        print(f"[{idx}/{len(entry_urls)}] Downloading: {u}")
        try:
            mp = process_one(u)
            if mp:
                metric_paths.append(mp)
        except Exception as e:
            # best-effort skip with message, continue next item
            print(f"Error downloading {u}: {e}", file=sys.stderr)

    return metric_paths
