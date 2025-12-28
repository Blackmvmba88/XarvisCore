#!/usr/bin/env python3
"""
🎧 BlackMamba Music Quality Analyzer
Análisis técnico de calidad de audio (bitrate, sample rate, etc.)
"""

import json
import subprocess
import os
from collections import defaultdict

MUSIC_LIBRARY = "music_library.json"

def analyze_audio_file(filepath):
    """Analiza archivo de audio usando ffprobe"""
    if not os.path.exists(filepath):
        return None
    
    try:
        # Ejecutar ffprobe para obtener información técnica
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            filepath
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            # Extraer información del stream de audio
            audio_stream = next((s for s in data.get('streams', []) 
                               if s.get('codec_type') == 'audio'), None)
            
            if audio_stream:
                return {
                    'codec': audio_stream.get('codec_name', 'unknown'),
                    'bitrate': int(audio_stream.get('bit_rate', 0)) // 1000,  # kbps
                    'sample_rate': int(audio_stream.get('sample_rate', 0)) // 1000,  # kHz
                    'channels': audio_stream.get('channels', 0),
                    'duration': float(data.get('format', {}).get('duration', 0))
                }
    except Exception as e:
        print(f"   ⚠️ Error analizando {os.path.basename(filepath)}: {e}")
    
    return None

def analyze_collection():
    """Analiza toda la colección musical"""
    print("🎧 BLACKMAMBA QUALITY ANALYZER")
    print("=" * 60)
    print("⚠️ Nota: Requiere ffprobe instalado (brew install ffmpeg)")
    print()
    
    # Verificar si ffprobe está disponible
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffprobe no encontrado. Instala con: brew install ffmpeg")
        return
    
    with open(MUSIC_LIBRARY, 'r') as f:
        library = json.load(f)
    
    print(f"🔍 Analizando {len(library)} canciones...")
    print()
    
    # Estadísticas
    bitrates = defaultdict(int)
    sample_rates = defaultdict(int)
    codecs = defaultdict(int)
    durations = []
    quality_tiers = {
        'high': [],      # 320 kbps o superior
        'medium': [],    # 192-319 kbps
        'low': [],       # 128-191 kbps
        'poor': []       # < 128 kbps
    }
    
    total_analyzed = 0
    total_duration = 0
    
    for i, song in enumerate(library, 1):
        print(f"   [{i}/{len(library)}] {song['title'][:40]}", end='\r')
        
        # Analizar MP3 (prioritario)
        filepath = song.get('file_path_mp3')
        if not filepath or not os.path.exists(filepath):
            filepath = song.get('file_path_wav')
        
        if not filepath or not os.path.exists(filepath):
            continue
        
        info = analyze_audio_file(filepath)
        
        if info:
            total_analyzed += 1
            
            # Estadísticas
            bitrates[info['bitrate']] += 1
            sample_rates[info['sample_rate']] += 1
            codecs[info['codec']] += 1
            durations.append(info['duration'])
            total_duration += info['duration']
            
            # Clasificar por calidad
            song_info = f"{song['title']} - {song['artist']} ({info['bitrate']} kbps)"
            
            if info['bitrate'] >= 320:
                quality_tiers['high'].append(song_info)
            elif info['bitrate'] >= 192:
                quality_tiers['medium'].append(song_info)
            elif info['bitrate'] >= 128:
                quality_tiers['low'].append(song_info)
            else:
                quality_tiers['poor'].append(song_info)
    
    print("\n")
    print("=" * 60)
    print("📊 ANÁLISIS DE CALIDAD")
    print("=" * 60)
    
    # Resumen general
    print(f"\n✅ {total_analyzed} archivos analizados")
    
    if total_duration > 0:
        hours = int(total_duration // 3600)
        minutes = int((total_duration % 3600) // 60)
        print(f"⏱️ Duración total: {hours}h {minutes}m")
    
    # Bitrate
    print(f"\n🎵 BITRATE:")
    sorted_bitrates = sorted(bitrates.items(), reverse=True)
    for bitrate, count in sorted_bitrates[:10]:
        percentage = (count / total_analyzed) * 100
        print(f"   {bitrate} kbps: {count} canciones ({percentage:.1f}%)")
    
    # Sample Rate
    print(f"\n📡 SAMPLE RATE:")
    sorted_rates = sorted(sample_rates.items(), reverse=True)
    for rate, count in sorted_rates:
        percentage = (count / total_analyzed) * 100
        print(f"   {rate} kHz: {count} canciones ({percentage:.1f}%)")
    
    # Códecs
    print(f"\n🎼 CÓDECS:")
    for codec, count in sorted(codecs.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_analyzed) * 100
        print(f"   {codec.upper()}: {count} canciones ({percentage:.1f}%)")
    
    # Tiers de calidad
    print(f"\n🏆 TIERS DE CALIDAD:")
    print(f"   🥇 Alta (≥320 kbps): {len(quality_tiers['high'])} canciones")
    print(f"   🥈 Media (192-319 kbps): {len(quality_tiers['medium'])} canciones")
    print(f"   🥉 Baja (128-191 kbps): {len(quality_tiers['low'])} canciones")
    print(f"   ⚠️ Pobre (<128 kbps): {len(quality_tiers['poor'])} canciones")
    
    # Mostrar canciones de baja calidad
    if quality_tiers['poor']:
        print(f"\n⚠️ CANCIONES DE BAJA CALIDAD:")
        for song in quality_tiers['poor'][:10]:
            print(f"   - {song}")
    
    # Estadísticas de duración
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print(f"\n⏱️ DURACIÓN:")
        print(f"   Promedio: {int(avg_duration // 60)}:{int(avg_duration % 60):02d}")
        print(f"   Más corta: {int(min_duration // 60)}:{int(min_duration % 60):02d}")
        print(f"   Más larga: {int(max_duration // 60)}:{int(max_duration % 60):02d}")
    
    # Exportar reporte detallado
    report_file = "music_quality_report.json"
    report = {
        "total_analyzed": total_analyzed,
        "total_duration_seconds": total_duration,
        "bitrates": dict(bitrates),
        "sample_rates": dict(sample_rates),
        "codecs": dict(codecs),
        "quality_tiers": {k: len(v) for k, v in quality_tiers.items()},
        "low_quality_songs": quality_tiers['poor']
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Reporte detallado guardado en: {report_file}")

if __name__ == "__main__":
    analyze_collection()
