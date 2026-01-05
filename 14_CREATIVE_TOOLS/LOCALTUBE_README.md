# 🦅 BlackMamba LocalTube - Reproductor Sin Lag

## 📺 ¿Qué es LocalTube?

LocalTube es un reproductor de videos local con interfaz tipo YouTube diseñado para reproducir tus ~4,000 videos del USB **sin lag**, sin buffering y sin necesidad de conexión a internet.

## ✨ Características

- **🎬 Reproducción Local**: Cero lag, cero buffering
- **📚 Biblioteca Inteligente**: Escanea automáticamente tu USB
- **🔍 Búsqueda Rápida**: Encuentra videos por nombre o carpeta
- **⚡ Controles Avanzados**: Velocidad (0.5x - 2x), loop, siguiente/anterior
- **🎨 Interfaz Matrix**: Estética cyberpunk con glassmorphism
- **📱 Drag & Drop**: Arrastra videos directamente a la interfaz
- **🎯 Filtros**: Por formato (MP4, MKV), fecha, etc.

## 🚀 Inicio Rápido

### Opción 1: Launcher Automático
```bash
cd /Users/blackmamba/Desktop/XarvisCore/14_CREATIVE_TOOLS
bash start_localtube.sh
```

### Opción 2: Manual

1. **Iniciar servidor**:
```bash
cd /Users/blackmamba/Desktop/XarvisCore
source venv/bin/activate
cd 14_CREATIVE_TOOLS
python3 local_youtube_server.py
```

2. **Abrir interfaz**:
```bash
open http://localhost:8888
```

O simplemente abre en tu navegador: http://localhost:8888

## 📊 Estadísticas

- **Videos Disponibles**: ~4,000
- **Ubicación**: `/Volumes/ADATA SC740`
- **Formatos Soportados**: MP4, MKV, MOV, AVI, WEBM, M4V
- **Puerto**: 8888

## 🎮 Uso

### Interfaz Principal

1. **Header**: 
   - Logo LocalTube
   - Barra de búsqueda
   - Estadísticas en tiempo real

2. **Reproductor Central**:
   - Video a pantalla completa
   - Controles nativos del navegador
   - Controles personalizados (velocidad, loop)

3. **Sidebar Derecho**:
   - Playlist completa
   - Filtros por formato
   - Videos recientes

### Controles de Teclado

- **Espacio**: Play/Pausa
- **←/→**: Retroceder/Adelantar 5 segundos
- **↑/↓**: Volumen
- **F**: Pantalla completa
- **M**: Silenciar

### Controles Personalizados

- **0.5x - 2x**: Cambiar velocidad de reproducción
- **🔁 Loop**: Repetir video actual
- **⏭️ Siguiente**: Reproducir siguiente en playlist
- **⏮️ Anterior**: Reproducir anterior

## 📂 Estructura de Videos

LocalTube escanea estas carpetas del USB:
- `/04_SERIES/` - Series como The Mandalorian
- `/02_MEDIA/` - Contenido multimedia general
- `/untitled folder/` - Videos variados
- `/00_ORGANIZED_MASTER/` - Archivos organizados

## 🔧 API Endpoints

### `GET /api/videos`
Retorna lista completa de videos con metadata
```json
{
  "total": 500,
  "last_scan": "2025-12-30T19:30:00",
  "videos": [...]
}
```

### `GET /api/scan`
Fuerza un nuevo escaneo del USB
```json
{
  "status": "success",
  "total": 500,
  "message": "Encontrados 500 videos"
}
```

### `GET /api/video/<path>`
Sirve un video específico en streaming

### `GET /api/stats`
Estadísticas de la biblioteca
```json
{
  "total_videos": 500,
  "total_size": "120 GB",
  "formats": {
    "MP4": 350,
    "MKV": 150
  }
}
```

## 🎯 Drag & Drop

Arrastra videos desde Finder directamente a LocalTube:
1. Abre LocalTube
2. Arrastra archivos `.mp4`, `.mkv`, etc.
3. Se agregan automáticamente a la playlist
4. Comienza a reproducir

## ⚙️ Configuración

### Cambiar Puerto
Edita `local_youtube_server.py`:
```python
app.run(host='0.0.0.0', port=8888, debug=False)
```

### Aumentar Límite de Videos
Edita `local_youtube_server.py`:
```python
scan_videos(max_videos=1000)  # Default: 500
```

### Agregar Directorios de Búsqueda
Edita `local_youtube_server.py`:
```python
search_dirs = [
    USB_BASE / "04_SERIES",
    USB_BASE / "TU_NUEVA_CARPETA",  # Agregar aquí
]
```

## 📋 Caché

LocalTube guarda un cache JSON para inicio rápido:
- Archivo: `video_library_cache.json`
- Se actualiza cada escaneo
- Contiene metadata de todos los videos

## 🐛 Troubleshooting

### Servidor no inicia
```bash
# Verificar puerto ocupado
lsof -i :8888

# Matar proceso si es necesario
kill -9 <PID>
```

### Videos no cargan
1. Verifica que el USB esté conectado
2. Verifica permisos de lectura
3. Fuerza un nuevo escaneo desde la interfaz

### Interfaz no abre
```bash
# Verificar servidor corriendo
ps aux | grep local_youtube

# Abrir manualmente
open http://localhost:8888
```

## 🔐 Seguridad

LocalTube:
- ✅ Solo lee archivos locales
- ✅ No envía datos a internet
- ✅ No requiere autenticación
- ✅ CORS habilitado solo para localhost

## 📝 Logs

El servidor imprime logs en tiempo real:
- 🔍 Escaneos de directorios
- ✅ Videos encontrados
- ❌ Errores de acceso
- 📊 Estadísticas finales

## 🎨 Personalización

### Cambiar Tema
Edita `local_youtube.html` CSS variables:
```css
:root {
    --primary: #00ff41;    /* Verde Matrix */
    --secondary: #0a84ff;  /* Azul */
    --bg: #0a0a0a;         /* Fondo negro */
}
```

### Iconos de Videos
Edita función `get_video_icon()` en el servidor:
```python
if 'tutorial' in name_lower:
    return '📚'
```

## 🚀 Próximas Características

- [ ] Miniaturas de videos (thumbnails)
- [ ] Marcadores de tiempo
- [ ] Playlists personalizadas
- [ ] Historial de reproducción
- [ ] Subtítulos automáticos
- [ ] Modo teatro
- [ ] Cast a TV

## 📄 Archivos del Sistema

```
14_CREATIVE_TOOLS/
├── local_youtube.html           # Interfaz web
├── local_youtube_server.py      # Servidor Flask
├── start_localtube.sh           # Launcher automático
├── video_library_cache.json     # Cache de videos
└── LOCALTUBE_README.md          # Esta documentación
```

## 👨‍💻 Arquitecto

**Iyari Cancino Gomez**  
BlackMamba XarvisCore - Sistema Soberano

---

🦅 **"No más lag. Solo videos."**
