import argparse
import sys
import os
from pathlib import Path
from typing import Tuple, Iterable
from PIL import Image, ImageOps, features

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="img2webp", description="Resize images and convert to WebP")
    p.add_argument("directory", type=Path, help="Directory containing images")
    p.add_argument("width", type=int, help="Target width in pixels")
    p.add_argument("height", type=int, help="Target height in pixels")
    p.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: <directory>/converted_webp)")
    p.add_argument("--recursive", action="store_true", help="Recurse into subdirectories")
    p.add_argument("--exact", action="store_true", help="Resize to exact WxH without preserving aspect ratio")
    p.add_argument("--quality", type=int, default=80, help="WebP quality 0-100 (default: 80)")
    p.add_argument("--lossless", action="store_true", help="Use lossless WebP")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    p.add_argument("--suffix", default="", help="Suffix to append to output basename")
    p.add_argument("--glob", default="*.*", help="Glob pattern for matching files (default: *.*)")
    return p.parse_args()

def ensure_webp_support() -> None:
    if not features.check("webp"):
        sys.stderr.write("Error: Pillow was built without WebP support. Install a Pillow wheel with libwebp enabled.\n")
        sys.exit(1)

def iter_input_files(root: Path, pattern: str, recursive: bool) -> Iterable[Path]:
    if recursive:
        yield from root.rglob(pattern)
    else:
        yield from root.glob(pattern)

def is_image(path: Path) -> bool:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp"}
    return path.suffix.lower() in exts

def compute_size_exact(w: int, h: int) -> Tuple[int, int]:
    return max(1, w), max(1, h)

def compute_size_contain(img: Image.Image, w: int, h: int) -> Image.Image:
    return ImageOps.contain(img, (max(1, w), max(1, h)))

def build_output_path(inp: Path, outdir: Path, suffix: str) -> Path:
    stem = inp.stem + (suffix if suffix else "")
    return outdir / f"{stem}.webp"

def convert_one(path: Path, outdir: Path, size: Tuple[int, int], exact: bool, quality: int, lossless: bool, overwrite: bool, suffix: str) -> Tuple[Path, str]:
    out_path = build_output_path(path, outdir, suffix)
    if out_path.exists() and not overwrite:
        return out_path, "skipped-exists"
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            if exact:
                im = im.convert("RGBA")
                im = im.resize(size, Image.Resampling.LANCZOS)
            else:
                im = compute_size_contain(im, size[0], size[1])
            params = {}
            if lossless:
                params.update(lossless=True, quality=100, method=6)
            else:
                params.update(quality=max(0, min(100, quality)), method=6)
            outdir.mkdir(parents=True, exist_ok=True)
            im.save(out_path, format="WEBP", **params)
        return out_path, "ok"
    except Exception as e:
        return out_path, f"error:{e}"

def main() -> None:
    args = parse_args()
    ensure_webp_support()
    src_dir = args.directory.resolve()
    if not src_dir.exists() or not src_dir.is_dir():
        sys.stderr.write("Error: directory does not exist or is not a directory\n")
        sys.exit(2)
    outdir = (args.output_dir or (src_dir / "converted_webp")).resolve()
    target_size = compute_size_exact(args.width, args.height)
    files = [p for p in iter_input_files(src_dir, args.glob, args.recursive) if p.is_file() and is_image(p)]
    if not files:
        sys.stderr.write("No image files found.\n")
        sys.exit(0)
    total = 0
    ok = 0
    skipped = 0
    errors = 0
    for f in files:
        total += 1
        out_path, status = convert_one(f, outdir, target_size, args.exact, args.quality, args.lossless, args.overwrite, args.suffix)
        if status == "ok":
            ok += 1
            sys.stdout.write(f"OK  {f} -> {out_path}\n")
        elif status == "skipped-exists":
            skipped += 1
            sys.stdout.write(f"SKIP {out_path} exists\n")
        else:
            errors += 1
            sys.stdout.write(f"ERR {f} -> {status}\n")
    sys.stdout.write(f"\nDone. total={total} ok={ok} skipped={skipped} errors={errors}\n")

if __name__ == "__main__":
    main()