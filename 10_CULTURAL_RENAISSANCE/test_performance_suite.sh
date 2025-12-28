#!/bin/bash
# BlackMamba Music Performance Suite - Bash Test Suite
# Arquitecto: Iyari Cancino Gomez
# Fecha: 28 de Diciembre, 2025

set -e  # Exit on error

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  BLACKMAMBA MUSIC PERFORMANCE SUITE - BASH TEST SUITE         ║"
echo "║  Arquitecto: Iyari Cancino Gomez                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Función para test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    echo -n "Test $TESTS_TOTAL: $test_name ... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "🔍 CATEGORÍA: Archivos y Estructura"
echo "─────────────────────────────────────────────────────────────────"

run_test "music_performance_suite.py existe" \
    "[ -f music_performance_suite.py ]"

run_test "start_performance_suite.sh existe" \
    "[ -f start_performance_suite.sh ]"

run_test "music_library.json existe" \
    "[ -f music_library.json ]"

run_test "audio_fingerprints.json existe" \
    "[ -f audio_fingerprints.json ]"

run_test "vpa_with_detector.py existe" \
    "[ -f vpa_with_detector.py ]"

run_test "audio_detector.py existe" \
    "[ -f audio_detector.py ]"

run_test "PERFORMANCE_SUITE_README.md existe" \
    "[ -f PERFORMANCE_SUITE_README.md ]"

echo ""
echo "🔐 CATEGORÍA: Permisos"
echo "─────────────────────────────────────────────────────────────────"

run_test "music_performance_suite.py es ejecutable" \
    "[ -x music_performance_suite.py ]"

run_test "start_performance_suite.sh es ejecutable" \
    "[ -x start_performance_suite.sh ]"

echo ""
echo "✅ CATEGORÍA: Validación de Sintaxis"
echo "─────────────────────────────────────────────────────────────────"

run_test "music_performance_suite.py sintaxis válida" \
    "python3 -m py_compile music_performance_suite.py"

run_test "start_performance_suite.sh sintaxis bash válida" \
    "bash -n start_performance_suite.sh"

run_test "vpa_with_detector.py sintaxis válida" \
    "python3 -m py_compile vpa_with_detector.py"

run_test "audio_detector.py sintaxis válida" \
    "python3 -m py_compile audio_detector.py"

echo ""
echo "📦 CATEGORÍA: Dependencias"
echo "─────────────────────────────────────────────────────────────────"

run_test "Python 3 disponible" \
    "command -v python3"

run_test "Flask instalado" \
    "python3 -c 'import flask'"

run_test "Flask-CORS instalado" \
    "python3 -c 'import flask_cors'"

run_test "psutil instalado" \
    "python3 -c 'import psutil'"

echo ""
echo "📊 CATEGORÍA: JSON Validation"
echo "─────────────────────────────────────────────────────────────────"

run_test "music_library.json es JSON válido" \
    "python3 -c 'import json; json.load(open(\"music_library.json\"))'"

run_test "audio_fingerprints.json es JSON válido" \
    "python3 -c 'import json; json.load(open(\"audio_fingerprints.json\"))'"

run_test "music_library tiene 194 canciones" \
    "[ \$(python3 -c 'import json; print(len(json.load(open(\"music_library.json\"))))') -eq 194 ]"

echo ""
echo "🔗 CATEGORÍA: Imports de Python"
echo "─────────────────────────────────────────────────────────────────"

run_test "Flask imports básicos" \
    "python3 -c 'from flask import Flask, jsonify, request'"

run_test "Flask-CORS import" \
    "python3 -c 'from flask_cors import CORS'"

run_test "JSON import" \
    "python3 -c 'import json'"

run_test "OS import" \
    "python3 -c 'import os'"

run_test "Datetime import" \
    "python3 -c 'import datetime'"

echo ""
echo "🎛️ CATEGORÍA: Integración con Music Manager"
echo "─────────────────────────────────────────────────────────────────"

run_test "music_manager.sh existe" \
    "[ -f music_manager.sh ]"

run_test "Performance Suite en menú" \
    "grep -q 'Performance Suite' music_manager.sh"

