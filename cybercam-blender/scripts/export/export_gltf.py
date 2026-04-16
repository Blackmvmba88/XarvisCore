"""Exportador GLTF (esqueleto)

Usar desde Blender: `blender --background cybercam_master.blend --python export_gltf.py`
"""
import sys
from pathlib import Path

try:
    import bpy
except Exception:
    print('Este script debe ejecutarse en Blender (bpy).')
    sys.exit(1)

OUT_DIR = Path(__file__).resolve().parents[3] / 'exports' / 'gltf'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def export(path=None):
    filepath = OUT_DIR / (path or 'cybercam_export.glb')
    bpy.ops.export_scene.gltf(filepath=str(filepath), export_format='GLB')
    print('Exportado a', filepath)

if __name__ == '__main__':
    export()
