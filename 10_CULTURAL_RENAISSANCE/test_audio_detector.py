#!/usr/bin/env python3
"""
Tests para BlackMamba Audio Detector
Dominio: 10_CULTURAL_RENAISSANCE
Arquitecto: Iyari Cancino Gomez
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from audio_detector import AudioFingerprinter, AudioRecorder

def test_fingerprinter_initialization():
    """Test 1: Inicialización de AudioFingerprinter."""
    print("🧪 Test 1: Inicialización de AudioFingerprinter...")
    
    fp = AudioFingerprinter()
    assert fp is not None, "❌ Fingerprinter no inicializado"
    assert isinstance(fp.fingerprints, dict), "❌ Fingerprints no es dict"
    
    print("✅ Test 1 PASSED")
    return True

def test_chromaprint_installed():
    """Test 2: Verificar chromaprint instalado."""
    print("\n🧪 Test 2: Verificar chromaprint instalado...")
    
    fp = AudioFingerprinter()
    installed = fp.check_fpcalc_installed()
    assert installed, "❌ chromaprint/fpcalc no está instalado"
    
    print("✅ Test 2 PASSED")
    return True

def test_recorder_initialization():
    """Test 3: Inicialización de AudioRecorder."""
    print("\n🧪 Test 3: Inicialización de AudioRecorder...")
    
    recorder = AudioRecorder()
    assert recorder is not None, "❌ Recorder no inicializado"
    assert recorder.recordings_dir.exists(), "❌ Directorio de grabaciones no creado"
    
    print(f"   📁 Directorio: {recorder.recordings_dir}")
    print("✅ Test 3 PASSED")
    return True

def test_fingerprint_comparison():
    """Test 4: Comparación de fingerprints."""
    print("\n🧪 Test 4: Comparación de fingerprints...")
    
    fp = AudioFingerprinter()
    
    # Fingerprints idénticos
    fp1 = "1,2,3,4,5,6,7,8,9,10"
    fp2 = "1,2,3,4,5,6,7,8,9,10"
    similarity = fp.compare_fingerprints(fp1, fp2)
    assert similarity >= 0.95, f"❌ Similitud de idénticos debe ser >0.95 (obtenido: {similarity})"
    print(f"   Idénticos: {similarity*100:.1f}%")
    
    # Fingerprints diferentes
    fp3 = "100,200,300,400,500,600,700,800,900,1000"
    similarity2 = fp.compare_fingerprints(fp1, fp3)
    assert similarity2 < 0.1, f"❌ Similitud de diferentes debe ser <0.1 (obtenido: {similarity2})"
    print(f"   Diferentes: {similarity2*100:.1f}%")
    
    # Fingerprints parcialmente similares
    fp4 = "1,2,3,4,5,100,200,300,400,500"
    similarity3 = fp.compare_fingerprints(fp1, fp4)
    print(f"   Parcialmente similares: {similarity3*100:.1f}%")
    
    print("✅ Test 4 PASSED")
    return True

def test_database_operations():
    """Test 5: Operaciones de base de datos."""
    print("\n🧪 Test 5: Operaciones de base de datos...")
    
    fp = AudioFingerprinter()
    
    # Guardar estado original
    original_fingerprints = fp.fingerprints.copy()
    
    # Agregar fingerprint de prueba
    test_song = {
        'song_name': 'test_song',
        'title': 'Test Song',
        'artist': 'Test Artist'
    }
    
    fp.fingerprints['test_song'] = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'fingerprint': '1,2,3,4,5',
        'type': 'test',
        'duration': 180
    }
    
    # Guardar
    fp._save_fingerprints()
    
    # Crear nueva instancia y verificar carga
    fp2 = AudioFingerprinter()
    assert 'test_song' in fp2.fingerprints, "❌ Fingerprint de prueba no se cargó"
    assert fp2.fingerprints['test_song']['title'] == 'Test Song', "❌ Datos incorrectos"
    
    # Restaurar estado original
    fp.fingerprints = original_fingerprints
    fp._save_fingerprints()
    
    print("✅ Test 5 PASSED")
    return True

def test_vpa_integration():
    """Test 6: Integración con VPA."""
    print("\n🧪 Test 6: Integración VPA + Detector...")
    
    try:
        from vpa_with_detector import VPAWithDetector
        
        vpa = VPAWithDetector()
        assert vpa is not None, "❌ VPAWithDetector no inicializado"
        assert hasattr(vpa, 'detector'), "❌ No tiene atributo 'detector'"
        assert hasattr(vpa, 'recorder'), "❌ No tiene atributo 'recorder'"
        assert len(vpa.library_data) > 0, "❌ Biblioteca vacía"
        
        print(f"   Biblioteca: {len(vpa.library_data)} canciones")
        print(f"   Fingerprints: {len(vpa.detector.fingerprints)} indexados")
        
        print("✅ Test 6 PASSED")
        return True
        
    except ImportError as e:
        print(f"⚠️  Test 6 SKIPPED: {e}")
        return True

def test_music_library_loaded():
    """Test 7: Biblioteca musical cargada."""
    print("\n🧪 Test 7: Biblioteca musical cargada...")
    
    library_path = Path(__file__).parent / "music_library.json"
    assert library_path.exists(), "❌ music_library.json no existe"
    
    with open(library_path, encoding='utf-8') as f:
        library = json.load(f)
    
    assert isinstance(library, list), "❌ Biblioteca debe ser lista"
    assert len(library) > 0, "❌ Biblioteca vacía"
    
    # Verificar estructura de canciones
    first_song = library[0]
    required_fields = ['song_name', 'title', 'artist', 'formats', 'status']
    for field in required_fields:
        assert field in first_song, f"❌ Campo '{field}' faltante"
    
    print(f"   Total canciones: {len(library)}")
    print(f"   Estructura: OK")
    print("✅ Test 7 PASSED")
    return True

def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("🦅 BLACKMAMBA AUDIO DETECTOR - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_fingerprinter_initialization,
        test_chromaprint_installed,
        test_recorder_initialization,
        test_fingerprint_comparison,
        test_database_operations,
        test_vpa_integration,
        test_music_library_loaded
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADOS: {passed} PASSED, {failed} FAILED")
    print("=" * 60)
    
    if failed == 0:
        print("✅ TODOS LOS TESTS PASARON")
        return 0
    else:
        print(f"❌ {failed} TESTS FALLARON")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
