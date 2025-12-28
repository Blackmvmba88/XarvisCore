# Xarvis Core: Instrucciones para Agentes de IA

## Filosofía del Proyecto
XarvisCore es una **arquitectura de sistema soberano** construida sobre principios de autogobierno, custodia y toma de decisiones racional. El código implementa una infraestructura modular basada en "dominios" donde servicios independientes se orquestan en un todo unificado. Cada módulo refleja un compromiso filosófico con la transparencia, el honor y la resiliencia sistémica.

**Arquitecto**: Iyari Cancino Gomez  
**Total Líneas de Código**: 40,000+  
**Proyectos Integrados**: 25+ (ver [BLACKMAMBA_ARSENAL.md](../BLACKMAMBA_ARSENAL.md) para 107 repositorios)

Consulta [../0_SOVEREIGN_MANIFESTO/The_Long_Manifesto.md](../0_SOVEREIGN_MANIFESTO/The_Long_Manifesto.md) y [../README.md](../README.md) para la visión fundacional del proyecto.

## Arquitectura General

### Estructura de Dominios (Directorios Numerados)
- **0_SOVEREIGN_MANIFESTO/**: Fundamento filosófico - define el "por qué" de este sistema
- **1_CORE/**: Aplicación Flask central (puerto 5050) - autenticación, dashboard, integraciones de protocolos, sistema Hermes (RAG con Ollama)
- **2_GUARDIANS/**: Certificados de seguridad (SSL/TLS) en `xarvis_certificados/`, Secure SSH Vault (backend/frontend)
- **3_POWER/**: API de monitoreo del sistema (puerto 8080) - CPU, RAM, disco, escaneo de red vía Flask, RAM Guardian
- **4_INTERFACE/**: Múltiples implementaciones de UI (dashboards, GUIs) - frecuentemente duplicados para iteración
- **5_INFRA/**: Scripts de despliegue, logs, instaladores y materiales de activación
- **6_WORLD_DATA/**: Repositorio de información global
- **7_EDUCATION_SYSTEM/**: BlackMamba University (BMU), Alexandria Engine, Atlas de 30+ certificaciones
- **8_RESOURCE_MGMT/**: Protocolo Hambre Cero, gestión de recursos vitales
- **9_POLITICAL_FOUNDATION/**: Diplomacia soberana, principios de fronteras líquidas
- **10_CULTURAL_RENAISSANCE/**: Golden Opportunity Music, Suite Suno completa (afinador, organizador), 280+ producciones
- **11_UNIVERSAL_SECURITY/**: Plenitude Engine, estándar de dignidad (4 carritos)
- **12_SOVEREIGN_FINANCE/**: Snowball Engine, algoritmo de micromovimientos
- **13_DIGITAL_GOVERNANCE/**: Identidad soberana (X-ID), ciudadanía digital
- **14_CREATIVE_TOOLS/**: Arsenal creativo (3milpixeles, BlackMamba YTDLP, Audio 3D Lab, Metacraft, YTDLP-Web)
- **15_ESCRIBA/** y **15_TRANSCRIPTION_ENGINE/**: Motor de transcripción con SQLite, CI/CD
- **16_AGRICULTURE/**: Sistema hidropónico de fresas, integración con Gaia
- **17_AI_EXPERIMENTS/**: Quantum Audio Player, ASCII Skull Visualizer (React+TypeScript, 50+ componentes)
- **18_BLACKMAMBA_STATION/**: Centro de comando con Hydra Server, auto-optimización, extracción masiva

### Orquestación de Procesos
El [xarvis_supervisor.py](../xarvis_supervisor.py) actúa como el **Orquestador Maestro de Infraestructura**:
- Gestiona el ciclo de vida de procesos para CORE (puerto 5050), POWER (puerto 8080) y RAM_GUARDIAN
- Auto-recuperación: monitorea cada 15 segundos, reinicia servicios caídos
- Usa `preexec_fn=os.setsid` para gestión de grupos de procesos
- Registra logs en `5_INFRA/logs/{master,core,full_power,ram_guardian}.log`
- Sistema de prioridades: CORE (1), POWER/RAM (2), STATION (3)
- Soporte para procesos extendidos opcionales (STATION_COMMAND)

**Crítico**: Siempre ejecuta los módulos desde su directorio padre mediante `cwd=os.path.dirname(config["path"])` para asegurar que las importaciones relativas funcionen.

## Flujos de Trabajo de Desarrollo

### Iniciar el Sistema
```bash
# Opción 1: Supervisor (recomendado para producción)
python3 xarvis_supervisor.py

# Opción 2: Manual (desarrollo)
cd 1_CORE && python3 xarvis_core.py  # Puerto 5050
cd 3_POWER && python3 xarvis_full_power.py  # Puerto 8080
cd 3_POWER && python3 ram_guardian.py  # Guardián de RAM

# Opción 3: Scripts de infraestructura
bash 5_INFRA/start_xarvis.sh  # Lanzador completo
bash 5_INFRA/validate_system.sh  # Validación pre-despliegue
```

### Configuración e Instalación
Ejecuta [../5_INFRA/setup_xarvis.sh](../5_INFRA/setup_xarvis.sh) primero en máquinas nuevas:
- Instala: brew, python3, docker, jq, htop
- Crea LaunchAgent `com.xarvis.autocheck` para monitoreo de salud del sistema
- Configura script de auto-chequeo que valida Docker, red y servicios

### Archivos de Configuración
- **BASE_DIR hardcodeado**: `/Users/blackmamba/Desktop/XarvisCore` aparece en supervisor y módulos core
- **Certificados**: Se esperan en `2_GUARDIANS/xarvis_certificados/{cert.pem, key.pem}`
- **Entorno**: Usa archivos `.env` con `SECRET_KEY`, `USERNAME`, `PASSWORD` (por defecto: BlackSekhmet/Admin123)
- **Config JSONs**: Configuraciones mínimas en `1_CORE/config.json` y `3_POWER/config.json`

### Dependencias
Los servicios core requieren dependencias mínimas:
```
flask
flask-cors
psutil
python-dotenv
```

**Gestión de Entorno Virtual**:
```bash
# Crear venv (primera vez)
python3 -m venv venv

# Activar venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Convenciones Específicas del Proyecto

### Filosofía de Nombres
- **Prefijo "Sovereign"**: Indica componentes autónomos y autogobernados
- **Módulos de protocolo**: Terminan en `_protocol.py` (ej., `gaia_protocol.py`, `oracle_protocol.py`)
- **Módulos de motor**: Terminan en `_engine.py` (ej., `plenitude_engine.py`, `snowball_engine.py`)
- **Mezcla Español/Inglés**: Nombres de módulos en inglés, UI/logs frecuentemente bilingües

### Estilo de Código
- **Instancias de clase simples**: Los protocolos crean singletons globales (`gaia = GaiaProtocol()`)
- **APIs minimalistas**: Las rutas Flask retornan JSON estructurado con campos status/description
- **UI Glassmorphism**: Temas oscuros con `--primary: #00ff41`, estética cyberpunk/Matrix
- **HTML inline**: El dashboard core usa `render_template_string()` con CSS embebido

### Patrón de Protocolo
Los módulos de dominio (7-13) siguen esta estructura:
```python
class ProtocolName:
    def __init__(self):
        self.philosophy = "Principio fundamental"
        self.status = "Operational"
    
    def get_status_or_data(self):
        return {
            "pillar_1": {"nombre": "...", "estado": "...", "descripcion": "..."},
            "timestamp": datetime.datetime.now().isoformat()
        }

# Instancia global para integración
protocol_instance = ProtocolName()
```

## Puntos de Integración Clave

### Comunicación CORE ↔ POWER
- El dashboard Core (`1_CORE/xarvis_core.py`) obtiene estadísticas de `http://localhost:8080/estado`
- JavaScript hace polling cada 2 segundos: función `updateStats()`
- CORS habilitado en ambos servicios para peticiones cross-origin

### Carga de Protocolos
Core puede importar protocolos dinámicamente:
```python
from gaia_protocol import gaia
from oracle_protocol import oracle
# Usa gaia.get_stewardship_brief(), oracle.assess_intent(), etc.
```

### Gestión del Supervisor
Agrega nuevos servicios al supervisor extendiendo el dict `PROCESSES`:
```python
"NEW_SERVICE": {
    "path": os.path.join(BASE_DIR, "X_DOMAIN/service.py"),
    "log": os.path.join(LOG_DIR, "service.log"),
    "proc": None,
    "priority": 2  # 1=máxima, 3=baja
}
```

### Sistema RAM Guardian
El RAM Guardian (`3_POWER/ram_guardian.py`) protege el sistema de sobrecarga de memoria:
- Monitoreo continuo cada 10 segundos
- Umbrales: Warning (75%), Critical (85%), Optimal (60%)
- Procesos protegidos: núcleo Xarvis, kernel, servicios del sistema
- Cierre inteligente de procesos de baja prioridad (Chrome Helper, Slack, etc.)
- Logging detallado de intervenciones y memoria liberada

## Dominios Especializados (14-18)

### 14_CREATIVE_TOOLS: Arsenal Creativo
Suite completa de herramientas para producción multimedia:
- **3milpixeles**: Redimensionador profesional de imágenes
- **BlackMamba YTDLP**: Suite de descarga (WebUI, TUI, CLI) con gestión de historial
- **Audio 3D Lab**: Laboratorio de audio espacial con backends Open3D, PyQtGraph, VTK
- **Metacraft**: Herramienta de metacreación
- **YTDLP-Web**: Interfaz web con pitch shifting

### 15_ESCRIBA/TRANSCRIPTION_ENGINE: Motor de Transcripción
Sistema completo de transcripción con base de datos SQLite:
- Pipeline de captura → procesamiento → refinamiento → exportación
- Detección de idioma y clasificación automática
- Tests completos y CI/CD con GitHub Actions
- Protocolo: `escriba_protocol.py` con filosofía "Preservar cada palabra con honor"

### 16_AGRICULTURE: Agricultura Inteligente
Sistema de cultivo hidropónico de fresas con integración Gaia:
- Motor agrícola para seguimiento de cultivos
- Plan de expansión con sensores virtuales
- Conexión directa con el Protocolo Gaia para custodia ambiental

### 17_AI_EXPERIMENTS: Laboratorio de IA
Experimentos avanzados de IA y visualización:
- **Quantum Audio Player**: Reproductor con procesamiento cuántico (macOS/Raspberry Pi)
- **ASCII Skull Visualizer**: 50+ componentes React+TypeScript, detección facial, análisis de audio en tiempo real

### 18_BLACKMAMBA_STATION: Centro de Comando
Centro de comando operacional con orquestación completa:
- Hydra Server para gestión distribuida
- Auto-optimización de recursos
- Sistema de backups automáticos
- Integración directa con CORE y POWER
- Launchers y scripts de automatización masiva

## Errores Comunes

1. **Supuestos de rutas**: El código asume rutas macOS (`/Users/blackmamba/Desktop/XarvisCore`) - ajusta BASE_DIR para portabilidad
2. **Conflictos de puerto**: Puertos hardcodeados (5050, 8080, 8000) - verifica disponibilidad antes de iniciar
3. **Certificados faltantes**: La configuración SSL requiere certificados en `2_GUARDIANS/` - el sistema usa HTTP como fallback si faltan
4. **Directorios duplicados**: `4_INTERFACE/` tiene muchas carpetas duplicadas (variaciones XARVIS-ULTRA, XARVIS-SEKHMET) - el trabajo más reciente probablemente está en versiones sin número
5. **Entorno virtual**: El código asume que existe `venv/` en la raíz del proyecto - crea con `python3 -m venv venv`

## Pruebas y Depuración

### Chequeo de Salud
```bash
# Chequeo manual del sistema
bash 5_INFRA/scripts/xarvis_checkup.sh

# Verificar procesos en ejecución
lsof -i :5050,8080

# Ver logs
tail -f 5_INFRA/logs/{master,core,full_power}.log
```

### Estado del Roadmap
Rastrea el progreso de implementación en [../EpicRoadmap.md](../EpicRoadmap.md) - usa sintaxis de checkbox `[x]` para fases completadas.

## Reglas de Organización de Archivos

- **Un interés por módulo**: Cada protocolo/motor maneja un solo dominio (educación, finanzas, diplomacia)
- **Infraestructura centralizada**: Todo despliegue/configuración en `5_INFRA/`
- **Iteración UI mediante duplicación**: La carpeta interface tiene copias versionadas - no borrar, documentan la evolución
- **Logs separados del código**: Nunca escribir logs en directorios de módulos, usar `5_INFRA/logs/`

## Al Hacer Cambios

1. **Actualiza el Roadmap**: Marca las fases relacionadas como completas en `EpicRoadmap.md`
2. **Preserva la Filosofía**: Verifica alineación con los principios del manifiesto antes de cambios arquitectónicos
3. **Prueba Auto-Recuperación**: Mata procesos para verificar que el supervisor los reinicie
4. **Actualiza el Supervisor**: Si agregas módulos que necesitan orquestación, regístralos en `PROCESSES`
5. **Mantén el Contexto Bilingüe**: Conserva términos filosóficos en español, términos técnicos en inglés

## Arsenal Extendido de BlackMamba

### Ecosistema de 107 Repositorios
El archivo [BLACKMAMBA_ARSENAL.md](../BLACKMAMBA_ARSENAL.md) cataloga el arsenal completo del Arquitecto:
- **Simulación & Gaming**: Avion (simulador vuelo), Rockhero (MambaHero musical), HonorHero (ritmo consciente), vuelo (simulador cuántico)
- **Producción Musical**: reproductornuevo, rainvow (db meter), Iyari-ear, winampGera
- **IA & Experimentación**: InteligenciaArtificial. (framework IA ligera), -ElFuegoDelConocimientoReal (grimorio alquímico-masónico)
- **Herramientas Web**: Múltiples proyectos TypeScript/JavaScript con estética cyberpunk
- **Data Science**: Proyectos de análisis y visualización

### Integración con XarvisCore
Algunos repositorios del arsenal están integrados como subdominios:
- `14_CREATIVE_TOOLS/`: Herramientas multimedia (3milpixeles, blackmamba-ytdlp, audio-3d-lab)
- `10_CULTURAL_RENAISSANCE/suno-suite/`: Suite completa de producción musical
- `17_AI_EXPERIMENTS/`: Quantum Audio Player, ASCII Skull Visualizer

## Patrones de Arquitectura Avanzados

### Sistema de Protocolos y Motores
Cada dominio implementa uno de estos patrones:

**Protocolo** (`*_protocol.py`): Representa un compromiso filosófico con estado operacional
```python
class ProtocoloEjemplo:
    def __init__(self):
        self.directive = "Razón de ser del protocolo"
        self.status = "Activo"
    
    def get_status_data(self):
        return {
            "pilar_N": {
                "nombre": "Nombre del Pilar",
                "estado": "Operativo|Cimentación|Analizando",
                "descripcion": "Explicación del compromiso"
            },
            "timestamp": datetime.datetime.now().isoformat()
        }

# Singleton global
protocolo = ProtocoloEjemplo()
```

**Motor** (`*_engine.py`): Sistema ejecutable con lógica de procesamiento
- Operan sobre datos y recursos
- Implementan algoritmos específicos (Snowball, Plenitude, etc.)
- Pueden tener estado persistente (SQLite, archivos config)

**Detector** (`*_detector.py`): Sistema de reconocimiento mediante fingerprinting
- Genera huellas digitales acústicas (chromaprint)
- Compara audio grabado vs. base de datos indexada
- Funciona offline sin depender de APIs externas
- Ejemplo: `audio_detector.py` para reconocer canciones de SoundCloud

### Estética de UI Consistente
Todos los dashboards siguen el tema Matrix/Cyberpunk:
```css
:root {
    --primary: #00ff41;      /* Verde Matrix */
    --bg: #0a0a0a;           /* Fondo oscuro */
    --glass: rgba(20, 20, 20, 0.8);  /* Glassmorphism */
    --border: rgba(0, 255, 65, 0.3); /* Bordes neón */
}
```
- Fuente: `'Inter', 'Courier New', monospace`
- Efectos: `text-shadow: 0 0 10px var(--primary)`, `backdrop-filter: blur(10px)`
- Layouts: Grid responsivo con `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`

## Sistema de Detección de Audio (BlackMamba Audio Detector)

### Arquitectura del Detector
El BlackMamba Audio Detector es un sistema soberano de reconocimiento musical que no depende de Shazam ni APIs externas:

**Componentes principales**:
1. **audio_detector.py**: Motor de fingerprinting standalone
   - `AudioFingerprinter`: Genera y compara huellas acústicas
   - `AudioRecorder`: Captura audio del sistema (macOS con SoX)
   - Base de datos: `audio_fingerprints.json`

2. **vpa_with_detector.py**: Integración VPA + Detector
   - Hereda de `VocalPerformanceAnalyzer`
   - Método `detect_song_dual()`: Shazam primero, luego BlackMamba
   - Método `detect_song_blackmamba()`: Solo detector propio
   - API Flask en puerto 9001

3. **vocal_performance_analyzer.py**: VPA original
   - Análisis vocal en tiempo real
   - Obtención de letras (Lyrics.ovh API)
   - Métricas de afinación y timing
   - Lee `music_library.json` (194 canciones)

### Tecnología: Chromaprint Fingerprinting
```bash
# Herramientas del sistema requeridas
brew install chromaprint sox

