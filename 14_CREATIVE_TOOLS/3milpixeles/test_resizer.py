#!/usr/bin/env python3
"""
Test script for image_resizer_3000.py
Tests the core image resizing functionality without GUI
"""

import sys
import os
from PIL import Image, ImageOps
import tempfile
import shutil

# Test the resizing methods directly without needing tkinter


def create_test_image(width, height, color=(255, 0, 0)):
    """Create a test image with given dimensions"""
    img = Image.new('RGB', (width, height), color)
    return img


def resize_fit(img):
    """Redimensiona ajustando dentro del cuadrado con márgenes"""
    # Crear imagen cuadrada blanca
    result = Image.new('RGB', (3000, 3000), (255, 255, 255))
    
    # Redimensionar manteniendo proporción
    img.thumbnail((3000, 3000), Image.Resampling.LANCZOS)
    
    # Centrar la imagen
    x = (3000 - img.width) // 2
    y = (3000 - img.height) // 2
    result.paste(img, (x, y))
    
    return result


def resize_fill(img):
    """Redimensiona rellenando el cuadrado (recorta excedente)"""
    return ImageOps.fit(img, (3000, 3000), Image.Resampling.LANCZOS)


def resize_stretch(img):
    """Estira la imagen a 3000x3000"""
    return img.resize((3000, 3000), Image.Resampling.LANCZOS)


def test_resize_fit():
    """Test the fit mode (with margins)"""
    print("Testing resize_fit mode...")
    
    try:
        # Test with a rectangular image
        test_img = create_test_image(2000, 1000, (255, 0, 0))
        result = resize_fit(test_img)
        
        # Check that result is 3000x3000
        assert result.size == (3000, 3000), f"Expected (3000, 3000) but got {result.size}"
        print("✓ resize_fit: Output dimensions correct (3000x3000)")
        
        # Save and verify
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            result.save(tmp.name)
            saved_img = Image.open(tmp.name)
            assert saved_img.size == (3000, 3000), "Saved image has wrong dimensions"
            print("✓ resize_fit: Saved image dimensions correct")
            os.unlink(tmp.name)
        
    except Exception as e:
        print(f"✗ resize_fit failed: {e}")
        return False
    
    return True


def test_resize_fill():
    """Test the fill mode (crop to fit)"""
    print("\nTesting resize_fill mode...")
    
    try:
        # Test with rectangular image
        test_img = create_test_image(4000, 2000, (0, 255, 0))
        result = resize_fill(test_img)
        
        assert result.size == (3000, 3000), f"Expected (3000, 3000) but got {result.size}"
        print("✓ resize_fill: Output dimensions correct (3000x3000)")
        
    except Exception as e:
        print(f"✗ resize_fill failed: {e}")
        return False
    
    return True


def test_resize_stretch():
    """Test the stretch mode"""
    print("\nTesting resize_stretch mode...")
    
    try:
        # Test with rectangular image
        test_img = create_test_image(1000, 2000, (0, 0, 255))
        result = resize_stretch(test_img)
        
        assert result.size == (3000, 3000), f"Expected (3000, 3000) but got {result.size}"
        print("✓ resize_stretch: Output dimensions correct (3000x3000)")
        
    except Exception as e:
        print(f"✗ resize_stretch failed: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 50)
    print("Image Resizer 3000 - Core Functionality Tests")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("resize_fit", test_resize_fit()))
    results.append(("resize_fill", test_resize_fill()))
    results.append(("resize_stretch", test_resize_stretch()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
