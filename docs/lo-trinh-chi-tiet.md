# Lộ Trình Chi Tiết — AI Code Auditor

> **Bắt đầu:** 17/6/2026 (Thứ Ba) · **Mục tiêu:** Nộp CV ~ giữa tháng 8/2026 (≈ 2 tháng)
> **Cấu trúc:** 8.5 tuần — Tuần 1-7 học + xây dự án, **Tuần 8 = buffer chống trễ + luyện phỏng vấn + hoàn thiện CV**
> **Thời gian/ngày:** 5+ giờ · **Dữ liệu thực hành:** repo `chatbot-fanpage` (đã clone tại `C:\Users\Pc\Desktop\chatbot-fanpage`)
> **Cập nhật lần cuối:** 2/7/2026 — **REV lớn** (đóng băng retrieval, bỏ Coursera Tuần 4, thêm Seeded-Bug Benchmark + phễu chi phí 3 tầng, nâng ưu tiên MCP) — xem khối **🔴 REV 2/7** bên dưới

> [!IMPORTANT]
> **Đọc trước khi bắt đầu:** phần [📚 Cách Dùng Tài Liệu + Công Thức Trả Lời Phỏng Vấn](#-cách-dùng-tài-liệu--công-thức-trả-lời-phỏng-vấn) ngay bên dưới. Mỗi ngày học giờ có thêm khối **💬 Đáp án mẫu** để bạn học cách *nói* được kiến thức, không chỉ *hiểu*.

---

## 🔴 Kiểm Tra Lỗi Thời — Những Gì Cần Sửa So Với Lộ Trình Cũ

Sau khi rà soát kỹ thuật tính đến 16/6/2026, có **4 điểm lỗi thời nghiêm trọng** trong lộ trình gốc:

| # | Vấn đề | Mức độ | Cách sửa |
|---|--------|--------|----------|
| 1 | **`google-generativeai` SDK đã bị khai tử** (30/11/2025). File `mini_rag.py` vẫn dùng `import google.generativeai as genai` + `genai.configure()` | 🔴 Chặn | Chuyển sang `google-genai` SDK mới. Dùng `client = genai.Client()` thay `genai.configure()` |
| 2 | **Model `gemini-1.5-flash` thuộc thế hệ cũ**. Gemini 2.0 đã shutdown 1/6/2026. Model hiện tại là `gemini-3.5-flash` | 🔴 Chặn | Đổi model name trong code sang `gemini-3.5-flash` |
| 3 | **`all-MiniLM-L6-v2` vẫn chạy được** nhưng đã bị vượt xa về chất lượng. SOTA 2026: **Qwen3-Embedding** (đa ngữ, RoPE) dẫn đầu; VN chuyên biệt có **halong-embedding, vietnamese-bi-encoder (bkai)**, BGE-M3. Đã có benchmark VN riêng **VN-MTEB** | 🟡 Không chặn | Giữ MiniLM cho tuần 1 (nhẹ, CPU, học). Tuần 2 upgrade + **đo trên golden set tiếng Việt của mình** (không tin leaderboard chung) — xem [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục A8 |
| 4 | **IBM Coursera đã có 10 khóa** (thêm khóa 9: MCP — Model Context Protocol, khóa 10: Capstone). Lộ trình cũ chỉ tính 8 khóa | 🟡 Điều chỉnh | ~~Với 7 ngày trial, chỉ học 4–5 khóa quan trọng nhất~~ **(REV 2/7: BỎ hẳn tuần Coursera — xem khối 🔴 REV bên dưới)** |

> **CẬP NHẬT 17/6/2026 (đã kiểm tra code thật):** `mini_rag.py` **ĐÃ được cập nhật sẵn** sang SDK `google-genai` mới (`from google import genai` + `genai.Client()` + `model="gemini-3.5-flash"`, xem dòng 241-253). Vì vậy buổi chiều Ngày 1 **không cần viết lại SDK** nữa — thay bằng **đọc-hiểu + xác minh chạy được** (so sánh SDK cũ vs mới). Môi trường `venv` cũng đã cài đủ `numpy`, `tiktoken`, `sentence-transformers`, `google-genai`; mắt xích duy nhất còn thiếu là biến môi trường `GEMINI_API_KEY` (set bằng `$env:GEMINI_API_KEY = "..."`).
>
> ✅ **[Đã xác minh 17/6/2026]** Bảng model trong `ban-do-cong-nghe-chi-phi.md` (mục II) đã được cập nhật: "Claude 3.5 Sonnet" → **Claude Sonnet 4.6** ($3/$15); "GPT-4o-mini" → dòng GPT nay là **GPT-5.4** ($2.50/$15); thêm **DeepSeek V3.2** ($0.14/$0.28 — rẻ nhất). **Lưu ý chi phí quan trọng:** `mini_rag.py` đang dùng `gemini-3.5-flash` — model *mới nhất* (19/5/2026) nhưng *đắt nhất họ Flash* ($1.50/$9.00). Cho **học** thì ổn; nhưng sang **vòng lặp agent** (Tuần 3+, gọi LLM nhiều lần) nên đổi sang `gemini-2.5-flash-lite` ($0.10/$0.40) hoặc **DeepSeek V3.2** ($0.14/$0.28) để tiết kiệm (⚠️ `gemini-2.0-flash` đã shutdown 1/6/2026, KHÔNG dùng được nữa).

> [!NOTE]
> **🆕 Track Beyond-RAG (bổ sung 22/6/2026):** sau khi rà bài nghiên cứu *"Beyond RAG"*, đã chắt **7 món Tầng 1** (rẻ, ăn điểm CV) gấp vào lộ trình — xem section cuối file [🆕 Tích Hợp Beyond-RAG (Tầng 1)](#-tích-hợp-beyond-rag-tầng-1). Phần nặng cấp Enterprise (GraphRAG/RAPTOR/vLLM) để ở doc riêng [beyond-rag-phase-2.md](beyond-rag-phase-2.md) — track *sau CV*.

> [!IMPORTANT]
> **🔴 REV 2/7/2026 — rà soát nghiêm túc + tra web (SOTA & nghiên cứu tuyển dụng 2026), 5 thay đổi lớn:**
>
> 1. **ĐÓNG BĂNG retrieval ở precision@3 = 60%** (Ngày 9–15 đã xong vai trò). Lý do đã kiểm chứng: ngành chuyển sang **agentic search** (grep/read loop) cho code — chính Claude Code bỏ vector DB (5/2025, Boris Cherny: *"agentic search generally works better"*); top SWE-bench 2026 không hệ nào dùng vector retrieval trên repo đích. Lỗi verifySig/RBAC của ta đúng lớp lỗi grep trị tận gốc. RAG giữ làm **1 tool ngữ nghĩa** trong agent. **Backlog (không xếp lịch):** Voyage instruction-following reranker, query VN→EN, mở rộng golden set retrieval. **Câu chuyện phỏng vấn:** *"tôi tự đo được giới hạn dense retrieval trên code → đó là lý do ngành chuyển sang agentic search"*.
> 2. **BỎ hẳn Tuần 4 Coursera** (cert = tín hiệu yếu 2026 so với dự án ship + eval) → thay bằng **Auditor v1 + Seeded-Bug Benchmark** (xem TUẦN 4 mới). LangGraph/MCP học qua docs chính thức 30–60'/tối.
> 3. **Định vị lại sản phẩm:** auditor **XUẤT BÁO CÁO FINDINGS** (schema JSON, citation file:line), KHÔNG phải Q&A trên code. Thước đo chính của CV = **detection recall + false-positive rate trên repo cấy lỗi** ("spiked repository" — phương pháp chuẩn ngành 2026), thay vai precision@3.
> 4. **MCP nâng ưu tiên:** từ 7/2026 MCP là chuẩn ngành (Linux Foundation; OpenAI/Google/Microsoft đồng bảo trợ; 97M SDK downloads/tháng; 41% doanh nghiệp production) → expose auditor như **MCP server** ở Tuần 5, KHÔNG còn nằm đầu danh sách cắt.
> 5. **Thị trường mục tiêu: công ty VN product + AI startup** → CV song ngữ, **README tiếng Anh**, **Streamlit UI + demo chạy được** (Tuần 6). AWS giữ mức đọc-hiểu 30'/tối, không tăng.

---

## Cài Đặt Trước Khi Bắt Đầu (Làm tối 16/6)

```bash
# 1. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate        # Windows

# 2. Cài thư viện (ĐÃ CẬP NHẬT cho 6/2026)
pip install sentence-transformers numpy google-genai tiktoken

# 3. Auth — CHỌN 1 backend (PowerShell). call_gemini trong mini_rag.py là dual-mode:
#   (A) AI Studio — free tier, đơn giản:
$env:GEMINI_API_KEY = "your_key_here"
#   (B) Vertex AI — paid GCP, KHÔNG dính trần 20 req/ngày (đang dùng từ 22/6/2026):
$env:GOOGLE_GENAI_USE_VERTEXAI = "True"
$env:GOOGLE_CLOUD_PROJECT      = "project-id-cua-ban"
$env:GOOGLE_CLOUD_LOCATION     = "us-central1"
#   Vertex cần chạy 1 lần: gcloud auth application-default login   (tạo ADC)

# 4. Test nhanh SDK hoạt động — genai.Client() KHÔNG tham số, tự đọc env ở bước 3
python -c "from google import genai; c = genai.Client(); print(c.models.generate_content(model='gemini-2.5-flash-lite', contents='Hello').text)"
```

---

## 📚 Cách Dùng Tài Liệu + Công Thức Trả Lời Phỏng Vấn

Tài liệu này không chỉ để *làm theo*, mà để *học cách nói lại*. Nhà tuyển dụng Intern/Junior AI không kỳ vọng bạn biết mọi thứ — họ kiểm tra **bạn có hiểu bản chất và giải thích được không**. Vì vậy mỗi ngày có thêm khối **💬 Đáp án mẫu**: câu hỏi + một câu trả lời viết sẵn để bạn luyện *nói*.

### Công thức 1 — Trả lời câu hỏi KHÁI NIỆM (dùng "3 câu bản chất")

Khi được hỏi *"X là gì / vì sao dùng X"*, trả lời theo đúng 3 nhịp này (15-30 giây là đủ):

> **(1) Vấn đề:** "Nếu không có X thì ta gặp vấn đề..."
> **(2) Giải pháp:** "X giải quyết bằng cách..."
> **(3) Đánh đổi / khi nào KHÔNG dùng:** "Nhưng X không phù hợp khi..., lúc đó tôi sẽ dùng..."

👉 Câu thứ (3) là thứ tách **người hiểu bản chất** khỏi **người học vẹt**. Hầu hết ứng viên chỉ nói được (1) và (2). Luôn cố gắng có câu (3).

### Công thức 2 — Trả lời câu hỏi VỀ DỰ ÁN (dùng cấu trúc "Bài toán → Lựa chọn → Kết quả")

Khi được hỏi *"kể về dự án của bạn / bạn làm gì ở đây"*:

> **Bài toán:** mình cần giải quyết gì, ràng buộc gì (dữ liệu, chi phí, thời gian).
> **Lựa chọn & lý do:** mình chọn công nghệ/cách làm nào, **và vì sao không chọn cái khác**.
> **Kết quả + số liệu:** đạt được gì, đo bằng con số (precision@3, latency, chi phí/query).

👉 Số liệu là vũ khí mạnh nhất của fresher. "Precision@3 tăng từ 60% lên 78% sau khi đổi embedding model" đáng giá gấp 10 lần "em có làm RAG".

### Quy ước ký hiệu trong tài liệu
- **💬 Đáp án mẫu:** câu trả lời phỏng vấn viết sẵn để học thuộc *cách nói* (không phải học vẹt từng chữ — hiểu rồi diễn đạt lại bằng lời mình).
- **⏸️ Dừng 30 giây:** câu hỏi tự kiểm trước khi chạy code.
- ⚠️ **[Chờ kiểm chứng web]:** số liệu/tên model cần soát lại khi có mạng.

> **Mẹo luyện nói:** mỗi cuối tuần, mở các khối 💬 của tuần đó, che phần đáp án, tự trả lời thành tiếng (hoặc quay video 3-5 phút). Tuần 8 sẽ gom tất cả thành một buổi mô phỏng phỏng vấn.

---

## TUẦN 1: RAG Tự Tay (Không Framework)

> [!TIP]
> **Tài liệu tham khảo System Design:** Trước khi bắt đầu Tuần 1, hãy đọc kỹ Phần I và V của [Bản Đồ Quyết Định Công Nghệ & Chi Phí](file:///c:/Users/Pc/Desktop/Build%20CV/ai-code-auditor/docs/ban-do-cong-nghe-chi-phi.md) để nắm được các cấp độ kiến trúc RAG và cách đọc code mẫu từ các dự án tham khảo.

**Mục tiêu tuần:** Tự viết từng bước RAG pipeline, hiểu input/output mỗi bước, giải thích được cho người khác.

> 🧭 **Góc Architect (song song, 30 phút/tối):** đọc [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A2 Chunking · A3 Embedding · A4 Retrieval · A5 Grounding** — tập trung khối 🚩 và 🔍 để biết AI hay sai gì khi sinh code các bước này.

---

### Ngày 1 (Thứ Ba 17/6) — Token, Context Window & Cập nhật SDK

**Thời gian:** 5h · **Track:** Code tay

#### Buổi sáng (2.5h): Hiểu Token & Context Window

**Bài toán gốc:** Máy không hiểu chữ, cần chuyển thành số (token). Mỗi lần gọi model chỉ "nhìn" được một lượng token giới hạn (context window).

**Thực hành:**
```python
# test_token.py
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# 1. So sánh tiếng Việt vs tiếng Anh
vi = "Xác thực chữ ký webhook từ Facebook bằng HMAC-SHA256"
en = "Verify webhook signature from Facebook using HMAC-SHA256"

vi_tokens = enc.encode(vi)
en_tokens = enc.encode(en)

print(f"Tiếng Việt: {len(vi_tokens)} tokens -> {vi_tokens}")
print(f"Tiếng Anh:  {len(en_tokens)} tokens -> {en_tokens}")

# 2. Đo kích thước file thật
with open("path/to/chatbot-fanpage/core/rules.js", "r", encoding="utf-8") as f:
    rules_text = f.read()
print(f"\nrules.js: {len(enc.encode(rules_text))} tokens")
print(f"Gemini 3.5 Flash context window: 1,048,576 tokens")
print(f"Tỉ lệ chiếm: {len(enc.encode(rules_text))/1048576*100:.2f}%")
```

**Kết quả kỳ vọng:**
- Tiếng Việt tốn ~2x token so với tiếng Anh cho cùng nội dung (do dấu, từ ghép)
- `rules.js` (~50KB) khoảng 12,000–15,000 tokens, vừa trong context window
- Nhưng cả `core/` + `docs/` (~2.4MB) khoảng 600,000+ tokens, gần giới hạn và **tốn tiền**

#### Buổi chiều (2.5h): Cập nhật `mini_rag.py` sang SDK mới

Sửa hàm `call_gemini` trong `mini_rag.py`:

```python
# CŨ (đã khai tử, SẼ LỖI):
# import google.generativeai as genai
# genai.configure(api_key=api_key)
# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content(prompt)

# MỚI (google-genai SDK, 6/2026):
def call_gemini(prompt):
    from google import genai
    import os

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set the GEMINI_API_KEY environment variable first")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    return response.text
```

Sửa `pip install` trong docstring:
```
# CŨ: pip install sentence-transformers google-generativeai numpy
# MỚI: pip install sentence-transformers google-genai numpy
```

#### Tự kiểm cuối ngày

Viết 3–4 câu trả lời (KHÔNG dùng AI):

1. **Nếu context window vô hạn và miễn phí, RAG còn cần không?**
   - *Gợi ý đáp án:* Vẫn có giá trị trong 2 trường hợp: (1) dữ liệu thay đổi liên tục — nhồi hết vào prompt mỗi lần gọi thì lãng phí, retrieval chỉ lấy phần liên quan; (2) "needle in haystack" — context quá dài thì model dễ bỏ sót thông tin ở giữa. Nhưng nếu tài liệu nhỏ + ít thay đổi thì nhồi thẳng (stuffing) đơn giản hơn, không cần RAG.

2. **Vì sao tiếng Việt tốn nhiều token hơn?**
   - *Gợi ý:* Tokenizer được train chủ yếu trên dữ liệu tiếng Anh, từ tiếng Anh phổ biến được gộp thành 1 token, tiếng Việt bị tách nhỏ hơn (từng âm tiết, dấu riêng).

> #### 💬 Đáp án mẫu phỏng vấn — Ngày 1
>
> **Hỏi: "Context window là gì, và vì sao nó ảnh hưởng tới cách bạn thiết kế một hệ thống RAG?"**
>
> *"Context window là lượng token tối đa mà model xử lý được trong một lần gọi — ví dụ Gemini 3.5 Flash khoảng 1 triệu token. **Vấn đề** là nó hữu hạn và mỗi token đều tốn tiền, nên ta không thể cứ nhồi cả codebase vào prompt mỗi lần hỏi: vừa đắt, vừa khiến model dễ bỏ sót thông tin nằm giữa đoạn dài (hiện tượng 'lost in the middle'). **Giải pháp** là RAG — chỉ lấy ra vài đoạn liên quan nhất tới câu hỏi rồi đưa vào context, thay vì đưa hết. **Đánh đổi:** nếu tài liệu nhỏ và ít thay đổi thì nhồi thẳng (stuffing) lại đơn giản hơn, không cần RAG. Tôi chỉ dùng RAG khi dữ liệu lớn hoặc thay đổi liên tục."*
>
> **Hỏi nhanh: "Vì sao tiếng Việt thường tốn nhiều token hơn tiếng Anh?"**
>
> *"Vì tokenizer được huấn luyện chủ yếu trên dữ liệu tiếng Anh, nên từ tiếng Anh phổ biến được gộp gọn thành 1 token, còn tiếng Việt bị tách nhỏ thành nhiều mảnh (âm tiết, dấu). Thực tế cùng một nội dung, tiếng Việt thường tốn gấp ~2 lần — điều này ảnh hưởng trực tiếp tới chi phí khi làm sản phẩm cho người dùng Việt."*

---

### Ngày 2 (Thứ Tư 18/6) — Embedding: Tìm Theo Nghĩa

**Thời gian:** 5h · **Track:** Code tay

#### Buổi sáng (2.5h): Quan sát embedding bằng mắt

**Bài toán:** Tìm kiếm keyword (substring) thất bại khi người hỏi dùng từ khác nhưng cùng nghĩa.
**Giải pháp:** Biến text thành vector số, sao cho nghĩa gần thì vector gần.

```python
# test_embedding.py
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "kiểm tra chữ ký webhook",                    # 0
    "verify signature from Facebook",              # 1 - đồng nghĩa với 0
    "mã hoá credential bằng AES-256-GCM",          # 2
    "encrypt tokens using AES Galois Counter Mode", # 3 - đồng nghĩa với 2
    "cách nấu phở bò Hà Nội",                      # 4 - không liên quan
    "thời tiết hôm nay thế nào",                   # 5 - không liên quan
]

embeddings = model.encode(sentences)

print(f"Số chiều vector: {embeddings.shape[1]}")   # Kỳ vọng: 384
print(f"Kích thước mảng: {embeddings.shape}")      # Kỳ vọng: (6, 384)

# In 5 số đầu của mỗi vector
for i, s in enumerate(sentences):
    print(f"[{i}] {s[:40]:40s} -> {embeddings[i][:5]}")
```

**Kết quả kỳ vọng:**
- Vector có 384 chiều (MiniLM-L6-v2 = 384)
- Nhìn bằng mắt thì 5 số đầu KHÔNG cho thấy rõ cặp nào "gần", đó là lý do cần cosine similarity ở ngày 3

#### Buổi chiều (2.5h): Thí nghiệm giới hạn embedding

```python
# Thêm vào cuối test_embedding.py

# Test giới hạn: embedding có hiểu số chính xác không?
extra = [
    "đơn hàng #1234 trạng thái gì",     # 6
    "đơn hàng #5678 trạng thái gì",     # 7 - khác số nhưng cùng pattern
    "order status for order number 1234", # 8
]

extra_emb = model.encode(extra)

from numpy.linalg import norm

def quick_cosine(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

print(f"\n#1234 vs #5678 (khác số):  {quick_cosine(extra_emb[0], extra_emb[1]):.4f}")
print(f"#1234 vi vs #1234 en:      {quick_cosine(extra_emb[0], extra_emb[2]):.4f}")
```

**Kết quả kỳ vọng:** Cả 3 cặp đều có similarity CAO (~0.8–0.95) — embedding hiểu "pattern hỏi trạng thái đơn hàng" nhưng KHÔNG phân biệt được #1234 vs #5678.

#### Tự kiểm cuối ngày
1. **Embedding có giúp tìm đúng đơn #1234 không?**
   - *Đáp án:* Không. Embedding bắt ý nghĩa ngữ cảnh (semantic), không khớp chính xác (exact match). Để tìm đúng #1234, dùng DB query hoặc keyword search.

2. **Khi nào dùng embedding, khi nào dùng keyword search?**
   - *Đáp án:* Embedding khi người dùng diễn đạt khác nhưng cùng ý. Keyword/DB query khi cần khớp chính xác: mã đơn, số điện thoại, tên hàm cụ thể.

> #### 💬 Đáp án mẫu phỏng vấn — Ngày 2
>
> **Hỏi: "Embedding là gì? Khi nào dùng embedding, khi nào dùng keyword search?"**
>
> *"Embedding là cách biến một đoạn text thành một vector số nhiều chiều, sao cho hai đoạn **gần nghĩa** thì hai vector **gần nhau** trong không gian. **Vấn đề** nó giải quyết: tìm kiếm bằng từ khóa (substring) thất bại khi người dùng diễn đạt khác từ nhưng cùng ý — ví dụ hỏi 'kiểm tra chữ ký' nhưng code ghi 'verify signature'. **Giải pháp:** so khớp theo vector ngữ nghĩa thay vì theo ký tự. **Đánh đổi:** embedding bắt *ý nghĩa* chứ không khớp *chính xác* — nó không phân biệt được đơn hàng #1234 với #5678, vì hai câu đó gần như cùng pattern. Nên khi cần khớp chính xác (mã đơn, số điện thoại, tên hàm), tôi dùng keyword search hoặc truy vấn DB; còn khi cần tìm theo ý, tôi dùng embedding. Hệ thống thật thường kết hợp cả hai gọi là hybrid search."*

---

### Ngày 3 (Thứ Năm 19/6) — Cosine Similarity: Tự Viết Bằng Tay

**Thời gian:** 5h · **Track:** Code tay

#### Buổi sáng (2.5h): Implement cosine_similarity

Mở `mini_rag.py`, implement hàm `cosine_similarity`:

```python
def cosine_similarity(vec_a, vec_b):
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)
```

**Test ngay (đừng đợi implement hết rồi mới test):**

```python
# test_cosine.py
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "kiểm tra chữ ký webhook",
    "verify signature from Facebook",
    "cách nấu phở bò Hà Nội",
    "mã hoá credential bằng AES",
    "encrypt tokens using AES GCM",
]

emb = model.encode(sentences)

def cosine_similarity(a, b):
    dot = np.dot(a, b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

# In ma trận similarity
print("Ma trận Cosine Similarity:")
for i in range(len(sentences)):
    for j in range(len(sentences)):
        score = cosine_similarity(emb[i], emb[j])
        print(f" {score:.3f} ", end="")
    print(f"  <- [{i}] {sentences[i][:35]}")
```

**Kết quả kỳ vọng:** Cặp đồng nghĩa (0-1, 3-4) có similarity cao hơn rõ rệt. "Nấu phở" vs mọi câu khác rất thấp.

#### Buổi chiều (2.5h): So sánh Cosine vs Euclidean

```python
# Câu dài vs câu ngắn cùng nghĩa
long_sentence = "Hệ thống xác thực và kiểm tra chữ ký số webhook được gửi từ nền tảng Facebook Messenger thông qua thuật toán HMAC-SHA256 với khóa bí mật"
short_sentence = "verify webhook signature"

long_emb = model.encode([long_sentence])[0]
short_emb = model.encode([short_sentence])[0]

cos_score = cosine_similarity(long_emb, short_emb)
euc_dist = np.linalg.norm(long_emb - short_emb)

print(f"Cosine similarity: {cos_score:.4f}")
print(f"Euclidean distance: {euc_dist:.4f}")
print(f"\n-> Cosine chỉ đo 'hướng' (góc), không quan tâm 'độ dài'")
print(f"-> Euclidean bị ảnh hưởng bởi magnitude")
```

#### Tự kiểm cuối ngày
1. **Cosine similarity 0.7 là "gần" hay "xa"?** — Không có ngưỡng tuyệt đối. Phụ thuộc model, dataset, domain. Phải thử nghiệm trên dữ liệu thật.
2. **Vì sao dùng cosine thay vì Euclidean?** — Cosine đo góc, bỏ qua magnitude. 2 câu cùng nghĩa khác độ dài vẫn cho score cao.

> #### 💬 Đáp án mẫu phỏng vấn — Ngày 3
>
> **Hỏi: "Cosine similarity và Euclidean distance khác nhau thế nào? Vì sao RAG hay dùng cosine?"**
>
> *"Cả hai đều đo độ giống nhau giữa hai vector, nhưng theo cách khác nhau. **Euclidean** đo *khoảng cách thẳng* giữa hai điểm — nó bị ảnh hưởng bởi độ lớn (magnitude) của vector. **Cosine** đo *góc* giữa hai vector, tức là 'hướng' của chúng, bỏ qua độ dài. **Vì sao RAG chuộng cosine:** một câu ngắn và một đoạn dài cùng nói về một chủ đề sẽ có magnitude rất khác nhau, nên Euclidean báo 'xa'; nhưng hướng của chúng giống nhau, nên cosine vẫn báo 'gần' — đúng với điều ta muốn. **Lưu ý quan trọng:** không có ngưỡng cosine 'đúng' tuyệt đối — 0.7 là gần hay xa còn tùy model và dữ liệu, nên phải đo trên tập test thật chứ không đoán."*
>
> **Hỏi sâu thêm: "Bạn tự viết cosine bằng tay, công thức ra sao?"**
>
> *"`cos = (A·B) / (||A|| × ||B||)` — tử số là tích vô hướng (dot product), mẫu số là tích hai độ dài L2. Tôi nhớ chắn chia cho 0: nếu một vector có norm bằng 0 thì trả về 0.0 thay vì để lỗi."*

---

### Ngày 4 (Thứ Sáu 20/6) — Chunking: Cắt Code Mà Không Phá Ngữ Cảnh

**Thời gian:** 5h · **Track:** Code tay

#### Buổi sáng (3h): Implement `chunk_text` trong `mini_rag.py`

```python
def chunk_text(file_dict):
    path = file_dict["path"]
    text = file_dict["text"]
    chunks = []
    
    if path.endswith(".md"):
        # A) Markdown: tách theo heading
        parts = re.split(r'(?m)^(#{1,6} .+)$', text)
        current = parts[0].strip()
        i = 1
        while i < len(parts):
            heading = parts[i]
            body = parts[i + 1] if i + 1 < len(parts) else ""
            section = (heading + "\n" + body).strip()
            if section:
                chunks.append(section)
            i += 2
        if current:
            chunks.insert(0, current)
    
    elif path.endswith(".js"):
        # B) JavaScript: tách theo khai báo hàm/route
        pattern = r'(?m)^(?:(?:async\s+)?function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(|router\.(?:get|post|put|delete|patch)\(|app\.(?:get|post|put|delete|patch)\(|module\.exports)'
        boundaries = [m.start() for m in re.finditer(pattern, text)]
        
        if boundaries:
            if boundaries[0] > 0:
                preamble = text[:boundaries[0]].strip()
                if preamble:
                    chunks.append(preamble)
            for idx, start in enumerate(boundaries):
                end = boundaries[idx + 1] if idx + 1 < len(boundaries) else len(text)
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
        else:
            chunks.append(text)
    else:
        chunks.append(text)
    
    # C) FALLBACK: tách chunk quá dài
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > FALLBACK_CHUNK_SIZE * 2:
            for i in range(0, len(chunk), FALLBACK_CHUNK_SIZE):
                piece = chunk[i:i + FALLBACK_CHUNK_SIZE].strip()
                if piece:
                    final_chunks.append(piece)
        else:
            final_chunks.append(chunk)
    
    return [
        {"path": path, "chunk_id": i, "content": c}
        for i, c in enumerate(final_chunks)
    ]
```

#### Buổi chiều (2h): Test trên file thật

```python
# test_chunking.py
from mini_rag import chunk_text

with open("path/to/chatbot-fanpage/DESIGN.md", "r", encoding="utf-8") as f:
    md_file = {"path": "DESIGN.md", "text": f.read()}

md_chunks = chunk_text(md_file)
print(f"DESIGN.md -> {len(md_chunks)} chunks")
for c in md_chunks:
    print(f"  chunk {c['chunk_id']}: {len(c['content'])} chars | {c['content'][:80]}...")
```

**Kiểm tra:** Mỗi chunk có phải một "đơn vị" có nghĩa? Có chunk nào bị cắt giữa hàm không?

#### Tự kiểm cuối ngày
- **Nếu tăng chunk lên bằng cả file, retrieval còn cần không?** — Nếu chỉ có 1 chunk = cả file thì retrieval luôn trả về toàn bộ, đúng bằng stuffing. RAG chỉ có giá trị khi chunk đủ nhỏ để retrieval "lọc" ra phần liên quan, nhưng đủ lớn để giữ ngữ cảnh.

> #### 💬 Đáp án mẫu phỏng vấn — Ngày 4
>
> **Hỏi: "Chunking là gì? Chunk to và chunk nhỏ ảnh hưởng thế nào tới chất lượng RAG?"**
>
> *"Chunking là bước cắt tài liệu thành những mảnh nhỏ trước khi embed và lưu. **Vấn đề:** nếu để nguyên cả file làm một đơn vị, retrieval sẽ luôn trả về toàn bộ file — không khác gì nhồi thẳng, và tốn context. Nếu cắt quá vụn (vd giữa thân một hàm), mỗi mảnh mất ngữ cảnh nên model không hiểu. **Giải pháp:** cắt theo *ranh giới có nghĩa* — file Markdown cắt theo heading, file JS cắt theo ranh giới hàm/route — để mỗi chunk là một đơn vị tự đủ nghĩa. **Đánh đổi:** chunk **to** giữ nhiều ngữ cảnh nhưng làm retrieval kém chính xác (lẫn nhiều thông tin thừa) và tốn token; chunk **nhỏ** chính xác hơn nhưng dễ mất ngữ cảnh. Tôi luôn có một bước fallback cắt theo số ký tự cố định cho những đoạn quá dài, để không bao giờ lọt một chunk khổng lồ làm hỏng bước embedding."*

---

### Ngày 5 (Thứ Bảy 21/6) — Ráp Pipeline End-to-End

**Thời gian:** 5h · **Track:** Code tay

#### Buổi sáng (3h): Implement `retrieve_top_k` + `build_prompt`

**`retrieve_top_k`:**
```python
def retrieve_top_k(query_embedding, index, k=TOP_K):
    scored = []
    for i in range(len(index["chunks"])):
        score = cosine_similarity(query_embedding, index["embeddings"][i])
        chunk_copy = dict(index["chunks"][i])
        chunk_copy["score"] = float(score)
        scored.append(chunk_copy)
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]
```

**`build_prompt`:**
```python
def build_prompt(question, retrieved_chunks):
    context_parts = []
    for c in retrieved_chunks:
        context_parts.append(
            f"--- File: {c['path']} | Chunk {c['chunk_id']} | Relevance: {c['score']:.3f} ---\n"
            f"{c['content']}\n"
        )
    context_text = "\n".join(context_parts)
    
    prompt = f"""Bạn là trợ lý chuyên phân tích codebase. Trả lời câu hỏi DUY NHẤT dựa trên context bên dưới.

NGUYÊN TẮC BẮT BUỘC:
1. Chỉ dùng thông tin từ context. KHÔNG bịa thêm code, hàm, hoặc logic không có trong context.
2. Nếu context không chứa thông tin liên quan, trả lời "Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp."
3. Khi trích dẫn, ghi rõ file và chunk number.

CONTEXT:
{context_text}

CÂU HỎI: {question}

TRẢ LỜI:"""
    return prompt
```

#### Buổi chiều (2h): Chạy pipeline lần đầu

```bash
python mini_rag.py path/to/chatbot-fanpage
```

Test 3 câu hỏi:
1. "verifySignature hoạt động ra sao?" — phải trả lời đúng, trích chunk từ webhook.js
2. "credential được mã hoá thế nào?" — trích chunk từ credentials/
3. "module thanh toán Stripe hoạt động thế nào?" — phải từ chối vì KHÔNG có Stripe trong codebase

> #### 💬 Đáp án mẫu phỏng vấn — Ngày 5
>
> **Hỏi: "Hãy mô tả luồng từ lúc người dùng đặt câu hỏi đến lúc nhận câu trả lời trong hệ thống RAG của bạn."**
>
> *"Có hai pha. **Pha index (làm một lần):** đọc file → chunk theo ranh giới có nghĩa → embed mỗi chunk thành vector → lưu chunk kèm vector vào kho. **Pha truy vấn (mỗi câu hỏi):** embed câu hỏi → tính cosine similarity giữa vector câu hỏi với từng chunk → lấy top-K chunk điểm cao nhất → ghép chúng cùng câu hỏi thành một prompt → gửi cho Gemini → in câu trả lời. Điểm mấu chốt ở bước ghép prompt là tôi ra lệnh rõ cho model **chỉ được trả lời dựa trên context cung cấp, nếu không có thì phải nói không biết** — đây là rào chắn chống bịa (hallucination)."*
>
> **Hỏi sâu: "Vì sao bạn cho mỗi chunk kèm theo file path và chunk_id trong prompt?"**
>
> *"Để **truy vết** — khi model trả lời, tôi biết nó dựa trên đoạn nào, file nào. Vừa để debug 'vì sao nó trả lời thế', vừa để hiển thị citation cho người dùng tin tưởng. Đây là kỹ năng dùng liên tục khi làm sản phẩm LLM thật."*

---

### Ngày 6 (Chủ Nhật 22/6) — Stress-Test Hallucination + Viết NOTES.md

**Thời gian:** 5h · **Track:** Áp dụng

#### Buổi sáng (3h): Test 10 câu hỏi có chuẩn bị

| # | Câu hỏi | Có trong code? | Kỳ vọng |
|---|---------|---------------|---------|
| 1 | "verifySignature dùng thuật toán gì?" | Có | HMAC-SHA256, timingSafeEqual |
| 2 | "credential encryption dùng mode gì?" | Có | AES-256-GCM |
| 3 | "lead parser hoạt động thế nào?" | Có | Trích xuất tên/SĐT/địa chỉ từ tin nhắn |
| 4 | "multi-shop isolation hoạt động ra sao?" | Có | Tách config theo shops/SHOP_ID |
| 5 | "RBAC có mấy vai trò?" | Có | 4: viewer/support/maintainer/owner |
| 6 | "module thanh toán Stripe?" | Không | Từ chối |
| 7 | "tích hợp với Zalo OA?" | Không | Từ chối |
| 8 | "database dùng MongoDB?" | Không | Từ chối, dùng PostgreSQL |
| 9 | "có dùng Redis cache không?" | Không | Từ chối |
| 10 | "unit test framework là gì?" | Có | Node built-in test runner hoặc Jest |

**Ghi lại kết quả:** Bao nhiêu câu trả lời đúng? Bao nhiêu câu bịa? Đây là baseline cho tuần 2 khi đo precision.

#### Buổi chiều (2h): Viết `NOTES.md`

Với mỗi khái niệm (token, embedding, cosine, chunking, retrieval, prompt-grounding), viết 3–4 câu theo công thức:
- **Vấn đề là...** (bài toán gốc nếu không có khái niệm này)
- **Giải pháp là...** (cách khái niệm giải quyết)
- **Không dùng khi...** (giới hạn / trường hợp không phù hợp)

File này dùng lại ở tuần 7 để luyện nói trước phỏng vấn.

> #### 💬 Đáp án mẫu phỏng vấn — Ngày 6
>
> **Hỏi: "Hallucination là gì? Nếu model bịa thông tin, bạn debug và giảm thiểu thế nào?"**
>
> *"Hallucination là khi model trả lời nghe rất tự tin nhưng sai hoặc bịa thông tin không có trong dữ liệu. **Cách giảm thiểu trong RAG:** (1) ràng buộc trong prompt — yêu cầu model *chỉ* dùng context được cung cấp và phải nói 'không tìm thấy' nếu thiếu thông tin; (2) cải thiện retrieval — nếu lấy nhầm chunk thì model trả lời sai từ gốc, nên tôi đo precision của bước retrieval; (3) hiển thị citation để con người kiểm chứng. **Cách debug khi nghi bịa:** việc đầu tiên tôi làm là **in ra đúng prompt** đã gửi cho model và xem các chunk được truyền vào — thường lỗi nằm ở retrieval lấy sai chunk, chứ không phải model 'ngu'. Tôi cũng cố tình test bằng câu hỏi off-topic (vd hỏi về Stripe trong khi codebase không có) để xác nhận rào chắn hoạt động."*
>
> 👉 *Đây là câu nhà tuyển dụng RẤT hay hỏi — vì nó cho thấy bạn từng làm sản phẩm thật, không chỉ chạy demo.*

---

### Ngày 7 (Thứ Hai 23/6) — Ôn lại + Bài tập tương tự

**Thời gian:** 5h · **Track:** Áp dụng

#### Buổi sáng (2h): Bài tập tương tự — RAG trên tài liệu Markdown

Tạo file `exercise_rag_markdown.py`: Build RAG pipeline tương tự nhưng chỉ cho thư mục `docs/` của chatbot-fanpage (toàn file .md). So sánh kết quả với pipeline đầy đủ (cả code + docs). Câu hỏi: "khi nào retrieval trên docs tốt hơn retrieval trên code?"

#### Buổi chiều (3h): Review toàn bộ tuần 1

1. Chạy lại pipeline end-to-end, đảm bảo mọi thứ hoạt động
2. Đọc to NOTES.md cho chính mình (hoặc quay video 3–5 phút giải thích RAG pipeline)
3. Commit tất cả code lên git

**Deliverable tuần 1:** Pipeline RAG thủ công chạy được, NOTES.md, video/ghi âm giải thích.

---

## TUẦN 2: Vector DB Thật + Đánh Giá Định Lượng

> [!TIP]
> **Tài liệu tham khảo:** Đọc Phần I & Phần V của [Bản Đồ Quyết Định Công Nghệ & Chi Phí](file:///c:/Users/Pc/Desktop/Build%20CV/ai-code-auditor/docs/ban-do-cong-nghe-chi-phi.md) để hiểu cách hoạt động của Persistent Vector DB (SQLite / ChromaDB) và cách Ingest dữ liệu hiệu quả tránh trùng lặp.

**Mục tiêu tuần:** Chuyển từ list Python sang vector DB, bắt đầu đo precision, có số liệu thật cho CV.

> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A4 Hybrid · B1 Evaluation · B3 chọn Vector DB** — gắn với việc đo precision@3 và migrate ChromaDB tuần này.

---

### Ngày 8 (Thứ Ba 24/6) — Cài ChromaDB, migrate storage

**Thời gian:** 5h · **Track:** Code tay

```bash
pip install chromadb
```

Viết `chroma_rag.py` — copy từ `mini_rag.py` nhưng thay phần lưu trữ:

```python
import chromadb

client = chromadb.Client()  # in-memory, local
collection = client.create_collection("code_chunks")

# Insert
collection.add(
    documents=[c["content"] for c in all_chunks],
    metadatas=[{"path": c["path"], "chunk_id": c["chunk_id"]} for c in all_chunks],
    ids=[f"{c['path']}_{c['chunk_id']}" for c in all_chunks],
)

# Query (Chroma tự embed + tính similarity)
results = collection.query(query_texts=[question], n_results=TOP_K)
```

**So sánh:** Kết quả top-3 từ Chroma có khớp với bản tự viết `mini_rag.py` không?

---

### Ngày 9 (Thứ Tư 25/6) — Đo Precision@3

**Thời gian:** 5h · **Track:** Code tay

Tạo bộ 15 câu hỏi test kèm "chunk đúng" đã biết trước (golden answers):

```python
# eval_set.py
EVAL_SET = [
    {
        "question": "verifySignature dùng thuật toán gì?",
        "expected_files": ["webhook.js"],
        "expected_keywords": ["HMAC", "SHA256", "timingSafeEqual"],
    },
    # ... thêm 14 câu nữa
]

# Script đo precision
correct = 0
for item in EVAL_SET:
    top_chunks = retrieve_top_k(embed(item["question"]), index)
    hit = any(
        any(kw.lower() in c["content"].lower() for kw in item["expected_keywords"])
        for c in top_chunks
    )
    if hit:
        correct += 1
    else:
        print(f"MISS: {item['question']}")

print(f"\nPrecision@3: {correct}/{len(EVAL_SET)} = {correct/len(EVAL_SET)*100:.1f}%")
```

**Mục tiêu:** >= 60% precision@3 với MiniLM. Đây là baseline cho so sánh khi upgrade model.

---

### Ngày 10 (Thứ Năm 26/6) — Thử embedding model tốt hơn

**Thời gian:** 5h · **Track:** Code tay

```python
# Thử embedding mạnh hơn MiniLM rất nhiều.
# Lựa chọn 1 — BGE-M3 (multilingual, ổn định, ~2GB):
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-m3")

# Lựa chọn 2 (KHUYÊN DÙNG nếu máy đủ khoẻ) — Qwen3-Embedding:
#   Dẫn đầu đa ngôn ngữ 2026 (RoPE + model lớn), rất mạnh cho tiếng Việt.
#   model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")  # bản nhỏ, nhẹ hơn
# (bản lớn mạnh nhất nhưng nặng — bản 0.6B đủ tốt để học + chạy CPU/GPU phổ thông)

# Lựa chọn 3 — VN chuyên biệt (đáng thử cho tiếng Việt thuần):
#   model = SentenceTransformer("bkai-foundation-models/vietnamese-bi-encoder")
#   # hoặc halong-embedding — đều có mặt trên benchmark VN-MTEB

# Chạy lại eval_set, so sánh precision@3
```

> ⚠️ **Đừng tin leaderboard chung (MTEB tiếng Anh) — dùng benchmark VN (VN-MTEB) làm điểm khởi đầu, rồi để GOLDEN SET tiếng Việt của mình chốt.** Quy trình swap-and-measure đầy đủ ở [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A8**.

Ghi lại kết quả so sánh (điền số thật để đưa vào CV):
```
| Model                          | Precision@3 | Ghi chú                          |
|--------------------------------|-------------|----------------------------------|
| all-MiniLM-L6-v2               | ??%         | 80MB, nhanh, baseline tuần 1     |
| BAAI/bge-m3                    | ??%         | ~2GB, đa ngôn ngữ tốt            |
| Qwen3-Embedding-0.6B           | ??%         | Dẫn đầu đa ngữ 2026, hợp VN       |
| vietnamese-bi-encoder (bkai)   | ??%         | VN chuyên biệt, nhẹ              |
```

> 💡 *Đây chính là số liệu vàng cho CV: "Cải thiện precision@3 từ X% (MiniLM) lên Y% bằng cách đổi sang Qwen3-Embedding, đo trên golden set tiếng Việt".*

---

### Ngày 11 (Thứ Sáu 27/6) — Tách retrieval text vs code

**Thời gian:** 5h · **Track:** Áp dụng

Thí nghiệm: tạo 2 collection riêng trong ChromaDB — `code_chunks` và `doc_chunks`. Khi query, tìm top-2 từ mỗi collection rồi merge. So sánh precision@3 với bản gộp chung 1 collection.

---

### Ngày 12–13 (Thứ Bảy–Chủ Nhật 28–29/6) — Bài tập tương tự + Ôn

**Thời gian:** 5h x 2 ngày · **Track:** Áp dụng

**Bài tập:** Viết script `compare_chunking.py` — thử 3 chiến lược chunking khác nhau trên cùng codebase:
1. Chunk theo ký tự cố định (500 chars)
2. Chunk theo ranh giới hàm/heading (hiện tại)
3. Chunk theo ký tự + overlap 100 chars

Đo precision@3 cho mỗi chiến lược. Ghi kết quả vào NOTES.md.

**Ngày 14 (Thứ Hai 30/6):** Commit, cleanup code, cập nhật NOTES.md.

---

## TUẦN 3: Agent + Tool-Calling

> [!TIP]
> **Tài liệu tham khảo:** Đọc Phần I, II, III của [Bản Đồ Quyết Định Công Nghệ & Chi Phí](file:///c:/Users/Pc/Desktop/Build%20CV/ai-code-auditor/docs/ban-do-cong-nghe-chi-phi.md) để nắm vững mô hình ReAct Agent, so sánh chi phí các model khi chạy vòng lặp Agent (ví dụ: vì sao dùng model rẻ DeepSeek V3.2 / Gemini 3.5 Flash cho agent loop).

**Mục tiêu tuần:** Hiểu pattern ReAct, viết vòng lặp agent cơ bản, thêm tool thật.

> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A6 Model & Cost · A7 Agent design (L3)** — đặc biệt khối 🛑 "khi nào KHÔNG cần agent" để tránh over-engineer.

> Lộ trình cũ đặt Agent ở tuần 4. Đẩy lên tuần 3 vì: (1) phần hấp dẫn nhất, giữ động lực; (2) cần thời gian nhiều hơn cho multi-agent + MCP ở tuần sau.

> [!IMPORTANT]
> **REV 2/7 cho Tuần 3:**
> 1. Lịch trượt +1 ngày: **Ngày 15 bắt đầu Thứ Tư 2/7** (1/7 đã dùng cho Ngày 14 metadata filter).
> 2. **Retrieval ĐÓNG BĂNG** — `rag_search` từ nay chỉ là 1 tool ngữ nghĩa của agent (cho câu hỏi concept), KHÔNG tối ưu tiếp.
> 3. **Dùng structured output NGAY TỪ ĐẦU** (function calling / JSON schema — Món 5 kéo lên): code mẫu bên dưới parse `Action:` bằng regex chỉ để HIỂU pattern ReAct; bản bạn viết nên ép schema từ Ngày 15 để khỏi vá sau (regex parse là bug runtime có thật).
> 4. Model cho agent loop: **`gemini-2.5-flash-lite`** (loop gọi LLM nhiều lần, đừng đốt tiền bằng 3.5-flash).

---

### Ngày 15 (Thứ Tư 2/7) — Pattern ReAct: Hiểu trước khi code

**Thời gian:** 5h · **Track:** Code tay

#### Lý thuyết ReAct (1h)

```
USER: "Kiểm tra xem code có chỗ nào dùng mã hoá yếu không?"

AGENT LOOP:
  Thought: Tôi cần tìm các hàm liên quan đến mã hoá/crypto trong codebase
  Action: grep_tool("crypto", codebase)
  Observation: Tìm thấy 5 file chứa "crypto": webhook.js, credentials/...
  
  Thought: Cần đọc từng file để xem dùng thuật toán gì
  Action: read_file_tool("credentials/encrypt.js")
  Observation: Dùng AES-256-GCM, IV ngẫu nhiên, auth tag...
  
  Thought: AES-256-GCM là mã hoá mạnh. Không tìm thấy mã hoá yếu.
  Answer: "Codebase dùng AES-256-GCM cho credential và HMAC-SHA256 cho webhook - 
           cả hai đều là tiêu chuẩn mạnh."
```

**Khái niệm cốt lõi:**
- **Thought:** Model "suy nghĩ" bước tiếp theo
- **Action:** Gọi tool cụ thể
- **Observation:** Kết quả từ tool
- Loop cho đến khi đủ thông tin rồi trả lời cuối

#### Implement `agent.py` (4h)

```python
# agent.py — Vòng lặp ReAct cơ bản
import os, re, subprocess, json, time
from google import genai

client = genai.Client()  # dual-mode: tự đọc env (Vertex hoặc GEMINI_API_KEY) — như call_gemini
CODEBASE_DIR = "path/to/chatbot-fanpage"

# --- TOOLS ---
def read_file_tool(filepath):
    full_path = os.path.join(CODEBASE_DIR, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 3000:
            content = content[:3000] + "\n... [truncated]"
        return content
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found"

def grep_tool(pattern):
    try:
        result = subprocess.run(
            ["grep", "-rnI", "--include=*.js", "--include=*.md", pattern, CODEBASE_DIR],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout[:2000]
        return output if output else f"No matches found for '{pattern}'"
    except Exception as e:
        return f"Error: {str(e)}"

def list_files_tool(directory="."):
    full_dir = os.path.join(CODEBASE_DIR, directory)
    files = []
    for root, dirs, filenames in os.walk(full_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git"}]
        for f in filenames:
            rel = os.path.relpath(os.path.join(root, f), CODEBASE_DIR)
            files.append(rel)
    return "\n".join(files[:50])

TOOLS = {
    "read_file": read_file_tool,
    "grep": grep_tool,
    "list_files": list_files_tool,
}

SYSTEM_PROMPT = """Bạn là AI agent chuyên phân tích codebase. Bạn có 3 tool:
1. read_file(filepath) - Đọc nội dung file
2. grep(pattern) - Tìm pattern trong code
3. list_files(directory) - Liệt kê file

FORMAT (bắt buộc):
Thought: [suy nghĩ]
Action: tool_name(arg)

Hoặc khi đủ thông tin:
Thought: [suy nghĩ cuối]
Answer: [câu trả lời]
"""

def run_agent(question, max_steps=6):
    messages = f"{SYSTEM_PROMPT}\n\nUser question: {question}\n\n"
    
    for step in range(max_steps):
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", contents=messages  # REV 2/7: model rẻ cho loop
        )
        reply = response.text.strip()
        messages += reply + "\n"
        
        print(f"\n--- Step {step + 1} ---")
        print(reply)
        
        if "Answer:" in reply:
            return reply.split("Answer:")[-1].strip()
        
        action_match = re.search(r'Action:\s*(\w+)\(([^)]*)\)', reply)
        if action_match:
            tool_name = action_match.group(1)
            tool_arg = action_match.group(2).strip().strip('"\'')
            if tool_name in TOOLS:
                observation = TOOLS[tool_name](tool_arg)
                messages += f"\nObservation: {observation}\n\n"
                print(f"Observation: {observation[:200]}...")
            else:
                messages += f"\nObservation: Unknown tool '{tool_name}'\n\n"
    
    return "Agent reached max steps without final answer."

if __name__ == "__main__":
    while True:
        q = input("\nQuestion (or 'quit'): ").strip()
        if q.lower() in ("quit", "exit", ""):
            break
        answer = run_agent(q)
        print(f"\n=== FINAL ANSWER ===\n{answer}")
```

---

### Ngày 16 (Thứ Năm 3/7) — Debug agent, thêm tool

**Thời gian:** 5h

Test agent với câu hỏi cần NHIỀU tool:
- "Kiểm tra code có chỗ nào dùng mã hoá yếu không, và test có pass không"
- "Liệt kê tất cả endpoint API và mô tả chức năng"

Thêm tool `run_tests`:
```python
def run_tests_tool(test_file=""):
    cmd = ["npm", "test"]
    result = subprocess.run(cmd, capture_output=True, text=True, 
                          timeout=60, cwd=CODEBASE_DIR)
    return (result.stdout + result.stderr)[:2000]
```

---

### Ngày 17 (Thứ Sáu 4/7) — Kết hợp RAG + Agent

**Thời gian:** 5h

Thêm RAG retrieval như một tool cho agent:
```python
def rag_search_tool(query):
    query_emb = embed_texts(model, [query])[0]
    results = retrieve_top_k(query_emb, index)
    output = ""
    for c in results:
        output += f"[{c['score']:.3f}] {c['path']} chunk {c['chunk_id']}:\n{c['content'][:300]}\n\n"
    return output
```

Giờ agent CHỌN giữa: grep (exact match) vs rag_search (semantic) vs read_file (full context).

---

### Ngày 18–19 (Thứ Bảy–Chủ Nhật 5–6/7) — Logging + Bài tập tương tự

**Thời gian:** 5h x 2

Thêm logging cho mọi lệnh gọi LLM:
```python
def log_llm_call(step, prompt_tokens, output_tokens, latency_ms, tool_used):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "step": step, "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens, "latency_ms": latency_ms,
        "tool_used": tool_used,
    }
    with open("agent_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

**Bài tập tương tự:** Viết agent cho bài toán khác — agent đọc CSV và trả lời câu hỏi thống kê (tool `read_csv` + `calculate`). Chứng minh pattern ReAct là tổng quát.

### Ngày 20–21 (Thứ Hai–Thứ Ba 7–8/7) — Ôn + Commit

---

## TUẦN 4 (REV 2/7): Auditor v1 + Seeded-Bug Benchmark (9–15/7)

> **Thay thế hoàn toàn tuần IBM Coursera cũ.** Lý do (quyết định 2/7, sau khi tra nghiên cứu tuyển dụng 2026): chứng chỉ là tín hiệu yếu so với dự án ship + eval — *"CV không nhắc eval là bị loại ở công ty nghiêm túc"*; 7 ngày này là quỹ thời gian quý nhất còn lại trước deadline. **LangGraph + MCP chuyển sang đọc docs chính thức 30–60 phút/tối** trong tuần này (bạn đã tự build agent loop nên đọc docs sẽ rất nhanh — vẫn giữ thói quen ghi "cái này tương đương hàm nào tôi tự viết?" vào NOTES.md).

**Mục tiêu tuần:** Biến "Q&A trên code" thành **auditor thật** — tự quét, xuất báo cáo findings có citation — và dựng **thước đo chính của CV: seeded-bug benchmark**.

> 🧭 **Góc Architect:** đây là tuần "reframe sản phẩm" — auditor ≠ chatbot. Ôn lại B1 Evaluation + B4 Build-vs-Buy trong [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md).

### Ngày 22 (Thứ Tư 9/7) — Định vị lại sản phẩm + thiết kế audit checklist

- **Reframe:** auditor KHÔNG chờ câu hỏi. Input = đường dẫn repo; output = **báo cáo findings**. Mỗi finding theo schema JSON cố định (structured output — Món 5): `{id, severity, category, file, line_range, evidence, explanation, suggestion}`.
- Thiết kế **audit checklist** từ chính kinh nghiệm vận hành chatbot-fanpage: secret hardcode, so sánh chữ ký không timing-safe, credential log ra console, doc–code lệch nhau, dependency lỗi thời, endpoint thiếu auth, input không validate...
- Agent Tuần 3 (grep/read/list/rag_search) **giữ nguyên** — chỉ đổi "câu hỏi user" thành "từng mục checklist".

### Ngày 23 (Thứ Năm 10/7) — Auditor v1 chạy end-to-end

Chạy trọn checklist trên `chatbot-fanpage` → gom findings → render báo cáo Markdown (bảng findings theo severity + citation `file:line`). Log token/chi phí **cho từng mục checklist** (nối logging Ngày 18–19) → biết mục nào đắt.

### Ngày 24 (Thứ Sáu 11/7) — Cấy lỗi: dựng "spiked repository"

- **Phương pháp chuẩn ngành 2026** (spiked repository — inject lỗi biết trước vào codebase THẬT, không tự bịa codebase fake): fork `chatbot-fanpage` → **cấy 15–20 lỗi**, rải 4–5 nhóm: (a) secret hardcode, (b) crypto sai (`==` thay `timingSafeEqual`, IV tái dùng), (c) doc–code mismatch, (d) auth/RBAC hổng, (e) dependency có CVE.
- Ghi **golden set findings**: mỗi lỗi cấy = 1 record `{file, line, category, mô tả}` — "đáp án vàng" mới của dự án (thay vai golden set retrieval 5 câu).
- ⚠️ Cấy lỗi **giống thật** (KHÔNG comment `// BUG HERE`); vài lỗi phải cần suy luận cross-file mới thấy — để phân tầng độ khó.

### Ngày 25 (Thứ Bảy 12/7) — Đo: detection recall + false-positive rate

- **Recall** = số lỗi cấy tìm được / tổng lỗi cấy. **FP rate** = findings sai / tổng findings.
- Đây là **số liệu CV chính** thay precision@3: *"Auditor phát hiện X/Y lỗi cấy chủ đích, false-positive Z%, có citation từng finding."*
- Chấm nửa tự động: match `file + line_range ±5 dòng + category`; case mơ hồ tự đọc (bài học Ngày 12: bộ lọc test lỏng = bug giả dạng).

### Ngày 26 (Chủ Nhật 13/7) — Phễu chi phí 3 tầng (L0 → L1 → L2)

- **L0 — Deterministic (miễn phí, quét cả repo):** regex/AST/lint bắt secret, `==` signature compare, dependency cũ. KHÔNG tốn token nào.
- **L1 — Agentic grep (rẻ):** agent khoanh vùng nghi vấn bằng grep/read, chỉ mở file liên quan.
- **L2 — LLM deep review (đắt, CHỈ vùng nghi vấn):** suy luận cross-file (doc khớp code? auth boundary hổng?).
- **Đo $/audit + recall/FP theo từng tầng** → bảng trade-off. Khớp phát hiện ngành: *LLM tăng recall, công cụ deterministic kìm false-positive*. Đúng nguyên tắc B4: đừng dùng LLM cho việc một hàm thường giải được.

### Ngày 27–28 (Thứ Hai–Thứ Ba 14–15/7) — LLM-as-judge cho findings + ôn + commit

- Món 4 (RAG Triad) **chuyển hóa cho auditor**: judge chấm mỗi finding theo **Groundedness** (evidence có thật trong code?) + **Actionability** (suggestion sửa được không?). So kết quả judge vs chấm tay trên tập cấy → báo luôn độ lệch judge (meta-eval).
- Ôn tuần, NOTES.md, commit. Tối: chốt docs LangGraph (StateGraph, checkpointing, conditional edges) chuẩn bị Tuần 5.

> #### 💬 Đáp án mẫu phỏng vấn — Tuần 4
>
> **Hỏi: "Làm sao bạn biết auditor của bạn TỐT? AI bảo code có lỗi thì tin được không?"**
>
> *"Tôi không tin cảm giác — tôi dựng benchmark. Tôi fork một codebase production thật và cấy 15–20 lỗi biết trước thuộc 5 nhóm (secret, crypto, auth, doc-lệch-code, dependency), rồi đo 2 số: **detection recall** (tìm được bao nhiêu lỗi cấy) và **false-positive rate** (báo láo bao nhiêu). Đây là phương pháp 'spiked repository' mà các benchmark ngành 2026 dùng. **Đánh đổi:** benchmark lỗi-cấy chỉ đo được loại lỗi mình nghĩ ra để cấy — nên tôi chạy thêm auditor trên OWASP NodeGoat, nơi lỗi do bên thứ ba document, để kiểm chứng độc lập."*
>
> **Hỏi: "Vì sao không cho LLM quét thẳng cả repo cho nhanh?"**
>
> *"Vì đắt và nhiễu. Tôi thiết kế phễu 3 tầng theo chi phí: tầng deterministic (regex/AST, miễn phí) bắt lớp lỗi máy móc như secret hardcode; tầng agentic grep (rẻ) khoanh vùng nghi vấn; LLM (đắt) chỉ vào nơi cần suy luận cross-file. Tôi đo $/audit từng tầng — LLM-quét-toàn-bộ đắt gấp N lần mà false-positive cao hơn."*

---

## TUẦN 5: Multi-Agent + LangGraph

> [!TIP]
> **Tài liệu tham khảo:** Đọc Phần I (Cấp độ 4), Phần IV (OpenRouter vs Gemini API) và Phần V của [Bản Đồ Quyết Định Công Nghệ & Chi Phí](file:///c:/Users/Pc/Desktop/Build%20CV/ai-code-auditor/docs/ban-do-cong-nghe-chi-phi.md) để so sánh các nhà cung cấp mô hình và học cách tích hợp Streamlit UI cho dự án.

**Mục tiêu tuần (REV 2/7):** Chuyển auditor sang LangGraph với **ĐÚNG 2 agent** (Auditor + Reviewer/Validator), thêm observability, và **expose MCP server**. Kiềm chế: KHÔNG router/multi-agent 3–4 vai — nguyên tắc đỉnh tháp (single agent + tools là đủ cho đa số; multi-agent chỉ khi vai trò thật sự tách bạch).

> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A7 · C3 Capstone điều phối (L4)** — nhớ nguyên tắc đỉnh tháp: kiềm chế, chỉ multi-agent khi vai trò thật sự tách bạch.

### Ngày 29 (Thứ Năm 16/7) — Setup LangGraph project

```bash
pip install langgraph langchain-google-genai
```

Map khái niệm về code tay đã viết (ghi NOTES.md): StateGraph ↔ vòng `for` + biến `messages` trong `agent.py`; checkpoint ↔ log jsonl; conditional edge ↔ `if "Answer:" in reply`.

### Ngày 30–31 (Thứ Sáu–Thứ Bảy 17–18/7) — Auditor + Reviewer trên LangGraph

Kiến trúc (REV 2/7 — 2 agent, BỎ Router/CodeFinder/Explainer):
```
Repo path + audit checklist
        |
        v
 [Auditor Agent] --tools--> grep, read_file, list_files, rag_search
        |  findings (JSON schema — Món 5)
        v
 [Reviewer/Validator] -> đối chiếu TỪNG finding với evidence trong code
        |                 (Món 3: generator-validator; số học đẩy Python sandbox)
        v
  PASS -> báo cáo cuối  |  FAIL -> trả critique có cấu trúc cho Auditor sửa (tối đa 2 vòng)
```

**Đo lại seeded-bug benchmark SAU khi thêm Reviewer:** kỳ vọng false-positive rate giảm → số CV thứ hai ("Reviewer agent giảm FP từ A% xuống B%").

### Ngày 32–33 (Chủ Nhật–Thứ Hai 19–20/7) — MCP server (REV 2/7: CHÍNH THỨC, không còn "nếu kịp")

MCP đã là chuẩn ngành (Linux Foundation, spec final 7/2026, 97M SDK downloads/tháng, 41% doanh nghiệp production). Expose auditor qua **FastMCP**: tool `audit_repo(path)` + `get_finding(id)` → bất kỳ MCP client nào (Claude Desktop, Claude Code...) gọi được auditor của bạn. ~1 ngày vì tools đã có sẵn; ngày còn lại: test từ client thật + quay demo GIF cho README.

### Ngày 34–35 (Thứ Ba–Thứ Tư 21–22/7) — Observability (Món 7) + testing + commit

Arize Phoenix (open-source, chạy local) hoặc LangSmith free tier: trace từng bước agent, bắt loop thừa / token đốt ở đâu. Chốt bộ số vận hành: latency/audit, $/audit, số bước agent trung bình.

---

## TUẦN 6: Deploy + Áp Dụng Ngược Lại Dự Án 1

> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **B3 Deploy (🟢)** + đọc-để-biết **B2 Security · B4 Build-vs-Buy (🔵)** — gắn với audit thật chatbot-fanpage (tìm hardcode secret).

### Ngày 36–37 (Thứ Năm–Thứ Sáu 23–24/7) — Docker + Deploy

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "agent.py"]
```

Deploy lên Railway (đồng bộ platform với chatbot-fanpage).

### Ngày 38 (Thứ Bảy 25/7) — Audit thật chatbot-fanpage (bản GỐC, không phải fork cấy lỗi)

Chạy full auditor → đọc báo cáo findings → **sửa các lỗi THẬT** tìm được trong chatbot-fanpage. Đọc kỹ code trước khi sửa; commit message giải thích rõ vì sao. Findings thật + fix thật trên hệ production = câu chuyện demo sống (hai dự án tự khóa vào nhau).

### Ngày 39 (Chủ Nhật 26/7) — Kiểm chứng ngoài: OWASP NodeGoat (REV 2/7)

Chạy auditor trên **OWASP NodeGoat** (app Node.js cố tình chứa OWASP Top 10, từng lỗi được document sẵn) → báo *"phát hiện X/Y lỗi đã document"*. Đây là số liệu **bên thứ ba kiểm chứng được** — chứng minh auditor không overfit vào repo nhà (benchmark cấy lỗi chỉ đo được loại lỗi mình nghĩ ra để cấy).

### Ngày 40 (Thứ Hai 27/7) — Streamlit UI (REV 2/7)

UI tối thiểu: nhập repo path → chạy audit → bảng findings (severity, category, `file:line`, evidence) → click xem chi tiết + citation. Bar portfolio 2026 yêu cầu "working UI + live demo" — công ty VN product càng nặng "demo bấm được".

### Ngày 41–42 (Thứ Ba–Thứ Tư 28–29/7) — README TIẾNG ANH + Architecture doc (REV 2/7)

Viết README.md cho `ai-code-auditor` **bằng tiếng Anh** (người screen CV nào cũng đọc GitHub bằng EN; CV nộp thì song ngữ):
- Mục tiêu dự án, kiến trúc (sơ đồ 2-agent + phễu chi phí L0→L2), demo GIF (kể cả gọi qua MCP client)
- Số liệu: **seeded-bug recall + FP rate** (trước/sau Reviewer), **NodeGoat X/Y**, **$/audit theo tầng**, latency/audit; precision@3 60% ghi như *"bài học đo giới hạn dense retrieval trên code → lý do chuyển agentic search"*
- Cách chạy (CLI, UI, MCP), link chatbot-fanpage như case study production

---

## TUẦN 7: CV + Luyện Phỏng Vấn

> 🧭 **Góc Architect:** ôn [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **C1 Khung phán đoán · C2 Catalog red-flags** — dùng để trả lời câu phỏng vấn "khi nào dùng gì / sao biết AI sai".

### Ngày 43–44 (Thứ Ba–Thứ Tư 29–30/7) — Viết CV bullet

**Dự án 1 (chatbot-fanpage):**
```
- Vận hành production chatbot Messenger cho shop thật trên Railway
  (webhook HMAC-SHA256, credential AES-256-GCM, RBAC 4 roles)
- Quản lý codebase 226 commits, 945 tests pass, multi-tenant
```

**Dự án 2 (ai-code-auditor)** *(REV 2/7 — điền số thật sau Tuần 4–6)*:
```
- Build AI Code Auditor (LangGraph 2-agent + MCP server): tự quét repo,
  xuất báo cáo findings có citation — detection recall X/Y lỗi cấy,
  false-positive Z% trên spiked-repo benchmark tự dựng; Reviewer agent
  giảm FP từ A% xuống B%
- Phễu audit 3 tầng theo chi phí (AST/regex -> agentic grep -> LLM deep
  review): $/audit giảm N lần so với LLM-quét-toàn-bộ
- Build RAG từ zero + đo giới hạn dense retrieval trên code (precision@3
  kẹt 60% sau rerank/hybrid trên golden set tự dựng) -> chuyển agentic
  search — trùng kết luận ngành 2026
- Deploy Docker/Railway + Streamlit UI + observability trace; kiểm chứng
  ngoài trên OWASP NodeGoat (X/Y lỗi documented)
```

### Ngày 45–46 (31/7–1/8) — Luyện giải thích 5 phút

Dựa trên NOTES.md, quay video tự giải thích mỗi dự án 5 phút, xem lại, quay lại.

### Ngày 47–49 (2–4/8) — Tự hỏi-đáp 10 câu phỏng vấn

| # | Câu hỏi |
|---|---------|
| 1 | Embedding vs keyword search — khi nào dùng cái nào? |
| 2 | RAG vs fine-tuning — vì sao bạn chọn RAG? |
| 3 | Cosine similarity vs Euclidean — ưu nhược? |
| 4 | Vector DB vs brute-force list — khi nào cần? |
| 5 | LangGraph vs tự viết agent loop — trade-off? |
| 6 | Chunking size lớn vs nhỏ — ảnh hưởng gì? |
| 7 | Gemini hallucinate thì bạn debug thế nào? |
| 8 | MCP là gì, giải quyết vấn đề gì? |
| 9 | Precision@3 của bạn bao nhiêu, đã làm gì để cải thiện? |
| 10 | Giải thích luồng từ khi user hỏi đến agent trả lời? |
| 11 | Context window 1M token rồi, RAG còn cần không? (long-context vs RAG) |
| 12 | GraphRAG là gì, khi nào chọn thay vì RAG thường? |
| 13 | Làm sao bạn biết auditor của bạn tốt? (→ 💬 Tuần 4: seeded-bug benchmark) |
| 14 | Vì sao không cho LLM quét thẳng cả repo? (→ 💬 Tuần 4: phễu chi phí 3 tầng) |

---

## 🎤 NGÂN HÀNG ĐÁP ÁN MẪU — 12 CÂU PHỎNG VẤN CỐT LÕI

> Đây là phần ôn luyện chính. Mỗi đáp án theo **Công thức 3 câu** (Vấn đề → Giải pháp → Đánh đổi). Đừng học vẹt từng chữ — hiểu ý rồi diễn đạt lại bằng lời mình. Che đáp án, tự nói thành tiếng trước.

**1. Embedding vs keyword search — khi nào dùng cái nào?**
> *"Keyword search khớp theo *ký tự*; embedding khớp theo *ý nghĩa*. Dùng embedding khi người dùng diễn đạt khác từ nhưng cùng ý ('kiểm tra chữ ký' vs 'verify signature'). Dùng keyword/DB query khi cần khớp chính xác: mã đơn, số điện thoại, tên hàm. **Đánh đổi:** embedding không phân biệt được #1234 vs #5678. Hệ thống thật thường kết hợp cả hai — gọi là **hybrid search** — rồi gộp điểm."*

**2. RAG vs fine-tuning — vì sao bạn chọn RAG?**
> *"Fine-tuning là *dạy lại* model bằng cách cập nhật trọng số; RAG là *đưa kiến thức vào lúc hỏi* qua context. Tôi chọn RAG vì: (1) dữ liệu (codebase) **thay đổi liên tục** — fine-tune lại mỗi lần đổi code là bất khả thi, còn RAG chỉ cần index lại; (2) RAG cho **trích dẫn nguồn**, kiểm chứng được, còn fine-tune thì kiến thức 'tan' vào trọng số, khó truy vết; (3) rẻ và nhanh hơn nhiều với fresher. **Khi nào fine-tune tốt hơn:** khi cần model học một *phong cách/định dạng* cố định hoặc một kỹ năng mới, chứ không phải tra cứu sự thật hay thay đổi."*

**3. Cosine similarity vs Euclidean — ưu nhược?**
> *"Euclidean đo khoảng cách thẳng, bị ảnh hưởng bởi độ lớn vector; cosine đo góc, bỏ qua độ lớn. RAG chuộng cosine vì một câu ngắn và một đoạn dài cùng chủ đề có magnitude khác nhau nhưng cùng hướng — cosine vẫn báo 'gần'. **Lưu ý:** không có ngưỡng cosine đúng tuyệt đối, phải đo trên dữ liệu thật."*

**4. Vector DB vs brute-force list — khi nào cần?**
> *"Bản tự viết của tôi quét *toàn bộ* chunk để tính similarity — đó là brute-force O(n), hoàn toàn ổn với vài trăm chunk. **Vấn đề** xuất hiện ở quy mô hàng triệu vector: quét hết quá chậm. **Giải pháp:** vector DB (pgvector, Chroma, Pinecone) dùng chỉ mục xấp xỉ như HNSW để tìm hàng xóm gần nhanh hơn nhiều. **Đánh đổi cốt lõi:** đánh đổi *độ chính xác tuyệt đối* lấy *tốc độ* (approximate nearest neighbor). Với dự án nhỏ thì brute-force còn đơn giản và chính xác hơn — không cần vác vector DB vào."*

**5. LangGraph vs tự viết agent loop — trade-off?**
> *"Tôi đã **tự viết** vòng lặp ReAct trước (Tuần 3) nên hiểu bản chất: nó chỉ là vòng lặp Thought→Action→Observation. **Vấn đề** khi agent phức tạp lên: cần quản lý state, retry khi lỗi, rẽ nhánh có điều kiện, phối hợp nhiều agent — tự viết thì code rối và khó kiểm soát. **Giải pháp:** LangGraph mô hình hóa luồng thành **máy trạng thái** (node = bước/agent, edge = điều kiện chuyển), kèm sẵn checkpoint, retry, human-in-the-loop. **Đánh đổi:** agent đơn giản một bước thì tự viết loop gọn hơn, kéo LangGraph vào là thừa; agent nhiều bước/nhiều vai trò thì LangGraph đáng giá."*

**6. Chunking size lớn vs nhỏ — ảnh hưởng gì?**
> *"Chunk **to** giữ nhiều ngữ cảnh nhưng làm retrieval kém chính xác (lẫn thông tin thừa) và tốn token. Chunk **nhỏ** chính xác hơn nhưng dễ mất ngữ cảnh, cắt giữa một hàm thì model không hiểu. Tôi cắt theo *ranh giới có nghĩa* (heading cho .md, ranh giới hàm cho .js) và có fallback cắt theo ký tự cho đoạn quá dài. Tôi đã *đo precision@3* với 3 chiến lược chunking khác nhau để chọn — chứ không đoán."*

**7. Gemini hallucinate thì bạn debug thế nào?**
> *"Việc đầu tiên: **in ra đúng prompt đã gửi** và xem các chunk được truyền vào. Phần lớn trường hợp model 'bịa' thực ra là do **retrieval lấy sai chunk** — model trả lời đúng theo context rác. Nếu retrieval đúng mà vẫn bịa thì siết prompt: bắt 'chỉ dùng context, không có thì nói không biết'. Tôi cũng test bằng câu hỏi off-topic để xác nhận rào chắn hoạt động. Tư duy chính: hallucination thường là **lỗi hệ thống (retrieval/prompt)**, không phải 'model ngu'."*

**8. MCP là gì, giải quyết vấn đề gì?**
> *"MCP (Model Context Protocol) là một **chuẩn giao tiếp** để model/agent gọi tới các tool và nguồn dữ liệu bên ngoài. **Vấn đề** trước MCP: mỗi tool tích hợp một kiểu riêng, đổi client là phải viết lại — giống thời mỗi thiết bị một cổng sạc. **Giải pháp:** MCP định nghĩa một 'cổng chuẩn' — server expose tool theo MCP thì *bất kỳ* client hỗ trợ MCP đều gọi được, không cần viết lại. **Khi nào chưa cần:** nếu chỉ có 1-2 tool đơn giản trong một app, function calling thường là đủ; MCP đáng giá khi cần tái sử dụng tool across nhiều agent/client."* ⚠️ **[Chờ kiểm chứng web]** — nên cập nhật phiên bản/chi tiết MCP mới nhất 2026.

**9. Precision@3 của bạn bao nhiêu, đã làm gì để cải thiện?**
> *"Tôi xây một bộ ~15 câu hỏi có 'đáp án vàng' (golden set) — biết trước chunk/từ khóa đúng. Precision@3 nghĩa là: trong top-3 chunk retrieval trả về, có chunk đúng không. Baseline với MiniLM của tôi là [X]%. Tôi cải thiện bằng cách: (1) đổi sang embedding mạnh hơn (BGE-M3) — precision lên [Y]%; (2) thử các chiến lược chunking khác nhau; (3) tách collection code và doc. **Điểm mấu chốt tôi muốn nhấn:** tôi *đo được* tác động của từng thay đổi bằng con số, thay vì 'cảm giác nó tốt hơn'."*
> 👉 *Điền số thật của bạn sau Tuần 2 — đây là bullet mạnh nhất trên CV.*

**10. Giải thích luồng từ khi user hỏi đến agent trả lời?**
> *"User đặt câu hỏi → (nếu là agent) router quyết định cần tool nào → agent chạy vòng ReAct: nghĩ (Thought) → gọi tool grep/read_file/rag_search (Action) → nhận kết quả (Observation) → lặp đến khi đủ thông tin → tổng hợp câu trả lời cuối, kèm trích dẫn file/chunk. Với RAG thuần (không agent): embed câu hỏi → cosine similarity → top-K chunk → ghép prompt có ràng buộc chống bịa → gọi LLM → trả lời. Tôi luôn log token/latency mỗi lần gọi LLM để biết chi phí và điểm nghẽn."*

---

> **Bổ sung từ track Beyond-RAG (Tầng 1)** — hai câu "cấp cao" để bật khỏi đám fresher. Đào sâu: [beyond-rag-phase-2.md](beyond-rag-phase-2.md).

**11. Context window 1M token rồi, RAG còn cần không? (long-context vs RAG)**
> *"Vẫn cần, và lý do mang tính vật lý chứ không phải sở thích. **Một:** nạp 1M token mỗi lần thì pha prefill cực nặng (self-attention ~O(n²)) đẩy thời gian phản hồi đầu tiên lên hàng chục giây, và KV-cache ngốn VRAM khổng lồ cho mỗi user đồng thời — không khả thi real-time. **Hai:** 'lost in the middle' — model đọc được nhưng suy luận kém với thông tin nằm giữa context dài. **Ba (điểm tôi muốn nhấn):** RAG là **màng lọc bảo mật** — gắn Row-Level Security vào metadata để loại dữ liệu user không có quyền *trước khi* nó vào prompt. **Đánh đổi:** tài liệu nhỏ + ít đổi thì nhồi thẳng (long-context) đơn giản hơn; thực tế tôi dùng kiến trúc lai — hybrid retrieval → rerank → đẩy top chunk vào long-context."*
> 👉 *Câu này cho thấy bạn hiểu hệ thống ở tầng phần cứng/kinh tế, không chỉ chạy demo.* ⚠️ **[Chờ kiểm chứng web]** mốc GB KV-cache nếu trích số cụ thể.

**12. GraphRAG là gì, khi nào chọn thay vì RAG thường?**
> *"RAG thường truy xuất các mảnh văn bản *rời rạc* theo độ tương đồng, nên **chết với câu hỏi cần đi qua quan hệ liên kết** — ví dụ 'hàm A gọi hàm nào, đổi nó ảnh hưởng module nào'. **GraphRAG** dựng knowledge graph (thực thể = node, quan hệ = edge); Local search duyệt lân cận một thực thể, Global search gom đồ thị thành cộng đồng bằng thuật toán Leiden rồi tóm tắt để trả câu vĩ mô. **Đánh đổi:** chi phí dựng index rất cao vì dùng LLM trích xuất. Riêng với code, tôi sẽ dựng call graph bằng **AST/static analysis** cho rẻ và chính xác, chỉ để LLM lo phần tóm tắt — đúng nguyên tắc đừng dùng LLM cho việc một hàm thường giải được."*
> 👉 *Đây là hướng "AI Code Auditor v2" của tôi sau CV (xem beyond-rag-phase-2.md).*

---

## TUẦN 8: Buffer + Sprint Phỏng Vấn (5/8 – ~13/8)

> **Mục tiêu:** không học kiến thức mới. Dùng tuần này để (1) bù các phần bị trễ, (2) đánh bóng dự án + CV, (3) luyện nói đến mức trả lời trôi chảy. Đây là tuần biến "đã làm" thành "kể được hay".

### Ngày 50–51 — Buffer bù tiến độ
Hoàn thành nốt bất kỳ mục nào còn dang dở của Tuần 1-7 (ưu tiên theo mục "Điểm Cắt Nếu Trễ Tiến Độ" bên dưới — làm ngược lại: bù phần quan trọng trước). Nếu không trễ gì → dùng để thêm 1 tính năng nhỏ gây ấn tượng (vd hiển thị citation đẹp trên UI).

### Ngày 52–53 — Đánh bóng dự án & CV
- Rà lại README `ai-code-auditor` (tiếng Anh): có sơ đồ kiến trúc (2-agent + phễu L0→L2), số liệu (seeded-bug recall + FP rate, NodeGoat X/Y, $/audit theo tầng, latency; precision@3 60% như "bài học giới hạn dense retrieval") chưa.
- Chốt 2 bullet CV cho mỗi dự án (xem Ngày 43-44), điền số thật.
- Dọn git: commit message rõ ràng, xóa file rác, đảm bảo repo public chạy được theo README.

### Ngày 54–55 — Mock interview (tự mô phỏng)
- Mở **Ngân hàng đáp án mẫu 10 câu** ở trên, che đáp án, tự trả lời thành tiếng → quay video → xem lại → quay lại.
- Tự chấm theo 3 tiêu chí: (a) có nói được câu "đánh đổi/khi nào KHÔNG dùng" không; (b) có dẫn được số liệu/ví dụ từ dự án không; (c) trôi chảy dưới 60 giây/câu không.
- Luyện thêm **2 câu khó**: *"Nếu được làm lại dự án này bạn sẽ thay đổi gì?"* và *"Phần nào trong dự án bạn thấy khó nhất, vì sao?"* — nhà tuyển dụng dùng để đo độ trung thực và chiều sâu.

### Ngày 56 — Buffer cuối + nộp CV
Dự phòng. Khi mọi thứ sẵn sàng → nộp CV, gửi link GitHub + README.

---

## Bảng Quyết Định: Bài Toán Nào Dùng Gì (Cập Nhật 6/2026)

| Tình huống | Dùng gì | Khi nào KHÔNG dùng |
|-----------|---------|-------------------|
| Câu hỏi diễn đạt khác nhưng cùng ý | Embedding + cosine similarity | Cần khớp chính xác (mã đơn, SĐT) -> DB query |
| Tài liệu nhỏ, fit context window | Stuffing (nhồi thẳng vào prompt) | Tài liệu lớn -> tốn tiền + model dễ bỏ sót |
| Dữ liệu riêng, thay đổi thường xuyên | RAG (retrieval lúc query) | Kiến thức tổng quát có sẵn trong model |
| Cần số liệu/thống kê chính xác | Tool-calling gọi SQL/API | Không dùng RAG, embedding không "tính toán" |
| Agent cần gọi nhiều service | MCP (chuẩn giao tiếp thống nhất) | Chỉ 1-2 tool đơn giản -> function calling đủ |
| Agent phức tạp, cần state + retry | LangGraph (state machine) | Agent đơn giản 1 bước -> tự viết loop đủ |
| Prototype nhanh multi-agent | CrewAI (role-based) | Cần kiểm soát chặt luồng -> LangGraph |

---

## Điểm Cắt Nếu Trễ Tiến Độ (REV 2/7 — đã đảo thứ tự)

Cắt từ trên xuống:
1. **NodeGoat external validation (Ngày 39)** — nice-to-have; benchmark cấy lỗi đã đủ số CV
2. **Observability tool (Ngày 34–35)** — fallback: giữ logging jsonl tự viết
3. **LLM-as-judge cho findings (Ngày 27–28)** — fallback: chấm tay trên tập cấy vẫn đủ
4. **Streamlit UI (Ngày 40)** — fallback: báo cáo Markdown đẹp + screenshot trong README
5. **Vòng critique Reviewer→Auditor (Tuần 5)** — fallback: Reviewer chấm 1 chiều, bỏ vòng lặp sửa

*(AWS buổi tối / Memory module / Demo #2 vốn đã NGOÀI đường tới CV — nếu lỡ nhồi lại lịch thì cắt các mục đó TRƯỚC TIÊN, trước cả danh sách trên.)*

**KHÔNG CẮT:**
- Tuần 1–2 (RAG tay + eval) — nền tảng + câu chuyện "đo giới hạn dense retrieval"
- Agent cơ bản (Tuần 3) — xương sống của auditor
- **Seeded-bug benchmark (Tuần 4) — SỐ LIỆU CV CHÍNH, mất nó là mất điểm khác biệt**
- **MCP server (Tuần 5)** — chuẩn ngành 2026, chỉ ~1 ngày công *(REV: mục này TRƯỚC ĐÂY đứng đầu danh sách cắt — đã đảo vì MCP nay là chuẩn Linux Foundation)*
- Deploy (Tuần 6) — nhà tuyển dụng muốn thấy production

---

## Học Bổ Sung Song Song: AWS Base Knowledge

> **Triết lý:** Học để **hiểu nền tảng cloud**, không phải để thi cert hay bắt buộc dùng AWS. Giống học cosine similarity để hiểu embedding — biết luôn tốt hơn không biết. Thời gian: **~30 phút/ngày buổi tối**, không thay thế dự án chính.
>
> **⚠️ REV 2/7 — lịch tối cụ thể (tối nào AWS, tối nào DSA/docs) xem [lich-hoc-buoi-toi.md](lich-hoc-buoi-toi.md) — nguồn duy nhất.** AWS **tạm dừng 9–22/7** (nhường slot cho docs LangGraph/MCP thay tuần Coursera đã bỏ), quay lại từ 22/7. Section này chỉ giữ vai **nội dung + tài nguyên** AWS.

### Tại sao AWS khớp với dự án này

| Bạn đang build bằng tay | AWS managed equivalent |
|---|---|
| Chunking + Embedding (tuần 1-2) | Amazon Bedrock Knowledge Bases |
| Vector DB + Cosine search (tuần 1-2) | S3 Vectors (GA 2026) |
| LangGraph agents (tuần 3-5) | Amazon Bedrock AgentCore |
| FastAPI server (tuần 6) | AWS Lambda + API Gateway |

**Story CV mạnh:** "Build RAG từ đầu để hiểu cơ chế → map sang managed service trên AWS" = tư duy Solution Architect, không chỉ là coder.

### Thứ tự học theo tuần dự án

| Tuần dự án | AWS học song song (30 phút/tối) | Lý do khớp |
|---|---|---|
| Tuần 1-2 (RAG tay) | IAM + S3 cơ bản | Hiểu cách lưu trữ + phân quyền production |
| Tuần 3-4 (Agents) | Amazon Bedrock Getting Started | Map agents bạn đang code với Bedrock AgentCore |
| Tuần 5-6 (Deploy) | Lambda + API Gateway | Hiểu serverless deployment — lựa chọn thay FastAPI trên cloud |
| Tuần 7-8 (CV) | Review toàn bộ — map dự án sang AWS | Chuẩn bị câu trả lời phỏng vấn về cloud |

### Tài nguyên (toàn bộ miễn phí)

**AWS Skill Builder (free):**
- [Amazon Bedrock Getting Started](https://skillbuilder.aws/) — 1h, làm trước nhất
- [Foundations of Prompt Engineering](https://skillbuilder.aws/) — 4h, chỉ học phần Advanced (chain-of-thought, few-shot, jailbreak mitigation)

**YouTube — search term theo tuần:**
- Tuần 1-2: `"AWS IAM roles explained simply"` + `"AWS S3 tutorial beginner"`
- Tuần 3-4: `"Amazon Bedrock explained 2025"`
- Tuần 5-6: `"AWS Lambda Python tutorial"` + `"AWS API Gateway Lambda Python full tutorial"`

**Kênh đáng tin:** AWS (official) · TechWorld with Nana · FreeCodeCamp

### Bảng quyết định: Khi nào dùng AWS vs alternatives

| Bài toán | Dùng gì | AWS có cần? |
|---|---|---|
| Startup / SME Việt Nam, budget thấp | Railway/Render ($5-20/tháng) | ❌ Không |
| SME cần AI chatbot đơn giản | VPS + Docker + Gemini API | ❌ Không |
| Enterprise / Fintech / outsource nước ngoài | AWS hoặc Azure | ✅ Cần |
| Công ty yêu cầu AWS trong JD | AWS | ✅ Cần |

> **Thực tế:** Học AWS để **đọc được JD tuyển dụng và không bị loại vòng CV** — nhiều công ty outsource và enterprise đề cập AWS. Không phải mọi dự án đều cần AWS, nhưng hiểu AWS giúp bạn tư duy đúng về cloud dù deploy ở đâu.

---

## 🆕 Tích Hợp Beyond-RAG (Tầng 1)

> **Nguồn:** chắt từ bài nghiên cứu *"Beyond RAG"* (rà 22/6/2026). 7 món **rẻ + ăn điểm CV/phỏng vấn**, đã duyệt gấp vào lộ trình 2 tháng. Phần nặng cấp Enterprise (GraphRAG/RAPTOR/vLLM/audit swarm) ở [beyond-rag-phase-2.md](beyond-rag-phase-2.md) — track *sau CV*.
>
> **Nguyên tắc:** cả 7 món ≈ **+2–4 ngày rải rác**, KHÔNG phá deadline giữa 8/2026. Ưu tiên món trị đúng **nút thắt đã đo** (recall in-scope 33%, MiniLM yếu cross-lingual, "chunk nam châm" `admin/views.js#188`).

### Món 1 — Reranking → "phễu 3 tầng" (hybrid → rerank → generate)
- **Chèn:** Tuần 2 (sau khi có precision@3 baseline, quanh Ngày 11–13).
- **3 câu:** Top-K cosine còn lẫn rác → reranker (cross-encoder, vd **BGE-Reranker** local hoặc **Cohere Rerank**) chấm lại từng cặp (câu hỏi, chunk) bằng cross-attention → lọc tinh top 5–10. **KHÔNG dùng** khi precision đã đủ (rerank thêm latency).
- **Công sức:** ~0.5 ngày. **Lấp khoảng trống thật:** architect map A4 đã nói rerank nhưng bạn **chưa build bao giờ**. Đo precision@3 trước/sau rerank = số liệu CV.

### Món 2 — CRAG-lite (Corrective RAG: tự chấm retrieval + fallback)
- **Chèn:** Tuần 3 (thêm 1 tool "tự chấm độ tin retrieval" cho agent).
- **3 câu:** Naive RAG tin mù kết quả search → một **retrieval evaluator** phân loại chunk (đúng/sai/mơ hồ), sai thì **fallback** (web search / keyword / hỏi lại). **KHÔNG dùng** khi retrieval vốn đã chuẩn (thêm bước thừa).
- **Công sức:** ~0.5–1 ngày. **Trị đúng bệnh đã đo:** recall 33% + "chunk nam châm".

### Món 3 — Generator–Validator loop + Python sandbox cho số học
- **Chèn:** Tuần 5 (nâng cấp agent **Reviewer** đã có sẵn trong kiến trúc).
- **3 câu:** LLM bịa và **tính sai số học** → tách Validator đối chiếu lại; *không cho nó tự nhẩm* mà chạy **Python sandbox** để có số tuyệt đối; lỗi thì trả critique có cấu trúc cho Generator sửa. **KHÔNG dùng** khi tác vụ không có ràng buộc kiểm chứng được.
- **Công sức:** ~0.5 ngày. Câu "LLM không biết tính toán nên đẩy sang sandbox" nói trong phỏng vấn rất "senior".

### Món 4 — RAG Triad + LLM-as-judge
- **Chèn:** Tuần 2 (mở rộng golden set / khung đo Ngày 9).
- **3 câu:** precision@3 chỉ đo *retrieval* → RAG Triad đo 3 trục: **Context Relevance · Groundedness · Answer Relevance** bằng một LLM chấm tự động. **KHÔNG dùng** khi chỉ demo 1 lần (khỏi dựng harness).
- **Công sức:** ~0.5 ngày. **NOTES Ngày 6 đã tự bắc cầu sang "LLM-as-judge"** — đây là phần nối tiếp.

### Món 5 — Constrained decoding / structured output (JSON Schema)
- **Chèn:** Tuần 3 (parse Action của agent) + Tuần 5 (output báo cáo).
- **3 câu:** Agent đang parse `Action: tool(arg)` bằng **regex** rất dễ vỡ → ép LLM xuất đúng JSON Schema (**function calling** / thư viện **Outlines**) để agent sau luôn parse được. **KHÔNG dùng** khi output là văn xuôi tự do.
- **Công sức:** ~0.5 ngày. Chặn bug runtime thật (LLM thêm câu dẫn làm hỏng JSON).

### Món 6 — Kinh tế Long-Context vs RAG + Self-Route/Pre-Route
- **Chèn:** Tuần 7 (ngân hàng phỏng vấn) — xem **Câu 11** ở mục Ngân Hàng Đáp Án Mẫu.
- **3 câu:** "Context 1M token rồi RAG chết chưa?" → chưa, vì prefill O(n²) + **KV-cache ngốn VRAM** + lost-in-the-middle + RAG là **màng lọc Row-Level Security**; tối ưu bằng Self-Route (thử RAG trước) / Pre-Route (model nhỏ định tuyến trước). **KHÔNG dùng** long-context thuần khi đa user / dữ liệu nhạy cảm phân quyền.
- **Công sức:** **0 code** — pure knowledge, ROI cao nhất nhóm. Đúng kiểu câu hiring manager 2026 hay hỏi.

### Món 7 — Observability bằng LangSmith / Arize Phoenix
- **Chèn:** Tuần 4–5 (đi kèm LangGraph).
- **3 câu:** "Log token/latency" thành "tôi **trace** được từng bước agent, bắt nút thắt + loop vô hạn" → đổi từ `print`/jsonl sang công cụ trace. **KHÔNG dùng** khi chạy 1 phát rồi bỏ.
- **Công sức:** ~0.5 ngày. Biến 1 dòng CV thành "production-minded".

> **Điểm cắt nếu trễ (REV 2/7):** Món 1 (rerank) ĐÃ XONG (Ngày 11). Món 5 (structured output) nay **BẮT BUỘC từ Ngày 15** (schema findings của auditor — không cắt được). Món 6 (0 code) giữ. Thứ tự cắt mới: **Món 2 (CRAG)** trước tiên — retrieval đã đóng băng, evaluator tự chấm retrieval ít giá trị → **Món 7 (observability**, fallback jsonl) → **Món 4 (judge**, fallback chấm tay).

---

## 🧠 MODULE BỔ SUNG — Tầng Memory cho Agent (Agent có trí nhớ dài hạn)

> **Vì sao thêm (chốt 29/6):** đối chiếu bản đồ hệ-agent production (video "4 AI buzzwords"), lộ trình đã phủ kín 2 ô NGÁCH (**retrieval** + **LLM Ops/eval**) nhưng thiếu **tầng memory đầy đủ** — *episodic memory* (lịch sử hội thoại) + *consolidation/summarizer*. Đây là ô **KỀ** (không phải lõi ngách retrieval/eval) nên **KHÔNG nằm trên đường tới CV** — build để *đi làm khỏi học gấp*, hiểu sâu lúc còn học. **Slot linh hoạt:** chèn sau **Tuần 5** (khi agent đã có tool + LangGraph) hoặc đẩy sang **tháng 9**. ~2–3 buổi. Lý thuyết đã ghi sẵn ở `NOTES.md` mục "TẦNG MEMORY".

### Buổi M1 — Episodic Memory: "RAG cho liên quan + SQL cho gần đây"
- **Bài toán:** Agent stateless — mỗi lần chạy quên sạch. Nhồi hết lịch sử chat vào context thì tốn token + lost-in-the-middle. Cần trí nhớ NGOÀI, lấy ra ĐÚNG phần cần.
- **Build:** lưu mỗi lượt hội thoại vào **SQLite** (cột `timestamp`) + embed vào vector store (tái dùng `mini_rag`/Chroma). Khi có câu mới: lấy **k lượt LIÊN QUAN** (RAG cosine) + **m lượt GẦN NHẤT** (SQL `ORDER BY ts DESC`) → ghép context. Đúng nhánh "RAG for relevance + SQL for recency" trên bản đồ; xác nhận note Ngày 2 (exact/recency → DB).
- **Đo / KHÔNG dùng:** hỏi câu tham chiếu lượt cũ ("lúc nãy tôi nói shop tên gì?") — có episodic thì trả đúng, không thì bịa. **KHÔNG dùng** khi hội thoại 1 lượt.
- **Công sức:** ~1 buổi. Lấy `SQLiteDocumentStore` của `support-rag-assistant` làm mẫu (đừng copy — đọc rồi viết lại).

### Buổi M2 — Consolidation + Summarizer Agent (gộp chat → facts)
- **Bài toán:** episodic chứa chat THÔ phình vô hạn → retrieval chậm + nhiễu + vẫn tốn token.
- **Build:** sau **N lượt**, một **summarizer agent dùng model RẺ** (gemini-flash-lite / DeepSeek) chắt lượt cũ thành **facts bền** ("user tên A, shop bán cà phê") → đẩy vào **semantic memory**; lượt thô archive. Đúng ô "Summarizer Agent (cheaper models) → distill into facts" trên bản đồ.
- **Đánh đổi / KHÔNG dùng:** summarize CÓ mất mát — chi tiết nén đi có thể cần lại; chỉ gộp khi lịch sử đủ dài. Cân N (sớm = mất chi tiết; muộn = phình).
- **Công sức:** ~0.5–1 buổi. 💬 Câu phỏng vấn vàng: *"vì sao summarizer dùng model rẻ, không dùng model chính?"* → tác vụ dễ (tóm tắt) + chạy nền nhiều lần ⇒ tối ưu chi phí (nối Ngày 6).

### (Tùy chọn) Buổi M3 — Procedural Memory / Skills
- **3 câu:** hành vi agent ("cách audit code") không nên hardcode trong prompt → tách ra **file `Skill.md`** nạp vào working memory khi cần → linh hoạt + version được. **KHÔNG dùng** khi chỉ 1 hành vi cố định.
- **Công sức:** ~0.5 buổi (nhẹ — chủ yếu là pattern tổ chức file, đúng kiểu skill mà chính Claude Code đang dùng).

> **Lưu ý scope:** module này **KHÔNG ưu tiên hơn** 2 ô niche. Nếu kẹt thời gian trước 13/8 → đẩy hết sang tháng 9; CV vẫn đủ mạnh với retrieval + eval. Giá trị ở đây là **chiều sâu để đi làm**, không phải bullet CV.

---

## 🏢 MODULE BỔ SUNG — Demo #2: Internal Knowledge Base đa phòng ban (synthetic + RLS)

> **Vì sao thêm (chốt 29/6):** AI Code Auditor chứng minh retrieval+eval trên **code**. Demo #2 chứng minh kỹ năng **CHUYỂN DOMAIN** (không dính chết vào code) + thêm 2 thứ enterprise mà demo RAG thường bỏ qua: **phân quyền (RLS)** và **đo rò rỉ**. **Slot linh hoạt:** sau Demo #1 / Tuần 6 stretch / **tháng 9**. ~3–4 buổi. 3 thứ CV thèm: (1) chuyển domain, (2) **retrieval = bảo mật, không chỉ search**, (3) vẫn **đo được bằng số**.

### Buổi E1 — Sinh synthetic corpus đa phòng ban + golden set
- **Bài toán:** không có data thật của công ty → tự tạo. Nhưng data ảo dễ **quá sạch** → demo đẹp hơn thực tế.
- **Build:** nhờ LLM sinh **4 phòng ban** (HR / Finance / Engineering / Legal), mỗi phòng vài chục doc; mỗi doc gắn metadata `department` + `access_level` (vd public / staff / manager / exec). **Cố ý nhét nhiễu:** thuật ngữ chồng chéo giữa phòng, 2 doc mâu thuẫn, near-duplicate xuyên phòng → mới lộ bài toán distractor thật.
- **Golden set 3 loại câu:** (a) in-scope 1 phòng, (b) **cross-department** (câu chạm 2 phòng), (c) **câu kiểm tra phân quyền** (user thấp quyền hỏi doc cấp cao → hệ PHẢI từ chối, KHÔNG được lộ).
- **KHÔNG dùng / Công sức:** ~1 buổi. Đừng sinh 10k doc — **thật ở cấu trúc + edge-case, không ở số lượng**.

### Buổi E2 — Access control = Row-Level Security (lọc TRƯỚC retrieval)
- **Bài toán:** nếu lọc quyền *sau* khi retrieve (hoặc để LLM tự "đừng nói") → doc cấm vẫn lọt vào prompt = **rò rỉ**. LLM không phải lớp bảo mật.
- **Build:** user mang 1 `role/clearance` → **lọc tập ứng viên theo quyền NGAY TRƯỚC** vector/keyword search → chỉ doc được phép mới tới được prompt. Đây đúng "RAG là màng lọc Row-Level Security" (note Beyond-RAG) — biến retrieval từ *search* thành *secure access*.
- **3 câu / KHÔNG dùng:** vấn đề = LLM tin context mù → giải pháp = chặn ở **tầng retrieval**, không ở prompt → **KHÔNG dùng** khi mọi user cùng quyền (khỏi RLS cho nhẹ).
- **Công sức:** ~1 buổi. Tái dùng filter metadata của Demo #1 (Ngày 14) — mở rộng từ `type=code/doc` sang `department`/`access_level`.

### Buổi E3 — Đo: precision@3 + "leak rate" (đòn chốt của demo)
- **Bài toán:** demo bảo mật phải **chứng minh bằng số**, không bằng lời.
- **Đo 2 trục:** **precision@3** theo từng phòng (chất lượng) + **leak rate** = số lần hệ surface 1 doc user KHÔNG được xem (bảo mật). **Leak rate phải = 0.**
- **Đòn chốt (so baseline):** chạy **không-RLS** → user thấp quyền **moi được** thông tin cấm (lỗ hổng thật, đo được) → bật RLS → **leak = 0**, precision không đổi. 💬 Câu phỏng vấn vàng: *"vì sao lọc quyền phải ở tầng retrieval chứ không phải dặn LLM 'đừng trả lời'?"*
- **Công sức:** ~1 buổi. Tái dùng khung `eval_set.py` — thêm 1 hàm chấm leak (đừng copy, mở rộng).

> **Lưu ý scope:** Demo #2 **sau** Demo #1 (đừng làm song song loãng cả hai). Nếu trễ → tháng 9. Nhưng nếu kịp, cặp "Code Auditor + KB đa phòng ban có RLS" là **portfolio mạnh hiếm** ở fresher: chứng minh kỹ năng **chuyển domain + tư duy bảo mật + đo lường**, đúng 3 thứ tách bạn khỏi đám "ráp RAG demo".
