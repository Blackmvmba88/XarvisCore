# Small script to enable GPU devices for Cycles when run inside Blender
# Usage: blender -b ... --python scripts/dev/enable_cycles_gpu.py

import sys
print('enable_cycles_gpu.py: starting')
try:
    import bpy
    prefs = bpy.context.preferences
    # prefer Metal on macOS, CUDA otherwise (best-effort)
    device_type = None
    try:
        addon = prefs.addons['cycles']
        cycles_prefs = addon.preferences
        # detect available compute types
        avail = getattr(cycles_prefs, 'get_devices', None)
    except Exception:
        cycles_prefs = getattr(prefs, 'cycles', None) or getattr(prefs, 'addon', None)

    # attempt to set compute device type heuristically
    try:
        if sys.platform == 'darwin':
            cycles_prefs.compute_device_type = 'METAL'
            device_type = 'METAL'
        else:
            # try CUDA first then OPTIX
            try:
                cycles_prefs.compute_device_type = 'CUDA'
                device_type = 'CUDA'
            except Exception:
                try:
                    cycles_prefs.compute_device_type = 'OPTIX'
                    device_type = 'OPTIX'
                except Exception:
                    device_type = None
    except Exception:
        device_type = None

    # enable all devices if possible
    enabled = 0
    try:
        devices = getattr(cycles_prefs, 'devices', [])
        for d in devices:
            try:
                d.use = True
                enabled += 1
            except Exception:
                pass
    except Exception:
        pass

    # set scene device to GPU where applicable
    try:
        for scene in bpy.data.scenes:
            try:
                if hasattr(scene, 'cycles'):
                    scene.cycles.device = 'GPU'
            except Exception:
                pass
    except Exception:
        pass

    print(f'enable_cycles_gpu.py: requested device_type={device_type}, enabled devices={enabled}')
except Exception as e:
    print('enable_cycles_gpu.py: failed to configure GPU for Cycles', e)

print('enable_cycles_gpu.py: done')