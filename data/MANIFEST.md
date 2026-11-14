# Data Manifest — Day 06

## Tài liệu

| Trường | Giá trị |
|---|---|
| source_id | `aispeis-r1-v1.3` |
| title | Vision & Scope Document — Development of an AI-Integrated System for the Practice and Evaluation of Interview Skills (AI-SPEIS) – Report 1 |
| source_path_or_url | `data/AI-SPEIS_Report1_Vision & Scope Document_v1.3.docx` |
| document_type | Vision & Scope report (đồ án nhóm) |
| language | en (có tên riêng/tiếng Việt xen kẽ) |
| version | v1.3 (Last Updated 09/08/2026, theo trang bìa tài liệu) |
| authors | Trần Hữu Tài (chủ biên), Nguyễn Thành Công, Trần Trung Kiên, Hoàng Anh Tú, Đồng Văn Quyến; reviewer: Bùi Trung Hiếu (mentor) |
| license_or_permission | Đồ án do học viên (Trần Hữu Tài) đồng tác giả và chủ biên; nhóm đồng ý dùng cho lab; chỉ dùng nội bộ, không phân phối lại. Không chứa dữ liệu cá nhân nhạy cảm ngoài tên thành viên/mentor; số liệu khảo sát ở dạng tổng hợp. |
| accessed_at | 2026-11-14 |
| file_size | 4,930,364 bytes |
| sha256 | `be2a516be137bf760221c55a4ad21c1930b085790aedaddb6f090f3d829c476e` |
| format | DOCX (xuất từ Google Docs, không có metadata số trang `docProps/app.xml`) |

## Quy tắc tính "trang nội dung"

DOCX không có phân trang vật lý cố định (số trang phụ thuộc phần mềm render). Theo GUIDE.md, áp dụng quy tắc cho tài liệu không phân trang:

- Chia nội dung đã chuẩn hóa **theo thứ tự** thành các đơn vị nguồn (`page_id`) có **≥ 1.500 ký tự**, cắt tại ranh giới đoạn văn hoặc dòng bảng (không cắt giữa đoạn).
- **Loại trừ**: trang bìa (bảng thông tin dự án), Document Change History, mục lục (TABLE OF CONTENTS) và mục References (ingestion dừng tại heading "References", ghi `stop_at_references` trong `starter/results/ingestion_log.json`).
- Phần đuôi < 1.500 ký tự được gộp vào đơn vị cuối (log `tail_merged`, 844 ký tự) thay vì tạo đơn vị thiếu.
- Mỗi đơn vị lưu: `page_id` (`aispeis-r1-v1.3#u001`…), `section` (heading của đoạn đầu đơn vị), `chapter`, số ký tự. Nội dung đầy đủ: `starter/results/units.jsonl`.
- Hình ảnh/biểu đồ (Figure 1–12) không OCR; chỉ giữ caption, văn bản và bảng.

**Kết quả thực tế: 31 đơn vị, 53.334 ký tự.** Nếu đếm trang vật lý, nội dung chính chỉ ~26 trang (tr. 5–30 theo mục lục), nên dùng quy tắc đơn vị ký tự.

## Danh sách đơn vị

| page_id | section | ký tự |
|---|---|---:|
| aispeis-r1-v1.3#u001 | 1. Product Background | 1830 |
| aispeis-r1-v1.3#u002 | 1.1 Project Context and Motivation | 1623 |
| aispeis-r1-v1.3#u003 | 1.2 Real-World Problems Identified from User and HR Stakeholder Research | 1725 |
| aispeis-r1-v1.3#u004 | 1.2.1 Target User Survey | 1834 |
| aispeis-r1-v1.3#u005 | 1.2.1 Target User Survey | 1661 |
| aispeis-r1-v1.3#u006 | 1.2.2 HR Stakeholder Interviews | 1833 |
| aispeis-r1-v1.3#u007 | 1.2.2 HR Stakeholder Interviews | 1774 |
| aispeis-r1-v1.3#u008 | 1.3 Limitations of Existing Solutions | 1517 |
| aispeis-r1-v1.3#u009 | 2.1 Traditional Self-Practice and Manual Preparation | 1731 |
| aispeis-r1-v1.3#u010 | 2.1 Traditional Self-Practice and Manual Preparation | 1560 |
| aispeis-r1-v1.3#u011 | 2.2.1 Exponent AI / Exponent | 1592 |
| aispeis-r1-v1.3#u012 | 2.2.2 Interviewing.io | 1544 |
| aispeis-r1-v1.3#u013 | 2.2.3 Pramp / Exponent Practice | 1784 |
| aispeis-r1-v1.3#u014 | 2.3 Improvement Opportunities for AI-SPEIS | 1734 |
| aispeis-r1-v1.3#u015 | 2.4 Identified Gaps | 1811 |
| aispeis-r1-v1.3#u016 | 2.4 Identified Gaps | 1816 |
| aispeis-r1-v1.3#u017 | 3. Proposed Solution | 1525 |
| aispeis-r1-v1.3#u018 | 3.1 Research Objective | 1519 |
| aispeis-r1-v1.3#u019 | 3.1 Research Objective | 1577 |
| aispeis-r1-v1.3#u020 | 3.2 AI Approach and Research Direction | 1555 |
| aispeis-r1-v1.3#u021 | 4.1 Major Features | 1861 |
| aispeis-r1-v1.3#u022 | 4.1 Major Features | 1666 |
| aispeis-r1-v1.3#u023 | 4.2 Limitations & Exclusions | 1653 |
| aispeis-r1-v1.3#u024 | 4.2 Limitations & Exclusions | 1571 |
| aispeis-r1-v1.3#u025 | 4.2 Limitations & Exclusions | 1861 |
| aispeis-r1-v1.3#u026 | 5.1 Business & Operational Impact | 1729 |
| aispeis-r1-v1.3#u027 | 5.1 Business & Operational Impact | 1921 |
| aispeis-r1-v1.3#u028 | 5.2 User Experience Impact | 1622 |
| aispeis-r1-v1.3#u029 | 5.2 User Experience Impact | 1876 |
| aispeis-r1-v1.3#u030 | 5.3 Research & Technical Contribution | 1514 |
| aispeis-r1-v1.3#u031 | 5.4 Planned Next Steps After Project Completion | 2515 |
| **Tổng** | **31 đơn vị** | **53334** |

## Trường metadata

| Trường | Kiểu | Nguồn giá trị | Lý do |
|---|---|---|---|
| `document_id`, `source` | text | source_id và tên file | Truy vết nguồn (bắt buộc) |
| `page`, `page_id` | int, text | số thứ tự đơn vị | Truy vết vị trí (tương đương số trang) |
| `section` | text | heading đánh số trong tài liệu | Ngữ cảnh, kiểm tra metadata |
| `chapter` | text ("1"–"5") | số đầu của heading | **Trường filter** (cấu hình C): câu hỏi thường gắn phạm vi chương (Scope, Limitations, Contributions) |

## Ghi chú / rủi ro

- Chỉ một tài liệu: filter theo `source` không có tác dụng; filter chính là `chapter`.
- Metadata mức đơn vị lấy theo đoạn đầu: u025 bắt đầu ở cuối 4.2 nên ghi `4.2` dù chứa đầu chương 5. Chunk B/C tự cập nhật section/chapter theo heading bên trong (chunk `u025:B:001` → chapter 5).
- "Đơn vị" ≠ trang thật: benchmark trích nguồn bằng `page_id`.
