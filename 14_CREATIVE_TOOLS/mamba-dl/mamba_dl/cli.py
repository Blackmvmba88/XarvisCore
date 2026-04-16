from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import typer

from .downloader import download, is_url


app = typer.Typer(add_completion=False, help="mamba-dl: download videos with yt-dlp at max quality with live speed and metrics.")


def _default_output_dir() -> Path:
    return (Path.home() / "Downloads" / "mamba-dl").expanduser()


def resolve_input(query_or_url: str) -> str:
    s = query_or_url.strip()
    if is_url(s):
        return s
    # treat as search term; take first result
    return f"ytsearch1:{s}"


def _warn_if_ffmpeg_missing():
    if shutil.which("ffmpeg") is None:
        typer.echo("ffmpeg not found. Merging best video+audio may fail. Install via Homebrew: brew install ffmpeg", err=True)


@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def main(
    query_or_url: str = typer.Argument(..., help="YouTube URL/playlist URL or plain text search query."),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory (default: ~/Downloads/mamba-dl)"),
    no_playlist: bool = typer.Option(False, "--no-playlist", help="If URL is a playlist, download only the first item."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Force re-download and overwrite existing files."),
    limit_rate: Optional[str] = typer.Option(None, "--limit-rate", help="Limit bandwidth, e.g., 5M or 500K."),
):
    """
    Command: mamba-dl [OPTIONS] <query_or_url>
    """
    out = output_dir or _default_output_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(parents=True, exist_ok=True)

    _warn_if_ffmpeg_missing()

    target = resolve_input(query_or_url)
    typer.echo(f"Target: {target}")
    typer.echo(f"Saving to: {out}")

    metric_paths = download(
        query_or_url=target,
        output_dir=out,
        noplaylist=no_playlist,
        overwrite=overwrite,
        limit_rate=limit_rate,
    )
    typer.echo(f"Done. Metrics files: {len(metric_paths)}")
    for p in metric_paths:
        typer.echo(f" - {p}")


if __name__ == "__main__":
    app()
