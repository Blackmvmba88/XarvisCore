import importlib.util
from pathlib import Path
import tempfile
import os

SCHEMA_DIR = Path(__file__).resolve().parents[1] / '20_BLENDER_INTEGRATION' / 'ai_jobs'

spec_spec = importlib.util.spec_from_file_location('ai_specify', SCHEMA_DIR / 'specify.py')
ai_specify = importlib.util.module_from_spec(spec_spec)
spec_spec.loader.exec_module(ai_specify)

spec_runner = importlib.util.spec_from_file_location('ai_runner', SCHEMA_DIR / 'runner.py')
ai_runner = importlib.util.module_from_spec(spec_runner)
spec_runner.loader.exec_module(ai_runner)

spec_schema = importlib.util.spec_from_file_location('ai_schema', SCHEMA_DIR / 'schema.py')
ai_schema = importlib.util.module_from_spec(spec_schema)
spec_schema.loader.exec_module(ai_schema)


def test_prompt_to_spec_and_run(tmp_path):
    prompt = 'A cozy studio with lots of natural light'
    job = ai_specify.prompt_to_spec(prompt)
    ai_schema.validate_job(job)
    runner = ai_runner.SimulatedRunner(str(tmp_path))
    res = runner.run(job)
    assert res['job_name'] == job['name']
    # check that at least one output file was produced
    assert res.get('produced')
    for p in res['produced']:
        if 'path' in p:
            assert os.path.exists(p['path'])
