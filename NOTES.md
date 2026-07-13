# SỔ TAY HỌC TẬP & HỆ THỐNG KIẾN THỨC (NOTES.md)

Chào mừng bạn đến với bộ não thứ hai của mình! File này được thiết kế để lưu giữ mọi khái niệm cốt lõi bạn học được trong suốt lộ trình 7 tuần xây dựng **AI Code Auditor**.

## HƯỚNG DẪN GHI CHÉP (Quy tắc 3 câu)
Mỗi khi gặp một khái niệm mới, hãy ép bản thân giải thích ngắn gọn bằng tiếng Việt theo cấu trúc sau:
1. **Vấn đề là gì?** (Nếu không có khái niệm/công nghệ này, hệ thống sẽ gặp lỗi, chạy chậm hoặc không hoạt động thế nào?)
2. **Giải pháp là gì?** (Nó giải quyết vấn đề đó bằng cơ chế hay thuật toán nào?)
3. **Khi nào KHÔNG dùng?** (Nhược điểm của nó là gì? Khi nào thì nên dùng công nghệ khác?)

---

## TUẦN 1: NỀN TẢNG RAG CƠ BẢN (BASIC RAG)

### Ngày 1: Token, Context Window & Tokenization
*   **Vấn đề là gì?**
    *   Máy không hiểu chữ thô — cần biến text thành số. Và mỗi lần gọi LLM nó chỉ "nhìn" được một lượng giới hạn = **context window** (Gemini 3.5 Flash ~1.048.576 token).
    *   Ví dụ của tôi: như một tài liệu 50 trang nhưng người đọc chỉ đọc nổi 10 trang; cố nhồi hết thì sẽ **quên dữ kiện ở giữa** ("lost in the middle"). Ngoài ra mỗi token đều **tốn tiền** (tính cả input lẫn output).
*   **Giải pháp là gì?**
    *   **Token hóa:** chia text thành các mảnh nhỏ (sub-word), mỗi mảnh là 1 số nguyên (token id). Nhờ vậy đo được độ dài text bằng token → biết một file có "nhét vừa" context window không và tốn bao nhiêu.
    *   Thực hành: `tiktoken` → `enc.encode(text)` trả về **list các token id**; `len(...)` của list đó = **số token** (khác số ký tự). Đo thật: rules.js 46.931 ký tự → 13.203 token, chỉ chiếm 1.26% context window.
*   **Khi nào KHÔNG dùng / Lưu ý quan trọng:**
    *   Số token đếm bằng `tiktoken` chỉ là **ước lượng để học** — Gemini dùng tokenizer riêng nên số tính tiền sẽ khác.
    *   **Tiếng Việt tốn ~2x token** so với tiếng Anh (đo thật: 19 vs 10). Lý do **KHÔNG phải dấu câu**, mà vì tokenizer học chủ yếu trên tiếng Anh → từ tiếng Anh gói gọn 1 token, tiếng Việt bị cắt vụn (âm tiết + dấu thanh). ⇒ làm sản phẩm cho người Việt tốn gấp đôi chi phí LLM.
    *   Với tài liệu **nhỏ + ít thay đổi**, nhồi thẳng (stuffing) là đủ, chưa cần tối ưu token hay RAG.

> 📌 **Ghi chú công cụ hôm nay — SDK Gemini cũ vs mới:**
> SDK cũ `google.generativeai` (dùng `genai.configure()` cấu hình **toàn cục**) đã bị **khai tử** → code dùng nó sẽ lỗi. SDK mới `google-genai` dùng **client tường minh**: `client = genai.Client(api_key=...)` rồi `client.models.generate_content(...)`. "Tường minh" = mọi cấu hình hiện rõ trong câu lệnh, không giấu ở state toàn cục → dễ test, chạy nhiều key/cấu hình song song được. Bẫy: hai SDK cùng import tên `genai` nhưng khác nguồn (`import google.generativeai` vs `from google import genai`).

### Ngày 2: Vector Embeddings & Mô hình biểu diễn ngữ nghĩa
*   **Vấn đề là gì?**
    *   Tìm kiếm bằng **từ khóa** (so khớp ký tự / substring) **chết** khi người hỏi dùng từ khác nhưng cùng nghĩa: code ghi `verify signature`, người dùng hỏi *"kiểm tra chữ ký"* → so khớp chữ ra **0 kết quả**, dù hai câu cùng một ý.
    *   Cần một cách "tìm theo nghĩa" thay vì "tìm theo chữ".
*   **Giải pháp là gì?**
    *   **Embedding**: dùng model (vd `all-MiniLM-L6-v2`) biến mỗi câu thành một **vector số nhiều chiều** (ở đây 384 chiều), sao cho **hai câu gần nghĩa thì hai vector gần nhau** trong không gian. Encode 6 câu → ma trận `(6, 384)`: 6 hàng = 6 câu, mỗi câu định vị bằng 384 "thước đo" nghĩa.
    "Embedding biến text thành vector số sao cho gần nghĩa thì gần nhau. Vấn đề nó giải: keyword search chết khi cùng ý mà khác chữ — hỏi 'cách thoát tài khoản' nhưng tài liệu ghi 'đăng xuất'. Giải pháp: so theo vector ngữ nghĩa thay vì ký tự. Đánh đổi: embedding mù khớp chính xác — em đo #1234 vs #5678 vẫn ra cosine 0.98, model không phân biệt được số. Nên mã đơn/SĐT em để DB query, tìm theo ý mới dùng embedding, và kết hợp cả hai gọi là hybrid search."
    *   Nghĩa được **rải khắp 384 chiều**, không nằm gọn ở vài số đầu → in 5/384 số ra nhìn mắt thường KHÔNG thấy cặp nào gần (như đọc 5/384 trang sách rồi đoán nội dung). Vì vậy cần một phép đo gộp cả 384 chiều thành 1 con số "độ gần" = **cosine similarity** (học ở Ngày 3 — đây là *cây thước đo*, không phải bản thân giải pháp embedding).
*   **Khi nào KHÔNG dùng?**
    *   **Cần khớp chính xác** (mã đơn, SĐT, tên hàm): embedding bắt *ngữ nghĩa* chứ không phân biệt *con số*. Đo thật: `#1234 vs #5678` cosine = **0.9835** (gần như giống hệt) → tra mã đơn phải dùng **keyword/DB query**, không dùng embedding. Hệ thật kết hợp cả hai = **hybrid search**.
    *   **Model yếu đa ngôn ngữ**: `#1234` tiếng Việt vs tiếng Anh dù cùng nghĩa chỉ đạt cosine = **0.2669** — vì MiniLM train chủ yếu trên tiếng Anh, yếu cross-lingual + tiếng Việt. Đây là *giới hạn của model*, không phải lỗi dữ liệu → bài toán tiếng Việt nên nâng cấp sang model mạnh hơn (vd Qwen3-Embedding) ở tuần 2. Đây cũng là **số liệu vàng cho CV**: "cải thiện precision@3 khi đổi MiniLM → Qwen3-Embedding".
    *   Tài liệu **nhỏ + ít thay đổi** (vài trang chính sách nội bộ): nhồi thẳng vào prompt là đủ, chưa cần embedding/RAG cho phức tạp.

### Ngày 3: Cosine Similarity — Đo "độ gần nghĩa" giữa hai vector
*   **Vấn đề là gì?**
    *   Sau Ngày 2, mỗi câu đã thành vector 384 chiều, nhưng "hai vector gần nhau" là một con số *chưa đo được*. Cần một phép gộp cả 384 chiều thành **một số duy nhất** thể hiện độ giống.
*   **Giải pháp là gì?**
    *   **Cosine similarity** đo **góc** giữa hai vector: `cos = (A·B) / (‖A‖×‖B‖)`. Cùng hướng → `cos(0°)=1` (đồng nghĩa); vuông góc → `cos(90°)=0` (không liên quan); ngược hướng → `cos(180°)=−1` (đối nghĩa).
    *   **Tử số `A·B`** trộn *cả hướng lẫn độ dài*; **mẫu số `‖A‖×‖B‖`** là *độ dài thuần*. Chia để **triệt tiêu độ dài**, chỉ giữ lại hướng (= nghĩa). Tự viết tay trong `mini_rag.py`, chốt chặn `norm==0 → return 0.0` (vector toàn số 0 mới có norm=0, tránh chia 0).
    *   Kiểm chứng đúng: **đường chéo ma trận = 1.000** (mỗi câu so với chính nó) — đây cũng là mẹo test nhanh hàm cosine.
