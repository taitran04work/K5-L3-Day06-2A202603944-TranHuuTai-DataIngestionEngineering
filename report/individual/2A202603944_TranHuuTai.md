# Báo cáo cá nhân — Day 6

> Bản nháp do AI (Claude) hỗ trợ soạn từ số liệu thật trong `starter/results/`; học viên đọc lại, xác nhận nhãn thủ công và chịu trách nhiệm nội dung (RULES.md cho phép dùng AI, yêu cầu ghi rõ công cụ và cách kiểm tra).

## Dữ liệu và pipeline
- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:** Corpus là *AI-SPEIS Report 1 — Vision & Scope Document v1.3* (DOCX, đồ án nhóm do học viên chủ biên; dùng nội bộ cho lab, chi tiết và sha256 trong `data/MANIFEST.md`). DOCX không có phân trang cố định nên áp dụng quy tắc GUIDE cho tài liệu không phân trang: loại bìa, change history, mục lục và References; chia theo thứ tự thành đơn vị ≥1.500 ký tự tại ranh giới đoạn/dòng bảng → **31 đơn vị (`aispeis-r1-v1.3#u001`…`u031`)**. (Nếu đếm trang vật lý, nội dung chỉ ~26 trang nên không dùng cách đếm trang.)
- **Chuẩn hóa, lỗi và giới hạn:** `python-docx` đọc paragraph + bảng theo đúng thứ tự; Unicode NFC, bỏ ký tự điều khiển/NBSP/zero-width, gộp khoảng trắng; bảng chuyển thành dòng `ô | ô`, bỏ ô merge lặp. Log: `starter/results/ingestion_log.json` (`stop_at_references`, `tail_merged` 844 ký tự). Hình (Figure 1–12) không OCR, chỉ giữ caption. Lỗi đã phát hiện và xử lý: (1) lần đầu bảng lớn dồn vào một unit (3.7–4.8k ký tự, chỉ 28 unit) → cắt bảng theo dòng; (2) References lọt vào unit cuối → dừng tại heading References; (3) metadata mức unit sai khi unit vắt qua 2 chương (u025 ghi 4.2 nhưng chứa đầu chương 5) — B/C sửa ở mức chunk.
- **Embedding / vector store / metric / lệnh chạy / chi phí:** Google `gemini-embedding-001` (SDK `google-genai` 3.3.0), `output_dimensionality=768`, chuẩn hóa L2; task_type `RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY`. PostgreSQL 16 + pgvector (image `pgvector/pgvector:0.8.7-pg16`), `psycopg` 3.3.8, cosine distance (`<=>`), tìm chính xác (210 vector, không cần ANN index). Python 3.11.9, `python-docx` 1.2.0. Lệnh (từ `starter/`): `python -m src.ingestion` → `python scripts/check_benchmark.py` → `python -m src.chunking` → `python -m src.run` → `python scripts/make_audit.py`. Chi phí **0 đồng** (free tier, 230 text embed); 202 s lần đầu (nạp A 87 s, B 45 s — phần lớn là chờ rate limit 100 text/phút); lần sau dùng cache `results/embedding_cache.json`.
- **Metadata:** bắt buộc `document_id`, `source` (tên file), `page` (số thứ tự unit) + `page_id`. Trường lọc bổ sung: `chapter` (1–5) và `section`, lấy từ heading đánh số trong tài liệu (không suy đoán). Chọn `chapter` vì câu hỏi về tài liệu Vision & Scope thường gắn phạm vi chương (Scope, Limitations, Contributions); corpus chỉ một tài liệu nên lọc theo `source` vô nghĩa.

## Cấu hình và benchmark
- **A / B / C:** A = fixed-size 500 ký tự, overlap 50, không filter (130 chunk). B = gom paragraph tối đa 1.000 ký tự, đoạn dài cắt theo câu, heading mới bắt đầu chunk mới và cập nhật `section/chapter` (80 chunk). C = **đúng index B**, chỉ thêm filter SQL `chapter = …` cho câu hỏi có nêu phạm vi; câu không có filter chạy như B. **A–B khác ở cách chunk; B–C khác duy nhất ở filter.** Cùng corpus, model, top-k = 3, benchmark. Nạp lại lần 2: A 130→130, B 80→80 dòng (upsert theo `chunk_id` ổn định, xóa chunk cũ không còn tồn tại).
- **Benchmark:** 20 câu trong `starter/data/benchmark.jsonl`, chia trước khi chạy **15 dev (q01–q15) / 5 test (q16–q20)**; loại câu: trực tiếp, diễn đạt lại (hỏi tiếng Việt trên văn bản tiếng Anh), điều kiện/ngoại lệ, filter. **4 câu filter** (dev q10, q11; test q17, q20). Câu có số liệu lặp ở 2 unit ghi `alt_gold_pages` (q02, q11, q16). `scripts/check_benchmark.py` kiểm chứng evidence nguyên văn nằm trong unit gold và filter khớp metadata → 0 lỗi. Chỉnh sửa trước khi chạy: q15 ban đầu có filter chapter 5 nhưng unit gold u025 bị gán chapter 4 → bỏ filter thay vì sửa dữ liệu cho khớp.
- **Tiêu chí chọn (chốt trước khi xem test):** ưu tiên Evidence Hit@3 dev, rồi Hit@1 dev, rồi khả năng filter/metadata, cuối cùng tài nguyên.

