# 🎵 Especificación: Sistema de Lista Musical para VPA

## 📋 Ubicaciones Oficiales de la Música

### Estructura Actual (Documentada)

```
1. USB/Producción Principal:
   /Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/
   ├── Archivos MP3/WAV sueltos
   ├── Carpetas por proyecto/álbum
   └── Total: ~11,000+ tracks

2. Carpeta Suno (Sistema):
   ~/Music/Suno/
   ├── index.json              # Índice generado por suno-organizer
   ├── .suno-index.json        # Alternativo
   └── Archivos organizados por suno-org

3. Carpeta Downloads (Temporal):
   ~/Downloads/
   └── Archivos recién generados en Suno
```

## 🎯 Reglas de Búsqueda VPA

### Prioridad de Búsqueda (Orden)

```python
SEARCH_PRIORITY = [
    {
        "location": "~/Music/Suno/",
        "index_file": "~/Music/Suno/index.json",
        "fallback_index": "~/Music/Suno/.suno-index.json",
        "priority": 1,  # Primera opción
        "reason": "Índice optimizado con metadatos completos"
    },
    {
        "location": "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/",
        "index_file": None,  # Escaneo en tiempo real o cache
        "priority": 2,
        "reason": "Biblioteca principal de producción"
    },
    {
        "location": "~/Downloads/",
        "index_file": None,
        "priority": 3,
        "reason": "Archivos recientes sin organizar"
    }
]
```

## 📊 Formato del Índice JSON

### Estructura de `index.json` (Suno Organizer)

```json
[
  {
    "file_path": "/Users/blackmamba/Music/Suno/trap_vibes_remix.mp3",
    "title": "Trap Vibes",
    "artist": "BlackMamba",
    "type": "remix",  // original|remix|cover|collaboration|experimental
    "genre": "trap",
    "duration_seconds": 180,
    "file_size_mb": 4.2,
    "format": "mp3",
    "audio_fingerprint": "abc123def456",  // Si tiene fingerprinting
    "created_date": "2025-12-20",
    "tags": ["trap", "remix", "energetic"]
  }
]
```

### Campos Mínimos Requeridos

```python
REQUIRED_FIELDS = [
    "file_path",    # Ruta absoluta al archivo
    "title",        # Título de la canción
    "artist"        # Artista (por defecto "BlackMamba")
]

OPTIONAL_FIELDS = [
    "type",         # Categoría Suno
    "genre",        # Género musical
    "duration_seconds",
    "format",       # mp3|wav|midi
    "tags"          # Lista de etiquetas
]
```

## 🔍 Algoritmo de Búsqueda VPA

### Cuando Shazam detecta: "Trap Vibes" por "BlackMamba"

```python
def find_song_in_library(title, artist):
    """
    Busca canción en todas las ubicaciones con búsqueda fuzzy.
    """
    
    # Paso 1: Buscar en índice Suno (más rápido)
    result = search_in_suno_index(title, artist)
    if result:
        return result
    
    # Paso 2: Buscar en USB (si está montado)
    if usb_is_mounted():
        result = search_in_usb(title, artist)
        if result:
            return result
    
    # Paso 3: Buscar en Downloads
    result = search_in_downloads(title, artist)
    if result:
        return result
    
    # Paso 4: No encontrado - modo manual
    return None

def search_in_suno_index(title, artist):
    """
    Lee index.json y busca con fuzzy matching.
    """
    with open("~/Music/Suno/index.json") as f:
        songs = json.load(f)
    
    for song in songs:
        # Matching simple (case-insensitive)
        if (title.lower() in song["title"].lower() and
            artist.lower() in song["artist"].lower()):
            return song
        
        # Matching por tags
        if "tags" in song:
            for tag in song["tags"]:
                if title.lower() in tag.lower():
                    return song
    
    return None
```

## 🎨 WebUI: Visualización de Lista

### Formato HTML para Dashboard

```html
<div class="song-card" data-song-id="{{song_id}}">
    <div class="song-icon">
        {{category_emoji}}  <!-- ✨🔄🤝🏛️🔬 según type -->
    </div>
    <div class="song-info">
        <h3>{{title}}</h3>
        <p>{{artist}} • {{genre}}</p>
        <span class="duration">{{duration}}</span>
    </div>
    <div class="song-actions">
        <button onclick="loadSong('{{file_path}}')">🎤 Cantar</button>
        <button onclick="playSong('{{file_path}}')">▶️</button>
    </div>
</div>
```

### Estados de Canción

