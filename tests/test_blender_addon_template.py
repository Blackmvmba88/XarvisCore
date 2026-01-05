import requests
import threading
import time

from pathlib import Path
import importlib.util

# import our server without relying on Blender
spec = importlib.util.spec_from_file_location("addon_server", Path(__file__).resolve().parents[1] / "20_BLENDER_INTEGRATION" / "addon_template" / "server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


def test_server_ping_and_shutdown():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    # ping
    r = requests.post(url, json={"action": "ping"}, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True and j.get("data", {}).get("status") == "ok"
    # stop
    server.stop_server()


def test_list_objects_when_bpy_missing():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    r = requests.post(url, json={"action": "list_objects"}, timeout=2)
    j = r.json()
    # outside Blender the handler should return an explanatory error with ok:false
    assert j.get("ok") is False
    assert j.get("error", {}).get("code") == "bpy_unavailable"
    server.stop_server()


def test_get_scene_state_bpy_missing():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    r = requests.post(url, json={"action": "get_scene_state"}, timeout=2)
    j = r.json()
    assert j.get("ok") is False and j.get("error", {}).get("code") == "bpy_unavailable"
    server.stop_server()


def test_render_still_requires_token():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    # ensure env requires token
    import os, tempfile
    dirpath = tempfile.mkdtemp()
    os.environ["HOME"] = dirpath
    os.environ["XARVIS_BLENDER_REQUIRE_TOKEN"] = "1"

    r = requests.post(url, json={"action": "render_still"}, timeout=2)
    j = r.json()
    assert j.get("ok") is False and j.get("error", {}).get("code") == "unauthorized"

    # write a token file and try with Authorization header
    tokenfile = os.path.join(dirpath, ".config/xarvis/blender.token")
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")
    headers = {"Authorization": "Bearer mytoken"}
    r2 = requests.post(url, json={"action": "render_still"}, headers=headers, timeout=2)
    j2 = r2.json()
    assert j2.get("ok") is False and j2.get("error", {}).get("code") == "bpy_unavailable"
    server.stop_server()
