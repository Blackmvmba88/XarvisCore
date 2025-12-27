#!/usr/bin/env python3
"""
organize_files.py

Organiza archivos dentro de un directorio por tipo (Photos, Videos, Music, Programs, Documents,
Archives, Others). Tiene modo --dry-run (por defecto) y --apply para ejecutar los movimientos.

Opciones relevantes:
  --path PATH        Carpeta origen a organizar (por defecto: carpeta actual)
  --apply            Aplica los movimientos (si no, solo muestra dry-run)
  --order-programs   Si se usa con --apply, renombra los archivos de Programs con prefijos
                     numéricos para dejarlos ordenados: "01 - nombre.ext"

Ejemplo:
  python3 organize_files.py --path "/Volumes/ADATA SC740" --dry-run

"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


PHOTO_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.heic', '.bmp', '.tif', '.tiff', '.raw', '.psd'}
VIDEO_EXTS = {'.mp4', '.mov', '.mkv', '.avi', '.m4v', '.mpg', '.mpeg', '.webm'}
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma'}
DOCUMENT_EXTS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md'}
ARCHIVE_EXTS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.tgz'}
PROGRAM_EXTS = {'.dmg', '.pkg', '.exe', '.msi', '.deb', '.rpm', '.app', '.sh', '.py', '.jar'}


def classify_path(p: Path) -> str:
    """Devuelve la categoría de destino para la ruta p."""
    # Archivos de resource-fork / metadata de macOS que empiezan por '._' los agrupamos
    # en Programs/meta para que no se mezclen con los instaladores reales.
    if p.name.startswith('._'):
        return 'Programs/meta'

    if p.is_dir():
        # En mac, aplicaciones son directorios terminados en .app
        if p.name.lower().endswith('.app'):
            return 'Programs'
        # otros directorios se tratan como Others
        return 'Others'

    ext = p.suffix.lower()
    if ext in PHOTO_EXTS:
        return 'Photos'
    if ext in VIDEO_EXTS:
        return 'Videos'
    if ext in AUDIO_EXTS:
        return 'Music'
    if ext in DOCUMENT_EXTS:
        return 'Documents'
    if ext in ARCHIVE_EXTS:
        return 'Archives'
    if ext in PROGRAM_EXTS:
        return 'Programs'
    return 'Others'


def gather_moves(root: Path, dest_root: Path) -> Dict[Path, Path]:
    """Recorre root (no recursivamente en carpetas destino) y devuelve un mapa {src: dst} para mover."""
    moves: Dict[Path, Path] = {}
    dest_dirs = {name for name in ['Photos', 'Videos', 'Music', 'Programs', 'Documents', 'Archives', 'Others']}

    for item in sorted(root.iterdir()):
        # saltar la carpeta destino si ya existe en root para evitar mover recursivamente
        if item.name in dest_dirs:
            continue
        # saltar el propio script si está en la misma carpeta
        try:
            # no mover este script ni la web app
            if item.name in {Path(__file__).name, 'web_app.py'}:
                continue
            if item.resolve() == Path(__file__).resolve():
                continue
        except Exception:
            pass

        # classify
        cat = classify_path(item)
        target_dir = dest_root / cat
        target_dir.mkdir(parents=True, exist_ok=True)

        dst = target_dir / item.name
        # si dst ya existe, se añadirá un sufijo numérico
        if dst.exists():
            dst = unique_path(dst)

        moves[item] = dst

    return moves


def unique_path(p: Path) -> Path:
    """Genera un path único agregando un sufijo (1), (2), ... antes de la extensión."""
    parent = p.parent
    stem = p.stem
    suffix = p.suffix
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def apply_moves(moves: Dict[Path, Path], do_apply: bool) -> List[Tuple[str, str, str, str]]:
    """Imprime y opcionalmente aplica los movimientos.

    Retorna una lista de tuplas (src, dst, status, message) donde status es 'planned',
    'moved' o 'error'. Esto facilita su uso desde una interfaz web.
    """
    results: List[Tuple[str, str, str, str]] = []
    if not moves:
        print("No hay archivos para mover.")
        return results

    print(f"Movimientos planificados: {len(moves)}")
    for src, dst in moves.items():
        print(f"{src} -> {dst}")
        results.append((str(src), str(dst), 'planned', ''))

    if not do_apply:
        print('\nDry-run — no se realizaron cambios. Añade --apply para mover archivos.')
        return results

    # aplicar
    for src, dst in moves.items():
        dst_parent = dst.parent
        dst_parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dst))
            results.append((str(src), str(dst), 'moved', ''))
        except Exception as e:
            msg = str(e)
            print(f"ERROR moviendo {src} -> {dst}: {msg}")
            results.append((str(src), str(dst), 'error', msg))

    return results


def order_programs(dest_root: Path) -> None:
    """Renombra los archivos en Programs con prefijos numerados (01 - name.ext). Solo si --order-programs."""
    prog_dir = dest_root / 'Programs'
    if not prog_dir.exists():
        return

    items = sorted(prog_dir.iterdir(), key=lambda p: p.name.lower())
    # compute width
    width = len(str(len(items)))
    for idx, item in enumerate(items, start=1):
        # skip if already prefixed like '01 - '
        if len(item.name) > 5 and item.name[:2].isdigit() and item.name[2:5] == ' - ':
            continue
        prefix = str(idx).zfill(width)
        new_name = f"{prefix} - {item.name}"
        new_path = prog_dir / new_name
        if new_path.exists():
            new_path = unique_path(new_path)
        try:
            item.rename(new_path)
        except Exception as e:
            print(f"ERROR renombrando {item} -> {new_path}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Organiza archivos por tipo (Photos, Videos, Music, Programs, ...)')
    parser.add_argument('--path', '-p', type=Path, default=Path('.'), help='Carpeta a organizar (por defecto: actual)')
    parser.add_argument('--apply', action='store_true', help='Aplica los movimientos (por defecto dry-run)')
    parser.add_argument('--order-programs', action='store_true', help='Si se usa con --apply, numera y ordena los programas')
    args = parser.parse_args()

    root = args.path.expanduser().resolve()
    dest_root = root

    print(f"Carpeta origen: {root}")
    moves = gather_moves(root, dest_root)
    apply_moves(moves, args.apply)

    if args.apply and args.order_programs:
        print('\nOrdenando programas en Programs/ ...')
        order_programs(dest_root)
        print('Orden de programas aplicado.')


if __name__ == '__main__':
    main()
