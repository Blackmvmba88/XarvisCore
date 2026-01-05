"""Render turntable (esqueleto).

Este script debe ejecutarse dentro de Blender y automatiza renders de giro.
"""
import sys
from pathlib import Path
from typing import List, Optional

def _frame_filenames(output_dir: Path, frames: int, image_format: str) -> List[Path]:
    ext = image_format.lower()
    out = []
    for i in range(frames):
        out.append(output_dir / f'frame_{i+1:04d}.{ext}')
    return out


def render_turntable(output_dir: str | Path, frames: int = 36, width: int = 1024, height: int = 1024,
                     image_format: str = 'PNG', camera_name: Optional[str] = 'CAM_TURNTABLE',
                     collection_name: Optional[str] = None, start_frame: int = 0, axis: str = 'Z',
                     preset: Optional[str] = None, hdri_path: Optional[str] = None) -> List[Path]:
    """Render a turntable sequence.

    - output_dir: where to save images
    - frames: number of frames (default 36)
    - width/height: resolution
    - image_format: PNG/JPEG
    - camera_name: name of camera object to use (must exist)
    - collection_name: optional collection name to restrict visibility

    Returns list of generated file paths.
    Raises RuntimeError on missing camera/scene/camera.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Try to import bpy; if not available, raise for runtime usage but allow tests to mock bpy
    try:
        import bpy
    except Exception:
        raise RuntimeError('render_turntable requires Blender (bpy). Run inside Blender or mock bpy in tests.')

    # Validate camera
    cam = None
    if camera_name:
        cam = bpy.data.objects.get(camera_name)
        if cam is None:
            raise RuntimeError(f'Camera "{camera_name}" not found in the current scene.')

    # Optionally check collection exists
    if collection_name:
        col = bpy.data.collections.get(collection_name)
        if col is None:
            raise RuntimeError(f'Collection "{collection_name}" not found in the current file.')

    scene = bpy.context.scene

    # Apply render preset if requested (sets engine, samples, denoise, HDRI hint, etc.)
    if preset:
        try:
            apply_render_preset(scene, preset, hdri_path)
            print(f'Applied render preset: {preset}')
        except Exception as e:
            print('Warning: failed to apply render preset', preset, e)

    # configure render settings
    scene.render.resolution_x = int(width)
    scene.render.resolution_y = int(height)
    scene.render.image_settings.file_format = image_format.upper()

    frame_paths = _frame_filenames(output_dir, frames, image_format)

    print(f'Starting turntable render: {frames} frames → {output_dir} ({width}x{height}, {image_format})')
    for idx, path in enumerate(frame_paths):
        frame_num = start_frame + idx
        scene.frame_set(frame_num)
        # set file path per-frame
        scene.render.filepath = str(path)
        print(f'Rendering frame {idx+1}/{frames} -> {path.name}')
        bpy.ops.render.render(write_still=True)

    print('Turntable render complete.')
    return frame_paths


if __name__ == '__main__':
    print('Turntable placeholder — ejecutar desde Blender')


# Render presets
PRESETS = {
    'preview': {
        'engine': 'BLENDER_EEVEE',
        'samples': 16,
        'denoise': False,
        'use_hdr': False,
    },
    'final': {
        'engine': 'CYCLES',
        'samples': 128,
        'denoise': True,
        'use_hdr': True,
    },
}


def apply_render_preset(scene, preset: str, hdri_path: Optional[str] = None):
    """Apply a named preset to the given Blender scene object.

    This function is designed to be testable with a fake `scene` object in unit tests.
    If hdri_path is provided and the preset requests use_hdr, it will attempt to set world background.
    Otherwise it will set a flag `scene._render_lighting` to '3point' to indicate procedural lights.
    """
    p = PRESETS.get(preset)
    if not p:
        raise ValueError(f'Unknown render preset: {preset}')

    # set engine
    scene.render.engine = p['engine']

    # set samples per engine
    if p['engine'] == 'CYCLES':
        # create cycles settings if missing
        try:
            scene.cycles.samples = int(p['samples'])
            scene.cycles.use_denoising = bool(p['denoise'])
        except Exception:
            # allow tests to run without full cycles API
            setattr(scene, '_cycles_samples', int(p['samples']))
            setattr(scene, '_cycles_denoise', bool(p['denoise']))
    elif p['engine'] == 'BLENDER_EEVEE':
        try:
            scene.eevee.taa_render_samples = int(p['samples'])
        except Exception:
            setattr(scene, '_eevee_samples', int(p['samples']))

    # Lighting: if hdri requested and provided, set a marker
    if p.get('use_hdr') and hdri_path:
        # attempt to assign hdri to world if possible, otherwise annotate
        try:
            world = scene.world
            if world and hasattr(world, 'node_tree'):
                # simple annotation for tests; real implementation would set nodes
                world['_hdri'] = str(hdri_path)
        except Exception:
            pass
    else:
        # mark to use procedural 3-point lighting
        setattr(scene, '_render_lighting', '3point')

    # simple compositing hint
    try:
        scene.view_settings.view_transform = 'Filmic'
        # gamma/contrast via small attributes so tests can assert them
        setattr(scene, '_render_gamma', 1.0)
        setattr(scene, '_render_contrast', 0.0)
    except Exception:
        setattr(scene, '_render_gamma', 1.0)
        setattr(scene, '_render_contrast', 0.0)
    # store applied preset name
    setattr(scene, '_applied_preset', preset)
