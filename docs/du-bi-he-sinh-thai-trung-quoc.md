# 🇨🇳 Danh Mục Dự Bị — Hệ Sinh Thái AI Trung Quốc

> **Tạo:** 7/7/2026 (phiên rà soát, tra web cùng ngày) · **Vai trò:** danh mục DỰ BỊ cho **tháng 9/2026 trở đi & năm 2027** — giống [beyond-rag-phase-2.md](beyond-rag-phase-2.md).
>
> ⛔ **CHỐT CHẶN:** KHÔNG món nào trong file này được xếp lịch trước **13/8/2026** (deadline CV). Ngoại lệ duy nhất: mục IV-1 (swap model 2h) — và chỉ khi Tuần 8 rảnh thật sự.

---

## I. Sự thật ít ai để ý: bạn ĐÃ đứng trên vai hệ sinh thái này

Không phải "thị trường xa lạ cần khám phá" — pipeline hiện tại của bạn đã là hàng Trung Quốc một nửa:

| Đang dùng trong dự án | Của ai |
|---|---|
| `BAAI/bge-m3` (embedding, Ngày 10 → 40%) | BAAI — Viện AI Bắc Kinh |
| `BAAI/bge-reranker-v2-m3` (Ngày 11 → 60%) | BAAI |
| Qwen3-Embedding (đã thử, dừng vì CPU chậm) | Alibaba |
| DeepSeek V3.2 trong bảng chi phí agent loop | DeepSeek |

👉 **Câu chuyện phỏng vấn có sẵn:** *"Tôi chọn model theo đo lường trên golden set của mình, không theo quốc tịch hãng — và thực tế open-source Trung Quốc thắng ở tầng embedding/rerank của tôi."* Đây là câu trả lời rất "engineer" cho câu hỏi nhạy cảm kiểu "em nghĩ gì về model TQ vs Mỹ".

---

## II. Bản đồ 4 nhà chính (tình hình ~7/2026)

| Nhà | Model đỉnh | Mạnh nhất ở | License | Một-số-neo |
|---|---|---|---|---|
| **DeepSeek** | V4 Pro | Giá sàn + coding tổng quát | open-weight | dẫn bảng coding ~89.8 điểm (BenchLM) |
| **Alibaba Qwen** | Qwen3.5 / Qwen3-Coder | Họ model RỘNG nhất (embedding→coder), license thoáng nhất | **Apache 2.0** | Qwen 3.6 Plus: free, 1M context |
| **Zhipu GLM** | GLM-5.1 | Long-horizon coding, giá/hiệu năng | **MIT** | ≈94% Claude Opus coding với ~nửa giá; top SWE-Bench Pro 4/2026 |
| **Moonshot Kimi** | K2.5 / K2.6 | Agentic coding chuyên biệt | open-weight | coding ~88.7 điểm |

**Chắt lọc cho MÌNH:** 2 cái tên đáng nhớ nhất là **Qwen** (vì Apache 2.0 = xài thương mại không lăn tăn, họ model phủ đúng stack của bạn) và **GLM** (vì MIT + rẻ = ứng viên số 1 thay flash-lite cho agent loop nếu cần).

---

## III. API free / siêu rẻ (kiểm chứng 7/7/2026 — hạn mức đổi nhanh, verify lại trước khi dùng)

| Nguồn | Free tier | Ghi chú |
|---|---|---|
| **ModelScope** (HuggingFace của TQ) | **2.000 req/ngày** cho Qwen3.5 + DeepSeek | rộng nhất (~53 model free); cần tài khoản Alibaba |
| **Zhipu Z.AI** | GLM-4.7-Flash free, **200K context**, không cần thẻ | giới hạn 1 concurrent request |
| **SiliconFlow** | 3 model free, OpenAI-compatible | infra tối ưu cho user TQ, latency từ VN cần đo |
| **GLM Coding Plan** | (trả phí) từ ~$3–6/tháng | "value pick 2026" theo codingplan.org |

