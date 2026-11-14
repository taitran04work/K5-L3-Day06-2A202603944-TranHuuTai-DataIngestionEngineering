"""Sinh bảng audit thủ công (coherence, metadata, grounding) từ chunks + trace.

Mẫu chọn TRƯỚC khi chấm: coherence = vị trí đầu của 10 unit đầu (u001..u010);
metadata + grounding = 5 câu test x top-3 của cấu hình C (cấu hình đã chọn trên dev).
Cột nhãn để trống / nháp; người chấm điền vào results/audit_*.md.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


units = {u["metadata"]["page_id"]: u for u in load(RES / "units.jsonl")}
chunks = {"A": load(RES / "chunks_A.jsonl"), "B": load(RES / "chunks_B.jsonl")}
traces = load(RES / "trace.jsonl")
bench = {q["id"]: q for q in load(ROOT / "data/benchmark.jsonl")}


def esc(s, n=None):
    s = s.replace("\n", " ").replace("|", "/")
    return s if n is None else (s[:n] + ("…" if len(s) > n else ""))


# 1) Coherence: chunk chứa ký tự đầu tiên của mỗi unit u001..u010
out = ["# Audit coherence (0 = cắt giữa ý / thiếu chủ thể; 1 = hiểu một phần; 2 = tự hiểu, trọn ý)", "",
       "Mẫu: vị trí = đầu unit u001..u010 (chọn trước khi chấm). C dùng chung chunk với B.", ""]
for s in ["A", "B"]:
    out += [f"## Strategy {s}", "", "| # | Vị trí | chunk_id | ký tự | Mở đầu | Kết thúc | Điểm | Lý do |",
            "|---|---|---|---:|---|---|---|---|"]
    for i, pid in enumerate(list(units)[:10], 1):
        c = next(c for c in chunks[s] if c["metadata"]["page_id"] == pid)
        t = c["text"]
        out.append(f"| {i} | {pid} | {c['chunk_id']} | {len(t)} | {esc(t[:80])} | {esc(t[-80:])} |  |  |")
    out.append("")
(RES / "audit_coherence_blank.md").write_text("\n".join(out), encoding="utf-8")

# 2) Metadata: 5 test x top-3 của C; tự kiểm tra một phần, người chấm xác nhận
out = ["# Audit metadata — C, 5 câu test x top-3", "",
       "Tự động kiểm tra: page_id tồn tại, source đúng file, đoạn text nằm trong unit page_id, chapter khớp filter.",
       "Người chấm xác nhận cột 'Đủ & đúng' sau khi đối chiếu nguồn.", "",
       "| Câu | Rank | chunk_id | page_id | chapter | section | text∈unit | filter | Đủ & đúng | Ghi chú |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for t in [t for t in traces if t["strategy"] == "C" and t["split"] == "test"]:
    for r in t["top3"]:
        u = units.get(r["page_id"])
        full = next(c for c in chunks["B"] if c["chunk_id"] == r["chunk_id"])
        in_unit = bool(u) and full["text"][:200] in u["text"]
        fok = "N/A" if not t["filter"] else ("OK" if all(r.get(k) == v for k, v in t["filter"].items()) else "SAI")
        out.append(f"| {t['id']} | {r['rank']} | {r['chunk_id']} | {r['page_id']} | {r['chapter']} | "
                   f"{esc(r['section'], 40)} | {'OK' if in_unit else 'SAI'} | {fok} |  |  |")
(RES / "audit_metadata_blank.md").write_text("\n".join(out), encoding="utf-8")

# 3) Grounding: 5 test, top-3 C (0 = không có bằng chứng; 1 = thiếu điều kiện; 2 = đủ trả lời + truy nguồn)
out = ["# Audit grounding — C, 5 câu test (chỉ đánh giá evidence retrieval, không phải câu trả lời LLM)", ""]
for t in [t for t in traces if t["strategy"] == "C" and t["split"] == "test"]:
    q = bench[t["id"]]
    out += [f"## {t['id']} — {q['question']}", "",
            f"- Đáp án kỳ vọng: {q['expected_answer']}",
            f"- Gold: {q['gold_page']} (+{q.get('alt_gold_pages', [])}); filter: {t['filter']}",
            f"- Evidence Hit@3 tự động: {t['hit@3']}", ""]
    for r in t["top3"]:
        full = next(c for c in chunks["B"] if c["chunk_id"] == r["chunk_id"])
        out.append(f"{r['rank']}. `{r['chunk_id']}` (score {r['score']}, hit={r['hit']}): {esc(full['text'], 400)}")
    out += ["", "**Điểm grounding:**    **Lý do:** ", ""]
(RES / "audit_grounding_blank.md").write_text("\n".join(out), encoding="utf-8")
print("Đã tạo results/audit_*_blank.md (bảng trống; nhãn đã chấm ở audit_*.md, không bị ghi đè)")
