#!/usr/bin/env python3
"""
🧹 BLACKMAMBA FILE NAME SANITIZER
Limpia nombres problemáticos para compatibilidad total con USB/FAT32
"""

import os
import re
from pathlib import Path

def sanitize_filename(name):
    """Limpiar nombre de archivo para máxima compatibilidad"""
    # Preservar extensión
    base, ext = os.path.splitext(name)
    
    # Eliminar caracteres problemáticos para FAT32/NTFS
    base = re.sub(r'[<>:"/\\|?*]', '', base)
    
    # Convertir múltiples espacios en uno solo
    base = re.sub(r'\s+', ' ', base)
    
    # Eliminar espacios al inicio/final
    base = base.strip()
    
    # Si el nombre queda vacío, usar "Untitled"
    if not base:
        base = "Untitled"
    
    return f"{base}{ext}"

def sanitize_vault():
    vault = Path.home() / "Desktop" / "BlackMamba_Music_Vault"
    
    for root, dirs, files in os.walk(vault):
        for filename in files:
            if not filename.endswith(('.mp3', '.wav', '.flac')):
                continue
            
            old_path = Path(root) / filename
            new_filename = sanitize_filename(filename)
            
            if filename != new_filename:
                new_path = Path(root) / new_filename
                
                # Si ya existe, agregar sufijo
                counter = 1
                while new_path.exists():
                    base, ext = os.path.splitext(new_filename)
                    new_path = Path(root) / f"{base}_{counter}{ext}"
                    counter += 1
                
                print(f"🔧 {filename} → {new_path.name}")
                old_path.rename(new_path)

if __name__ == "__main__":
    print("🧹 Limpiando nombres para compatibilidad USB...")
    sanitize_vault()
    print("✅ Nombres sanitizados. Listo para sincronización total.")
