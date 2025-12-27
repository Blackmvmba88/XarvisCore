# Audio 3D Lab — Cubo sobre Piso (STFT)

Visualización 3D en tiempo real de audio: un cubo que avanza sobre un piso (heightmap) modulado por la energía espectral. UI con PyQt6 y backend 3D por defecto pyqtgraph GL. Centralizado y reproducible vía Homebrew + venv.

## Requisitos
- macOS con Homebrew.
- GPU integrada de macOS es suficiente para el backend por defecto.

## Instalación (centralizada, sin desorden)
1. Crear/cambiar a la carpeta:
   ```
   mkdir -p /Users/blackmamba/Projects/audio-3d-lab
   cd /Users/blackmamba/Projects/audio-3d-lab
   ```
2. Instalar dependencias nativas con Brewfile:
   ```
   export HOMEBREW_NO_AUTO_UPDATE=1
   brew bundle --file=Brewfile
   ```
3. Crear entorno virtual e instalar la app:
   ```
   /opt/homebrew/bin/python3 -m venv .venv   # Apple Silicon, en Intel usar /usr/local
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -e .
   ```
4. Dar permisos a scripts (una sola vez):
   ```
   chmod +x scripts/*.sh
   ```

## Uso
- Ejecutar desde terminal:
  ```
  source .venv/bin/activate
  audio3d-cube
  ```
- Controles: Abrir, Abrir carpeta, Generar Onda (sine), Play, Pausa, Stop, Anterior/Siguiente, Seek, Volumen, selector de backend.
- Carpeta por defecto del diálogo: /Users/blackmamba/Downloads.
- Formatos soportados (vía librosa/ffmpeg/audioread): wav, mp3, flac, m4a, ogg, opus, etc.
- Playlist: al abrir una carpeta se construye una lista ordenada por nombre; al terminar una pista, avanza automáticamente (configurable en config/defaults.yaml: auto_advance).
- Generador: en el menú “Generar Onda (sine)” puedes especificar frecuencia (Hz) y duración (s) para probar el visualizador sin archivos.

## Parámetros (CLI)
```
audio3d-cube -h
# Archivo específico
audio3d-cube -f ~/Downloads/tema.wav
# Carpeta (playlist)
audio3d-cube --carpeta ~/Downloads
# Sinusoide (frecuencia y duración)
audio3d-cube --sine --sine-freq 440 --sine-seconds 120
# Seleccionar backend
audio3d-cube --backend pyqtgraph_gl --source-dir ~/Downloads
```

## Configuración
- Archivo: src/audio3d/config/defaults.yaml
- Claves:
  - source_dir: carpeta por defecto para abrir archivos.
  - backend: pyqtgraph_gl | vtk | open3d (opcional).
  - sample_rate: tasa unificada (48 kHz).
  - stft: window_size, hop_size.
  - mesh: freq_bins, time_cols, amplitude_scale.
  - features: log_scale, smoothing.
  - fps_cap: límite de FPS para UI/visual.

## Arquitectura
- audio_io: carga con librosa, reproducción con sounddevice/PortAudio.
- dsp: STFT + features; cola productor/consumidor.
- viz: interface backend-agnóstico; pyqtgraph_gl por defecto.
- UI: PyQt6 QMainWindow con controles mínimos.

## Backends
- pyqtgraph_gl: por defecto, rápido y estable.
- vtk / open3d: opcionales; requieren wheels (pip) y pueden activarse en el menú.

## Notas de compatibilidad
- Se detecta arquitectura al iniciar (ver consola: arm64 o x86_64).
- Usamos venv local y pip wheels; Homebrew sólo provee libs nativas y toolchain.

## Limpieza y centralización
- Todo vive en /Users/blackmamba/Projects/audio-3d-lab.
- Opcional: crear symlink en ~/Programs/audio-3d-lab -> ~/Projects/audio-3d-lab.

## Roadmap
- Implementar backends VTK/Open3D.
- Optimización con Numba/CuPy/Metal (feature flag).
- Packaging como app bundle en macOS.
