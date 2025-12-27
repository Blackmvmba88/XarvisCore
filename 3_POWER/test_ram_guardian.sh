#!/bin/bash
# Test rápido del RAM Guardian
# Ejecuta este script para probar el sistema de gestión de memoria

echo "🧪 TEST DE RAM GUARDIAN"
echo "======================="
echo ""

# Verificar que existe
if [ ! -f "3_POWER/ram_guardian.py" ]; then
    echo "❌ ram_guardian.py no encontrado"
    exit 1
fi

echo "✅ RAM Guardian encontrado"
echo ""

# Mostrar estado actual de RAM
echo "📊 Estado actual de RAM:"
python3 -c "
import psutil
mem = psutil.virtual_memory()
print(f'  Total: {round(mem.total / (1024**3), 2)} GB')
print(f'  Usado: {round(mem.used / (1024**3), 2)} GB')
print(f'  Disponible: {round(mem.available / (1024**3), 2)} GB')
print(f'  Porcentaje: {mem.percent}%')
status = 'CRITICO' if mem.percent > 85 else 'ADVERTENCIA' if mem.percent > 75 else 'OPTIMO'
print(f'  Estado: {status}')
"

echo ""
echo "🔍 Top 5 procesos por memoria:"
python3 -c "
import psutil
procs = []
for proc in psutil.process_iter(['name', 'memory_percent']):
    try:
        if proc.info['memory_percent'] and proc.info['memory_percent'] > 0.1:
            procs.append((proc.info['name'], proc.info['memory_percent']))
    except: pass
procs.sort(key=lambda x: x[1], reverse=True)
for name, percent in procs[:5]:
    print(f'  {name}: {round(percent, 2)}%')
"

echo ""
echo "💡 Para iniciar el RAM Guardian automáticamente:"
echo "   python3 xarvis_supervisor.py"
echo ""
echo "💡 Para probar manualmente (Ctrl+C para detener):"
echo "   cd 3_POWER && python3 ram_guardian.py"
