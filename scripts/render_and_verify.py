"""Render the map to PNG, then overlay the extracted tree positions to verify alignment."""
import json
from pathlib import Path

import fitz

ROOT = Path(r"G:\My Drive\Morningside Gardens\Grounds Committee\Tree Map")
PDF = ROOT / "treeidmapandtableattacheddocuments" / "tree map 2025.pdf"
OUT_DIR = ROOT / "site" / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

doc = fitz.open(PDF)
page = doc[0]
print(f"page native rect={page.rect} rotation={page.rotation}")

# The PDF's stored rotation (270) leaves the on-page text upside-down.
# Override to 90 so labels read correctly.
page.set_rotation(90)
zoom = 2.0
mat = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=mat, alpha=False)
print(f"rendered pixmap: {pix.width}x{pix.height} at rotation={page.rotation}")
png_path = OUT_DIR / "map.png"
pix.save(png_path)
print(f"wrote {png_path}")

# annotation rects are in NATIVE page coords. To map them to the rendered image
# (which uses the page's display rotation), apply page.rotation_matrix * zoom.
rot_mat = page.rotation_matrix  # native -> rotated page coords
print(f"rotation_matrix={rot_mat}")

annots_data = json.loads((ROOT / "scripts" / "annotations_raw.json").read_text())

import re
id_pat = re.compile(r"^(NW|NE|SW|SE)-?\d+$", re.I)
positions = []
for a in annots_data:
    if not id_pat.match(a["content"]):
        continue
    # transform native rect center -> rendered pixel coords
    cx_native, cy_native = a["cx"], a["cy"]
    pt = fitz.Point(cx_native, cy_native) * rot_mat
    px = pt.x * zoom
    py = pt.y * zoom
    positions.append({
        "id": a["content"].upper().replace(" ", "-"),
        "x": round(px, 1),
        "y": round(py, 1),
    })

# normalize id format: NE-13 not NE13
def norm(s):
    s = s.upper().replace(" ", "")
    if "-" not in s:
        # split letters / digits
        for i, c in enumerate(s):
            if c.isdigit():
                return s[:i] + "-" + s[i:]
    return s
for p in positions:
    p["id"] = norm(p["id"])

(ROOT / "scripts" / "positions.json").write_text(json.dumps(positions, indent=2))
print(f"extracted {len(positions)} tree positions")

# Render a verification overlay: red dots at each position, with id text
from PIL import Image, ImageDraw, ImageFont
img = Image.open(png_path).convert("RGB")
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arial.ttf", 14)
except Exception:
    font = ImageFont.load_default()
for p in positions:
    x, y = p["x"], p["y"]
    r = 6
    draw.ellipse((x - r, y - r, x + r, y + r), outline="red", width=2)
    draw.text((x + 8, y - 8), p["id"], fill="red", font=font)
verify_path = OUT_DIR / "map_verify.png"
img.save(verify_path)
print(f"wrote {verify_path}")
