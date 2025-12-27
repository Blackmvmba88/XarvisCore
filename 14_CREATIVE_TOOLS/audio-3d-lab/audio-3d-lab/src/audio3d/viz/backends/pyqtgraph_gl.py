import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QColor

class PyqtgraphGLScene:
    def __init__(self, freq_bins=128, time_cols=256):
        self.freq_bins = int(freq_bins)
        self.time_cols = int(time_cols)

        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor(QColor(10, 10, 10))
        self.view.setCameraPosition(distance=60, elevation=20, azimuth=45)

        g = gl.GLGridItem()
        g.scale(2, 2, 1)
        self.view.addItem(g)

        # Datos Z iniciales
        self.z = np.zeros((self.freq_bins, self.time_cols), dtype=np.float32)
        x = np.linspace(0, self.time_cols-1, self.time_cols)
        y = np.linspace(0, self.freq_bins-1, self.freq_bins)
        self.xgrid, self.ygrid = np.meshgrid(x, y)

        self.surface = gl.GLSurfacePlotItem(x=self.xgrid, y=self.ygrid, z=self.z, shader='shaded', smooth=False)
        self.surface.setGLOptions('opaque')
        self.view.addItem(self.surface)

        # Cubo
        md = gl.MeshData.cube(1, 1, 1)
        self.cube = gl.GLMeshItem(meshdata=md, smooth=False, color=(1.0, 0.3, 0.3, 1.0), shader='shaded')
        self.view.addItem(self.cube)

    def widget(self):
        return self.view

    def show_dummy_heightmap(self):
        # onda estacionaria de ejemplo
        yy = np.linspace(0, np.pi*8, self.freq_bins)[:, None]
        tt = np.linspace(0, np.pi*6, self.time_cols)[None, :]
        self.z = 0.2 * (np.sin(yy) * np.cos(tt)).astype(np.float32)
        self.surface.setData(z=self.z)

    def append_heightmap_column(self, col: np.ndarray):
        # col shape: (freq_bins,)
        if col.shape[0] != self.freq_bins:
            col = np.resize(col, self.freq_bins)
        self.z[:, :-1] = self.z[:, 1:]
        self.z[:, -1] = col
        self.surface.setData(z=self.z)

    def move_cube(self, t_sec: float):
        # mover en +X con el tiempo; mapear t a columna
        x = (t_sec * 30.0) % self.time_cols  # 30 columnas por segundo, p.ej.
        self.cube.resetTransform()
        self.cube.translate(x, self.freq_bins * 0.5, 1.5)

def create(freq_bins=128, time_cols=256):
    return PyqtgraphGLScene(freq_bins=freq_bins, time_cols=time_cols)
