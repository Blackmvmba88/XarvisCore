import importlib.util
from pathlib import Path
import tempfile
import os

SCHEMA_DIR = Path(__file__).resolve().parents[1] / '20_BLENDER_INTEGRATION' / 'ai_jobs'

spec = importlib.util.spec_from_file_location('ai_runner', SCHEMA_DIR / 'runner.py')
ai_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_runner)

spec2 = importlib.util.spec_from_file_location('ai_schema', SCHEMA_DIR / 'schema.py')
ai_schema = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(ai_schema)


def test_runner_generates_files(tmp_path):
    runner = ai_runner.SimulatedRunner(str(tmp_path))
    job = {"name": "t", "steps": [{"type": "generate_model", "model_name": "m1"}, {"type": "render_still", "output": "out/still.png"}, {"type": "export", "format": "GLTF", "output_path": "out/out.gltf"}]}
    ai_schema.validate_job(job)
    res = runner.run(job)
    assert isinstance(res, dict)
    produced = res.get('produced', [])
    assert any(p['type'] == 'generate_model' for p in produced)
    assert any(p['type'] == 'render_still' for p in produced)
    assert any(p['type'] == 'export' for p in produced)
    # files exist
    for p in produced:
        if 'path' in p:
            assert os.path.exists(p['path'])
