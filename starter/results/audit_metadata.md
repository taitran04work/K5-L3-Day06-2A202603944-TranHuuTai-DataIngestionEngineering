# Audit metadata — C, 5 câu test x top-3 (15 bản ghi)

Tự động (scripts/make_audit.py): page_id tồn tại, text chunk nằm trong unit page_id, chapter khớp filter.
Thủ công: đối chiếu source (tên file docx), page_id, section/chapter với heading thật trong tài liệu.
Nhãn: nháp do AI đề xuất — học viên XÁC NHẬN TRƯỚC KHI NỘP.

| Câu | Rank | chunk_id | chapter | section | text∈unit | filter | Đủ & đúng | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| q16 | 1 | u004:B:002 | 1 | 1.2.1 Target User Survey | OK | N/A | ✔ | |
| q16 | 2 | u029:B:000 | 5 | 5.2 User Experience Impact | OK | N/A | ✔ | |
| q16 | 3 | u005:B:000 | 1 | 1.2.1 Target User Survey | OK | N/A | ✔ | |
| q17 | 1 | u024:B:001 | 4 | 4.2 Limitations & Exclusions | OK | OK | ✔ | |
| q17 | 2 | u023:B:000 | 4 | 4.2 Limitations & Exclusions | OK | OK | ✔ | |
| q17 | 3 | u023:B:001 | 4 | 4.2 Limitations & Exclusions | OK | OK | ✔ | |
| q18 | 1 | u019:B:000 | 3 | 3.1 Research Objective | OK | N/A | ✔ | |
| q18 | 2 | u017:B:001 | 3 | 3. Proposed Solution | OK | N/A | ✔ | |
| q18 | 3 | u022:B:001 | 4 | 4.1 Major Features | OK | N/A | ✔ | Tiểu mục không đánh số "Research and AI Evaluation Scope" gán vào 4.1 — chấp nhận được |
| q19 | 1 | u023:B:001 | 4 | 4.2 Limitations & Exclusions | OK | N/A | ✔ | |
| q19 | 2 | u021:B:000 | 4 | 4.1 Major Features | OK | N/A | ✔ | |
| q19 | 3 | u031:B:000 | 5 | 5.4 Planned Next Steps | OK | N/A | ✔ | |
| q20 | 1 | u027:B:001 | 5 | 5.2 User Experience Impact | OK | OK | ✔ | |
| q20 | 2 | u025:B:002 | 5 | 5.1 Business & Operational Impact | OK | OK | ✔ | Unit u025 ghi 4.2 nhưng chunk B tự cập nhật đúng 5.1 |
| q20 | 3 | u029:B:000 | 5 | 5.2 User Experience Impact | OK | OK | ✔ | |

**Metadata đủ và đúng: 15/15. Filter tuân thủ: test 2/2 câu; toàn benchmark 4/4.**

Hữu dụng: `chapter` giới hạn q17 vào nhóm Limitations, q20 loại nhiễu từ chương 1.
Hạn chế: metadata mức unit (u025) sai khi unit vắt qua 2 chương; tiểu mục không đánh số bị gán vào mục cha.
