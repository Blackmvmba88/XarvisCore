# Minimal perception mock for Style Matching Mode
# Input: image path (string)
# Output: dict of features: { 'dominant_color': '#rrggbb', 'roughness': 'high|medium|low', 'lighting': 'hdr|studio|ambient', 'style': 'photoreal|stylized' }

from PIL import Image


def extract_simple_features(image_path: str) -> dict:
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception:
        return {}
    # compute very simple dominant color by downsampling
    small = img.resize((16, 16))
    pixels = list(small.getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    dominant = '#%02x%02x%02x' % (r, g, b)
    # naive heuristics for roughness and lighting
    avg_lum = (r + g + b) / 3
    roughness = 'low' if avg_lum > 180 else ('medium' if avg_lum > 80 else 'high')
    lighting = 'hdr' if avg_lum > 200 else ('studio' if avg_lum > 100 else 'ambient')
    style = 'photoreal' if avg_lum > 50 else 'stylized'
    return {'dominant_color': dominant, 'roughness': roughness, 'lighting': lighting, 'style': style}
