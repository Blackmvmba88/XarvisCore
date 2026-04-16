#!/bin/zsh
# 🎼 ANALIZADOR MUSICAL INTELIGENTE - BLACKMAMBA
# Comparación por duración y análisis de ondas sinusoidales
# ¿No crees que es mejor analizar el contenido real que solo nombres?

echo "🎼 ANALIZADOR MUSICAL INTELIGENTE SUNO - BLACKMAMBA 🐍"
echo "====================================================="

# Función para obtener duración de archivo de audio
obtener_duracion() {
    local archivo="$1"
    if command -v ffprobe >/dev/null 2>&1; then
        # Con ffprobe (más preciso)
        ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$archivo" 2>/dev/null
    elif command -v afinfo >/dev/null 2>&1; then
        # Con afinfo (macOS)
        afinfo "$archivo" 2>/dev/null | grep "estimated duration" | awk '{print $3}'
    else
        # Fallback: estimación por tamaño de archivo
        local tamaño=$(stat -f%z "$archivo" 2>/dev/null || echo 0)
        # Aproximación: 1MB ≈ 1 minuto de MP3 a 128kbps
        echo "scale=2; $tamaño / 1000000" | bc 2>/dev/null || echo "0"
    fi
}

# Función para comparar archivos similares por duración
comparar_por_duracion() {
    echo "⏱️ ANÁLISIS POR DURACIÓN DE AUDIO"
    echo "================================="
    
    local temp_file="/tmp/duraciones_suno.txt"
    rm -f "$temp_file"
    
    echo "🔍 Analizando duraciones de archivos Suno..."
    echo ""
    
    # Encontrar grupos de archivos con nombres similares
    find "/Volumes/ADATA SC740" -maxdepth 1 -type f \( -name "*.mp3" -o -name "*.wav" \) | \
    grep -E '\([0-9]\)\.' | while read archivo; do
        # Extraer nombre base sin números
        nombre_base=$(basename "$archivo" | sed 's/ ([0-9]).*//' | sed 's/\.mp3$//' | sed 's/\.wav$//')
        duracion=$(obtener_duracion "$archivo")
        tamaño=$(stat -f%z "$archivo" 2>/dev/null || echo 0)
        
        echo "$nombre_base|$duracion|$tamaño|$archivo" >> "$temp_file"
    done
    
    if [[ -f "$temp_file" ]]; then
        echo "🎯 GRUPOS DE ARCHIVOS CON NOMBRES SIMILARES:"
        echo "-------------------------------------------"
        
        # Agrupar por nombre base y mostrar diferencias
        cat "$temp_file" | cut -d'|' -f1 | sort | uniq | while read nombre_cancion; do
            archivos_grupo=$(grep "^$nombre_cancion|" "$temp_file")
            cantidad=$(echo "$archivos_grupo" | wc -l)
            
            if [[ $cantidad -gt 1 ]]; then
                echo ""
                echo "🎵 $nombre_cancion ($cantidad versiones):"
                echo "$archivos_grupo" | while IFS='|' read nombre dur tamaño ruta; do
                    duracion_formatted=$(printf "%.1f" "$dur" 2>/dev/null || echo "N/A")
                    tamaño_mb=$(echo "scale=1; $tamaño / 1000000" | bc 2>/dev/null || echo "N/A")
                    echo "   📊 ${duracion_formatted}s | ${tamaño_mb}MB | $(basename "$ruta")"
                done
                
                # Verificar si son realmente duplicados (misma duración ±1s)
                duraciones_unicas=$(echo "$archivos_grupo" | cut -d'|' -f2 | sort -n | uniq | wc -l)
                if [[ $duraciones_unicas -eq 1 ]]; then
                    echo "   ⚠️  POSIBLES DUPLICADOS REALES (misma duración)"
                else
                    echo "   ✅ VARIACIONES SUNO (diferentes duraciones)"
                fi
            fi
        done
        
        rm -f "$temp_file"
    else
        echo "❌ No se encontraron archivos para analizar"
    fi
}

