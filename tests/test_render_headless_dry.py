import subprocess
import os
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / 'cybercam-blender' / 'scripts' / 'dev' / 'render_headless.sh'


def test_render_headless_dry_composition(tmp_path):
    preset = f"testdry_{tmp_path.name}"

    # create an out dir to exercise timestamping behavior
    out_dir = REPO_ROOT / 'exports' / 'renders' / preset
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'placeholder.txt').write_text('x')

    cmd = [str(SCRIPT), '--preset', preset, '--frames', '2', '--timestamped-output', '--use-gpu', '--log-file', str(tmp_path / 'rh.log')]
    env = os.environ.copy()
    env['BLENDER_BIN'] = 'echo'

    # Run the script (dry-run via BLENDER_BIN=echo). Should exit 0
    res = subprocess.run(cmd, env=env, cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = res.stdout
    assert res.returncode == 0, f"Script failed: {out}"

    # Command composition checks
    assert 'enable_cycles_gpu.py' in out, 'GPU enabler not included in command'
    assert 'assemble_cam.py' in out, 'assemble script not included in command'
    assert '--render-frames 2' in out or '--render-frames 2' in out
    assert '--render-format PNG' in out
    assert 'Logging output to' in out or 'Logging output' in out or 'preview.log' in out or 'rh.log' in out

    # Timestamping: the original out_dir should have been moved to a timestamped name
    parent = REPO_ROOT / 'exports' / 'renders'
    moved = list(parent.glob(f'{preset}-*'))
    assert len(moved) >= 1, f'Expected timestamped dir for {preset}, found: {list(parent.iterdir())}'

    # Cleanup
    for d in moved:
        if d.exists():
            shutil.rmtree(d)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    logf = tmp_path / 'rh.log'
    if logf.exists():
        logf.unlink()
