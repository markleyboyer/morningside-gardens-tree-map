"""Merge tree positions (from map) with table data (species, planted, etc).
Outputs the canonical dataset trees.json that the web viewer consumes."""
import json
from pathlib import Path

ROOT = Path(r"G:\My Drive\Morningside Gardens\Grounds Committee\Tree Map")

positions = json.loads((ROOT / "scripts" / "positions.json").read_text())
table = json.loads((ROOT / "scripts" / "trees_table.json").read_text())

pos_by_id = {p["id"]: p for p in positions}
tab_by_id = {r["id"]: r for r in table}

pos_ids = set(pos_by_id)
tab_ids = set(tab_by_id)

print(f"positions: {len(pos_ids)}, table: {len(tab_ids)}")
print(f"positions intersect table: {len(pos_ids & tab_ids)}")
print(f"in positions but not table: {sorted(pos_ids - tab_ids)}")
print(f"in table but not positions: {sorted(tab_ids - pos_ids)}")

merged = []
for tid in sorted(pos_ids | tab_ids, key=lambda s: (s.split("-")[0], int(s.split("-")[1]) if s.split("-")[1].isdigit() else 0)):
    p = pos_by_id.get(tid, {})
    t = tab_by_id.get(tid, {})
    merged.append({
        "id": tid,
        "x": p.get("x"),
        "y": p.get("y"),
        "common_name": t.get("common_name", ""),
        "botanical_name": t.get("botanical_name", ""),
        "dba_2020": t.get("dba_2020", ""),
        "planted": t.get("planted", ""),
        "note": t.get("note", ""),
        "has_position": tid in pos_ids,
        "has_table_data": tid in tab_ids and bool(t.get("common_name") or t.get("botanical_name")),
    })

with_pos = sum(1 for m in merged if m["has_position"])
with_data = sum(1 for m in merged if m["has_table_data"])
print(f"merged total: {len(merged)} (with position: {with_pos}, with table data: {with_data})")

OUT = ROOT / "site" / "data" / "trees.json"
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(merged, indent=2))
print(f"wrote {OUT}")
