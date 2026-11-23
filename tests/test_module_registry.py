import json

from xarvis.modules.registry import discover_modules, inspect_module


def _manifest(folder, **overrides):
    folder.mkdir(parents=True)
    data = {
        "id": "demo_module",
        "version": "1.0.0",
        "entrypoint": "main.py",
        "capabilities": ["demo"],
    }
    data.update(overrides)
    path = folder / "module.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_ready_module(tmp_path):
    folder = tmp_path / "demo"
    path = _manifest(folder)
    (folder / "main.py").write_text("pass\n", encoding="utf-8")
    assert inspect_module(path)["status"] == "ready"
    assert discover_modules(tmp_path)[0]["id"] == "demo_module"


def test_missing_entrypoint(tmp_path):
    result = inspect_module(_manifest(tmp_path / "demo"))
    assert result["status"] == "missing_entrypoint"


def test_reject_parent_traversal(tmp_path):
    result = inspect_module(_manifest(tmp_path / "demo", entrypoint="../outside.py"))
    assert result["status"] == "invalid"


def test_reject_absolute_entrypoint(tmp_path):
    result = inspect_module(_manifest(tmp_path / "demo", entrypoint="/tmp/run.py"))
    assert result["status"] == "invalid"


def test_bad_json_does_not_abort_discovery(tmp_path):
    good = _manifest(tmp_path / "good")
    (good.parent / "main.py").touch()
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "module.json").write_text("{bad", encoding="utf-8")
    records = discover_modules(tmp_path)
    assert [r["status"] for r in records] == ["invalid", "ready"]


def test_empty_directory(tmp_path):
    assert discover_modules(tmp_path) == []


def test_reject_nonobject_manifest(tmp_path):
    folder = tmp_path / "demo"
    folder.mkdir()
    path = folder / "module.json"
    path.write_text("[]", encoding="utf-8")
    assert inspect_module(path)["status"] == "invalid"
