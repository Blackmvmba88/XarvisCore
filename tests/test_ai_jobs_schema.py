import importlib.util
from pathlib import Path
import pytest

SCHEMA_PATH = Path(__file__).resolve().parents[1] / '20_BLENDER_INTEGRATION' / 'ai_jobs' / 'schema.py'

spec = importlib.util.spec_from_file_location('ai_schema', SCHEMA_PATH)
ai_schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_schema)


def test_validate_ok_job():
    job = {"name": "t", "steps": [{"type": "generate_model", "model_name": "m1"}, {"type": "render_still"}]}
    # should not raise
    ai_schema.validate_job(job)


def test_validate_missing_fields():
    job = {"steps": []}
    with pytest.raises(ai_schema.JobValidationError):
        ai_schema.validate_job(job)
