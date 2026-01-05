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

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b""
            obj = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception as e:
            self._send_json(400, {"error": "invalid-json", "msg": str(e)})
            return

        action = obj.get("action")
        if action == "ping":
            self._send_json(200, {"status": "ok"})
            return

        if action == "list_objects":
            # best-effort: try import bpy (works only inside Blender)
            try:
                import bpy
                objs = [{"name": o.name, "type": o.type} for o in bpy.data.objects]
                self._send_json(200, {"objects": objs})
            except Exception as e:
                self._send_json(200, {"error": "bpy-unavailable", "msg": str(e)})
            return

        self._send_json(400, {"error": "unknown-action", "action": action})

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
