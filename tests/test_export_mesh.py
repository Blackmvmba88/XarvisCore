import os
import tempfile
import time
import requests
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("addon_server", Path(__file__).resolve().parents[1] / "20_BLENDER_INTEGRATION" / "addon_template" / "server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


def test_export_mesh_input_validation(monkeypatch):
    monkeypatch.delenv("XARVIS_BLENDER_REQUIRE_TOKEN", raising=False)
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    # missing format
    r = requests.post(url, json={"action": "export_mesh", "output_path": "/tmp/x.ex"}, timeout=2)
    assert r.status_code == 200 or r.status_code == 400
    j = r.json()
    assert j.get("ok") is False
    server.stop_server()


def test_export_mesh_forbidden_path(monkeypatch):
    monkeypatch.delenv("XARVIS_BLENDER_REQUIRE_TOKEN", raising=False)
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    # attempt to write outside allowed roots
    r = requests.post(url, json={"action": "export_mesh", "format": "GLTF", "output_path": "/etc/passwd"}, timeout=2)
    assert r.status_code == 200 or r.status_code == 400
    j = r.json()
    assert j.get("ok") is False
    assert j.get("error", {}).get("code") == "forbidden_path"
    server.stop_server()


def test_export_mesh_bpy_missing(monkeypatch):
    # require token via env (privileged action)
    dirpath = tempfile.mkdtemp()
    monkeypatch.setenv("HOME", dirpath)
    monkeypatch.setenv("XARVIS_BLENDER_REQUIRE_TOKEN", "1")
    tokenfile = f"{dirpath}/.config/xarvis/blender.token"
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")

    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    headers = {"Authorization": "Bearer mytoken"}
    r = requests.post(url, json={"action": "export_mesh", "format": "GLTF", "output_path": "/tmp/x.ex"}, headers=headers, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is False
    assert j.get("error", {}).get("code") == "bpy_unavailable"
    server.stop_server()


def test_export_mesh_happy_path_with_mock_bpy(monkeypatch):
    # Use a fake bpy module to simulate exporter behavior
    import sys
    import types

    fake_bpy = types.SimpleNamespace()
    fake_bpy.data = types.SimpleNamespace(objects=[])

    def _make_op(name):
        def _op(**kwargs):
            fp = kwargs.get('filepath') or kwargs.get('filepath', None) or kwargs.get('filepath', None)
            # create the file to simulate export
            if fp:
                d = os.path.dirname(fp)
                os.makedirs(d, exist_ok=True)
                with open(fp, 'w', encoding='utf-8') as f:
                    f.write(f"fake-{name}")
            return {'msg': 'ok'}
        return _op

    export_scene = types.SimpleNamespace(gltf=_make_op('gltf'), fbx=_make_op('fbx'), obj=_make_op('obj'))
    ops = types.SimpleNamespace(export_scene=export_scene)
    fake_bpy.ops = ops
    fake_bpy.data.objects = []

    sys.modules['bpy'] = fake_bpy

    # require token
    dirpath = tempfile.mkdtemp()
    monkeypatch.setenv("HOME", dirpath)
    monkeypatch.setenv("XARVIS_BLENDER_REQUIRE_TOKEN", "1")
    tokenfile = f"{dirpath}/.config/xarvis/blender.token"
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")

    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    headers = {"Authorization": "Bearer mytoken"}
    out = f"/tmp/xarvis_export_test_{int(time.time()*1000)}.gltf"
    r = requests.post(url, json={"action": "export_mesh", "format": "GLTF", "output_path": out}, headers=headers, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    job_id = j.get("data", {}).get("job_id")
    assert job_id

    # poll job status until done
    done = False
    for _ in range(200):
        r2 = requests.post(url, json={"action": "get_job_status", "job_id": job_id}, headers=headers, timeout=2)
        s = r2.json()
        if s.get("ok") and s.get("data", {}).get("status") == 'done':
            done = True
            break
        time.sleep(0.01)
    assert done

    # check file was created
    assert os.path.exists(out)

    # cleanup
    try:
        os.remove(out)
    except Exception:
        pass
    server.stop_server()
    del sys.modules['bpy']
