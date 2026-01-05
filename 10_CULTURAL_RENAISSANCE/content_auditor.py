#!/usr/bin/env python3
"""
🦅 BlackMamba Content Audit
Auditoría completa de organización de contenido multimedia
Arquitecto: Iyari Cancino Gomez
Fecha: 1 de Enero, 2026
"""

import os
import json
from pathlib import Path
from collections import defaultdict

class ContentAuditor:
    """Auditor de contenido multimedia"""
    
    def __init__(self):
        self.home = Path.home()
        self.desktop = self.home / "Desktop"
        self.xarvis = self.desktop / "XarvisCore"
        self.renaissance = self.xarvis / "10_CULTURAL_RENAISSANCE"
        
        self.report = {
            'music': {},
            'videos': {},
            'downloads': {},
            'organization_tools': [],
            'issues': [],
            'recommendations': []
        }
    
    def check_music_organization(self):
        """Verifica organización de música"""
        print("🎵 Analizando MÚSICA...")
        
        # Biblioteca principal
        music_lib = self.renaissance / "music_library.json"
        if music_lib.exists():
            try:
                size_mb = music_lib.stat().st_size / (1024*1024)
                self.report['music']['library_exists'] = True
                self.report['music']['library_size_mb'] = round(size_mb, 2)
                print(f"  ✅ music_library.json existe ({size_mb:.1f} MB)")
            except:
                self.report['music']['library_exists'] = False
                print(f"  ⚠️  music_library.json existe pero no se puede leer")
        else:
            self.report['music']['library_exists'] = False
            print(f"  ❌ music_library.json NO encontrado")
            self.report['issues'].append("Necesitas escanear tu biblioteca musical")
        
        # Fingerprints de audio
        audio_fp = self.renaissance / "audio_fingerprints.json"
        if audio_fp.exists():
            size_mb = audio_fp.stat().st_size / (1024*1024)
            self.report['music']['fingerprints_exist'] = True
            self.report['music']['fingerprints_size_mb'] = round(size_mb, 2)
            print(f"  ✅ audio_fingerprints.json existe ({size_mb:.1f} MB)")
        
        # Reportes de duplicados
        duplicates = self.renaissance / "music_duplicates_report.json"
        if duplicates.exists():
            self.report['music']['duplicates_checked'] = True
            print(f"  ✅ Reporte de duplicados existe")
        else:
            self.report['music']['duplicates_checked'] = False
            print(f"  ⚠️  Sin reporte de duplicados")
            self.report['recommendations'].append("Ejecutar: python3 music_duplicate_finder.py")
        
        # Archivo musical organizado
        archivo = self.renaissance / "archivo_musical"
        if archivo.exists():
            self.report['music']['organized_archive'] = True
            print(f"  ✅ Directorio archivo_musical existe")
        else:
            self.report['music']['organized_archive'] = False
    
    def check_videos_organization(self):
        """Verifica organización de videos"""
        print("\n🎬 Analizando VIDEOS Y PELÍCULAS...")
        
        locations = {
            'Movies': self.home / "Movies",
            'Desktop/Videos': self.desktop / "Videos",
            'Downloads': self.home / "Downloads"
        }
        
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'}
        
        for name, path in locations.items():
            if path.exists():
                videos = list(path.rglob('*'))
                video_files = [f for f in videos if f.is_file() and f.suffix.lower() in video_extensions]
                
                if video_files:
                    total_size = sum(f.stat().st_size for f in video_files if f.exists())
                    size_gb = total_size / (1024**3)
                    
                    self.report['videos'][name] = {
                        'count': len(video_files),
                        'size_gb': round(size_gb, 2)
                    }
                    
                    print(f"  📹 {name}: {len(video_files)} archivos ({size_gb:.1f} GB)")
                else:
                    print(f"  ✅ {name}: Vacío/Organizado")
    
    def check_downloads_chaos(self):
        """Verifica caos en Downloads"""
        print("\n📥 Analizando DOWNLOADS...")
        
        downloads = self.home / "Downloads"
        if not downloads.exists():
            print("  ✅ Downloads no existe o está vacío")
            return
        
        categories = {
            'music': {'.mp3', '.wav', '.flac', '.m4a', '.aac'},
            'video': {'.mp4', '.mkv', '.avi', '.mov'},
            'images': {'.jpg', '.png', '.gif', '.jpeg'},
            'documents': {'.pdf', '.doc', '.docx', '.txt'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz'}
        }
        
        counts = defaultdict(int)
        
        try:
            for item in downloads.iterdir():
                if item.is_file():
                    ext = item.suffix.lower()
                    categorized = False
                    for cat, exts in categories.items():
                        if ext in exts:
                            counts[cat] += 1
                            categorized = True
                            break
                    if not categorized:
                        counts['otros'] += 1
        except:
            pass
        
        total = sum(counts.values())
        
        if total == 0:
            print("  ✅ Downloads está vacío/limpio")
            self.report['downloads']['status'] = 'clean'
        elif total < 20:
            print(f"  ⚠️  {total} archivos sin organizar (manejable)")
            self.report['downloads']['status'] = 'manageable'
            self.report['downloads']['file_count'] = total
            for cat, count in counts.items():
                print(f"     • {cat}: {count}")
        else:
            print(f"  🔥 {total} archivos sin organizar (CAOS)")
            self.report['downloads']['status'] = 'chaos'
            self.report['downloads']['file_count'] = total
            for cat, count in counts.items():
                print(f"     • {cat}: {count}")
            self.report['issues'].append("Downloads necesita limpieza urgente")
            self.report['recommendations'].append("Ejecutar: cd 14_CREATIVE_TOOLS && python3 downloads_organizer.py --execute")
    
    def check_organization_tools(self):
        """Lista herramientas de organización disponibles"""
        print("\n🛠️  HERRAMIENTAS DE ORGANIZACIÓN DISPONIBLES:")
        
        tools = [
            ('10_CULTURAL_RENAISSANCE/scan_music_library.py', 'Escanear biblioteca musical'),
            ('10_CULTURAL_RENAISSANCE/music_duplicate_finder.py', 'Encontrar duplicados de música'),
            ('10_CULTURAL_RENAISSANCE/organize_music.py', 'Organizar música'),
            ('10_CULTURAL_RENAISSANCE/music_backup_manager.py', 'Backup de música'),
            ('10_CULTURAL_RENAISSANCE/sync_to_usb.sh', 'Sincronizar a USB'),
            ('14_CREATIVE_TOOLS/downloads_organizer.py', 'Organizar Downloads → USB'),
        ]
        
        for tool, description in tools:
            tool_path = self.xarvis / tool
            exists = "✅" if tool_path.exists() else "❌"
            print(f"  {exists} {description}")
            if tool_path.exists():
                self.report['organization_tools'].append({
                    'path': tool,
                    'description': description,
                    'exists': True
                })
    
    def generate_action_plan(self):
        """Genera plan de acción"""
        print("\n" + "="*60)
        print("📋 PLAN DE ACCIÓN RECOMENDADO")
        print("="*60)
        
        if not self.report['music'].get('library_exists'):
            print("\n🎵 MÚSICA - Prioridad ALTA:")
            print("  1. python3 10_CULTURAL_RENAISSANCE/scan_music_library.py")
            print("  2. python3 10_CULTURAL_RENAISSANCE/music_duplicate_finder.py")
        elif not self.report['music'].get('duplicates_checked'):
            print("\n🎵 MÚSICA - Verificar duplicados:")
            print("  1. python3 10_CULTURAL_RENAISSANCE/music_duplicate_finder.py")
        else:
            print("\n✅ MÚSICA - Bien organizada")
        
        downloads_status = self.report['downloads'].get('status')
        if downloads_status == 'chaos':
            print("\n📥 DOWNLOADS - Prioridad URGENTE:")
            print("  1. cd 14_CREATIVE_TOOLS")
            print("  2. python3 downloads_organizer.py --execute")
        elif downloads_status == 'manageable':
            print("\n📥 DOWNLOADS - Limpieza sugerida:")
            print("  1. python3 14_CREATIVE_TOOLS/downloads_organizer.py")
        else:
            print("\n✅ DOWNLOADS - Limpio")
        
        video_count = sum(v.get('count', 0) for v in self.report['videos'].values())
        if video_count > 0:
            print("\n🎬 VIDEOS - Acción sugerida:")
            print("  1. Revisar manualmente en:")
            for loc, data in self.report['videos'].items():
                if data.get('count', 0) > 0:
                    print(f"     • {loc}: {data['count']} archivos")
            print("  2. Considerar crear organizador de videos similar")
        else:
            print("\n✅ VIDEOS - Organizados")
        
        print("\n" + "="*60)
    
    def run(self):
        """Ejecuta auditoría completa"""
        print("🦅 BLACKMAMBA CONTENT AUDIT")
        print("="*60)
        
        self.check_music_organization()
        self.check_videos_organization()
        self.check_downloads_chaos()
        self.check_organization_tools()
        self.generate_action_plan()
        
        # Guardar reporte
        report_file = self.renaissance / "content_audit_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado: {report_file}")

if __name__ == "__main__":
    auditor = ContentAuditor()
    auditor.run()
