# BEYOND RAG — TRACK GIAI ĐOẠN 2 (Sau CV)

> **Tài liệu này là gì:** Nơi chứa các kiến trúc "Beyond RAG" cấp Enterprise/Solution-Architect được chắt ra từ bài nghiên cứu *"Thiết kế hệ thống AI Agentic & nền tảng truy xuất tri thức Beyond RAG"*. Đây là **sao Bắc Đẩu sau CV** — KHÔNG nhồi vào lộ trình 2 tháng.
>
> **Vì sao tách ra:** lộ trình chính là kế hoạch 2 tháng cấp Application Engineer fresher. Các thứ ở đây cần **6 tháng + phần cứng (GPU) + ngữ cảnh doanh nghiệp**. Nhồi vào 2 tháng = vi phạm chính nguyên tắc *"đỉnh tháp = kiềm chế, chọn giải pháp NHỎ nhất chạy được"* (xem [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md), thang L1→L5).
>
> **Vì sao vẫn hoãn (dù quota đã gỡ):** Ngày 6 đụng trần 429 (free tier 20 req/ngày) — nhưng từ **22/6 đã chuyển Vertex AI (paid)**: quota không còn chặn, và build full index trên codebase nhỏ chỉ ~$1–3. **Rào thật còn lại là THỜI GIAN** — GraphRAG/RAPTOR là build nhiều tuần, không kịp trước mốc giữa 8/2026. ⇒ để sau CV (hoặc stretch Tuần 8), không phải vì quota/chi phí.
>
> **Living document:** đọc-để-biết bây giờ (đủ để *nói* trong phỏng vấn), build khi sang dự án thật sau CV.

**Quy ước (đồng bộ với các doc khác):** 🟢 build trong giai đoạn 2 · 🔵 chỉ đọc-để-biết · 🚩 AI/vibe coding hay sai · 🔍 câu tự soi · ⚠️ **[Chờ kiểm chứng web]** số liệu cần soát lại.

---

## Bản đồ: cái gì đã gấp vào roadmap, cái gì để ở đây

| Tầng | Nội dung | Ở đâu |
|---|---|---|
| **Tầng 1** (rẻ, ăn điểm CV ngay) | Reranking · CRAG-lite · Generator-Validator + Python sandbox · RAG Triad + LLM-as-judge · Constrained decoding · Kinh tế Long-Context vs RAG · Observability (LangSmith) | **Đã gấp vào** `lo-trinh-chi-tiet.md` (section cuối "Tích hợp Beyond-RAG Tầng 1") + architect map |
| **Tầng 2** (nặng, cần GPU/6 tháng) | GraphRAG · RAPTOR · Speculative RAG · vLLM/On-prem/FP8 · Multimodal Audit Swarm | **Doc này** |

---

## 1. GraphRAG — Đồ thị tri thức + Vector Search 🟢 [Hướng v2 ấn tượng nhất]

- **Vấn đề là gì?** RAG thường truy xuất các mảnh văn bản *rời rạc* theo độ tương đồng → **chết với câu hỏi cần đi qua quan hệ liên kết** ("hàm A gọi hàm nào, đổi nó ảnh hưởng module nào?") và câu vĩ mô ("kiến trúc tổng thể là gì?").
- **Giải pháp là gì?** Dựng **knowledge graph**: node = thực thể (file/hàm/class/người/tổ chức), edge = quan hệ. Hai chế độ truy vấn:
  - **Local Search:** định vị thực thể trong câu hỏi → duyệt lân cận 1–2 hop → ghép vào prompt. Độ trễ thấp, chi phí thấp.
  - **Global Search:** phân cụm đồ thị thành **cộng đồng (thuật toán Leiden)** → LLM **tóm tắt trước** từng cộng đồng → truy vấn trên các tóm tắt để trả câu tổng quan. Độ trễ + chi phí token **cực cao**.
- **Khi nào KHÔNG dùng?** Dữ liệu không có tính liên kết mạnh, hoặc câu hỏi chỉ là tra cứu sự thật đơn lẻ → RAG/hybrid thường là đủ; dựng đồ thị là over-engineer + đắt.

