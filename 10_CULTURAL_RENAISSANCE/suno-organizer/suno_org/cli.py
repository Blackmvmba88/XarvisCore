from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from . import __version__
from .config import (
    AUDIO_EXTS,
    DEFAULT_AUDIO_ROOTS,
    DUP_DIR,
    INDEX_CSV,
    INDEX_JSON,
    INSTALLERS_DIR,
    ScanOptions,
    SCRIPTS_DIR,
    SUNO_ROOT,
)
from .scan import scan_audio, save_indexes, print_table, group_duplicates
from .utils.fs import ensure_dir, safe_move, deconflict_name, walk_files
from .utils.naming import slugify
from .report import write_csv, write_json, write_m3u
from .manifest import build_title_manifest, write_title_manifest
from .tags import write_tags
from .covers import fetch_cover_url_from_page, download_image, maybe_write_tag
from .suno_fetch import extract_audio_url_from_page, extract_title_from_page, download_audio, maybe_tag_after_download, extract_lyrics_from_page
from .discovery import discover_urls_from_profile, discover_urls_from_seeds
from .utils.url import canonicalize_suno_url
from .history import collect_suno_urls_from_browsers
from .browser_collect import collect_song_urls_via_browser

app = typer.Typer(add_completion=False, help="suno-org: listar y organizar descargas de Suno con índice y dedupe.")


@app.callback()
def _version(ctx: typer.Context, version: Optional[bool] = typer.Option(None, "--version", callback=None, is_eager=True, help="Mostrar versión y salir.")):
    if version:
        typer.echo(f"suno-org v{__version__}")
        raise typer.Exit()


@app.command()
def list_suno(
    roots: List[Path] = typer.Option(None, "--roots", help="Directorios raíz a escanear (por defecto: Downloads, Desktop, Documents, Music)", show_default=False),
    limit: int = typer.Option(50, help="Límite de filas a mostrar"),
):
    """Escanea audios y muestra una tabla de posibles archivos Suno."""
    opts = ScanOptions(roots=roots or DEFAULT_AUDIO_ROOTS, fingerprint=False)
    rows = scan_audio(opts)
    # Marcar 'pinned' si corresponde
    try:
        from .pins import annotate_pins
        rows = annotate_pins(rows)
    except Exception:
        pass
    # Filtrar solo Suno-likes
    rows = [r for r in rows if r.suno_like]
    print_table(rows, limit=limit)


@app.command()
def scan_audio_cmd(
    roots: List[Path] = typer.Option(None, "--roots", help="Directorios raíz a escanear"),
    fingerprint: bool = typer.Option(False, "--fingerprint", help="Calcular huella (requiere fpcalc)"),
    out_json: Optional[Path] = typer.Option(None, "--out-json", help=f"Ruta JSON (por defecto: {INDEX_JSON})"),
    out_csv: Optional[Path] = typer.Option(None, "--out-csv", help=f"Ruta CSV (por defecto: {INDEX_CSV})"),
):
    """Escanea audios y guarda índices CSV/JSON."""
    opts = ScanOptions(roots=roots or DEFAULT_AUDIO_ROOTS, fingerprint=fingerprint)
    rows = scan_audio(opts)
    try:
        from .pins import annotate_pins
        rows = annotate_pins(rows)
    except Exception:
        pass
    save_indexes(rows, json_path=out_json or INDEX_JSON, csv_path=out_csv or INDEX_CSV)
    typer.echo(f"Listo. Índices escritos en {(out_json or INDEX_JSON)} y {(out_csv or INDEX_CSV)}")


@app.command()
def dedupe(
    from_index: Optional[Path] = typer.Option(None, "--from-index", help="Usar índice JSON existente (si no, escanea)"),
    apply: bool = typer.Option(False, "--apply", help="Mover duplicados (por defecto solo simula)"),
    duplicates_dir: Path = typer.Option(DUP_DIR, "--duplicates-dir", help="Dónde mover duplicados"),
):
    """Detecta duplicados por huella (Chromaprint) o, si no hay, por hash de archivo.
    Por defecto, solo informa. Con --apply, mueve a .Duplicates sin borrar nada.
    """
    if from_index and from_index.exists():
        import json
        rows_data = json.loads(from_index.read_text())
        from .scan import AudioRow
        rows = [AudioRow(**d) for d in rows_data]
    else:
        rows = scan_audio(ScanOptions(roots=DEFAULT_AUDIO_ROOTS, fingerprint=True))
    # Anotar pines, si existen, para respetarlos
    try:
        from .pins import annotate_pins
        rows = annotate_pins(rows)
    except Exception:
        pass

    groups = group_duplicates(rows)
    total_groups = len(groups)
    total_files = sum(len(v) for v in groups.values())
    typer.echo(f"Grupos de duplicados: {total_groups} (archivos involucrados: {total_files})")
    if not groups:
        return

    ensure_dir(duplicates_dir)
    for key, items in groups.items():
        # Si hay pines en el grupo, conservar el primero pineado; si hay varios, aplicar regla secundaria
        pinned_items = [r for r in items if getattr(r, "pinned", False)]
        if pinned_items:
            keeper = sorted(pinned_items, key=lambda r: (-r.size_bytes, r.created_at))[0]
        else:
            # Regla: conservar el más grande; si empatan, el más antiguo
            keeper = sorted(items, key=lambda r: (-r.size_bytes, r.created_at))[0]
        to_move = [r for r in items if r is not keeper and not getattr(r, "pinned", False)]
        skipped = [r for r in items if getattr(r, "pinned", False) and r is not keeper]
        typer.echo(f"- Grupo {key[:12]}… mantener: {keeper.file_name} ({len(to_move)} mover, {len(skipped)} protegidos)")
        if apply:
            for r in to_move:
                src = Path(r.file_path)
                dst = deconflict_name(duplicates_dir, src.name)
                final = safe_move(src, dst)
                typer.echo(f"  movido -> {final}")


