# Device enumeration utilities (skeleton)
# Returns a mapping backend -> list of devices. Safe to call when `bpy` is not available.

from typing import Dict, List


def _safe_getattr(obj, name, default=None):
    try:
        return getattr(obj, name)
    except Exception:
        return default


def detect_devices() -> Dict[str, List[str]]:
    """Return a dict with available compute backends and devices.

    Safe to call without Blender (returns empty dict).
    When run inside Blender, will attempt to read Cycles preferences and list devices.
    """
    try:
        import bpy  # type: ignore
    except Exception:
        return {}

    res = {}
    try:
        prefs = _safe_getattr(bpy.context, 'preferences', None)
        cycles = None
        if prefs is not None:
            cycles = _safe_getattr(prefs, 'cycles', None) or _safe_getattr(prefs, 'addon', None)

        device_type = None
        devices = []
        if cycles is not None:
            device_type = _safe_getattr(cycles, 'compute_device_type', None)
            devs = _safe_getattr(cycles, 'devices', []) or []
            for d in devs:
                name = _safe_getattr(d, 'name', None) or str(d)
                devices.append(name)

        if device_type:
            res[device_type] = devices
        else:
            # If no explicit compute_device_type, try to infer available backends
            if devices:
                res['UNKNOWN'] = devices
    except Exception:
        return {}

    return res
