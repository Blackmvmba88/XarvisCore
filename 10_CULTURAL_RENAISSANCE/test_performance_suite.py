#!/usr/bin/env python3
"""
BlackMamba Music Performance Suite - Test Suite (Simplified)
Arquitecto: Iyari Cancino Gomez
Fecha: 28 de Diciembre, 2025

Suite simplificada y robusta de tests para el Performance Suite.
"""

import unittest
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestFiles(unittest.TestCase):
    """Tests de archivos y configuración"""
    
    def test_all_files_exist(self):
        """Verificar que todos los archivos necesarios existen"""
        files = [
            'music_performance_suite.py',
            'start_performance_suite.sh',
            'music_library.json',
            'audio_fingerprints.json'
        ]
        
        for f in files:
            self.assertTrue(os.path.exists(f), f"Falta: {f}")
    
    def test_executables(self):
        """Verificar permisos de ejecución"""
        self.assertTrue(os.access('music_performance_suite.py', os.X_OK))
        self.assertTrue(os.access('start_performance_suite.sh', os.X_OK))


class TestMusicLibrary(unittest.TestCase):
    """Tests de la biblioteca musical"""
    
    @classmethod
    def setUpClass(cls):
        with open('music_library.json', 'r') as f:
            cls.library = json.load(f)
    
    def test_library_not_empty(self):
        """Biblioteca no está vacía"""
        self.assertGreater(len(self.library), 0)
    
    def test_library_count(self):
        """Verificar cantidad esperada de canciones"""
        self.assertEqual(len(self.library), 194)
    
    def test_basic_structure(self):
        """Verificar estructura básica de canciones"""
        for song in self.library[:5]:
            self.assertIn('title', song)
            self.assertIn('artist', song)
    
    def test_json_valid(self):
        """JSON es válido"""
        self.assertIsInstance(self.library, list)


class TestDependencies(unittest.TestCase):
    """Tests de dependencias"""
    
    def test_flask_available(self):
        """Flask disponible"""
        try:
            import flask
            import flask_cors
        except ImportError as e:
            self.fail(f"Flask import failed: {e}")
    
    def test_psutil_available(self):
        """psutil disponible"""
        try:
            import psutil
        except ImportError as e:
            self.fail(f"psutil import failed: {e}")


class TestIntegration(unittest.TestCase):
    """Tests de integración"""
    
    def test_music_manager_exists(self):
        """Music Manager existe"""
        self.assertTrue(os.path.exists('music_manager.sh'))
    
    def test_performance_suite_in_menu(self):
        """Performance Suite en menú"""
        with open('music_manager.sh', 'r') as f:
            content = f.read()
        self.assertIn('Performance Suite', content)
    
    def test_documentation_exists(self):
        """Documentación completa"""
        docs = [
            'PERFORMANCE_SUITE_README.md',
            'INTEGRATION_COMPLETE.md',
            'PERFORMANCE_SUITE_VALIDATION.md'
        ]
        for doc in docs:
            self.assertTrue(os.path.exists(doc), f"Falta: {doc}")


class TestPerformance(unittest.TestCase):
    """Tests de performance"""
    
    def test_library_loads_fast(self):
        """Library carga rápido"""
        start = time.time()
        with open('music_library.json', 'r') as f:
            json.load(f)
        elapsed = time.time() - start
        self.assertLess(elapsed, 2.0, f"Muy lento: {elapsed}s")
    
    def test_file_sizes_reasonable(self):
        """Archivos de tamaño razonable"""
        lib_size = os.path.getsize('music_library.json')
        fp_size = os.path.getsize('audio_fingerprints.json')
        
        self.assertLess(lib_size, 10 * 1024 * 1024)  # < 10MB
        self.assertLess(fp_size, 20 * 1024 * 1024)   # < 20MB


def run_tests():
    """Ejecutar suite de tests"""
    
    print("="  * 70)
    print("  BLACKMAMBA MUSIC PERFORMANCE SUITE - TEST SUITE")
    print("  Arquitecto: Iyari Cancino Gomez")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestFiles,
        TestMusicLibrary,
        TestDependencies,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print("  RESUMEN")
    print("=" * 70)
    print(f"Total: {result.testsRun}")
    print(f"✅ Pasados: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Fallidos: {len(result.failures)}")
    print(f"⚠️  Errores: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        return 0
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
