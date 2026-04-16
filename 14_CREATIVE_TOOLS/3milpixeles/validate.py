
import os
from PIL import Image
from core import ResizerCore
import unittest

class TestVisualAlpha(unittest.TestCase):
    def setUp(self):
        # Create a test image
        self.test_img_path = "test_source.png"
        img = Image.new('RGB', (1000, 500), color=(73, 109, 137))
        img.save(self.test_img_path)
        self.output_dir = "test_output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def tearDown(self):
        if os.path.exists(self.test_img_path):
            os.remove(self.test_img_path)
        if os.path.exists(self.output_dir):
            import shutil
            shutil.rmtree(self.output_dir)

    def test_fit_mode(self):
        out_path = ResizerCore.process_image(self.test_img_path, self.output_dir, mode='fit')
        with Image.open(out_path) as img:
            self.assertEqual(img.size, (3000, 3000))
            # Test for white margins (0,0 should be white in fit mode for 1000x500)
            self.assertEqual(img.getpixel((0, 0)), (255, 255, 255))

    def test_fill_mode(self):
        out_path = ResizerCore.process_image(self.test_img_path, self.output_dir, mode='fill')
        with Image.open(out_path) as img:
            self.assertEqual(img.size, (3000, 3000))
            # Center should have the color
            self.assertEqual(img.getpixel((1500, 1500)), (73, 109, 137))

    def test_stretch_mode(self):
        out_path = ResizerCore.process_image(self.test_img_path, self.output_dir, mode='stretch')
        with Image.open(out_path) as img:
            self.assertEqual(img.size, (3000, 3000))

if __name__ == "__main__":
    print("🔍 Starting Validation...")
    unittest.main()