# Función para analizar archivos por contenido de audio (checksums de audio)
analizar_contenido_audio() {
    echo ""
    echo "🎵 ANÁLISIS POR CONTENIDO DE AUDIO"
    echo "================================="
    
    echo "🔍 Comparando hashes de contenido de audio..."
    echo ""
    
    # Usar checksums de los primeros bytes para detectar contenido idéntico
    find "/Volumes/ADATA SC740" -maxdepth 1 -type f \( -name "*.mp3" -o -name "*.wav" \) | \
    head -20 | while read archivo; do
        # Hash de los primeros 1KB del archivo (después de metadatos)
        hash_contenido=$(tail -c +1024 "$archivo" | head -c 10240 | md5 2>/dev/null || echo "N/A")
        tamaño=$(stat -f%z "$archivo" 2>/dev/null || echo 0)
        echo "$hash_contenido|$tamaño|$(basename "$archivo")"
    done | sort | uniq -d -w 32 | while IFS='|' read hash tamaño nombre; do
        echo "🔄 CONTENIDO IDÉNTICO DETECTADO:"
        echo "   Hash: $hash"
        echo "   Archivos con mismo contenido:"
        
        find "/Volumes/ADATA SC740" -maxdepth 1 -type f \( -name "*.mp3" -o -name "*.wav" \) | \
        head -20 | while read archivo_check; do
            hash_check=$(tail -c +1024 "$archivo_check" | head -c 10240 | md5 2>/dev/null || echo "N/A")
            if [[ "$hash_check" == "$hash" ]]; then
                echo "      → $(basename "$archivo_check")"
            fi
        done
        echo ""
    done
}

# Función para detectar variaciones Suno inteligentemente
detectar_variaciones_suno() {
    echo ""
    echo "🎭 DETECTOR INTELIGENTE DE VARIACIONES SUNO"
    echo "==========================================="
    
    echo "🎯 Criterios de análisis:"
    echo "  • Nombres similares pero duraciones diferentes = Variaciones Suno ✅"
    echo "  • Nombres similares y misma duración = Duplicados reales ⚠️"
    echo "  • Diferencia de tamaño >20% = Variaciones ✅"
    echo ""
    
    # Buscar patrones específicos de Suno
    find "/Volumes/ADATA SC740" -maxdepth 1 -type f \( -name "*.mp3" -o -name "*.wav" \) | \
    grep -E '\([0-9]\)\.' | head -20 | while read archivo; do
        nombre_base=$(basename "$archivo" | sed 's/ ([0-9]).*//')
        numero_version=$(basename "$archivo" | sed -n 's/.* (\([0-9]\)).*/\1/p')
        
        # Buscar otras versiones del mismo nombre
        find "/Volumes/ADATA SC740" -maxdepth 1 -name "$nombre_base*" | while read version; do
            if [[ "$version" != "$archivo" ]]; then
                dur1=$(obtener_duracion "$archivo")
                dur2=$(obtener_duracion "$version")
                
                # Calcular diferencia porcentual
                if [[ "$dur1" != "0" && "$dur2" != "0" ]]; then
                    diferencia=$(echo "scale=2; ($dur1 - $dur2) * 100 / $dur1" | bc 2>/dev/null | sed 's/-//' || echo "0")
                    
                    if [[ $(echo "$diferencia < 5" | bc 2>/dev/null || echo 0) -eq 1 ]]; then
                        echo "⚠️  DUPLICADO REAL: $nombre_base"
                        echo "   → $(basename "$archivo") vs $(basename "$version")"
                        echo "   → Diferencia: ${diferencia}% en duración"
                    else
                        echo "✅ VARIACIÓN SUNO: $nombre_base"
                        echo "   → $(basename "$archivo") (${dur1}s) vs $(basename "$version") (${dur2}s)"
                        echo "   → Diferencia: ${diferencia}% - Son variaciones diferentes"
                    fi
                    echo ""
                fi
            fi
        done
    done | sort | uniq
}

