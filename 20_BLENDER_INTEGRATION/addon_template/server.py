"""Small HTTP server to expose a JSON command endpoint inside Blender.

Safety notes:
- The server binds to localhost by default. Do NOT bind to 0.0.0.0 in production.
- Commands that require Blender import will return an explanatory error outside Blender.
"""
from __future__ import annotations

import json
import threading
import socket
import socketserver
import http.server
from typing import Optional, Tuple


class JSONHandler(http.server.BaseHTTPRequestHandler):
    server_version = "XarvisBlenderServer/0.1"

    def _send_json(self, code: int, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_error(self, code: str, message: str, details: dict | None = None, http_code: int = 400):
        payload = {"ok": False, "error": {"code": code, "message": message}}
        if details:
            payload["error"]["details"] = details
        self._send_json(http_code, payload)

    def _send_ok(self, data: dict):
        self._send_json(200, {"ok": True, "data": data})

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b""
            return json.loads(raw.decode("utf-8")) if raw else {}
        except Exception as e:
            return None, str(e)

    def _check_token(self):
        """Validate token using the following precedence:
        - If running inside Blender and addon prefs require token -> read token_path from prefs
        - Else if env var XARVIS_BLENDER_REQUIRE_TOKEN is set to "1" -> require token using default path
        - Else: if token file exists and contains a token, require it; otherwise allow (development convenience)
        """
        import os
        # try Blender addon prefs first (if available)
        try:
            import bpy
            # NOTE: the addon module name may differ in installations; 'addon_template' is the local module name here
            mod = bpy.context.preferences.addons.get('addon_template')
            if mod:
                prefs = mod.preferences
                if getattr(prefs, 'require_token', False):
                    token_path = getattr(prefs, 'token_path', None) or os.path.expanduser('~/.config/xarvis/blender.token')
                    if not os.path.exists(token_path):
                        return False
                    try:
                        with open(token_path, 'r', encoding='utf-8') as f:
                            token = f.read().strip()
                    except Exception:
                        return False
                    auth = self.headers.get('Authorization','')
                    if auth.startswith('Bearer '):
                        return auth.split(None,1)[1].strip() == token
                    return False
        except Exception:
            # not running inside Blender or prefs not available; fallback to env / file
            pass

        # env var override for tests and deployments
        require_env = os.environ.get('XARVIS_BLENDER_REQUIRE_TOKEN')
        token_path = os.path.expanduser('~/.config/xarvis/blender.token')
        if require_env == '1':
            if not os.path.exists(token_path):
                return False
            try:
                with open(token_path, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
            except Exception:
                return False
            auth = self.headers.get('Authorization','')
            if auth.startswith('Bearer '):
                return auth.split(None,1)[1].strip() == token
            return False

        # default: if token file exists, enforce it; else allow
        if os.path.exists(token_path):
            try:
                with open(token_path, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
            except Exception:
                return False
            auth = self.headers.get('Authorization','')
            if auth.startswith('Bearer '):
                return auth.split(None,1)[1].strip() == token
            return False

        return True  # no token configured -> allow (development convenience)

    def do_POST(self):
        obj, err = self._read_json(), None
        if obj is None:
            # fallback: _read_json returned None if exception occurred
            try:
                # try again to capture message
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length else b""
                _ = json.loads(raw.decode("utf-8"))
            except Exception as e:
                self._send_error("invalid_json", "Could not parse JSON", {"msg": str(e)}, 400)
                return

        action = obj.get("action") if isinstance(obj, dict) else None
        if not action:
            self._send_error("invalid_input", "Missing 'action' field")
            return

        if action == "ping":
            self._send_ok({"status": "ok"})
            return

        if action == "list_objects":
            try:
                import bpy
                objs = [{"name": o.name, "type": o.type} for o in bpy.data.objects]
                self._send_ok({"objects": objs})
            except Exception as e:
                self._send_error("bpy_unavailable", "Blender (bpy) unavailable", {"msg": str(e)}, 200)
            return

        if action == "get_scene_state":
            # read optional include list
            include = obj.get("include", ["cameras", "render", "frame_range"]) if isinstance(obj, dict) else ["cameras","render","frame_range"]
            allowed = set(["cameras","render","frame_range","objects","materials"])
            if not isinstance(include, list) or any(i not in allowed for i in include):
                self._send_error("invalid_input", "Invalid 'include' list", {"allowed": list(allowed)})
                return
            try:
                import bpy
                data = {}
                if "cameras" in include:
                    cams = []
                    for c in bpy.data.cameras:
                        cams.append({"name": c.name})
                    data["cameras"] = cams
                if "render" in include:
                    scene = bpy.context.scene
                    data["render"] = {"engine": scene.render.engine, "resolution": [scene.render.resolution_x, scene.render.resolution_y]}
                if "frame_range" in include:
                    s = bpy.context.scene
                    data["frame_range"] = {"start": s.frame_start, "end": s.frame_end}
                if "objects" in include:
                    data["objects"] = [{"name": o.name, "type": o.type} for o in bpy.data.objects]
                self._send_ok(data)
            except Exception as e:
                self._send_error("bpy_unavailable", "Blender (bpy) unavailable", {"msg": str(e)}, 200)
            return

        if action == "render_still":
            # privileged action: check token
            if not self._check_token():
                self._send_error("unauthorized", "Missing or invalid token", None, 403)
                return
            # validate inputs
            camera = obj.get("camera")
            frame = obj.get("frame")
            output = obj.get("output") or ""
            async_flag = bool(obj.get("async", False))
            timeout = int(obj.get("timeout_seconds", 600))
            # Basic input validation
            if output and not isinstance(output, str):
                self._send_error("invalid_input", "output must be a filepath string")
                return

            # Use job manager for both async and sync paths; sync will wait for job completion
            def render_runner(jobmgr, job, camera=None, frame=None, output=None):
                # Runner called in a separate thread; should return info dict on success
                import time
                try:
                    import bpy
                    if frame is not None:
                        bpy.context.scene.frame_set(int(frame))
                    if camera is not None:
                        cam = bpy.data.objects.get(camera)
                        if cam:
                            bpy.context.scene.camera = cam
                    if output:
                        bpy.context.scene.render.filepath = output
                    # perform render animation call with write_still
                    bpy.ops.render.render(write_still=True)
                    return {"output": bpy.context.scene.render.filepath}
                except Exception as e:
                    # raise to be caught by JobManager wrapper
                    raise

            try:
                # Check bpy availability early
                import bpy
            except Exception as e:
                self._send_error("bpy_unavailable", "Blender (bpy) unavailable", {"msg": str(e)}, 200)
                return

            # schedule job
            st = _server_thread
            job_id = st.jobs.create_job(render_runner, args=(camera, frame, output))
            if async_flag:
                self._send_ok({"job_id": job_id, "status": "scheduled"})
                return
            else:
                # sync path: wait for job to finish with timeout
                import time
                t0 = time.time()
                while time.time() - t0 < timeout:
                    j = st.jobs.get_job(job_id)
                    if not j:
                        break
                    if j.get('status') in ('done', 'error', 'cancelled'):
                        if j['status'] == 'done':
                            self._send_ok({"job_id": job_id, "result": j.get('result')})
                            return
                        else:
                            # propagate job error
                            self._send_error("render_failed", "Render job failed or cancelled", {"status": j.get('status'), "error": j.get('error')}, 500)
                            return
                    time.sleep(0.1)
                self._send_error("timeout", "Render timed out", None, 504)
            return

        if action == "render_animation":
            # privileged action: check token
            if not self._check_token():
                self._send_error("unauthorized", "Missing or invalid token", None, 403)
                return
            # validate inputs
            frame_start = obj.get("frame_start")
            frame_end = obj.get("frame_end")
            output_dir = obj.get("output_dir")
            async_flag = bool(obj.get("async", True))
            fmt = obj.get("format", "PNG")
            if frame_start is not None and frame_end is not None:
                try:
                    frame_start = int(frame_start); frame_end = int(frame_end)
                except Exception:
                    self._send_error("invalid_input", "frame_start and frame_end must be integers")
                    return
            if not output_dir or not isinstance(output_dir, str):
                self._send_error("invalid_input", "output_dir is required and must be a string")
                return
            if fmt not in ("PNG","JPEG","EXR","MP4"):
                self._send_error("invalid_input", "unsupported format", {"supported": ["PNG","JPEG","EXR","MP4"]})
                return

            def animation_runner(jobmgr, job, frame_start, frame_end, output_dir, fmt):
                """Render animation by iterating frames and rendering per-frame.
                Update job['progress'] after each frame. Respect job['cancel_requested'].
                """
                import os
                try:
                    import bpy
                    scene = bpy.context.scene
                    start = frame_start if frame_start is not None else scene.frame_start
                    end = frame_end if frame_end is not None else scene.frame_end
                    total = max(1, end - start + 1)
                    # ensure output dir exists
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                    except Exception:
                        pass
                    for idx, f in enumerate(range(start, end + 1)):
                        # check cancel
                        if job.get('cancel_requested'):
                            return {'msg': 'cancelled'}
                        scene.frame_set(f)
                        # pick per-frame filename
                        if fmt == 'MP4':
                            # render animation to a container: use animation render at the end
                            # For simplicity, render frames to images and rely on external packaging or Blender settings
                            pass
                        ext = 'png' if fmt == 'PNG' else ('jpg' if fmt == 'JPEG' else 'exr')
                        out_file = os.path.join(output_dir, f'frame_{f:04d}.{ext}')
                        scene.render.filepath = out_file
                        bpy.ops.render.render(write_still=True)
                        # update progress
                        with jobmgr._lock:
                            job['progress'] = (idx + 1) / total * 100.0
                    return {"output_dir": output_dir}
                except Exception:
                    raise

            st = _server_thread
            job_id = st.jobs.create_job(animation_runner, args=(frame_start, frame_end, output_dir, fmt))
            self._send_ok({"job_id": job_id, "status": "scheduled"})
            return

        if action == "get_job_status":
            job_id = obj.get("job_id")
            if not job_id:
                self._send_error("invalid_input", "job_id is required")
                return
            st = _server_thread
            j = st.jobs.get_job(job_id)
            if not j:
                self._send_error("not_found", "job not found")
                return
            self._send_ok({"job_id": job_id, "status": j.get('status'), "progress": j.get('progress'), "result": j.get('result'), "error": j.get('error')})
            return

        if action == "cancel_job":
            job_id = obj.get("job_id")
            if not job_id:
                self._send_error("invalid_input", "job_id is required")
                return
            st = _server_thread
            ok = st.jobs.cancel_job(job_id)
            if not ok:
                self._send_error("not_found", "job not found")
                return
            self._send_ok({"job_id": job_id, "cancelled": True})
            return

        self._send_error("unknown_action", "Unknown action requested", {"action": action}, 400)

    def log_message(self, format, *args):
        # keep quiet; Blender/host will handle logging if needed
        pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True


class JobManager:
    """Simple in-memory job manager for asynchronous jobs.
    Jobs structure:
    { job_id: { 'status': 'queued'|'running'|'done'|'error'|'cancelled', 'progress': 0.0, 'result': {...}, 'error': {...}, 'thread': Thread, 'cancel_requested': False }}
    """
    def __init__(self):
        self._jobs = {}
        self._lock = threading.Lock()
        self._counter = 0

    def create_job(self, target, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        with self._lock:
            self._counter += 1
            job_id = f"job-{self._counter:04d}"
            job = {
                'status': 'queued',
                'progress': 0.0,
                'result': None,
                'error': None,
                'thread': None,
                'cancel_requested': False,
            }
            self._jobs[job_id] = job

        def wrapper():
            with self._lock:
                job['status'] = 'running'
                job['progress'] = 0.0
            try:
                res = target(self, job, *args, **kwargs)
                with self._lock:
                    if job['cancel_requested']:
                        job['status'] = 'cancelled'
                    else:
                        job['status'] = 'done'
                        job['result'] = res
                        job['progress'] = 100.0
            except Exception as e:
                with self._lock:
                    job['status'] = 'error'
                    job['error'] = {'msg': str(e)}

        th = threading.Thread(target=wrapper, daemon=True)
        with self._lock:
            job['thread'] = th
        th.start()
        return job_id

    def get_job(self, job_id):
        with self._lock:
            return dict(self._jobs.get(job_id, {})) if job_id in self._jobs else None

    def cancel_job(self, job_id):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            job['cancel_requested'] = True
            return True


class ServerThread(threading.Thread):
    def __init__(self, host: str = "127.0.0.1", port: int = 47211):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self._httpd: Optional[ThreadedHTTPServer] = None
        self.jobs = JobManager()

    def run(self):
        with ThreadedHTTPServer((self.host, self.port), JSONHandler) as httpd:
            self._httpd = httpd
            # store bound port (0 means ephemeral)
            self.port = httpd.server_address[1]
            httpd.serve_forever()

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()


# Module-level helpers for addon entrypoints
_server_thread: Optional[ServerThread] = None


def start_server(host: str = "127.0.0.1", port: int = 47211) -> Tuple[str, int]:
    global _server_thread
    if _server_thread is not None:
        return (_server_thread.host, _server_thread.port)
    st = ServerThread(host=host, port=port)
    st.start()
    # wait briefly until server thread binds
    import time
    timeout = 2.0
    t0 = time.time()
    while getattr(st, "port", None) == 0 and time.time() - t0 < timeout:
        time.sleep(0.01)
    _server_thread = st
    return (st.host, st.port)


def stop_server() -> None:
    global _server_thread
    if _server_thread:
        _server_thread.stop()
        _server_thread = None