@app.command()
def move_suno(
    dest: Path = typer.Option(SUNO_ROOT, "--dest", help="Destino para audios de Suno"),
    rename: bool = typer.Option(False, "--rename", help="Renombrar a patrón limpio"),
    apply: bool = typer.Option(False, "--apply", help="Aplicar (por defecto dry-run)"),
    skip_pinned: bool = typer.Option(True, "--skip-pinned/--no-skip-pinned", help="No mover/renombrar los favoritos (pines)"),
):
    """Mover audios detectados como Suno a la carpeta destino. Renombrar opcional."""
    from .utils.naming import build_suno_filename
    rows = scan_audio(ScanOptions(roots=DEFAULT_AUDIO_ROOTS, fingerprint=False))
    # Anotar pines para respetarlos si corresponde
    try:
        from .pins import annotate_pins
        rows = annotate_pins(rows)
    except Exception:
        pass
    suno_rows = [r for r in rows if r.suno_like and (not (skip_pinned and getattr(r, "pinned", False)))]
    ensure_dir(dest)

    moved = 0
    for r in suno_rows:
        src = Path(r.file_path)
        ext = src.suffix
        created_dt = datetime.fromisoformat(r.created_at)
        new_name = src.name
        if rename:
            title = r.file_name.rsplit('.', 1)[0]
            new_name = build_suno_filename(created_dt, title, ext)
        dst = deconflict_name(dest, new_name)
        if apply:
            final = safe_move(src, dst)
            typer.echo(f"movido: {src} -> {final}")
            moved += 1
        else:
            typer.echo(f"simular: {src} -> {dst}")
    typer.echo(f"Listo. {'Movidos' if apply else 'Simulados'}: {moved if apply else len(suno_rows)}")


@app.command()
def pin(
    patterns: List[str] = typer.Argument(None, help="Patrones (regex simples) o rutas para marcar como favoritos/pines"),
    from_index: Optional[Path] = typer.Option(None, "--from-index", help="Índice JSON para resolver coincidencias (si no, escanea)"),
    all_suno: bool = typer.Option(False, "--all-suno", help="Pinear todos los detectados como Suno"),
):
    """Marca archivos como favoritos (pines) para protegerlos de dedupe/movimientos y facilitar exportar offline."""
    from .scan import AudioRow
    if from_index and from_index.exists():
        import json
        rows_data = json.loads(from_index.read_text())
        rows = [AudioRow(**d) for d in rows_data]
    else:
        rows = scan_audio(ScanOptions(roots=DEFAULT_AUDIO_ROOTS, fingerprint=False))
    try:
        from .pins import add_pins_by_patterns
        added = add_pins_by_patterns(rows, patterns or [], all_suno=all_suno)
        typer.echo(f"Pines añadidos: {added}")
    except Exception as e:
        typer.echo(f"Error al añadir pines: {e}")


@app.command()
def list_pins():
    """Lista los elementos marcados como favoritos/pines."""
    try:
        from .pins import load_pins
        pins = load_pins().get("entries", [])
        typer.echo(f"Total pines: {len(pins)}")
        for p in pins[:100]:
            typer.echo(f" - {p.get('file_name','?')} :: {p.get('file_path','?')}")
        if len(pins) > 100:
            typer.echo(f"... {len(pins)-100} más")
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
def export_pins(
    out_dir: Path = typer.Option(SUNO_ROOT / "Favorites", "--out-dir", help="Dónde copiar favoritos"),
    zip_pack: bool = typer.Option(False, "--zip", help="Crear .zip del paquete exportado"),
):
    """Copia los favoritos/pines a una carpeta para uso offline; puede generar un .zip + playlist."""
    ensure_dir(out_dir)
    try:
        from .pins import resolve_pins_to_rows
        rows = scan_audio(ScanOptions(roots=DEFAULT_AUDIO_ROOTS, fingerprint=False))
        rows = resolve_pins_to_rows(rows)
        # Copiar archivos
        copied_paths = []
        for r in rows:
            src = Path(r.file_path)
            dst = deconflict_name(out_dir, src.name)
            final = safe_move(src, dst) if False else dst  # no mover por defecto; copiamos con shutil.copy2 si quisiéramos
            # Usamos copia conservando original
            import shutil
            shutil.copy2(src, final)
            copied_paths.append(final)
        # Manifest
        manifest_json = out_dir / "manifest.json"
        write_json(manifest_json, ({k: getattr(r, k) for k in r.__dict__} for r in rows))
        # Playlist
        write_m3u(out_dir / "playlist.m3u", copied_paths)
        # Zip opcional
        if zip_pack:
            import shutil
            base_name = str(out_dir) + "_pack"
            shutil.make_archive(base_name, 'zip', root_dir=out_dir)
            typer.echo(f"ZIP creado: {base_name}.zip")
        typer.echo(f"Exportados {len(copied_paths)} favoritos a {out_dir}")
    except Exception as e:
        typer.echo(f"Error exportando pines: {e}")


@app.command()
def suggest_titles(
    from_index: Optional[Path] = typer.Option(None, "--from-index", help="Usar índice JSON existente (si no, escanea)"),
    use_lyrics: bool = typer.Option(False, "--use-lyrics", help="Intentar transcribir un extracto con Whisper (requiere faster-whisper)"),
    max_duration: int = typer.Option(45, "--max-duration", help="Segundos a transcribir"),
    limit: Optional[int] = typer.Option(100, "--limit", help="Límite de archivos a sugerir (None = todos)"),
):
    """Genera un manifiesto con títulos sugeridos a partir de letras (si disponibles) y nombre de archivo."""
    if from_index and from_index.exists():
        import json
        rows_data = json.loads(from_index.read_text())
        from .scan import AudioRow
        rows = [AudioRow(**d) for d in rows_data]
    else:
        rows = scan_audio(ScanOptions(roots=DEFAULT_AUDIO_ROOTS, fingerprint=False))
    # Filtrar Suno-likes primero para foco
    rows = [r for r in rows if r.suno_like]
    manifest_rows = build_title_manifest(rows, use_lyrics=use_lyrics, max_duration_sec=max_duration, limit=limit)
    paths = write_title_manifest(manifest_rows)
    typer.echo(f"Listo. Manifiestos: {paths['csv']} y {paths['json']}")


@app.command()
def write_tags_from_manifest(
    manifest_csv: Path = typer.Argument(..., help="Ruta a suno_manifest.csv"),
    apply: bool = typer.Option(False, "--apply", help="Aplicar escritura de tags"),
):
    """Escribe tags (título/género/letras/portada) en los archivos según el manifiesto CSV."""
    import csv
    rows = []
    with manifest_csv.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    ok = 0
    for row in rows:
        p = Path(row["file_path"]).expanduser()
        title = row.get("proposed_title") or None
        genre = row.get("genre_guess") or None
        lyrics = row.get("lyrics_excerpt") or None
        cover = row.get("cover_image") or None
        cover_path = Path(cover).expanduser() if cover else None
        if apply:
            if write_tags(p, title=title, genre=genre, lyrics=lyrics, cover_image_path=cover_path):
                ok += 1
        else:
            typer.echo(f"simular: escribir tags en {p} -> title={title} genre={genre} lyrics={'yes' if lyrics else 'no'} cover={'yes' if cover else 'no'}")
    typer.echo(f"Listo. {'Escritos' if apply else 'Simulados'}: {ok if apply else len(rows)} archivos")