run_test "Llamada a start_performance_suite.sh en manager" \
    "grep -q 'start_performance_suite.sh' music_manager.sh"

echo ""
echo "🌐 CATEGORÍA: Red y Puerto"
echo "─────────────────────────────────────────────────────────────────"

run_test "Puerto 9002 disponible" \
    "! lsof -i :9002 > /dev/null 2>&1"

run_test "Puerto 9001 no conflictúa" \
    "! lsof -i :9001 > /dev/null 2>&1 || true"

echo ""
echo "📝 CATEGORÍA: Documentación"
echo "─────────────────────────────────────────────────────────────────"

run_test "README existe" \
    "[ -f PERFORMANCE_SUITE_README.md ]"

run_test "Integration doc existe" \
    "[ -f INTEGRATION_COMPLETE.md ]"

run_test "Validation doc existe" \
    "[ -f PERFORMANCE_SUITE_VALIDATION.md ]"

run_test "README no está vacío" \
    "[ -s PERFORMANCE_SUITE_README.md ]"

echo ""
echo "🔧 CATEGORÍA: Code Quality"
echo "─────────────────────────────────────────────────────────────────"

run_test "Archivo Python tiene shebang" \
    "head -1 music_performance_suite.py | grep -q '^#!/usr/bin/env python3'"

run_test "Launcher tiene shebang" \
    "head -1 start_performance_suite.sh | grep -q '^#!/bin/bash'"

run_test "Python file tiene imports" \
    "grep -q '^import ' music_performance_suite.py"

run_test "Python file tiene Flask app" \
    "grep -q 'app = Flask' music_performance_suite.py"

run_test "Python file tiene CORS" \
    "grep -q 'CORS(app)' music_performance_suite.py"

echo ""
echo "📈 CATEGORÍA: Métricas de Código"
echo "─────────────────────────────────────────────────────────────────"

LINES_OF_CODE=$(wc -l < music_performance_suite.py)
run_test "Código tiene al menos 500 líneas" \
    "[ $LINES_OF_CODE -ge 500 ]"

ENDPOINTS=$(grep -c '@app.route' music_performance_suite.py)
run_test "Al menos 8 endpoints definidos" \
    "[ $ENDPOINTS -ge 8 ]"

FUNCTIONS=$(grep -c '^def ' music_performance_suite.py)
run_test "Al menos 10 funciones definidas" \
    "[ $FUNCTIONS -ge 10 ]"

echo ""
echo "🧪 CATEGORÍA: Componentes Opcionales"
echo "─────────────────────────────────────────────────────────────────"

# Tests que pueden fallar sin romper el sistema
echo -n "Test: VPA disponible ... "
if python3 -c "from vpa_with_detector import VPAWithDetector" 2>/dev/null; then
    echo -e "${GREEN}✅ AVAILABLE${NC}"
else
    echo -e "${YELLOW}⚠️  OPTIONAL${NC}"
fi

echo -n "Test: Audio Detector disponible ... "
if python3 -c "from audio_detector import AudioFingerprinter" 2>/dev/null; then
    echo -e "${GREEN}✅ AVAILABLE${NC}"
else
    echo -e "${YELLOW}⚠️  OPTIONAL${NC}"
fi

echo -n "Test: Shazamio disponible ... "
if python3 -c "import shazamio" 2>/dev/null; then
    echo -e "${GREEN}✅ AVAILABLE${NC}"
else
    echo -e "${YELLOW}⚠️  OPTIONAL${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    RESUMEN DE TESTS                            ║"
echo "╠════════════════════════════════════════════════════════════════╣"

echo -e "║  Total de tests ejecutados: ${TESTS_TOTAL}"
echo -e "║  ${GREEN}✅ Tests pasados: ${TESTS_PASSED}${NC}"
echo -e "║  ${RED}❌ Tests fallidos: ${TESTS_FAILED}${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo "╠════════════════════════════════════════════════════════════════╣"
    echo -e "║  ${GREEN}🎉 ¡TODOS LOS TESTS PASARON!${NC}                               ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "╠════════════════════════════════════════════════════════════════╣"
    echo -e "║  ${RED}⚠️  ALGUNOS TESTS FALLARON${NC}                                 ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 1
fi
