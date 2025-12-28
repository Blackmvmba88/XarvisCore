# 🎤 BlackMamba Music Performance Suite

**Integración completa**: Music Manager + VPA + Audio Detector  
**Arquitecto**: Iyari Cancino Gomez  
**Fecha**: 28 de Diciembre, 2025

---

## 🎯 ¿Qué es?

La **Music Performance Suite** es una integración total de:
- 🎵 **Music Management Suite** (10 herramientas)
- 🎤 **VPA (Vocal Performance Analyzer)** - Análisis vocal en tiempo real
- 🔊 **BlackMamba Audio Detector** - Fingerprinting acústico offline

Todo en una **interfaz web unificada** con API REST completa.

---

## 🚀 Quick Start

### Iniciar el servidor:
```bash
cd 10_CULTURAL_RENAISSANCE
./start_performance_suite.sh
```

### O desde el Music Manager:
```bash
./music_manager.sh
# Selecciona opción 10
```

**Acceso**: http://localhost:9002

---

## 🛠️ Componentes Integrados

### 1. **Detección Dual** 🔍
Combina Shazam + BlackMamba Detector para máxima precisión:
- **Shazam primero**: Para canciones en Spotify/mainstream
- **BlackMamba después**: Para SoundCloud y locales

**Endpoint**: `POST /api/detect/dual`
```json
{
  "duration": 10
}
```

**Respuesta**:
```json
{
  "method": "shazam|blackmamba",
  "detected": true,
  "song": {
    "title": "Canción detectada",
    "artist": "Artista",
    "file_path": "/ruta/al/archivo.mp3"
  },
  "confidence": 0.95
}
```

---

### 2. **BlackMamba Detector** 🎵
Detección offline por fingerprinting acústico:
- No requiere internet
- Reconoce canciones de SoundCloud
- 194 canciones indexadas

**Endpoint**: `POST /api/detect/blackmamba`

**Ventajas**:
- ✅ Funciona offline
- ✅ Reconoce música local
- ✅ Sistema soberano (sin APIs externas)

---

### 3. **Shazam Integration** 🔊
Detección vía API de Shazam:
- Reconocimiento de música mainstream
- Links directos a Shazam
- Integración con biblioteca local

**Endpoint**: `POST /api/detect/shazam`

---

### 4. **Análisis Vocal** 🎤
Métricas de performance vocal:
- **Pitch accuracy**: Precisión de afinación
- **Timing**: Análisis rítmico
- **Comparación** con referencia

**Endpoint**: `POST /api/analyze/vocal`
```json
{
  "audio_path": "/ruta/audio.mp3"
}
```

**Métricas**:
- Pitch accuracy (0-100%)
- Timing accuracy (0-100%)
- Desviación promedio en cents
- Notas detectadas vs esperadas

---

### 5. **Obtención de Letras** 📝
Fetching automático de letras:
- API: Lyrics.ovh
- Cache local
- Sincronización con detección

**Endpoint**: `GET /api/lyrics?title=...&artist=...`

---

### 6. **Biblioteca Musical** 📚
Acceso a las 194 canciones indexadas:
- Búsqueda por título/artista
- Filtros por formato (MP3/WAV)
- Estadísticas de colección

**Endpoints**:
- `GET /api/library` - Biblioteca completa
- `GET /api/library/search?q=query` - Búsqueda

---

## 🎛️ Interfaz Web (Dashboard)

### Características:

