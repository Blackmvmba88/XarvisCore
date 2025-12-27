# Afinador Suno (macOS)

Objetivo
- App en Python que:
  - Pre-analiza una canción local (Suno/Descargas), extrae su melodía de referencia (F0 por tiempo) y guarda el análisis.
  - Reproduce la canción y escucha el micrófono en vivo.
  - Muestra una aguja de afinación comparando tu voz con la referencia en cada instante y marca "Afinado" cuando estás dentro de ±25 cents (ajustable).

Estado
- MVP en desarrollo. Esta versión inicial incluye la estructura del proyecto, dependencias y esqueleto funcional para:
  - Catálogo de canciones (lee ~/Music/Suno/index.json y/o ~/Downloads).
  - Decodificación a WAV (ffmpeg) y cacheo.
  - Extractor de F0 offline (torchcrepe) y guardado en JSON.
  - Reproducción de audio (sounddevice) y UI Tkinter con aguja básica.
  - Captura de micrófono (sounddevice) [WIP].
  - Sincronización con offset manual para latencias (p. ej., Bluetooth).

Requisitos
- macOS 12+ (Intel/Apple Silicon)
- Python 3.10+
- Homebrew con ffmpeg y libsndfile:
  - brew install ffmpeg libsndfile

Instalación rápida
1) Crear entorno
   python3 -m venv .venv
   source .venv/bin/activate

2) Instalar dependencias
   pip install -U pip wheel setuptools
   pip install -e .

3) Lanzar UI
   python -m afinador_suno.ui.app

4) Analizar una canción (opcional por CLI)
   afinador-suno analyze --help

Carpetas
- src/afinador_suno: código fuente
- analyses/: resultados de análisis (JSON/CSV)
- cache/: WAV decodificados y stems (Demucs opcional)
- logs/: bitácoras
- scripts/: utilidades de bootstrap/diagnóstico

Notas
- Política "no hay desorden": no duplicamos tu música; sólo cacheamos WAV/stems bajo cache/ usando identificadores por hash. La lista de canciones usa el index.json de Suno si existe y, si no, recurre a ~/Downloads.
- Precisión: para máxima calidad se recomienda separar voz con Demucs antes de extraer F0, pero el MVP puede trabajar sobre el mix completo.
