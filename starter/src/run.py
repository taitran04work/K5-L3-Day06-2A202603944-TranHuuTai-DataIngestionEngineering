"""Pipeline Day 06: units -> chunk A/B -> Gemini embedding (cache) -> pgvector -> benchmark A/B/C."""
import hashlib
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from .chunking import by_paragraph, fixed_size
from .embeddings import GeminiEmbedder
from .evaluation import evaluate_query, summarize
from .models import DocumentPage
from .store import PgVectorStore

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
CACHE_FILE = RES / "embedding_cache.json"

CONFIG = {
    "embedding_model": "gemini-embedding-001",
    "dimensions": 768,
    "A": {"chunking": "fixed_size", "size": 500, "overlap": 50, "filter": False},
    "B": {"chunking": "by_paragraph", "max_size": 1000, "filter": False},
    "C": {"chunking": "by_paragraph (dùng index B)", "max_size": 1000, "filter": "chapter khi câu hỏi có filter"},
    "top_k": 3,
}


class CachedEmbedder:
    """Cache theo hash(model + task + text): chạy lại không tốn quota."""

    def __init__(self, inner: GeminiEmbedder):
        self.inner = inner
        self.cache = json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else {}
        self.api_calls = 0

    def _key(self, task: str, text: str) -> str:
        return hashlib.sha256(f"{self.inner.model_name}|{self.inner.dimensions}|{task}|{text}".encode()).hexdigest()

    def docs(self, texts: list[str]) -> list[list[float]]:
        missing = [t for t in texts if self._key("doc", t) not in self.cache]
        if missing:
            self.api_calls += len(missing)
            for t, v in zip(missing, self.inner.embed_documents(missing)):
                self.cache[self._key("doc", t)] = v
            self.save()
        return [self.cache[self._key("doc", t)] for t in texts]

    def query(self, q: str) -> list[float]:
        k = self._key("query", q)
        if k not in self.cache:
            self.api_calls += 1
            self.cache[k] = self.inner.embed_query(q)
            self.save()
        return self.cache[k]

    def save(self):
        CACHE_FILE.write_text(json.dumps(self.cache), encoding="utf-8")


def main() -> None:
    t0 = time.time()
    pages = [DocumentPage(**json.loads(l)) for l in open(RES / "units.jsonl", encoding="utf-8")]
    chunk_sets = {
        "A": [c for p in pages for c in fixed_size(p, 500, 50)],
        "B": [c for p in pages for c in by_paragraph(p, 1000)],
    }
    emb = CachedEmbedder(GeminiEmbedder(CONFIG["embedding_model"], CONFIG["dimensions"]))
    store = PgVectorStore(os.environ["DATABASE_URL"], CONFIG["dimensions"])
    store.create_schema()

    timing = {}
    for s, chunks in chunk_sets.items():
        t = time.time()
        vecs = emb.docs([c.text for c in chunks])
        store.upsert(s, chunks, vecs)
        before = store.count(s)
        store.upsert(s, chunks, vecs)  # nạp lại lần 2: số dòng phải giữ nguyên
        after = store.count(s)
        print(f"[{s}] {len(chunks)} chunks | DB {before} -> nạp lại {after} | "
              f"{'OK không trùng' if before == after == len(chunks) else 'LỖI TRÙNG'}")
        timing[s] = round(time.time() - t, 2)

    qs = [json.loads(l) for l in open(ROOT / "data/benchmark.jsonl", encoding="utf-8") if l.strip()]
    traces = []
    for q in qs:
        qv = emb.query(q["question"])
        for s, index, use_filter in [("A", "A", False), ("B", "B", False), ("C", "B", True)]:
            f = q.get("filter") if use_filter else None
            res = store.search(index, qv, CONFIG["top_k"], f)
            traces.append(evaluate_query(q, res, s, f))

    with open(RES / "trace.jsonl", "w", encoding="utf-8") as fh:
        for t in traces:
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")
    summary = summarize(traces)
    filt = [t for t in traces if t["strategy"] == "C" and t["filter"]]
    run_info = {**CONFIG, "chunks": {k: len(v) for k, v in chunk_sets.items()},
                "embedding_api_texts_this_run": emb.api_calls, "load_seconds": timing,
                "total_seconds": round(time.time() - t0, 2), "cost": "0 (Gemini free tier)",
                "C_filter_respected": f"{sum(bool(t['filter_respected']) for t in filt)}/{len(filt)}",
                "summary": summary}
    (RES / "run_summary.json").write_text(json.dumps(run_info, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n| Strategy | Split | Hit@1 | Hit@3 | Evidence bị tách |")
    print("|---|---|---|---|---|")
    for r in summary:
        print(f"| {r['strategy']} | {r['split']} | {r['hit@1']} ({r['hit@1_pct']}%) | "
              f"{r['hit@3']} ({r['hit@3_pct']}%) | {r['evidence_split']} |")
    print(f"\nC tuân thủ filter: {run_info['C_filter_respected']} | "
          f"text gọi API lần này: {emb.api_calls} | tổng {run_info['total_seconds']}s")


if __name__ == "__main__":
    main()