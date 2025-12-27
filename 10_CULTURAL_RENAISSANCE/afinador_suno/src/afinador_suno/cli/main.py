from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print

from ..core.catalog import build_catalog
from ..io.decode import ensure_wav_stereo_and_mono
from ..core.f0 import extract_f0_offline, save_analysis_json

app = typer.Typer(add_completion=False, no_args_is_help=True, help="CLI Afinador Suno")


@app.command()
def list(source: str = typer.Option("auto", help="auto|suno|downloads")):
    """Lista canciones detectadas."""
    items = build_catalog()
    for it in items:
        if source != "auto" and it.source != source:
            continue
        print(f"[cyan]{it.id}[/]  [green]{it.source}[/]  {it.title} -> {it.path}")


@app.command()
def analyze(id: str = typer.Option(None, help="ID de la canción (sha1 corto)")):
    """Analiza F0 de una canción por ID (pre-procesa y guarda JSON)."""
    items = build_catalog()
    target = None
    for it in items:
        if it.id.startswith(id):
            target = it
            break
    if not target:
        typer.echo("No se encontró el ID")
        raise typer.Exit(code=1)

    stereo, mono = ensure_wav_stereo_and_mono(target.path)
    result = extract_f0_offline(mono)
    out = Path(__file__).resolve().parents[3] / "analyses" / f"{target.id}.json"
    save_analysis_json(result, out)
    print(f"[✓] Análisis guardado: {out}")


if __name__ == "__main__":
    app()