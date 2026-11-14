"""Fixed-size (A) và paragraph-aware (B/C) chunking, giữ metadata truy vết."""
import json
import re
from pathlib import Path

from .models import Chunk, DocumentPage

HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+[A-Z]")
SENT_RE = re.compile(r"(?<=[.!?])\s+")


def _make_chunk(page: DocumentPage, strategy: str, idx: int, text: str, extra: dict) -> Chunk:
    meta = {**page.metadata, **extra, "strategy": strategy, "chunk_index": idx, "chars": len(text)}
    return Chunk(
        chunk_id=f"{page.metadata['page_id']}:{strategy}:{idx:03d}",  # ID ổn định -> upsert không trùng
        document_id=page.document_id,
        source=page.source,
        page=page.page,
        text=text,
        metadata=meta,
    )


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    if overlap >= size:
        raise ValueError("overlap phải nhỏ hơn size")
    text, chunks, start, idx = page.text, [], 0, 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(_make_chunk(page, "A", idx, piece, {"char_start": start}))
            idx += 1
        if start + size >= len(text):
            break
        start += size - overlap
    return chunks


def _split_long(par: str, max_size: int) -> list[str]:
    """Cắt đoạn quá dài theo câu; câu vẫn quá dài thì cắt cứng."""
    out, cur = [], ""
    for sent in SENT_RE.split(par):
        while len(sent) > max_size:
            out.append(sent[:max_size])
            sent = sent[max_size:]
        if cur and len(cur) + 1 + len(sent) > max_size:
            out.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        out.append(cur)
    return out


def by_paragraph(page: DocumentPage, max_size: int = 1000) -> list[Chunk]:
    section = page.metadata.get("section", "")
    chapter = page.metadata.get("chapter", "")
    chunks, buf, idx = [], [], 0
    buf_meta = {"section": section, "chapter": chapter}

    def flush():
        nonlocal buf, idx
        if buf:
            chunks.append(_make_chunk(page, "B", idx, "\n\n".join(buf), dict(buf_meta)))
            idx += 1
            buf = []

    for par in [p.strip() for p in page.text.split("\n\n") if p.strip()]:
        m = HEADING_RE.match(par)
        if m and len(par) < 120:
            flush()  # heading mới -> bắt đầu chunk mới, cập nhật section/chapter
            section, chapter = par, m.group(1).split(".")[0]
        if not buf:
            buf_meta = {"section": section, "chapter": chapter}
        for piece in _split_long(par, max_size) if len(par) > max_size else [par]:
            if buf and sum(len(b) + 2 for b in buf) + len(piece) > max_size:
                flush()
                buf_meta = {"section": section, "chapter": chapter}
            buf.append(piece)
    flush()
    return chunks


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    pages = []
    for line in open(root / "results/units.jsonl", encoding="utf-8"):
        d = json.loads(line)
        pages.append(DocumentPage(**d))
    for name, fn in [("A", lambda p: fixed_size(p, 500, 50)), ("B", lambda p: by_paragraph(p, 1000))]:
        chunks = [c for p in pages for c in fn(p)]
        with open(root / f"results/chunks_{name}.jsonl", "w", encoding="utf-8") as fh:
            for c in chunks:
                fh.write(json.dumps(c.__dict__, ensure_ascii=False) + "\n")
        sizes = [len(c.text) for c in chunks]
        print(f"{name}: {len(chunks)} chunks | min {min(sizes)} | avg {sum(sizes)//len(sizes)} | max {max(sizes)}")
    # Kiểm tra lỗi u025: chunk B chứa "5. Expected Contributions" phải có chapter 5
    for line in open(root / "results/chunks_B.jsonl", encoding="utf-8"):
        c = json.loads(line)
        if c["text"].startswith("5. Expected"):
            print("u025 fix:", c["chunk_id"], "-> chapter", c["metadata"]["chapter"])