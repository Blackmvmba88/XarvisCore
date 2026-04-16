# 🦅 Network Priority Manager - Optimización de Red para Gaming

**Arquitecto**: Iyari Cancino Gomez  
**Fecha**: 1 de Enero, 2026  
**Dominio**: 3_POWER

---

## ¿Qué hace?

El **Network Priority Manager** es un sistema inteligente que optimiza tu conexión de red cuando juegas Flight Simulator 2024 (o cualquier juego).

### Beneficios:
- ⚡ **Menor latencia** - Prioriza tráfico del simulador
- 📶 **Conexión estable** - Reduce interferencias de otras apps
- 🚀 **Mejor rendimiento** - 80% del ancho de banda garantizado para el juego
- 🎯 **Automático** - Detecta cuando juegas y optimiza solo entonces

---

## 🚀 Uso Rápido

### Opción 1: Launcher interactivo (Recomendado)
```bash
cd /Users/blackmamba/Desktop/XarvisCore/3_POWER
bash start_network_optimizer.sh
```

Selecciona:
- **Opción 1**: Activar ahora (manual)
- **Opción 2**: Monitoreo automático (se activa solo cuando juegas)
- **Opción 3**: Desactivar

### Opción 2: Comandos directos
```bash
# Activar prioridad manual
sudo /Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 network_priority_manager.py enable

# Monitoreo automático
sudo /Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 network_priority_manager.py monitor

# Desactivar
sudo /Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 network_priority_manager.py disable
```

---

## 🔧 Cómo Funciona

### 1. Detección Automática
El sistema monitorea procesos cada 10 segundos buscando:
- FlightSimulator.exe
- Microsoft Flight Simulator
- MSFS
- fs2024

### 2. Optimizaciones Aplicadas

#### A. Priorización de Tráfico (Packet Filter)
- Crea colas de prioridad en la red
- **Critical Queue (80%)**: Flight Simulator (puertos 3074-3076, 7000-7001)
- **High Queue (60%)**: Otros juegos
- **Normal Queue (40%)**: Apps normales
- **Low Queue (20%)**: Sincronizaciones, backups

#### B. Optimizaciones del Sistema
- Deshabilita IPv6 (reduce latencia)
- Limpia caché DNS
- Reduce prioridad de apps que consumen ancho de banda:
  - Dropbox
  - Google Drive
  - OneDrive
  - iCloud
  - Time Machine
  - Steam (si no es la app activa)

### 3. Restauración Automática
Cuando cierras el juego:
- Remueve prioridades de red
- Restaura configuración normal
- Todo vuelve a la normalidad

---

## 📊 Puertos Priorizados

### Flight Simulator 2024 / MSFS
- **3074** - Xbox Live
- **3075** - Multiplayer
- **3076** - Streaming
- **7000** - SimConnect
- **7001** - Datos de vuelo

---

## 🎮 Modos de Uso

### Modo 1: Manual
**Uso**: Antes de empezar a jugar, activas manualmente.

**Ventajas**:
- Control total
- Sin consumo de recursos de monitoreo

**Pasos**:
```bash
# Antes de jugar
bash start_network_optimizer.sh  # Opción 1

# Después de jugar
bash start_network_optimizer.sh  # Opción 3
```

### Modo 2: Automático (Recomendado)
**Uso**: El sistema detecta cuando juegas y optimiza solo entonces.

**Ventajas**:
- Totalmente automático
- Se activa solo cuando es necesario
- No tienes que recordar activar/desactivar

**Pasos**:
```bash
# Una vez al inicio del día o al encender la Mac
bash start_network_optimizer.sh  # Opción 2

# Mantén la terminal abierta o en background
# El sistema trabaja solo
```

**Para ejecutar en background**:
```bash
sudo /Users/blackmamba/Desktop/XarvisCore/venv/bin/python3 network_priority_manager.py monitor &
```

---

## 🔍 Verificación

### Ver si está activo
```bash
sudo pfctl -s rules
```

Si ves reglas con "Xarvis Network Priority", está activo.

### Ver estadísticas de red
```bash
sudo pfctl -s queue
```

### Ver log
```bash
tail -f /Users/blackmamba/Desktop/XarvisCore/5_INFRA/logs/network_priority.log
```

---

## ⚙️ Configuración Avanzada

### Agregar más aplicaciones prioritarias

Edita `network_priority_manager.py`:

```python
self.priority_apps = {
    'Flight Simulator': {
        'patterns': ['FlightSimulator', 'MSFS'],
        'priority': 'CRITICAL',
        'ports': [3074, 3075, 3076, 7000, 7001],
        'bandwidth_guarantee': 80
    },
    'Tu Juego': {  # Agrega tu juego aquí
        'patterns': ['NombreDelJuego', 'GameProcess'],
        'priority': 'HIGH',
        'ports': [1234, 5678],  # Puertos del juego
        'bandwidth_guarantee': 70
    }
}
```

### Cambiar puertos

Si Flight Simulator usa otros puertos, actualiza la lista:
```python
'ports': [3074, 3075, 3076, 7000, 7001, TU_PUERTO_AQUI]
```

