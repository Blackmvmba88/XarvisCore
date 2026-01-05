import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(path, args=None):
    cmd = [sys.executable, str(path)]
    if args:
        cmd += args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc


def test_create_parts_template_requires_bpy():
    script = ROOT / 'cybercam-blender' / 'blend' / 'create_parts_template.py'
    proc = run_script(script)
    assert proc.returncode != 0
    assert 'bpy' in (proc.stderr + proc.stdout).lower() or 'must be run inside blender' in (proc.stderr + proc.stdout).lower()


def test_assemble_requires_bpy():
    script = ROOT / 'cybercam-blender' / 'scripts' / 'build' / 'assemble_cam.py'
    proc = run_script(script, args=['--preset=mk1'])
    assert proc.returncode != 0
    assert 'bpy' in (proc.stderr + proc.stdout).lower() or 'este script debe ejecutarse' in (proc.stderr + proc.stdout).lower()