# Dependencias Python
pip install numpy flask flask-cors requests
```

**Proceso de indexación**:
```python
# Generar fingerprint de una canción
fingerprinter = AudioFingerprinter()
duration, fingerprint = fingerprinter.generate_fingerprint('/path/to/song.mp3')
# fingerprint = "123,456,789,..." (array de ints como string)
```

**Proceso de detección**:
```python
# 1. Grabar audio del sistema (10 segundos)
recorder = AudioRecorder()
recording = recorder.record_system_audio_macos(10)

# 2. Generar fingerprint de la grabación
_, rec_fp = fingerprinter.generate_fingerprint(recording)

# 3. Comparar con base de datos (sliding window)
for song_fp in database:
    similarity = compare_fingerprints(rec_fp, song_fp)
    # similarity: 0.0 - 1.0 (threshold: 0.60)
```

### Algoritmo de Matching
```python
def compare_fingerprints(fp1, fp2, threshold=0.60):
    """
    Compara dos fingerprints usando sliding window.
    - Window size: 100 frames
    - Offset range: ±20 frames (tolerancia temporal)
    - Retorna: similitud (0.0 - 1.0)
    """
    arr1 = [int(x) for x in fp1.split(',')]
    arr2 = [int(x) for x in fp2.split(',')]
    
    max_similarity = 0
    for offset in range(-20, 21):
        matches = 0
        comparisons = 0
        for i in range(min(100, len(arr1))):
            idx2 = i + offset
            if 0 <= idx2 < len(arr2):
                comparisons += 1
                if arr1[i] == arr2[idx2]:
                    matches += 1
        if comparisons > 0:
            similarity = matches / comparisons
            max_similarity = max(max_similarity, similarity)
    
    return max_similarity
