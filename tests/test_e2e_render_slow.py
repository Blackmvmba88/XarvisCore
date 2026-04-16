import os
import subprocess
import sys
import shutil
import time
from pathlib import Path
import pytest

BLENDER_BIN = os.environ.get('BLENDER_BIN')

skip_msg = 'BLENDER_BIN not set or not executable; skip slow E2E Blender test.'


@pytest.mark.slow
@pytest.mark.skipif(not BLENDER_BIN or not Path(BLENDER_BIN).is_file() or not os.access(BLENDER_BIN, os.X_OK), reason=skip_msg)
def test_assemble_and_render_e2e(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    # ensure parts template is generated
    parts_script = repo_root / 'cybercam-blender' / 'blend' / 'create_parts_template.py'
    parts_out = repo_root / 'cybercam-blender' / 'blend' / 'cybercam_parts.blend'
    proc = subprocess.run([BLENDER_BIN, '--background', '--python', str(parts_script), '--', '--output', str(parts_out)], capture_output=True, text=True)
    assert proc.returncode == 0, f'create_parts_template failed: {proc.stderr}\n{proc.stdout}'
    assert parts_out.exists()

    # create master blend with anchors using a small temp script executed by Blender
    master_script = tmp_path / 'create_master.py'
    master_path = repo_root / 'cybercam-blender' / 'blend' / 'cybercam_master.blend'
    master_script.write_text(f"""
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
anchors = ['ANCHOR_body','ANCHOR_lens','ANCHOR_mount','ANCHOR_base','ANCHOR_cable_01','ANCHOR_cable_02','ANCHOR_cable_03','ANCHOR_screw_array_01']
for a in anchors:
    o = bpy.data.objects.new(a, None)
    o.empty_display_type = 'ARROWS'
    bpy.context.scene.collection.objects.link(o)

bpy.ops.wm.save_as_mainfile(filepath=r'{master_path}')
print('Saved master', r'{master_path}')
""")
    proc = subprocess.run([BLENDER_BIN, '--background', '--python', str(master_script)], capture_output=True, text=True)
    assert proc.returncode == 0, f'create_master failed: {proc.stderr}\n{proc.stdout}'
    assert master_path.exists()

    # run assemble with render: small frames
    preset = f'mk1_e2e_{int(time.time())}'
    assemble_script = repo_root / 'cybercam-blender' / 'scripts' / 'build' / 'assemble_cam.py'
    cmd = [BLENDER_BIN, '-b', str(master_path), '--python', str(assemble_script), '--', '--preset', preset, '--screws', '4', '--cables', '1', '--render', '--render-frames', '4', '--render-width', '64', '--render-height', '64', '--render-format', 'PNG']
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, f'assemble_cam failed: {proc.stderr}\n{proc.stdout}'

    renders_dir = repo_root / 'exports' / 'renders' / preset
    assert renders_dir.exists(), f'renders dir missing: {renders_dir}'

    pngs = list(renders_dir.glob('*.png'))
    assert len(pngs) >= 1, 'No PNGs generated'

    # check png signature and non-zero size
    sig = b'\x89PNG\r\n\x1a\n'
    for p in pngs:
        s = p.stat().st_size
        assert s > 0, f'Empty PNG: {p}'
        with open(p, 'rb') as fh:
            header = fh.read(len(sig))
            assert header == sig, f'Not a PNG: {p}'

    # cleanup generated files to keep repo tidy
    try:
        parts_out.unlink()
    except Exception:
        pass
    try:
        master_path.unlink()
    except Exception:
        pass
    shutil.rmtree(renders_dir)
