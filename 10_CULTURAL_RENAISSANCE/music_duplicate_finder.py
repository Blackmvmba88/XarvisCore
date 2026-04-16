#!/usr/bin/env python3
"""
🔍 BlackMamba Duplicate Finder
Encuentra canciones duplicadas por nombre, hash o similitud
"""

import json
import os
import hashlib
from collections import defaultdict
from difflib import SequenceMatcher

MUSIC_LIBRARY = "music_library.json"

def calculate_file_hash(filepath):
    """Calcula hash SHA256 de un archivo"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def normalize_title(title):
    """Normaliza título para comparación"""
    # Remover caracteres especiales, espacios extra, convertir a minúsculas
    normalized = title.lower().strip()
    # Remover etiquetas comunes
    for tag in ['(intro)', '(verse)', '(chorus)', '(bridge)', '(outro)', 
                '[official]', '[audio]', '[video]', '(official)', '(audio)']:
        normalized = normalized.replace(tag, '')
    return ' '.join(normalized.split())

def string_similarity(a, b):
    """Calcula similitud entre dos strings (0.0 - 1.0)"""
    return SequenceMatcher(None, a, b).ratio()

def find_duplicates():
    """Encuentra duplicados en la colección"""
    print("🔍 BLACKMAMBA DUPLICATE FINDER")
    print("=" * 60)
    
    with open(MUSIC_LIBRARY, 'r') as f:
        library = json.load(f)
    
    print(f"🔎 Analizando {len(library)} canciones...")
    print()
    
    # Categorías de duplicados
    exact_title_dupes = defaultdict(list)
    similar_title_dupes = []
    file_hash_dupes = defaultdict(list)
    
    # 1. Buscar duplicados exactos por título
    print("📝 Buscando duplicados exactos por título...")
    title_map = defaultdict(list)
    for song in library:
        normalized = normalize_title(song['title'])
        title_map[normalized].append(song)
    
    for title, songs in title_map.items():
        if len(songs) > 1:
            exact_title_dupes[title] = songs
    
    print(f"   ✅ {len(exact_title_dupes)} grupos de duplicados exactos")
    
    # 2. Buscar duplicados similares (90%+ similitud)
    print("🔎 Buscando títulos similares (≥90% similitud)...")
    checked_pairs = set()
    
    for i, song1 in enumerate(library):
        for song2 in library[i+1:]:
            pair_id = tuple(sorted([song1['title'], song2['title']]))
            if pair_id in checked_pairs:
                continue
            checked_pairs.add(pair_id)
            
            title1 = normalize_title(song1['title'])
            title2 = normalize_title(song2['title'])
            
            similarity = string_similarity(title1, title2)
            
            if similarity >= 0.90 and similarity < 1.0:
                similar_title_dupes.append({
                    'song1': song1,
                    'song2': song2,
                    'similarity': similarity
                })
    
    print(f"   ✅ {len(similar_title_dupes)} pares similares")
    
    # 3. Buscar duplicados por hash de archivo
    print("🔐 Calculando hashes de archivos...")
    hash_map = defaultdict(list)
    
    for i, song in enumerate(library, 1):
        print(f"   [{i}/{len(library)}]", end='\r')
        
        for path_key in ['file_path_mp3', 'file_path_wav']:
            filepath = song.get(path_key)
            if filepath and os.path.exists(filepath):
                file_hash = calculate_file_hash(filepath)
                if file_hash:
                    hash_map[file_hash].append({
                        'song': song,
                        'file': os.path.basename(filepath)
                    })
    
    for file_hash, files in hash_map.items():
        if len(files) > 1:
            file_hash_dupes[file_hash] = files
    
    print(f"\n   ✅ {len(file_hash_dupes)} grupos de duplicados por hash")
    
    # REPORTE
    print("\n" + "=" * 60)
    print("📊 REPORTE DE DUPLICADOS")
    print("=" * 60)
    
    # Duplicados exactos
    if exact_title_dupes:
        print(f"\n🔴 {len(exact_title_dupes)} GRUPOS DE TÍTULOS IDÉNTICOS:")
        for title, songs in list(exact_title_dupes.items())[:10]:
            print(f"\n   📝 '{title}'")
            for song in songs:
                location = song.get('file_path_mp3') or song.get('file_path_wav', 'Sin archivo')
                print(f"      - {song['artist']} | {os.path.basename(location)}")
    
    # Duplicados similares
    if similar_title_dupes:
        print(f"\n🟡 {len(similar_title_dupes)} PARES DE TÍTULOS SIMILARES:")
        for dupe in similar_title_dupes[:10]:
            print(f"\n   🔗 Similitud: {dupe['similarity']*100:.1f}%")
            print(f"      1) {dupe['song1']['title']} - {dupe['song1']['artist']}")
            print(f"      2) {dupe['song2']['title']} - {dupe['song2']['artist']}")
    
    # Duplicados por hash
    if file_hash_dupes:
        print(f"\n🔵 {len(file_hash_dupes)} GRUPOS DE ARCHIVOS IDÉNTICOS:")
        for file_hash, files in list(file_hash_dupes.items())[:10]:
            print(f"\n   🔐 Hash: {file_hash[:16]}...")
            for item in files:
                print(f"      - {item['song']['title']} | {item['file']}")
    
    # Resumen
    total_dupes = (len(exact_title_dupes) + 
                   len(similar_title_dupes) + 
                   len(file_hash_dupes))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"   🔴 Títulos idénticos: {len(exact_title_dupes)}")
    print(f"   🟡 Títulos similares: {len(similar_title_dupes)}")
    print(f"   🔵 Archivos idénticos: {len(file_hash_dupes)}")
    print(f"   📊 Total de problemas: {total_dupes}")
    
    # Exportar reporte
    report = {
        "exact_title_duplicates": {
            title: [{'title': s['title'], 'artist': s['artist'], 
                    'file': s.get('file_path_mp3') or s.get('file_path_wav')} 
                   for s in songs]
            for title, songs in exact_title_dupes.items()
        },
        "similar_title_duplicates": [
            {
                'song1': {'title': d['song1']['title'], 'artist': d['song1']['artist']},
                'song2': {'title': d['song2']['title'], 'artist': d['song2']['artist']},
                'similarity': d['similarity']
            }
            for d in similar_title_dupes
        ],
        "file_hash_duplicates": {
            hash_val: [{'title': item['song']['title'], 
                       'artist': item['song']['artist'], 
                       'file': item['file']} 
                      for item in files]
            for hash_val, files in file_hash_dupes.items()
        }
    }
    
    report_file = "music_duplicates_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Reporte detallado guardado en: {report_file}")
    
    # Sugerencias
    if total_dupes > 0:
        print("\n💡 RECOMENDACIONES:")
        if exact_title_dupes:
            print("   🔴 Revisar manualmente títulos idénticos (pueden ser versiones diferentes)")
        if similar_title_dupes:
            print("   🟡 Verificar títulos similares (posibles errores de tipeo)")
        if file_hash_dupes:
            print("   🔵 Eliminar archivos idénticos (ocupan espacio innecesario)")

if __name__ == "__main__":
    find_duplicates()
