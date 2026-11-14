# Audit grounding — C, 5 câu test (chỉ đánh giá evidence retrieval, không phải câu trả lời LLM)

Thang: 0 = không có bằng chứng; 1 = có nhưng thiếu điều kiện/ngữ cảnh; 2 = đủ trả lời và truy nguồn.
Nhãn: nháp do AI đề xuất — XÁC NHẬN TRƯỚC KHI NỘP.

| Câu | Điểm | Lý do |
|---|---|---|
| q16 | 2 | Rank 1 (u004) chứa nguyên văn mức giá 30,000–50,000 VND (38.1%) |
| q17 | 2 | Rank 3 (u023:B:001) chứa LI-05 "transcription (Google Cloud Speech-to-Text)"; rank 1–2 là nhiễu cùng chương |
| q18 | 1 | Top-3 chỉ nói dự án fine-tune model có sẵn, không train từ đầu (u022) nhưng thiếu lý do "limited data and computing resources" (nằm ở u024 LI-09, không vào top-3) |
| q19 | 2 | Rank 3 (u031) chứa câu question generation nằm ngoài MVP |
| q20 | 2 | Rank 1 (u027) chứa "Behavioral rounds guided by the STAR…" |

**Phân bố: 0 → 0 câu, 1 → 1 câu, 2 → 4 câu. Trung bình 9/10 = 1.8 /2.** (Evidence Hit@3 tự động của C trên test: 4/5, khớp.)

## q16 — Mức giá hàng tháng được người khảo sát ưa chuộng nhất là bao nhiêu?

- Đáp án kỳ vọng: 30.000–50.000 VND/tháng (38.1%)
- Gold: aispeis-r1-v1.3#u004 (+['aispeis-r1-v1.3#u029']); filter: None
- Evidence Hit@3 tự động: True

1. `aispeis-r1-v1.3#u004:B:002` (score 0.7461, hit=True): Affordable payment willingness: Figure 5 shows that approximately 69.9% of respondents were willing to pay for an online interview practice system. The most preferred price range was 30,000–50,000 VND per month (38.1%), followed by 50,000–100,000 VND per month (19.9%). These findings suggest that a freemium or low-cost subscription model is more appropriate for the target users.
2. `aispeis-r1-v1.3#u029:B:000` (score 0.7, hit=False): Overall, AI-SPEIS is expected to replace isolated and passive interview preparation with a personalized, interactive, voice-based, and feedback-driven practice experience.  Figure 12 Respondent Demand for AI-SPEIS Core Features  The survey also examined respondents' willingness to pay for an online interview practice platform. Among the 236 respondents, approximately 69.9% indicated willingness to…
3. `aispeis-r1-v1.3#u005:B:000` (score 0.6298, hit=False): Figure 2 Percentage of respondents reporting each difficulty during interview preparation.  Figure 3 How often respondents practice answering interview questions aloud  Figure 4 Respondent ratings (1–5) on the necessity of CV-personalized interview practice  Figure 5 Respondent willingness to pay for an online interview practice system  In summary, the survey findings indicate that the lack of a s…

**Điểm grounding:**    **Lý do:** 

## q17 — In the Limitations & Exclusions, which service is used for transcription?

- Đáp án kỳ vọng: Google Cloud Speech-to-Text
- Gold: aispeis-r1-v1.3#u023 (+[]); filter: {'chapter': '4'}
- Evidence Hit@3 tự động: True

1. `aispeis-r1-v1.3#u024:B:001` (score 0.6531, hit=False): LI-09 / Fine-Tuned Model Scope and Generalization / The fine-tuned model is optimized for the interview tasks, datasets, rubrics, and decision rules defined within AI-SPEIS. Performance outside the supported interview domain is not a primary objective of the project. Due to limitations in available training data and computing resources, the research focuses on adapting an existing pretrained langu…
2. `aispeis-r1-v1.3#u023:B:000` (score 0.6479, hit=False): 4.2 Limitations & Exclusions  ID / Excluded Item / Reason  LI-01 / Real-Time Video/ Image Processing / Video-based interview analysis, including facial expression tracking, eye-contact detection, and body language analysis, is excluded from the MVP to reduce project complexity.  LI-02 / Native iOS/Android Mobile Applications / The system will be built entirely as a Responsive Web Application using…
3. `aispeis-r1-v1.3#u023:B:001` (score 0.6477, hit=True): LI-04 / Direct Banking Gateway & Refund Automation / The MVP integrates with MoMo Developer Sandbox to simulate and verify the payment workflow. Real-money transactions, production payment processing, and automated refunds are excluded from the MVP because they require production merchant approval, legal compliance, and financial risk management.  LI-05 / Offline AI Model Execution / All heavy pro…

