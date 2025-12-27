from __future__ import annotations

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Optional
import re

_TRACK_RE = re.compile(r"/(?:song|songs|track|s)/([A-Za-z0-9_-]+)")


def canonicalize_suno_url(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        p = urlparse(url.strip())
        if not p.scheme:
            return None
        netloc = (p.netloc or '').lower()
        scheme = (p.scheme or 'https').lower()
        path = re.sub(r"/+", "/", p.path or "/").rstrip("/")
        # remove tracking params
        q = [(k, v) for (k, v) in parse_qsl(p.query, keep_blank_values=False) if not k.lower().startswith("utm_")]
        query = urlencode(q)
        frag = ''
        return urlunparse((scheme, netloc, path, '', query, frag))
    except Exception:
        return None


def extract_song_id_from_url(url: str) -> str:
    try:
        p = urlparse(url)
        m = _TRACK_RE.search(p.path or '')
        if m:
            return m.group(1)
        # fallback: last segment
        segs = [s for s in (p.path or '').split('/') if s]
        return segs[-1] if segs else ''
    except Exception:
        return ''
