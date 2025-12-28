# 🎵 BlackMamba Music Collection - WebUI

Sistema completo de gestión y reproducción de tu colección musical.

## 🚀 Quick Start

### Ver tu colección (WebUI)
```bash
bash launch_music_webui.sh
```

O directamente:
```bash
open music_webui.html
```

### Generar Playlists (M3U/M3U8/PLS)
```bash
python3 generate_playlists.py
```

Esto genera playlists compatibles con:
- **VLC Media Player**
- **iTunes/Apple Music**  
- **Winamp**
- **foobar2000**
- Cualquier reproductor estándar

**Playlists generadas:**
- `BlackMamba_ALL.m3u8` - Todas las canciones (194)
- `BlackMamba_SOUNDCLOUD.m3u8` - Solo SoundCloud
- `BlackMamba_SUNO.m3u8` - Solo Suno
- `BlackMamba_LOCAL.m3u8` - Solo local
- `BlackMamba_MP3_ONLY.m3u8` - Solo MP3
- `BlackMamba_WAV_ONLY.m3u8` - Solo WAV

### Organizar canciones en carpeta única

**Paso 1: Modo Prueba (DRY RUN)**
```bash
python3 organize_music.py
```
Esto mostrará lo que haría sin mover archivos.

**Paso 2: Ejecutar Organización**
Edita `organize_music.py` y cambia:
```python
DRY_RUN = False  # Cambiar a False para ejecutar
```

Luego ejecuta:
```bash
python3 organize_music.py
```

## 📊 Características de la WebUI

### 🎯 Visualización
- **Grid responsive** con todas tus canciones
- **Búsqueda en tiempo real** por título o artista
- **Filtros por formato**: Todas, Solo MP3, Solo WAV, Completas (MP3+WAV)
- **Filtros por origen**: 🔊 SoundCloud, 🎵 Suno, 💿 Local
- **Estadísticas** en tiempo real (total canciones, MP3, WAV, por origen)
- **Badges visuales** que muestran origen y formato de cada canción

### 🎵 Reproductor Integrado
- **Player estilo Spotify** en la barra inferior
- **Controles**: Play/Pause, Siguiente, Anterior
- **Barra de progreso** interactiva
- **Control de volumen**
- **Auto-reproducción** de siguiente canción

### 🎨 Estética
- **Tema Matrix/Cyberpunk** (verde neón #00ff41)
- **Glassmorphism** con blur effects
- **Animaciones suaves**
- *🎼 Playlists Exportables

### Formatos Soportados

**M3U (Simple)**
```
/Users/blackmamba/Downloads/cancion1.mp3
/Users/blackmamba/Downloads/cancion2.mp3
```

**M3U8 (Extended con metadata)**
```
#EXTM3U
#EXTINF:-1,BlackMamba - Título de Canción
/Users/blackmamba/Downloads/cancion1.mp3
```

**PLS (Winamp/foobar2000)**
```
[playlist]
File1=/Users/blackmamba/Downloads/cancion1.mp3
Title1=BlackMamba - Título de Canción
```

### Uso de Playlists

**En VLC:**
```bash
open -a VLC playlists/BlackMamba_ALL.m3u8
```

**En iTunes/Music:**
```bash
open -a Music playlists/BlackMamba_ALL.m3u8
```

**Importar a cualquier reproductor:**
Abre el archivo `.m3u8` o `.pls` desde tu reproductor favorito.

## *Responsive** para móvil y desktop

## 📁 Organización de Archivos

### Antes (Disperso)
```
/Users/blackmamba/Downloads/cancion1.mp3
/Users/blackmamba/Desktop/cancion2.mp3
/Users/blackmamba/Music/cancion3.wav
...
```

### Después (Unificado)
```
10_CULTURAL_RENAISSANCE/
└── BlackMamba_Music_Collection/
    ├── Canción 1 - BlackMamba.mp3
    ├── Canción 2 - BlackMamba.mp3
    ├── Canción 3 - BlackMamba.wav
    └── ...
```

## 🛠️ Funcionalidades del Organizador

### `organize_music.py`
- ✅ **Copia** (no mueve) canciones a carpeta única
- ✅ **Nombres limpios**: "Título - Artista.mp3"
- ✅ **Evita duplicados**: No sobreescribe archivos existentes
- ✅ **Estadísticas**: Reporte de copiadas/omitidas/errores
- ✅ **Actualiza rutas**: Opción para actualizar `music_library.json`
- ✅ **Modo DRY RUN**: Prueba sin riesgo

### Estadísticas que genera
- ✅ Archivos copiados
- ⏭️ Archivos omitidos (ya existen)
- ⚠️ Archivos no encontrados
- ❌ Errores durante copia

## 📝 Uso Recomendado

### 1. Ver tu colección
```bash
bash launch_music_webui.sh
```

### 2. Organizar archivos (primera vez)
```bash
# Modo prueba
python3 organize_music.py

# Verificar que todo está bien

# Ejecutar (cambiar DRY_RUN = False)
python3 organize_music.py

# Actualizar rutas en biblioteca
# El script preguntará si quieres hacerlo
```

### 3. Disfrutar tu música
La WebUI leerá automáticamente de `music_library.json` que ahora tendrá las rutas actualizadas.

## 🎨 Personalización

### Cambiar carpeta destino
Edita en `organize_music.py`:
```python
UNIFIED_FOLDER = Path(__file__).parent / "MI_CARPETA_PERSONALIZADA"
```

### Cambiar colores de WebUI
Edita en `music_webui.html`:
```css
:root {
    --primary: #00ff41;  /* Verde Matrix */
    --purple: #8B5CF6;   /* Púrpura */
    --bg: #0a0a0a;       /* Fondo */
}
```

## 🔊 Compatibilidad

- **Navegadores**: Chrome, Firefox, Safari, Edge
- **Formatos**: MP3, WAV
- **Sistema**: macOS, Linux, Windows (con ajustes menores)

## 📊 Tu Biblioteca Actual

Según `music_library.json`:
- **Total canciones**: 194+
- **Ubicaciones**: Downloads, Desktop, Music, etc.
- **Formatos**: MP3 y WAV

## 🦅 Filosofía BlackMamba

> "Cada canción es un sistema de arquitectura emocional. No buscamos canciones que se consuman rápido, buscamos sistemas que sigan respirando cuando el eco se apaga."

---

**Arquitecto**: Iyari Cancino Gomez  
**Dominio**: 10_CULTURAL_RENAISSANCE  
**Catálogo**: https://soundcloud.com/iyari-c/tracks (280+ producciones)
