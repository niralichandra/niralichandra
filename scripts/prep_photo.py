#!/usr/bin/env python3
"""
Prepare a portrait photo for clean ASCII conversion:
  1. remove the background (rembg if available, otherwise OpenCV grabCut fallback)
  2. boost LOCAL contrast (CLAHE) so facial features and eyes stay crisp
  3. composite the subject onto pure white so the background reads as blank
     (white -> spaces in the ascii ramp)
  4. head-and-shoulders crop centered on the head

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run whenever the source photo changes; the ascii SVG itself is static.

    python scripts/prep_photo.py [input.png] [output.png]
"""
import glob
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")


def default_input():
    patterns = ["source-photo.png", "source-photo.jpg", "source-photo.jpeg", "source-photo.webp", "source-photo.*"]
    for pat in patterns:
        found = sorted(glob.glob(os.path.join(ROOT, pat)))
        if found:
            return found[0]
    sys.exit("no source-photo.* found in the repo root")


INP = sys.argv[1] if len(sys.argv) > 1 else default_input()
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "source-prepped.png")

# head-and-shoulders crop fraction
BUST = 0.52

# 1. cut out the subject
img_in = ImageOps.exif_transpose(Image.open(INP))

rembg_success = False
try:
    from rembg import remove
    cut = remove(img_in.convert("RGBA"))
    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])
    rembg_success = True
    print("used rembg for background removal")
except Exception as e:
    print(f"rembg not available ({e}), falling back to OpenCV GrabCut segmentation")

if not rembg_success:
    rgb = np.array(img_in.convert("RGB"))
    h, w, _ = rgb.shape
    mask = np.zeros((h, w), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (int(w * 0.05), int(h * 0.05), int(w * 0.9), int(h * 0.9))
    cv2.grabCut(rgb, mask, rect, bgdModel, fgdModel, 4, cv2.GC_INIT_WITH_RECT)
    alpha = np.where((mask == 2) | (mask == 0), 0, 255).astype(np.uint8)

# crop bounding box of subject
ys, xs = np.where(alpha > 16)
if len(xs):
    pad = 12
    y0, y1 = max(0, ys.min() - pad), min(alpha.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(alpha.shape[1], xs.max() + pad)
    rgb, alpha = rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]

# 2. local-contrast the luminance (CLAHE)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
gray = clahe.apply(gray)
gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=15)

# 3. paste onto white using alpha mask
mask_f = alpha.astype(np.float32) / 255.0
mask_f = cv2.GaussianBlur(mask_f, (0, 0), 1.2)
out = gray.astype(np.float32) * mask_f + 255.0 * (1.0 - mask_f)
out = np.clip(out, 0, 255).astype(np.uint8)

# 4. crop to head and shoulders, centered on the head
h, w = out.shape
if BUST < 1.0:
    side = int(h * BUST)
    head = out[: int(h * 0.25)]
    cols = np.where((head < 200).any(axis=0))[0]
    cx = (cols.min() + cols.max()) // 2 if len(cols) else w // 2
    x0 = max(0, min(w - side, cx - side // 2))
    out = out[:side, x0:x0 + side]

# square it up on white
h, w = out.shape
side = max(h, w)
canvas = np.full((side, side), 255, np.uint8)
canvas[(side - h) // 2:(side - h) // 2 + h, (side - w) // 2:(side - w) // 2 + w] = out

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape)