**Điểm grounding:**    **Lý do:** 

## q18 — Why does the research adapt an existing pretrained model instead of training a foundation model from scratch?

- Đáp án kỳ vọng: Due to limitations in available training data and computing resources.
- Gold: aispeis-r1-v1.3#u024 (+[]); filter: None
- Evidence Hit@3 tự động: False

1. `aispeis-r1-v1.3#u019:B:000` (score 0.7207, hit=False): The objective is not to assume that fine-tuning will necessarily outperform a general-purpose model. Instead, the project seeks to provide empirical evidence regarding when domain-specific model adaptation is beneficial for AI-assisted interview evaluation.
2. `aispeis-r1-v1.3#u017:B:001` (score 0.6929, hit=False): In parallel with the development of the functional interview platform, AI-SPEIS also includes an applied AI research track. The product track uses a general-purpose external AI model as a practical baseline for the interview workflow, while the research track explores domain-specific fine-tuning of a pretrained language model. These two approaches are developed and evaluated in parallel to investi…
3. `aispeis-r1-v1.3#u022:B:001` (score 0.6861, hit=False): In addition to the functional product scope, AI-SPEIS includes an applied AI research scope focused on domain-specific language-model adaptation. This research scope covers the preparation of structured interview datasets, fine-tuning of a selected pretrained language model, development of controlled evaluation data, and comparative evaluation between the fine-tuned model and a general-purpose ext…

**Điểm grounding:**    **Lý do:** 

## q19 — Việc sinh câu hỏi tự động (question generation) có nằm trong MVP hiện tại không?

- Đáp án kỳ vọng: Không; có thể nghiên cứu sau, nhưng nằm ngoài quy tắc nguồn câu hỏi của MVP hiện tại.
- Gold: aispeis-r1-v1.3#u031 (+[]); filter: None
- Evidence Hit@3 tự động: True

1. `aispeis-r1-v1.3#u023:B:001` (score 0.7188, hit=False): LI-04 / Direct Banking Gateway & Refund Automation / The MVP integrates with MoMo Developer Sandbox to simulate and verify the payment workflow. Real-money transactions, production payment processing, and automated refunds are excluded from the MVP because they require production merchant approval, legal compliance, and financial risk management.  LI-05 / Offline AI Model Execution / All heavy pro…
2. `aispeis-r1-v1.3#u021:B:000` (score 0.7029, hit=False): FE-05 / Centralized Question Bank & Selection / Hosts a repository of categorized interview questions and utilizes LLM support to select domain-specific questions from question bank, moving beyond static and theoretical self-study lists. User can select active saved question to start Single Question Mode / GAP-01, GAP-02  FE-06 / Subscription, Payment, and Quota Management / Provides a freemium/pr…
3. `aispeis-r1-v1.3#u031:B:000` (score 0.7025, hit=True): The first next step is to conduct user testing with students from the target group. Since the original survey already shows strong demand for personalized and feedback-based interview practice, the next validation should focus on whether students find the system useful, understandable, realistic, and easy to use. Important evaluation criteria may include question relevance, feedback usefulness, sp…

**Điểm grounding:**    **Lý do:** 

## q20 — Trong phần User Experience Impact, vòng Behavioral được hướng dẫn theo framework nào?

- Đáp án kỳ vọng: STAR (Situation, Task, Action, Result)
- Gold: aispeis-r1-v1.3#u027 (+[]); filter: {'chapter': '5'}
- Evidence Hit@3 tự động: True

1. `aispeis-r1-v1.3#u027:B:001` (score 0.6377, hit=True): 5.2 User Experience Impact  AI-SPEIS is expected to significantly improve the user experience of interview preparation by making it more personalized, interactive, and measurable.  First, students can receive interview questions based not only on their own CV but also on a specific Job Description (JD). Through CV-to-JD matching analysis, AI-SPEIS identifies skill gaps and selects highly relevant …
2. `aispeis-r1-v1.3#u025:B:002` (score 0.6259, hit=False): 5.1 Business & Operational Impact  AI-SPEIS is expected to create business and operational value by centralizing the interview preparation process into one integrated platform. Currently, respondents prepare through fragmented methods such as searching online, watching tutorial videos, asking friends, or using general-purpose AI tools. According to the survey, 64.0% of respondents search for sampl…
3. `aispeis-r1-v1.3#u029:B:000` (score 0.6149, hit=False): Overall, AI-SPEIS is expected to replace isolated and passive interview preparation with a personalized, interactive, voice-based, and feedback-driven practice experience.  Figure 12 Respondent Demand for AI-SPEIS Core Features  The survey also examined respondents' willingness to pay for an online interview practice platform. Among the 236 respondents, approximately 69.9% indicated willingness to…

**Điểm grounding:**    **Lý do:** 
