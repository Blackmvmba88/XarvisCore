from typer.testing import CliRunner

from mamba_dl.cli import app, resolve_input


def test_help():
    runner = CliRunner()
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "mamba-dl" in res.output or "download" in res.output.lower()


def test_resolve_search():
    s = resolve_input("lofi hip hop")
    assert s.startswith("ytsearch1:")


def test_resolve_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    s = resolve_input(url)
    assert s == url
