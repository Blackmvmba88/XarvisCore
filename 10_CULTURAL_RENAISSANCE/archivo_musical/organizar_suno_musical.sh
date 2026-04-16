#!/bin/zsh
# 🎼 ORGANIZADOR MUSICAL SUNO - BLACKMAMBA RECORDS
# Archivo musical profesional con criterios musicológicos
# ¿No crees que es hora de organizar esta biblioteca magistral?

echo "🎵 INICIANDO ORGANIZACIÓN MUSICAL BLACKMAMBA 🐍"
echo "=================================================="

# Función para analizar y categorizar archivos musicales
categorizar_archivo() {
    local archivo="$1"
    local nombre_base=$(basename "$archivo" | tr '[:upper:]' '[:lower:]')
    
    # 01_ORIGINALS - Composiciones originales
    if [[ "$nombre_base" =~ "blackmamba" && ! "$nombre_base" =~ "(remix|cover|ft|feat)" ]]; then
        echo "📝 ORIGINAL: $archivo"
        return 1
    fi
    
    # 02_REMIXES - Todas las versiones remix
    if [[ "$nombre_base" =~ "(remix|remastered|edit)" ]]; then
        echo "🔄 REMIX: $archivo"
        return 2
    fi
    
    # 03_COLLABORATIONS - Colaboraciones con otros artistas
    if [[ "$nombre_base" =~ "(ft|feat|collaboration|with)" ]]; then
        echo "🤝 COLLABORACIÓN: $archivo"
        return 3
    fi
    
    # 05_CULTURAL_FUSION - Música con elementos culturales/idiomas originarios
    if [[ "$nombre_base" =~ "(náhuatl|maya|chīchīltikpa|yōllōtl|día de muertos|catrina)" ]]; then
        echo "🏛️ FUSIÓN CULTURAL: $archivo"
        return 5
    fi
    
    # 04_EXPERIMENTAL - Géneros experimentales/electrónicos
    if [[ "$nombre_base" =~ "(neon|galactic|quantum|experimental|electronic|psytrance)" ]]; then
        echo "🔬 EXPERIMENTAL: $archivo"
        return 4
    fi
    
    # 08_MASTERS_WAV - Archivos WAV de alta calidad
    if [[ "$archivo" =~ "\.wav$" ]] && [[ $(stat -f%z "$archivo" 2>/dev/null || echo 0) -gt 10000000 ]]; then
        echo "💎 MASTER WAV: $archivo"
        return 8
    fi
    
    # 07_STEMS_MIDI - Stems y archivos MIDI
    if [[ "$nombre_base" =~ "(stems|midi|multitrack)" ]] || [[ "$archivo" =~ "\.(mid|midi)$" ]]; then
        echo "🎛️ STEMS/MIDI: $archivo"
        return 7
    fi
    
    # 09_DEMOS - Versiones demo o trabajos en progreso
    if [[ "$nombre_base" =~ "(demo|rough|draft|wip)" ]]; then
        echo "🎤 DEMO: $archivo"
        return 9
    fi
    
    # 06_WORK_IN_PROGRESS - Por defecto para otros archivos
    echo "⚠️ WORK IN PROGRESS: $archivo"
    return 6
}

# Función principal de organización
organizar_musica() {
    echo "🔍 Analizando archivos musicales..."
    
    # Buscar todos los archivos musicales en el USB
    find "/Volumes/ADATA SC740" -maxdepth 1 \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" -o -name "*.mid" -o -name "*.midi" \) | while read archivo; do
        
        if [[ "$archivo" =~ "🎼_ARCHIVO_MUSICAL_BLACKMAMBA" ]]; then
            continue  # Skip already organized files
        fi
        
        categorizar_archivo "$archivo"
        categoria=$?
        
        # Determinar carpeta destino
        case $categoria in
            1) destino="01_ORIGINALS" ;;
            2) destino="02_REMIXES" ;;
            3) destino="03_COLLABORATIONS" ;;
            4) destino="04_EXPERIMENTAL" ;;
            5) destino="05_CULTURAL_FUSION" ;;
            6) destino="06_WORK_IN_PROGRESS" ;;
            7) destino="07_STEMS_MIDI" ;;
            8) destino="08_MASTERS_WAV" ;;
            9) destino="09_DEMOS" ;;
            *) destino="10_CONCEPTS" ;;
        esac
        
        # Crear subcarpeta por año
        año=$(stat -f %Sm -t %Y "$archivo" 2>/dev/null || echo "2024")
        mkdir -p "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/$destino/$año"
        
        # ¿No sería mejor tener un backup antes de mover?
        echo "   → Moviendo a: $destino/$año/"
        # mv "$archivo" "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/$destino/$año/"
        
    done
}

