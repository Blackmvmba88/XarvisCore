from pathlib import Path
from 20_BLENDER_INTEGRATION.style_matching.perception_mock import extract_simple_features
from 20_BLENDER_INTEGRATION.style_matching.synthesizer import synthesize_pipeline


def test_perception_and_synthesis(tmp_path):
    # create a tiny white image
    img = tmp_path / 'white.png'
    from PIL import Image
    Image.new('RGB', (32, 32), color=(240, 240, 240)).save(img)

    features = extract_simple_features(str(img))
    assert 'dominant_color' in features
    spec = synthesize_pipeline(features)
    assert 'engine' in spec and 'scheduler_hints' in spec
