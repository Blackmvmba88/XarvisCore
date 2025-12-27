# Xarvis Core: Instrucciones para Agentes de IA

## Filosofía del Proyecto
XarvisCore es una **arquitectura de sistema soberano** construida sobre principios de autogobierno, custodia y toma de decisiones racional. El código implementa una infraestructura modular basada en "dominios" donde servicios independientes se orquestan en un todo unificado. Cada módulo refleja un compromiso filosófico con la transparencia, el honor y la resiliencia sistémica.

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

## Documentación de Referencia
- Certificaciones del Arquitecto: https://www.linkedin.com/in/iyari-c/details/certifications/
- Catálogo musical: https://soundcloud.com/iyari-c/tracks (280+ producciones)
