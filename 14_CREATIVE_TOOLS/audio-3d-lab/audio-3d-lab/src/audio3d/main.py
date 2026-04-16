import sys
import argparse
from importlib.resources import files
from pathlib import Path
import yaml

from PyQt6.QtWidgets import QApplication

from audio3d.ui.app import AppWindow
from audio3d.utils.arch import detect_arch
from audio3d.utils.paths import expand_user

def load_defaults():
    cfg_res = files("audio3d.config") / "defaults.yaml"
    with cfg_res.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    defaults = load_defaults()
    arch = detect_arch()
    print(f"[audio3d] Arquitectura detectada: {arch}")

    parser = argparse.ArgumentParser(
        prog="audio3d-cube",
        description="Visualización 3D de audio (cubo que avanza sobre un piso heightmap)."
    )
    parser.add_argument("-f", "--archivo", type=str, default=None,
                        help="Ruta de archivo de audio a reproducir (por defecto se abrirá un diálogo).")
    parser.add_argument("--carpeta", type=str, default=None,
                        help="Carpeta para construir una playlist de canciones.")
    parser.add_argument("--sine", action="store_true",
                        help="En lugar de archivo/carpeta, generar una onda sinusoidal.")
    parser.add_argument("--sine-freq", type=float, default=float(defaults.get("generator", {}).get("sine_freq", 440.0)),
                        help="Frecuencia de la sinusoide (Hz).")
    parser.add_argument("--sine-seconds", type=float, default=float(defaults.get("generator", {}).get("sine_seconds", 60.0)),
                        help="Duración de la sinusoide (segundos).")
    parser.add_argument("--backend", type=str, default=None,
                        choices=["pyqtgraph_gl", "vtk", "open3d"],
                        help="Backend de visualización 3D (por defecto: pyqtgraph_gl).")
    parser.add_argument("--source-dir", type=str, default=defaults.get("source_dir", str(Path.home() / "Downloads")),
                        help="Carpeta por defecto para abrir archivos (por defecto: ~/Downloads).")

    args = parser.parse_args()

    # Preparar configuración efectiva
    cfg = defaults.copy()
    if args.backend:
        cfg["backend"] = args.backend
    if args.source_dir:
        cfg["source_dir"] = expand_user(args.source_dir)

    initial_dir = args.carpeta
    sine_opts = None
    if args.sine:
        sine_opts = {"freq": args.sine_freq, "seconds": args.sine_seconds}
        # Ignorar archivo/carpeta si se pide sinusoide
        initial_dir = None
        args.archivo = None

    app = QApplication(sys.argv)
    win = AppWindow(config=cfg, initial_file=args.archivo, initial_dir=initial_dir, sine=sine_opts)
    win.show()
    sys.exit(app.exec())
