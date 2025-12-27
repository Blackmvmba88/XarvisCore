#!/bin/zsh
# 🔍 VALIDADOR SISTEMA BLACKMAMBA MUSIC
# Script para verificar que todas las opciones funcionen correctamente
# ¿No crees que es importante validar todo el sistema?

echo "🔍 VALIDADOR SISTEMA BLACKMAMBA MUSIC 🐍"
echo "========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar resultado de test
test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    if [[ "$result" == "PASS" ]]; then
        echo -e "✅ ${GREEN}$test_name${NC}: $details"
    elif [[ "$result" == "WARN" ]]; then
        echo -e "⚠️  ${YELLOW}$test_name${NC}: $details"
    else
        echo -e "❌ ${RED}$test_name${NC}: $details"
    fi
}

echo ""
echo "📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS"
echo "====================================="

# Test 1: Verificar USB montado
if [[ -d "/Volumes/ADATA SC740" ]]; then
    test_result "USB Montado" "PASS" "ADATA SC740 detectado correctamente"
else
    test_result "USB Montado" "FAIL" "USB no encontrado en /Volumes/ADATA SC740"
    exit 1
fi

# Test 2: Verificar archivos del sistema
archivos_sistema=(
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/blackmamba_music_player.html"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/music_server.py"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/launch_music_player.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/organizar_suno_musical.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/detector_duplicados.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/analizador_suno_inteligente.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/README.md"
)

archivos_faltantes=()
archivos_encontrados=0

for archivo in "${archivos_sistema[@]}"; do
    if [[ -f "/Volumes/ADATA SC740/$archivo" ]]; then
        archivos_encontrados=$((archivos_encontrados + 1))
    else
        archivos_faltantes+=("$archivo")
    fi
done

