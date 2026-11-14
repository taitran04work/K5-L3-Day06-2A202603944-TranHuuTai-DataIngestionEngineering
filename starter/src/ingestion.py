"""Đọc DOCX, chuẩn hóa và chia thành đơn vị nguồn >= 1.500 ký tự (quy tắc GUIDE.md)."""
import json
import re
import unicodedata
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from .models import DocumentPage

MIN_UNIT_CHARS = 1500
# Heading dạng "1. Product Background", "2.2.1 Exponent AI / Exponent"
HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+\S")
CONTENT_START = "1. Product Background"


def normalize_text(text: str) -> str:
    """NFC Unicode, bỏ ký tự điều khiển, gộp khoảng trắng; giữ xuống dòng giữa các đoạn."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _iter_blocks(doc):
    """Trả về (kind, text, style) theo đúng thứ tự trong tài liệu, gồm cả bảng."""
    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            p = Paragraph(child, doc)
            yield "p", p.text, (p.style.name if p.style is not None else "")
        elif tag == "tbl":
            t = Table(child, doc)
            rows = []
            for r in t.rows:
                cells = []
                for c in r.cells:
                    ct = c.text.strip()
                    if ct and (not cells or cells[-1] != ct):  # bỏ ô merge bị lặp
                        cells.append(ct)
                if cells:
                    rows.append(" | ".join(cells))
            yield "tbl", "\n".join(rows), "Table"


def _is_heading(text: str, style: str) -> bool:
    if style.lower().startswith("heading"):
        return True
    return bool(HEADING_RE.match(text)) and len(text) < 120 and "\t" not in text


def load_docx(path: Path, document_id: str, source: str, log: list[dict]) -> list[DocumentPage]:
    doc = Document(str(path))
    started = False
    section, chapter = "", ""
    buf: list[str] = []
    buf_section = ""
    units: list[DocumentPage] = []

    def flush():
        nonlocal buf
        text = normalize_text("\n\n".join(buf))
        if text:
            n = len(units) + 1
            units.append(DocumentPage(
                document_id=document_id,
                source=source,
                page=n,
                text=text,
                metadata={
                    "page_id": f"{document_id}#u{n:03d}",
                    "section": buf_section,
                    "chapter": buf_section.split(" ")[0].split(".")[0] if buf_section else "",
                    "chars": len(text),
                    "document_type": "vision_scope_report",
                    "version": "v1.3",
                },
            ))
        buf = []

    for i, (kind, raw, style) in enumerate(_iter_blocks(doc)):
        text = normalize_text(raw)
        if not started:
            # Bỏ bìa, change history, mục lục (dòng mục lục có tab + số trang)
            if kind == "p" and text.startswith(CONTENT_START) and "\t" not in raw:
                started = True
            else:
                continue
        if not text:
            continue
        if kind == "p" and text == "References":
            log.append({"event": "stop_at_references", "block": i})
            break
        if kind == "p" and _is_heading(text, style):
            section = text
            chapter = text.split(".")[0]
        pieces = text.split("\n") if kind == "tbl" else [text]
        for piece in pieces:
            if not buf:
                buf_section = section
            buf.append(piece)
            if sum(len(b) for b in buf) >= MIN_UNIT_CHARS:
                flush()

    if buf:  # phần đuôi < 1.500: gộp vào unit cuối thay vì tạo unit thiếu
        tail = normalize_text("\n\n".join(buf))
        if units and len(tail) < MIN_UNIT_CHARS:
            last = units[-1]
            last.text = last.text + "\n\n" + tail
            last.metadata["chars"] = len(last.text)
            log.append({"event": "tail_merged", "chars": len(tail)})
            buf = []
        else:
            flush()

    if not started:
        log.append({"event": "error", "msg": f"Không thấy mốc '{CONTENT_START}'"})
    log.append({"event": "loaded", "document_id": document_id, "units": len(units)})
    return units


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    raise NotImplementedError("Corpus hiện là DOCX; dùng load_docx")


if __name__ == "__main__":
    data = Path(__file__).resolve().parents[2] / "data"
    f = data / "AI-SPEIS_Report1_Vision & Scope Document_v1.3.docx"
    log: list[dict] = []
    units = load_docx(f, "aispeis-r1-v1.3", f.name, log)
    out = Path(__file__).resolve().parents[1] / "results"
    out.mkdir(exist_ok=True)
    with open(out / "units.jsonl", "w", encoding="utf-8") as fh:
        for u in units:
            fh.write(json.dumps(u.__dict__, ensure_ascii=False) + "\n")
    with open(out / "ingestion_log.json", "w", encoding="utf-8") as fh:
        json.dump(log, fh, ensure_ascii=False, indent=2)
    print("| page_id | section | ký tự |")
    print("|---|---|---:|")
    for u in units:
        print(f"| {u.metadata['page_id']} | {u.metadata['section'][:50]} | {u.metadata['chars']} |")
    total = sum(u.metadata["chars"] for u in units)
    print(f"| **Tổng** | **{len(units)} đơn vị** | **{total}** |")