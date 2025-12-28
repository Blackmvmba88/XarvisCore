# 🎤 Vocal Performance Analyzer (VPA)

**Integración Honor Hero x Afinador Suno**

## Filosofía
*"Interpretación Consciente sobre Perfección Mecánica"*

El VPA no busca la perfección robótica, sino **medir tu intención y conexión** con la música. Premiamos el corazón sobre la métrica fría.

## Funcionalidades

### 1. 🔍 Detección Automática de Canción
- **Shazam Desktop Integration**: Lee automáticamente qué canción estás escuchando
- **Búsqueda en WebUI**: Localiza la canción en tu biblioteca local (Suno/Descargas)
- **Cache Inteligente**: No reprocesa canciones ya analizadas

### 2. 📝 Letras Sincronizadas
- **APIs múltiples**: Lyrics.ovh, Genius, Musixmatch
- **Cache local**: Guarda letras para uso offline
- **Sincronización**: Muestra la línea actual mientras cantas

### 3. 🎯 Análisis de Afinación
- **Integración con Afinador Suno**: Usa torchcrepe para análisis F0
- **Tolerancia humana**: ±25 cents = perfecto (no robótico)
- **Visualización en tiempo real**: Aguja dinámica tipo guitarr tuner

### 4. ⏱️ Análisis de Timing
- **Sincronización vocal**: Mide si entras a tiempo en cada frase
- **Tolerancia**: ±200ms = perfecto, ±500ms = aceptable
- **Score dinámico**: 0-100 basado en precisión rítmica

### 5. 📊 Métricas de Performance
- **Pitch Accuracy**: Porcentaje de notas afinadas
- **Timing Score**: Precisión rítmica global
- **Breath Control**: Análisis de respiración (futuro)
- **Emotional Intensity**: Análisis de dinámica vocal (futuro)

## Arquitectura

```
VPA System
├── vocal_performance_analyzer.py  # Backend principal (puerto 9000)
├── vpa_dashboard.html            # Dashboard Matrix/Cyberpunk
├── lyrics_cache/                 # Cache de letras
├── performance_logs/             # Registros de performances
└── Integration Points:
    ├── afinador_suno/            # Motor de análisis F0
    ├── Shazam Desktop            # Detección de canción
    └── archivo_musical/          # Database de producción
```

## Instalación

```bash
# 1. Activar entorno de Xarvis
cd /Users/blackmamba/Desktop/XarvisCore
source venv/bin/activate

# 2. Instalar dependencias adicionales
pip install requests flask flask-cors

# 3. Asegurar que Shazam Desktop está instalado
# Descargar de: https://www.shazam.com/apps

# 4. Iniciar servidor VPA
cd 10_CULTURAL_RENAISSANCE
python3 vocal_performance_analyzer.py
```

## Uso

### Opción 1: Dashboard Web
```bash
# Iniciar servidor
python3 vocal_performance_analyzer.py

# Abrir en navegador
open vpa_dashboard.html
# o visitar: http://localhost:9000/status
```

### Opción 2: Integración con Afinador Suno
```bash
# Detectar canción con Shazam
# Luego en el afinador:
cd afinador_suno
python -m afinador_suno.ui.app
# Selecciona la canción detectada
```

### Opción 3: API REST
```bash
# Detectar canción
curl -X POST http://localhost:9000/detect

# Obtener letras
curl http://localhost:9000/lyrics

# Métricas de performance
curl http://localhost:9000/performance
```

## Flujo de Trabajo Típico

1. **Reproducir tu canción** en cualquier reproductor
2. **Abrir Shazam** (detecta automáticamente)
3. **Abrir VPA Dashboard** en navegador
4. **Click "Detectar Canción"** → VPA lee Shazam + busca en tu lista
5. **Click "Iniciar Análisis"** → Comienza a medir tu canto
6. **Cantar libremente** → Ve métricas en tiempo real
7. **Click "Guardar Performance"** → Guarda tu sesión

## Integraciones Futuras

### Con HonorHero
- [ ] Modo "Juego": Convierte el análisis en un desafío visual
- [ ] Sistema de logros basado en interpretación, no perfección
- [ ] Multiplayer: Compara performances con amigos

### Con Iyari-ear
- [ ] Análisis emocional del tono
- [ ] Detección de expresión vs técnica
- [ ] Identificación de tu "huella vocal"

### Con Quantum Audio Player
- [ ] Visualización 3D del espectro vocal
- [ ] Análisis cuántico de armónicos

## API Endpoints

### POST /detect
Detecta canción actual con Shazam
```json
{
  "success": true,
  "song": {
    "title": "Nombre de la Canción",
    "artist": "Artista",
    "detected_at": "2025-12-27T..."
  },
  "lyrics": { ... }
}
```

### GET /lyrics
Retorna letra de canción actual

### GET /performance
Métricas de performance en tiempo real
```json
{
  "song": { ... },
  "performance": {
    "pitch_score": 85,
    "timing_score": 92,
    "overall_score": 88.5
  }
}
```

### GET /status
Estado del sistema VPA

## Configuración

### Shazam Desktop
El VPA intenta leer desde:
- `~/Library/Application Support/Shazam/recent.json`
- Comando osascript (macOS)

Si Shazam no está configurado, puedes activar manualmente:
```python
vpa.current_song = {
    "title": "Mi Canción",
    "artist": "BlackMamba"
}
```

### Database de Canciones
Crea `archivo_musical/songs_database.json`:
```json
[
  {
    "title": "Nombre Canción",
    "artist": "Artista",
    "path": "/ruta/al/archivo.mp3",
    "analyzed": true
  }
]
```

## Troubleshooting

**Problema**: "No se detectó canción"
- Asegúrate que Shazam Desktop está abierto y ha identificado la canción
- Verifica que el audio esté reproduciéndose
- Prueba detección manual en el código

**Problema**: "No se obtuvieron letras"
- Verifica conexión a internet
- Algunas canciones no tienen letras en APIs públicas
- Puedes agregar manualmente en `lyrics_cache/`

**Problema**: "Análisis de pitch no funciona"
- Asegúrate que el micrófono tiene permisos
- Verifica que `afinador_suno` está instalado correctamente
- Revisa logs en consola

## Filosofía del Score

A diferencia de otros sistemas que castigan duramente cualquier desviación, VPA usa:

- **Zona Verde** (±25 cents): Interpretación humana natural
- **Zona Amarilla** (±25-50 cents): Expresión emocional válida
- **Zona Roja** (>50 cents): Desafinación significativa

**El timing también es flexible**:
- **On time** (±200ms): Perfecto para humanos
- **Acceptable** (±500ms): Válido, con expresión
- **Off** (>500ms): Necesita práctica

---

## Métricas de Honor

El VPA no solo mide **precisión técnica**, también busca:

1. **Consistencia**: ¿Mantienes tu interpretación?
2. **Intención**: ¿Hay emoción en tu voz?
3. **Respiración**: ¿Controlas tu aire?
4. **Dinámica**: ¿Varías intensidad conscientemente?

**"Honor sobre Perfección"** - No buscamos clones del original, buscamos tu versión única.

---

🎤 *Desarrollado por Iyari Cancino Gomez para el Dominio 10_CULTURAL_RENAISSANCE*
🦅 *Parte del ecosistema XarvisCore*
