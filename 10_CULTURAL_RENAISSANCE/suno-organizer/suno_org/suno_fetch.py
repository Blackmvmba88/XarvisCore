from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional, Tuple, Dict

import requests
from bs4 import BeautifulSoup

from .utils.naming import slugify
from .covers import fetch_cover_url_from_page
from .tags import write_tags

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
}

def extract_title_from_page(suno_url: str, timeout: int = 15) -> Optional[str]:
    try:
        r = requests.get(suno_url, headers=UA, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("meta", attrs={"property": "og:title"}) or soup.find("meta", attrs={"name": "og:title"})
        if tag and tag.get("content"):
            return tag["content"].strip()
        title = soup.title.text.strip() if soup.title else None
        return title
    except Exception:
        return None


def extract_audio_url_from_page(suno_url: str, timeout: int = 15) -> Optional[str]:
    """Try common patterns: <audio src>, og:audio, or JSON blob with audio url."""
    try:
        r = requests.get(suno_url, headers=UA, timeout=timeout)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        # audio tag
        audio = soup.find("audio")
        if audio and audio.get("src"):
            return audio["src"].strip()
        # og:audio
        tag = soup.find("meta", attrs={"property": "og:audio"}) or soup.find("meta", attrs={"name": "og:audio"})
        if tag and tag.get("content"):
            return tag["content"].strip()
        # simple regex for likely audio urls
        m = re.search(r"https?://[^'\"]+\.(?:mp3|wav|m4a)(?:\?[^'\"]*)?", html, re.I)
        if m:
            return m.group(0)
    except Exception:
        return None
    return None


def download_audio(url: str, out_dir: Path, base_name: str) -> Optional[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    # pick extension
    ext = ".mp3"
    m = re.search(r"\.(mp3|wav|m4a|aac)(?:\?|$)", url, re.I)
    if m:
        ext = "." + m.group(1).lower().replace("aac", "m4a")
    name = slugify(base_name or "suno")
    path = out_dir / f"{name}{ext}"
    # avoid overwrite
    i = 1
    while path.exists():
        path = out_dir / f"{name} ({i}){ext}"
        i += 1
    try:
        with requests.get(url, headers=UA, stream=True, timeout=30) as r:
            r.raise_for_status()
            with path.open("wb") as f:
                for chunk in r.iter_content(64 * 1024):
                    if chunk:
                        f.write(chunk)
        return path
    except Exception:
        return None


def extract_lyrics_from_page(suno_url: str, timeout: int = 15) -> Optional[str]:
    """Try to find lyrics on the shared page via og:description, JSON blobs or obvious containers."""
    try:
        r = requests.get(suno_url, headers=UA, timeout=timeout)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        # og:description often carries a summary/lyrics-like text
        tag = soup.find("meta", attrs={"property": "og:description"}) or soup.find("meta", attrs={"name": "og:description"})
        if tag and tag.get("content"):
            txt = tag["content"].strip()
            if len(txt) > 8:
                return txt
        # JSON patterns like "lyrics":"..."
        m = re.search(r'\"lyrics\"\s*:\s*\"([^\"]+)\"', html, re.I)
        if m:
            txt = m.group(1)
            txt = txt.replace("\\n", "\n")
            return txt
        # visible containers
        cand = soup.find(lambda t: t.name in {"div","p","section"} and t.get_text(strip=True) and re.search(r"lyric|letra", " ".join([t.get("class",""), t.get("id",""), t.name]), re.I))
        if cand:
            txt = cand.get_text("\n", strip=True)
            if len(txt) > 8:
                return txt
    except Exception:
        return None
    return None


def extract_bpm_from_page(suno_url: str, timeout: int = 15) -> Optional[int]:
    """Best-effort: extract BPM from page text or JSON hints.
    Patterns handled:
    - "120 bpm" or "bpm: 120"
    - JSON like "bpm":120 or "tempo":120
    """
    try:
        r = requests.get(suno_url, headers=UA, timeout=timeout)
        r.raise_for_status()
        html = r.text
        # Direct patterns
        m = re.search(r"\b(tempo|bpm)\s*[:=-]?\s*(\d{2,3})\b", html, re.I)
        if m:
            try:
                val = int(m.group(2))
                if 40 <= val <= 240:
                    return val
            except Exception:
                pass
        # JSON style
        m = re.search(r'"(?:bpm|tempo)"\s*:\s*(\d{2,3})', html)
        if m:
            try:
                val = int(m.group(1))
                if 40 <= val <= 240:
                    return val
            except Exception:
                pass
    except Exception:
        return None
    return None


def extract_created_at_from_page(suno_url: str, timeout: int = 15) -> Optional[str]:
    """Best-effort: intenta extraer fecha de creación/publicación en ISO-8601.
    Busca en meta tags (article:published_time, datePublished) o JSON embebido (created_at/createdAt/datePublished).
    """
    try:
        r = requests.get(suno_url, headers=UA, timeout=timeout)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        # meta tags comunes
        for attrs in (
            {"property": "article:published_time"},
            {"name": "article:published_time"},
            {"property": "og:published_time"},
            {"name": "date"},
            {"name": "datePublished"},
            {"itemprop": "datePublished"},
        ):
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content"):
                return tag["content"].strip()
        # JSON-LD
        for sc in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                import json
                data = json.loads(sc.string or "{}")
                if isinstance(data, dict):
                    v = data.get("datePublished") or data.get("dateCreated")
                    if v:
                        return str(v)
                elif isinstance(data, list):
                    for it in data:
                        v = it.get("datePublished") or it.get("dateCreated") if isinstance(it, dict) else None
                        if v:
                            return str(v)
            except Exception:
                pass
        # Regex genérica
        m = re.search(r'"(?:created_at|createdAt|datePublished)"\s*:\s*"([^"]+)"', html)
        if m:
            return m.group(1)
    except Exception:
        return None
    return None


def maybe_tag_after_download(audio_path: Path, title: Optional[str], cover_url: Optional[str], lyrics: Optional[str] = None) -> None:
    try:
        img_path = None
        if cover_url:
            # temp download to same folder with title
            from .covers import download_image
            img = download_image(cover_url, audio_path.parent, title or audio_path.stem)
            if img:
                write_tags(audio_path, title=title, cover_image_path=img, lyrics=lyrics)
            else:
                write_tags(audio_path, title=title, lyrics=lyrics)
        else:
            if title or lyrics:
                write_tags(audio_path, title=title, lyrics=lyrics)
    except Exception:
        pass