### 💡 Map vào AI Code Auditor (đây là điểm vàng)
Code **chính là đồ thị tự nhiên**: node = file/hàm/class, edge = gọi/import/kế thừa. GraphRAG trả lời đúng loại **câu Level-3** mà `ban-do-cong-nghe-chi-phi.md` (dòng 33) đã nêu: *"verifySignature gọi hàm nào ở credentials.js, luồng dữ liệu đi thế nào?"* → đây là **"AI Code Auditor v2"** tự nhiên nhất.

### 🔑 Insight bài nghiên cứu BỎ LỠ — và bạn nên ghi điểm
Bài mặc định dùng **LLM trích xuất entity/relation cho MỌI thứ** (đắt + cháy quota). Nhưng với **code**, phần lớn đồ thị (call graph, import graph) dựng được bằng **AST / static analysis (tree-sitter, `ast` của Python)** — **deterministic, miễn phí, chính xác hơn LLM**. Chỉ để LLM lo phần *tóm tắt ngôn ngữ tự nhiên* cho mỗi node/cộng đồng.
→ Đây đúng nguyên tắc **B4 "đừng dùng LLM khi một hàm thường giải được"**. Nói được câu này trong phỏng vấn = tư duy architect thật.

- **🚩 AI/vibe coding hay sai:** dùng LLM trích xuất cho cả call graph (trong khi AST làm chuẩn + free); bỏ qua bước **entity resolution** (cùng thực thể nhiều tên → node trùng); chạy Global Search cho câu hỏi local (đốt token vô ích).
- **🔍 Câu tự soi:** "Đồ thị này có dựng được bằng static analysis không, hay đang phí LLM?"; "Câu này là local (1 thực thể) hay global (toàn cục) — đã route đúng chế độ chưa?"
- **Tối ưu khi build:** cache Entity Linking + truy vấn Cypher phổ biến (Redis); **cắt tỉa subgraph động** (PageRank/Closeness Centrality + điểm vector, giữ top-K node); embedded graph DB (**Kuzu**) cho đơn luồng để bỏ network overhead so với cụm Neo4j. ⚠️ **[Chờ kiểm chứng web]** các con số độ trễ.
- **Stack tham khảo:** Neo4j (hoặc Kuzu nhúng) + Cypher; thư viện `graspologic`/Leiden cho community detection.

---

## 2. RAPTOR — Cây tóm tắt phân cấp đệ quy 🔵

- **Vấn đề là gì?** RAG thường chỉ lấy **mảnh ngắn, rời rạc** → mất cái nhìn toàn cục, không trả nổi câu tổng hợp cao ("chiến lược công nghệ thay đổi thế nào qua 5 năm?").
- **Giải pháp là gì?** Gom cụm chunk lá (**GMM + giảm chiều UMAP**, cho phép 1 chunk thuộc nhiều cụm) → LLM **tóm tắt trừu tượng** mỗi cụm → nhúng tóm tắt → **đệ quy** gom-tóm tiếp cho tới đỉnh cây. Truy xuất có thể chạm **bất kỳ tầng nào** → vừa chi tiết vừa tổng quan.
- **Khi nào KHÔNG dùng?** Khi không cần câu hỏi tổng hợp toàn tài liệu, hoặc index thay đổi liên tục — **chi phí xây chỉ mục "cực kỳ cao"** (chính bảng trong bài ghi vậy), build lại mỗi lần đổi data là phá sản về cost.
- **🚩 hay sai:** build RAPTOR cho codebase đổi mỗi ngày (index hết hạn liên tục); dùng RAPTOR khi RAG phẳng đã đủ.
- **Map code-auditor:** câu "tóm tắt kiến trúc toàn repo / module này làm gì ở tầng cao". Pair tốt với GraphRAG (graph cho quan hệ, RAPTOR cho tóm tắt phân cấp).

---

## 3. Speculative RAG — Drafter nhỏ + Verifier lớn 🔵 [Chỉ cần biết để nói]

