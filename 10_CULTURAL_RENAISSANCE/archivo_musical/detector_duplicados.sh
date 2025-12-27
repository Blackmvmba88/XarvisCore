#!/bin/zsh
# 🔍 DETECTOR DE DUPLICADOS MUSICALES - BLACKMAMBA
# Análisis musicológico para encontrar archivos repetidos
# ¿No crees que es mejor limpiar antes de organizar?

echo "🔍 DETECTOR DE DUPLICADOS MUSICALES BLACKMAMBA 🐍"
echo "=================================================="

# Crear directorio temporal para análisis
mkdir -p "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS"

# Función para detectar duplicados por nombre (sin extensión)
detectar_duplicados_nombre() {
    echo "📝 ANÁLISIS 1: Duplicados por nombre (ignorando extensión)"
    echo "========================================================="
    
    # Encontrar todos los archivos musicales y extraer nombres base
    find "/Volumes/ADATA SC740" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" -o -name "*.mid" -o -name "*.midi" \) 2>/dev/null | \
    while read archivo; do
        # Extraer nombre sin extensión y sin números de versión
        nombre_base=$(basename "$archivo" | sed 's/\.[^.]*$//' | sed 's/ (Cover)//g' | sed 's/ (Remix)//g' | sed 's/ ([0-9])//g' | sed 's/ \([0-9]\)//g')
        echo "$nombre_base|$archivo"
    done | sort > "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS/nombres_archivos.txt"
    
    # Contar duplicados
    echo ""
    echo "🎯 ARCHIVOS CON NOMBRES SIMILARES:"
    echo "----------------------------------"
    
    cat "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS/nombres_archivos.txt" | \
    cut -d'|' -f1 | sort | uniq -d | head -20 | while read nombre; do
        echo "🎵 $nombre:"
        grep "^$nombre|" "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS/nombres_archivos.txt" | \
        cut -d'|' -f2 | sed 's|^|   → |'
        echo ""
    done
}

# Función para detectar duplicados por tamaño
detectar_duplicados_tamaño() {
    echo "💾 ANÁLISIS 2: Duplicados por tamaño exacto"
    echo "==========================================="
    
    # Encontrar archivos con mismo tamaño
    find "/Volumes/ADATA SC740" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" \) -exec stat -f "%z %N" {} \; 2>/dev/null | \
    sort | uniq -d -w 10 > "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS/duplicados_tamaño.txt"
    
    echo ""
    echo "🎯 ARCHIVOS CON TAMAÑO IDÉNTICO:"
    echo "--------------------------------"
    
    if [[ -s "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS/duplicados_tamaño.txt" ]]; then
        cat "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS/duplicados_tamaño.txt" | head -20 | while read linea; do
            tamaño=$(echo "$linea" | awk '{print $1}')
            archivo=$(echo "$linea" | cut -d' ' -f2-)
            echo "💾 Tamaño: $(numfmt --to=iec $tamaño) - $(basename "$archivo")"
        done
    else
        echo "✅ No se encontraron duplicados exactos por tamaño"
    fi
}

# Función para analizar versiones de la misma canción
analizar_versiones() {
    echo ""
    echo "🎭 ANÁLISIS 3: Múltiples versiones de canciones"
    echo "==============================================="
    
    echo "🎯 CANCIONES CON MÚLTIPLES VERSIONES:"
    echo "------------------------------------"
    
    # Buscar patrones comunes de versionado
    find "/Volumes/ADATA SC740" -type f \( -name "*.mp3" -o -name "*.wav" \) 2>/dev/null | \
    grep -E '\((Cover|Remix|Edit|Extended|Radio|Club|Acoustic|Live)\)' | \
    head -20 | while read archivo; do
        nombre_cancion=$(basename "$archivo" | sed 's/ (Cover).*$//' | sed 's/ (Remix).*$//' | sed 's/ (Edit).*$//')
        echo "🎵 $nombre_cancion"
        find "/Volumes/ADATA SC740" -name "*$nombre_cancion*" 2>/dev/null | head -5 | sed 's|^|   → |'
        echo ""
    done
}