## Kết quả
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
|---|---|---|---|---|---|---|
| A | dev | 6/15 | 11/15 | 130 | nạp 87 s | 0 |
| A | test | 2/5 | 4/5 | 130 | | 0 |
| B | dev | 9/15 | 12/15 | 80 | nạp 45 s | 0 |
| B | test | 1/5 | 4/5 | 80 | | 0 |
| C | dev | 9/15 | 12/15 | 80 (index B) | như B | 0 |
| C | test | 2/5 | 4/5 | 80 (index B) | | 0 |

| Strategy | Coherence trung bình /2 (n) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 |
|---|---|---|---|---|
| A | 1.0 (10) | không audit | N/A (không filter) | không audit |
| B | 1.4 (10) | không audit | N/A (không filter) | không audit |
| C | 1.4 (10, chung chunk B) | 15/15 | test 2/2; toàn bộ 4/4 | 0/1/4 → 1.8 |

**Trace, nhãn và cách chọn mẫu:** trace top-3 mọi câu × 3 cấu hình: `starter/results/trace.jsonl`; tổng hợp: `starter/results/run_summary.json`. Nhãn thủ công: `starter/results/audit_coherence.md` (vị trí = đầu unit u001–u010, chọn trước khi chấm), `audit_metadata.md` và `audit_grounding.md` (5 câu test × top-3 của C, cấu hình đã chọn). Metadata/grounding chỉ audit cho C do giới hạn thời gian.

## Phân tích và kết luận
- **A–B:** B tốt hơn trên dev (Hit@1 9 vs 6, Hit@3 12 vs 11) và coherence (1.4 vs 1.0). Nguyên nhân chính A thua: evidence bị cắt qua 2 chunk — 4 câu dev A lấy đúng trang nhưng không chunk nào chứa đủ evidence. Ví dụ **q05** (gold u009, "Primary Users | Students preparing for internships…"): chunk `u009:A:000` kết thúc giữa dòng bảng này. Ngược lại B thua A ở chi tiết nằm trong chunk dài nhiều dòng bảng — ví dụ **q12** (gold u022, FE-12 device readiness check): A trúng top-3, B/C trượt vì dòng FE-12 bị "loãng" trong chunk ~1.000 ký tự gồm FE-10…FE-13; tương tự q18 (u024, LI-09).
- **B–C:** dev bằng nhau (2 câu filter dev đã đúng sẵn ở B); test C hơn 1 câu Hit@1 — **q17** (gold u023, transcription Google Cloud STT) được đẩy lên nhờ loại nhiễu ngoài chương 4. Filter tuân thủ 4/4.
- **Chiến lược chọn:** **C** (B = C trên dev theo tiêu chí; C có thêm filter tuân thủ đầy đủ, không tốn thêm tài nguyên vì dùng chung index). Điều kiện áp dụng: câu hỏi/ngữ cảnh cung cấp phạm vi chương trước khi truy xuất; nếu không, C = B. Đánh đổi: chunk theo đoạn giữ ý tốt hơn nhưng kém nhạy với chi tiết nhỏ trong bảng; fixed-size đơn giản nhưng hay cắt evidence.
- **Hạn chế:** một tài liệu, 20 câu (test chỉ 5 → chênh 1 câu = 20 điểm %, không có ý nghĩa thống kê); câu hỏi và nhãn do một người (đồng thời là tác giả tài liệu) soạn với hỗ trợ AI → nguy cơ thiên lệch; B sinh chunk chỉ chứa heading (`u001:B:000` 21 ký tự, `u003:B:000` 72 ký tự); metadata mức unit sai ở ranh giới chương; thời gian đo bị chi phối bởi rate limit free tier; hình/biểu đồ khảo sát không được trích xuất.
- **Nếu làm lại:** gộp heading vào đoạn kế tiếp; tách bảng thành chunk theo nhóm dòng có lặp tiêu đề cột; thử chunk lai (paragraph ~600 + overlap 1 câu); thêm Report 2/3 để có filter `document_id` và test lớn hơn; tính metadata ở mức chunk ngay từ ingestion.
