
import argparse
import os
from PIL import Image
from image_resizer_3000 import ImageResizer3000

def main():
    parser = argparse.ArgumentParser(description='Resize images to 3000x3000 pixels from the command line.')
    parser.add_argument('input_file', type=str, help='The path to the input image file.')
    parser.add_argument('output_file', type=str, help='The path to save the resized image.')
    parser.add_argument('--mode', type=str, choices=['fit', 'fill', 'stretch'], default='fit', help='The resizing mode.')

    args = parser.parse_args()

    # We don't need the GUI, but the resizing functions are part of the ImageResizer3000 class
    # We can instantiate it with a dummy root object
    class DummyTk:
        def __init__(self):
            self.root = None
    
    resizer = ImageResizer3000(DummyTk())


    try:
        img = Image.open(args.input_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        if args.mode == 'fit':
            result = resizer.resize_fit(img)
        elif args.mode == 'fill':
            result = resizer.resize_fill(img)
        elif args.mode == 'stretch':
            result = resizer.resize_stretch(img)

        result.save(args.output_file, quality=95)
        print(f"Image saved to {args.output_file}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {args.input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
