# Xarvis Core: Instrucciones para Agentes de IA

## Filosofía del Proyecto
XarvisCore es una **arquitectura de sistema soberano** construida sobre principios de autogobierno, custodia y toma de decisiones racional. El código implementa una infraestructura modular basada en "dominios" donde servicios independientes se orquestan en un todo unificado. Cada módulo refleja un compromiso filosófico con la transparencia, el honor y la resiliencia sistémica.

Consulta [../0_SOVEREIGN_MANIFESTO/The_Long_Manifesto.md](../0_SOVEREIGN_MANIFESTO/The_Long_Manifesto.md) y [../README.md](../README.md) para la visión fundacional del proyecto.

## Arquitectura General

### Estructura de Dominios (Directorios Numerados)
- **0_SOVEREIGN_MANIFESTO/**: Fundamento filosófico - define el "por qué" de este sistema
- **1_CORE/**: Aplicación Flask central (puerto 5050) - autenticación, dashboard, integraciones de protocolos
- **2_GUARDIANS/**: Certificados de seguridad (SSL/TLS) almacenados en `xarvis_certificados/`
- **3_POWER/**: API de monitoreo del sistema (puerto 8080) - CPU, RAM, disco, escaneo de red vía Flask
- **4_INTERFACE/**: Múltiples implementaciones de UI (dashboards, GUIs) - frecuentemente duplicados para iteración
- **5_INFRA/**: Scripts de despliegue, logs, instaladores y materiales de activación
- **6-13/**: Dominios de funcionalidad (Educación, Finanzas, Gobernanza, Cultural, etc.) - módulos de protocolo

### Orquestación de Procesos
El [xarvis_supervisor.py](../xarvis_supervisor.py) actúa como el **Orquestador Maestro de Infraestructura**:
- Gestiona el ciclo de vida de procesos para CORE (puerto 5050) y POWER (puerto 8080)
- Auto-recuperación: monitorea cada 15 segundos, reinicia servicios caídos
- Usa `preexec_fn=os.setsid` para gestión de grupos de procesos
- Registra logs en `5_INFRA/logs/{master,core,full_power}.log`

**Crítico**: Siempre ejecuta los módulos desde su directorio padre mediante `cwd=os.path.dirname(config["path"])` para asegurar que las importaciones relativas funcionen.

## Flujos de Trabajo de Desarrollo

### Iniciar el Sistema
```bash
# Opción 1: Supervisor (recomendado para producción)
python3 xarvis_supervisor.py

# Opción 2: Manual (desarrollo)
cd 1_CORE && python3 xarvis_core.py  # Puerto 5050
cd 3_POWER && python3 xarvis_full_power.py  # Puerto 8080
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
    "proc": None
}
```

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