# Función para estadísticas de duplicados
estadisticas_duplicados() {
    echo ""
    echo "📊 ESTADÍSTICAS DE DUPLICADOS"
    echo "============================="
    
    total_archivos=$(find "/Volumes/ADATA SC740" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" \) 2>/dev/null | wc -l)
    
    # Contar nombres únicos vs total
    nombres_unicos=$(find "/Volumes/ADATA SC740" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" \) 2>/dev/null | \
    xargs -I {} basename {} | sed 's/\.[^.]*$//' | sed 's/ (Cover)//g' | sed 's/ (Remix)//g' | sed 's/ ([0-9])//g' | \
    sort | uniq | wc -l)
    
    duplicados_potenciales=$((total_archivos - nombres_unicos))
    
    echo "🎵 Total archivos musicales: $total_archivos"
    echo "🎯 Nombres únicos estimados: $nombres_unicos"
    echo "⚠️ Posibles duplicados/versiones: $duplicados_potenciales"
    echo ""
    
    if [[ $duplicados_potenciales -gt 0 ]]; then
        porcentaje=$((duplicados_potenciales * 100 / total_archivos))
        echo "📈 Porcentaje de duplicación: ~${porcentaje}%"
        echo "¿No crees que vale la pena limpiar esto?"
    else
        echo "✅ ¡Tu biblioteca está muy bien organizada!"
    fi
}

# Función para crear reporte detallado
crear_reporte_duplicados() {
    echo ""
    echo "📄 Creando reporte detallado de duplicados..."
    
    cat > "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/REPORTE_DUPLICADOS.md" << 'EOF'
# 🔍 REPORTE DE DUPLICADOS - BLACKMAMBA MUSIC LIBRARY

## Análisis Musicológico de Duplicados

### Metodología:
1. **Análisis por nombre** - Canciones con títulos similares
2. **Análisis por tamaño** - Archivos idénticos en bytes
3. **Análisis por versiones** - Covers, remixes, edits

### Criterios de Limpieza Recomendados:
- **Mantener WAV** sobre MP3 cuando sean la misma canción
- **Conservar versión más reciente** en duplicados exactos
- **Organizar versiones** (Original, Remix, Cover) en subcarpetas
- **Documentar decisiones** de qué se mantiene/elimina

### Acciones Recomendadas:
1. Revisar duplicados exactos → Eliminar redundancias
2. Organizar versiones → Crear estructura jerárquica
3. Unificar nomenclatura → Consistencia en nombres
4. Backup antes de eliminar → Seguridad total

---
*Análisis generado automáticamente*
*BlackMamba Records © 2025*
EOF

    echo "✅ Reporte guardado en: REPORTE_DUPLICADOS.md"
}

# Menú principal
main_menu() {
    echo ""
    echo "🔍 ¿QUÉ ANÁLISIS DESEAS REALIZAR?"
    echo "================================="
    echo "1) 📝 Detectar duplicados por nombre"
    echo "2) 💾 Detectar duplicados por tamaño"
    echo "3) 🎭 Analizar versiones múltiples"
    echo "4) 📊 Ver estadísticas generales"
    echo "5) 🔄 Análisis completo"
    echo "6) 📄 Crear reporte detallado"
    echo "7) 🧹 Limpiar archivos temporales"
    echo "8) 🚪 Salir"
    echo ""
    read "opcion?Selecciona una opción [1-8]: "
    
    case $opcion in
        1) detectar_duplicados_nombre ;;
        2) detectar_duplicados_tamaño ;;
        3) analizar_versiones ;;
        4) estadisticas_duplicados ;;
        5) 
            detectar_duplicados_nombre
            detectar_duplicados_tamaño  
            analizar_versiones
            estadisticas_duplicados
            ;;
        6) crear_reporte_duplicados ;;
        7) rm -rf "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/TEMP_ANALYSIS"; echo "🧹 Archivos temporales limpiados" ;;
        8) echo "👋 ¡Análisis completado!" ;;
        *) echo "❌ Opción inválida. ¿No crees que deberías elegir del 1 al 8?" ;;
    esac
}

# Ejecutar
main_menu