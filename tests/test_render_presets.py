import importlib.util
from pathlib import Path

MOD_PATH = Path(__file__).resolve().parents[1] / 'cybercam-blender' / 'scripts' / 'utils' / 'render_turntable.py'
spec = importlib.util.spec_from_file_location('render_turntable', str(MOD_PATH))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)


def make_fake_scene():
    import types
    scene = types.SimpleNamespace()
    scene.render = types.SimpleNamespace()
    scene.world = types.SimpleNamespace()
    # cycles/eevee containers
    scene.cycles = types.SimpleNamespace()
    scene.eevee = types.SimpleNamespace()
    scene.view_settings = types.SimpleNamespace()
    return scene


def test_apply_preview_preset_sets_eevee():
    scene = make_fake_scene()
    rt.apply_render_preset(scene, 'preview')
    assert scene.render.engine == 'BLENDER_EEVEE'
    # preview sets eevee samples
    assert hasattr(scene, '_eevee_samples') or hasattr(scene.eevee, 'taa_render_samples')
    assert scene._applied_preset == 'preview'


def test_apply_final_preset_sets_cycles_and_denoise():
    scene = make_fake_scene()
    rt.apply_render_preset(scene, 'final')
    assert scene.render.engine == 'CYCLES'
    # final sets cycles samples and denoise flag
    assert (hasattr(scene, '_cycles_samples') or hasattr(scene.cycles, 'samples'))
    assert (hasattr(scene, '_cycles_denoise') or hasattr(scene.cycles, 'use_denoising'))
    assert scene._applied_preset == 'final'


def test_apply_unknown_preset_raises():
    scene = make_fake_scene()
    import pytest
    with pytest.raises(ValueError):
        rt.apply_render_preset(scene, 'unknown')
