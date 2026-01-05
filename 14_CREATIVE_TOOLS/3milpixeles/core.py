
import os
import logging
from PIL import Image, ImageOps, ExifTags
from datetime import datetime
from typing import Tuple, List, Optional

class ResizerError(Exception):
    """Custom exception for all errors raised by ResizerCore."""
    pass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResizerCore:
    TARGET_SIZE = (3000, 3000)
    DEFAULT_QUALITY = 95
    
    @staticmethod
    def validate_image(filepath: str) -> bool:
        """Validate that the given file exists and is a readable image.

        Returns:
            bool: ``True`` if the file can be opened by Pillow, ``False`` otherwise.
        """
        if not os.path.isfile(filepath):
            logger.error(f"File does not exist: {filepath}")
            return False
        try:
            with Image.open(filepath) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Validation failed for {filepath}: {e}")
            return False

    @staticmethod
    def resize_fit(img: Image.Image, target_size: Tuple[int, int] = TARGET_SIZE) -> Image.Image:
        """Resizes image to fit within target size, adding padding to maintain aspect ratio."""
        # Create canvas
        canvas = Image.new('RGB', target_size, (255, 255, 255))
        
        # Maintain aspect ratio using thumbnail (modifies in-place)
        img_copy = img.copy()
        img_copy.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Center the image
        x = (target_size[0] - img_copy.width) // 2
        y = (target_size[1] - img_copy.height) // 2
        canvas.paste(img_copy, (x, y))
        
        return canvas

    @staticmethod
    def resize_fill(img: Image.Image, target_size: Tuple[int, int] = TARGET_SIZE) -> Image.Image:
        """Resizes and crops image to fill the target size completely."""
        return ImageOps.fit(img, target_size, Image.Resampling.LANCZOS)

    @staticmethod
    def resize_stretch(img: Image.Image, target_size: Tuple[int, int] = TARGET_SIZE) -> Image.Image:
        """Stretches image to exactly match target size."""
        return img.resize(target_size, Image.Resampling.LANCZOS)

    @classmethod
    def process_image(cls,
                      input_path: str,
                      output_folder: str,
                      mode: str = 'fit',
                      save_original: bool = True,
                      quality: int = DEFAULT_QUALITY,
                      output_format: str = 'PNG') -> str:
        """Process an image and save it to ``output_folder``.

        Args:
            input_path: Path to the source image.
            output_folder: Destination directory.
            mode: One of ``'fit'``, ``'fill'`` or ``'stretch'``.
            save_original: If ``True`` the original filename is kept with a timestamp.
            quality: Quality for lossy formats (JPEG/WebP). Ignored for PNG.
            output_format: Desired output format (``'PNG'``, ``'JPEG'`` or ``'WEBP'``).

        Returns:
            The absolute path to the saved image.

        Raises:
            ResizerError: If the input is invalid or the mode is unknown.
        """
        if not cls.validate_image(input_path):
            raise ResizerError(f"Invalid image file: {input_path}")

        if mode not in {'fit', 'fill', 'stretch'}:
            raise ResizerError(f"Unknown resize mode: {mode}")

        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)

        with Image.open(input_path) as img:
            # Apply EXIF orientation if present
            try:
                exif = img._getexif()
                if exif:
                    orientation_key = next(
                        k for k, v in ExifTags.TAGS.items() if v == 'Orientation'
                    )
                    orientation = exif.get(orientation_key, 1)
                    if orientation != 1:
                        img = ImageOps.exif_transpose(img)
            except Exception:
                # If EXIF handling fails we simply continue
                pass

            # Ensure RGB for consistent processing
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Perform resizing based on mode
            if mode == 'fit':
                result = cls.resize_fit(img)
            elif mode == 'fill':
                result = cls.resize_fill(img)
            else:  # stretch
                result = cls.resize_stretch(img)

            # Build output filename
            if save_original:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"{name}_3000x3000_{timestamp}.{output_format.lower()}"
            else:
                output_name = f"{name}_3000.{output_format.lower()}"

            output_path = os.path.join(output_folder, output_name)
            os.makedirs(output_folder, exist_ok=True)

            save_params = {}
            if output_format.upper() in {'JPEG', 'WEBP'}:
                save_params['quality'] = quality

            result.save(output_path, output_format.upper(), **save_params)
            logger.info(f"Successfully processed {filename} -> {output_path}")
            return output_path
