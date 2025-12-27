from importlib import import_module

def available_backends():
    # siempre incluir el default; los demás aparecerán aunque sean stubs
    return ["pyqtgraph_gl", "vtk", "open3d"]

def create_scene(backend_name: str, freq_bins=128, time_cols=256):
    if backend_name not in available_backends():
        backend_name = "pyqtgraph_gl"
    if backend_name == "pyqtgraph_gl":
        mod = import_module("audio3d.viz.backends.pyqtgraph_gl")
        return mod.create(freq_bins=freq_bins, time_cols=time_cols)
    elif backend_name == "vtk":
        try:
            mod = import_module("audio3d.viz.backends.vtk_backend")
            return mod.create(freq_bins=freq_bins, time_cols=time_cols)
        except Exception as e:
            print(f"[viz] VTK no disponible: {e}. Usando pyqtgraph_gl.")
            mod = import_module("audio3d.viz.backends.pyqtgraph_gl")
            return mod.create(freq_bins=freq_bins, time_cols=time_cols)
    elif backend_name == "open3d":
        try:
            mod = import_module("audio3d.viz.backends.open3d_backend")
            return mod.create(freq_bins=freq_bins, time_cols=time_cols)
        except Exception as e:
            print(f"[viz] Open3D no disponible: {e}. Usando pyqtgraph_gl.")
            mod = import_module("audio3d.viz.backends.pyqtgraph_gl")
            return mod.create(freq_bins=freq_bins, time_cols=time_cols)
