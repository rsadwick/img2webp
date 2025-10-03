# img2webp

A command-line tool for resizing images and converting them to WebP format using Python and Pillow.

## Features
- Resize images to specified dimensions while optionally preserving aspect ratio.
- Convert supported image formats (JPG, PNG, BMP, TIFF, GIF, WEBP) to WebP.
- Support for lossless or lossy WebP compression with adjustable quality.
- Recursive directory processing.
- Custom output directory, filename suffixes, and glob patterns for file selection.
- Handles EXIF orientation automatically.
- Skips existing files unless overwrite is specified.
- Detailed status reporting for each file and a final summary.
- Checks for Pillow WebP support at runtime.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/rsadwick/img2webp.git
   ```
2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   (Requires Pillow >= 10.0.0 with WebP support.)

## Usage
Run the script with:
```
python img2webp.py <directory> <width> <height> [options]
```
Or make it executable and run `./img2webp.py` (on Unix-like systems).

### Options
- `--output-dir PATH`: Output directory (default: `<directory>/converted_webp`).
- `--recursive`: Process subdirectories recursively.
- `--exact`: Resize to exact width x height without preserving aspect ratio.
- `--quality N`: WebP quality (0-100, default: 80) for lossy compression.
- `--lossless`: Use lossless WebP (ignores `--quality`).
- `--overwrite`: Overwrite existing output files.
- `--suffix STR`: Append suffix to output filenames.
- `--glob PATTERN`: Glob pattern for input files (default: `*.*`).

## Examples
- Basic resize (fit within 1600x900, preserve aspect):
  ```
  python img2webp.py ./images 1600 900
  ```
- Recursive, exact size, lossless:
  ```
  python img2webp.py ./images 800 600 --recursive --exact --lossless
  ```
- Custom output, quality 90, suffix "-opt", only PNGs:
  ```
  python img2webp.py ./images 1024 768 --output-dir /output --quality 90 --suffix -opt --glob "*.png"
  ```