# Función para crear índice musical
crear_indice() {
    echo "📊 Creando índice musical..."
    
    cat > "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/INDICE_MUSICAL.md" << 'EOF'
# 🎼 ARCHIVO MUSICAL BLACKMAMBA 
## Índice Musicológico Profesional

### 📁 Estructura del Archivo:

**01_ORIGINALS** - Composiciones originales de BlackMamba
**02_REMIXES** - Versiones remix y remastered  
**03_COLLABORATIONS** - Colaboraciones con otros artistas
**04_EXPERIMENTAL** - Música experimental/electrónica
**05_CULTURAL_FUSION** - Fusión con elementos culturales mexicanos
**06_WORK_IN_PROGRESS** - Trabajos en desarrollo
**07_STEMS_MIDI** - Stems, multitracks y archivos MIDI
**08_MASTERS_WAV** - Masters en alta calidad (WAV)
**09_DEMOS** - Demos y bocetos musicales
**10_CONCEPTS** - Conceptos y ideas musicales

### 🎯 Criterios de Organización:

- **Por género y estilo musical**
- **Por calidad técnica (MP3 vs WAV)**
- **Por tipo de producción (original/remix/demo)**
- **Por elementos culturales**
- **Por año de creación**

### 📈 Estadísticas del Archivo:
*(Actualizadas automáticamente)*

**Total de composiciones:** [TBD]
**Géneros representados:** Reggae, Electronic, Latin, Fusion, Experimental
**Idiomas:** Español, Náhuatl
**Formato predominante:** MP3, WAV
**Período:** 2024-2025

---
*Organizado con criterios musicológicos profesionales*
*BlackMamba Records © 2025*
EOF

    echo "✅ Índice creado exitosamente"
}

# Función para mostrar estadísticas
mostrar_estadisticas() {
    echo ""
    echo "📊 ESTADÍSTICAS MUSICALES"
    echo "========================"
    
    total_mp3=$(find "/Volumes/ADATA SC740" -name "*.mp3" -not -path "*/.Trash*" -not -path "*/.Spotlight*" -not -path "*/.TemporaryItems*" 2>/dev/null | wc -l)
    total_wav=$(find "/Volumes/ADATA SC740" -name "*.wav" -not -path "*/.Trash*" -not -path "*/.Spotlight*" -not -path "*/.TemporaryItems*" 2>/dev/null | wc -l)
    total_midi=$(find "/Volumes/ADATA SC740" -name "*.mid*" -not -path "*/.Trash*" -not -path "*/.Spotlight*" -not -path "*/.TemporaryItems*" 2>/dev/null | wc -l)
    
    echo "🎵 Total MP3: $(echo $total_mp3 | tr -d ' ')"
    echo "💎 Total WAV: $(echo $total_wav | tr -d ' ')" 
    echo "🎛️ Total MIDI: $(echo $total_midi | tr -d ' ')"
    echo ""
    echo "¿No crees que esta biblioteca merece un orden profesional?"
}

# Menú principal
main_menu() {
    echo ""
    echo "🎼 ¿QUÉ ACCIÓN DESEAS REALIZAR?"
    echo "==============================="
    echo "1) 📊 Ver estadísticas actuales"
    echo "2) 🔍 Simular organización (no mover archivos)"
    echo "3) 🚀 Ejecutar organización completa"
    echo "4) 📝 Crear solo el índice musical"
    echo "5) 🚪 Salir"
    echo ""
    read "opcion?Selecciona una opción [1-5]: "
    
    case $opcion in
        1) mostrar_estadisticas ;;
        2) echo "🔍 Simulando..."; organizar_musica ;;
        3) echo "🚀 Organizando..."; organizar_musica && crear_indice ;;
        4) crear_indice ;;
        5) echo "👋 ¡Hasta la vista, musicólogo!" ;;
        *) echo "❌ Opción inválida. ¿No crees que deberías elegir del 1 al 5?" ;;
    esac
}

# Ejecutar
main_menu