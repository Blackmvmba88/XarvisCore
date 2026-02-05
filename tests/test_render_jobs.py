import time
import requests
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("addon_server", Path(__file__).resolve().parents[1] / "20_BLENDER_INTEGRATION" / "addon_template" / "server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


def test_render_animation_job_creation_and_bpy_missing(monkeypatch):
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"

    # require token via env
    import os, tempfile
    dirpath = tempfile.mkdtemp()
    monkeypatch.setenv("HOME", dirpath)
    monkeypatch.setenv("XARVIS_BLENDER_REQUIRE_TOKEN", "1")
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


def test_render_animation_progress_simulated():
    # Simulate an animation runner that updates progress per frame
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    st = server._server_thread

    def fake_animation(jobmgr, job, frames=10, per_frame=0.01):
        import time
        last = -1
        for i in range(frames):
            if job.get('cancel_requested'):
                return {'msg': 'cancelled'}
            time.sleep(per_frame)
            with jobmgr._lock:
                job['progress'] = (i+1)/frames*100.0
                if job['progress'] < last:
                    raise RuntimeError("progress decreased")
                last = job['progress']
        return {'msg': 'done'}

    job_id = st.jobs.create_job(fake_animation, args=(20,0.001))
    # poll and ensure progress increases monotonically and ends at 100
    prev = -1
    finished = False
    for _ in range(500):
        r = requests.post(url, json={"action":"get_job_status","job_id":job_id}, timeout=2)
        s = r.json()
        assert s.get("ok")
        data = s.get("data", {})
        prog = data.get("progress")
        if prog is not None:
            assert prog >= prev
            prev = prog
        if data.get("status") in ("done", "error", "cancelled"):
            finished = True
            break
        time.sleep(0.01)
    assert finished
    r_final = requests.post(url, json={"action":"get_job_status","job_id":job_id}, timeout=2)
    final = r_final.json().get("data",{})
    assert final.get("status") == "done"
    assert final.get("progress") == 100.0
    server.stop_server()


def test_render_animation_progress_cancel_mid():
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    st = server._server_thread

    def fake_animation(jobmgr, job, frames=50, per_frame=0.02):
        import time
        for i in range(frames):
            if job.get('cancel_requested'):
                return {'msg': 'cancelled'}
            time.sleep(per_frame)
            with jobmgr._lock:
                job['progress'] = (i+1)/frames*100.0
        return {'msg': 'done'}

    job_id = st.jobs.create_job(fake_animation, args=(50,0.01))
    # wait a bit for progress to start
    time.sleep(0.05)
    # cancel job
    r = requests.post(url, json={"action":"cancel_job","job_id":job_id}, timeout=2)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") and j.get("data",{}).get("cancelled") is True
    # wait and verify status cancelled and progress < 100
    time.sleep(0.1)
    r2 = requests.post(url, json={"action":"get_job_status","job_id":job_id}, timeout=2)
    s = r2.json()
    assert s.get("ok")
    st_data = s.get("data",{})
    assert st_data.get("status") == "cancelled"
    assert 0 <= st_data.get("progress",0) < 100.0
    server.stop_server()


def test_frame_hook_registers_and_releases(monkeypatch):
    # env enable frame hooks
    monkeypatch.setenv('XARVIS_BLENDER_FRAME_HOOKS', '1')
    host, port = server.start_server(host="127.0.0.1", port=0)
    url = f"http://{host}:{port}/"
    st = server._server_thread

    def long_job(jobmgr, job, duration=1.0):
        import time
        # keep running until cancelled
        for i in range(100):
            if job.get('cancel_requested'):
                return {'msg': 'cancelled'}
            time.sleep(duration/100.0)
        return {'msg': 'done'}

    job_id = st.jobs.create_job(long_job, args=(1.0,), use_frame_hook=True, meta={'frame_start':1,'frame_end':100})
    # wait until job is running and hook registered
    import time
    t0 = time.time()
    while time.time() - t0 < 2.0:
        if st._frame_hook_registered:
            break
        time.sleep(0.01)
    assert st._frame_hook_registered is True
    # cancel job and ensure hook de-registers
    r = requests.post(url, json={"action":"cancel_job","job_id":job_id}, timeout=2)
    assert r.status_code == 200
    # wait until hook is deactivated
    t0 = time.time()
    while time.time() - t0 < 2.0:
        if not st._frame_hook_registered:
            break
        time.sleep(0.01)
    assert st._frame_hook_registered is False
    server.stop_server()


def test_frame_hook_simulated_updates_progress(monkeypatch):
    monkeypatch.setenv('XARVIS_BLENDER_FRAME_HOOKS', '1')
    host, port = server.start_server(host="127.0.0.1", port=0)
    st = server._server_thread

    def sleeper(jobmgr, job, duration=1.0):
        import time
        # remain running for a short while
        for i in range(50):
            if job.get('cancel_requested'):
                return {'msg': 'cancelled'}
            time.sleep(duration/50.0)
        return {'msg': 'done'}

    job_id = st.jobs.create_job(sleeper, args=(1.0,), use_frame_hook=True, meta={'frame_start':1,'frame_end':10})
    # wait until hook active
    import time
    t0 = time.time()
    while time.time() - t0 < 2.0:
        if st._frame_hook_registered:
            break
        time.sleep(0.01)
    assert st._frame_hook_registered is True
    # simulate blender reporting frame 5
    st._frame_hook_notify(5)
    # check job progress updated to expected value
    j = st.jobs.get_job(job_id)
    assert j.get('progress') is not None
    expected = (5 - 1 + 1) / (10 - 1 + 1) * 100.0
    assert j.get('progress') >= expected
    # cleanup
    r = requests.post(f"http://{host}:{port}/", json={"action":"cancel_job","job_id":job_id}, timeout=2)
    server.stop_server()


def test_frame_hook_disabled_no_effect(monkeypatch):
    monkeypatch.delenv('XARVIS_BLENDER_FRAME_HOOKS', raising=False)
    host, port = server.start_server(host="127.0.0.1", port=0)
    st = server._server_thread

    def sleeper(jobmgr, job, duration=0.5):
        import time
        for i in range(20):
            if job.get('cancel_requested'):
                return {'msg': 'cancelled'}
            time.sleep(duration/20.0)
        return {'msg': 'done'}

    job_id = st.jobs.create_job(sleeper, args=(0.5,), use_frame_hook=True, meta={'frame_start':1,'frame_end':10})
    # ensure hook not active
    import time
    time.sleep(0.05)
    assert st._frame_hook_registered is False
    # simulate frame notify - should have no effect
    st._frame_hook_notify(5)
    j = st.jobs.get_job(job_id)
    assert j.get('progress') == 0.0
    r = requests.post(f"http://{host}:{port}/", json={"action":"cancel_job","job_id":job_id}, timeout=2)
    server.stop_server()
