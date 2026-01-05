# 🦅 Suno AutoPipeline - Sistema Inteligente de Procesamiento Musical

**Arquitecto**: Iyari Cancino Gomez  
**Fecha**: 1 de Enero, 2026  
**Dominio**: 10_CULTURAL_RENAISSANCE

---

## ¿Qué hace?

El **Suno AutoPipeline** es el sistema inteligente que automatiza todo el flujo de trabajo cuando creas nueva música en Suno:

```
📥 Detecta canciones nuevas
    ↓
📦 Copia MP3 + WAV al vault
    ↓
📝 Extrae las letras automáticamente
    ↓
📚 Agrega a music_library.json
    ↓
🔍 Genera fingerprint para detector
    ↓
💾 Sincroniza al USB
    ↓
✅ COMPLETADO
```

**Todo esto sucede automáticamente. Sin intervención manual.**

---

## Uso Básico

### Opción 1: Ejecutar manualmente (recomendado)
```bash
cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE
bash start_suno_autopipeline.sh
```

### Opción 2: Python directo
```bash
cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE
/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 suno_autopipeline.py
```

---

## Flujo de Trabajo

### 1. Creas música en Suno
- Descargas el MP3
- Opcionalmente el WAV
- Guardas las letras en un .txt (o las copia Suno automáticamente)

### 2. Ejecutas el pipeline
```bash
bash start_suno_autopipeline.sh
```

### 3. El sistema hace TODA la magia:
- ✅ Encuentra tus canciones nuevas en Downloads/Desktop
- ✅ Las copia al vault local (`~/Desktop/BlackMamba_Music_Vault`)
- ✅ Detecta y extrae las letras (de .txt o metadatos)
- ✅ Agrega la canción a `music_library.json` con todos los datos
- ✅ Genera fingerprint acústico para el detector
- ✅ Sincroniza todo al USB (si está conectado)

### 4. Resultado
Tu canción está:
- 📁 En el vault local organizado
- 📚 En el índice de la biblioteca
- 🔍 Reconocible por el detector de audio
- 💾 Respaldada en el USB
- 📝 Con las letras extraídas

**Todo en menos de 30 segundos por canción.**

---

## Carpetas y Archivos

### Carpetas escaneadas (automáticamente)
```
~/Downloads/                    # Donde Suno descarga por defecto
~/Music/Suno/                   # Si configuraste esta carpeta
~/Desktop/                      # Descargas alternativas
```

### Carpetas de destino
```
~/Desktop/BlackMamba_Music_Vault/
├── MP3/                        # Todos los MP3
├── WAV/                        # Todos los WAV
└── Lyrics/                     # Todas las letras (.txt)
```

### USB (auto-sincronización si está conectado)
```
/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/
├── MP3/
├── WAV/
└── Lyrics/
```

### Archivos generados/actualizados
```
music_library.json              # Índice maestro actualizado
audio_fingerprints.json         # Fingerprints para detector
suno_pipeline.log              # Log completo del proceso
```

---

## Detección de Canciones Nuevas

El pipeline detecta canciones de Suno mediante:

### 1. Patrones de nombre de archivo
- `Cancion (Intro).mp3` - Formato con paréntesis
- `Cancion-Version.mp3` - Formato con guión
- `Cancion_v2.mp3` - Versiones numeradas

### 2. Archivos recientes
- Cualquier MP3/WAV descargado en las últimas 24 horas

### 3. Verificación de duplicados
- Calcula hash MD5 de cada archivo
- Solo procesa canciones que NO estén en la biblioteca

---

## Extracción de Letras

El sistema intenta 3 métodos automáticamente:

### Método 1: Archivo .txt con el mismo nombre
```
Mi_Cancion.mp3
Mi_Cancion.txt  ← Busca este archivo
```

### Método 2: Archivo .txt reciente en la misma carpeta
- Si descargaste las letras en la última hora
- El sistema las encuentra automáticamente

### Método 3: Metadatos del audio
- Extrae letras de tags ID3
- Busca en: `lyrics`, `LYRICS`, `unsyncedlyrics`

**Si encuentra letras por cualquier método, las guarda automáticamente.**

---

## Integración con Otros Sistemas

### BlackMamba Audio Detector
- Genera fingerprint acústico automáticamente
- La canción es reconocible inmediatamente
- No necesitas indexar manualmente

### Music Library Scanner
- Actualiza `music_library.json` con metadata completa
- Incluye: título, artista, fuente, hash, fecha, rutas

### USB Sync
- Sincronización bidireccional automática
- Respaldo seguro de toda tu producción

### Lyric Mentor
- Las letras extraídas alimentan el análisis de estilo
- Mejora las sugerencias del mentor

---

## Configuración Avanzada

