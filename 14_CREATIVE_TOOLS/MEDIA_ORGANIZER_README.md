# 📂 ORGANIZADOR MULTIMEDIA BLACKMAMBA

## 🎯 ¿Qué hace?

Organiza automáticamente tu contenido multimedia:
- **🎵 Música**: Unifica canciones en carpeta única (ya implementado)
- **🎬 Películas**: Categoriza videos de Downloads → ~/Movies/BlackMamba_Cinema

## 📊 Estado Actual

### Música ✅
- **280+ tracks** organizados en `10_CULTURAL_RENAISSANCE/BlackMamba_Music_Collection`
- Indexados en `music_library.json`
- Integrado con VPA, Audio Detector y suite Suno

### Películas 🆕
- **64 videos** detectados en Downloads
- Categorización automática:
  - 🎬 **Películas** (>500 MB, keywords: 1080p, IMAX, BluRay)
  - 📺 **Series** (s01, season, episode)
  - 📚 **Documentales** (documentary, national geographic)
  - 🎞️ **Cortos** (<100 MB o <15 minutos)

---

## 🚀 Uso Rápido

### Opción 1: Simulación (Ver qué pasaría)
```bash
cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 movie_organizer.py
```

### Opción 2: Ejecutar Organización
```bash
cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS

# Editar movie_organizer.py línea 21:
# DRY_RUN = False  # Cambiar True → False

/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 movie_organizer.py
```

### Opción 3: Script Interactivo
```bash
cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
bash organize_media.sh
# Seleccionar opción:
# 1 = Solo música
# 2 = Solo películas
# 3 = Ambos
# 4 = Ver estadísticas
```

---

## 📁 Estructura Resultante

### Después de organizar películas:
```
~/Movies/BlackMamba_Cinema/
├── Películas/
│   ├── Mission Impossible The Final Reckoning 2025.mkv (2.9 GB)
│   └── [Otra película].mp4 (593 MB)
├── Documentales/
├── Series/
├── Cortos/
│   ├── super tormenta.mp4
│   ├── cocina tradicional mexicana.mp4
│   └── [60 videos más]
├── Sin_Clasificar/
└── movie_catalog.json  (catálogo completo)
```

### Música (ya organizado):
```
~/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE/
└── BlackMamba_Music_Collection/
    ├── [280+ canciones en MP3/WAV]
    └── music_library.json
```

---

## 🔍 Categorización Inteligente

### Películas
- Tamaño > 500 MB
- Keywords: 1080p, 720p, 4K, BluRay, WEB-DL, IMAX, HDRip
- Duración > 60 minutos (si ffprobe disponible)

### Series
- Keywords: s01, s02, season, episode, ep, temporada
- Ejemplo: `Breaking.Bad.S05E14.1080p.mp4`

### Documentales
- Keywords: documental, documentary, national, geographic, discovery
- Ejemplo: `National.Geographic.Ocean.Documentary.mp4`

### Cortos
- Tamaño < 100 MB
- Duración < 15 minutos
- Clips generados, videos cortos

---

## 🛡️ Seguridad

### Modo DRY RUN (por defecto)
- ✅ NO mueve archivos
- ✅ Solo muestra qué haría
- ✅ Seguro para probar

### Modo Ejecución
- ⚠️ Mueve archivos permanentemente
- ✅ Crea backup en catálogo JSON
- ✅ Respeta archivos existentes (no sobrescribe)

---

## 📊 Ver Resultados

### Después de organizar:
```bash
cd ~/Movies/BlackMamba_Cinema
ls -lh Películas/
ls -lh Cortos/

# Ver catálogo completo
cat movie_catalog.json | jq '.statistics'
```

### Ver estadísticas:
```bash
cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 movie_organizer.py --stats
```

---

## 🎯 Características

### Limpieza de Nombres
Antes: `Mission.Impossible.2025.IMAX.1080p.WEB-DL.HEVC.x265-RMTeam.mkv`  
Después: `Mission Impossible 2025.mkv`

### Preserva Extensiones
- ✅ .mp4, .mkv, .avi, .mov, .m4v, .webm
- ✅ Respeta formato original

### Catálogo JSON
```json
{
  "generated": "2025-12-30T11:30:00",
  "total_files": 64,
  "files": [
    {
      "original": "Mission.Impossible.2025.mkv",
      "clean_name": "Mission Impossible 2025.mkv",
      "category": "Películas",
      "size_mb": 2943.1,
      "source": "/Users/.../Downloads/...",
      "destination": "/Users/.../Movies/BlackMamba_Cinema/Películas/..."
    }
  ],
  "statistics": {
    "Películas": 2,
    "Cortos": 62
  }
}
```

---

## 🔧 Personalización

### Cambiar destino:
```python
# En movie_organizer.py línea 18
MOVIES_BASE = Path.home() / "Movies" / "Mi_Carpeta_Custom"
```

### Ajustar umbrales:
```python
# Línea 74-75
if duration < 15:  # Cambiar 15 minutos
if size_mb > 500:  # Cambiar 500 MB
```

### Agregar keywords:
```python
# Línea 28-32
KEYWORDS = {
    'Documentales': ['documental', 'mi_keyword'],
    'Series': ['s01', 'mi_pattern']
}
```

---

## 🎬 Ejemplo Completo

```bash
# 1. Ver qué tienes
cd ~/Downloads
ls -lh *.{mp4,mkv}

# 2. Simulación
cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 movie_organizer.py

# 3. Si te gusta el resultado, ejecutar
# Editar: DRY_RUN = False
/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 movie_organizer.py

# 4. Ver resultado
cd ~/Movies/BlackMamba_Cinema
tree -L 2
```

---

## 🎵 Integración con Suite Musical

El organizador es parte del ecosistema BlackMamba:
- **10_CULTURAL_RENAISSANCE**: Música + VPA + Audio Detector
- **14_CREATIVE_TOOLS**: Películas + 3milpixeles + YTDLP + Audio 3D Lab

Ambos comparten la filosofía de **organización inteligente** y **catálogos JSON** para integración futura.

---

**Arquitecto**: Iyari Cancino Gomez  
**Sistema**: BlackMamba Media Organizer  
**Filosofía**: "Orden sin esfuerzo, creatividad sin límites."

🎬🎵📂
