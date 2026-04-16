# RAM Guardian - Configuración
# Ajusta estos valores según las necesidades de tu sistema

# === UMBRALES DE MEMORIA ===
RAM_THRESHOLD_WARNING = 75     # % - Advertencia (liberación preventiva)
RAM_THRESHOLD_CRITICAL = 85    # % - Crítico (liberación agresiva)
RAM_THRESHOLD_OPTIMAL = 60     # % - Objetivo óptimo

# === MONITOREO ===
CHECK_INTERVAL = 10            # Segundos entre chequeos

# === PROCESOS PROTEGIDOS ===
# Estos procesos NUNCA serán cerrados
PROTECTED_PROCESSES = [
    'xarvis_core.py',
    'xarvis_full_power.py',
    'xarvis_supervisor.py',
    'ram_guardian.py',
    'kernel_task',
    'launchd',
    'WindowServer',
    'loginwindow',
    'systemd',
    'python3'
]

# === PROCESOS DE BAJA PRIORIDAD ===
# Estos son candidatos para cierre cuando la RAM está alta
LOW_PRIORITY_PATTERNS = [
    'Google Chrome Helper',
    'Chrome',
    'slack',
    'discord',
    'spotify',
    'Steam',
    'Epic',
    'firefox',
    'safari',
    'mail',
    'calendar',
    'notes',
    'preview'
]

# === NOTAS DE USO ===
# 1. El RAM Guardian se ejecuta automáticamente con el supervisor
# 2. Logs disponibles en: 5_INFRA/logs/ram_guardian.log
# 3. Para ajustar umbrales, modifica los valores arriba y reinicia
# 4. Agrega procesos protegidos si necesitas mantener algo corriendo