```

### Flujo de Trabajo del Detector

**1. Setup inicial**:
```bash
cd 10_CULTURAL_RENAISSANCE
./setup_audio_detector.sh  # Instala chromaprint + sox
```

**2. Indexar biblioteca**:
```bash
python3 audio_detector.py --index --library music_library.json
# Genera audio_fingerprints.json con 194 canciones
```

**3. Detectar canción (standalone)**:
```bash
python3 audio_detector.py --detect 10
# Graba 10 seg, compara y muestra resultado
```

**4. Servidor integrado con VPA**:
```bash
./start_vpa_detector.sh
# Puerto 9001 con API completa
```

### API Endpoints del Detector
```
POST /api/detect/dual
  Body: {"duration": 10}
  → Intenta Shazam primero, si falla usa BlackMamba
  Response: {
    "detected": true,
    "method": "shazam|blackmamba",
    "song": {"title": "...", "artist": "...", "file_path": "..."},
    "confidence": 0.85
  }

POST /api/detect/blackmamba
  Body: {"duration": 10}
  → Solo usa BlackMamba detector
  
POST /api/index
  → Indexa biblioteca completa con fingerprints
  
GET /api/detector/status
  → Estado del detector
  Response: {
    "indexed_songs": 194,
    "library_songs": 194,
    "method": "chromaprint_fingerprinting"
  }
