import pytest
from xarvis.memory.store import load_json, save_output
from xarvis.memory import store


def test_round_trip(tmp_path):
    path = tmp_path / 'nested' / 'output.json'
    payload = save_output({'message': 'México'}, path)
    assert load_json(path) == payload
    assert payload['timestamp']
    assert list(path.parent.iterdir()) == [path]


def test_serialization_failure_preserves_previous_output(tmp_path):
    path = tmp_path / 'output.json'
    previous = save_output({'value': 1}, path)
    with pytest.raises(TypeError):
        save_output({'value': object()}, path)
    assert load_json(path) == previous
    assert list(tmp_path.iterdir()) == [path]


def test_replace_failure_preserves_previous_output(tmp_path, monkeypatch):
    path = tmp_path / 'output.json'
    previous = save_output({'value': 1}, path)
    def fail(*args):
        raise OSError('simulated replace failure')
    monkeypatch.setattr(store.os, 'replace', fail)
    with pytest.raises(OSError):
        save_output({'value': 2}, path)
    assert load_json(path) == previous
    assert list(tmp_path.iterdir()) == [path]