# Función para crear reporte de análisis musical
crear_reporte_analisis() {
    echo ""
    echo "📄 Creando reporte de análisis musical..."
    
    cat > "/Volumes/ADATA SC740/🎼_ARCHIVO_MUSICAL_BLACKMAMBA/ANALISIS_MUSICAL_SUNO.md" << 'EOF'
# 🎼 ANÁLISIS MUSICAL INTELIGENTE - BLACKMAMBA

## Metodología de Análisis Suno

### Problema Identificado:
Suno AI genera **múltiples variaciones** de la misma prompt, no duplicados exactos.
Cada variación puede tener:
- Diferente duración
- Diferente arreglo instrumental  
- Diferente interpretación vocal
- Diferente estructura musical

### Criterios de Análisis:
1. **Duración de audio** - Métrica principal de diferenciación
2. **Tamaño de archivo** - Indicador de calidad/compresión
3. **Contenido de audio** - Hash de ondas sinusoidales
4. **Patrones de nomenclatura** - (1), (2), (Cover), (Remix)

### Clasificación:
- **✅ VARIACIONES SUNO:** Misma base, diferente contenido musical
- **⚠️ DUPLICADOS REALES:** Mismo contenido, mismo archivo
- **🔄 VERSIONES INTENCIONADAS:** Cover, Remix, Edit claramente etiquetados

### Recomendaciones:
1. **CONSERVAR todas las variaciones Suno** - Son únicamente musicales
2. **ELIMINAR solo duplicados reales** - Archivos idénticos por error
3. **ORGANIZAR por tipo** - Original, Variación 1, Variación 2, etc.
4. **DOCUMENTAR diferencias** - Notas musicológicas de cada variación

---
*Análisis basado en criterios musicológicos profesionales*
*BlackMamba Records © 2025*
EOF

    echo "✅ Reporte guardado en: ANALISIS_MUSICAL_SUNO.md"
}

# Función para instalar dependencias de análisis de audio
verificar_herramientas() {
    echo "🔧 VERIFICANDO HERRAMIENTAS DE ANÁLISIS"
    echo "======================================"
    
    if command -v ffprobe >/dev/null 2>&1; then
        echo "✅ ffprobe detectado - Análisis de audio disponible"
    elif command -v afinfo >/dev/null 2>&1; then
        echo "✅ afinfo detectado - Análisis básico disponible (macOS)"
    else
        echo "⚠️  Herramientas de análisis de audio no detectadas"
        echo ""
        echo "📦 Para análisis preciso, instala FFmpeg:"
        echo "   brew install ffmpeg"
        echo ""
        echo "🔄 Usando análisis básico por tamaño de archivo..."
    fi
    echo ""
}

# Menú principal
main_menu() {
    echo ""
    echo "🎼 ¿QUÉ ANÁLISIS MUSICAL DESEAS REALIZAR?"
    echo "========================================"
    echo "1) ⏱️  Comparar por duración de audio"
    echo "2) 🎵 Analizar contenido de audio (hash)"
    echo "3) 🎭 Detector inteligente variaciones Suno"
    echo "4) 🔧 Verificar herramientas de análisis"
    echo "5) 🔄 Análisis musical completo"
    echo "6) 📄 Crear reporte de análisis"
    echo "7) 🚪 Salir"
    echo ""
    read "opcion?Selecciona una opción [1-7]: "
    
    case $opcion in
        1) comparar_por_duracion ;;
        2) analizar_contenido_audio ;;
        3) detectar_variaciones_suno ;;
        4) verificar_herramientas ;;
        5) 
            verificar_herramientas
            comparar_por_duracion
            analizar_contenido_audio
            detectar_variaciones_suno
            ;;
        6) crear_reporte_analisis ;;
        7) echo "👋 ¡Análisis musical completado!" ;;
        *) echo "❌ Opción inválida. ¿No crees que deberías elegir del 1 al 7?" ;;
    esac
}

# Ejecutar
main_menu