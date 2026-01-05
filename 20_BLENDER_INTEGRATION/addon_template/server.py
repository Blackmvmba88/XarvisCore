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
            try:
                import bpy
                # if Blender is busy rendering
                if getattr(bpy.context.scene, "rendering", False):
                    if not async_flag:
                        self._send_error("busy", "Blender is currently rendering", None, 409)
                        return
                # For safety in this template, do not actually perform heavy render in tests
                # Instead, if running inside Blender, call bpy.ops.render.render()
                if async_flag:
                    # schedule job: for now, just respond scheduled
                    self._send_ok({"job_id": "job-0001", "status": "scheduled"})
                else:
                    # perform a blocking render
                    try:
                        # set frame if provided
                        if frame is not None:
                            bpy.context.scene.frame_set(int(frame))
                        # set camera
                        if camera is not None:
                            cam = bpy.data.objects.get(camera)
                            if cam:
                                bpy.context.scene.camera = cam
                        # set output path if provided
                        if output:
                            bpy.context.scene.render.filepath = output
                        bpy.ops.render.render(write_still=True)
                        out_path = bpy.context.scene.render.filepath
                        self._send_ok({"output": out_path, "render_time_seconds": 0.0})
                    except Exception as e:
                        self._send_error("render_failed", "Render operation failed", {"msg": str(e)}, 500)
            except Exception as e:
                self._send_error("bpy_unavailable", "Blender (bpy) unavailable", {"msg": str(e)}, 200)
            return

        self._send_error("unknown_action", "Unknown action requested", {"action": action}, 400)

    def log_message(self, format, *args):
        # keep quiet; Blender/host will handle logging if needed
        pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True


class ServerThread(threading.Thread):
    def __init__(self, host: str = "127.0.0.1", port: int = 47211):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self._httpd: Optional[ThreadedHTTPServer] = None

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
