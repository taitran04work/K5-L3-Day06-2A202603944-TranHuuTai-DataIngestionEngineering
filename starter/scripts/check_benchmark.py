"""Kiểm chứng benchmark: evidence có nguyên văn trong gold unit, đủ split/filter."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
units = {}
for line in open(root / "results/units.jsonl", encoding="utf-8"):
    u = json.loads(line)
    units[u["metadata"]["page_id"]] = u

qs = [json.loads(l) for l in open(root / "data/benchmark.jsonl", encoding="utf-8") if l.strip()]
bad = 0
for q in qs:
    page = q["gold_page"]
    if page not in units or q["evidence_quote"] not in units[page]["text"]:
        bad += 1
        print("FAIL evidence", q["id"], page)
    f = q.get("filter") or {}
    for k, v in f.items():
        if page in units and units[page]["metadata"].get(k) != v:
            bad += 1
            print("FAIL filter", q["id"], k, v)
    for alt in q.get("alt_gold_pages", []):
        if alt not in units:
            bad += 1
            print("FAIL alt", q["id"], alt)

splits = [q["split"] for q in qs]
nf = [q for q in qs if q.get("filter")]
print(f"{len(qs)} câu | dev {splits.count('dev')} | test {splits.count('test')} | "
      f"filter {len(nf)} (test: {sum(q['split'] == 'test' for q in nf)}) | lỗi {bad}")
