from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup

from .utils.naming import slugify
from .tags import write_tags


def fetch_cover_url_from_page(suno_url: str, timeout: int = 15) -> Optional[str]:
    """Fetch Suno share page and try to extract an image URL (og:image)."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
        }
        r = requests.get(suno_url, headers=headers, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("meta", attrs={"property": "og:image"}) or soup.find("meta", attrs={"name": "og:image"})
        if tag and tag.get("content"):
            return tag["content"].strip()
        # fallback: simple regex for og:image
        m = re.search(r"<meta[^>]+property=['\"]og:image['\"][^>]+content=['\"]([^'\"]+)['\"]", r.text, re.I)
        if m:
            return m.group(1)
    except Exception:
        return None
    return None


def download_image(url: str, out_dir: Path, base_name: str) -> Optional[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = ".jpg"
    # naive extension detection
    m = re.search(r"\.(png|jpg|jpeg|webp)(?:\?|$)", url, re.I)
    if m:
        ext = "." + m.group(1).lower().replace("jpeg", "jpg")
    name = slugify(base_name or "cover")
    path = out_dir / f"{name}{ext}"
    try:
        with requests.get(url, stream=True, timeout=20) as r:
            r.raise_for_status()
            with path.open("wb") as f:
                for chunk in r.iter_content(64 * 1024):
                    if chunk:
                        f.write(chunk)
        return path
    except Exception:
        return None


def maybe_write_tag(audio_path: Path, title: Optional[str], img_path: Path, apply: bool) -> bool:
    if not apply:
        return False
    try:
        return write_tags(audio_path, title=title, cover_image_path=img_path)
    except Exception:
        return False