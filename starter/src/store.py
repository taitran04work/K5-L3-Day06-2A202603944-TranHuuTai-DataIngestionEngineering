"""Lưu và tìm vector bằng PostgreSQL + pgvector (cosine distance)."""
import json
from typing import Any

import psycopg

from .models import Chunk

# Chỉ cho phép filter trên các cột này -> tránh SQL injection qua tên cột
ALLOWED_FILTERS = {"chapter", "section", "document_id", "page_id"}


def _vec(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in v) + "]"


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions phải > 0")
        self.url = database_url
        self.dim = dimensions

    def _conn(self):
        return psycopg.connect(self.url, autocommit=True)

    def create_schema(self) -> None:
        with self._conn() as c:
            c.execute("CREATE EXTENSION IF NOT EXISTS vector")
            c.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id    TEXT PRIMARY KEY,
                    strategy    TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    source      TEXT NOT NULL,
                    page        INT  NOT NULL,
                    page_id     TEXT NOT NULL,
                    section     TEXT,
                    chapter     TEXT,
                    text        TEXT NOT NULL,
                    metadata    JSONB NOT NULL,
                    embedding   vector({self.dim}) NOT NULL
                )""")
            c.execute("CREATE INDEX IF NOT EXISTS chunks_strategy_idx ON chunks (strategy, chapter)")

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks nhưng {len(vectors)} vectors")
        for v in vectors:
            if len(v) != self.dim:
                raise ValueError(f"vector {len(v)} chiều, store cần {self.dim}")
        ids = [ch.chunk_id for ch in chunks]
        docs = sorted({ch.document_id for ch in chunks})
        with self._conn() as c, c.cursor() as cur:
            for ch, v in zip(chunks, vectors):
                m = ch.metadata
                cur.execute("""
                    INSERT INTO chunks (chunk_id, strategy, document_id, source, page, page_id,
                                        section, chapter, text, metadata, embedding)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        text = EXCLUDED.text, metadata = EXCLUDED.metadata,
                        section = EXCLUDED.section, chapter = EXCLUDED.chapter,
                        page = EXCLUDED.page, page_id = EXCLUDED.page_id,
                        embedding = EXCLUDED.embedding
                """, (ch.chunk_id, strategy, ch.document_id, ch.source, ch.page, m["page_id"],
                      m.get("section"), m.get("chapter"), ch.text,
                      json.dumps(m, ensure_ascii=False), _vec(v)))
            # Xóa chunk cũ không còn tồn tại (khi dữ liệu nguồn đổi)
            cur.execute("""
                DELETE FROM chunks
                WHERE strategy = %s AND document_id = ANY(%s) AND NOT (chunk_id = ANY(%s))
            """, (strategy, docs, ids))
            print(f"[{strategy}] upsert {len(ids)} | xóa chunk cũ: {cur.rowcount}")

    def count(self, strategy: str) -> int:
        with self._conn() as c:
            return c.execute("SELECT count(*) FROM chunks WHERE strategy = %s", (strategy,)).fetchone()[0]

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        where, params = ["strategy = %s"], [strategy]
        for k, v in (filters or {}).items():
            if k not in ALLOWED_FILTERS:
                raise ValueError(f"Filter không hợp lệ: {k}")
            where.append(f"{k} = %s")
            params.append(v)
        sql = f"""
            SELECT chunk_id, page_id, section, chapter, text, metadata,
                   1 - (embedding <=> %s::vector) AS score
            FROM chunks WHERE {' AND '.join(where)}
            ORDER BY embedding <=> %s::vector
            LIMIT %s"""
        qv = _vec(query_vector)
        with self._conn() as c:
            rows = c.execute(sql, [qv, *params, qv, top_k]).fetchall()
        return [{"chunk_id": r[0], "page_id": r[1], "section": r[2], "chapter": r[3],
                 "text": r[4], "metadata": r[5], "score": float(r[6])} for r in rows]