### Agregar carpetas de escaneo
Edita `suno_autopipeline.py`:
```python
SUNO_DOWNLOAD_PATHS = [
    Path.home() / "Downloads",
    Path.home() / "Music/Suno",
    Path.home() / "Desktop",
    Path.home() / "TU_CARPETA_AQUI"  # Agrega la tuya
]
```

### Cambiar ruta del USB
```python
USB_PATHS = [
    Path("/Volumes/TU_USB/ruta"),
    Path("/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA"),
]
```

### Patrones personalizados
```python
SUNO_PATTERNS = [
    r'.*\(.*\)\.mp3$',
    r'TU_PATRON_AQUI',
]
```

---

## Automatización Total

### Opción 1: Ejecutar al inicio del día
Agrega a tu rutina matutina:
```bash
cd ~/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE
bash start_suno_autopipeline.sh
```

### Opción 2: Cron job (cada hora)
```bash
crontab -e
```
Agrega:
```
0 * * * * cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE && /Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 suno_autopipeline.py
```

### Opción 3: Watch folder (avanzado)
Usar `fswatch` para ejecutar automáticamente cuando detecte nuevos archivos en Downloads.

---

## Logs y Diagnóstico

### Ver log completo
```bash
tail -f suno_pipeline.log
```

### Ver últimas 50 líneas
```bash
tail -n 50 suno_pipeline.log
```

### Buscar errores
```bash
grep ERROR suno_pipeline.log
```

---

## Troubleshooting

### "No hay canciones nuevas que procesar"
✅ **Normal** - Significa que todas tus canciones ya están procesadas

### "USB no detectado"
⚠️ **No crítico** - El proceso continúa sin sincronizar al USB
- Conecta el USB y vuelve a ejecutar
- O sincroniza manualmente después

### "Letras no encontradas"
⚠️ **No crítico** - La canción se procesa igual
- Agrega las letras manualmente a `~/Desktop/BlackMamba_Music_Vault/Lyrics/`
- Nombra el archivo: `nombre_cancion.txt`

### "Error generando fingerprint"
⚠️ **Requiere chromaprint instalado**
```bash
brew install chromaprint
```

---

## Ejemplos de Uso Real

### Escenario 1: Acabas de terminar 3 canciones en Suno
```bash
# Descargas: Mi_Trap.mp3, Mi_Trap.wav, Mi_Trap.txt
# Descargas: Reggae_Vibes.mp3, Reggae_Vibes.wav, Reggae_Vibes.txt
# Descargas: Salsa_King.mp3

bash start_suno_autopipeline.sh

# Output:
# 🔍 Escaneando carpetas de descarga...
# ✅ Encontradas 3 canciones nuevas
# 
# 🎵 PROCESANDO: mi_trap
# 📦 Copiando 'mi_trap'...
#   ✅ MP3 -> Mi_Trap.mp3
#   ✅ WAV -> Mi_Trap.wav
# 📝 Extrayendo letras de 'mi_trap'...
#   ✅ Letras encontradas en .txt
#   ✅ Agregada a biblioteca: Mi Trap
#   ✅ Fingerprint generado
#   ✅ USB sync: MP3
#   ✅ USB sync: WAV
#   ✅ USB sync: Lyrics
# ✅ COMPLETADO: Mi Trap
# 
# [Repite para las otras 2 canciones...]
# 
# 🎉 PIPELINE COMPLETADO
# 📊 Canciones procesadas: 3
```

### Escenario 2: Solo tienes MP3 sin WAV
✅ **No hay problema** - El pipeline procesa lo que tengas

### Escenario 3: Letras no vienen en .txt
✅ **El sistema intenta extraerlas de metadatos automáticamente**

---

## Filosofía del Pipeline

> **"La creatividad no debe detenerse por tareas administrativas."**

Este pipeline libera al Arquitecto de:
- ❌ Copiar archivos manualmente
- ❌ Renombrar y organizar
- ❌ Actualizar índices
- ❌ Recordar sincronizar al USB
- ❌ Generar fingerprints
- ❌ Copiar letras

Para que pueda enfocarse en:
- ✅ **CREAR MÚSICA**
- ✅ **EXPERIMENTAR**
- ✅ **PRODUCIR**

---

## Roadmap

- [ ] Integración directa con API de Suno (descarga automática)
- [ ] Detección de género musical automática (ML)
- [ ] Generación de artwork automático
- [ ] Publicación automática a SoundCloud
- [ ] Análisis de calidad de audio (bitrate, sample rate)
- [ ] Sugerencias de mezcla/masterización

---

## Mantenimiento

### Limpiar logs antiguos
```bash
rm suno_pipeline.log
```

### Reindexar todo
```bash
python3 scan_music_library.py
```

### Verificar integridad de biblioteca
```bash
python3 music_quality_analyzer.py
```

---

**🦅 "El sistema trabaja para el Rey. El Rey crea sin interrupciones."**

*Arquitecto: Iyari Cancino Gomez*  
*Sistema: XarvisCore - Dominio 10_CULTURAL_RENAISSANCE*
