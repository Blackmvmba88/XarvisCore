from __future__ import annotations

from pathlib import Path
from typing import List, Set


def collect_song_urls_via_browser(profile_url: str, limit: int | None = None, headless: bool = False, max_scrolls: int = 600, wait_ms: int = 700, linger_seconds: int = 0, storage_path: Path | None = None, pages: int = 200, strategy: str = "hybrid") -> List[str]:
    """
    Usa Playwright para abrir el perfil/listado y recolectar enlaces a canciones (/song/...).
    - No descarga audio; solo lee el DOM tras ejecutar JS de la página.
    - `headless=False` para permitir login manual si Suno lo pide.
    - strategy: "scroll" (solo scroll infinito), "paginate" (solo ?page=N), "hybrid" (ambas).
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("Playwright no está instalado") from e

    def canonicalize(u: str) -> str:
        try:
            from .utils.url import canonicalize_suno_url
            return canonicalize_suno_url(u) or ""
        except Exception:
            return u

    out: List[str] = []
    seen: Set[str] = set()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        ctx_args = {}
        if storage_path and Path(storage_path).exists():
            ctx_args["storage_state"] = str(storage_path)
        ctx = browser.new_context(**ctx_args)
        page = ctx.new_page()
        page.set_default_timeout(20000)
        page.goto(profile_url, wait_until="load")
        # Intentar pequeñas esperas iniciales por contenido lazy
        page.wait_for_timeout(1200)
        patience = 0
        # Tiempo adicional para que el usuario pueda iniciar sesión y/o cargar más contenido manualmente (scroll infinito)
        if linger_seconds and linger_seconds > 0:
            # Escanear de forma continua durante el tiempo indicado
            import time
            deadline = time.time() + linger_seconds
            while time.time() < deadline:
                try:
                    hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href).filter(h => h && h.includes('/song/'))")
                except Exception:
                    hrefs = []
                for h in hrefs or []:
                    cu = canonicalize(h)
                    if cu and cu not in seen:
                        seen.add(cu); out.append(cu)
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                except Exception:
                    pass
                page.wait_for_timeout(wait_ms)
            # tras linger, seguimos con el bucle normal por si queda algo
        for i in range(max_scrolls if strategy in ("scroll", "hybrid") else 0):
            # extraer hrefs actuales
            try:
                hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href).filter(h => h && h.includes('/song/'))")
            except Exception:
                hrefs = []
            added = 0
            for h in hrefs or []:
                cu = canonicalize(h)
                if cu and cu not in seen:
                    seen.add(cu)
                    out.append(cu)
                    added += 1
                    if limit and len(out) >= limit:
                        break
            # detener si llegamos al límite
            if limit and len(out) >= limit:
                break
            # scroll down
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            except Exception:
                pass
            page.wait_for_timeout(wait_ms)
            # si no aparecen nuevos links varias veces, cortar
            if added == 0:
                patience += 1
            else:
                patience = 0
            if patience >= 5:
                break
        # Paginación por parámetros ?page=N (intenta varias variantes)
        from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
        start_url = page.url or profile_url
        def build_url(base: str, page_no: int) -> List[str]:
            cands: List[str] = []
            p = urlparse(base)
            q = dict(parse_qsl(p.query))
            # 1) añadir page
            q1 = q.copy(); q1["page"] = str(page_no)
            cands.append(urlunparse((p.scheme, p.netloc, p.path, '', urlencode(q1), '')))
            # 2) wid=default
            q2 = q.copy(); q2.setdefault("wid", "default"); q2["page"] = str(page_no)
            cands.append(urlunparse((p.scheme, p.netloc, p.path, '', urlencode(q2), '')))
            # 3) tab=songs
            q3 = q.copy(); q3.setdefault("tab", "songs"); q3["page"] = str(page_no)
            cands.append(urlunparse((p.scheme, p.netloc, p.path, '', urlencode(q3), '')))
            return cands
        if strategy in ("paginate", "hybrid"):
            no_gain_rounds = 0
            for n in range(1, max(1, pages)+1):
                before = len(seen)
                for cand in build_url(start_url, n):
                    try:
                        page.goto(cand, wait_until="load")
                        page.wait_for_timeout(500)
                        try:
                            hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href).filter(h => h && h.includes('/song/'))")
                        except Exception:
                            hrefs = []
                        for h in hrefs or []:
                            cu = canonicalize(h)
                            if cu and cu not in seen:
                                seen.add(cu); out.append(cu)
                    except Exception:
                        continue
                after = len(seen)
                if after == before:
                    no_gain_rounds += 1
                    if no_gain_rounds >= 3:
                        break
                else:
                    no_gain_rounds = 0
        # Guardar estado de sesión (cookies/localStorage) para futuros runs
        try:
            if storage_path:
                ctx.storage_state(path=str(storage_path))
        except Exception:
            pass
        browser.close()
    # dedup manteniendo orden ya está en out/seen
    return out