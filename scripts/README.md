# Preparing Bekezela website photos

The site expects four image files: `hero.jpg`, `butchery.jpg`, `bottle-store.jpg`, and `grocery.jpg`. The preparation script converts common image formats to lightweight progressive JPEGs, respects EXIF camera rotation, and scales oversized photos down without cropping or enlarging them. Original inputs are left untouched.

## 1. Install Pillow

```bash
python3 -m pip install Pillow
```

## 2. Put the original photos in a folder

Use these filenames (extensions may be `.jpg`, `.jpeg`, `.png`, `.webp`, `.tif`, `.tiff`, or `.bmp`):

```text
my-photos/
  hero.png
  butchery.jpg
  bottle-store.webp
  grocery.jpg
```

## 3. Prepare optimized copies

Run from the repository root:

```bash
python3 scripts/prepare_photos.py --input-dir ~/my-photos
```

The outputs go to `images/optimized/` by default. The script limits the hero to 1920 × 1080 px and department images to 1200 × 1500 px, keeps each photo's aspect ratio, and aims for a maximum of 700 KB. If needed, it reduces JPEG quality to reach that size (down to quality 60).

To use a different output folder or size limit:

```bash
python3 scripts/prepare_photos.py \
  --input-dir ~/my-photos \
  --output-dir ~/bekezela-ready \
  --max-kb 500
```

## 4. Replace the site images

Review the files in `images/optimized/`, then copy them over the matching files in `images/`:

```bash
cp images/optimized/*.jpg images/
```

Preview the site, then commit and push the four replacements. Keep the original photos somewhere safe; this script never edits them.
