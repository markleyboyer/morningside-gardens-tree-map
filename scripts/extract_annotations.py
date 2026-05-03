"""Extract all annotation labels (AutoCAD SHX Text) with positions."""
import json
from collections import Counter
from pathlib import Path

import fitz

PDF = Path(r"G:\My Drive\Morningside Gardens\Grounds Committee\Tree Map\treeidmapandtableattacheddocuments\tree map 2025.pdf")
OUT = Path(r"G:\My Drive\Morningside Gardens\Grounds Committee\Tree Map\scripts\annotations_raw.json")

doc = fitz.open(PDF)
page = doc[0]
print(f"page rect={page.rect} rotation={page.rotation}")

rows = []
for a in page.annots():
    r = a.rect
    info = a.info
    rows.append({
        "content": info.get("content", ""),
        "title": info.get("title", ""),
        "rect": [r.x0, r.y0, r.x1, r.y1],
        "cx": (r.x0 + r.x1) / 2,
        "cy": (r.y0 + r.y1) / 2,
        "w": r.width,
        "h": r.height,
    })

print(f"total annotations: {len(rows)}")
# distribution of content lengths and samples
lens = Counter(len(r["content"]) for r in rows)
print("content-length distribution:", dict(sorted(lens.items())))

# tree-id-like patterns
import re
pat = re.compile(r"^(NW|NE|SW|SE)-?\d+$", re.I)
ids = [r for r in rows if pat.match(r["content"])]
print(f"tree-id matches: {len(ids)}")
if ids:
    print("samples:", [r["content"] for r in ids[:20]])

# what are the non-id contents?
non_ids = [r for r in rows if not pat.match(r["content"])]
print(f"non-id labels: {len(non_ids)}")
content_counter = Counter(r["content"] for r in non_ids)
print("top 30 non-id contents:")
for c, n in content_counter.most_common(30):
    print(f"  {n:4d}  {c!r}")

OUT.write_text(json.dumps(rows, indent=2))
print(f"wrote {OUT}")