```python
SONG_STATUS = {
    "available": "✅ Disponible",
    "analyzed": "🔬 Analizada (F0 extraído)",
    "missing": "❌ Archivo no encontrado",
    "usb_offline": "💾 En USB (sin montar)"
}
```

## 🔧 Integración con Componentes Existentes

### Con Afinador Suno

```python
# VPA encuentra la canción
song = vpa.find_song_in_library("Trap Vibes", "BlackMamba")

# Pasa al afinador para análisis F0
if song and song["status"] != "analyzed":
    afinador.analyze_song(song["file_path"])
    song["status"] = "analyzed"
    song["f0_analysis_path"] = f"analyses/{song['id']}.json"

# Carga análisis para comparación en tiempo real
reference_f0 = afinador.load_f0_analysis(song["f0_analysis_path"])
```

### Con Music Server (archivo_musical)

```python
# VPA puede usar el servidor existente para streaming
MUSIC_SERVER_PORT = 8888
MUSIC_SERVER_URL = f"http://localhost:{MUSIC_SERVER_PORT}"

def stream_song(song_path):
    """
    Usa el music_server.py existente para streaming.
    """
    # Codificar path para URL
    encoded_path = urllib.parse.quote(song_path)
    stream_url = f"{MUSIC_SERVER_URL}/audio/{encoded_path}"
    return stream_url
```

## 📝 Reglas de Categorización

### Detección Automática de Tipo

```python
def detect_song_type(title, filename):
    """
    Categoriza automáticamente según nombre.
    """
    title_lower = title.lower()
    file_lower = filename.lower()
    
    # Remix
    if any(x in title_lower for x in ["remix", "extended", "edit"]):
        return "remix"
    
    # Colaboración
    if any(x in title_lower for x in ["ft.", "feat.", "featuring"]):
        return "collaboration"
    
    # Cover
    if "cover" in title_lower or "version" in title_lower:
        return "cover"
    
    # Cultural
    if any(x in title_lower for x in ["náhuatl", "maya", "azteca", "mexica"]):
        return "cultural"
    
    # Experimental
    if any(x in title_lower for x in ["neon", "galactic", "quantum", "cyber"]):
        return "experimental"
    
    # Por defecto: Original
    return "original"
```

## 🚀 Generación del Índice (Primera Vez)

### Script de Inicialización

```bash
# Opción 1: Usar suno-organizer (si ya está instalado)
cd ~/Music/Suno
suno-org scan-audio --fingerprint --out-json index.json

# Opción 2: Script VPA propio (escaneo básico)
cd 10_CULTURAL_RENAISSANCE
python3 -c "
from vocal_performance_analyzer import vpa
vpa.generate_music_index()
"
```

### Formato Mínimo para Empezar

Si no tienes índice, crea uno simple:

```json
[
  {
    "file_path": "/ruta/completa/a/cancion.mp3",
    "title": "Nombre de la Canción",
    "artist": "BlackMamba"
  }
]
```

Guárdalo en: `10_CULTURAL_RENAISSANCE/music_library.json`

## 🎯 Roadmap de Implementación

### Fase 1: MVP (Actual) ✅
- [x] Detección con Shazam
- [x] Búsqueda básica en índice
- [x] Obtención de letras

### Fase 2: Integración Index (Siguiente)
- [ ] Leer `~/Music/Suno/index.json`
- [ ] Fallback a escaneo en Downloads
- [ ] Cache de búsquedas

### Fase 3: UI Completa
- [ ] Lista visual de canciones en dashboard
- [ ] Filtros por tipo/género
- [ ] Selector manual si Shazam falla

### Fase 4: Sincronización Total
- [ ] Integración con Afinador Suno
- [ ] Streaming desde Music Server
- [ ] Base de datos SQLite para performances

---

## 💡 Ejemplo de Uso Completo

```bash
# Terminal 1: Music Server (para streaming)
cd archivo_musical
./launch_music_player.sh

# Terminal 2: VPA Server
cd 10_CULTURAL_RENAISSANCE
./start_vpa.sh

# Terminal 3: Shazam Desktop
# (Abierto en background, detectando)

# Navegador:
# 1. Abre vpa_dashboard.html
# 2. Reproduce tu canción en cualquier player
# 3. Shazam la detecta automáticamente
# 4. VPA la encuentra en index.json
# 5. Carga letra + análisis F0
# 6. ¡Empieza a cantar!
```

---

🎤 **Especificación v1.0** - 27 de Diciembre, 2025  
📋 Iyari Cancino Gomez - Dominio 10_CULTURAL_RENAISSANCE
