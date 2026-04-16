import os
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / 'cybercam-blender' / 'scripts' / 'dev' / 'run_mk1.sh'


def make_fake_blender(tmpdir: Path):
    fake = tmpdir / 'fake_blender.sh'
    content = f"""#!/usr/bin/env bash
# fake blender: log its invocation
LOGFILE='{tmpdir}/blender_calls.log'
echo "$0 $@" >> "$LOGFILE"
OUTPUT=""
ARGS=("$@")
for ((i=0;i<${{#ARGS[@]}};i++)); do
  if [[ "${{ARGS[$i]}}" == "--output" ]]; then
    j=$((i+1))
    OUTPUT="${{ARGS[$j]}}"
  fi
done
if [[ -n "$OUTPUT" ]]; then
  mkdir -p "$(dirname "$OUTPUT")"
  touch "$OUTPUT"
  echo "Fake Blender created: $OUTPUT" >> "$LOGFILE"
fi
# print something similar to blender stdout
echo "Fake Blender running: $@"
"""
    fake.write_text(content)
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    return fake, tmpdir / 'blender_calls.log'


def test_run_mk1_calls_blender(tmp_path):
    fake, logfile = make_fake_blender(tmp_path)
    env = os.environ.copy()
    env['BLENDER_BIN'] = str(fake)
    # create dummy master blend so wrapper proceeds
    repo_root = Path(__file__).resolve().parents[1] / 'cybercam-blender'
    master = repo_root / 'blend' / 'cybercam_master.blend'
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text('')
    # Run the wrapper
    proc = subprocess.run([str(WRAPPER)], env=env, capture_output=True, text=True)
    assert proc.returncode == 0, f'Wrapper failed: {proc.stderr}\n{proc.stdout}'
    # Check logfile content contains script names
    content = logfile.read_text()
    assert 'create_parts_template.py' in content or 'create_parts_template.py' in proc.stdout
    assert 'assemble_cam.py' in content or 'assemble_cam.py' in proc.stdout
