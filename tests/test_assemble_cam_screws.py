import importlib.util
from pathlib import Path
import types

MODULE_PATH = Path(__file__).resolve().parents[1] / 'cybercam-blender' / 'scripts' / 'build' / 'assemble_cam.py'
spec = importlib.util.spec_from_file_location('assemble_cam', str(MODULE_PATH))
ac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ac)


class FakeMatrix:
    def to_translation(self):
        return (0.0, 0.0, 0.0)

    def to_3x3(self):
        return self

    def __matmul__(self, vec):
        # return vec as-is (vec is tuple-like)
        return vec


class FakeAnchor:
    def __init__(self):
        class M:
            pass

        self.matrix_world = FakeMatrix()


def test_create_screws_calls_n_times(monkeypatch):
    calls = []

    def fake_append(name):
        calls.append(name)
        # return a simple object with location attribute
        obj = types.SimpleNamespace()
        obj.location = None
        return obj

    anchor = FakeAnchor()
    parts_file = Path('dummy.blend')

    placed = ac.create_screws_at_anchor(parts_file, anchor, count=5, pattern='radial', radius=0.1,
                                        offset_z=0.0, start_angle=0.0, axis='Z', append_fn=fake_append)
    assert len(calls) == 5
    assert all(c == 'part_screw_M3' for c in calls)
    assert len(placed) == 5


def test_count_zero_no_calls(monkeypatch):
    calls = []

    def fake_append(name):
        calls.append(name)
        return types.SimpleNamespace()

    anchor = FakeAnchor()
    parts_file = Path('dummy.blend')
    placed = ac.create_screws_at_anchor(parts_file, anchor, count=0, pattern='radial', append_fn=fake_append)
    assert len(calls) == 0
    assert placed == []


def test_invalid_pattern_raises():
    anchor = FakeAnchor()
    parts_file = Path('dummy.blend')
    import pytest
    with pytest.raises(ValueError):
        ac.create_screws_at_anchor(parts_file, anchor, count=3, pattern='unknown_pattern')


def test_parameters_forwarded(monkeypatch):
    captured = {}

    def fake_place(count, pattern, radius, offset_z, start_angle, axis):
        captured['count'] = count
        captured['pattern'] = pattern
        captured['radius'] = radius
        captured['offset_z'] = offset_z
        captured['start_angle'] = start_angle
        captured['axis'] = axis
        return [(0, 0, 0)] * count

    # monkeypatch screw_utils.place_screws_positions
    import importlib.util as iu
    su_path = Path(__file__).resolve().parents[1] / 'cybercam-blender' / 'scripts' / 'build' / 'screw_utils.py'
    spec2 = iu.spec_from_file_location('screw_utils', str(su_path))
    su = iu.module_from_spec(spec2)
    spec2.loader.exec_module(su)

    monkeypatch.setattr(su, 'place_screws_positions', fake_place)

    # inject our modified module into sys.modules so assemble_cam imports it
    import sys
    import types
    pkg = types.ModuleType('scripts')
    pkg_build = types.ModuleType('scripts.build')
    pkg_build.screw_utils = su
    pkg.build = pkg_build
    sys.modules['scripts'] = pkg
    sys.modules['scripts.build'] = pkg_build
    sys.modules['scripts.build.screw_utils'] = su

    calls = []

    def fake_append(name):
        calls.append(name)
        return types.SimpleNamespace()

    anchor = FakeAnchor()
    parts_file = Path('dummy.blend')
    ac.create_screws_at_anchor(parts_file, anchor, count=4, pattern='grid', radius=0.2, offset_z=0.01, start_angle=0.1, axis='Y', append_fn=fake_append)

    assert captured['count'] == 4
    assert captured['pattern'] == 'grid'
    assert captured['radius'] == 0.2
    assert captured['offset_z'] == 0.01
    assert captured['start_angle'] == 0.1
    assert captured['axis'] == 'Y'
    assert len(calls) == 4