*   **Khi nào KHÔNG dùng / Lưu ý quan trọng:**
    *   **Cosine vs Euclidean:** Euclidean đo khoảng cách thẳng, bị ảnh hưởng bởi magnitude; cosine bỏ qua magnitude, chỉ đo hướng → công bằng với câu dài/ngắn cùng nghĩa. **NHƯNG** đo thật: `all-MiniLM-L6-v2` xuất vector **đã normalize về độ dài 1** (kiểm chứng `norm(emb)=1.0000`). Khi đã normalize, hai phép **tương đương về thứ hạng**: `Euclidean² = 2×(1−cosine)` (đo thật: √(2×(1−0.7154))=0.7545 ✅). Vẫn chọn cosine vì **bị chặn trong [−1,1]**, dễ đặt ngưỡng. → Câu này tách người hiểu sâu khỏi người học vẹt.
    *   **Brute-force O(n):** tự so query với *từng* chunk. OK với vài trăm chunk; ở quy mô triệu vector phải dùng ANN index (HNSW) trong vector DB thật (Chroma, pgvector) — đánh đổi tốc độ vs chính xác tuyệt đối.
    *   **🔴 Giới hạn model (KHÔNG phải lỗi code):** đo ma trận thấy MiniLM **thất bại song ngữ Việt–Anh**: cặp đồng nghĩa "kiểm tra chữ ký webhook" vs "verify signature" = **−0.026**, còn "chữ ký webhook" vs "nấu phở" (đều tiếng Việt) lại = **0.403**! Model gom cụm theo **ngôn ngữ/bề mặt**, không theo **nghĩa** → nối tiếp phát hiện Ngày 2 (#1234 VI-EN = 0.2669). **💎 Số liệu vàng CV:** đề xuất nâng cấp Qwen3-Embedding ở Tuần 2 và đo lại precision@3.

### Ngày 4: Chunking — Cắt code/docs mà không phá ngữ cảnh
*   **Vấn đề là gì?**
    *   Embed nguyên cả file thành 1 vector → retrieval lúc nào cũng trả về cả file = không khác gì stuffing, tốn token + lẫn rác. Ngược lại cắt quá vụn (giữa thân một hàm) → mảnh mất ngữ cảnh, model đọc không hiểu. Cần cắt sao cho mỗi mảnh là **một đơn vị tự đủ nghĩa**.
*   **Giải pháp là gì?**
    *   Cắt theo **ranh giới có nghĩa** (semantic boundary), không cắt mù theo số ký tự: `.md` cắt theo **heading**, `.js` cắt theo **ranh giới hàm/route** (`function`, `router.get(`, `module.exports`...), mỗi chunk dính kèm heading/tên hàm để biết "mình mô tả cái gì".
    *   **3 bẫy regex đã học (nhánh `.md`):** (1) `(?m)` = multiline → `^`/`$` khớp đầu/cuối **mỗi dòng**, không bật thì `^#` chỉ bắt heading ở dòng đầu cả file. (2) `#{1,6}` = "1–6 ký tự `#` liên tiếp" = heading **bất kỳ cấp nào**, KHÔNG phải "theo thứ tự tăng dần". (3) **Dấu ngoặc `( )` trong `re.split` = capturing group → GIỮ LẠI dòng heading** trong list kết quả; bỏ ngoặc thì heading bị vứt mất, chunk còn mỗi body trơ trụi.
    *   **Fallback bắt buộc:** chunk nào dài hơn `FALLBACK_CHUNK_SIZE*2` (=1600) thì cắt cứng mỗi 800 ký tự, để không bao giờ lọt 1 chunk khổng lồ làm "nhạt nhòa" vector embedding.
*   **Khi nào KHÔNG dùng / Đánh đổi (đo thật trên DESIGN.md):**
    *   Đo thật: DESIGN.md → **13 chunks**. Chunk 0–8 sạch (mỗi chunk 1 section, độ dài lẻ 739/625/784...). Nhưng section `## Admin Auth/RBAC/Audit Proposal` quá dài (~3500 ký tự) → fallback chém thành chunk 9–12 **đúng 800 chars mỗi cái** (dấu vân tay của fallback), cắt **giữa từ**: `rota|tion`, `rout|es`, `fut|ure`. → fallback cắt theo *chỉ số ký tự* nên **phá ngữ cảnh + mất heading**.
    *   **Đánh đổi:** fallback đảm bảo *không có chunk khổng lồ*, nhưng trả giá bằng *mất nghĩa khi cắt giữa câu/từ* (KHÔNG phải "tốn token" — đó là hiểu nhầm).
    *   **Cách cải tiến (→ bài tập `compare_chunking.py` cuối tuần):** (1) cắt ở **ranh giới tự nhiên** gần mốc 800 nhất (`\n\n` → `\n` → dấu câu) = recursive character splitting (LangChain); (2) **overlap ~100 ký tự** giữa 2 chunk liền kề để câu bị cắt đôi vẫn trọn vẹn ở ít nhất 1 chunk.
    *   Tài liệu **nhỏ + ít thay đổi** → bỏ qua chunking, nhồi thẳng là đủ (nối tiếp kết luận Ngày 1–2).

### Ngày 5: Context Packing & Prompt Grounding (rào chắn chống bịa)
*   **Vấn đề là gì?**
    *   LLM được train để **luôn trả lời cho trôi chảy**, kể cả khi không biết. Đưa câu hỏi + vài chunk rồi bảo "trả lời đi" → model sẽ **bịa** ra hàm/logic không có trong codebase (vd mô tả Stripe chung chung từ kiến thức train sẵn rồi gán như thể đó là code của dự án) = **hallucination**.
    *   Nguy hiểm gấp đôi: `retrieve_top_k` **luôn trả về đủ k chunk** kể cả câu hỏi lạc đề (moi 3 chunk "đỡ tệ nhất"). Không có rào chắn, model thấy "có context kèm file path" → gán đại câu trả lời vào chunk vô-quan-hệ + **citation trông xịn** = bịa CÓ dẫn nguồn, còn khó phát hiện hơn bịa trơn.
*   **Giải pháp là gì?**
    *   **Prompt Grounding** = "buộc chân" câu trả lời vào context bằng lệnh tường minh trong prompt: (1) *chỉ dùng thông tin trong context*; (2) *không có thì phải nói "không tìm thấy", tuyệt đối không đoán*; (3) *trích dẫn rõ file + chunk_id*. Dòng (2) là **quan trọng nhất** — nó ra lệnh model **tự xét chunk có liên quan không**, đừng tin "cứ có context là phải dùng".
    *   **Mẹo priming:** kết prompt bằng `TRẢ LỜI:` rồi bỏ trống → LLM là máy đoán-chữ-tiếp-theo, bị đặt đúng "ghế" để sinh ra câu trả lời thay vì lặp lại câu hỏi.
    *   **Context có nhãn:** mỗi chunk dán `file path | chunk_id | score` → **truy vết** (debug "model dùng đoạn nào" + hiển thị citation cho user tin tưởng). `f"""..."""` = f-string nhiều dòng, `{question}`/`{context_text}` bị thay bằng giá trị thật trước khi gửi Gemini (khác docstring ở chỗ nó được **gán vào biến** = dữ liệu thật, không phải chú thích).
*   **Khi nào KHÔNG dùng / Giới hạn (đo thật trên chatbot-fanpage — 3308 chunks/115 files):**
    *   Grounding chỉ là **rào chắn mềm** — **không thay được retrieval tốt**. Chạy thật: hỏi `verifySignature hoạt động ra sao?` → model **từ chối** dù `webhook.js` CÓ trong index. Rào chắn **vô tội** (gặp context rác thì từ chối thay vì bịa ✅); **thủ phạm là retrieval**. ⇒ câu lý thuyết "retrieval lấy rác thì model ngoan cũng vô dụng" thành sự thật.
    *   **💎 Phát hiện vàng 1 — embedding yếu cross-lingual (nối tiếp Ngày 2–3):** câu hỏi **tiếng Việt** cho điểm CAO HƠN (0.613) nhưng tới các doc **tiếng Việt SAI** (`HUONG_DAN.md`...); chỉ khi hỏi `verifySignature HMAC` (**tiếng Anh**) thì `webhook.js` mới lọt top-3 (0.434). ⇒ MiniLM chấm theo **ngôn ngữ/bề mặt**, không theo **nghĩa**. Điểm tuyệt đối toàn ~0.4–0.6 (thấp). **Số liệu định lượng để nâng cấp MiniLM → Qwen3/BGE-M3 ở Tuần 2 + đo lại precision@3.**
    *   **💎 Phát hiện vàng 2 — chunking xé hàm lồng phá luôn retrieval (nối tiếp Ngày 4):** `verifySignature` là **hàm con thụt lề** trong `createWebhook`. Pattern `.js` neo `(?m)^` (cột 0) → **không bắt** dòng thụt lề → cả `createWebhook` gom thành 1 chunk khổng lồ → **fallback chém cứng 800 ký tự**, xé thân `createHmac/timingSafeEqual` khỏi header `function verifySignature` → embedding nhạt nhòa → **không bao giờ nổi top-K**. ⇒ bug chunking Ngày 4 không chỉ "phá ngữ cảnh khi đọc" mà **phá cả retrieval**. Hướng sửa: regex bắt cả khai báo thụt lề / overlap ~100 ký tự / dùng splitter thư viện.
    *   **2 tầng chunking tách bạch:** Tầng 1 (regex ngữ nghĩa) chỉ xét **khớp pattern**, KHÔNG xét độ dài — dòng thụt lề không bao giờ là ranh giới. Tầng 2 (fallback) mới xét **độ dài** chunk đã chia. Đừng trộn hai tầng.

### Ngày 6: Stress-Test Hallucination & Baseline (đo để Tuần 2 có cái mà so)
*   **Vấn đề là gì?**
    *   Ngày 5 chỉ thấy pipeline chạy *được* trên vài câu lẻ = "demo may mắn", chưa phải bằng chứng. Không có bộ test cố định + con số, thì Tuần 2 nâng MiniLM→Qwen3 mình **không biết tốt lên thật hay chỉ cảm giác**.
    *   Máy tự gắn được nhãn `[TỪ CHỐI]` (vì câu từ chối là chuỗi cố định do CHÍNH MÌNH ra lệnh trong prompt → so khớp ký tự). Nhưng **"đúng/bịa" thì máy KHÔNG tự chấm được**: (1) script không chứa ground-truth máy-so-được; (2) câu trả lời là văn xuôi tự do, "đúng" phải so theo *nghĩa* không phải *chữ* → buộc có người (hoặc LLM-judge) phán. Đây là cầu nối sang bài toán **eval / precision@k / LLM-as-judge** ở Tuần 2.
*   **Giải pháp là gì?**
    *   Soạn **bộ câu hỏi cố định có đáp án biết trước**, cố tình trộn câu *có trong code* (đo recall) + câu *không có* (đo rào chắn từ chối), chạy 1 lượt, ghi 3 con số **đúng/bịa/từ chối** = **baseline** (vạch xuất phát).
    *   **Đo thật (chatbot-fanpage, 10 mẫu — Q5 re-run trên Vertex 23/6):** Bịa = **0/10** (rào chắn vững, không citation giả); Từ chối đúng off-topic = **4/4** (Q8 còn *sửa* tiền-giả-định sai "MongoDB?" → "là PostgreSQL"); Recall in-scope = **2/6 (~33%)**. **Kết luận vàng: generation đã hoàn hảo, nút thắt 100% ở retrieval** — 4 câu trượt (verifySignature, lead parser, RBAC, test framework) đều CÓ trong code nhưng chunk đúng không lọt top-3, khớp y 2 phát hiện vàng Ngày 5. ⚠️ **Q5 lật một bài học:** ghi chú cũ "Q5 retrieval đã trúng" là **giả định SAI** — grep ra `HUONG_DAN.md` không hề chứa vai trò (đáp án ở test/code) → verify nội dung, đừng đoán theo tên file.
    *   Phát hiện thêm: "**chunk nam châm**" `admin/views.js#188` lọt top-3 ở 4 câu khác hẳn nhau → nghi đoạn fallback 800 ký tự mờ nghĩa, hút mọi truy vấn = nhiễu cần xử lý Tuần 2.
*   **Khi nào KHÔNG dùng / Lưu ý vận hành (học từ chính cú crash hôm nay):**
    *   Baseline chỉ đáng đo khi **sắp có thay đổi lớn cần chứng minh** (đúng lúc mình sắp sang Tuần 2). Pipeline còn đổi mỗi ngày thì đo xong số hết hạn ngay.
    *   **🔑 503 vs 429 (tự tay gặp cả hai):** `503 UNAVAILABLE` = server Google quá tải, lỗi CỦA HỌ, transient → **retry backoff** là đúng. `429 RESOURCE_EXHAUSTED` = hết **quota free CỦA MÌNH** (`gemini-3.5-flash` free chỉ **20 req/ngày**), retry ngắn hạn vô ích → đổi model/đợi reset.
    *   **💡 Retry mù đốt quota:** retry-trên-503 ở mẻ 10 câu cộng dồn ~20 request → cháy đúng trần 20/ngày. ⇒ Production phải giới hạn CẢ số lần retry LẪN tổng request/phút (rate limiter), không chỉ bắt lỗi. Đổi `gemini-3.5-flash` → `gemini-2.5-flash-lite` = **bucket quota riêng + rẻ ~15x** ($0.10/$0.40 vs $1.50/$9.00) → đã đổi trong `call_gemini`.
    *   **Robustness transcript:** ghi file SAU MỖI câu (không phải cuối vòng) → crash giữa chừng vẫn giữ tiến độ, khỏi chạy lại tốn quota.

### Ngày 7: Chuyển backend LLM sang Vertex + Bài học vận hành & kiểm chứng
*   **A. Backend AI Studio vs Vertex (cùng một SDK):**
    *   *Vấn đề:* free tier AI Studio chỉ **20 req/ngày** (đã cháy Ngày 6) → chặn học/test/agent loop.
    *   *Giải pháp:* SDK `google-genai` che cả 2 backend sau **cùng API** — chỉ phần `Client()` đổi. `call_gemini` giờ **dual-mode**: env `GOOGLE_GENAI_USE_VERTEXAI=True` (+ `GOOGLE_CLOUD_PROJECT` + `GOOGLE_CLOUD_LOCATION`, auth bằng **ADC** `gcloud auth application-default login`) → Vertex; không thì fallback `GEMINI_API_KEY`. `generate_content` **giữ nguyên** → đây là cái lợi "explicit client" của Ngày 1.
    *   *Khi nào KHÔNG:* prototype 1 lần / tài liệu nhỏ → AI Studio free là đủ, đừng dựng Vertex cho nặng.
*   **B. Bẫy env var (mất 3 lần thử mới ra):**
    *   *Vấn đề:* set env xong chạy vẫn báo "Chưa set backend LLM".
    *   *Giải pháp/Phân biệt:* `$env:FOO` = **session hiện tại**, mất khi đóng · `setx FOO` = **vĩnh viễn nhưng chỉ terminal MỞ MỚI**, không áp cho session đang mở · **VS Code chụp env lúc khởi động** → `setx` + mở tab mới vẫn vô dụng cho tới khi **restart cả VS Code**. Cách chắc: set `$env:` ngay trong session, hoặc `setx` rồi restart VS Code.
    *   *Khi nào KHÔNG:* chỉ là vận hành — nhưng đây là loại bug "môi trường" tốn thời gian nhất, nhớ để khỏi mất buổi.
*   **C. Phương pháp: cô lập biến số + verify, đừng đoán:**
    *   *Vấn đề:* lỗi/đánh giá dễ đổ nhầm nguyên nhân (tưởng lỗi code/máy mình, hoặc tin ghi chú cũ).
    *   *Giải pháp:* (1) **Cô lập** — test ở Cloud Shell (đã pre-auth) trước → biết lỗi ở GCP hay máy local; (2) **Verify ground-truth** — Q5 "không tìm thấy" → grep repo mới lòi ra `HUONG_DAN.md` KHÔNG chứa vai trò (đáp án ở `tests/admin-routes.test.js` + `core/admin/`) → ghi chú "retrieval đã trúng" là **giả định SAI**.
    *   *Khi nào KHÔNG:* với fresher, gần như không có ngoại lệ — luôn verify bằng số/grep thay vì đoán. (= câu chuyện phỏng vấn "tôi tự bắt lỗi đánh giá của chính mình".)

---

## TUẦN 2: VECTOR DB THẬT + ĐÁNH GIÁ ĐỊNH LƯỢNG

### Ngày 8: Migrate list Python → ChromaDB + so "apples-to-apples"
*   **Vấn đề là gì?**
    *   Kho Tuần 1 = list Python + ma trận numpy nằm trong **RAM** → tắt script là mất sạch, lần sau phải embed lại 3308 chunk. Và `retrieve_top_k` tự viết là **brute-force O(n)** — quét *từng* chunk mỗi câu hỏi, vài nghìn thì ổn, triệu vector thì sập.
*   **Giải pháp là gì?**
    *   **ChromaDB** lo 3 việc list không làm được: (a) **persistence** (lưu đĩa, khỏi embed lại); (b) **ANN index — HNSW** thay O(n) bằng **~O(log n)** (đồ thị "nhảy tắt" tới vùng vector gần); (c) lưu metadata + query bằng 1 lệnh.
    *   **🔑 So công bằng (apples-to-apples) — né "bẫy 1":** để `query_texts=[...]` thì Chroma **tự embed bằng MiniLM-qua-ONNX** (khác runtime với `sentence-transformers`) → đang so **2 model khác nhau**, không phải kho-cũ vs kho-mới. Cách đúng: **tự embed rồi bơm `embeddings=` (lúc add) + `query_embeddings=` (lúc query)** → cả 2 bên cùng một bộ não. (= cô lập biến số, Ngày 7.) Tách 3 thứ na ná: **embedding** (vector, ở `embeddings=`) ≠ **cosine** (cách đo, đặt 1 lần `hnsw:space="cosine"` lúc tạo collection) ≠ **`embeddings`/`query_embeddings`** (tên cái hộp).
    *   **Đo thật (chatbot-fanpage, 3308 chunks, 3 câu):** top-3 **KHỚP TUYỆT ĐỐI** cả chunk lẫn thứ tự ⇒ bằng chứng chạy thật cho **L2 ↔ cosine xếp hạng y hệt** (Ngày 3, vì MiniLM normalize sẵn). `hnsw:space=cosine` trả về **cosine _distance_ = 1 − similarity**, đúng từng số (sim 0.434 → dist 0.566 — *dự đoán trước, máy in đúng*).
*   **Khi nào KHÔNG dùng / Lưu ý:**
    *   **Đánh đổi HNSW = tốc độ vs chính xác tuyệt đối:** ANN là **gần đúng**, *có thể bỏ sót* true nearest neighbor; brute-force tay luôn đúng tuyệt đối nhưng chậm. Quy mô nhỏ (vài nghìn chunk, 1 user) → list + cosine tay vẫn nhanh + dễ debug hơn, cài Chroma là để **học nghề + đo so sánh**, không phải vì list đang chậm.
    *   **🧠 HNSW 1 dòng:** = **Skip List trên graph** — *ngẫu nhiên* gán tầng lúc **build** (xác suất giảm theo hàm mũ → tầng cao càng thưa), *cố định* entry-point + greedy "nhảy cóc" tầng trên rồi "bò" tầng đáy lúc **search** → **O(log N)**. Giá phải trả: recall **95–99%** (KHÔNG tuyệt đối — đây là con số của "approximate") + **tốn RAM** (lưu cả đồ thị + edges, nặng hơn IVF-PQ). Data nhỏ (3308 chunk) nằm gọn RAM nên hôm nay chưa trượt phát nào ⇒ top-3 khớp tuyệt đối; tới *triệu* vector mới thấy 95–99% cắn vào.
    *   **💎 Migrate KHÔNG sửa recall:** câu RBAC vẫn trúng `HUONG_DAN.md#30` (chunk SAI, đã grep-bóc Ngày 7). Đổi **kho chứa** (tầng dưới) ≠ đổi **bộ não embed** (tầng model). Sửa precision là việc **Ngày 10** (MiniLM → Qwen3/BGE-M3). Đừng kỳ vọng đổi DB mà số nhảy — 2 tầng khác nhau.

### Ngày 9: Golden Set + Precision@3 (biến "cảm giác" thành 1 con số)
*   **Vấn đề là gì?**
    *   Baseline Ngày 6 là câu hỏi tùy hứng = "demo may mắn". Ngày 10 đổi MiniLM→Qwen3 **không chứng minh được** tốt lên thật hay tự huyễn hoặc, vì không có bài thi cố định + đáp án biết trước.
    *   `precision@3 = 0/5` mới nói "đáp án không lọt top-3" — nhưng CHƯA phân biệt 2 thảm họa khác hẳn: (A) đáp án ở hạng 4–15 (sát nút, model nhỉnh là cứu) vs (B) hạng vài trăm / không có trong index (vỡ trận). Thiếu cái này thì 0/5 vô dụng để định hướng.
*   **Giải pháp là gì?**
    *   **Golden set** (`eval_set.py`): bộ câu hỏi **đóng băng**, mỗi câu dán sẵn `expected_path_substr` + `expected_keywords` (ground-truth). Chấm tự động 1 quy tắc: top-3 có mảnh nào **VỪA đúng file VÀ chứa keyword** không (`AND`, không `OR` — `OR` thổi điểm giả vì mảnh sai file vô tình dính keyword vẫn đậu). Tái dùng `build_index/embed_texts/retrieve_top_k` từ `mini_rag` (import, không copy).
    *   **precision@3 ≠ recall/hit-rate@3:** cách roadmap đếm ("top-3 có dính chunk đúng không → 1 câu") thực ra là **hit-rate@3**; precision@3 thật = (số mảnh liên quan / 3). Phải gọi đúng tên khi phỏng vấn.
    *   **Hàm chẩn đoán `gold_rank`** (món senior): xếp hạng TOÀN BỘ 3308 chunk, báo mảnh vàng nằm **hạng mấy**. Đây là cái biến "0/5 nản chí" thành bằng chứng định lượng. **Đo thật (5 câu in-scope, MiniLM): precision@3 = 0/5 = 0%**, nhưng mảnh vàng đều CÓ trong kho, chôn ở hạng **116 / 130 / 391 / 415 / 1724 trên 3308** (score 0.15–0.34) trong khi rác `.md` tiếng Việt ngồi top (0.5–0.65). ⇒ MiniLM **không thiếu kiến thức, nó xếp hạng sai** = bệnh retrieval/embedding, không phải generation. **Chunk nam châm mới: `HUONG_DAN.md#23`** hút top-1 của 4/6 câu tiếng Việt.
*   **Khi nào KHÔNG dùng / Bẫy đã sập (verify, đừng đoán — Ngày 7 lặp lại):**
    *   **`gold_rank` bắt lỗi của CHÍNH bài thi:** 2 câu báo "KHÔNG TÌM THẤY" → grep ra `IGNORE_DIRS` của `mini_rag` loại thư mục `tests/`, mà ground-truth mình trỏ vào `tests/admin-routes.test.js` + `tests/harness.js` → đáp án KHÔNG có trong corpus = **mình soạn golden set sai**, không phải retrieval dở. ⇒ **Quy tắc vàng: ground-truth phải trỏ vào nơi THẬT SỰ được index.** Sửa: RBAC trỏ lại `core/admin-auth.js` (có `ROLE_PERMISSIONS`, hạng 391); rút câu test-framework (đáp án chỉ ở tests/). **Phát hiện kiến trúc:** corpus đang bỏ `tests/`, trong khi tests chứa "sự thật quyền lực" (danh sách vai trò) → cân nhắc index tests sau.
    *   **Golden set chỉ đáng làm khi sắp có thay đổi lớn cần chứng minh** (đúng lúc sắp sang Ngày 10). Và **đừng so 0/5 (Ngày 9) với 2/6 (Ngày 6)** — câu Ngày 9 thuần tiếng Việt hơn (khó + thực tế hơn), khác wording = khác bài thi. Từ giờ bộ 5 câu này **đóng băng** làm chuẩn; trị số tuyệt đối ít quan trọng bằng việc nó **cố định** để so Ngày 10.

### Ngày 10: Swap embedding model (MiniLM → BGE-M3 → Qwen3) + đo lại precision@3
*   **Vấn đề là gì?**
    *   Ngày 9 đã chốt baseline MiniLM = **0/5**, mảnh vàng chôn hạng 116–1724 ⇒ nghi tầng embedding là nút thắt. Nhưng "nghi" chưa phải bằng chứng — phải **đổi đúng 1 biến (model) và đo lại trên CÙNG bài thi** mới biết model mạnh hơn có cứu được không, hay chỉ là kỳ vọng.
*   **Giải pháp là gì?**
    *   **Swap sạch (apples-to-apples):** thêm tham số `model_name` cho `load_embedding_model`, cho `eval_set.py` đọc tên model từ `sys.argv` → đổi model **KHÔNG sửa logic**, giữ nguyên chunking + golden set + cách chấm. Chỉ 1 biến thay đổi.
    *   **Bẫy Qwen3 bất đối xứng:** Qwen3-Embedding là model *asymmetric* — query phải gắn "lời dặn" (`Instruct: ...\nQuery: ...`), document để trần. Bỏ bước này là **chấm oan** cho nó. BGE-M3/MiniLM không cần ⇒ chỉ áp khi tên model chứa `qwen3` (`embed_query`).
    *   **Đo thật (CÙNG 5 câu golden set):**
        | Model | precision@3 | Mảnh vàng (hạng) |
        |---|---|---|
        | all-MiniLM-L6-v2 | **0/5 = 0%** | 1724 / 415 / 391 / 116 / 130 |
        | BAAI/bge-m3 | **2/5 = 40%** | verifySig **8**, credential **5**, RBAC **109**, lead ĐẬU, multi-shop ĐẬU |
        | Qwen3-Embedding-0.6B | **N/A** | embed CPU-only ~310s/batch → ETA ~9h, DỪNG |
    *   **💎 Bằng chứng vàng 1 — embedding KHÔNG còn là nút thắt:** đổi MiniLM→BGE-M3 đẩy mảnh vàng từ hạng **1724 → 8**, **415 → 5**. precision@3 **0% → 40%**. Câu CV: *"cải thiện precision@3 0%→40% khi đổi MiniLM→BGE-M3, đo trên golden set tiếng Việt"*.
    *   **💎 Bằng chứng vàng 2 — 2 câu trượt nằm hạng 5 & 8 (sát top-3):** đây KHÔNG phải thất bại mà là **lời mời cho reranker / top-k lớn hơn** (Level 3). `gold_rank` biến "RỚT" thành định hướng: thêm rerank là 4/5, khỏi đổi model mù quáng.
    *   **💎 Bằng chứng vàng 3 — verifySignature lộ thủ phạm mới = CHUNKING:** BGE-M3 đưa `webhook.js` lên **top-1 (0.662)** = đúng file! Nhưng vẫn RỚT vì chunk top-1 KHÔNG chứa keyword, chunk có keyword nằm hạng 8 → đúng "phát hiện vàng 2" Ngày 5 (hàm con `verifySignature` bị xé header khỏi thân). ⇒ **Embedding sửa xong → bug chunking Ngày 4–5 trồi lên là nút thắt kế.**
*   **Khi nào KHÔNG dùng / Bẫy đã sập (verify, đừng đoán):**
    *   **🔴 Số tham số ≠ chi phí inference — KIẾN TRÚC quyết định.** Qwen3-0.6B và BGE-M3 (~0.6B) bằng nhau về tham số, nhưng Qwen3 là **decoder (causal LM)** fp32 trên CPU → **~310s/batch, ~9.7s/chunk → ETA ~9h** cho 3308 chunk = bất khả thi; BGE-M3 là **encoder** (1 lượt forward 2 chiều) chạy CPU ngon. ⇒ Chọn model phải cân **cả hạ tầng** (có GPU không?), không chỉ điểm benchmark. Muốn Qwen3: cần GPU hoặc quantize (ONNX/int8). Máy này không có GPU (`torch.cuda.is_available()=False`).
    *   **🔴 Nghi ngờ chính cây thước (golden set) — verify từng câu:** grep thật chatbot-fanpage: 3/5 ground-truth **đá tảng** (verifySig→webhook.js dòng 270-276 `createHmac/timingSafeEqual`; RBAC→admin-auth.js dòng 15 `ROLE_PERMISSIONS`; lead→lead-parser.js). Câu **credential** đúng (code ở `page-credentials.js` dòng 33,54) nhưng keyword `aes-256-gcm` rò ra 6 file docs → docs là distractor, luật `path AND keyword` loại đúng. Câu **multi-shop YẾU NHẤT**: ground-truth là 1 doc **archive/checkpoint**, keyword `dry_run` có ở **66 file** → logic isolation thật chắc nằm ở `core/shops/db-shop-config.js` / `db/multi-shop-proposal.sql`. ⇒ TODO: re-ground câu này rồi chạy lại CẢ 3 model cho đồng nhất. "ĐẬU" của multi-shop hôm nay đọc kèm chú thích.
    *   **💡 Tác vụ dài PHẢI có tín hiệu sống:** `model.encode(3308)` để `show_progress_bar=False` → chạy mù 2 tiếng tưởng treo. Cách verify treo-hay-chậm: đo **delta CPU** (còn tăng = còn chạy). Đã đổi sang `show_progress_bar=True`. Bài học UX: im lặng = người dùng tưởng hỏng.

### Ngày 11: Two-stage retrieval (Reranker) + GPU sống lại + ràng buộc 4GB VRAM
*   **Vấn đề là gì?**
    *   Ngày 10 chốt BGE-M3 = 40%, 2 mảnh vàng nằm hạng 5 & 8 (sát top-3). Bi-encoder embed query/chunk **riêng rẽ** → nén chunk thành vector TRƯỚC khi thấy câu hỏi → mất tương tác chéo, mảnh đúng tụt hạng. Cần tầng 2 đọc **(query + chunk) cùng lúc**.
*   **Giải pháp là gì?**
    *   **Two-stage:** bi-encoder lọc top-N (rẻ, quét cả kho) → **cross-encoder** (`bge-reranker-v2-m3`, XLM-R large ~568M) chấm lại từng cặp → top-3. `rerank()` trả **bản sao** (không mutate list caller); `eval_set.py` đọc `K_RETRIEVE` từ argv; **cache embedding bằng pickle** (khỏi embed lại 38'/lần — vector tái dùng được, chỉ rerank N là đổi).
    *   **💎 Reranker CÓ tác dụng — ở ĐÚNG N:** quét N=10→100 đều **3/5 = 60%** (cứu câu credential, mảnh vàng hạng 5 lọt top-3); baseline no-rerank = 40%. ⇒ 40% → 60%.
    *   **💎 N to hơn lại TỆ hơn (60% → 40% ở N=150):** cross-encoder chấm **từng cặp ĐỘC LẬP** nên điểm mảnh vàng **không đổi** theo N; rổ to chỉ **thêm cơ hội cho distractor mạnh lọt vào** — `next-session-prompt.md` (hạng bi-encoder ~101–150) được chấm +0.38, đạp credential ra. ⇒ chọn **N nhỏ (20–30): precision bằng, nhanh hơn, ít rủi ro hơn**. "To cho chắc" là phản trực giác SAI (= câu phỏng vấn vàng).
    *   **💎 GPU = đòn bẩy TỐC ĐỘ, KHÔNG phải chất lượng:** CPU N=150 = **91 s/câu** → GPU ~**9.4 s** (~10×). precision **không đổi** theo thiết bị (đo thật, cùng golden set). Máy giờ có GPU thật (RTX 3050 Ti, torch cu126) — lật quyết định "DỪNG Qwen3" Ngày 10.
*   **Khi nào KHÔNG dùng / Bẫy đã sập (verify, đừng đoán):**
    *   **🔴 Mentor kết luận VỘI:** ban đầu chốt "reranker vô dụng, 40%→40%" khi **chỉ có dữ liệu N=150**. N=50 (60%) lật ngược. Lặp đúng bài học Q5/RBAC: **đừng chốt khi thiếu phép đo** — cái thiếu (N nhỏ) đúng là cái thay đổi câu chuyện.
    *   **🔴 4GB VRAM là ràng buộc THẬT:** BGE-M3 (~2.2GB) + reranker (~2.27GB) fp32 cùng lúc > 3.45GB trống → **OOM**. Sửa: ép **embed→CPU** (đã cache nên chỉ embed 1 câu hỏi/lần, nhẹ), **rerank→GPU** (nút thắt tốc độ). Model >1B vẫn phải dùng API.
    *   **Reranker KHÔNG sửa được 2 thứ → trần 60%:** (1) **recall tầng 1** — RBAC hạng 109 ngoài rổ nhỏ tối ưu; vào rổ 150 thì thua prose `DESIGN.md` (distractor `.md` tiếng Việt); (2) **chunking hỏng** — verifySig: chunk chứa `createHmac` bị xé mất tên hàm nên cross-encoder cũng dìm. ⇒ nút thắt kế: **chunking (Ngày 12)** + **tách/lọc doc-vs-code** diệt distractor.
    *   **Pipeline tất định:** chạy lại cùng N ra **cùng số** (vector cached + cross-encoder eval mode, không random) → tái lập được, không phải bế tắc. Đo thời gian bị nhiễu **warmup GPU** + `gold_rank` quét tay 3308 chunk bằng Python (N=50 14s > N=150 9.4s là do warmup, không phải rerank chậm hơn) → muốn số sạch phải chạy 1 lần làm nóng trước vòng đo.
*   **🎤 Câu phỏng vấn + trả lời mẫu (đã sửa — đọc to để ôn):**
    *   *Hỏi:* "Rerank đẩy 40%→60% nhưng trần ở 60%, 2 câu kia bó tay. Cho 1 tuần, em làm gì — và vì sao KHÔNG phải đổi embedding model mạnh hơn?"
    *   *Đáp:* "Tôi chọn **vá chunking** trước. Bằng chứng: sau khi thêm **tầng rerank** (không phải đổi model — BGE-M3 giữ nguyên), verifySignature đã lên **top-1 đúng file** → 'tìm đúng chỗ' hết là vấn đề. Nó vẫn rớt vì chunk chứa thuật toán bị **xé mất tên hàm**, nên cross-encoder **dìm** (KHÔNG phải 'từ chối' — từ chối là việc tầng generation) nó xuống dưới top-3. Đổi embedding model mạnh hơn vô ích vì nó vẫn embed **đúng cái chunk vụn đó** — **rác vào, rác ra**. Còn RBAC là **bệnh khác** (distractor doc tiếng Việt + recall, không phải chunking) → xử riêng bằng tách collection code/doc. Và tôi **đo lại trên cùng golden set** để chứng minh, không đoán."
    *   **3 lỗi tự bắt được khi tập nói:** (1) rerank **dìm/rank thấp**, KHÔNG "từ chối"; (2) 40→60 là do **thêm tầng rerank**, không phải model mạnh hơn; (3) 2 câu rớt là **2 bệnh khác nhau** (verifySig=chunking, RBAC=distractor) — đừng gộp.

### Ngày 12: Vá chunking 2 tầng + bài học "nút thắt ràng buộc" (vá đúng kỹ thuật mà số KHÔNG đổi)
*   **Vấn đề là gì?**
    *   Ngày 11 chốt trần 60%, verifySignature là "bệnh chunking": regex `.js` neo `(?m)^` **cột 0** → bỏ sót ~30 hàm con **thụt lề** trong `createWebhook` → cả hàm gom 1 cục khổng lồ → fallback chém mù 800 ký tự → xé `function verifySignature` khỏi thân `createHmac`. Không chunk nào tự đủ nghĩa.
    *   Phụ: chunk mịn quá đà → nhiều helper tí hon (255–340 ký tự) mất ngữ cảnh.
*   **Giải pháp là gì? (2 tầng tách bạch — đừng trộn)**
    *   **Tầng 1 — regex:** chèn `[ \t]*` ngay sau `^` → `(?m)^[ \t]*(?:...function...)`. `[ \t]*` = "0-nhiều space/tab **trong cùng dòng**" → bắt cả hàm thụt lề. ⚠️ KHÔNG dùng `\s*` (nó nuốt cả `\n`, trườn qua dòng). An toàn vì `function\s+\w+` đòi "space + TÊN" ngay sau (chuỗi `'function'` giữa câu không khớp) + anchor đòi mở đầu dòng.
    *   **Tầng 2 — `_merge_small_chunks(target=600)`:** gom các chunk liền kề vào "rổ" chừng nào tổng ≤ 600; chunk tự nó đã to thì đứng riêng. **Chỉ gộp NGUYÊN mảnh, không cắt** (ngược fallback). Đặt **TRƯỚC** fallback (nếu sau, fallback đã chém đứt seam rồi mới gộp = dán mảnh gãy). Goldilocks: 200=không gộp gì (fix chết yểu), **600=vừa**, 2000=chunk khổng lồ trở lại + vượt 1600 làm fallback nổ lại = **tái tạo bệnh Ngày 4-5**. Quy tắc: `MERGE_TARGET` luôn **< `FALLBACK*2`** kẻo 2 tầng đánh nhau.
    *   **Đo thật (cùng golden set):** verifySignature bi-encoder **hạng 8 → 1** (chunk #18 tự đủ nghĩa 452 ký tự, có cả tên hàm + `createHmac/timingSafeEqual`). Chunk count toàn corpus: tầng1 → 3589, +tầng2 → **3016** (gộp −573 mảnh vụn). **Chunking ĐÚNG về cấu trúc.**
*   **🔴 Nhưng precision@3 KHÔNG đổi: 40% (no-rerank) / 40% (rerank N=50) — thậm chí TỤT so Ngày 11 (60%, do lead rớt).** Đây là bài học lớn nhất:
    *   **💎 Theory of Constraints:** verify đúng bệnh (vụn), vá đúng kỹ thuật — nhưng vá một bệnh **KHÔNG-phải-nút-thắt** thì đầu ra **đứng im**. Sửa cái không ràng buộc = 0 tác động.
    *   **💎 Nút thắt thật = tầng RERANK + distractor doc `.md`** (đã verify bằng cách đọc tận chunk). 3/5 câu (verifySig, RBAC, lead) bị doc `.md` tiếng Việt "nói VỀ chủ đề" thắng chunk `.js` "LÀ bản cài đặt": verifySig→reranker chọn `webhook.js#28`+`zenbot-source-map.md`; lead→`HUONG_DAN.md#13` lên #1; RBAC→`DESIGN.md#9`. **Reranker khớp THỰC THỂ/bề mặt, không khớp Ý ĐỊNH "lấy phần triển khai".** "Chứa TÊN ≠ chứa ĐÁP ÁN."
    *   **Reranker KHÔNG tự phân biệt code/doc** — nó coi tất cả là text như nhau nên mới bị lừa. **CHÍNH TA** phải áp cấu trúc (metadata `type` / 2 collection) để chặn distractor. → hồi sinh ý "tách code-vs-doc" hoãn từ Ngày 11, **giờ có bằng chứng tươi**. Đây là ROI kế tiếp, KHÔNG phải vặn thêm chunking.
*   **Khi nào KHÔNG dùng / Bẫy đã sập (verify, đừng đoán — chủ đề lặp Ngày 7/9):**
    *   **🔴 Bộ lọc test lỏng tay = bug giả dạng "hệ thống hỏng":** lệnh kiểm chứng dùng `endswith('webhook.js')` + `[0]` → quơ nhầm `sheets-webhook.js` (không có verifySignature) → tưởng regex hỏng. Regex không sai, **cây thước sai**. Lọc phải chặt: `endswith('core\\webhook.js')`.
    *   **🔴 Cache `.pkl` phải xoá khi đổi chunking:** `build_index_cached` cache-hit → return vector CŨ, bỏ qua cả chunk lẫn embed → đo nhầm chunking cũ (apples-to-apples Ngày 10). Đổi chunk = `Remove-Item .index_cache_*.pkl` rồi chạy lại.
    *   **Quyết định kỹ thuật:** GIỮ chunking mới (đúng cấu trúc, 8→1 sẽ thành điểm-đậu KHI trị xong reranker) nhưng **DỪNG vặn chunking** — chuyển nút thắt sang tách code/doc. Đừng đuổi con số bằng cách revert một thay đổi đúng.
*   **🎤 Câu phỏng vấn:** *"Bỏ 1 ngày vá chunking mà precision vẫn 40%, có phí không?"* → *"Không. Chứng minh được chunking KHÔNG phải nút thắt (chunk đích 8→1 ở bi-encoder); precision đứng im dạy tôi 'sửa bệnh không-ràng-buộc thì output không đổi'; và nó định vị nút thắt thật = rerank bị doc `.md` đánh lừa 3/5 câu → hành động tiếp theo CÓ bằng chứng là tách code/doc. Báo team bằng số trên golden set, không bằng cảm giác."*

### Ngày 13: Hybrid Search (BM25 + Dense → RRF) — thêm kênh keyword mà precision TỤT (bài học nút-thắt lặp lần 3)
*   **Vấn đề là gì?**
    *   Dense (bi-encoder) **mù token hiếm/định danh** (tên hàm, ID, `aes-256-gcm`) vì nén chunk thành vector TRƯỚC khi thấy query — nối tiếp Ngày 2 (`#1234`≈`#5678`). Tầng 1 chỉ có **1 kênh** (ngữ nghĩa) → thiếu hẳn kênh khớp-mặt-chữ. Pipeline chuẩn ngành = **BM25 + Dense → RRF → rerank**.
*   **Giải pháp là gì?**
    *   **BM25** (lib `rank_bm25`, `BM25Okapi`): chấm theo khớp mặt chữ (TF, có **bão hoà** k1 — lặp từ 10 lần KHÔNG ×10 điểm) × độ hiếm toàn corpus (**IDF**). Token càng hiếm mà khớp → điểm càng cao → kéo thẳng chunk chứa đúng `createHmac` lên. Dựng trên **CÙNG list chunk** của index (không re-chunk, không copy); tokenize `re.findall(r"\w+", text.lower())` — `\w` Unicode nên giữ token tiếng Việt có dấu.
    *   **RRF (Reciprocal Rank Fusion)** trộn 2 danh sách: `RRF(d) = Σ 1/(k+rank_i(d))`, `k=60`. **Chỉ dùng THỨ HẠNG** → né bài toán **cosine bị chặn [−1,1] vs BM25 không chặn [0,∞)** (cộng thẳng thì thang BM25 nuốt cosine, chuẩn hoá thì mong manh). Chunk được **CẢ 2 kênh gật đầu** (đồng thuận) vượt chunk chỉ #1 ở một kênh — đó là linh hồn RRF. Code ~6 dòng: 1 dict cộng dồn, `enumerate(start=1)`, `sorted reverse`.
*   **🔴 Đo thật (CÙNG golden set, BGE-M3, N=50): baseline dense→rerank 40% → HYBRID 20%. TỤT, không phải tăng** (dự đoán 40→60-80% SAI). Đổi đúng 1 kết quả: credential **ĐẬU→RỚT**.
    *   **💎 Theory of Constraints (lặp lần 3 sau Ngày 11–12):** `gold_rank` cho thấy 3/5 mảnh vàng **đã trong rổ** (hạng **1, 5, 5** ở tầng 1) ⇒ **recall tầng 1 KHÔNG phải nút thắt**. BM25 chỉ giỏi *kéo mảnh vàng vào rổ* — mà rổ đã có sẵn. Vá cái không-ràng-buộc → số đứng im hoặc **tụt**.
    *   **💎 Tác dụng phụ giết điểm:** reranker chấm **độc lập từng cặp** (Ngày 11) nên thêm ứng viên = **thêm cơ hội cho distractor thắng**, KHÔNG nâng gold. Hybrid bơm `next-session-prompt.md` (prose nói VỀ credential, BM25 khớp token `credential`/`mode` trong câu hỏi) vào rổ → reranker (mê doc `.md`, Ngày 12) chọn nó → credential vỡ. **Cùng cơ chế "N=150 tệ hơn N=50" Ngày 11**, chỉ khác nguồn distractor.
    *   **💎 Đừng cargo-cult pipeline chuẩn:** BM25+dense→RRF→rerank **giả định tầng rerank tốt**. Ở corpus này rerank là **mắt xích yếu** → đắp thêm kênh keyword trước khi sửa reranker = đổ thêm dầu. **Golden set là trọng tài**, không đoán theo "best practice".
*   **Khi nào KHÔNG dùng / Bẫy đã sập (verify, đừng đoán):**
    *   **Hybrid KHÔNG có lỗi — sai ở thứ tự ưu tiên.** RRF/truncation code đúng: gold credential (hạng 5) VẪN trong rổ fused, reranker thấy mà vẫn dìm → không phải bug "evict gold". KHÔNG vứt code hybrid (giữ làm biến bật/tắt, test lại CÙNG code/doc filter Ngày 14 — có khi hybrid+filter mới thắng).
    *   **🔴 Verify cây thước (lặp Ngày 9/12):** grep ra `wizard-routes.js` & `views.js` **cũng chứa** `aes-256-gcm` → có thể là đáp án hợp lệ, golden set đang siết `path=page-credentials.js` only. TODO: soi lại có nên cho credential nhiều path đúng. (Nhưng `next-session-prompt.md#2` top-1 thì chắc chắn distractor.)
    *   **🔴 Lỗ hổng chẩn đoán:** `gold_rank` trong chế độ hybrid vẫn tính theo **dense ranking**, chưa phản ánh **hạng trong rổ FUSED** → message "NGOÀI rổ" của RBAC (dense hạng 104) gây hiểu nhầm. Cần thêm `fused_rank` để chẩn đúng tầng hybrid.
    *   **🔑 Bẫy paste:** dán `rrf_fuse` nuốt mất dòng `def retrieve_top_k` → hàm biến mất → `import` sẽ vỡ. Quy tắc: sau mỗi paste lớn chạy `python -m py_compile file.py` (hoặc `import`) để chắc file còn parse.
*   **SOTA + quyết định (research 29/6, Lăng kính 6 câu):** nút thắt = reranker bị doc distractor → trị bằng ranh giới **code/doc**. Chọn **metadata filter `type` trong 1 collection** (nhẹ, reversible, suy từ đuôi `.js`/`.md`, production-proven Chroma/NVIDIA) THAY VÌ tách 2-collection+routing (nặng, lock-in, +classifier). Tách 2-collection cho thêm *cô lập* (embedding riêng/loại) nhưng đó CHƯA phải nút thắt. Micro-PoC ≤2h Ngày 14: thử (a) chỉ-code, (b) code-trước doc-sau; leo routing chỉ khi filter cứng giết câu doc-hợp-lệ.

### Ngày 14: Metadata filter code/doc (soft-boost λ) — hypothesis bị golden set BÁC BỎ (nút-thắt lặp lần 4)
*   **Vấn đề là gì?**
    *   Ngày 12–13 chốt (bằng cách đọc chunk): 3/5 câu vỡ vì reranker mê prose `.md` "nói VỀ" hơn `.js` "LÀ bản cài đặt". Giả thuyết: reranker không phân biệt code/doc → **CHÍNH TA** áp cấu trúc bằng nhãn `type` rồi phạt điểm doc để chặn distractor.
    *   Rủi ro biết trước: có câu **đáp án LÀ doc** (multi-shop → `multi-shop-rollout.md`). Phạt cứng doc sẽ giết nó → chọn **soft-boost (trừ λ), KHÔNG hard-filter**.
*   **Giải pháp là gì? (2 mảnh — giữ hàm cũ nguyên)**
    *   **Nhãn `type`** suy TỪ ĐUÔI FILE (`.md`=doc, còn lại=code), gắn NGAY trong `chunk_text` (chỗ chunk khai sinh) → mọi consumer (build_index, bm25, chroma_rag import, test) TỰ thừa hưởng = **một nguồn sự thật**. KHÔNG hardcode (bug thầm lặng: gắn cứng "code" thì soft-boost vô hiệu). Đo: 2190 code / 826 doc.
    *   **`soft_boost_by_type(reranked, lam)`**: TRỪ λ vào `rerank_score` của chunk doc rồi xếp lại. λ CÙNG ĐƠN VỊ điểm rerank (**logit, KHÔNG phải %** — không copy λ từ blog, mỗi reranker một thang). λ=0 → y baseline (chốt chặn sanity). **Thứ tự BẮT BUỘC:** rerank chấm CẢ RỔ (`top_k=len`) TRƯỚC, soft-boost mới cắt top-K — nếu cắt top-3 trước rồi mới phạt thì code đã bị cắt mất, phạt vô ích. `hard_filter_type` (vứt doc trước rerank) để riêng làm **ablation**.
*   **🔴 Đo thật (CÙNG golden set, BGE-M3) — lưới 2×2 + N=150. Winner = BASELINE N=50 no-filter = 40%. Filter làm TỆ ĐI:**
    | Ô | N50 base | N50 soft λ1 | N50 hyb | N50 hyb+soft | N150 base | N150 soft λ1 |
    |---|---|---|---|---|---|---|
    | precision@3 | **40%** | 20% | 20% | 20% | 20% | **0%** |
    *   **💎 Zero-sum (tổng-bằng-không):** trên golden set này chỉ credential & multi-shop từng đậu, và filter **đổi câu này lấy câu kia**: soft-boost cứu credential (phạt `next-session-prompt.md`) NHƯNG giết multi-shop (đáp án LÀ doc). `type` flag mù — **không tách được "doc nói VỀ" với "doc LÀ đáp án"**.
    *   **💎💎 Đòn đá tảng — RBAC ở N=150 soft bác bỏ CHÍNH giả thuyết:** gold `admin-auth.js` hạng 104 < 150 → **ĐÃ vào rổ**; mọi doc bị λ phạt sạch → top-3 **toàn code**; **VẪN RỚT** vì reranker chọn `admin-routes.js#68`/`views.js#190`, KHÔNG chọn gold `admin-auth.js`. ⇒ Gold trong rổ + distractor doc đã dọn sạch mà reranker **vẫn dìm gold** → nút thắt **KHÔNG phải** doc-distractor, **KHÔNG phải** recall.
    *   **💎 Nút thắt thật = ĐỘ CHÍNH XÁC RERANKER (chọn nhầm chunk anh-em).** Cả 3 câu vỡ đều: gold ở tầng-1 nằm trong tầm (verifySig dense **#1**, lead **#5**, RBAC **#104**→vào rổ N150) NHƯNG reranker chọn chunk khác cùng-file/cùng-loại-code không chứa keyword. Filter/hybrid/N-lớn KHÔNG chạm được cái này → **Theory of Constraints lần 4** (vá cái không-ràng-buộc → số đứng im hoặc tụt).
*   **Khi nào KHÔNG dùng / Bẫy đã sập (verify, đừng đoán):**
    *   **type-filter KHÔNG dùng** khi golden set có câu **đáp-án-là-doc** (nó giết chúng). Và filter chỉ có ý nghĩa khi nút thắt ĐÚNG là doc-distractor — ở đây không phải.
    *   **λ=1 ≈ hard-filter** ở thang điểm reranker này (điểm trải ~[−?, +0.6]; doc `+0.38` trừ 1 = `−0.62` rơi dưới mọi code). "Soft λ=1" thực chất test gần-hard → mới giết sạch multi-shop. Muốn soft thật phải λ nhỏ (~0.1–0.2), nhưng ở đây **không λ nào cứu** vì gold-code cũng bị reranker dìm.
    *   **🔴 Cây thước chẩn đoán NÓI DỐI (lặp Ngày 9/13):** dòng `-> reranker vẫn dìm` cho câu bị λ phạt là sai — nó bị **λ của TA** đẩy xuống, không phải reranker. `gold_rank`/message chưa trừ boost (đúng lỗ `fused_rank` đã ghi trong plan). Sửa message ở Ngày 15.
    *   **🔴 Cache: xoá hay VÁ?** Thêm key `type` chỉ đổi **metadata suy-được**, `content` y nguyên → **vector y hệt**. Bài học Ngày 12 ("đổi chunking → xoá `.pkl`") áp cho đổi CONTENT; ở đây chỉ cần **vá** cache (thêm `type` từ path, ~1s) thay vì re-embed 44 phút. Quy tắc tinh: *invalidate theo cái ĐÃ đổi* — content đổi mới re-embed; metadata suy-được đổi thì patch.
*   **Quyết định:** KHÔNG ship filter; `λ=0` mặc định, code soft/hard giữ làm toggle (như hybrid). **Nút thắt kế = reranker precision** — tách 2 giả thuyết TRƯỚC khi tốn tiền: **H1** reranker yếu → thử **instruction-following reranker** (Voyage rerank-2.5 "ưu tiên implementation"); **H2** gold-chunk tự nó dở (chunking xé, đọc không ra đáp án) → reranker dìm ĐÚNG = "rác vào rác ra" (Ngày 11) → quay về chunking/golden-set. **Phải ĐỌC gold-chunk vs chunk-thắng mới phân định** (verify, đừng đoán).

### Ngày 15: ReAct agent + structured output (`agent.py`) — agent chạy thật, 5 vòng debug đắt hơn bài học chính

*   **Pattern ReAct (3 câu):**
    *   **Vấn đề:** pipeline RAG là one-shot (retrieve 1 lần → trả lời), không xử lý được câu audit đa bước ("có mã hoá yếu không?" = tìm → đọc → thấy manh mối → tìm tiếp); chính tôi đã đo trần dense retrieval 60%, và lớp lỗi verifySig/RBAC là thứ grep trị tận gốc — lý do ngành chuyển sang agentic search.
    *   **Giải pháp:** đặt LLM vào vòng lặp Thought → Action (gọi tool) → Observation (kết quả nối lại vào context) → lặp đến khi đủ thì Answer; model TỰ quyết bước kế dựa trên observation.
    *   **Khi nào KHÔNG dùng:** câu 1 bước — mỗi step = 1 LLM call và **mỗi call gửi lại TOÀN BỘ lịch sử** (token phình dần) → agent chậm + đắt + thêm bề mặt lỗi loop vô hạn (bắt buộc `MAX_STEPS`, của MÌNH đặt, không phải của Google). Model cho loop = flash-lite ($0.10/$0.40, rẻ ~15–22× so 3.5-flash).
*   **Structured output thay regex parse (3 câu):**
    *   **Vấn đề:** cách paper 2022 bắt model in text `Action: grep(...)` rồi regex bắt lại — model lệch format một sợi tóc là agent đứng hình (bug runtime thật).
    *   **Giải pháp:** truyền `tools=[hàm Python]` vào config; SDK đọc **signature + docstring** sinh JSON schema (⇒ **docstring = PROMPT dạy model dùng tool**, không phải ghi chú); model trả `response.function_calls` có sẵn `name`+`args` dict — không parse gì. TẮT `automatic_function_calling` để tự viết vòng lặp → có **trace từng bước** (nguyên liệu citation/findings của auditor — cái gì không quan sát được thì không sửa được).
    *   **Khi nào KHÔNG dùng:** model không hỗ trợ function calling (local cũ) mới phải prompt-parse; automatic mode tiện demo nhưng nuốt trace.
*   **API stateless — `contents` LÀ trí nhớ:** server không nhớ gì giữa 2 call; mỗi vòng phải append **2 lượt**: quyết định của model (`candidates[0].content` — thiếu nó là function_response mồ côi → lỗi 400) + kết quả tool (`Part.from_function_response`, role `user`). `candidates[0]` = phương án trả lời thứ nhất (N mặc định = 1), không phải thời gian 😅.
*   💎 **Vòng lặp đúng ≠ agent giỏi:** cơ chế nằm ở code, **hành vi nằm ở SYSTEM_PROMPT (= bản policy)**. Đo thật 5 vòng: model nhỏ **lờ luật nếu-thì** ("nếu trượt thì thử lại") nhưng **theo QUY TRÌNH đánh số** (Bước 1→4); luật phải đo được ("ít nhất 2 pattern KHÁC"); ép **khảo sát MẶT DƯƠNG trước** (grep cái ĐANG dùng) rồi mới soi danh sách yếu — vì **vắng bằng chứng ≠ bằng chứng vắng**, và trả lời **đúng-nhờ-may ≠ đúng-nhờ-bằng-chứng** (phải nắm ground truth TRƯỚC khi chấm agent — grep tay codebase: HMAC-SHA256 `webhook.js:271`, AES-256-GCM `page-credentials.js:33`, timingSafeEqual khắp nơi).
*   💎💎 **Chuỗi bug 3 tầng (chuyện phỏng vấn vàng):**
    1.  **Bẫy Windows:** code mẫu `subprocess.run(["grep",...])` — Windows không có grep.exe (`where.exe grep` = not found) → `FileNotFoundError` bị `except Exception` nuốt → tool trả "Error" làm observation = **chết im lặng kiểu 1**. Vá: viết grep **Python thuần** (os.walk + re, tự lắp `file:line:` = format citation, 0 dependency).
    2.  **Chuỗi con:** pattern `des` khớp `designed` (regex mù nghĩa/mù ngôn ngữ — chỉ so ký tự; khác embedding) → observation ngập rác DESIGN.md. Vá: dạy model `\b` **qua docstring tool** — KHÔNG ép `\b` trong tool (giết use-case tìm chuỗi con chủ đích như `Hmac`⊂`createHmac`).
    3.  **JSON escape:** model viết `"\b..."` trong function call → JSON decode thành **ký tự backspace `\x08`** → regex hợp lệ nhưng match 0 → "No matches" = **chết im lặng kiểu 2** → agent phán chắc nịch "hệ thống không dùng mật mã" = **FALSE NEGATIVE TỰ TIN — tội nặng nhất của auditor** (bằng chứng nó sai: ground truth đầy crypto). Vá defensive: `pattern.replace("\x08", r"\b")` — tool biết tật của model thì sửa hộ. (Bẫy cùng họ: trong Python string `"\b"` cũng là backspace → source phải viết `\\b`.)
*   🪜 **Thang đòn bẩy khi agent lười (leo từ rẻ):** sửa prompt (free, đã vắt 3 bản) → bật thinking → đổi model to. Mỗi lần leo đổi đúng 1 biến, có trace so sánh.
*   **Thiết kế có chủ đích:** agent KHÔNG import `IGNORE_DIRS` của mini_rag dù có quy ước import-lại — set đó loại `tests/` (chính nó gây bug golden-set Ngày 9), mà **auditor không được mù tests** → agent chỉ bỏ `node_modules`/`.git`. Quy ước tái dùng thua ngữ nghĩa đúng.
*   **Kết quả vòng 5 (đậu có điều kiện):** 2 grep đúng bài (dương trước, `\b` sau), kết luận khớp ground truth (SHA-256 + timingSafeEqual, sạch md5/sha1/des/rc4), tự khai vùng chưa chắc (.agent/ nói "encrypt" chưa rõ thuật toán). **Còn 3 bệnh → Ngày 16:** (1) **0 lần read_file** — tin lời README "kể" về page-credentials.js mà không mở code → **sót AES-256-GCM**; (2) citation mới có tên file, thiếu số dòng; (3) trần 50 dòng grep bị `.md` chiếm chỗ (os.walk đi từ gốc) = **doc distractor kiếp thứ 3** — cùng con quỷ Ngày 11-14, đổi tầng.

### Ngày 16: Guardrail tầng harness + tool che chắn model — con cá AES vào lưới sau 3 lần sổng

*   **Guardrail tầng harness (3 câu):**
    *   **Vấn đề:** vắt 3 bản SYSTEM_PROMPT mà model nhỏ vẫn lờ luật "phải read_file trước khi kết luận" (vòng 5 Ngày 15: 0 lần) — prompt là *lời khuyên*, không có gì đảm bảo tuân thủ.
    *   **Giải pháp:** chuyển luật xuống CODE vòng lặp: model muốn kết thúc (không gọi tool) → harness soi trace `tools_called` — chưa `read_file` thì TỪ CHỐI (append câu-trả-lời-bị-vứt + message từ chối role user) và ép loop tiếp. Luật giờ deterministic 100%. Đo thật: bắn 2 phát thật, model tuân, từ 0 → 7 lần read_file.
    *   **Khi nào KHÔNG dùng:** luật không kiểm tra được bằng code ("phân tích sâu sắc") vẫn phải nhờ prompt/model to; guardrail BẮT BUỘC có đường thoát (`MAX_REJECTIONS=2`) — không thì deadlock. Thang đòn bẩy: prompt (free) → guardrail harness (vài dòng code) → `tool_config` mode ANY (còng số 8: ép gọi tool MỌI lượt → agent không tự kết thúc được — thuốc cho JSON-extraction, không phải ReAct).
*   💎 **Nhân quả cuốn sổ — "model trước, thế giới sau":** `contents` chỉ có MỘT độc giả là model vòng kế; mọi lượt append phải kể đúng thứ tự nhân quả (model nói gì → thế giới đáp gì). Đảo thứ tự = sổ kể láo ("model trả lời ĐÁP LẠI lời từ chối") → model học láo, và **không 400 nào báo** = **chết im lặng kiểu 3** (API chỉ soát cú pháp sổ, không soát sự thật). Cùng nguyên lý cho function_response Ngày 15, guardrail và cú gọi chốt hôm nay — 1 luật, 3 ví dụ.
*   **Cú gọi CHỐT khi hết steps (3 câu):** hết `MAX_STEPS` mà trả câu báo lỗi kỹ thuật = vứt sạch findings đã điều tra (auditor nộp giấy trắng). Giải pháp: append message "hết giờ, tổng kết ngay" + gọi LLM 1 cú **KHÔNG truyền tools** (model hết đường gọi tool, chỉ còn nước trả text) + ép khai rõ vùng "CHUA KIEM TRA" (chống false-negative-tự-tin). KHÔNG dùng cho agent thực thi lệnh (đặt hàng/sửa DB) — tổng kết nửa vời dễ bị hiểu là "đã làm xong"; nếu quên bỏ tools → model trả function_call → `final.text` rỗng = bệnh "answer rỗng" tự chế.
*   💎 **Parallel function calling — giả định ngầm vỡ:** vòng lặp từ Ngày 15 ngầm coi "1 lượt model = 1 function call" — chưa bao giờ nằm trong hợp đồng API, chỉ *tình cờ đúng*. Hôm nay model gọi ~15 call/lượt → 400 "number of function response parts must equal function call parts". Hợp đồng thật: lượt model có N call parts → lượt đáp = **MỘT Content chứa đúng N response parts** (không phải N Content lẻ). Lỗi 400 CÓ KÊU = lỗi rẻ, tự khai chỗ sửa — so với chết im lặng đắt gấp 10.
*   **Tool che chắn model (defensive tool design, 3 mảnh đo thật):**
    *   `read_file` đánh SỐ DÒNG + tham số `start_line` (80 dòng/trang): citation `file:line` trích từ bằng chứng thật thay vì đoán; file dài hết là bức tường 3000 ký tự — model tự lật trang, đo thật nó nhảy đúng `start_line=33`.
    *   `grep` thêm `ext` — **chính là metadata filter code/doc Ngày 14, nhưng sống vì MODEL cầm công tắc** (tự bật `.js` khi audit code, bỏ trống khi cần doc) thay vì ta áp λ mù mọi query. Cùng kỹ thuật: chết ở pipeline tĩnh, sống ở agent động. Đo: 2028 khớp → 395 → 114.
    *   Trần grep: 5 dòng/FILE (không cho 1 file độc chiếm) + **chế độ ĐỘ PHỦ khi >12 file** (mỗi file 1 dòng đầu + đếm số còn lại) — vì nâng trần tổng 50→200 là thuốc sai: **cơ chế N=150 Ngày 11 tái hiện ở tầng tool output** (nới cửa chỉ tăng cơ hội distractor; walk-order giấu `page-credentials.js` khỏi đuôi danh sách 3 trận liền). Grep = trinh sát cần ĐỘ PHỦ; độ sâu đã có read_file.
*   **Kết quả trận cuối (ĐẬU):** AES-256-GCM vào báo cáo với citation verify đúng từng số (`page-credentials.js:33` code thật + `wizard-routes.js:1590` chuỗi UI); 4 grep âm tính có chủ đích từng thuật toán (md5/sha1/des-cbc/rc4 sạch); vaccine `\x08` đỡ virus lần thứ 4; guardrail im lặng cả trận (model tự read_file từ Step 2 — lưới tốt nhất là lưới không cần bung). **Còn lại → Ngày 17:** (1) bệnh "hỏi ngược làm câu trả lời cuối" (Step 6 trận 3: model hỏi "Bạn có muốn tôi đọc tiếp?" và nó lọt qua hợp lệ) → thuốc = **`submit_findings` JSON schema làm CỬA RA duy nhất** của loop (= findings report REV 2/7); (2) hạt sạn: báo cáo xếp chuỗi UI "nói VỀ AES" ngang code "LÀ bản cài đặt" — con quỷ code-vs-doc kiếp 4 chui vào string literal → schema cần field phân cấp bằng chứng.

### Ngày 17: `submit_findings` — JSON schema làm CỬA RA duy nhất + người gác validator (3 trận + 6 viên đạn giả)

*   **Structured output làm cửa ra — exit door (3 câu):**
    *   **Vấn đề:** cửa ra của agent là text tự do → bệnh "hỏi ngược làm câu trả lời cuối" lọt qua hợp lệ; và văn xuôi thì MÁY KHÔNG CHẤM ĐƯỢC — seeded-bug benchmark Tuần 4 cần code so findings với đáp án vàng.
    *   **Giải pháp:** khai tool `submit_findings` bằng schema TAY — `types.FunctionDeclaration(parameters_json_schema=SUBMIT_SCHEMA)` (tham số lồng nhau mảng-object, docstring không tả nổi); vòng lặp CHỈ kết thúc khi model gọi nó VÀ validator PASS; nộp hỏng → lỗi dội ngược qua `function_response` (model coi như kết quả tool), vòng chạy tiếp.
    *   **Khi nào KHÔNG dùng:** output cho người đọc tự do (chat/brainstorm — schema bóp nghẹt); và KHÔNG ép schema lên các bước suy nghĩ TRUNG GIAN — chỉ cửa ra, bóp cả Thought là bóp chất lượng điều tra.
*   💎 **Thang 3 tầng luật (chuyện kể 3 ngày, có số đo từng nấc):** tầng 1 PROMPT = lời khuyên (Ngày 15: luật nếu-thì bị lờ) → tầng 2 GUARDRAIL CODE = chặn cửa (Ngày 16: 2 phát từ chối, 0→7 read_file) → tầng 3 API CƯỠNG CHẾ = `tool_config` mode `'ANY'` + `allowed_function_names=['submit_findings']` (Ngày 17: model KHÔNG TỒN TẠI lựa chọn khác). Đo thật tầng 1 thua tầng 3 trong CÙNG trận: system prompt ghi "chỉ được kết thúc bằng submit_findings" — model vẫn không tự nộp suốt 10 bước; cú chốt mode ANY thì nộp ngay. ⚠️ Chỉ bật ANY ở CÚ CHỐT — bật suốt vòng là giết Thought + ép gọi tool cả lượt nên dừng.
*   💎💎 **Hai luật đá nhau thì luật VẬT LÝ thắng (bug harness tự khóa cửa — trận 1):** prompt đòi `submit_findings` nhưng cú chốt cũ (Ngày 16) RÚT HẾT tools + bắt trả text → model ngoan ngoãn trả text. Model vô tội — harness tự mâu thuẫn. Bài học rà soát: mỗi lần thêm luật mới, phải đi lại MỌI NHÁNH RA cũ xem nhánh nào đang cấm ngầm luật mới.
*   💎 **Schema-induced hallucination — "field bắt buộc thì model LẤP, kể cả bằng rác" (trận 2):** mode ANY ép nộp + không tìm ra vấn đề thật → **12 findings – 0 vấn đề** (cả 12 explanation đều "SHA-256… KHÔNG phải thuật toán yếu… info") = FP rate 100%; `not_checked=[]` là khai man (`encryptCredential` hiện NGAY trong observation mà không soi). Gốc bệnh: `required` ≠ phải-có-phần-tử, nhưng model không dám nộp mảng rỗng vì không ai bảo rỗng hợp lệ. **Thuốc = description trong schema (description = prompt):** "đã kiểm và AN TOÀN → verified_ok; không có vấn đề → `[]` là câu trả lời TỐT" → trận 3: `findings=[]` ĐÚNG SỰ THẬT, `verified_ok` 11 mục tách bạch (file:line + cách kiểm + kết luận), model TỰ phân code/comment/test-string trong từng mục. Cùng lý do `suggestion` để optional: ép điền field không kiểm chứng được = mời model bịa.
*   **`evidence_type`: code-LÀ vs doc-NÓI-VỀ (3 câu):**
    *   **Vấn đề:** con quỷ 4 kiếp — dòng `.md`, comment `//`, string literal trong `.js` đều chỉ NÓI VỀ code. Đuôi file nói về CÁI HỘP, evidence_type nói về DÒNG BÊN TRONG hộp (`console.log("...md5...")` nằm trong `.js` vẫn là doc); field mà máy tự suy được từ field khác là field thừa — cái này máy KHÔNG tự suy được, nên mới phải hỏi model (đứa duy nhất đã đọc dòng đó).
    *   **Giải pháp:** enum `["code","doc"]` bắt model tự khai lúc nộp; harness verify được MỘT CHIỀU: `.md` ⇒ chắc chắn doc (khai 'code' = láo lộ liễu → dội), còn `.js` ⇏ code — chiều đó phải tin model + để benchmark đo.
    *   **Khi nào KHÔNG đủ:** flag tự khai thì khai láo được (bài Ngày 14: flag mù không thay việc đọc) — ranh giới string-literal để seeded-bug benchmark phán.
*   **Validator (người gác cửa) + test đạn giả (3 câu):**
    *   **Vấn đề:** Ngày 16 verify citation bằng TAY; và guard mà ngồi CHỜ model tình cờ phạm lỗi mới biết nó chạy thì không bao giờ tin được nó.
    *   **Giải pháp:** `validate_report` 4+1 bước — b0: đã `read_file` chưa (**guardrail Ngày 16 dời chỗ về đây, cùng check chỉ đổi CỔNG**: từ message role-user sang `function_response`); b1 file tồn tại; b2 dòng có thật; b3 evidence khớp NGUYÊN VĂN dòng thật (ép whitespace về 1 space trước khi so — citation bịa hết đường); b4 `.md` khai 'code' → dội. Cửa trong vòng: dội không-return; cú chốt: dội đúng 1 lần rồi nộp kèm `[VALIDATOR-WARN]` (chống deadlock, cùng triết lý MAX_REJECTIONS). Guard TÁCH KHỎI model → test thuần Python 0 token: `test_validator.py` 6 viên (5 hỏng bẻ-đúng-1-chỗ + **1 viên SẠCH chống từ-chối-oan** — guard chỉ biết chửi cũng là guard hỏng) = **6/6**.
    *   **Khi nào KHÔNG đủ:** validator chỉ kiểm HÌNH THỨC (citation/file/line); bệnh NGỮ NGHĨA — finding rác, khai man not_checked, "an toàn" phán từ 1 dòng grep chưa đọc hàm (bằng chứng NÔNG, vd page-credentials.js:33 trận 3) — trị bằng description + benchmark, không phải bằng if/else.
*   **Hiện tượng ghi sổ chờ ngày trị:** model không bao giờ TỰ nộp giữa vòng (10 bước điều tra hết trước — cửa tự nguyện chưa được test); model lặp grep âm tính Y HỆT 2 lần trong 1 trận (không đọc lại sổ của chính nó).

### Ngày 18: Logging token/$/latency — trạm cân 1 cửa + sổ JSONL (con số "$/audit" đầu tiên: ~1 xu/câu)

*   **Logging chi phí cấp-cuộc-gọi (3 câu):**
    *   **Vấn đề:** agent loop gọi LLM 2–11 lần/câu, mỗi cú nạp lại TOÀN BỘ `contents` → chi phí phiên KHÔNG tuyến tính theo số step; không log thì Tuần 4 không trả lời được "mục checklist nào ĐẮT" = không có số "$/audit" cho CV. Tự ước lượng token là đoán (tokenizer Gemini ≠ tiktoken).
    *   **Giải pháp:** mỗi `response` của SDK đính kèm hóa đơn `usage_metadata`: `prompt_token_count` (nguyên liệu vào), `candidates_token_count` (hàng model viết ra), `thoughts_token_count` (giấy nháp thinking — VẪN tính tiền, giá OUTPUT), `cached_content_token_count` (nguyên liệu mua giảm giá). Nhặt + bấm giờ `perf_counter` (đồng hồ đơn điệu, không phải `time.time()` bị NTP chỉnh) → 1 dòng JSON/cú gọi vào `agent_log.jsonl`. ⚠️ Bẫy: field vắng mặt SDK trả **`None` chứ không phải 0** → `or 0` từng field, không thì `TypeError` giữa phiên.
    *   **Khi nào KHÔNG dùng:** đừng dựng platform observability (Phoenix Tuần 5 — fallback của nó chính là jsonl này); đừng log nguyên văn prompt/response vào sổ chi phí (trace nội dung ≠ sổ tiền, trộn là phình cả hai).
*   **JSONL vs JSON vs CSV (3 câu):** JSON array muốn append phải đọc-cả-file ghi-đè-cả-file → crash giữa phiên (503/429 đã gặp thật) là hỏng/mất sạch. JSONL: 1 dòng = 1 record độc lập, mở mode `"a"` — crash mất tối đa dòng đang ghi dở. KHÔNG dùng khi cần query nhiều chiều (→ SQLite) hay file config người đọc-sửa tay (→ JSON indent); CSV phẳng, mất cấu trúc lồng (list `function_calls` trong 1 step).
*   💎 **Trạm cân 1 cửa `call_llm` + vỏ `try/finally` — cùng 1 nguyên lý lặp lần 3:** 2 call site (vòng chính + cú chốt) mà rắc logging từng chỗ = quên đúng chỗ ĐẮT NHẤT (cú chốt có contents dài nhất — đo thật: cú đắt nhất phiên $0.0014). Gói 1 hàm: giờ + hóa đơn + ghi sổ + cộng `totals` (dict truyền THAM CHIẾU — hàm trong ghi, hàm ngoài thấy) rồi trả response Y NGUYÊN (cân hàng, không đóng hàng). `_audit_loop` có 4 đường return → tổng kết đặt trong `finally` = MỘT điểm thoát cho sổ sách, return đường nào (kể cả crash) cũng in. *Chuỗi: cửa ra duy nhất (Ngày 17) → trạm cân duy nhất → điểm thoát duy nhất: dồn về 1 cửa để CODE ép, thay vì nhờ trí nhớ.*
*   💎 **Tam giác chi phí — đo thật (run 20260713-084516, 11 cú gọi, ~$0.0097 ≈ 1 xu/câu audit):** `prompt_tokens` tăng đơn điệu **1,017 → 12,943** (API stateless, nạp lại lịch sử mỗi step); tổng input **92,843 = 7.2× cú cuối** ⇒ tiền phiên ~ **bình phương** số step, KHÔNG phải "token cuối × giá". Hệ quả kiến trúc: `MAX_STEPS` không chỉ là stopping-criteria — nó là **van ngân sách**.
*   💎 **Implicit cache Vertex hiện nguyên hình trong log:** từ step 3, ~**71% input trúng cache** (65,872/92,843 tok — phần lịch sử đầu không đổi giữa các step); nhưng cú chốt `cached_tokens=0` dù contents dài nhất — vì **đổi `config` (tools/tool_config khác) = đổi prefix = phá cache**. Bài học: giữ config ổn định giữa các step là tiền thật. Sổ mình tính cached đủ giá (thực tế giảm ~75%) → số hơi ĐỘI lên = sai về phía an toàn cho ngân sách.
*   **Behavior ghi sổ chờ trị (nhìn thấy NHỜ log):** agent đốt cả 10 step vì đọc-lướt-từng-trang-80-dòng từ ĐẦU file (read_file ×7, không nhảy `start_line` tới dòng grep đã khớp) → bị cú chốt ép nộp; latency step 1 = 6.1s (thinking 253 tok) vs các step sau ~0.7–0.9s. Tuần 4 checklist cần dạy "đọc có địa chỉ" qua docstring.
*   **2 review-fix 7/7 đã trả nợ:** ① nhánh A hết đường thoát text — kết thúc text thường bị dội `EXIT_MSG`, lỳ quá `MAX_REJECTIONS` thì `break` xuống cú chốt mode='ANY' (giờ submit_findings mới THẬT là cửa ra duy nhất, hết 2-luật-đá-nhau); ② `grep` chuẩn hóa `ext` ('JS'/'*.js'/'js' → '.js', so `name.lower()`) — verify 3 dạng cùng ra 21 khớp; trước fix 'JS' = "No matches" = **false negative im lặng** (cùng họ bug `\x08`: tool phòng thủ trước tật đã biết của model).

---

## KIẾN THỨC NGOÀI LỀ TRÌNH — TẦNG XỬ LÝ INPUT (Ingestion)
*(Học từ thảo luận: input thị trường thật là PDF/docx/excel/link/ảnh, không phải text thuần. Đây là tầng đứng TRƯỚC RAG.)*

### Tầng Ingestion / Document Routing
*   **Vấn đề là gì?**
    *   Input thực tế đủ loại định dạng (PDF, docx, excel, link, ảnh). Nhét thẳng vào RAG thì hoặc **hỏng** (đọc sai), hoặc **mất dữ liệu** (không trích được chữ). Sản phẩm không thể bắt user "tự chuyển sang .txt".
*   **Giải pháp là gì?**
    *   Một **router phân loại** từng input → gọi đúng parser: `pymupdf`/`pdfplumber` cho PDF text, OCR (PaddleOCR/Tesseract) cho PDF scan & ảnh, `python-docx` cho .docx, `pandas`/`openpyxl` cho .xlsx, `httpx`+`trafilatura` cho link.
    *   Pipeline: `Input → Router → Parser → Text + metadata → Chunk → Embedding → RAG`. **Luôn giữ metadata nguồn** (tên file, số trang, URL) để sau còn trích dẫn (citation) — thứ làm sản phẩm trông "production".
*   **Khi nào KHÔNG dùng?**
    *   Khi input đã là **text thuần** (repo code `.py`/`.md`) thì bỏ qua tầng này cho nhẹ. Core AI Code Auditor giai đoạn đầu chưa cần — để PDF/OCR/Excel thành **"mở rộng giai đoạn 2"** trong CV.
    *   **Excel KHÔNG embedding thẳng**: bảng số liệu nhét vào vector là vô nghĩa (`#1234` ≈ `#5678`) → đẩy sang **structured query** (pandas/SQL), hoặc convert mỗi dòng thành câu mô tả rồi mới embed.

### OCR như một Fallback có điều kiện (per-page, có threshold)
*   **Vấn đề là gì?**
    *   PDF/docx chia 2 loại: **born-digital** (chữ là text thật, ~90% file thực tế) và **scan/ảnh** (chữ là pixel). OCR mặc định mọi file thì vừa **chậm gấp nhiều lần**, vừa **làm bẩn text** born-digital (OCR đọc "l" thành "1").
*   **Giải pháp là gì?**
    *   **Trích text trước**; chỉ trang nào có độ dài text **< ngưỡng (threshold)** mới đẩy qua OCR. Xét **per-page** chứ không xét cả file (1 PDF có thể trộn 48 trang text + 2 trang scan = **hybrid extraction**).
    *   Dùng **ngưỡng**, không so `== ""` cứng — vì trang scan vẫn lẫn rác (số trang, watermark) nên `if len(text.strip()) < threshold: → OCR; else: dùng text luôn`.
*   **Khi nào KHÔNG dùng?**
    *   PDF/docx **born-digital** đã có text số hóa sẵn — KHÔNG OCR.
    *   Công thức trả lời phỏng vấn cho câu này: **Cách làm (threshold) + Tại sao (OCR mặc định chậm & bẩn text) + Đánh đổi** → đủ 3 vế mới là câu trả lời cấp senior.

---

## KIẾN THỨC NGOÀI LỀ TRÌNH — BEYOND RAG (rà bài nghiên cứu 22/6)
*(Kiến thức để NÓI được + định hướng sau CV — chưa tự build. Chi tiết: `docs/beyond-rag-phase-2.md` + roadmap section "Tích Hợp Beyond-RAG (Tầng 1)".)*

### Bản đồ "Beyond RAG" — naive RAG hết hơi ở đâu, đi tiếp bằng gì
*   **Vấn đề là gì?**
    *   Naive RAG (đúng cái tôi đang xây) có 3 điểm chết: (1) không suy luận đa bước; (2) mất ngữ cảnh toàn cục → trả kém câu hỏi tổng quan; (3) bất lực với **dữ liệu có tính liên kết cao** (quan hệ giữa các thực thể). Tôi đã *tự đo* được hệ quả: recall in-scope 33% (sau khi hoàn tất Q5), "chunk nam châm".
*   **Giải pháp là gì? (mỗi cái trị một bệnh)**
    *   **GraphRAG** — dựng đồ thị thực thể-quan hệ; Local search (lân cận 1 thực thể) + Global search (cộng đồng Leiden + tóm tắt). Trị bệnh *dữ liệu liên kết*. Với CODE = call/import graph → dựng bằng **AST cho rẻ**, chỉ LLM tóm tắt.
    *   **RAPTOR** — cây tóm tắt đệ quy (GMM+UMAP). Trị bệnh *câu hỏi toàn cục*.
    *   **CRAG** — chấm độ tin retrieval, sai thì fallback. Trị bệnh *retrieval trả rác* (đúng bệnh của tôi) → đây là món rẻ đã đưa vào Tầng 1.
    *   **Speculative RAG** — drafter nhỏ song song + verifier lớn → nhanh hơn, giảm position bias. Niche, chỉ cần biết.
*   **Khi nào KHÔNG dùng?**
    *   GraphRAG/RAPTOR có **chi phí dựng index cao** (hàng trăm–nghìn lượt LLM). Trên free tier 20 req/ngày (cháy Ngày 6) là bất khả thi — **nhưng từ 22/6 tôi đã chuyển Vertex AI (paid)** nên **quota hết là rào**, codebase nhỏ của tôi build full index chỉ ~$1–3. ⇒ Rào còn lại thuần là **thời gian/thứ tự học** (build nhiều tuần) → vẫn để **v2 sau CV** (hoặc stretch Tuần 8), KHÔNG phải "không build nổi". Dữ liệu không liên kết / không cần câu toàn cục → RAG/hybrid thường vẫn là lựa chọn nhỏ-nhất-chạy-được (kiềm chế).

### Kinh tế học Long-Context vs RAG (câu phỏng vấn "vàng", 0 dòng code)
*   **Vấn đề là gì?**
    *   Có luồng ý kiến "context 1M token rồi, RAG lỗi thời". Cần phản biện được bằng lý do *vật lý/kinh tế*, không cảm tính.
*   **Giải pháp là gì? (vì sao RAG vẫn sống)**
    *   **Prefill nặng:** self-attention ~O(n²) → nạp 1M token đẩy TTFT lên hàng chục giây, không real-time được.
    *   **KV-cache ngốn VRAM:** tăng phi mã theo độ dài × số user đồng thời. ⚠️ **[Chờ kiểm chứng web]** mốc GB cụ thể trong bài.
    *   **Lost in the middle:** model đọc được nhưng suy luận kém với info giữa context dài (nối tiếp ghi chú Ngày 1).
    *   **Bảo mật:** RAG là *màng lọc* Row-Level Security — loại data trái quyền **trước khi** vào prompt; long-context thuần không làm được.
    *   Kiến trúc lai tối ưu: **hybrid retrieval → rerank → long-context generation**; định tuyến **Self-Route** (thử RAG trước) / **Pre-Route** (model nhỏ quyết trước). ⚠️ **[Chờ kiểm chứng web]** "Pre-Route cắt 80% chi phí".
*   **Khi nào KHÔNG dùng (RAG)?**
    *   Tài liệu nhỏ + ít đổi + 1 user → nhồi thẳng long-context đơn giản hơn, khỏi RAG. Đây vẫn là nguyên tắc xuyên suốt từ Ngày 1.

---

## KIẾN THỨC NGOÀI LỀ TRÌNH — TẦNG MEMORY (Agent có trí nhớ dài hạn)
*(Đối chiếu bản đồ hệ-agent production 29/6: lộ trình phủ kín retrieval + eval — NGÁCH của mình — nhưng thiếu tầng memory đầy đủ. Đây là ô KỀ, ghi để NÓI được + build ở module bổ sung. Chi tiết build: `lo-trinh-chi-tiet.md` mục "MODULE BỔ SUNG — Tầng Memory".)*

### 3 loại Memory + vì sao tách
*   **Vấn đề là gì?** Mỗi lần chạy agent là STATELESS — *"everything inside the box is ephemeral"*, quên sạch sau mỗi lượt. Nhồi hết mọi thứ (lịch sử, hồ sơ user, hướng dẫn) vào 1 context thì tốn token + lost-in-the-middle + lẫn rác.
*   **Giải pháp là gì?** Tách trí nhớ ra NGOÀI thành 3 loại, mỗi loại 1 kho + 1 cách lấy: **Procedural** (cách hành xử / skills → file `Skill.md`), **Semantic** (facts bền + hồ sơ user → vector store, lấy bằng **RAG top-k**), **Episodic** (sự kiện có mốc thời gian + lịch sử chat → **SQL + vector**). Working memory chỉ nạp ĐÚNG phần cần mỗi lượt.
*   **Khi nào KHÔNG dùng?** Tác vụ 1 lượt / không cần nhớ qua phiên → stateless là đủ. Đừng dựng đủ 3 tầng từ đầu — đa số hệ khởi động chỉ cần **semantic (RAG)**; thêm tầng khi *dữ liệu* đòi.

### Episodic: "RAG cho liên quan + SQL cho gần đây" (xác nhận note Ngày 2)
*   **Vấn đề là gì?** Lịch sử hội thoại vừa cần lấy theo NGHĨA ("hồi nãy bàn về thanh toán") vừa cần lấy theo THỜI GIAN ("3 lượt gần nhất"). Một mình embedding làm KHÔNG nổi vế thời gian — embedding mù thứ tự/recency y như mù số (`#1234`≈`#5678`, Ngày 2).
*   **Giải pháp là gì?** Hai kênh: **vector RAG** lấy k lượt LIÊN QUAN + **SQL `ORDER BY timestamp`** lấy m lượt GẦN NHẤT → ghép vào context. Đúng nhánh "RAG for relevance + SQL for recency" trên bản đồ — và là **bằng chứng sống** cho quy tắc "exact/recency → DB, KHÔNG dùng embedding".
*   **Khi nào KHÔNG dùng?** Hội thoại 1 lượt; hoặc khi chỉ cần facts bền (đẩy thẳng sang semantic) chứ không cần lượt thô.

### Consolidation / Summarizer Agent (chống phình episodic)
*   **Vấn đề là gì?** Episodic chứa chat THÔ phình vô hạn → retrieval chậm + nhiễu + vẫn ngốn token. Không giữ mọi lượt mãi được.
*   **Giải pháp là gì?** Sau **N lượt**, một **summarizer agent dùng model RẺ** (flash-lite / DeepSeek) chắt lượt cũ thành **facts bền** đẩy vào semantic memory; lượt thô archive. Dùng model rẻ vì tác vụ dễ (tóm tắt) + chạy nền nhiều lần (tối ưu chi phí — nối bản năng đổi flash-lite Ngày 6).
*   **Khi nào KHÔNG dùng?** Summarize CÓ mất mát — chi tiết nén đi có thể cần lại; chỉ gộp khi lịch sử đủ dài. Cân N: gộp sớm mất chi tiết, muộn thì phình.

---

## TỔNG KẾT TUẦN & TỰ ĐÁNH GIÁ (Hằng tuần)
*(Mỗi tối Chủ Nhật, hãy dành 10 phút trả lời các câu hỏi tự kiểm tra trong lộ trình chi tiết và ghi điểm số của bạn tại đây)*

*   **Tuần 1:** ... / 10 điểm.
    *   *Điều tôi hiểu rõ nhất:* ...
    *   *Chỗ tôi vẫn còn lúng túng cần xem lại:* ...