@app.command()
def rename_from_manifest(
    manifest_csv: Path = typer.Argument(..., help="Ruta a suno_manifest.csv"),
    apply: bool = typer.Option(False, "--apply", help="Aplicar renombrado"),
    dest: Optional[Path] = typer.Option(None, "--dest", help="Destino para mover; por defecto mismo directorio"),
    skip_pinned: bool = typer.Option(True, "--skip-pinned/--no-skip-pinned", help="No renombrar/mover favoritos"),
):
    """Renombra/mueve archivos según los títulos propuestos en el manifiesto."""
    import csv
    from .utils.naming import build_suno_filename
    # Construir índice de pines
    try:
        from .pins import load_pins
        pin_paths = {e.get('file_path') for e in load_pins().get('entries', [])}
    except Exception:
        pin_paths = set()

    with manifest_csv.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            src = Path(row["file_path"]).expanduser()
            if skip_pinned and str(src) in pin_paths:
                continue
            title = row.get("proposed_title")
            if not title:
                continue
            created = src.stat().st_ctime
            from datetime import datetime
            new_name = build_suno_filename(datetime.fromtimestamp(created), title, src.suffix)
            target_dir = (dest or src.parent)
            dst = deconflict_name(target_dir, new_name)
            if apply:
                final = safe_move(src, dst)
                typer.echo(f"renombrado/movido: {src} -> {final}")
            else:
                typer.echo(f"simular: {src} -> {dst}")


