#!/usr/bin/env python3
"""
🎵 XARVIS SUNO TERMINAL
Sistema unificado de control de Suno desde terminal
Arquitecto: Iyari Cancino Gomez
"""

import os
import sys
from pathlib import Path

# Colores para terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Muestra el header del sistema"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}🎵 XARVIS SUNO TERMINAL{Colors.RESET}")
    print(f"{Colors.CYAN}Sistema Unificado de Control Musical{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_menu():
    """Menú principal"""
    print(f"{Colors.BOLD}HERRAMIENTAS DISPONIBLES:{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}📦 1. SUNO ORGANIZER{Colors.RESET} - Gestión completa")
    print(f"   → Escanear descargas de Suno")
    print(f"   → Detectar duplicados")
    print(f"   → Organizar biblioteca")
    print(f"   → Exportar playlists\n")
    
    print(f"{Colors.CYAN}🎼 2. AFINADOR SUNO{Colors.RESET} - Análisis musical")
    print(f"   → Listar canciones")
    print(f"   → Analizar frecuencias (F0)")
    print(f"   → Procesar audio\n")
    
    print(f"{Colors.MAGENTA}⬇️  3. SUNO EXTRACTOR{Colors.RESET} - Descarga directa")
    print(f"   → Extraer de URLs")
    print(f"   → Validar enlaces")
    print(f"   → Descarga automática\n")
    
    print(f"{Colors.YELLOW}📊 4. VER ESTADÍSTICAS{Colors.RESET} - Estado de biblioteca\n")
    
    print(f"{Colors.RED}🚪 5. SALIR{Colors.RESET}\n")

def run_suno_organizer():
    """Ejecutar Suno Organizer"""
    print(f"\n{Colors.GREEN}=== SUNO ORGANIZER ==={Colors.RESET}\n")
    print("Comandos disponibles:\n")
    
    commands = {
        "1": ("Listar canciones Suno", "suno-org list-suno"),
        "2": ("Escanear y crear índice", "suno-org scan-audio-cmd"),
        "3": ("Detectar duplicados (simulación)", "suno-org dedupe"),
        "4": ("Mover duplicados (aplicar)", "suno-org dedupe --apply"),
        "5": ("Descargar de URL", "suno-org download-url <URL>"),
        "6": ("Volver al menú principal", None)
    }
    
    for key, (desc, cmd) in commands.items():
        print(f"  {key}. {desc}")
        if cmd:
            print(f"     {Colors.CYAN}$ {cmd}{Colors.RESET}")
    
    print()
    choice = input("Opción (1-6): ").strip()
    
    if choice == "6":
        return
    
    if choice in commands and commands[choice][1]:
        print(f"\n{Colors.YELLOW}Ejecutando...{Colors.RESET}\n")
        os.system(commands[choice][1])
        input(f"\n{Colors.GREEN}Presiona Enter para continuar...{Colors.RESET}")

def run_afinador():
    """Ejecutar Afinador Suno"""
    print(f"\n{Colors.CYAN}=== AFINADOR SUNO ==={Colors.RESET}\n")
    
    commands = {
        "1": ("Listar todas las canciones", "afinador-suno list"),
        "2": ("Listar solo de Suno", "afinador-suno list --source=suno"),
        "3": ("Analizar canción por ID", "afinador-suno analyze --id=<ID>"),
        "4": ("Volver al menú principal", None)
    }
    
    for key, (desc, cmd) in commands.items():
        print(f"  {key}. {desc}")
        if cmd:
            print(f"     {Colors.CYAN}$ {cmd}{Colors.RESET}")
    
    print()
    choice = input("Opción (1-4): ").strip()
    
    if choice == "4":
        return
    
    if choice == "3":
        song_id = input(f"\n{Colors.YELLOW}ID de la canción (primeros caracteres): {Colors.RESET}")
        os.system(f"afinador-suno analyze --id={song_id}")
    elif choice in commands and commands[choice][1]:
        print(f"\n{Colors.YELLOW}Ejecutando...{Colors.RESET}\n")
        os.system(commands[choice][1])
    
    input(f"\n{Colors.GREEN}Presiona Enter para continuar...{Colors.RESET}")

def run_extractor():
    """Ejecutar Suno Extractor"""
    print(f"\n{Colors.MAGENTA}=== SUNO EXTRACTOR ==={Colors.RESET}\n")
    
    base_path = Path(__file__).parent / "suno-suite/tools/suno-extractor"
    
    print("Opciones:\n")
    print(f"  1. Quick Start (menú guiado)")
    print(f"  2. Extraer URL específica")
    print(f"  3. Validar URLs")
    print(f"  4. Volver al menú principal\n")
    
    choice = input("Opción (1-4): ").strip()
    
    if choice == "4":
        return
    elif choice == "1":
        quick_start = base_path / "suno_quick_start.py"
        if quick_start.exists():
            os.system(f"python3 {quick_start}")
        else:
            print(f"{Colors.RED}❌ Quick Start no encontrado{Colors.RESET}")
    elif choice == "2":
        url = input(f"\n{Colors.YELLOW}URL de Suno: {Colors.RESET}")
        extractor = base_path / "suno_real_extractor.py"
        if extractor.exists():
            # Aquí iría la lógica de extracción con la URL
            print(f"{Colors.GREEN}Extrayendo: {url}{Colors.RESET}")
            os.system(f"python3 {extractor}")
        else:
            print(f"{Colors.RED}❌ Extractor no encontrado{Colors.RESET}")
    elif choice == "3":
        validator = base_path / "suno_url_validator.py"
        if validator.exists():
            os.system(f"python3 {validator}")
        else:
            print(f"{Colors.RED}❌ Validador no encontrado{Colors.RESET}")
    
    input(f"\n{Colors.GREEN}Presiona Enter para continuar...{Colors.RESET}")

def show_stats():
    """Mostrar estadísticas de biblioteca"""
    print(f"\n{Colors.YELLOW}=== ESTADÍSTICAS ==={Colors.RESET}\n")
    
    # Intentar obtener estadísticas
    suno_root = Path.home() / "Music" / "Suno"
    if suno_root.exists():
        audio_files = list(suno_root.rglob("*.mp3")) + list(suno_root.rglob("*.wav"))
        print(f"📁 Directorio Suno: {suno_root}")
        print(f"🎵 Archivos de audio: {len(audio_files)}")
    else:
        print(f"⚠️  Directorio Suno no encontrado en ubicación estándar")
    
    print(f"\n{Colors.CYAN}Para ver estadísticas detalladas:{Colors.RESET}")
    print(f"  $ suno-org list-suno --limit=100")
    
    input(f"\n{Colors.GREEN}Presiona Enter para continuar...{Colors.RESET}")

def show_quick_commands():
    """Comandos rápidos"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}COMANDOS RÁPIDOS:{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}Organizer:{Colors.RESET}")
    print(f"  suno-org list-suno              # Listar canciones")
    print(f"  suno-org scan-audio-cmd         # Escanear biblioteca")
    print(f"  suno-org dedupe                 # Ver duplicados")
    print(f"  suno-org dedupe --apply         # Mover duplicados")
    print(f"  suno-org download-url <URL>     # Descargar canción\n")
    
    print(f"{Colors.CYAN}Afinador:{Colors.RESET}")
    print(f"  afinador-suno list              # Listar todo")
    print(f"  afinador-suno list --source=suno # Solo Suno")
    print(f"  afinador-suno analyze --id=abc  # Analizar por ID\n")
    
    print(f"{Colors.MAGENTA}Paths de Extractor:{Colors.RESET}")
    print(f"  ~/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE/suno-suite/tools/suno-extractor/\n")

def main():
    """Función principal"""
    
    # Cambiar al directorio correcto
    os.chdir(Path(__file__).parent)
    
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        print_header()
        print_menu()
        
        choice = input(f"{Colors.BOLD}Selecciona una opción (1-5): {Colors.RESET}").strip()
        
        if choice == "1":
            run_suno_organizer()
        elif choice == "2":
            run_afinador()
        elif choice == "3":
            run_extractor()
        elif choice == "4":
            show_stats()
        elif choice == "5":
            print(f"\n{Colors.GREEN}👋 Hasta luego, Arquitecto!{Colors.RESET}\n")
            break
        else:
            print(f"\n{Colors.RED}❌ Opción inválida{Colors.RESET}")
            input(f"{Colors.GREEN}Presiona Enter para continuar...{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.RESET}\n")
        sys.exit(0)
