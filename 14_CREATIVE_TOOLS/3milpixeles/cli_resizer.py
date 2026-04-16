
import argparse
import os
import sys
from core import ResizerCore

def main():
    parser = argparse.ArgumentParser(description='Resize images to 3000x3000px using Visual Alpha Engine.')
    parser.add_argument('input', type=str, help='Path to input image')
    parser.add_argument('output_folder', type=str, nargs='?', default='.', help='Output folder (default: current)')
    parser.add_argument('--mode', type=str, choices=['fit', 'fill', 'stretch'], default='fit', help='Resizing mode')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite original name pattern')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    try:
        print(f"🚀 Processing: {os.path.basename(args.input)}...")
        out_path = ResizerCore.process_image(
            args.input, 
            args.output_folder, 
            mode=args.mode, 
            save_original=not args.overwrite
        )
        print(f"✅ Success! Saved to: {out_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
