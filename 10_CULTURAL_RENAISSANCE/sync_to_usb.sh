#!/bin/bash

# 🦅 BLACKMAMBA USB SYNC SCRIPT
# Sincronización bidireccional con el USB

MUSIC_VAULT="$HOME/Desktop/BlackMamba_Music_Vault"
USB_PATHS=(
    "/Volumes/ADATA SC740/BlackMamba_Music_Arsenal"
    "/Volumes/ADATA/BlackMamba_Music_Arsenal"
    "/Volumes/SC740/BlackMamba_Music_Arsenal"
)

USB_DIR=""
for path in "${USB_PATHS[@]}"; do
    if [ -d "$path" ]; then
        USB_DIR="$path"
        break
    fi
done

if [ -z "$USB_DIR" ]; then
    echo "❌ USB no detectado. Conectar ADATA SC740."
    exit 1
fi

echo "🦅 BLACKMAMBA USB SYNC"
echo "======================================"
echo "📁 Local: $MUSIC_VAULT"
echo "💾 USB: $USB_DIR"
echo ""

# Función de sincronización
sync_folder() {
    local folder=$1
    echo "🔄 Sincronizando: $folder"
    
    # Local → USB (archivos nuevos/modificados)
    rsync -avh --progress \
        "$MUSIC_VAULT/$folder/" \
        "$USB_DIR/$folder/"
    
    # USB → Local (si hay archivos en USB que no están localmente)
    rsync -avh --progress --ignore-existing \
        "$USB_DIR/$folder/" \
        "$MUSIC_VAULT/$folder/"
    
    echo "✅ $folder sincronizado"
    echo ""
}

# Sincronizar todas las carpetas
sync_folder "WAV_Masters"
sync_folder "MP3_Distribution"
sync_folder "FLAC_Archive"

# Backup de music_library.json
echo "💾 Backup de biblioteca..."
cp "$HOME/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE/music_library.json" \
   "$USB_DIR/Backups/music_library_$(date +%Y%m%d_%H%M%S).json"

echo "======================================"
echo "✅ Sincronización completa. Arsenal protegido."