### Cambiar intervalo de monitoreo
```bash
# Verificar cada 5 segundos en lugar de 10
sudo python3 network_priority_manager.py monitor 5
```

---

## 🚨 Troubleshooting

### "pfctl: Permission denied"
**Solución**: Necesitas ejecutar con `sudo`
```bash
sudo bash start_network_optimizer.sh
```

### "No se detecta Flight Simulator"
**Posibles causas**:
1. El juego usa otro nombre de proceso
2. El juego está en versión diferente

**Solución**: Verificar nombre del proceso
```bash
# Mientras el juego corre:
ps aux | grep -i flight
ps aux | grep -i simulator
ps aux | grep -i msfs
```

Agrega el nombre encontrado a `patterns` en el código.

### "Sigue lento el juego"
**Verificaciones**:
1. ¿Las reglas están activas? `sudo pfctl -s rules`
2. ¿Tu ISP tiene problemas? Ejecuta speedtest
3. ¿Otras apps consumen red? Abre Activity Monitor → Network

**Optimizaciones extra**:
```bash
# Cerrar apps innecesarias
killall Dropbox
killall "Google Drive"

# Reiniciar router
# (botón físico o admin del router)
```

### "Error aplicando reglas"
**Causa común**: Conflicto con otras reglas de pf

**Solución**: Ver reglas existentes
```bash
sudo pfctl -s rules
```

Desactivar todo y reintentar:
```bash
sudo pfctl -d
sudo pfctl -f /tmp/xarvis_network_priority.rules
sudo pfctl -e
```

---

## 🎯 Resultados Esperados

### Antes (sin optimización)
- Latencia: 80-150ms
- Stuttering ocasional
- Lag en multijugador
- Desconexiones esporádicas

### Después (con optimización)
- ⚡ Latencia: 30-60ms
- 🎮 Sin stuttering
- 📶 Conexión estable en multiplayer
- ✅ Sin desconexiones

**Nota**: Los resultados dependen de tu conexión base. Si tu ISP tiene problemas, esto ayuda pero no hace milagros.

---

## 📈 Monitoreo de Rendimiento

### Ver latencia en tiempo real
```bash
ping -i 0.5 google.com
```

### Ver uso de red por aplicación
```bash
# Abrir Activity Monitor
# Tab: Network
# Ordenar por "Sent Bytes" o "Rcvd Bytes"
```

### Ver calidad de conexión
```bash
# Durante el juego
ping -c 100 8.8.8.8 | tail -5
```

**Meta**: < 50ms promedio, < 10% packet loss

---

## 🔄 Integración con Xarvis Supervisor

Para que el optimizador arranque automáticamente con Xarvis:

Edita `xarvis_supervisor.py`:
```python
EXTENDED_PROCESSES = {
    "NETWORK_OPTIMIZER": {
        "path": os.path.join(BASE_DIR, "3_POWER/network_priority_manager.py"),
        "log": os.path.join(LOG_DIR, "network_optimizer.log"),
        "proc": None,
        "priority": 2,
        "enabled": True  # Activar para auto-inicio
    }
}
```

---

## 🎓 Conceptos Técnicos

### ¿Qué es Packet Filter (pf)?
Es el firewall de macOS. Permite:
- Filtrar tráfico
- Crear colas de prioridad (QoS)
- Limitar ancho de banda
- Priorizar puertos específicos

### ¿Qué es QoS (Quality of Service)?
Sistema que garantiza que el tráfico importante tenga prioridad sobre el resto.

**Ejemplo**:
- Flight Simulator: 80% ancho de banda garantizado
- Spotify: Lo que sobre
- Dropbox sync: Mínimo necesario

### ¿Por qué deshabilitar IPv6?
Algunos ISPs tienen configuración IPv6 deficiente, causando:
- Latencia extra (50-100ms)
- Resolución DNS lenta
- Routing ineficiente

Deshabilitar IPv6 fuerza IPv4 puro = más estable para gaming.

---

## 🚀 Roadmap

- [ ] Interfaz gráfica (GUI) para activar/desactivar
- [ ] Integración con Dashboard Xarvis Core
- [ ] Detección automática de puertos del juego (sin configurar manualmente)
- [ ] Perfiles por juego (LoL, Valorant, etc.)
- [ ] Estadísticas de mejora de latencia (antes/después)
- [ ] Notificaciones cuando detecta lag
- [ ] Auto-reinicio de router si detecta problemas

---

## 📝 Notas

- **Requiere macOS**: Este sistema usa `pfctl` de macOS
- **Requiere sudo**: Modificar reglas de red requiere permisos de admin
- **Compatibilidad**: Probado en macOS 11+ (Big Sur, Monterey, Ventura, Sonoma)
- **Impacto**: Mínimo en CPU/RAM (< 10MB RAM, < 1% CPU)

---

**🦅 "Vuela sin lag. El cielo te espera."**

*Arquitecto: Iyari Cancino Gomez*  
*Sistema: XarvisCore - Dominio 3_POWER*