- **Vấn đề là gì?** Naive RAG bắt **model lớn đọc hết** mọi tài liệu thô → chậm khi số tài liệu tăng, lại dính **position bias** (thiên vị thông tin đầu/cuối).
- **Giải pháp là gì?** Lấy ý từ *speculative decoding*: nhiều **Drafter** (model nhỏ, nhanh) đọc các tập con tài liệu **song song**, mỗi cái sinh bản nháp + lập luận; một **Verifier** (model lớn) chạy **một lần** chọn/ghép bản nháp tốt nhất. ⚠️ **[Chờ kiểm chứng web]** "nhanh +50%".
- **Khi nào KHÔNG dùng?** Hệ nhỏ, ít tài liệu → overhead điều phối 2 tầng model không bõ. Đây là tối ưu tốc độ cho quy mô lớn.
- **Ghi chú:** niche; trong 3 dự án portfolio bên dưới nó hợp Dự án 1 (pháp lý). Với code-auditor thì chưa cần.

---

## 4. Kiến trúc lai: Long-Context LLM + RAG 🔵

> Phần *kiến thức* (vì sao RAG còn cần, Self-Route/Pre-Route) **đã gấp vào Tầng 1** (ngân hàng phỏng vấn + NOTES). Ở đây giữ phần *kiến trúc build*.

- **Phễu 3 tầng tối ưu:** (1) **Lọc thô** — hybrid retrieval (BM25 + vector) lấy top 50–100; (2) **Rerank** — cross-encoder (Cohere Rerank / BGE-Reranker) thu về top 5–10; (3) **Long-Context Generation** — đẩy top đã rerank vào model context lớn để tổng hợp. Tầng này khử nhiễu + né "lost in the middle".
- **Định tuyến động:** **Self-Route** (thử RAG rẻ trước, model báo "unanswerable" mới nạp long-context đắt) · **Pre-Route** (model phân loại nhỏ, vd Qwen3-1.7B, quyết trước fact-retrieval → RAG, suy luận phức tạp → long-context). ⚠️ **[Chờ kiểm chứng web]** "cắt 80% chi phí".
- **Vì sao RAG không chết dù context 1M token** (math để nhớ): prefill self-attention ~O(n²) → TTFT hàng chục giây; **KV-cache ngốn VRAM** phi mã theo số user đồng thời; lost-in-the-middle; và RAG là **màng lọc Row-Level Security** loại data trái quyền *trước khi* vào prompt. ⚠️ **[Chờ kiểm chứng web]** các mốc GB KV-cache trong bài.

---

## 5. On-premise / vLLM / Quantization 🔵 [Đọc-để-biết, KHÔNG build — không có H100]

> Đã có ở `ban-do-cong-nghe-chi-phi.md` mục III Nhóm 2. Đây là phần đào sâu thêm từ bài.

- **Vì sao on-prem:** doanh nghiệp lớn tuyệt đối không gửi mã nguồn ra API công cộng → phải tự host trong hạ tầng cô lập.
- **Nén model:** **FP8 (W8A8)** giảm ~50% VRAM trọng số, tăng tốc Tensor Core trên Hopper (H100/H200), gần như không mất accuracy (thư viện **LLM Compressor**). **KV-cache quant** (INT8/FP8) tiết kiệm tới ~60% VRAM tĩnh → gấp đôi user đồng thời. ⚠️ **[Chờ kiểm chứng web]** % cụ thể.
- **Phục vụ bằng vLLM:** PagedAttention; `--tensor-parallel-size` (chia model nhiều GPU); `--enable-prefix-caching` (bỏ prefill cho phần prompt lặp → phản hồi <100ms); `--chunked-prefill-size` (chống Head-of-Line Blocking giữa request dài và ngắn).
- **🚩 hay sai:** kéo vLLM/H100 vào project học (over-engineer cực độ); quên rằng đây là kiến thức để **đọc JD enterprise**, không phải để fresher build ngay.

---

## 6. Multi-Agent nâng cao & Audit Swarm 🔵

> Multi-agent cơ bản (Router/Worker/Reviewer) **đã ở roadmap Tuần 5** + architect C3. Đây là phần *doanh nghiệp* của bài.

- **3 mô hình điều phối:** **Routing** (router → 1 agent chuyên) · **Orchestrator-Workers / Supervisor** (planner phân rã DAG → worker chuyên: SQL Agent, Retrieval Agent → tổng hợp; *tối ưu nhất cho nghiệp vụ kiểm soát cao*) · **Choreography** (phi tập trung qua message queue; mở rộng cao nhưng **cực khó debug** → tránh ở giai đoạn này).
- **State & Memory:** State store dạng đồ thị (LangGraph → Postgres/Redis), **append-only log** cho time-travel/rollback; **short-term** = scratchpad phiên (nén/tóm tắt khi gần tràn context); **long-term** = episodic memory — lưu *quỹ đạo thực thi thành công* thành vector (Qdrant), truy xuất lại khi gặp tác vụ tương tự.
- **🚩 hay sai (đỉnh tháp):** đẻ 5 agent cho việc 2 agent làm xong; Choreography cho hệ nhỏ; quên agent reviewer.

