import runpy
import sys
import types


def test_no_bpy_does_not_crash(capsys):
    # Ensure bpy is not present and the script exits cleanly (shouldn't raise)
    sys.modules.pop('bpy', None)
    runpy.run_path('cybercam-blender/scripts/dev/enable_cycles_gpu.py', run_name='__main__')
    captured = capsys.readouterr()
    # script prints start and done/failure messages; ensure it printed the start line
    assert 'enable_cycles_gpu.py: starting' in captured.out


def test_with_fake_bpy(capsys, monkeypatch):
    # Provide a minimal fake bpy module and ensure the script runs without error
    fake = types.ModuleType('bpy')

    class FakeCyclesPrefs:
        def __init__(self):
            self.compute_device_type = None
            self.devices = []

    class FakePrefs:
        def __init__(self):
            self.cycles = FakeCyclesPrefs()
            self.addons = {}

    fake.context = types.SimpleNamespace(preferences=FakePrefs())
    fake.data = types.SimpleNamespace(scenes=[])
    fake.ops = types.SimpleNamespace()

    monkeypatch.setitem(sys.modules, 'bpy', fake)

    runpy.run_path('cybercam-blender/scripts/dev/enable_cycles_gpu.py', run_name='__main__')
    captured = capsys.readouterr()
    assert 'enable_cycles_gpu.py: done' in captured.out
