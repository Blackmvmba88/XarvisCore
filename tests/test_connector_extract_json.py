import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / '20_BLENDER_INTEGRATION' / 'connector.py'

spec = importlib.util.spec_from_file_location('blender_connector', str(MODULE_PATH))
conn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conn)


def test_extract_json_simple():
    text = 'some logs\n{"objects": [{"name": "part_body_basic"}], "blend_file": ""}\nother logs'
    parsed = conn._extract_json_from_text(text)
    assert parsed is not None
    assert 'objects' in parsed
    assert parsed['objects'][0]['name'] == 'part_body_basic'
