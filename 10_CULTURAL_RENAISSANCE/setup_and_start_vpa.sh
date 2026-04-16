#!/bin/bash
# Setup completo de VPA - Escaneo + Validación + Lanzamiento
# Autor: Iyari Cancino Gomez

echo "🎵 VOCAL PERFORMANCE ANALYZER - Setup Completo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

cd "$(dirname "$0")"

# Función para chequear si existe el índice
check_library_index() {
    if [ -f "music_library.json" ]; then
        SONG_COUNT=$(python3 -c "import json; print(len(json.load(open('music_library.json'))))" 2>/dev/null || echo "0")
        return 0
    else
        return 1
    fi
}

# Paso 1: Verificar o generar índice de biblioteca
echo -e "\n${CYAN}📚 Paso 1: Verificación de Biblioteca Musical${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if check_library_index; then
    echo -e "${GREEN}✓${NC} Índice encontrado: music_library.json"
    echo -e "  📊 Canciones indexadas: $SONG_COUNT"
    echo ""
    read -p "¿Re-escanear biblioteca? (s/N): " RESCAN
    
    if [[ "$RESCAN" =~ ^[Ss]$ ]]; then
        echo -e "\n${YELLOW}🔍 Re-escaneando biblioteca...${NC}"
        python3 scan_music_library.py
    else
        echo -e "${GREEN}✓${NC} Usando índice existente"
    fi
else
    echo -e "${YELLOW}⚠️  No se encontró índice de biblioteca${NC}"
    echo -e "${CYAN}🔍 Escaneando música en USB y Downloads...${NC}"
    echo ""
    python3 scan_music_library.py
    
    if [ $? -ne 0 ]; then
        echo -e "\n${RED}❌ Error en el escaneo${NC}"
        exit 1
    fi
fi

# Paso 2: Verificar dependencias Python
echo -e "\n${CYAN}📦 Paso 2: Verificación de Dependencias${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Activar venv si existe
if [ -d "../../venv" ]; then
    source ../../venv/bin/activate
    echo -e "${GREEN}✓${NC} Entorno virtual activado"
else
    echo -e "${YELLOW}⚠️  No se encontró venv${NC}"
fi

# Instalar dependencias si faltan
MISSING_DEPS=0
for package in flask flask-cors requests; do
    if ! pip3 show $package &>/dev/null; then
        echo -e "${YELLOW}⚠️  Instalando $package...${NC}"
        pip3 install $package -q
        MISSING_DEPS=1
    fi
done

if [ $MISSING_DEPS -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Todas las dependencias instaladas"
fi

# Paso 3: Verificar Shazam (opcional)
echo -e "\n${CYAN}🎵 Paso 3: Verificación de Shazam Desktop${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "$HOME/Library/Application Support/Shazam" ]; then
    echo -e "${GREEN}✓${NC} Shazam Desktop detectado"
else
    echo -e "${YELLOW}⚠️  Shazam Desktop no encontrado${NC}"
    echo "   Descarga: https://www.shazam.com/apps"
    echo "   (Opcional - puedes buscar canciones manualmente)"
fi

# Paso 4: Crear directorios necesarios
mkdir -p lyrics_cache performance_logs
echo -e "${GREEN}✓${NC} Directorios de trabajo creados"

# Paso 5: Mostrar resumen
echo -e "\n${CYAN}📊 Resumen de Sistema${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "music_library.json" ]; then
    SONG_COUNT=$(python3 -c "import json; d=json.load(open('music_library.json')); print(len(d))" 2>/dev/null || echo "?")
    COMPLETE=$(python3 -c "import json; d=json.load(open('music_library.json')); print(sum(1 for s in d if s['status']=='complete'))" 2>/dev/null || echo "?")
    MP3_ONLY=$(python3 -c "import json; d=json.load(open('music_library.json')); print(sum(1 for s in d if s['status']=='mp3_only'))" 2>/dev/null || echo "?")
    WAV_ONLY=$(python3 -c "import json; d=json.load(open('music_library.json')); print(sum(1 for s in d if s['status']=='wav_only'))" 2>/dev/null || echo "?")
    
    echo -e "🎼 Total de canciones: ${GREEN}$SONG_COUNT${NC}"
    echo -e "✅ Pares completos (MP3+WAV): ${GREEN}$COMPLETE${NC}"
    echo -e "⚠️  Solo MP3: ${YELLOW}$MP3_ONLY${NC}"
    echo -e "⚠️  Solo WAV: ${YELLOW}$WAV_ONLY${NC}"
else
    echo -e "${RED}❌ No hay biblioteca indexada${NC}"
fi

# Paso 6: Lanzar VPA
echo -e "\n${GREEN}🚀 Paso 6: Iniciando VPA Server${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}📡 API disponible en:${NC} http://localhost:9000/status"
echo -e "${CYAN}🎨 Dashboard:${NC} Abre vpa_dashboard.html en tu navegador"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener${NC}"
echo ""

# Iniciar servidor
python3 vocal_performance_analyzer.py