---

## 7. Ba dự án portfolio (re-scoped cho thực tế của bạn)

> Giữ ý tưởng của bài, nhưng gắn nhãn độ thực tế. **Ưu tiên: nâng cấp chính AI Code Auditor**, đừng đẻ 3 repo mới rời rạc.

| Dự án (theo bài) | Độ khó | Khuyến nghị cho bạn |
|---|---|---|
| **1. Thẩm định luật (Speculative + CRAG)** | Trung bình | Speculative RAG niche; **lấy phần CRAG** (đã ở Tầng 1) là đủ ăn điểm. Để nguyên dự án này = optional. |
| **2. Chuỗi cung ứng (GraphRAG + RAPTOR)** | Khó | **Chuyển ý tưởng GraphRAG sang code** = "AI Code Auditor v2" (call/import graph bằng AST). Hợp bạn hơn nhiều domain chuỗi cung ứng. |
| **3. Agentic Auditing Swarm (đa Agent + SQL + sandbox + vLLM on-prem)** | Rất khó | **Capstone xa nhất.** Phần khả thi không-cần-GPU: Generator-Validator + Python sandbox (đã ở Tầng 1). Phần vLLM/on-prem để khi có hạ tầng. |

**Lộ trình sau CV (anchor theo dự án, KHÔNG theo lịch):** v2 = thêm GraphRAG (AST + Neo4j/Kuzu) vào AI Code Auditor → v3 = thêm RAPTOR tóm tắt kiến trúc → v4 = audit swarm + self-host khi có ngân sách/GPU. Mỗi bước chỉ lên cấp khi cấp dưới không còn đủ (nguyên tắc L1→L5).

---

## ⚠️ Rà soát phản biện bài nghiên cứu (giữ tinh thần "review, không tin mù")

1. **Tên model đã cũ:** bài ghi "Claude 3.5 Sonnet", "Gemini 2.5 Pro". Bảng của bạn (`ban-do-cong-nghe-chi-phi.md` II) đã cập nhật **Claude Sonnet 4.6 / Gemini 3.5 Flash / GPT-5.4** → chuẩn hóa về bảng của mình khi trích.
2. **Số "ấn tượng" cần `[Chờ kiểm chứng web]`:** Speculative +50%, Pre-Route −80% chi phí, các mốc GB KV-cache, % FP8/KV-quant — là minh họa, đừng đưa vào CV/báo cáo khi chưa soát.
3. **Mâu thuẫn với YAGNI của bạn:** bài đẩy GraphRAG+RAPTOR+multi-agent cùng lúc; architect C3 của bạn lại *cắt agent thứ 3 đầu tiên khi trễ*. Luôn hỏi câu C1.6: "bỏ bớt component nào vẫn chạy?".
4. **Thời gian là rào thật (quota đã gỡ):** đã chuyển Vertex (paid) nên free-tier 20 req/ngày không còn chặn; build index codebase nhỏ chỉ ~$1–3. Cái thiếu là **thời gian nhiều tuần** → khởi động Tầng 2 sau CV. Vẫn đặt **Budget Alert** vì Vertex tính tiền theo token.

---

## 🔗 Liên kết
- Tầng 1 (đã gấp vào lộ trình): [lo-trinh-chi-tiet.md](lo-trinh-chi-tiet.md) — section cuối "Tích hợp Beyond-RAG Tầng 1".
- Phán đoán "khi nào dùng gì": [ban-do-phan-doan-architect.md](ban-do-phan-doan-architect.md) — thang L1→L5, A4 (rerank/CRAG), B1 (RAG Triad).
- Chi phí + on-prem: [ban-do-cong-nghe-chi-phi.md](ban-do-cong-nghe-chi-phi.md) — mục II, III.
- Benchmark tra định kỳ: VN-MTEB · SEA-HELM · vmlu.ai.
