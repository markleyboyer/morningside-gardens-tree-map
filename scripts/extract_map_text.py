"""Dump every text fragment in the tree map PDF with position, rotation, and size."""
import json
import sys
from pathlib import Path

import fitz

PDF = Path(r"G:\My Drive\Morningside Gardens\Grounds Committee\Tree Map\treeidmapandtableattacheddocuments\tree map 2025.pdf")
OUT_JSON = Path(r"G:\My Drive\Morningside Gardens\Grounds Committee\Tree Map\scripts\map_text_raw.json")

doc = fitz.open(PDF)
print(f"pages: {doc.page_count}")
fragments = []
for pi, page in enumerate(doc):
    print(f"page {pi}: size={page.rect}, rotation={page.rotation}")
    d = page.get_text("rawdict")
    for block in d.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            wmode = line.get("wmode")
            dirv = line.get("dir")
            text_parts = []
            char_positions = []
            for span in line.get("spans", []):
                for ch in span.get("chars", []):
                    text_parts.append(ch.get("c", ""))
                    bbox = ch.get("bbox")
                    char_positions.append(bbox)
            text = "".join(text_parts).strip()
            if not text:
                continue
            line_bbox = line.get("bbox")
            fragments.append({
                "page": pi,
                "text": text,
                "bbox": line_bbox,
                "dir": dirv,
                "wmode": wmode,
            })

print(f"fragments: {len(fragments)}")
OUT_JSON.write_text(json.dumps(fragments, indent=2))
print(f"wrote {OUT_JSON}")

# quick sanity peek
for f in fragments[:30]:
    print(f)