**So với hiện tại:** bạn đang trả tiền Vertex cho `gemini-2.5-flash-lite` ($0.10/$0.40). ModelScope 2.000 req/ngày free = đủ chạy **toàn bộ seeded-bug benchmark nhiều lần mà $0** — đáng giá nhất khi cần chạy ablation lặp lại nhiều lần (tháng 9+).

---

## IV. Món mang về được — soi qua Lăng kính 6 câu

### IV-1. Ablation "agent loop chạy model TQ" — micro-PoC 2h ⭐ ROI cao nhất
- **Bài toán & nút thắt:** benchmark Tuần 4 chỉ đo trên 1 model (flash-lite) → nhà tuyển dụng hỏi "đổi model thì recall/FP đổi không?" là nghẹn. Đây là lỗ hổng THẬT của báo cáo.
- **Cách làm:** GLM-4.7-Flash (free) hoặc Qwen qua ModelScope đều OpenAI-compatible → viết 1 client swap cạnh `client` google-genai (~30'), chạy lại benchmark, thêm 1 hàng vào bảng kết quả.
- **Khi nào KHÔNG:** trước khi benchmark chính chạy xong và ổn định. Đổi model giữa chừng = đổi 2 biến.
- **Chi phí:** $0 (free tier) · ~2h · reversibility 100% (thêm client, không sửa logic).
- **Trưởng thành:** API production-grade, hàng triệu dev dùng.
- **Bằng chứng:** chính seeded-bug benchmark là trọng tài. Số CV mới nếu đẹp: *"recall giữ nguyên khi swap sang model open-weight free — auditor không phụ thuộc 1 vendor."*
- **Slot:** Tuần 8 nếu rảnh, không thì tháng 9. **Đây là món duy nhất được phép chen trước 13/8.**

### IV-2. RAGFlow — đọc code module document-parsing (nối thẳng Phase 2 PDF/invoice)
- **Bài toán:** Phase 2 của bạn (đã chốt trong memory: ingestion PDF/hóa đơn SAU checkpoint auditor) cần deep-document-understanding — đúng thứ RAGFlow (InfiniFlow, TQ) làm tốt nhất thị trường open-source, "parsing leagues ahead" với doc enterprise phức tạp.
- **Cách dùng ĐÚNG:** không phải cài xài, mà **đọc kiến trúc module parser** của nó như đã đọc `support-rag-assistant` — học cách họ tách layout/table/OCR trước khi tự build bản mini.
- **Khi nào KHÔNG:** đem cả platform RAGFlow vào dự án nhỏ = vác voi cày ruộng.
- **Slot:** tháng 9, mở màn Phase 2.

### IV-3. LlamaFactory — cửa vào fine-tuning (kỹ năng khát 2026)
- **Bài toán:** khảo sát tuyển dụng 2026: LLM fine-tuning nằm top kỹ năng khó tuyển; CV bạn hiện chỉ có RAG + agent, chưa có tuning.
- **Giải pháp:** LlamaFactory (TQ) = chuẩn de-facto fine-tune hàng trăm model qua 1 giao diện; QLoRA model nhỏ (Qwen3-4B) chạy vừa RTX 3050 Ti 4GB của bạn.
- **Ý tưởng dự án dự bị 2027:** fine-tune model nhỏ **phân loại findings** (true/false positive) từ chính dữ liệu benchmark bạn tự tạo — khép vòng "dữ liệu tự sinh → model tự luyện", câu chuyện rất đẹp nối tiếp auditor.
- **Khi nào KHÔNG:** khi RAG/prompt còn giải được (bài học cũ: đừng tune cái retrieval sửa được).
- **Slot:** năm 2027, sau khi có việc/thực tập.

### IV-4. MetaGPT / OpenManus — đọc để ĐỐI CHIẾU, không phải để theo
- **Giá trị:** MetaGPT mô phỏng cả công ty phần mềm bằng role-playing agents — đọc kiến trúc nó để kiểm chứng ngược nguyên tắc "kiềm chế 2-agent" của bạn: họ trả giá gì (token, độ ổn định) cho N vai trò?
- **Câu hỏi mang theo khi đọc:** "vai trò nào của họ thật sự tách bạch, vai trò nào chỉ là prompt khác nhau trên cùng 1 model?"
- **Slot:** đọc chơi buổi tối, bất kỳ lúc nào sau CV.

### IV-5. Dify (138k ⭐) — biết để NÓI CHUYỆN, không phải để dùng
- **Nó là gì:** platform low-code dựng LLM app (visual workflow + RAG + agent), 1M app đã deploy — nhiều công ty VN/SME dùng thật.
- **Giá trị với bạn:** bạn build tay từng lớp nên đi phỏng vấn gặp công ty đang xài Dify, câu *"Dify của anh chị làm X thì tương đương lớp Y em tự viết"* là đòn ghi điểm. Học cách map, không học cách dùng.
- **Khi nào KHÔNG:** thay việc tự build bằng kéo-thả = phản bội chính mục tiêu học bản chất của lộ trình.

---

## V. Góc thị trường & nghề nghiệp (cho định vị 2027)

1. **Công ty VN đang chạy model TQ rất nhiều** (DeepSeek/Qwen vì rẻ + open-weight tự host được). Biết **đọc license đúng** là điểm cộng phỏng vấn hiếm: Qwen = Apache 2.0 (thoáng nhất), GLM-5.1 = MIT, DeepSeek/Kimi = open-weight có điều kiện riêng — "open-source" KHÔNG phải một khối đồng nhất.
2. **ModelScope = HuggingFace phía TQ** — kho model + dataset + demo; nguồn cập nhật SOTA embedding/rerank tiếng Trung-đa ngữ (ảnh hưởng trực tiếp chất lượng tiếng Việt, như VN-MTEB đã cho thấy với BGE).
3. **Rủi ro cần nói được khi phỏng vấn:** hạn mức free đổi nhanh (Qwen coder free tier đã có kế hoạch kết thúc Q2/2026), data-residency khi gọi API TQ cho dữ liệu khách hàng nhạy cảm → tự host open-weight là đường thoát (và là lý do open-weight TQ thắng ở SME).

### 💬 Đáp án mẫu phỏng vấn (bỏ túi)

**Hỏi: "Em chọn LLM cho dự án thế nào giữa một rừng model Mỹ-Trung?"**

> *"Tôi tách 3 lớp quyết định: **(1) đo được** — chạy benchmark của chính tôi (seeded-bug) trên 2–3 ứng viên, không tin leaderboard suông; **(2) chi phí vận hành** — agent loop gọi LLM hàng chục lần/audit nên giá input/output token quyết định, model TQ đang giữ giá sàn; **(3) ràng buộc pháp lý** — license (Apache/MIT/có điều kiện) và data-residency: dữ liệu khách nhạy cảm thì tự host open-weight thay vì gọi API xuyên biên giới. Trong dự án của tôi, tầng embedding/rerank là BGE của BAAI vì nó thắng trên golden set của tôi, còn LLM generation là Gemini vì lúc đó tôi cần độ ổn định API hơn giá."*

---

## VI. Những gì CỐ TÌNH không mang về (để khỏi cám dỗ)

- **Đổi LLM chính của auditor trước 13/8** — đổi vendor giữa benchmark = vỡ apples-to-apples.
- **Coding plan subscription** ($3–50/tháng) — bạn đang học build, không cần thuê thợ code hộ.
- **Dùng Dify/RAGFlow làm nền dự án CV** — CV của bạn mạnh CHÍNH VÌ tự build từng lớp.
- **Kimi K2/DeepSeek self-host** — model trăm tỷ tham số, RTX 3050 Ti 4GB không có cửa; chỉ dùng qua API.

---

*Nguồn tra 7/7/2026: BenchLM Chinese leaderboard · codingplan.org · freellm.net (ModelScope/Zhipu/SiliconFlow free tiers) · dev.to "5 Chinese AI Open-Source Tools" · GitHub Dify/MetaGPT. Hạn mức & giá đổi theo tuần — verify lại trước khi dùng thật.*
