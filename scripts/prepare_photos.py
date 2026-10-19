#!/usr/bin/env python3
"""Resize and compress Bekezela website photos without cropping or upscaling.

Expected inputs (any Pillow-readable image format):
    hero.*
    butchery.*
    bottle-store.*
    grocery.*

Example:
    python3 scripts/prepare_photos.py --input-dir ~/bekezela-photos

Output is written to images/optimized/ by default. Source photos are never
modified. Images keep their original aspect ratio and are fitted inside the
website's maximum display dimensions; the website handles any visual crop.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

# Maximum pixel dimensions needed by the site. These are limits, not target
# dimensions: smaller source photos will not be enlarged.
PHOTO_LIMITS: dict[str, tuple[int, int]] = {
    "hero": (1920, 1080),
    "butchery": (1200, 1500),
    "bottle-store": (1200, 1500),
    "grocery": (1200, 1500),
}
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
BACKGROUND = (247, 243, 233)  # warm cream, used if a source has transparency


def find_source(source_dir: Path, photo_name: str) -> Path | None:
    """Find a case-insensitive matching photo name with a supported suffix."""
    matches = [
        path
        for path in source_dir.iterdir()
        if path.is_file()
        and path.stem.casefold() == photo_name.casefold()
        and path.suffix.casefold() in SUPPORTED_SUFFIXES
    ]
    return sorted(matches, key=lambda path: path.name.casefold())[0] if matches else None


def prepare(source: Path, destination: Path, bounds: tuple[int, int], quality: int, max_kb: int) -> tuple[tuple[int, int], int, int]:
    """Orient, fit, and save one source photo as a progressive optimized JPEG."""
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        image.thumbnail(bounds, Image.Resampling.LANCZOS)

        # Composite transparency onto a neutral shop-paper color before JPEG.
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGBA", rgba.size, BACKGROUND + (255,))
            image = Image.alpha_composite(background, rgba).convert("RGB")
        else:
            image = image.convert("RGB")

        dimensions = image.size
        chosen_quality = quality
        while True:
            buffer = io.BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=chosen_quality,
                optimize=True,
                progressive=True,
                subsampling="4:2:0",
            )
            size_kb = (buffer.tell() + 1023) // 1024
            if size_kb <= max_kb or chosen_quality <= 60:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(buffer.getvalue())
                return dimensions, chosen_quality, size_kb
            chosen_quality = max(60, chosen_quality - 5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare Bekezela's four site photos as lightweight JPEGs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("photos/incoming"),
        help="Folder containing hero, butchery, bottle-store, and grocery photos",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("images/optimized"),
        help="Folder for optimized JPEG copies; source files are never changed",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=83,
        help="Starting JPEG quality from 60 to 95 (lowered if needed to meet max-kb)",
    )
    parser.add_argument(
        "--max-kb",
        type=int,
        default=700,
        help="Try reducing JPEG quality to keep each image at or below this size",
    )
    args = parser.parse_args()
    if not 60 <= args.quality <= 95:
        parser.error("--quality must be between 60 and 95")
    if args.max_kb < 1:
        parser.error("--max-kb must be at least 1")
    return args


def main() -> int:
    args = parse_args()
    source_dir = args.input_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not source_dir.is_dir():
        print(f"Input folder does not exist: {source_dir}", file=sys.stderr)
        return 2

    missing = [name for name in PHOTO_LIMITS if find_source(source_dir, name) is None]
    if missing:
        print(
            "Missing photo(s): " + ", ".join(f"{name}.*" for name in missing)
            + f"\nAdd them to {source_dir}. Supported types: "
            + ", ".join(sorted(SUPPORTED_SUFFIXES)),
            file=sys.stderr,
        )
        return 2

    failures = 0
    for name, bounds in PHOTO_LIMITS.items():
        source = find_source(source_dir, name)
        assert source is not None
        destination = output_dir / f"{name}.jpg"
        if source.resolve() == destination.resolve():
            print(f"Refusing to overwrite source photo: {source}", file=sys.stderr)
            failures += 1
            continue
        try:
            size, quality, size_kb = prepare(
                source, destination, bounds, args.quality, args.max_kb
            )
        except (OSError, UnidentifiedImageError) as error:
            print(f"Could not process {source.name}: {error}", file=sys.stderr)
            failures += 1
            continue
        print(
            f"{source.name} -> {destination}  "
            f"{size[0]}×{size[1]} px · Q{quality} · {size_kb} KB"
        )
        if size_kb > args.max_kb:
            print(
                f"  Note: still above {args.max_kb} KB at minimum quality 60; "
                "the output is saved, with no crop or upscaling."
            )

    if failures:
        print(f"Finished with {failures} error(s).", file=sys.stderr)
        return 1
    print(f"\nReady to upload the four optimized photos from {output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
