"""Chấm Hit@1 / Evidence Hit@3 và giữ trace từng câu."""
import re
from collections import defaultdict
from typing import Any


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def is_hit(result: dict[str, Any], q: dict[str, Any]) -> bool:
    """Hit = chunk thuộc trang gold (hoặc alt) VÀ chứa đủ evidence_quote."""
    gold_pages = {q["gold_page"], *q.get("alt_gold_pages", [])}
    if result["page_id"] not in gold_pages:
        return False
    return _norm(q["evidence_quote"]) in _norm(result["text"])


def evaluate_query(q: dict[str, Any], results: list[dict[str, Any]], strategy: str,
                   applied_filter: dict | None) -> dict[str, Any]:
    hits = [is_hit(r, q) for r in results]
    page_only = [r["page_id"] in {q["gold_page"], *q.get("alt_gold_pages", [])} for r in results]
    filter_ok = None
    if applied_filter:
        filter_ok = all(r.get(k) == v for r in results for k, v in applied_filter.items())
    return {
        "strategy": strategy,
        "id": q["id"],
        "split": q["split"],
        "type": q.get("type"),
        "question": q["question"],
        "gold_page": q["gold_page"],
        "filter": applied_filter,
        "hit@1": bool(hits[:1] and hits[0]),
        "hit@3": any(hits[:3]),
        # đúng trang nhưng evidence bị cắt qua nhiều chunk -> ghi lại để phân tích lỗi
        "page_hit@3_but_evidence_split": any(page_only[:3]) and not any(hits[:3]),
        "filter_respected": filter_ok,
        "top3": [{"rank": i + 1, "chunk_id": r["chunk_id"], "page_id": r["page_id"],
                  "chapter": r["chapter"], "section": r["section"], "score": round(r["score"], 4),
                  "hit": h, "text": r["text"][:300]} for i, (r, h) in enumerate(zip(results, hits))],
    }


def summarize(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple, list] = defaultdict(list)
    for t in traces:
        groups[(t["strategy"], t["split"])].append(t)
    rows = []
    for (s, sp), ts in sorted(groups.items()):
        n = len(ts)
        h1 = sum(t["hit@1"] for t in ts)
        h3 = sum(t["hit@3"] for t in ts)
        rows.append({"strategy": s, "split": sp, "n": n,
                     "hit@1": f"{h1}/{n}", "hit@3": f"{h3}/{n}",
                     "hit@1_pct": round(100 * h1 / n, 1), "hit@3_pct": round(100 * h3 / n, 1),
                     "evidence_split": sum(t["page_hit@3_but_evidence_split"] for t in ts)})
    return rows