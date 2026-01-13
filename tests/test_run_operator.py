import os
import tempfile
import time
import requests
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("addon_server", Path(__file__).resolve().parents[1] / "20_BLENDER_INTEGRATION" / "addon_template" / "server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


def test_run_operator_forbidden():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    # token required - create one
    dirpath = tempfile.mkdtemp()
    os.environ["HOME"] = dirpath
    os.environ["XARVIS_BLENDER_REQUIRE_TOKEN"] = "1"
    tokenfile = f"{dirpath}/.config/xarvis/blender.token"
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")
    headers = {"Authorization": "Bearer mytoken"}

    r = requests.post(url, json={"action":"run_operator","operator":"object.unknown_op","params":{}}, headers=headers, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is False
    assert j.get("error",{}).get("code") == "forbidden_operator"
    server.stop_server()


def test_run_operator_invalid_params():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    dirpath = tempfile.mkdtemp()
    os.environ["HOME"] = dirpath
    os.environ["XARVIS_BLENDER_REQUIRE_TOKEN"] = "1"
    tokenfile = f"{dirpath}/.config/xarvis/blender.token"
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")
    headers = {"Authorization": "Bearer mytoken"}

    # choose a whitelisted op
    op = "object.modifier_add"
    # invalid params (nested dict)
    r = requests.post(url, json={"action":"run_operator","operator":op,"params":{"a":{"nested":1}}}, headers=headers, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is False
    assert j.get("error",{}).get("code") == "invalid_params"
    server.stop_server()


def test_run_operator_bpy_missing():
    dirpath = tempfile.mkdtemp()
    os.environ["HOME"] = dirpath
    os.environ["XARVIS_BLENDER_REQUIRE_TOKEN"] = "1"
    tokenfile = f"{dirpath}/.config/xarvis/blender.token"
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    headers = {"Authorization": "Bearer mytoken"}
    r = requests.post(url, json={"action":"run_operator","operator":"object.modifier_add","params":{"type":"SUBSURF"}, "as_job": False}, headers=headers, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is False
    assert j.get("error",{}).get("code") == "bpy_unavailable"
    server.stop_server()


def test_run_operator_happy_path_mock_bpy():
    import sys
    import types

    fake_bpy = types.SimpleNamespace()
    # build nested ops: bpy.ops.object.modifier_add
    class _Call:
        def __call__(self, **kwargs):
            # simulate some work
            return {'result': 'ok'}
    ops_object = types.SimpleNamespace(modifier_add=_Call())
    ops = types.SimpleNamespace(object=ops_object)
    fake_bpy.ops = ops

    sys.modules['bpy'] = fake_bpy

    # require token
    dirpath = tempfile.mkdtemp()
    os.environ["HOME"] = dirpath
    os.environ["XARVIS_BLENDER_REQUIRE_TOKEN"] = "1"
    tokenfile = f"{dirpath}/.config/xarvis/blender.token"
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")

    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    headers = {"Authorization": "Bearer mytoken"}

    r = requests.post(url, json={"action":"run_operator","operator":"object.modifier_add","params":{"type":"SUBSURF"}}, headers=headers, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    job_id = j.get("data",{}).get("job_id")
    assert job_id

    done = False
    for _ in range(200):
        r2 = requests.post(url, json={"action":"get_job_status","job_id": job_id}, headers=headers, timeout=2)
        s = r2.json()
        if s.get("ok") and s.get("data",{}).get("status") == 'done':
            done = True
            break
        time.sleep(0.01)
    assert done

    server.stop_server()
    del sys.modules['bpy']
