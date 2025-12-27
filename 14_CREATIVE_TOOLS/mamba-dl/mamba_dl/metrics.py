from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any
from pathlib import Path
import json
import time


@dataclass
class DownloadMetrics:
    id: str
    title: str
    url: str
    filename: str

    filesize: Optional[int] = None          # on-disk bytes
    duration: Optional[float] = None

    downloaded_bytes: int = 0               # measured via hooks
    average_speed: Optional[float] = None   # bytes/sec
    peak_speed: Optional[float] = None      # bytes/sec

    start_ts: Optional[float] = None        # epoch seconds
    end_ts: Optional[float] = None

    format_id: Optional[str] = None
    container: Optional[str] = None         # ext/container
    resolution: Optional[str] = None        # "WxH"
    fps: Optional[float] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    abr: Optional[float] = None             # audio bitrate (k)

    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


HEAVY_KEYS = {
    "formats",
    "thumbnails",
    "automatic_captions",
    "subtitles",
    "requested_formats",
    "requested_downloads",
}


def write_metrics(metrics: DownloadMetrics, logs_dir: Path, info_dict: Optional[Dict[str, Any]]) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = int(metrics.end_ts or time.time())
    vid = metrics.id or "unknown"
    path = logs_dir / f"{ts}_{vid}.json"

    payload = metrics.to_dict()
    if info_dict:
        trimmed = {}
        for k, v in info_dict.items():
            if k in HEAVY_KEYS:
                trimmed[k] = f"<omitted:{k}>"
            else:
                # yt-dlp dict is mostly JSON-serializable; fallback via str if needed
                try:
                    json.dumps(v)
                    trimmed[k] = v
                except Exception:
                    trimmed[k] = str(v)
        payload["yt_dlp_info"] = trimmed

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
