from __future__ import annotations

import re
import time
from typing import Iterable, List, Set

import requests
from bs4 import BeautifulSoup

from .utils.url import canonicalize_suno_url

UA = {
    "User-Agent": "suno-organizer/0.1 (+https://example.local)"
}

_SONG_PAT = re.compile(r"https?://[^\s'\"]*suno[^\s'\"]*/(?:song|songs|track|s)/[^\s'\"]+", re.I)


def _extract_links_from_html(html: str, base_url: str | None = None) -> Set[str]:
    out: Set[str] = set()
    # anchors
    try:
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            if href.startswith("/"):
                if base_url:
                    from urllib.parse import urlparse, urlunparse
                    p = urlparse(base_url)
                    href = urlunparse((p.scheme, p.netloc, href, '', '', ''))
                else:
                    continue
            if "suno" in href and ("/song" in href or "/track" in href or "/s/" in href or "/songs/" in href):
                out.add(href)
        # og:url often points to the share page as well
        tag = soup.find("meta", attrs={"property": "og:url"}) or soup.find("meta", attrs={"name": "og:url"})
        if tag and tag.get("content"):
            c = tag["content"].strip()
            if "suno" in c and ("/song" in c or "/track" in c or "/s/" in c or "/songs/" in c):
                out.add(c)
    except Exception:
        pass
    # regex fallback (absolute)
    for m in _SONG_PAT.finditer(html or ""):
        out.add(m.group(0))
    # regex fallback (relative)
    try:
        import re as _re
        for m in _re.finditer(r"['\"](/(?:song|songs|track|s)/[A-Za-z0-9\-]+)['\"]", html or ""):
            if base_url:
                from urllib.parse import urlparse, urlunparse
                p = urlparse(base_url)
                href = urlunparse((p.scheme, p.netloc, m.group(1), '', '', ''))
                out.add(href)
    except Exception:
        pass
    # canonicalize
    return {canonicalize_suno_url(u) for u in out if canonicalize_suno_url(u)}


def discover_urls_from_profile(profile_url: str, max_pages: int = 50, delay_seconds: float = 0.7) -> List[str]:
    """Best-effort: obtiene enlaces de canciones desde una página de perfil pública.

    Notas: muchas páginas son dinámicas; si no están renderizadas en server, solo se obtendrán
    los enlaces presentes en el HTML estático inicial.
    """
    urls: List[str] = []
    seen_pages: Set[str] = set()
    try:
        u = canonicalize_suno_url(profile_url) or profile_url
        for i in range(max_pages):
            if u in seen_pages:
                break
            seen_pages.add(u)
            r = requests.get(u, headers=UA, timeout=20)
            r.raise_for_status()
            urls.extend(sorted(_extract_links_from_html(r.text, base_url=u)))
            # intentar paginación simple ?page=N
            if "?page=" in u:
                base = u.split("?page=")[0]
            else:
                base = u
            next_u = base + ("?page=" + str(i + 2))
            # heurística: si al solicitar next retorna 404/empty, detenemos
            try:
                rr = requests.get(next_u, headers=UA, timeout=15)
                if rr.status_code == 200 and len(rr.text) > 1024:
                    u = next_u
                    time.sleep(max(0.0, delay_seconds))
                    continue
            except Exception:
                pass
            break
    except Exception:
        pass
    # dedup manteniendo orden
    seen = set(); ordered = []
    for u in urls:
        if u not in seen:
            seen.add(u); ordered.append(u)
    return ordered


def discover_urls_from_seeds(seeds: Iterable[str], delay_seconds: float = 0.7) -> List[str]:
    out: List[str] = []
    seen = set()
    for su in seeds:
        try:
            r = requests.get(su, headers=UA, timeout=20)
            r.raise_for_status()
            links = _extract_links_from_html(r.text)
            for u in links:
                if u not in seen:
                    seen.add(u); out.append(u)
            time.sleep(max(0.0, delay_seconds))
        except Exception:
            continue
    return out
