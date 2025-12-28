# 🎵 BlackMamba Music Management Suite

**Arquitecto**: Iyari Cancino Gomez  
**Dominio**: 10_CULTURAL_RENAISSANCE  
**Colección**: 194 canciones | 1.46 GB | BlackMamba RECORDS

---

## 📚 Herramientas Disponibles

### 🌐 1. Music WebUI (Interfaz Web)
**Archivo**: `music_webui.html`  
**Launcher**: `./launch_music_webui.sh`

**Características**:
- Reproductor integrado con controles completos
- Búsqueda en tiempo real por título/artista
- Filtros: Por formato (MP3/WAV/Complete), Por origen (SoundCloud/Suno/Local)
- Vista en grid con 6 estadísticas principales
- Diseño Matrix/Cyberpunk (#00ff41 green)

**Uso**:
```bash
./launch_music_webui.sh
# o
open music_webui.html
```

---

### 📀 2. Generador de Playlists Básicas
**Archivo**: `generate_playlists.py`

**Genera** (11 playlists):
- `BlackMamba_ALL.{m3u,m3u8,pls}` - Toda la colección
- `BlackMamba_SUNO.{m3u,m3u8,pls}` - Solo producciones Suno
- `BlackMamba_LOCAL.{m3u,m3u8,pls}` - Solo música local
- `BlackMamba_MP3_ONLY.m3u8` - Solo archivos MP3
- `BlackMamba_WAV_ONLY.m3u8` - Solo archivos WAV

**Formatos**:
- **M3U**: Simple, compatible con VLC/Winamp
- **M3U8**: Extended con metadata (#EXTINF)
- **PLS**: Formato Winamp con índices

**Uso**:
```bash
python3 generate_playlists.py
# Playlists en: playlists/
```

---

### 🎲 3. Generador de Playlists Avanzadas
**Archivo**: `generate_advanced_playlists.py`

**Genera** (13+ playlists):
- **Shuffle**: ALL (194), RANDOM_50, MINI_MIX (20)
- **Por año**: 2025, 2024, etc.
- **Por tamaño**: HEAVIEST_30, LIGHTEST_30
- **Temáticas**: WORKOUT, CHILL, FOCUS
- **Alfabéticas**: A-Z por título/artista
- **Exportación**: .txt para Spotify/Apple Music

**Uso**:
```bash
python3 generate_advanced_playlists.py
# Playlists en: playlists/
```

---

### 📋 4. Analizador de Origen
**Archivo**: `analyze_music_sources.py`

**Detecta**:
- 🔊 **SoundCloud**: Patrón "soundcloud" o "sc-" en nombre
- 🎵 **Suno**: Tags "(Intro)" "(Verse)" "(Chorus)" en título
- 💿 **Local**: Todo lo que no coincida con anteriores

**Uso**:
```bash
python3 analyze_music_sources.py
# Genera: music_sources_report.json
```

---

### 📊 5. Estadísticas Detalladas
**Archivo**: `music_statistics.py`

**Métricas**:
- Almacenamiento total y promedio
- Breakdown por artista (100% BlackMamba)
- Distribución por ubicación (Downloads)
- Análisis por año (2025)
- Tiers de calidad (Complete/MP3-only/WAV-only)
- Curiosidades (más larga/corta, duplicados)

**Uso**:
```bash
python3 music_statistics.py
# Genera: music_statistics_report.json
```

---

### 📁 6. Organizador de Música
**Archivo**: `organize_music.py`

**Función**:
- Copia todas las canciones a `BlackMamba_Music_Collection/`
- Renombra: `"Título - Artista.ext"`
- Actualiza `music_library.json` con nuevas rutas
- **Modo seguro**: `DRY_RUN = True` por defecto (simula sin copiar)

**Uso**:
```bash
# Modo simulación (recomendado primero)
python3 organize_music.py

# Ejecutar real (edita DRY_RUN = False en el archivo)
python3 organize_music.py
```

---

### 🛡️ 7. Gestor de Backups
**Archivo**: `music_backup_manager.py`

**Características**:
- Backup completo con timestamp
- Cálculo de hash SHA256 para integridad
- Verificación de archivos corruptos
- Lista de backups históricos
- Metadata automática (tamaño, fecha, errores)

**Uso**:
```bash
python3 music_backup_manager.py
# Menú interactivo:
#   1) Crear backup nuevo
#   2) Verificar integridad
#   3) Listar backups
```

**Backups en**: `music_backups/backup_YYYYMMDD_HHMMSS/`

---

### 🎧 8. Analizador de Calidad
**Archivo**: `music_quality_analyzer.py`

**Requiere**: `brew install ffmpeg` (para ffprobe)

**Analiza**:
- **Bitrate**: kbps por canción
- **Sample Rate**: kHz (44.1, 48, etc.)
- **Códecs**: MP3, WAV, AAC, FLAC
- **Duración**: Total, promedio, min/max
- **Tiers**: Alta (≥320kbps), Media (192-319), Baja (128-191), Pobre (<128)

**Uso**:
```bash
python3 music_quality_analyzer.py
# Genera: music_quality_report.json
```

**Output ejemplo**:
```
✅ 194 archivos analizados
⏱️ Duración total: 8h 45m

🎵 BITRATE:
   320 kbps: 150 canciones (77.3%)
   192 kbps: 30 canciones (15.5%)
   128 kbps: 14 canciones (7.2%)

🏆 TIERS:
   🥇 Alta (≥320 kbps): 150 canciones
   🥈 Media (192-319 kbps): 30 canciones
   🥉 Baja (128-191 kbps): 14 canciones
```

---

### 🔍 9. Buscador de Duplicados
**Archivo**: `music_duplicate_finder.py`

**Detecta**:
1. **Títulos idénticos**: Normaliza y compara exactamente
2. **Títulos similares**: ≥90% similitud (typos, variaciones)
3. **Archivos idénticos**: Compara hash SHA256 completo

**Uso**:
```bash
python3 music_duplicate_finder.py
# Genera: music_duplicates_report.json
```

**Output ejemplo**:
```
📊 RESUMEN:
   🔴 Títulos idénticos: 5 grupos
   🟡 Títulos similares: 12 pares
   🔵 Archivos idénticos: 2 grupos
   
💡 RECOMENDACIONES:
   🔴 Revisar títulos idénticos (versiones diferentes)
   🟡 Verificar similares (errores de tipeo)
   🔵 Eliminar archivos idénticos (espacio innecesario)
```

---

### 🎛️ 10. Music Manager (Menú Unificado)
**Archivo**: `music_manager.sh`

**Menú interactivo**:
```
1) 🌐 Ver WebUI (navegador)
2) 🎼 Generar Playlists básicas
3) 🎲 Generar Playlists avanzadas
4) 📋 Analizar origen
5) 📊 Ver estadísticas detalladas
6) 📁 Organizar en carpeta única
7) 🛡️ Gestión de backups
8) 🎧 Analizar calidad de audio
9) 🔍 Buscar duplicados
10) 🚪 Salir
```

**Uso**:
```bash
./music_manager.sh
```

---

## 📂 Estructura de Archivos

```
10_CULTURAL_RENAISSANCE/
├── music_library.json              # Base de datos principal (194 songs)
├── music_orphans_report.json       # Archivos sin metadata
│
├── music_webui.html                # 🌐 Interfaz web
├── launch_music_webui.sh           # Launcher WebUI
│
├── generate_playlists.py           # 📀 Playlists básicas
├── generate_advanced_playlists.py  # 🎲 Playlists avanzadas
├── analyze_music_sources.py        # 📋 Detector de origen
├── music_statistics.py             # 📊 Estadísticas
├── organize_music.py               # 📁 Organizador
├── music_backup_manager.py         # 🛡️ Backups
├── music_quality_analyzer.py       # 🎧 Análisis de calidad
├── music_duplicate_finder.py       # 🔍 Detector duplicados
│
├── music_manager.sh                # 🎛️ Menú unificado
│
├── playlists/                      # Todas las playlists generadas
│   ├── BlackMamba_ALL.m3u
│   ├── BlackMamba_ALL.m3u8
│   ├── BlackMamba_SHUFFLE_ALL.m3u8
│   ├── BlackMamba_WORKOUT.m3u8
│   └── ... (24+ playlists)
│
├── BlackMamba_Music_Collection/    # Colección organizada (si se ejecuta)
├── music_backups/                  # Backups con timestamp
├── audio_recordings/               # Grabaciones VPA
└── lyrics_cache/                   # Cache de letras
```

---

## 🚀 Quick Start

### Primera vez (recomendado):
```bash
# 1. Abrir interfaz web
./launch_music_webui.sh

# 2. Ver estadísticas
python3 music_statistics.py

# 3. Generar todas las playlists
python3 generate_playlists.py
python3 generate_advanced_playlists.py

# 4. Buscar duplicados
python3 music_duplicate_finder.py

# 5. Crear backup de seguridad
python3 music_backup_manager.py
```

### Uso diario:
```bash
# Menú todo-en-uno
./music_manager.sh
```

---

## 📊 Estado Actual de la Colección

**Total**: 194 canciones  
**Almacenamiento**: 1.46 GB (1496.65 MB)  
**Promedio**: 7.71 MB por canción  

**Formatos**:
- 186 archivos MP3
- 25 archivos WAV
- 17 canciones completas (ambos formatos)

**Artistas**: 100% BlackMamba  
**Año**: 100% 2025  
**Ubicación**: 100% Downloads  

**Canción más pesada**: Untitled (81.51 MB)  
**Canción más ligera**: Voicerecordingstopped (0.02 MB)  

---

## 🎯 Roadmap de Mejoras

### Implementadas ✅:
- [x] WebUI con reproductor y filtros
- [x] Playlists básicas (M3U/M3U8/PLS)
- [x] Playlists avanzadas (shuffle, temas, año)
- [x] Detección de origen (SoundCloud/Suno/Local)
- [x] Estadísticas detalladas
- [x] Organizador de carpetas
- [x] Sistema de backups con hash
- [x] Análisis de calidad (bitrate/codec)
- [x] Detector de duplicados

### Futuras 🔮:
- [ ] Integración con Vocal Performance Analyzer
- [ ] Integración con BlackMamba Audio Detector
- [ ] Auto-etiquetado con IA (género, BPM)
- [ ] Visualizador de espectro de audio
- [ ] Exportador a Spotify/Apple Music (API)
- [ ] Sincronización con cloud (Dropbox/Drive)
- [ ] Player de terminal (mpv/vlc)
- [ ] Editor de metadata bulk
- [ ] Conversor de formatos (MP3↔WAV)
- [ ] Análisis de similitud acústica (Librosa)

---

## 🦅 Filosofía del Sistema

> **"No solo reproducimos música, custodiamos el arte."**

Este sistema de gestión musical refleja los principios del Arquitecto:
- **Soberanía**: Control total sobre tu colección
- **Custodia**: Backups, integridad, preservación
- **Honor**: Herramientas transparentes sin dependencias externas
- **Eficiencia**: Un comando para todo (`music_manager.sh`)

---

## 📝 Notas Técnicas

### Dependencias:
- **Python 3.14.2+**: Core de todas las herramientas
- **ffmpeg/ffprobe**: Solo para análisis de calidad (opcional)
- **Navegador web**: Para WebUI (Chrome/Firefox/Safari)
- **JSON**: Base de datos lightweight

### Compatibilidad:
- macOS ✅ (nativo)
- Linux ✅ (compatible)
- Windows ⚠️ (requiere WSL o adaptaciones)

### Performance:
- WebUI: Carga instantánea (client-side)
- Playlists: ~2-3 segundos por batch
- Backups: ~5-10 segundos (194 archivos)
- Análisis de calidad: ~30-60 segundos (con ffprobe)
- Duplicados: ~10-15 segundos (hash completo)

---

🦅 **"Quiero ser sistema. Algo que funcione incluso cuando yo no esté mirando."**  
— Iyari Cancino Gomez, Arquitecto de XarvisCore

