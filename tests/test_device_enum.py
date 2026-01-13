import importlib.util
import sys
import types
from pathlib import Path


def _load_module(path):
    spec = importlib.util.spec_from_file_location('device_enum', str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_detect_devices_no_bpy():
    sys.modules.pop('bpy', None)
    m = _load_module(Path('20_BLENDER_INTEGRATION/hero/device_enum.py'))
    res = m.detect_devices()
    assert isinstance(res, dict)


def test_detect_devices_with_fake_bpy(monkeypatch):
    fake = types.ModuleType('bpy')

    class FakeDevice:
        def __init__(self, name):
            self.name = name

    class FakeCycles:
        def __init__(self):
            self.compute_device_type = 'CUDA'
            self.devices = [FakeDevice('GPU0'), FakeDevice('GPU1')]

    fake.context = types.SimpleNamespace(preferences=types.SimpleNamespace(cycles=FakeCycles()))
    monkeypatch.setitem(sys.modules, 'bpy', fake)

    m = _load_module(Path('20_BLENDER_INTEGRATION/hero/device_enum.py'))
    res = m.detect_devices()
    assert 'CUDA' in res and res['CUDA'] == ['GPU0', 'GPU1']
