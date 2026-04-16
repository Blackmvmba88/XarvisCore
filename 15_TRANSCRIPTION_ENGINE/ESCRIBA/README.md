# ESCRIBA

ESCRIBA es una plataforma local de _speech-to-text_ pensada para convertirse en un "escritor inteligente" que registra y organiza todo lo que escucha. Trabaja con audio del micrófono, archivos y pistas ocultas de video, y ofrece una capa de inteligencia que limpia, puntúa y clasifica el texto antes de guardarlo de forma íntegra.

## 🌍 Características Principales

### ✅ Reconocimiento Multi-Idioma
- **Detección automática de idiomas**: Reconoce y transcribe en más de 99 idiomas
- **Adaptación inteligente**: Se adapta automáticamente al idioma detectado
- **Alta precisión**: Utiliza modelos Whisper de OpenAI con validación dual de detección

### 🏷️ Clasificación Inteligente
- **Categorización automática**: Clasifica el contenido (técnico, negocios, educativo, etc.)
- **Extracción de palabras clave**: Identifica términos importantes automáticamente
- **Etiquetado contextual**: Genera etiquetas relevantes basadas en el contenido
- **Análisis de sentimiento**: Detecta tono positivo, negativo o neutral

### 🔄 Adaptación al Sistema
- **100% local**: No requiere conexión a internet
- **Multi-plataforma**: Compatible con macOS, Linux y Windows
- **Modelos escalables**: Desde tiny (rápido) hasta large (alta precisión)
- **Almacenamiento inteligente**: Base de datos SQLite con búsqueda y filtros

## Objetivos principales

- **Captura híbrida**: escuchar el micrófono en tiempo real y procesar archivos/audio extraído de video en paralelo.
- **Transcripción local**: utilizar modelos como `faster-whisper` para mantener los datos en el dispositivo.
- **Escritura inteligente**: aplicar limpieza, puntuación contextual, etiquetas temáticas y preparación de formatos (`.md`, `.srt`, `.json`).
- **Persistencia total**: almacenar tanto el texto crudo como las versiones refinadas en archivos y en SQLite para futuras consultas.
- **Interfaces sincronizadas**: ofrecer una TUI en terminal y una WebUI local que reflejen la misma sesión y permitan edición ligera.

## Arquitectura de alto nivel

```
[captura] -> [transcripción] -> [escritor inteligente] -> [almacenamiento] -> [UIs]
     ^              ^                    ^                      ^            ^
  mic/file     faster-whisper     Limpieza + IA         SQLite + Markdown   TUI/Web
```

- **CaptureService**: `sounddevice` para micrófono y `ffmpeg-python` para extraer/normalizar audio de archivos o video.
- **TranscriberService**: `faster-whisper` (modelos tiny→large) trabajando en colas priorizadas.
- **WriterService**: pipeline de posprocesado (regex/spaCy) con opción de reescritura ligera para estilo.
- **StorageService**: archivos de sesión (`sessions/<fecha>/<canal>.md`) + base SQLite (`transcripts.db`).
- **Interfaces**: TUI con Rich/Textual y WebUI (FastAPI + HTMX/Tailwind) sincronizadas vía eventos/WebSockets.

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Blackmvmba88/ESCRIBA.git
cd ESCRIBA

# Instalar el paquete
pip install -e .

# Instalar dependencias de desarrollo (opcional)
pip install -e ".[dev]"
```

## Uso Rápido

```python
import asyncio
from escriba import create_escriba

async def main():
    # Crear instancia de ESCRIBA
    escriba = create_escriba(model_size="small")
    
    # Procesar archivo de audio - detecta el idioma automáticamente
    result = await escriba.process_audio_file('audio.wav')
    
    print(f"Idioma detectado: {result['language']}")
    print(f"Categoría: {result['category']}")
    print(f"Transcripción: {result['full_text']}")
    
    # Exportar a Markdown
    escriba.export_session()

asyncio.run(main())
```

### Ejemplos de Idiomas Soportados

ESCRIBA reconoce automáticamente y transcribe en más de 99 idiomas, incluyendo:

- 🇪🇸 **Español**: "Hola, ¿cómo estás?" → Detectado y transcrito
- 🇺🇸 **Inglés**: "Hello, how are you?" → Detectado y transcrito
- 🇫🇷 **Francés**: "Bonjour, comment allez-vous?" → Detectado y transcrito
- 🇩🇪 **Alemán**: "Hallo, wie geht es dir?" → Detectado y transcrito
- 🇯🇵 **Japonés**: "こんにちは、お元気ですか？" → Detectado y transcrito
- 🇨🇳 **Chino**: "你好，你好吗？" → Detectado y transcrito
- Y muchos más...

## Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=escriba

# Ver ejemplo de uso
python examples/demo.py
```

## Requisitos iniciales

- macOS / Linux con Python 3.11+
- `ffmpeg` disponible en el PATH (opcional, para procesamiento de video)
- Dependencias principales se instalan automáticamente con pip

## Estructura del Proyecto

```
ESCRIBA/
├── README.md
├── pyproject.toml
├── docs/
│   └── ROADMAP.md
├── src/
│   └── escriba/
│       ├── __init__.py
│       ├── core.py                    # Integración principal
│       ├── transcribe/
│       │   ├── language_detector.py   # Detección multi-idioma
│       │   └── service.py             # Servicio de transcripción
│       ├── writer/
│       │   └── classifier.py          # Clasificación inteligente
│       ├── storage/
│       │   ├── models.py              # Modelos de datos
│       │   └── service.py             # Persistencia
│       ├── capture/
│       └── ui/
├── examples/
│   ├── demo.py
│   └── README.md
└── tests/
    ├── test_language_detection.py
    ├── test_classification.py
    └── test_storage.py
```

## Roadmap

Consulta `docs/ROADMAP.md` para ver el plan detallado de hitos y tareas.

## Próximos pasos

1. Inicializar entorno Python (por ejemplo con `uv` o `poetry`).
2. Implementar `CaptureService` para micrófono y normalización de archivos.
3. Integrar `faster-whisper` en un servicio asincrónico con colas.
4. Construir la capa de escritura inteligente y persistencia dual.
5. Desarrollar las interfaces TUI y WebUI sincronizadas.
