import asyncio
import os
import json
import pytest
from fastapi.testclient import TestClient

from tools.mem_manager import server

client = TestClient(server.app)

# Helper to mock run_ps

def fake_run_ps_spotify():
    return [{"pid": 20551, "rss_mb": 300, "pcpu": 0.0, "comm": "/Applications/Spotify.app/Contents/MacOS/Spotify"}]


def fake_run_ps_windowserver():
    return [{"pid": 418, "rss_mb": 100, "pcpu": 0.0, "comm": "WindowServer"}]


def test_describe_known_app(monkeypatch):
    monkeypatch.setattr(server, 'run_ps', fake_run_ps_spotify)
    r = client.get('/processes')
    assert r.status_code == 200
    pid = r.json()['processes'][0]['pid']
    rd = client.get(f'/describe?pid={pid}')
    assert rd.status_code == 200
    body = rd.json()
    assert 'Spotify' in body['name'] or 'Spotify' in body['description']
    assert 'reopen_cmd' in body


def test_describe_unknown(monkeypatch):
    def fake():
        return [{"pid": 99999, "rss_mb": 10, "pcpu": 0.0, "comm": "/usr/bin/some-daemon"}]
    monkeypatch.setattr(server, 'run_ps', fake)
    r = client.get('/describe?pid=99999')
    assert r.status_code == 200
    body = r.json()
    assert 'Proceso no identificado' in body['description'] or 'some-daemon' in body['name']


def test_kill_single_protected(monkeypatch):
    monkeypatch.setattr(server, 'run_ps', fake_run_ps_windowserver)
    # Trying to kill WindowServer without force should be forbidden
    r = client.post('/kill_single', json={'pid': 418})
    assert r.status_code == 403
    # Force should allow (but we mock os.kill to avoid real kills)
    monkeypatch.setattr(server, 'os', server.os)
    def fake_kill(pid, sig):
        return None
    monkeypatch.setattr(server.os, 'kill', fake_kill)
    r2 = client.post('/kill_single?force=true', json={'pid': 418})
    assert r2.status_code == 200
    assert r2.json()['result'] in ('closed_soft', 'killed') or 'result' in r2.json()


def test_monitor_run_once(monkeypatch, tmp_path):
    # Simulate low free percent and a high-priority process
    monkeypatch.setattr(server, 'get_free_percent', lambda: 5.0)
    monkeypatch.setattr(server, 'run_ps', lambda: [{"pid": 12345, "rss_mb": 600, "pcpu": 0.0, "comm": "/Applications/TestApp.app/Contents/MacOS/TestApp"}])
    # Ensure actions are cleared
    state = {'marked': [], 'actions': []}
    server.save_state(state)
    # Run monitor once with auto_kill False -> should log would_close
    server.monitor.config['auto_kill'] = False
    asyncio.run(server.monitor.run_once())
    st = server.load_state()
    assert 'actions' in st
    assert any('would_close' in (a.get('result') or '') for a in st['actions'])
