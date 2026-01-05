import time
import requests
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("addon_server", Path(__file__).resolve().parents[1] / "20_BLENDER_INTEGRATION" / "addon_template" / "server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


def test_render_animation_job_creation_and_bpy_missing():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"

    # require token via env
    import os, tempfile
    dirpath = tempfile.mkdtemp()
    os.environ["HOME"] = dirpath
    os.environ["XARVIS_BLENDER_REQUIRE_TOKEN"] = "1"
    tokenfile = f"{dirpath}/.config/xarvis/blender.token"
    import os
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write("mytoken")

    headers = {"Authorization": "Bearer mytoken"}
    payload = {
        "action": "render_animation",
        "frame_start": 1,
        "frame_end": 3,
        "output_dir": "/tmp/xarvis_renders",
        "async": True
    }
    r = requests.post(url, json=payload, headers=headers, timeout=5)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    job_id = j.get("data", {}).get("job_id")
    assert job_id

    # poll job status until it becomes error (because bpy missing in this env)
    status_url = url
    ok = False
    for _ in range(50):
        r2 = requests.post(status_url, json={"action": "get_job_status", "job_id": job_id}, headers=headers, timeout=2)
        assert r2.status_code == 200
        s = r2.json()
        if s.get("ok"):
            st = s.get("data", {}).get("status")
            if st in ("error", "done", "cancelled"):
                ok = True
                break
        time.sleep(0.1)
    assert ok
    server.stop_server()


def test_cancel_job():
    # Create a job where runner respects cancel flag by sleeping
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    st = server._server_thread

    def long_job(jobmgr, job, duration=2):
        import time
        for i in range(20):
            if job.get('cancel_requested'):
                return {'msg': 'cancelled_early'}
            time.sleep(duration/20.0)
            with jobmgr._lock:
                job['progress'] = (i+1)/20.0*100
        return {'msg': 'done'}

    job_id = st.jobs.create_job(long_job, args=(2,))
    # cancel immediately
    r = requests.post(url, json={"action":"cancel_job","job_id":job_id}, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") and j.get("data",{}).get("cancelled") is True
    # check status becomes cancelled
    time.sleep(0.2)
    r2 = requests.post(url, json={"action":"get_job_status","job_id":job_id}, timeout=2)
    s = r2.json()
    assert s.get("ok") and s.get("data",{}).get("status") in ("cancelled","done")
    server.stop_server()