@app.command()
def fetch_suno_audio(
    manifest_csv: Optional[Path] = typer.Option(None, "--manifest", help="CSV con columna 'suno_url'"),
    urls: List[str] = typer.Argument(None, help="URLs de Suno a descargar"),
    out_dir: Path = typer.Option(SUNO_ROOT / "suno_downloads", "--out-dir", help="Dónde guardar el audio"),
    write_tags_opt: bool = typer.Option(False, "--write-tags", help="Escribir título/portada en tags"),
    apply: bool = typer.Option(False, "--apply", help="Descargar y actualizar CSV (por defecto: simulación)"),
):
    """Descarga audio desde páginas compartidas de Suno (uso personal) y actualiza el CSV.

    Fuentes:
    - Argumentos URLs
    - O --manifest con columna 'suno_url'.

    Escribe archivos en --out-dir. Si --manifest está presente, completa file_path/file_name y proposed_title si falta.
    """
    import csv

    url_list: List[str] = []
    rows: List[dict] = []
    if manifest_csv and manifest_csv.exists():
        with manifest_csv.open("r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append(row)
                su = (row.get("suno_url") or "").strip()
                if su:
                    url_list.append(su)
    if urls:
        url_list.extend(urls)

    # dedupe keep order
    seen = set(); ordered_urls = []
    for u in url_list:
        if u not in seen:
            seen.add(u); ordered_urls.append(u)

    planned = []
    completed: List[Tuple[str, Optional[Path]]] = []

    for su in ordered_urls:
        au = extract_audio_url_from_page(su)
        ti = extract_title_from_page(su) or "suno"
        cu = fetch_cover_url_from_page(su)
        ly = extract_lyrics_from_page(su)
        if not au:
            typer.echo(f"No se encontró audio en: {su}")
            continue
        if not apply:
            planned.append((su, ti, au, cu, ly))
        else:
            p = download_audio(au, out_dir, ti)
            completed.append((su, p))
            if p and write_tags_opt:
                maybe_tag_after_download(p, ti, cu, ly)
            if p and rows:
                # try to update first matching row by suno_url
                for row in rows:
                    if (row.get("suno_url") or "").strip() == su:
                        row["file_path"] = str(p)
                        row["file_name"] = Path(p).name
                        if not row.get("proposed_title"):
                            row["proposed_title"] = ti
                        if cu and not (row.get("cover_image") or "").strip():
                            row["cover_image"] = cu  # store URL; can be fetched later
                        if ly and not (row.get("lyrics_excerpt") or "").strip():
                            row["lyrics_excerpt"] = ly[:200]
                        break

    if not apply:
        typer.echo(f"Simulación: {len(planned)} audios a descargar")
        for (su, ti, au, cu, ly) in planned[:20]:
            preview = (ly or "").splitlines()[0][:80] if ly else "-"
            typer.echo(f" - {ti}\n   {su}\n   -> audio: {au}\n   -> cover: {cu or '-'}\n   -> lyrics: {preview}")
        return

    # Reescribir CSV si aplica y si se proporcionó --manifest
    if rows and manifest_csv:
        import csv
        fieldnames = list(rows[0].keys())
        tmp_path = manifest_csv.with_suffix(manifest_csv.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in rows:
                w.writerow(row)
        tmp_path.replace(manifest_csv)
        typer.echo(f"Actualizado CSV: {manifest_csv} | Audios descargados: {sum(1 for _,p in completed if p)}")


@app.command()
def fetch_covers(
    manifest_csv: Path = typer.Argument(..., help="Ruta a suno_manifest.csv"),
    out_dir: Path = typer.Option(SUNO_ROOT / "covers", "--out-dir", help="Carpeta donde guardar portadas"),
    url_col: str = typer.Option("suno_url", "--url-col", help="Nombre de columna en el CSV con URL de Suno"),
    write_tags_opt: bool = typer.Option(False, "--write-tags", help="Escribir carátula en el archivo de audio"),
    apply: bool = typer.Option(False, "--apply", help="Descargar y actualizar CSV (por defecto: simulación)"),
):
    """Descarga portadas de canciones desde páginas de Suno y actualiza cover_image en el CSV.

    CSV esperado: columnas file_path, [proposed_title opcional], [cover_image], y una columna con URLs (por defecto 'suno_url').
    Si falta cover_image y existe suno_url, se resuelve og:image y se descarga a --out-dir.
    Con --write-tags se incrusta la imagen descargada como carátula en el archivo de audio.
    """
    import csv

    rows: list[dict] = []
    with manifest_csv.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        fieldnames = r.fieldnames or []
        for row in r:
            rows.append(row)
    if "cover_image" not in (rows[0].keys() if rows else {}):
        for row in rows:
            row.setdefault("cover_image", "")

    planned = []
    updated = 0
    for row in rows:
        fp = (row.get("file_path") or "").strip()
        if not fp:
            continue
        cover_path_val = (row.get("cover_image") or "").strip()
        if cover_path_val:
            continue  # ya tiene portada
        suno_url = (row.get(url_col) or "").strip()
        if not suno_url:
            continue
        title = (row.get("proposed_title") or row.get("file_name") or Path(fp).stem).strip()
        cover_url = fetch_cover_url_from_page(suno_url)
        if not cover_url:
            typer.echo(f"No se encontró imagen para: {suno_url}")
            continue
        if not apply:
            planned.append((fp, title, suno_url, cover_url))
        else:
            img_path = download_image(cover_url, out_dir, title or Path(fp).stem)
            if img_path:
                row["cover_image"] = str(img_path)
                if write_tags_opt:
                    maybe_write_tag(Path(fp), title, img_path, apply=True)
                updated += 1
                typer.echo(f"descargada portada -> {img_path}")

    if not apply:
        typer.echo(f"Simulación: {len(planned)} portadas a descargar")
        for (fp, title, su, cu) in planned[:20]:
            typer.echo(f" - {title} :: {fp}\n   {su}\n   -> {cu}")
        return

    # Re-escribir CSV actualizado (atómico)
    import tempfile, os
    fieldnames = list(rows[0].keys()) if rows else ["file_path", "file_name", "proposed_title", "cover_image"]
    tmp_path = manifest_csv.with_suffix(manifest_csv.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    tmp_path.replace(manifest_csv)
    typer.echo(f"Actualizado CSV: {manifest_csv} | Portadas descargadas: {updated}")


@app.command()
def centralize_programs(
    roots: List[Path] = typer.Option(None, "--roots", help="Raíces a escanear (por defecto Downloads/Desktop)"),
    apply: bool = typer.Option(False, "--apply", help="Aplicar (por defecto dry-run)"),
    report_csv: Path = typer.Option(Path.home() / "PROGRAMS_REPORT.csv", "--report-csv", help="Ruta report CSV"),
    report_json: Path = typer.Option(Path.home() / "PROGRAMS_REPORT.json", "--report-json", help="Ruta report JSON"),
):
    """Centraliza instaladores (.dmg/.pkg/.zip) y scripts en carpetas dedicadas, generando reporte."""
    from .config import INSTALLER_EXTS, SCRIPT_EXTS
    roots = roots or [Path.home() / "Downloads", Path.home() / "Desktop"]
    rows = []

    def record(row):
        rows.append(row)

    # Instaladores
    for p in walk_files(roots, include_exts=INSTALLER_EXTS | SCRIPT_EXTS):
        ext = p.suffix.lower()
        size = p.stat().st_size
        created = datetime.fromtimestamp(p.stat().st_ctime).isoformat(timespec="seconds")
        if ext in INSTALLER_EXTS:
            target_dir = INSTALLERS_DIR
            type_ = "installer"
        else:
            target_dir = SCRIPTS_DIR
            type_ = "script"
        ensure_dir(target_dir)
        dst = deconflict_name(target_dir, p.name)
        if apply:
            final = safe_move(p, dst)
            moved = True
        else:
            final = dst
            moved = False
        record({
            "type": type_, "src_path": str(p), "dest_path": str(final), "size_bytes": size, "created_at": created, "moved": moved
        })

    # Escribir reportes
    write_json(report_json, rows)
    fieldnames = ["type", "src_path", "dest_path", "size_bytes", "created_at", "moved"]
    write_csv(report_csv, rows, fieldnames)
    typer.echo(f"Reporte escrito en {report_csv} y {report_json}")


@app.command()
def write_readmes(force: bool = typer.Option(False, "--force", help="Sobrescribir si ya existen")):
    """Crea README.txt en carpetas destino para explicar su propósito."""
    ensure_dir(SUNO_ROOT)
    ensure_dir(DUP_DIR)
    ensure_dir(INSTALLERS_DIR)
    ensure_dir(SCRIPTS_DIR)

    def write_if_needed(path: Path, text: str):
        if path.exists() and not force:
            return
        path.write_text(text, encoding="utf-8")

    write_if_needed(SUNO_ROOT / "README.txt", (
        "Esta carpeta centraliza tu música generada/descargada de Suno.\n"
        "- index.json / index.csv: índices con metadatos.\n"
        "- duplicates: usa 'suno-org dedupe' para detectar duplicados y moverlos a .Duplicates.\n"
        "- rename & move: usa 'suno-org move-suno --rename --apply' para mover/renombrar.\n"
        "- pins: usa 'suno-org pin' para fijar favoritos (se respetan en dedupe/move) y 'suno-org export-pins' para copia offline.\n"
    ))
    write_if_needed(DUP_DIR / "README.txt", (
        "Duplicados detectados por fingerprint (Chromaprint) o hash de archivo.\n"
        "Aquí se mueven duplicados para revisión. Nada se borra automáticamente.\n"
        "Puedes restaurar moviéndolos de vuelta manualmente.\n"
    ))
    write_if_needed(INSTALLERS_DIR / "README.txt", (
        "Central de instaladores (.dmg/.pkg/.zip).\n"
        "Guarda aquí instaladores descargados para no perderlos.\n"
    ))
    write_if_needed(SCRIPTS_DIR / "README.txt", (
        "Scripts personales ejecutables (.sh/.py/.js/.zsh/.command).\n"
        "Puedes añadir esta carpeta a tu PATH para ejecutar scripts fácilmente.\n"
    ))


@app.command()
def collect_urls_from_history(
    out_file: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_urls.txt", "--out-file", help="Dónde escribir la lista de URLs"),
    limit: int = typer.Option(0, "--limit", help="Máximo de URLs a escribir (0 = sin límite)"),
):
    """Escanea historiales locales de navegadores (solo lectura) y recopila URLs de Suno visitadas.

    Soporta Safari, Chrome/Brave/Edge/Chromium y Firefox (si existen). No accede a contraseñas ni cookies.
    """
    urls = collect_suno_urls_from_browsers()
    # normalizar y ordenar
    seen = set(); ordered: List[str] = []
    for u in urls:
        cu = canonicalize_suno_url(u)
        if cu and cu not in seen:
            seen.add(cu); ordered.append(cu)
    if limit > 0:
        ordered = ordered[:limit]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(ordered) + ("\n" if ordered else ""), encoding="utf-8")
    typer.echo(f"Listo. URLs desde historial -> {out_file} | total únicas: {len(ordered)}")


@app.command()
def collect_urls_browser(
    profile: str = typer.Argument(..., help="URL del perfil de Suno @usuario"),
    out_file: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_urls_profile.txt", "--out-file", help="Dónde guardar URLs"),
    headless: bool = typer.Option(False, "--headless/--headed", help="Ejecutar sin ventana del navegador"),
    limit: int = typer.Option(0, "--limit", help="Cortar tras N URLs (0 = sin límite)"),
    linger_seconds: int = typer.Option(90, "--linger-seconds", help="Mantener el navegador abierto N segundos para que puedas iniciar sesión/navegar"),
    state_file: Path = typer.Option(SUNO_ROOT / "playwright_state.json", "--state-file", help="Archivo para guardar/cargar sesión (cookies)"),
    pages: int = typer.Option(200, "--pages", help="Máximo de páginas a intentar con ?page=N"),
    strategy: str = typer.Option("hybrid", "--strategy", help="scroll | paginate | hybrid"),
):
    """Abre un navegador (Playwright) y recolecta todos los enlaces /song/ del perfil.

    Útil para cuentas con contenido cargado por JavaScript. Puedes iniciar sesión en la ventana si lo pide.
    """
    try:
        urls = collect_song_urls_via_browser(profile, limit=limit or None, headless=headless, linger_seconds=linger_seconds, storage_path=state_file, pages=pages, strategy=strategy)
    except RuntimeError as e:
        typer.echo(f"Error: {e}. Instala Playwright con 'pip install playwright && playwright install chromium'")
        raise typer.Exit(code=2)
    # escribir
    out_file.parent.mkdir(parents=True, exist_ok=True)
    # normalizar y dedupe final
    seen = set(); ordered = []
    for u in urls:
        if u and u not in seen:
            seen.add(u); ordered.append(u)
    out_file.write_text("\n".join(ordered) + ("\n" if ordered else ""), encoding="utf-8")
    typer.echo(f"Listo. URLs encontradas: {len(ordered)} -> {out_file}")


@app.command()
def collect_urls(
    profile: Optional[str] = typer.Option(None, "--profile", help="URL del perfil/página de colección pública de Suno"),
    seeds: List[str] = typer.Argument(None, help="URLs semilla (cualquier página pública de Suno)"),
    out_file: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_urls.txt", "--out-file", help="Dónde escribir la lista de URLs"),
    max_pages: int = typer.Option(50, "--max-pages", help="Máximo de páginas a intentar en perfil"),
    delay_seconds: float = typer.Option(0.7, "--delay-seconds", help="Pausa entre solicitudes"),
):
    """Descubre automáticamente enlaces de canciones de Suno a partir de un perfil o de páginas semilla.

    No descarga audio. Escribe un archivo .txt con una URL por línea, sin duplicados.
    """
    urls: List[str] = []
    if profile:
        urls.extend(discover_urls_from_profile(profile, max_pages=max_pages, delay_seconds=delay_seconds))
    if seeds:
        urls.extend(discover_urls_from_seeds(seeds, delay_seconds=delay_seconds))
    # Normalizar y dedup
    seen = set()
    ordered: List[str] = []
    for u in urls:
        cu = canonicalize_suno_url(u)
        if cu and cu not in seen:
            seen.add(cu)
            ordered.append(cu)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(ordered) + ("\n" if ordered else ""), encoding="utf-8")
    typer.echo(f"Listo. URLs escritas en {out_file} | total únicas: {len(ordered)}")


@app.command()
def urls_to_manifest(
    urls_file: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_urls.txt", "--urls-file", help="Archivo con una URL por línea o CSV con columna 'suno_url'"),
    out_json: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_links.json", "--out-json", help="Salida JSON"),
    out_csv: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_links.csv", "--out-csv", help="Salida CSV"),
    delay_seconds: float = typer.Option(0.7, "--delay-seconds", help="Pausa entre solicitudes"),
    timeout: int = typer.Option(20, "--timeout", help="Timeout por solicitud"),
    max_workers: int = typer.Option(6, "--max-workers", help="Paralelismo para resolver metadatos"),
    only_songs: bool = typer.Option(True, "--only-songs/--all-pages", help="Mantener solo URLs de canciones (/song)"),
):
    """Lee URLs de Suno y construye un manifiesto con metadatos (título, portada URL, letras breves, idioma, flags).

    No descarga audio ni imágenes. Solo HTTP GET de páginas públicas.
    """
    import csv, time
    from .manifest import _detect_language_basic
    from .report import write_json, write_csv
    from .covers import fetch_cover_url_from_page

    # Leer URLs
    urls: List[str] = []
    p = urls_file
    if not p.exists():
        typer.echo(f"No existe {p}. Usa 'suno-org collect-urls' o crea el archivo manualmente.")
        raise typer.Exit(code=2)
    if p.suffix.lower() == ".csv":
        with p.open("r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                su = (row.get("suno_url") or "").strip()
                if su:
                    urls.append(su)
    else:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                urls.append(line)

    # Normalizar y deduplicar entrada
    seen = set(); ordered = []
    for u in urls:
        cu = canonicalize_suno_url(u)
        if cu and cu not in seen:
            if (not only_songs) or ("/song/" in cu):
                seen.add(cu); ordered.append(cu)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    rows: List[dict] = []
    errors: List[tuple[str, str]] = []
    lock = threading.Lock()

    def process(su: str) -> None:
        try:
            ti = extract_title_from_page(su, timeout=timeout) or ""
            au = extract_audio_url_from_page(su, timeout=timeout) or ""
            cu = fetch_cover_url_from_page(su, timeout=timeout) or ""
            ly = extract_lyrics_from_page(su, timeout=timeout) or ""
            lang = _detect_language_basic((ly or "") + " " + (ti or "")) or ""
            lower = (ti + " " + ly).lower()
            is_cover = "yes" if (" cover" in lower or "(cover" in lower or "versión" in lower or "version" in lower) else "no"
            explicit = "yes" if any(tok in lower for tok in ["explicit", "[explicit]"]) else "no"
            from .utils.url import extract_song_id_from_url
            song_id = extract_song_id_from_url(su)
            from .suno_fetch import extract_created_at_from_page
            created = extract_created_at_from_page(su, timeout=timeout) or ""
            from .manifest import lyrics_excerpt, genre_guess_basic
            excerpt = lyrics_excerpt(ly, max_len=280)
            # genre guess from title+lyrics
            genre = genre_guess_basic((ti or "") + " " + (ly or ""))
            # bpm
            from .suno_fetch import extract_bpm_from_page
            bpm = extract_bpm_from_page(su, timeout=timeout)
            row = {
                "suno_url": su,
                "audio_url": au,
                "proposed_title": ti.strip(),
                "lyrics_excerpt": excerpt,
                "language": lang,
                "cover_url": cu,
                "genre_guess": genre,
                "bpm": bpm or "",
                "explicit": explicit,
                "is_cover": is_cover,
                "notes": "",
                "song_id": song_id,
                "created_at": created,
                "lyrics": ly or "",
            }
            with lock:
                rows.append(row)
        except Exception as e:
            with lock:
                errors.append((su, str(e)))

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(process, su) for su in ordered]
        for fut in as_completed(futs):
            pass
        # Pequeña pausa al final para no saturar
    time.sleep(min(1.0, delay_seconds))

    # Deduplicar por audio_url y por suno_url canónica (mantener primera fila)
    dedup_seen = set(); final_rows: List[dict] = []
    for r in rows:
        key = r.get("audio_url") or r.get("suno_url")
        if key and key not in dedup_seen:
            dedup_seen.add(key); final_rows.append(r)
        else:
            # marcar duplicado en notes de la primera coincidencia si podemos
            pass

    # Escribir salidas
    write_json(out_json, final_rows)
    fieldnames = ["suno_url","audio_url","proposed_title","lyrics_excerpt","language","cover_url","genre_guess","bpm","explicit","is_cover","notes","song_id","created_at"]
    write_csv(out_csv, final_rows, fieldnames)

    # Errores
    if errors:
        err_path = out_csv.with_suffix(out_csv.suffix + ".errors.txt")
        err_path.write_text("\n".join(f"{u}\t{e}" for (u,e) in errors) + "\n", encoding="utf-8")
        typer.echo(f"Completado con errores: {len(errors)}. Ver {err_path}")
        raise typer.Exit(code=2)
    else:
        typer.echo(f"Listo. Manifiestos: {out_json} y {out_csv} | filas: {len(final_rows)}")


@app.command()
def build_webui(
    webui_dir: Path = typer.Option(SUNO_ROOT / "webui", "--webui-dir", help="Carpeta de salida de la UI"),
    manifest_json: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_links.json", "--manifest-json", help="Ruta del JSON a cargar"),
):
    """Genera una WebUI estática simple para explorar el manifiesto."""
    from textwrap import dedent
    webui_dir.mkdir(parents=True, exist_ok=True)
    # index.html (con DATA embebida para evitar problemas de fetch)
    import json
    try:
      data = json.loads(manifest_json.read_text(encoding='utf-8'))
    except Exception:
      data = []
    data_js = json.dumps(data, ensure_ascii=False)
    index_html = dedent(f"""
    <!doctype html>
    <html lang=\"es\">
    <head>
      <meta charset=\"utf-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
      <title>Suno Links</title>
      <link rel=\"stylesheet\" href=\"styles.css\" />
    </head>
    <body class=\"neon\">
      <header>
        <h1>Suno Links – Lista Inteligente</h1>
        <div class=\"controls\">
          <input id=\"q\" placeholder=\"Buscar título/letras\" />
          <select id=\"lang\"><option value=\"\">Idioma</option><option>es</option><option>en</option></select>
          <select id=\"cover\"><option value=\"\">Cover?</option><option value=\"yes\">yes</option><option value=\"no\">no</option></select>
          <select id=\"explicit\"><option value=\"\">Explicit?</option><option value=\"yes\">yes</option><option value=\"no\">no</option></select>
        </div>
      </header>
      <main>
        <table id=\"tbl\">
          <thead>
            <tr>
              <th data-k=\"proposed_title\">Title</th>
          <th data-k=\"language\">Lang</th>
              <th>Cover</th>
              <th>Lyrics</th>
              <th data-k=\"bpm\">BPM</th>
              <th data-k=\"created_at\">Created</th>
              <th>Status</th>
              <th>Suno</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
        <div id=\"status\"></div>
      </main>
      <script>window.MANIFEST_PATH = '/manifests/{manifest_json.name}'; window.DATA = {data_js};</script>
      <script src="https://cdn.jsdelivr.net/npm/hydra-synth@1.3.11"></script>
      <script src=\"script.js\"></script>
    </body>
    </html>
    """)
    (webui_dir / "index.html").write_text(index_html, encoding="utf-8")

    # styles.css
    styles = dedent("""
    :root{--hue:260;--fg:#f7f7ff}
    *{box-sizing:border-box}
    html,body{height:100%}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;padding:0;color:var(--fg);background:#000}
    body.trippy{
      background: radial-gradient(1000px 700px at 10% 20%, hsl(var(--hue) 70% 10%), transparent 60%),
                  radial-gradient(900px 600px at 85% 10%, hsl(calc(var(--hue)+120) 70% 12%), transparent 50%),
                  linear-gradient(135deg, hsl(var(--hue) 60% 8%), hsl(calc(var(--hue)+180) 60% 8%));
      background-size:200% 200%;
      animation:bgMove 12s ease-in-out infinite;
    }
    @keyframes bgMove{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
    header{position:sticky;top:0;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.15);background:rgba(0,0,0,.25);backdrop-filter: blur(10px) saturate(140%);box-shadow:0 10px 30px rgba(0,0,0,.25)}
    h1{margin:0 0 8px 0;font-size:20px;letter-spacing:.3px;text-shadow:0 0 8px hsl(calc(var(--hue)+40) 100% 60%),0 0 18px hsl(calc(var(--hue)+200) 100% 60%)}
    .controls{display:flex;gap:8px;flex-wrap:wrap}
    .controls input,.controls select,.controls button{border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.06);color:var(--fg);padding:8px 10px;border-radius:8px;outline:none}
    .controls button{cursor:pointer;font-weight:600;box-shadow:0 0 8px hsl(calc(var(--hue)+40) 100% 55%) inset,0 0 14px rgba(0,0,0,.2);transition:transform .12s ease, box-shadow .2s ease}
    .controls button:hover{transform:translateY(-1px);box-shadow:0 0 12px hsl(calc(var(--hue)+40) 100% 60%),0 0 22px hsl(calc(var(--hue)+200) 100% 60%) inset}
    #tbl{width:100%;border-collapse:separate;border-spacing:0 6px;margin-top:6px}
    #tbl th{background:linear-gradient(90deg, rgba(255,255,255,.10), rgba(255,255,255,.05));position:sticky;top:68px}
    #tbl th,#tbl td{padding:8px 10px;vertical-align:top;border-bottom:1px solid rgba(255,255,255,.12);color:#ffffff}
    #tbl tbody tr{background:rgba(0,0,0,.35);transition:transform .15s ease, box-shadow .15s ease, filter .2s ease}
    #tbl tbody tr:hover{transform:scale(1.01);box-shadow:0 0 0 1px hsl(calc(var(--hue)+160) 100% 60%) inset,0 0 22px hsl(calc(var(--hue)+40) 100% 60%);filter:hue-rotate(10deg) saturate(1.2)}
img.cover{width:96px;height:96px;object-fit:cover;border-radius:10px;border:1px solid rgba(255,255,255,.25);box-shadow:0 0 18px hsl(calc(var(--hue)+200) 100% 60%);transition:transform .2s ease, box-shadow .2s ease}
img.cover:hover{transform:rotate(-3deg) scale(1.06);box-shadow:0 0 28px hsl(calc(var(--hue)+40) 100% 60%),0 0 48px hsl(calc(var(--hue)+180) 100% 60%)}
/* Neon mode enhancements */
body.neon #tbl tbody tr{animation:neonPulse 3.6s ease-in-out infinite alternate;background:linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.04));box-shadow:0 0 0 1px rgba(255,255,255,.08) inset}
body.neon img.cover{box-shadow:0 0 24px #0ff,0 0 46px #f0f,0 0 64px #0ff}
body.neon td.title{font-weight:700;letter-spacing:.3px;color:#fff;text-shadow:0 0 8px #0ff,0 0 18px #f0f}
@keyframes neonPulse{0%{box-shadow:0 0 0 1px rgba(255,255,255,.10) inset}50%{box-shadow:0 0 0 1px rgba(255,255,255,.18) inset,0 0 18px hsl(calc(var(--hue)+180) 100% 55%)}100%{box-shadow:0 0 0 1px rgba(255,255,255,.10) inset,0 0 26px hsl(calc(var(--hue)+40) 100% 55%)}}
    td.lyrics{max-width:520px}
    td.lyrics span{display:inline-block;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    a{color:hsl(calc(var(--hue)+40) 100% 70%);text-decoration:none}
    a:hover{color:hsl(calc(var(--hue)+200) 100% 70%);text-shadow:0 0 8px hsl(calc(var(--hue)+200) 100% 60%)}
    body.trippy::before{content:"";position:fixed;inset:-20vmax;background:conic-gradient(from 0deg,transparent,rgba(255,255,255,.06),transparent);animation:spin 18s linear infinite;pointer-events:none;mix-blend-mode:overlay}
    @keyframes spin{to{transform:rotate(360deg)}}
    """)
    (webui_dir / "styles.css").write_text(styles, encoding="utf-8")

    # script.js
    script = dedent("""
    const state = { data: [], filtered: [], sortK: 'proposed_title', sortDir: 1 };
    async function load(){
      const elStatus = document.getElementById('status');
      try{
        const manifestPath = (window.MANIFEST_PATH || '../manifests/suno_links.json');
        if (Array.isArray(window.DATA)) {
          state.data = window.DATA;
        } else {
          const res = await fetch(manifestPath, {cache:'no-store'});
          if(!res.ok) throw new Error('HTTP '+res.status);
          state.data = await res.json();
        }
        applyFilters();
        elStatus.textContent = `${state.data.length} filas`;
        document.title = `Suno Links (${state.data.length})`;
      }catch(err){
        document.getElementById('status').innerHTML = `No se pudo cargar el manifiesto.<br>${err && err.message ? err.message : err}`;
      }
    }
    // Animación de color (psicodélica): rotación de tono cuando está activo
    (function(){
      let hue = 260;
      setInterval(()=>{
        if(document.body.classList.contains('trippy')){
          hue = (hue + 1) % 360;
          document.documentElement.style.setProperty('--hue', hue);
        }
      }, 120);
    })();
    function render(){
      const tbody = document.querySelector('#tbl tbody');
      tbody.innerHTML='';
      for(const r of state.filtered){
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class=\"title\">${escapeHtml(r.proposed_title||'')}</td>
          <td>${escapeHtml(r.language||'')}</td>
          <td>${r.cover_url?`<img class=\"cover\" src=\"${r.cover_url}\">`:''}</td>
          <td class=\"lyrics\"><span title=\"${escapeHtml(r.lyrics_excerpt||'')}\">${escapeHtml(r.lyrics_excerpt||'')}</span></td>
          <td>${escapeHtml((r.bpm||'').toString())}</td>
          <td>${escapeHtml((r.created_at||'').split('T')[0])}</td>
          <td>${(r.file_path && r.file_path.length>0)?'downloaded':'-'}</td>
          <td>${r.suno_url?`<a href=\"${r.suno_url}\" target=\"_blank\">link</a>`:''}</td>
          <td>${escapeHtml(r.notes||'')}</td>`;
        // expand lyrics on click
        tr.addEventListener('click', ()=>{
          const full = (r.lyrics || r.lyrics_excerpt || '').toString();
          if(!full) return;
          alert(full);
        });
        tbody.appendChild(tr);
      }
    }
    function applyFilters(){
      const q = document.getElementById('q').value.trim().toLowerCase();
      const lang = document.getElementById('lang').value;
      const cover = document.getElementById('cover').value;
      const expl = document.getElementById('explicit').value;
      let arr = [...state.data];
      if(q){
        arr = arr.filter(r => (r.proposed_title||'').toLowerCase().includes(q) || (r.lyrics_excerpt||'').toLowerCase().includes(q));
      }
      if(lang){ arr = arr.filter(r => (r.language||'')===lang); }
      if(cover){ arr = arr.filter(r => (r.is_cover||'')===cover); }
      if(expl){ arr = arr.filter(r => (r.explicit||'')===expl); }
      arr.sort((a,b)=>{
        const A=(a[state.sortK]||'').toString().toLowerCase();
        const B=(b[state.sortK]||'').toString().toLowerCase();
        return A<B ? -1*state.sortDir : A>B ? 1*state.sortDir : 0;
      });
      state.filtered = arr; render();
    }
    function setup(){
      document.getElementById('q').addEventListener('input', applyFilters);
      document.getElementById('lang').addEventListener('change', applyFilters);
      document.getElementById('cover').addEventListener('change', applyFilters);
      document.getElementById('explicit').addEventListener('change', applyFilters);
      // Render summary of top genres
      const header = document.querySelector('header .controls');
      const wrap = document.createElement('div'); wrap.style.display='flex'; wrap.style.flexWrap='wrap'; wrap.style.gap='6px'; wrap.style.marginTop='6px';
      const counts = {};
      for(const r of (window.DATA||[])){
        const g=(r.genre_guess||'').trim(); if(!g) continue; counts[g]=(counts[g]||0)+1;
      }
      const top = Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,12);
      for(const [g,c] of top){
        const b = document.createElement('button'); b.textContent = `${g} (${c})`;
        b.addEventListener('click', ()=>{ document.getElementById('q').value=''; state.sortK='proposed_title'; state.sortDir=1; state.data = window.DATA.filter(x=>(x.genre_guess||'')===g); applyFilters(); });
        wrap.appendChild(b);
      }
      header.parentElement.appendChild(wrap);
      document.querySelectorAll('#tbl th[data-k]').forEach(th=>{
        th.style.cursor='pointer';
        th.addEventListener('click', ()=>{ const k=th.dataset.k; state.sortDir = (state.sortK===k? -state.sortDir:1); state.sortK=k; applyFilters(); });
      });
      // Botón de modo psicodélico
      const btnTrippy = document.createElement('button');
      btnTrippy.id = 'trippy';
      btnTrippy.textContent = document.body.classList.contains('trippy') ? 'Trippy: ON' : 'Trippy: OFF';
      document.querySelector('.controls').appendChild(btnTrippy);
      btnTrippy.addEventListener('click', ()=>{
        document.body.classList.toggle('trippy');
        btnTrippy.textContent = document.body.classList.contains('trippy') ? 'Trippy: ON' : 'Trippy: OFF';
      });
      // Botón de modo neon
      const btnNeon = document.createElement('button');
      btnNeon.id = 'neon';
      btnNeon.textContent = document.body.classList.contains('neon') ? 'Neon: ON' : 'Neon: OFF';
      document.querySelector('.controls').appendChild(btnNeon);
      btnNeon.addEventListener('click', ()=>{
        document.body.classList.toggle('neon');
        btnNeon.textContent = document.body.classList.contains('neon') ? 'Neon: ON' : 'Neon: OFF';
      });
    }
    function escapeHtml(s){
      const m = {'&':'&amp;','<':'&lt;','>':'&gt;'}; m['"']='&quot;'; m["'"]='&#39;';
      return s.replace(/[&<>\"']/g, c=>m[c]||c);
    }
    window.addEventListener('DOMContentLoaded', ()=>{ setup(); load(); });
    """)
    (webui_dir / "script.js").write_text(script, encoding="utf-8")
    typer.echo(f"WebUI escrita en {webui_dir}/ (usa {manifest_json.name})")


@app.command()
def build_genre_folders(
    manifest_json: Path = typer.Option(SUNO_ROOT / "manifests" / "suno_links.json", "--manifest-json", help="Manifiesto JSON de entrada"),
    out_dir: Path = typer.Option(SUNO_ROOT / "Genres", "--out-dir", help="Carpeta raíz para géneros"),
    link_files: bool = typer.Option(False, "--link-files", help="Crear symlinks a archivos ya descargados si existen"),
):
    """Crea carpetas por género con sub-manifiestos y playlist M3U por género.
    No descarga audio. Si --link-files está activo y existe file_path en el
    manifiesto, creará enlaces simbólicos dentro de la carpeta del género.
    """
    import json, os, shutil
    from collections import defaultdict
    if not manifest_json.exists():
        typer.echo(f"No existe {manifest_json}")
        raise typer.Exit(code=2)
    data = json.loads(manifest_json.read_text(encoding="utf-8"))
    by_genre: dict[str, list[dict]] = defaultdict(list)
    for row in data:
        g = (row.get("genre_guess") or "Uncategorized").strip() or "Uncategorized"
        by_genre[g].append(row)
    ensure_dir(out_dir)
    # README de raíz
    (out_dir / "README.txt").write_text(
        "Carpetas agrupadas por género generadas por suno-org.\n" \
        "Cada carpeta contiene manifest.json, manifest.csv y playlist_urls.m3u.\n" \
        "Usa --link-files para crear enlaces simbólicos si ya descargaste los audios.\n",
        encoding="utf-8"
    )
    created = 0
    for g, rows in sorted(by_genre.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())):
        slug = slugify(g or "Uncategorized") or "uncategorized"
        gd = out_dir / slug
        ensure_dir(gd)
        # Manifiestos
        jpath = gd / "manifest.json"
        cpath = gd / "manifest.csv"
        write_json(jpath, rows)
        fns = list(rows[0].keys()) if rows else ["suno_url","proposed_title","cover_url"]
        write_csv(cpath, rows, fns)
        # Playlist de URLs (suno_url o audio_url si existe)
        m3u = gd / "playlist_urls.m3u"
        from .report import write_m3u as _write_m3u
        paths = []
        for r in rows:
            if r.get("suno_url"):
                paths.append(Path(r["suno_url"]))
        # Escribimos el M3U con rutas textualizadas
        m3u.parent.mkdir(parents=True, exist_ok=True)
        with m3u.open("w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for r in rows:
                url = (r.get("audio_url") or r.get("suno_url") or "").strip()
                if url:
                    f.write(url + "\n")
        # Symlinks si procede
        if link_files:
            links_dir = gd / "links"
            ensure_dir(links_dir)
            for r in rows:
                fp = (r.get("file_path") or "").strip()
                if not fp:
                    continue
                p = Path(fp).expanduser()
                if p.exists():
                    try:
                        target = links_dir / p.name
                        if not target.exists():
                            os.symlink(p, target)
                    except Exception:
                        pass
        created += 1
    typer.echo(f"Listo. Géneros creados: {created} -> {out_dir}")


if __name__ == "__main__":
    app()
