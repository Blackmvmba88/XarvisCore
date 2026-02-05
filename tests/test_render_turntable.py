import importlib.util
from pathlib import Path
import tempfile
import os

# import module under test
MOD_PATH = Path(__file__).resolve().parents[1] / 'cybercam-blender' / 'scripts' / 'utils' / 'render_turntable.py'
spec = importlib.util.spec_from_file_location('render_turntable', str(MOD_PATH))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)


def test_frame_filenames(tmp_path):
    fps = rt._frame_filenames(tmp_path, frames=3, image_format='PNG')
    assert len(fps) == 3
    assert fps[0].name == 'frame_0001.png'
    assert fps[-1].name == 'frame_0003.png'


def test_render_invokes_bpy_and_writes_files(monkeypatch, tmp_path):
    # Create fake bpy
    class FakeRenderOps:
        def __init__(self):
            self.calls = []

        def render(self, write_still=True):
            # write to scene.render.filepath
            path = bpy.context.scene.render.filepath
            with open(path, 'w') as f:
                f.write('ok')
            self.calls.append(path)

    class FakeRender:
        def __init__(self):
            self.resolution_x = 0
            self.resolution_y = 0
            self.image_settings = types.SimpleNamespace()
            self.image_settings.file_format = 'PNG'
            self.filepath = ''

    class FakeContextScene:
        def __init__(self):
            self.render = FakeRender()
            self._frame = 0

        def frame_set(self, f):
            self._frame = f

    class FakeDataObjects(dict):
        def get(self, name):
            if name == 'CAM_TURNTABLE':
                return object()
            return None

    import types
    bpy = types.SimpleNamespace()
    bpy.ops = types.SimpleNamespace()
    bpy.ops.render = FakeRenderOps()
    bpy.data = types.SimpleNamespace()
    bpy.data.objects = FakeDataObjects()
    bpy.context = types.SimpleNamespace()
    bpy.context.scene = FakeContextScene()

    # inject into sys.modules
    import sys
    monkeypatch.setitem(sys.modules, 'bpy', bpy)

    out = rt.render_turntable(tmp_path, frames=2, width=64, height=64, image_format='PNG', camera_name='CAM_TURNTABLE')
    assert len(out) == 2
    for p in out:
        assert p.exists()
        assert p.read_text() == 'ok'


def test_missing_camera_raises(monkeypatch, tmp_path):
    import types
    bpy = types.SimpleNamespace()
    bpy.data = types.SimpleNamespace()
    bpy.data.objects = {}  # no camera
    import sys
    monkeypatch.setitem(sys.modules, 'bpy', bpy)

    try:
        rt.render_turntable(tmp_path, frames=1, camera_name='CAM_TURNTABLE')
        assert False, 'Should have raised'
    except RuntimeError as e:
        assert 'Camera "CAM_TURNTABLE" not found' in str(e)
