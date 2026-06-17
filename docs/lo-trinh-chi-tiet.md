# Lộ Trình Chi Tiết — AI Code Auditor

> **Bắt đầu:** 17/6/2026 (Thứ Ba) · **Mục tiêu:** Nộp CV ~ giữa tháng 8/2026 (≈ 2 tháng)
> **Cấu trúc:** 8.5 tuần — Tuần 1-7 học + xây dự án, **Tuần 8 = buffer chống trễ + luyện phỏng vấn + hoàn thiện CV**
> **Thời gian/ngày:** 5+ giờ · **Dữ liệu thực hành:** repo `chatbot-fanpage` (đã clone tại `C:\Users\Pc\Desktop\chatbot-fanpage`)
> **Cập nhật lần cuối:** 17/6/2026 (nâng cấp: giãn 2 tháng + thêm đáp án mẫu phỏng vấn)

> [!IMPORTANT]
> **Đọc trước khi bắt đầu:** phần [📚 Cách Dùng Tài Liệu + Công Thức Trả Lời Phỏng Vấn](#-cách-dùng-tài-liệu--công-thức-trả-lời-phỏng-vấn) ngay bên dưới. Mỗi ngày học giờ có thêm khối **💬 Đáp án mẫu** để bạn học cách *nói* được kiến thức, không chỉ *hiểu*.

---

## 🔴 Kiểm Tra Lỗi Thời — Những Gì Cần Sửa So Với Lộ Trình Cũ

Sau khi rà soát kỹ thuật tính đến 16/6/2026, có **4 điểm lỗi thời nghiêm trọng** trong lộ trình gốc:

| # | Vấn đề | Mức độ | Cách sửa |
|---|--------|--------|----------|
| 1 | **`google-generativeai` SDK đã bị khai tử** (30/11/2025). File `mini_rag.py` vẫn dùng `import google.generativeai as genai` + `genai.configure()` | 🔴 Chặn | Chuyển sang `google-genai` SDK mới. Dùng `client = genai.Client()` thay `genai.configure()` |
| 2 | **Model `gemini-1.5-flash` thuộc thế hệ cũ**. Gemini 2.0 đã shutdown 1/6/2026. Model hiện tại là `gemini-3.5-flash` | 🔴 Chặn | Đổi model name trong code sang `gemini-3.5-flash` |
| 3 | **`all-MiniLM-L6-v2` vẫn chạy được** nhưng đã bị vượt xa về chất lượng. State-of-the-art 2026 là Qwen3-Embedding, BGE-M3 | 🟡 Không chặn | Giữ MiniLM cho tuần 1 (nhẹ, chạy CPU, mục đích học). Upgrade lên model tốt hơn ở tuần 2 khi đo precision |
| 4 | **IBM Coursera đã có 10 khóa** (thêm khóa 9: MCP — Model Context Protocol, khóa 10: Capstone). Lộ trình cũ chỉ tính 8 khóa | 🟡 Điều chỉnh | Với 7 ngày trial, chỉ học 4–5 khóa quan trọng nhất, bỏ multimodal + capstone |

> **CẬP NHẬT 17/6/2026 (đã kiểm tra code thật):** `mini_rag.py` **ĐÃ được cập nhật sẵn** sang SDK `google-genai` mới (`from google import genai` + `genai.Client()` + `model="gemini-3.5-flash"`, xem dòng 241-253). Vì vậy buổi chiều Ngày 1 **không cần viết lại SDK** nữa — thay bằng **đọc-hiểu + xác minh chạy được** (so sánh SDK cũ vs mới). Môi trường `venv` cũng đã cài đủ `numpy`, `tiktoken`, `sentence-transformers`, `google-genai`; mắt xích duy nhất còn thiếu là biến môi trường `GEMINI_API_KEY` (set bằng `$env:GEMINI_API_KEY = "..."`).
>
> ✅ **[Đã xác minh 17/6/2026]** Bảng model trong `ban-do-cong-nghe-chi-phi.md` (mục II) đã được cập nhật: "Claude 3.5 Sonnet" → **Claude Sonnet 4.6** ($3/$15); "GPT-4o-mini" → dòng GPT nay là **GPT-5.4** ($2.50/$15); thêm **DeepSeek V3.2** ($0.14/$0.28 — rẻ nhất). **Lưu ý chi phí quan trọng:** `mini_rag.py` đang dùng `gemini-3.5-flash` — model *mới nhất* (19/5/2026) nhưng *đắt nhất họ Flash* ($1.50/$9.00). Cho **học** thì ổn; nhưng sang **vòng lặp agent** (Tuần 3+, gọi LLM nhiều lần) nên đổi sang `gemini-2.0-flash` ($0.10/$0.40) hoặc `gemini-3.1-flash-lite` để tiết kiệm.

---

## Cài Đặt Trước Khi Bắt Đầu (Làm tối 16/6)

```bash
# 1. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate        # Windows

# 2. Cài thư viện (ĐÃ CẬP NHẬT cho 6/2026)
pip install sentence-transformers numpy google-genai tiktoken

# 3. Set API key (PowerShell)
$env:GEMINI_API_KEY = "your_key_here"

# 4. Test nhanh SDK mới hoạt động
python -c "from google import genai; c = genai.Client(); print(c.models.generate_content(model='gemini-3.5-flash', contents='Hello').text)"
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
#   #1 bảng MTEB đa ngôn ngữ 2026 (~70.6), rất mạnh cho tiếng Việt.
#   model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")  # bản nhỏ, nhẹ hơn
# (bản 8B mạnh nhất nhưng nặng — bản 0.6B đủ tốt để học + chạy CPU/GPU phổ thông)

# Chạy lại eval_set, so sánh precision@3
```

Ghi lại kết quả so sánh (điền số thật để đưa vào CV):
```
| Model               | Precision@3 | Ghi chú                          |
|---------------------|-------------|----------------------------------|
| all-MiniLM-L6-v2    | ??%         | 80MB, nhanh, baseline tuần 1    |
| BAAI/bge-m3         | ??%         | ~2GB, đa ngôn ngữ tốt           |
| Qwen3-Embedding-0.6B| ??%         | SOTA đa ngôn ngữ 2026, hợp VN   |
```

> 💡 *Đây chính là số liệu vàng cho CV: "Cải thiện precision@3 từ X% (MiniLM) lên Y% bằng cách đổi sang Qwen3-Embedding".*

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
> **Tài liệu tham khảo:** Đọc Phần I, II, III của [Bản Đồ Quyết Định Công Nghệ & Chi Phí](file:///c:/Users/Pc/Desktop/Build%20CV/ai-code-auditor/docs/ban-do-cong-nghe-chi-phi.md) để nắm vững mô hình ReAct Agent, so sánh chi phí các model khi chạy vòng lặp Agent (ví dụ: vì sao dùng GPT-4o-mini/Gemini 3.5 Flash cho agent loop).

**Mục tiêu tuần:** Hiểu pattern ReAct, viết vòng lặp agent cơ bản, thêm tool thật.

> Lộ trình cũ đặt Agent ở tuần 4. Đẩy lên tuần 3 vì: (1) phần hấp dẫn nhất, giữ động lực; (2) cần thời gian nhiều hơn cho multi-agent + MCP ở tuần sau.

---

### Ngày 15 (Thứ Ba 1/7) — Pattern ReAct: Hiểu trước khi code

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

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
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
            model="gemini-3.5-flash", contents=messages
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

### Ngày 16 (Thứ Tư 2/7) — Debug agent, thêm tool

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

### Ngày 17 (Thứ Năm 3/7) — Kết hợp RAG + Agent

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

### Ngày 18–19 (Thứ Sáu–Thứ Bảy 4–5/7) — Logging + Bài tập tương tự

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

### Ngày 20–21 (Chủ Nhật–Thứ Hai 6–7/7) — Ôn + Commit

---

## TUẦN 4: IBM Coursera Sprint (7 ngày trial)

**Mục tiêu:** Học 5 khóa quan trọng nhất trong 7 ngày free trial.

> **QUAN TRỌNG:** Đăng ký trial ngày 8/7 (Thứ Ba). Trial hết hạn 14/7.

| Ngày trial | Khóa | Thời gian | Ghi chú |
|-----------|------|-----------|---------|
| 1 (8/7) | Khóa 1: Develop GenAI Apps: Get Started | 3-4h | Đối chiếu với `call_gemini` đã viết |
| 2 (9/7) | Khóa 2: Build RAG Applications | 4-5h | **Quan trọng nhất** — map về `mini_rag.py` |
| 3 (10/7) | Khóa 3: Vector DBs for RAG | 3-4h | Đối chiếu ChromaDB tuần 2 |
| 4 (11/7) | Khóa 6: Fundamentals of Building AI Agents | 4-5h | Đối chiếu `agent.py` tuần 3 |
| 5 (12/7) | Khóa 7: Agentic AI with LangChain + LangGraph | 5h | **Framework chính** cho tuần 5 |
| 6 (13/7) | Khóa 9: Build AI Agents using MCP | 4h | **Concept mới 2026** |
| 7 (14/7) | Buffer / Hoàn thành quiz / Lấy chứng chỉ | 3-4h | Pass tất cả quiz |

**Bỏ qua:** Khóa 4 (đã tự đo precision), Khóa 5 (Multimodal), Khóa 8 (CrewAI/AutoGen — lướt nếu dư thời gian), Khóa 10 (Capstone).

Mỗi khái niệm LangChain/LangGraph học xong, mở `mini_rag.py` hoặc `agent.py` và ghi: "cái này tương đương hàm nào tôi đã tự viết?" Ghi vào NOTES.md.

---

## TUẦN 5: Multi-Agent + LangGraph

> [!TIP]
> **Tài liệu tham khảo:** Đọc Phần I (Cấp độ 4), Phần IV (OpenRouter vs Gemini API) và Phần V của [Bản Đồ Quyết Định Công Nghệ & Chi Phí](file:///c:/Users/Pc/Desktop/Build%20CV/ai-code-auditor/docs/ban-do-cong-nghe-chi-phi.md) để so sánh các nhà cung cấp mô hình và học cách tích hợp Streamlit UI cho dự án.

**Mục tiêu tuần:** Tách agent thành 2–3 agent phối hợp, dùng LangGraph.

### Ngày 29 (Thứ Ba 15/7) — Setup LangGraph project

```bash
pip install langgraph langchain-google-genai
```

### Ngày 30–31 (16–17/7) — Tách ai-code-auditor thành 2–3 agent

Kiến trúc:
```
User Question
     |
     v
[Router Agent] -> Quyết định route câu hỏi
     |
  +--+--+
  v     v
[Code   [Explain
Finder]  Agent] -> Nhận chunks, viết câu trả lời
  |        |
  |   [Reviewer] -> Kiểm tra answer có khớp evidence
  |
  +-> Tools: grep, read_file, rag_search, run_tests
```

### Ngày 32–33 (18–19/7) — MCP integration (nếu kịp)

MCP (Model Context Protocol) là chuẩn mới 2025–2026. Expose tools qua MCP protocol để bất kỳ AI client nào cũng gọi được. Nếu bạn học kịp Coursera khóa 9, implement ở đây. Nếu không, bỏ qua.

### Ngày 34–35 (20–21/7) — Testing multi-agent + commit

---

## TUẦN 6: Deploy + Áp Dụng Ngược Lại Dự Án 1

### Ngày 36–37 (Thứ Ba–Thứ Tư 22–23/7) — Docker + Deploy

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "agent.py"]
```

Deploy lên Railway (đồng bộ platform với chatbot-fanpage).

### Ngày 38–39 (24–25/7) — Audit thật chatbot-fanpage

Dùng agent chạy câu hỏi audit:
- "File nào lớn nhất và nên tách ra?"
- "Có chỗ nào hardcode secret không?"
- "README mô tả SHOP_ID mặc định có khớp với code không?"

Mở chatbot-fanpage ra sửa. Đọc kỹ code trước khi sửa. Commit message giải thích rõ vì sao.

### Ngày 40–42 (26–28/7) — README + Architecture doc

Viết README.md cho `ai-code-auditor`:
- Mục tiêu dự án, kiến trúc (sơ đồ agent)
- Số liệu: precision@3, thời gian phản hồi, số chunk indexed
- Cách chạy, link tới chatbot-fanpage như case study

---

## TUẦN 7: CV + Luyện Phỏng Vấn

### Ngày 43–44 (Thứ Ba–Thứ Tư 29–30/7) — Viết CV bullet

**Dự án 1 (chatbot-fanpage):**
```
- Vận hành production chatbot Messenger cho shop thật trên Railway
  (webhook HMAC-SHA256, credential AES-256-GCM, RBAC 4 roles)
- Quản lý codebase 226 commits, 945 tests pass, multi-tenant
```

**Dự án 2 (ai-code-auditor):**
```
- Xây RAG pipeline từ zero: chunking, embedding, vector search,
  prompt grounding (precision@3 từ ??% lên ??%)
- Multi-agent system (LangGraph): Code Finder + Explainer + Reviewer
- Deploy Docker/Railway, logging chi phí/latency cho mỗi LLM call
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

---

## 🎤 NGÂN HÀNG ĐÁP ÁN MẪU — 10 CÂU PHỎNG VẤN CỐT LÕI

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

## TUẦN 8: Buffer + Sprint Phỏng Vấn (5/8 – ~13/8)

> **Mục tiêu:** không học kiến thức mới. Dùng tuần này để (1) bù các phần bị trễ, (2) đánh bóng dự án + CV, (3) luyện nói đến mức trả lời trôi chảy. Đây là tuần biến "đã làm" thành "kể được hay".

### Ngày 50–51 — Buffer bù tiến độ
Hoàn thành nốt bất kỳ mục nào còn dang dở của Tuần 1-7 (ưu tiên theo mục "Điểm Cắt Nếu Trễ Tiến Độ" bên dưới — làm ngược lại: bù phần quan trọng trước). Nếu không trễ gì → dùng để thêm 1 tính năng nhỏ gây ấn tượng (vd hiển thị citation đẹp trên UI).

### Ngày 52–53 — Đánh bóng dự án & CV
- Rà lại README `ai-code-auditor`: có sơ đồ kiến trúc, số liệu (precision@3, latency, chi phí/query, số chunk) chưa.
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

## Điểm Cắt Nếu Trễ Tiến Độ

Cắt từ trên xuống:
1. **MCP integration (tuần 5)** — concept mới nhưng không bắt buộc cho CV fresher
2. **Agent phản biện thứ 3 (tuần 5)** — giữ 2 agent đủ
3. **So sánh embedding model (ngày 10)** — giữ 1 model cũng OK
4. **Coursera khóa 9 (MCP)** — bỏ nếu không kịp 7 ngày

**KHÔNG CẮT:**
- Tuần 1 (RAG tự tay) — nền tảng mọi thứ
- Agent cơ bản (tuần 3) — câu chuyện CV chính
- Deploy (tuần 6) — nhà tuyển dụng muốn thấy production
- Precision@3 (tuần 2) — số liệu cụ thể cho CV
