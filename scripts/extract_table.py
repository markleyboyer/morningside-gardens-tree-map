"""Extract the tree ID table from the PDF into structured JSON."""
import json
import re
from pathlib import Path

import fitz

ROOT = Path(r"G:\My Drive\Morningside Gardens\Grounds Committee\Tree Map")
TABLE_PDF = ROOT / "treeidmapandtableattacheddocuments" / "tree ID table 10-15-25.pdf"
OUT = ROOT / "scripts" / "trees_table.json"

doc = fitz.open(TABLE_PDF)

# Get text by line, group by approximate y on each page, then split by x columns.
# Easier approach: use get_text("blocks") -> each block has lines.
all_rows = []
header_skipped = set()
for page_idx, page in enumerate(doc):
    # Use words: each word is (x0, y0, x1, y1, "text", block_no, line_no, word_no)
    words = page.get_text("words")
    # Group by line_no (within a block) — but easier: group by rounded y
    lines = {}
    for w in words:
        x0, y0, x1, y1, text, *_ = w
        key = round(y0, 0)
        lines.setdefault(key, []).append((x0, text))
    # For each line, sort by x and join
    for y, items in sorted(lines.items()):
        items.sort(key=lambda t: t[0])
        # Build a row by inferring columns from x positions.
        # Columns roughly: ID# (~80), COMMON NAME (~140), BOTANICAL NAME (~340),
        # DBA 2020 (~640), PLANTED (~720), NOTE (~870)
        col_bounds = [(0, 40), (40, 200), (200, 400), (400, 450), (450, 580), (580, 9999)]
        col_text = ["", "", "", "", "", ""]
        for x, t in items:
            for ci, (lo, hi) in enumerate(col_bounds):
                if lo <= x < hi:
                    col_text[ci] = (col_text[ci] + " " + t).strip()
                    break
        # First column should be an ID like NW-1; if not, skip
        idv = col_text[0]
        if not re.match(r"^(NW|NE|SW|SE)-?\d+$", idv, re.I):
            continue
        # normalize id
        idv = idv.upper()
        if "-" not in idv:
            idv = idv[:2] + "-" + idv[2:]
        all_rows.append({
            "id": idv,
            "common_name": col_text[1],
            "botanical_name": col_text[2],
            "dba_2020": col_text[3],
            "planted": col_text[4],
            "note": col_text[5],
        })

print(f"extracted {len(all_rows)} rows from table")
# Show a sample
for r in all_rows[:5]:
    print(r)

OUT.write_text(json.dumps(all_rows, indent=2))
print(f"wrote {OUT}")
