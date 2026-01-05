import importlib.util
import os
import json

import pytest
from flask import Flask

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
RG_WEBUI = os.path.join(REPO_ROOT, "5_INFRA", "ram_guardian_webui.py")

spec = importlib.util.spec_from_file_location("rg_webui", RG_WEBUI)
rg_webui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rg_webui)

app = rg_webui.app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_status_endpoint(client, monkeypatch):
    monkeypatch.setattr(rg_webui.ram_guardian, "available_fraction", lambda: 0.33)
    monkeypatch.setattr(rg_webui.ram_guardian, "top_memory_procs", lambda n=10: [(1, "a", 1024), (2, "b", 2048)])
    monkeypatch.setattr(rg_webui.ram_guardian, "total_memory_bytes", lambda: 1024*1024*1024)
    r = client.get('/api/status')
    assert r.status_code == 200
    d = r.get_json()
    assert abs(d["available_fraction"] - 0.33) < 0.001


def test_metrics_endpoint(tmp_path, client):
    path = tmp_path / "metrics.jsonl"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps({"a":1}) + "\n")
    # patch METRICS_PATH
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv('RAM_GUARDIAN_METRICS_PATH', str(path))
    # reload module to pick env var; brittle but sufficient for unit test
    import importlib
    importlib.reload(rg_webui)
    app = rg_webui.app
    with app.test_client() as c:
        r = c.get('/api/metrics')
        assert r.status_code == 200
        arr = r.get_json()
        assert isinstance(arr, list)
        assert arr[0]['a'] == 1
    monkeypatch.undo()


def test_action_requires_auth_and_approval(client, monkeypatch, tmp_path):
    # ensure no web secret => destructive action must be blocked due to missing approval file
    # test quit_app without approval
    r = client.post('/api/action', json={"action":"quit_app", "target":"Safari"})
    assert r.status_code == 403

    # with secret set but no approval file -> still blocked
    monkeypatch.setenv('RAM_GUARDIAN_WEB_SECRET', 's3cr3t')
    import importlib
    importlib.reload(rg_webui)
    with app.test_client() as c:
        r = c.post('/api/action', headers={'Authorization': 'Bearer s3cr3t'}, json={"action":"quit_app", "target":"Safari"})
        assert r.status_code == 403

    # create approval file and test again (monkeypatch env var for approval file)
    approval = tmp_path / 'approval'
    approval.write_text('ok')
    monkeypatch.setenv('RAM_GUARDIAN_APPROVAL_FILE', str(approval))
    importlib.reload(rg_webui)
    # patch perform_action_and_measure to return a dummy success
    monkeypatch.setattr(rg_webui.ram_guardian, 'perform_action_and_measure', lambda f, timeout=10: {"pre_free_bytes": 0, "post_free_bytes": 1000, "delta_bytes": 1000, "success": True})
    with rg_webui.app.test_client() as c:
        r = c.post('/api/action', headers={'Authorization': 'Bearer s3cr3t'}, json={"action":"quit_app", "target":"Safari"})
        assert r.status_code == 200
        j = r.get_json()
        assert j['success'] is True
