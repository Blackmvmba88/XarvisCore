# 🛡️ RAM Guardian - Sistema de Gestión Automática de Memoria

## Descripción
RAM Guardian es un sistema autónomo que monitorea y libera memoria automáticamente para evitar que tu Mac se sature y tenga que ser reiniciada. Mantiene el sistema "fit y bien aceitado" cerrando procesos innecesarios cuando la RAM está alta.

## 🎯 Estado Actual del Sistema
```
Total RAM: 8.0 GB
RAM Usada: 3.19 GB (85.2%)
Estado: ⚠️ CRÍTICO
```

**Necesitas RAM Guardian activo!** Tu sistema está en zona crítica.

## ⚙️ Cómo Funciona

### Umbrales de Acción
- **60% o menos** → ✅ Estado ÓPTIMO (sin intervención)
- **60-75%** → 🟢 Estado BUENO (monitoreo pasivo)
- **75-85%** → 🟡 ADVERTENCIA (liberación preventiva)
- **85% o más** → 🔴 CRÍTICO (liberación agresiva)

### Proceso de Liberación
1. Detecta cuando la RAM supera umbrales
2. Identifica procesos de baja prioridad
3. Cierra procesos innecesarios de forma segura
4. Nunca toca procesos protegidos (Xarvis, sistema)
5. Registra toda actividad en logs

## 🚀 Uso

### Iniciar con el Supervisor (Recomendado)
El RAM Guardian se inicia automáticamente con el sistema:
```bash
python3 xarvis_supervisor.py
```

### Iniciar Manualmente (Para pruebas)
```bash
cd 3_POWER
python3 ram_guardian.py
```

### Verificar Estado
```bash
bash 3_POWER/test_ram_guardian.sh
```

## 🔒 Procesos Protegidos
**Estos NUNCA serán cerrados:**
- `xarvis_core.py` - Core del sistema
- `xarvis_full_power.py` - Monitoreo
- `xarvis_supervisor.py` - Orquestador
- `ram_guardian.py` - El guardian mismo
- Procesos del sistema (kernel, WindowServer, etc.)

## 🎯 Procesos Candidatos a Cierre
**Baja prioridad (se cierran cuando hay presión de memoria):**
- Google Chrome Helper
- Slack, Discord, Spotify
- Steam, Epic Games
- Firefox, Safari
- Mail, Calendar, Notes

## ⚙️ Configuración

Edita los umbrales en `3_POWER/ram_guardian.py`:

```python
RAM_THRESHOLD_WARNING = 75   # Advertencia
RAM_THRESHOLD_CRITICAL = 85  # Crítico
RAM_THRESHOLD_OPTIMAL = 60   # Objetivo
CHECK_INTERVAL = 10          # Segundos entre chequeos
```

Agrega procesos protegidos:
```python
PROTECTED_PROCESSES = {
    'tu_app_importante.py',
    'otro_proceso'
}
```

Agrega patrones de baja prioridad:
```python
LOW_PRIORITY_PATTERNS = [
    'nombre_app',
    'otro_patron'
]
```

## 📊 Monitoreo

### Logs en Tiempo Real
```bash
tail -f 5_INFRA/logs/ram_guardian.log
```

### Endpoint API
```bash
curl http://localhost:8080/ram
```

Retorna:
```json
{
  "total_gb": 8.0,
  "used_gb": 3.19,
  "percent": 85.2,
  "status": "CRITICAL",
  "top_processes": [...]
}
```

## 📈 Estadísticas

El guardian rastrea:
- Total de intervenciones realizadas
- Memoria total liberada (MB)
- Procesos cerrados (contador por tipo)
- Historial de liberaciones

Al detener con `Ctrl+C`, muestra resumen completo.

## 🔧 Resolución de Problemas

### El guardian no libera suficiente memoria
- Reduce `RAM_THRESHOLD_OPTIMAL` para objetivo más bajo
- Agrega más patrones a `LOW_PRIORITY_PATTERNS`

### Se cerró un proceso importante
- Agrégalo a `PROTECTED_PROCESSES`
- Reinicia el supervisor

### Quiero liberación más/menos agresiva
- Ajusta `RAM_THRESHOLD_WARNING` y `RAM_THRESHOLD_CRITICAL`
- Modifica `CHECK_INTERVAL` (más frecuente = más reactivo)

## 🎯 Recomendaciones

1. **Deja que corra 24/7**: El guardian aprende los patrones de uso
2. **Revisa logs periódicamente**: Identifica apps problemáticas
3. **Ajusta umbrales a tu flujo**: Si editas video, sube los límites
4. **Protege lo importante**: Marca tus apps críticas como protegidas

## 📋 Ejemplo de Log
```
2025-12-27 15:30:00 [RAM_GUARDIAN] INFO: 🛡️ RAM Guardian iniciado
2025-12-27 15:30:00 [RAM_GUARDIAN] INFO: Umbrales: Warning=75%, Critical=85%
2025-12-27 15:35:00 [RAM_GUARDIAN] WARNING: ⚠️ ADVERTENCIA: 78% - Liberación preventiva
2025-12-27 15:35:02 [RAM_GUARDIAN] INFO: ✂️ Proceso cerrado: Chrome Helper (PID: 12345)
2025-12-27 15:35:05 [RAM_GUARDIAN] INFO: 🧹 Limpieza completada: 3 procesos cerrados
2025-12-27 15:35:05 [RAM_GUARDIAN] INFO: 📊 Memoria: 78% → 65% (liberado: 13%)
```

## 🚨 Nota Importante

RAM Guardian **nunca** cierra procesos sin razón. Solo actúa cuando:
1. La RAM supera umbrales configurados
2. Hay procesos de baja prioridad disponibles
3. Los procesos NO están protegidos

Es completamente seguro y reversible - los procesos pueden reiniciarse si son necesarios.

---

**Arquitecto**: Iyari Cancino Gomez  
**Dominio**: 3_POWER  
**Fecha**: 27 de Diciembre, 2025
