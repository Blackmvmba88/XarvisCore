# Rule-based synthesizer: maps perception features -> PipelineSpec

def synthesize_pipeline(features: dict) -> dict:
    # Minimal rule-based mapping for MVP
    spec = {}
    style = features.get('style', 'photoreal')
    lighting = features.get('lighting', 'studio')

    spec['engine'] = 'CYCLES' if style == 'photoreal' else 'BLENDER_EEVEE'
    spec['resolution'] = (2048, 2048) if style == 'photoreal' else (1024, 1024)
    spec['samples'] = 128 if style == 'photoreal' else 32
    spec['denoise'] = True if spec['engine'] == 'CYCLES' else False
    spec['hdr_hint'] = True if lighting == 'hdr' else False
    spec['passes'] = ['combined', 'depth', 'normal']
    spec['scheduler_hints'] = {'requires_gpu': spec['engine'] == 'CYCLES', 'estimated_memory_mb': 4000}
    return spec
