#!/bin/bash
# === VALIDACIÓN COMPLETA DEL SISTEMA XARVIS ===
# Arquitecto: Iyari Cancino Gomez
# Fecha: 27 de Diciembre, 2025

echo "🔍 INICIANDO VALIDACIÓN DEL SISTEMA XARVIS..."
echo "=========================================="

BASE_DIR="/Users/blackmamba/Desktop/XarvisCore"
cd "$BASE_DIR" || exit 1

# === 1. VALIDAR ESTRUCTURA DE DOMINIOS ===
echo ""
echo "📂 Validando estructura de dominios..."
DOMINIOS=(
    "0_SOVEREIGN_MANIFESTO"
    "1_CORE"
    "2_GUARDIANS"
    "3_POWER"
    "4_INTERFACE"
    "5_INFRA"
    "6_WORLD_DATA"
    "7_EDUCATION_SYSTEM"
    "8_RESOURCE_MGMT"
    "9_POLITICAL_FOUNDATION"
    "10_CULTURAL_RENAISSANCE"
    "11_UNIVERSAL_SECURITY"
    "12_SOVEREIGN_FINANCE"
    "13_DIGITAL_GOVERNANCE"
    "14_CREATIVE_TOOLS"
    "15_ESCRIBA"
    "16_AGRICULTURE"
    "17_AI_EXPERIMENTS"
    "18_BLACKMAMBA_STATION"
)

MISSING_DOMAINS=0
for dominio in "${DOMINIOS[@]}"; do
    if [ -d "$dominio" ]; then
        echo "  ✅ $dominio"
    else
        echo "  ❌ $dominio - NO ENCONTRADO"
        ((MISSING_DOMAINS++))
    fi
done

# === 2. VALIDAR ARCHIVOS CRÍTICOS ===
echo ""
echo "🔧 Validando archivos críticos..."
CRITICAL_FILES=(
    "xarvis_supervisor.py"
    "1_CORE/xarvis_core.py"
    "3_POWER/xarvis_full_power.py"
    "README.md"
    "EpicRoadmap.md"
    "ARCHITECTURE.md"
    ".github/copilot-instructions.md"
)

MISSING_FILES=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - NO ENCONTRADO"
        ((MISSING_FILES++))
    fi
done

# === 3. VALIDAR SINTAXIS PYTHON ===
echo ""
echo "🐍 Validando sintaxis Python..."
PYTHON_FILES=(
    "xarvis_supervisor.py"
    "1_CORE/xarvis_core.py"
    "3_POWER/xarvis_full_power.py"
)

SYNTAX_ERRORS=0
for py_file in "${PYTHON_FILES[@]}"; do
    if python3 -m py_compile "$py_file" 2>/dev/null; then
        echo "  ✅ $py_file"
    else
        echo "  ❌ $py_file - ERROR DE SINTAXIS"
        ((SYNTAX_ERRORS++))
    fi
done

# === 4. VALIDAR ENTORNO VIRTUAL ===
echo ""
echo "🌐 Validando entorno virtual..."
if [ -d "venv" ]; then
    echo "  ✅ Entorno virtual existe"
    if [ -f "venv/bin/python3" ]; then
        echo "  ✅ Intérprete Python configurado"
        VENV_VERSION=$(venv/bin/python3 --version 2>&1)
        echo "     📌 $VENV_VERSION"
    else
        echo "  ❌ Intérprete Python no encontrado"
    fi
else
    echo "  ⚠️  Entorno virtual no encontrado (crear con: python3 -m venv venv)"
fi

# === 5. VALIDAR DEPENDENCIAS ===
echo ""
echo "📦 Validando dependencias críticas..."
DEPENDENCIES=("flask" "psutil" "flask_cors")
MISSING_DEPS=0

for dep in "${DEPENDENCIES[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo "  ✅ $dep"
    else
        echo "  ❌ $dep - NO INSTALADO"
        ((MISSING_DEPS++))
    fi
done

# === 6. VALIDAR GIT ===
echo ""
echo "🔧 Validando repositorio Git..."
if [ -d ".git" ]; then
    echo "  ✅ Repositorio Git inicializado"
    BRANCH=$(git branch --show-current 2>/dev/null)
    echo "     📌 Branch: $BRANCH"
    
    REMOTE=$(git remote get-url origin 2>/dev/null)
    if [ -n "$REMOTE" ]; then
        echo "  ✅ Remote configurado: $REMOTE"
    else
        echo "  ⚠️  Remote no configurado"
    fi
else
    echo "  ❌ No es un repositorio Git"
fi

# === RESUMEN FINAL ===
echo ""
echo "=========================================="
echo "📊 RESUMEN DE VALIDACIÓN"
echo "=========================================="
echo "Dominios faltantes: $MISSING_DOMAINS"
echo "Archivos críticos faltantes: $MISSING_FILES"
echo "Errores de sintaxis: $SYNTAX_ERRORS"
echo "Dependencias faltantes: $MISSING_DEPS"
echo ""

TOTAL_ISSUES=$((MISSING_DOMAINS + MISSING_FILES + SYNTAX_ERRORS + MISSING_DEPS))

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo "✅ SISTEMA VALIDADO: TODO OPERACIONAL"
    echo "🚀 El Sistema Xarvis está listo para despliegue"
    exit 0
else
    echo "⚠️  PROBLEMAS DETECTADOS: $TOTAL_ISSUES"
    echo "🔧 Revisar elementos marcados arriba"
    exit 1
fi