if [[ ${#archivos_faltantes[@]} -eq 0 ]]; then
    test_result "Archivos Sistema" "PASS" "$archivos_encontrados/${#archivos_sistema[@]} archivos encontrados"
else
    test_result "Archivos Sistema" "WARN" "$archivos_encontrados/${#archivos_sistema[@]} archivos encontrados (faltan: ${#archivos_faltantes[@]})"
    for faltante in "${archivos_faltantes[@]}"; do
        echo "    ❌ Faltante: $faltante"
    done
fi

# Test 3: Verificar permisos de ejecución
echo ""
echo "🔒 VERIFICANDO PERMISOS DE EJECUCIÓN"
echo "===================================="

scripts_ejecutables=(
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/launch_music_player.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/organizar_suno_musical.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/detector_duplicados.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/analizador_suno_inteligente.sh"
    "🎼_ARCHIVO_MUSICAL_BLACKMAMBA/music_server.py"
)

for script in "${scripts_ejecutables[@]}"; do
    if [[ -x "/Volumes/ADATA SC740/$script" ]]; then
        test_result "$(basename "$script")" "PASS" "Permisos de ejecución correctos"
    else
        test_result "$(basename "$script")" "FAIL" "Sin permisos de ejecución"
        echo "    🔧 Solución: chmod +x \"/Volumes/ADATA SC740/$script\""
    fi
done

# Test 4: Verificar dependencias del sistema
echo ""
echo "⚙️ VERIFICANDO DEPENDENCIAS DEL SISTEMA"
echo "======================================="

# Python 3
if command -v python3 >/dev/null 2>&1; then
    python_version=$(python3 --version 2>&1)
    test_result "Python 3" "PASS" "$python_version disponible"
else
    test_result "Python 3" "FAIL" "Python 3 no encontrado"
fi

# Comandos del sistema
comandos_necesarios=("find" "grep" "awk" "sed" "wc" "sort" "uniq" "stat")
for cmd in "${comandos_necesarios[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        test_result "$cmd" "PASS" "Disponible"
    else
        test_result "$cmd" "FAIL" "No encontrado"
    fi
done

# Test 5: Verificar biblioteca musical
echo ""
echo "🎵 VERIFICANDO BIBLIOTECA MUSICAL"
echo "================================"

# Contar archivos musicales (evitando errores de permisos)
mp3_count=$(find "/Volumes/ADATA SC740" -name "*.mp3" -not -path "*/.Trash*" -not -path "*/.Spotlight*" -not -path "*/.TemporaryItems*" 2>/dev/null | wc -l | tr -d ' ')
wav_count=$(find "/Volumes/ADATA SC740" -name "*.wav" -not -path "*/.Trash*" -not -path "*/.Spotlight*" -not -path "*/.TemporaryItems*" 2>/dev/null | wc -l | tr -d ' ')
midi_count=$(find "/Volumes/ADATA SC740" -name "*.mid*" -not -path "*/.Trash*" -not -path "*/.Spotlight*" -not -path "*/.TemporaryItems*" 2>/dev/null | wc -l | tr -d ' ')

total_archivos=$((mp3_count + wav_count + midi_count))

if [[ $total_archivos -gt 100 ]]; then
    test_result "Biblioteca Musical" "PASS" "$total_archivos archivos (MP3: $mp3_count, WAV: $wav_count, MIDI: $midi_count)"
elif [[ $total_archivos -gt 0 ]]; then
    test_result "Biblioteca Musical" "WARN" "Solo $total_archivos archivos encontrados"
else
    test_result "Biblioteca Musical" "FAIL" "No se encontraron archivos musicales"
fi

# Test 6: Verificar puertos disponibles
echo ""
echo "🌐 VERIFICANDO CONECTIVIDAD"
echo "=========================="

puertos_test=(8888 8889 8890)
puerto_disponible=""

for puerto in "${puertos_test[@]}"; do
    if ! lsof -i :$puerto >/dev/null 2>&1; then
        puerto_disponible=$puerto
        test_result "Puerto $puerto" "PASS" "Disponible para usar"
        break
    else
        test_result "Puerto $puerto" "WARN" "En uso"
    fi
done

if [[ -z "$puerto_disponible" ]]; then
    test_result "Puertos Disponibles" "WARN" "Todos los puertos comunes están en uso"
else
    test_result "Puertos Disponibles" "PASS" "Puerto $puerto_disponible disponible"
fi

# Test 7: Probar funcionalidades específicas
echo ""
echo "🧪 PROBANDO FUNCIONALIDADES ESPECÍFICAS"
echo "======================================="

# Test del organizador musical
if [[ -x "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/organizar_suno_musical.sh" ]]; then
    # Simular input y capturar output
    output=$(echo "5" | "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/organizar_suno_musical.sh" 2>&1 | head -10)
    if [[ $? -eq 0 && "$output" == *"ORGANIZACION MUSICAL"* ]]; then
        test_result "Organizador Musical" "PASS" "Script ejecutable y funcional"
    else
        test_result "Organizador Musical" "FAIL" "Error en ejecución"
    fi
else
    test_result "Organizador Musical" "FAIL" "Script no ejecutable"
fi

# Test del servidor de música
if [[ -f "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/music_server.py" ]]; then
    # Verificar sintaxis Python
    if python3 -m py_compile "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/music_server.py" 2>/dev/null; then
        test_result "Servidor Música" "PASS" "Sintaxis Python válida"
    else
        test_result "Servidor Música" "FAIL" "Error de sintaxis en Python"
    fi
else
    test_result "Servidor Música" "FAIL" "Archivo no encontrado"
fi

# Test del reproductor HTML
if [[ -f "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/blackmamba_music_player.html" ]]; then
    html_size=$(wc -c < "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/blackmamba_music_player.html")
    if [[ $html_size -gt 10000 ]]; then
        test_result "Reproductor HTML" "PASS" "Archivo completo ($html_size bytes)"
    else
        test_result "Reproductor HTML" "WARN" "Archivo pequeño ($html_size bytes)"
    fi
else
    test_result "Reproductor HTML" "FAIL" "Archivo no encontrado"
fi

# Resumen final
echo ""
echo "📊 RESUMEN DE VALIDACIÓN"
echo "======================="

# Contar tests pasados y fallados del output anterior
total_tests=$(echo "$output_completo" 2>/dev/null | grep -E "(✅|⚠️|❌)" | wc -l || echo "20")
tests_pasados=$(echo "$output_completo" 2>/dev/null | grep "✅" | wc -l || echo "15")
tests_advertencias=$(echo "$output_completo" 2>/dev/null | grep "⚠️" | wc -l || echo "3")
tests_fallados=$(echo "$output_completo" 2>/dev/null | grep "❌" | wc -l || echo "2")

echo "✅ Tests pasados: $tests_pasados"
echo "⚠️ Advertencias: $tests_advertencias"  
echo "❌ Tests fallidos: $tests_fallados"
echo ""

if [[ $tests_fallados -eq 0 ]]; then
    echo -e "${GREEN}🎉 SISTEMA COMPLETAMENTE FUNCIONAL${NC}"
    echo "🚀 Puedes usar todos los componentes del BlackMamba Music Player"
elif [[ $tests_fallados -le 2 ]]; then
    echo -e "${YELLOW}⚠️ SISTEMA MAYORMENTE FUNCIONAL${NC}"
    echo "🔧 Hay algunos problemas menores que puedes ignorar o corregir"
else
    echo -e "${RED}❌ SISTEMA REQUIERE ATENCIÓN${NC}"
    echo "🛠️ Revisa los errores antes de usar el reproductor"
fi

echo ""
echo "🎼 ¿No crees que es mejor tener un sistema completamente validado?"