**Diseño Matrix/Cyberpunk**:
- Glassmorphism estético
- Verde neón (#00ff41)
- Animaciones fluidas
- Responsive design

**Funcionalidades**:
1. **Detección en vivo**: Botones para cada método
2. **Status indicators**: Verde = activo, Gris = inactivo
3. **Loading states**: Feedback visual durante procesos
4. **Results cards**: Despliegue de resultados en tiempo real

**Componentes UI**:
- 6 tarjetas principales (Dual, Detector, Shazam, Vocal, Letras, Biblioteca)
- Status bar con contador de componentes activos
- Estadísticas de biblioteca
- Links directos a Music WebUI y Music Manager

---

## 📡 API REST Completa

### Base URL: `http://localhost:9002`

### Endpoints de Detección:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/detect/dual` | Detección dual (Shazam + BlackMamba) |
| POST | `/api/detect/blackmamba` | Solo BlackMamba detector |
| POST | `/api/detect/shazam` | Solo Shazam |

### Endpoints de Análisis:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/analyze/vocal` | Análisis vocal completo |
| GET | `/api/lyrics` | Obtener letras (query params) |

### Endpoints de Biblioteca:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/library` | Biblioteca completa |
| GET | `/api/library/search` | Búsqueda en biblioteca |

### Endpoint de Status:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/status` | Estado del sistema |

**Respuesta de `/api/status`**:
```json
{
  "status": "operational",
  "components": {
    "vpa": true,
    "detector": true,
    "music_library": 194
  },
  "features": {
    "dual_detection": true,
    "shazam": true,
    "blackmamba_detector": true,
    "vocal_analysis": true,
    "lyrics_fetch": true
  },
  "library_stats": {
    "total_songs": 194,
    "indexed": 194
  }
}
```

---

## 🔧 Requisitos

### Python Packages:
```
flask>=3.0.0
flask-cors>=4.0.0
shazamio>=0.4.0
numpy>=1.24.0
librosa>=0.10.0
```

### Sistema:
- **chromaprint** (para detector): `brew install chromaprint`
- **ffmpeg** (para análisis): `brew install ffmpeg`
- **SoX** (para grabación): `brew install sox`

### Archivos necesarios:
- `music_library.json` - Biblioteca musical
- `audio_fingerprints.json` - Base de fingerprints
- `vocal_performance_analyzer.py` - VPA base
- `vpa_with_detector.py` - VPA + Detector integrado
- `audio_detector.py` - Detector standalone

---

## 🎯 Casos de Uso

### 1. **Karaoke Inteligente**
```
1. Abrir Performance Suite
2. Detectar canción que está sonando (Dual)
3. Obtener letras automáticamente
4. Cantar y grabar
5. Analizar performance vocal
6. Ver métricas de afinación
```

### 2. **Identificación de Música Local**
```
1. Reproducir canción de SoundCloud
2. Usar BlackMamba Detector
3. Obtener info de archivo local
4. Ver en biblioteca completa
```

### 3. **Práctica Vocal**
```
1. Seleccionar canción de biblioteca
2. Obtener letras
3. Grabar interpretación
4. Analizar vocal (pitch + timing)
5. Repetir hasta mejorar métricas
```

### 4. **Curación de Biblioteca**
```
1. Detectar canciones desconocidas
2. Auto-completar metadata
3. Organizar en carpeta única
4. Generar playlists automáticas
```

---

## 🚀 Flujo de Trabajo Típico

### **Sesión de Práctica Vocal:**

1. **Iniciar Suite**:
   ```bash
   ./start_performance_suite.sh
   ```

2. **Detectar canción actual**:
   - Click en "Detección Dual"
   - Esperar 10 segundos
   - Ver resultado (título + artista)

3. **Obtener letras**:
   - Auto-fill desde detección
   - O buscar manualmente
   - Ver letras completas

4. **Practicar y grabar**:
   - Cantar con la canción
   - Grabar con VPA

5. **Analizar performance**:
   - Upload de grabación
   - Ver métricas de afinación
   - Comparar con referencia

6. **Iterar**:
   - Repetir hasta alcanzar >90% accuracy
   - Guardar mejores takes

---

## 📊 Métricas y Estadísticas

### Sistema:
- **Componentes activos**: 3/3 (VPA + Detector + Library)
- **Canciones indexadas**: 194
- **Fingerprints**: 194
- **Cache de letras**: ~50 canciones

### Performance:
- **Detección dual**: ~12-15 segundos
- **BlackMamba only**: ~2-3 segundos
- **Shazam only**: ~5-7 segundos
- **Análisis vocal**: ~10-20 segundos
- **Fetch letras**: ~1-2 segundos (con cache)

---

## 🔮 Roadmap

### Próximas Features:

#### Alta Prioridad:
- [ ] **Upload de audio** para análisis vocal
- [ ] **Sincronización de letras** con audio
- [ ] **Visualización de pitch** en tiempo real
- [ ] **Comparación lado a lado** (original vs grabación)

#### Media Prioridad:
- [ ] **Modo práctica** con loops
- [ ] **Banco de ejercicios** vocales
- [ ] **Progress tracking** de mejora
- [ ] **Leaderboards** de accuracy

#### Baja Prioridad:
- [ ] **Export a formato MIDI**
- [ ] **Auto-transcripción** de melodías
- [ ] **Harmony detector**
- [ ] **Mood analyzer**

---

## 🐛 Troubleshooting

### VPA no disponible:
```bash
# Verificar imports
python3 -c "from vpa_with_detector import VPAWithDetector"

# Instalar dependencias
pip install shazamio numpy librosa
```

### Audio Detector falla:
```bash
# Verificar chromaprint
fpcalc -version

# Instalar si falta
brew install chromaprint
```

### Grabación no funciona:
```bash
# Verificar SoX
rec --version

# Instalar si falta
brew install sox

# Configurar device de audio
# En macOS: Usar BlackHole o Multi-Output Device
```

### Puerto ocupado:
```bash
# Cambiar puerto en music_performance_suite.py
PORT = 9003  # O cualquier otro
```

---

## 📝 Notas del Arquitecto

> **"Esta integración representa la culminación de 3 sistemas independientes en una sola herramienta unificada. Cada componente aporta su soberanía: Music Suite gestiona, VPA analiza, Detector identifica. Juntos, crean una experiencia musical completa."**

**Filosofía de diseño**:
- **Soberanía**: Sistema funciona offline (excepto Shazam)
- **Custodia**: Preserva y analiza tu música con honor
- **Eficiencia**: Una interfaz para todo
- **Transparencia**: API REST abierta

---

## 🦅 Integración con XarvisCore

El Performance Suite es el **componente musical del dominio 10_CULTURAL_RENAISSANCE**:

**Conectado con**:
- `1_CORE` - Dashboard principal de Xarvis
- `3_POWER` - Monitoreo de recursos
- `xarvis_supervisor.py` - Orquestación de servicios

**Puede integrarse con**:
- `17_AI_EXPERIMENTS` - Quantum Audio Player
- `7_EDUCATION_SYSTEM` - BMU (clases de canto)
- `18_BLACKMAMBA_STATION` - Command Center

---

🎵 **BlackMamba Music Performance Suite - La música es arquitectura emocional.**

