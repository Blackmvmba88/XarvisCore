import json

import pytest

from xarvis.integrations import warpblack


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_bridge_must_be_loopback():
    config = warpblack.WarpBlackConfig(
        base_url="http://example.com:8765", token="secret"
    )
    with pytest.raises(warpblack.WarpBlackConfigurationError):
        config.validate()


def test_execute_keeps_request_id(monkeypatch):
    def fake_urlopen(request, timeout):
        body = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"ok": True, "request_id": body["request_id"]})

    monkeypatch.setattr(warpblack, "urlopen", fake_urlopen)
    adapter = warpblack.WarpBlackAdapter(
        warpblack.WarpBlackConfig(token="secret")
    )
    result = adapter.execute(
        ["git", "status"], request_id="xarvis:test"
    )
    assert result["request_id"] == "xarvis:test"


def test_execute_rejects_wrong_request_id(monkeypatch):
    monkeypatch.setattr(
        warpblack,
        "urlopen",
        lambda request, timeout: FakeResponse(
            {"ok": True, "request_id": "wrong"}
        ),
    )
    adapter = warpblack.WarpBlackAdapter(
        warpblack.WarpBlackConfig(token="secret")
    )
    with pytest.raises(warpblack.WarpBlackError):
        adapter.execute(
            ["git", "status"], request_id="xarvis:expected"
        )
