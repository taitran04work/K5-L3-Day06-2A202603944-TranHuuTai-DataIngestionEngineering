# Audit coherence (0 = cắt giữa ý / thiếu chủ thể; 1 = hiểu một phần; 2 = tự hiểu, trọn ý)

Mẫu: vị trí = đầu unit u001..u010 (chọn trước khi chấm, sinh bằng `scripts/make_audit.py`). C dùng chung chunk với B.
Nhãn: nháp do AI (Claude) đề xuất — học viên XÁC NHẬN/SỬA TRƯỚC KHI NỘP.

## Strategy A (fixed 500 / overlap 50)

| # | Vị trí | chunk_id | ký tự | Điểm | Lý do |
|---|---|---|---:|---|---|
| 1 | u001 | u001:A:000 | 499 | 1 | Mở đầu đúng heading, kết thúc cắt giữa câu ("This shift creates") |
| 2 | u002 | u002:A:000 | 500 | 1 | Đầu trọn ý, cuối cắt giữa câu ("Relying entirely on a general-pu") |
| 3 | u003 | u003:A:000 | 500 | 1 | Cắt giữa câu về nhóm người trả lời khảo sát |
| 4 | u004 | u004:A:000 | 500 | 1 | Cắt giữa số liệu 76.7% ("on the five-poi") |
| 5 | u005 | u005:A:000 | 500 | 1 | Cắt giữa câu tóm tắt khảo sát |
| 6 | u006 | u006:A:000 | 500 | 1 | Cắt trước bảng pain point, bảng nằm ở chunk sau |
| 7 | u007 | u007:A:000 | 500 | 1 | "The rubric…" thiếu ngữ cảnh trước; cuối cắt giữa câu |
| 8 | u008 | u008:A:000 | 500 | 1 | Cắt giữa ý về nền tảng quốc tế |
| 9 | u009 | u009:A:000 | 500 | 1 | Cắt giữa dòng bảng "Primary Users" (nguyên nhân miss q05) |
| 10 | u010 | u010:A:000 | 500 | 1 | Danh sách 3 hệ thống bị cắt ("P") |

**Trung bình A: 10/20 = 1.0 /2 (n = 10)**

## Strategy B / C (by paragraph, max 1000)

| # | Vị trí | chunk_id | ký tự | Điểm | Lý do |
|---|---|---|---:|---|---|
| 1 | u001 | u001:B:000 | 21 | 0 | Chunk chỉ có heading "1. Product Background", không có nội dung |
| 2 | u002 | u002:B:000 | 713 | 2 | Trọn đoạn về hạn chế của LLM tổng quát |
| 3 | u003 | u003:B:000 | 72 | 0 | Chỉ có heading 1.2, không có nội dung |
| 4 | u004 | u004:B:000 | 688 | 2 | Trọn 2 ý khảo sát (53.0%, 76.7%) |
| 5 | u005 | u005:B:000 | 942 | 2 | Trọn đoạn tóm tắt khảo sát |
| 6 | u006 | u006:B:000 | 933 | 2 | Giữ trọn bảng pain point HR |
| 7 | u007 | u007:B:000 | 234 | 1 | "The rubric…" phụ thuộc đoạn ở unit trước |
| 8 | u008 | u008:B:000 | 898 | 2 | Trọn ý về nền tảng chưa bản địa hóa |
| 9 | u009 | u009:B:000 | 934 | 1 | Kết thúc bằng heading treo "Strengths" |
| 10 | u010 | u010:B:000 | 193 | 2 | Ngắn nhưng tự hiểu được (Gap for AI-SPEIS) |

**Trung bình B/C: 14/20 = 1.4 /2 (n = 10)**

Phát hiện: B tạo chunk chỉ chứa heading (min 21 ký tự) vì flush khi gặp heading liên tiếp → cải tiến: gộp heading vào đoạn kế tiếp.