```

### Estructura de Archivos del Detector
```
10_CULTURAL_RENAISSANCE/
├── audio_detector.py               # Motor fingerprinting
├── vpa_with_detector.py            # VPA + Detector integrado
├── vocal_performance_analyzer.py   # VPA original
├── music_library.json              # Índice unificado (scan_music_library.py)
├── audio_fingerprints.json         # Base de fingerprints
├── music_orphans_report.json       # Reporte MP3/WAV huérfanos
├── setup_audio_detector.sh         # Setup automático
├── start_vpa_detector.sh           # Launcher servidor
├── BLACKMAMBA_AUDIO_DETECTOR.md    # Documentación completa
├── DETECTOR_STATUS.txt             # Status visual
└── audio_recordings/               # Grabaciones temporales
```

### Casos de Uso del Detector

**1. Canciones de SoundCloud**:
```python
# Problema: Shazam no reconoce canciones solo en SoundCloud
# Solución: BlackMamba Detector las reconoce por fingerprint local

vpa = VPAWithDetector()
result = vpa.detect_song_blackmamba(duration=10)
# ✅ Detecta cualquier canción de los 280+ tracks de BlackMamba RECORDS
```

**2. Detección Dual (mejor opción)**:
```python
# Usa Shazam para mainstream, BlackMamba para local
result = vpa.detect_song_dual(duration=10)
# method: "shazam" (rápido) o "blackmamba" (completo)
```

**3. Análisis Vocal Completo**:
```python
# 1. Detecta canción (dual)
result = vpa.detect_song_dual()

