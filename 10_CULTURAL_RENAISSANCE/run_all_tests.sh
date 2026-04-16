#!/bin/bash
# BlackMamba Music Performance Suite - Master Test Runner
# Ejecuta todos los tests: Python + Bash + Integration

cd "$(dirname "$0")"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     BLACKMAMBA MUSIC PERFORMANCE SUITE                          ║"
echo "║     MASTER TEST SUITE                                           ║"
echo "║                                                                  ║"
echo "║     Arquitecto: Iyari Cancino Gomez                             ║"
echo "║     Fecha: 28 de Diciembre, 2025                                ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_FAILURES=0

# Función para ejecutar test suite
run_suite() {
    local suite_name="$1"
    local suite_command="$2"
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  EJECUTANDO: $suite_name${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if eval "$suite_command"; then
        echo ""
        echo -e "${GREEN}✅ $suite_name: TODOS LOS TESTS PASARON${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ $suite_name: ALGUNOS TESTS FALLARON${NC}"
        TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
        return 1
    fi
}

# 1. BASH TEST SUITE
run_suite "BASH TEST SUITE" "./test_performance_suite.sh"

# 2. PYTHON UNITTEST SUITE
run_suite "PYTHON UNITTEST SUITE" "python3 test_performance_suite.py"

# 3. QUICK VALIDATION
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  QUICK VALIDATION CHECKS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo "📊 Estadísticas del código:"
echo "  - Líneas de código: $(wc -l < music_performance_suite.py)"
echo "  - API Endpoints: $(grep -c '@app.route' music_performance_suite.py)"
echo "  - Funciones: $(grep -c '^def ' music_performance_suite.py)"
echo ""

echo "📚 Biblioteca musical:"
SONG_COUNT=$(python3 -c "import json; print(len(json.load(open('music_library.json'))))")
echo "  - Canciones indexadas: $SONG_COUNT"
echo ""

echo "🔊 Audio fingerprints:"
FP_COUNT=$(python3 -c "import json; print(len(json.load(open('audio_fingerprints.json'))))")
echo "  - Fingerprints: $FP_COUNT"
echo ""

echo "📁 Archivos de documentación:"
for doc in PERFORMANCE_SUITE_README.md INTEGRATION_COMPLETE.md PERFORMANCE_SUITE_VALIDATION.md; do
    if [ -f "$doc" ]; then
        SIZE=$(du -h "$doc" | cut -f1)
        echo "  ✅ $doc ($SIZE)"
    else
        echo "  ❌ $doc (faltante)"
    fi
done
echo ""

# RESUMEN FINAL
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                     RESUMEN FINAL                               ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

if [ $TOTAL_FAILURES -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                                                                    ${NC}"
    echo -e "${GREEN}   🎉 ¡ÉXITO TOTAL!                                                ${NC}"
    echo -e "${GREEN}                                                                    ${NC}"
    echo -e "${GREEN}   Todas las suites de tests pasaron correctamente.                ${NC}"
    echo -e "${GREEN}   El Performance Suite está listo para producción.                ${NC}"
    echo -e "${GREEN}                                                                    ${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "🚀 Para iniciar el servidor:"
    echo "   ./start_performance_suite.sh"
    echo ""
    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}                                                                    ${NC}"
    echo -e "${RED}   ⚠️  ALGUNOS TESTS FALLARON                                      ${NC}"
    echo -e "${RED}                                                                    ${NC}"
    echo -e "${RED}   Suites fallidas: $TOTAL_FAILURES                                ${NC}"
    echo -e "${RED}   Revisa los logs arriba para más detalles.                       ${NC}"
    echo -e "${RED}                                                                    ${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    exit 1
fi
