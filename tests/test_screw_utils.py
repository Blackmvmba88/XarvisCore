import importlib.util
from pathlib import Path
import math

MODULE_PATH = Path(__file__).resolve().parents[1] / 'cybercam-blender' / 'scripts' / 'build' / 'screw_utils.py'
spec = importlib.util.spec_from_file_location('screw_utils', str(MODULE_PATH))
su = importlib.util.module_from_spec(spec)
spec.loader.exec_module(su)


def test_zero_count():
    assert su.place_screws_positions(0) == []


def test_radial_count_and_start_angle():
    pts1 = su.place_screws_positions(4, pattern='radial', radius=1.0, start_angle=0.0)
    pts2 = su.place_screws_positions(4, pattern='radial', radius=1.0, start_angle=math.pi/2)
    assert len(pts1) == 4
    assert len(pts2) == 4
    assert pts1[0] != pts2[0]


def test_invalid_pattern_raises():
    import pytest
    with pytest.raises(ValueError):
        su.place_screws_positions(3, pattern='unknown')


def test_linear_positions_centered():
    pts = su.place_screws_positions(3, pattern='linear', radius=0.1, axis='X')
    assert len(pts) == 3
    xs = [p[0] for p in pts]
    assert xs[0] < 0 and abs(xs[1]) < 1e-9 and xs[2] > 0