# 2. Obtiene letras
lyrics = vpa.fetch_lyrics(result['song']['title'], result['song']['artist'])

# 3. Analiza tu canto
metrics = vpa.analyze_vocal_pitch(audio_path)
# pitch_accuracy, timing_accuracy, etc.
```

### Filosofía del Detector
> **"Shazam reconoce Spotify, nosotros reconocemos SoundCloud."**

- **Soberanía Tecnológica**: No dependemos de APIs de terceros
- **Custodia del Arte**: Cada canción tiene su huella única
- **Honor al Proceso**: Reconocemos nuestra propia creación
- **Offline First**: Funciona sin internet una vez indexado

### Performance y Benchmarks
- **Indexación**: ~3-4 seg/canción (Mac Mini M1)
- **Detección**: ~2-3 seg (incluyendo grabación de 10s)
- **Precisión**:
  - Audio limpio: 95%+
  - Con ruido moderado: 85%+
  - Con conversación de fondo: 70%+
- **Tamaño fingerprint**: ~5-10 KB por canción
- **Base de datos**: JSON (194 canciones = ~1-2 MB)

### Limitaciones y Roadmap
**Actual**:
- Solo macOS (uso de `rec` de SoX)
- Requiere audio del sistema (BlackHole o Multi-Output Device)
- Comparación básica de fingerprints (puede optimizarse)

**Futuro**:
- [ ] Soporte Linux/Windows
- [ ] UI para visualizar fingerprints
- [ ] Detección en streaming (chunks de 3s)
- [ ] Integración con Afinador Suno para análisis F0
- [ ] Export a MusicBrainz/AcousticID
- [ ] Cache de fingerprints en memoria (RAM)
- [ ] Algoritmo de matching optimizado (Cython/Numba)

## Documentación de Referencia
- Certificaciones del Arquitecto: https://www.linkedin.com/in/iyari-c/details/certifications/
- Catálogo musical: https://soundcloud.com/iyari-c/tracks (280+ producciones)
- Arsenal completo: Ver [BLACKMAMBA_ARSENAL.md](../BLACKMAMBA_ARSENAL.md) para los 107 repositorios
