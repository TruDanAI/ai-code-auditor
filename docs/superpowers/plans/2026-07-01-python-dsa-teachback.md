# Kế Hoạch Thực Thi — Giai Đoạn A: Nền Python theo bản chất (teach-back)

> **Cho người thực thi:** Đây KHÔNG phải plan code cho máy chạy — đây là **lịch học** do
> chính người học thực thi mỗi ngày CÙNG mentor. Mỗi "Task" = 1 buổi ~45–60'. Đánh dấu
> `- [ ]` để theo dõi. Nguồn: [spec teach-back](../specs/2026-07-01-python-dsa-teachback-design.md).

**Mục tiêu:** Vững 7 khái niệm Python nền tới mức qua **bài test 60 giây** (dạy lại được), mỗi
khái niệm neo vào code thật trong `mini_rag.py` và chốt thành 1 trang playbook.

**Cách tiếp cận:** Mỗi buổi chạy **vòng 5 bước** (nhắc lại → giảng bản chất → đọc code mẫu →
nói lại → tự tay → chốt playbook). Ví dụ ưu tiên lấy từ `mini_rag.py`. Bài tự làm KHÔNG kèm
đáp án (quy ước "review chứ không sửa hộ").

**Công cụ:** Python 3, `mini_rag.py` (đã implement), venv trên `E:\venvs\ai-code-auditor`.

## Global Constraints (áp cho MỌI buổi)

- **Cổng "xong" = test 60 giây:** nói lại cho người không biết gì, KHÔNG nhìn note, đủ 4 ý
  (vấn đề nếu không có → cách hoạt động → khi nào KHÔNG dùng → 1 số neo). Chưa qua → chưa sang buổi sau.
- **Bám cổng, không bám lịch:** qua cổng thì được gộp 2 buổi thành 1; vấp thì chậm lại đúng chỗ đó.
- **Quy ước dạy học (CLAUDE.md):** 3-câu · không dump code · pause-30s hỏi 1 câu · reflex Q&A cuối buổi ·
  review không sửa hộ · cập nhật `NOTES.md` cuối buổi.
- **Ví dụ ưu tiên từ auditor:** trước khi bịa ví dụ, tìm trong `mini_rag.py` / `ai-workflow-engine` / `support-rag-assistant`.
- **Mỗi buổi kết bằng 1 file playbook + commit.**

---

## Task 0: Dựng khung Playbook

**Files:**
- Create: `docs/python-dsa-playbook/README.md`
- Create: `docs/python-dsa-playbook/_TEMPLATE.md`

**Interfaces:**
- Produces: thư mục playbook + template mà mọi buổi sau đổ nội dung vào.

- [ ] **B1: Tạo template** `_TEMPLATE.md` với đúng các ô:

```markdown
# <Tên khái niệm>
```mermaid
%% sơ đồ bản chất, điền khi học
```
- **Vấn đề nếu không có nó:**
- **Cách hoạt động bên dưới:**
- **Khi nào KHÔNG dùng:**
- 🔢 **Số neo:**
- 🎤 **Kịch bản dạy 60s:** "Nếu phải giải thích cho đồng nghiệp, tôi sẽ nói: ..."
- **Neo code auditor:** `mini_rag.py:<dòng>`
- **Bài đã tự làm:** <mô tả / link>
- 🔗 **Nội dung nguồn:** `dsa-cho-ky-su-ai.md §<n>` (nếu có)
```

- [ ] **B2: Viết `README.md`** liệt kê 7 khái niệm Giai đoạn A dạng checklist rỗng + 1 câu:
  "Mỗi file = 1 khái niệm đã qua cổng test 60s. Trỏ về [spec](../superpowers/specs/2026-07-01-python-dsa-teachback-design.md)."

- [ ] **B3: Commit**

```bash
git add docs/python-dsa-playbook/
git commit -m "docs(playbook): khung + template Giai doan A"
```

---

## Task 1: Mô hình bộ nhớ — nhãn, tham chiếu vs copy, mutable vs immutable

**Files:**
- Read: `mini_rag.py:331` (`chunk_copy = dict(index["chunks"][i])`) và `mini_rag.py:402-410` (comment "KHÔNG mutate... list gốc nguyên vẹn").
- Create: `docs/python-dsa-playbook/01-memory-reference-vs-copy.md`

**Interfaces:**
- Consumes: —
- Produces: playbook entry #01 + cổng 60s đã qua.

- [ ] **B1 (nhắc lại):** — (buổi đầu, bỏ qua)
- [ ] **B2 (bản chất):** mentor giảng 4 câu hỏi. Neo số: **gán `=` KHÔNG copy — chỉ dán thêm 1 nhãn lên cùng 1 object**. 3-câu: (1) không phân biệt → sửa bản sao mà hỏng bản gốc; (2) biến = nhãn trỏ tới object, `dict(x)`/`x[:]` mới tạo object mới; (3) copy vô tội vạ tốn RAM khi object lớn.
- [ ] **B3 (code mẫu):** đọc `mini_rag.py:331` — hỏi: *vì sao `retrieve_top_k` phải `dict(...)` chứ không gán thẳng?* (pause-30s trước khi mentor trả lời).
- [ ] **B4 (nói lại):** người học giải thích dòng 331 bằng lời mình, 60s.
- [ ] **B5 (tự tay — KHÔNG đáp án):** trong shell, **đoán TRƯỚC khi chạy**:
  `a=[1,2]; b=a; b.append(3); print(a)` → rồi lặp lại với `b=a[:]`. Giải thích khác biệt và nối về dòng 331.
- [ ] **B6 (cổng 60s + playbook + commit):** qua test 60s → điền `01-...md` (nhớ Mermaid: 2 nhãn → 1 hộp object) →

```bash
git add docs/python-dsa-playbook/01-memory-reference-vs-copy.md NOTES.md
git commit -m "docs(playbook): 01 memory reference-vs-copy"
```

---

## Task 2: list vs dict vs set (hash table) + Big-O tra cứu

**Files:**
- Read: `mini_rag.py:292-303` (`rrf_fuse`: `scores={}`, `scores.get(key,0.0)`), `mini_rag.py:44` (`IGNORE_DIRS = {...}` set), `mini_rag.py:546` (set comprehension đếm file).
- Create: `docs/python-dsa-playbook/02-list-dict-set.md`

**Interfaces:**
- Consumes: nhắc lại #01.
- Produces: playbook #02 + cổng 60s.

- [ ] **B1 (nhắc lại #01):** mentor đóng vai người mới hỏi "copy khác gán chỗ nào?".
- [ ] **B2 (bản chất):** neo số **dict/set tra cứu O(1), tìm trong list O(n)**. 3-câu: (1) dùng list để "đã thấy chưa?" → chậm dần khi to; (2) dict/set băm key → nhảy thẳng ô nhớ; (3) cần thứ tự/trùng lặp thì list, không dùng set.
- [ ] **B3 (code mẫu):** `rrf_fuse` dùng `dict` làm sổ cộng dồn điểm; `IGNORE_DIRS` là `set` để check `d not in IGNORE_DIRS` nhanh. Hỏi: *vì sao IGNORE_DIRS là set chứ không list?* (pause-30s).
- [ ] **B4 (nói lại):** người học giải thích `scores.get(key, 0.0)` làm gì và vì sao là dict.
- [ ] **B5 (tự tay — KHÔNG đáp án):** trên 2 list key đồ chơi, tự viết lại vòng cộng dồn RRF bằng dict từ số 0; rồi thử làm SAI bằng list `[ (key,score) ]` và tự chỉ ra chỗ phải quét O(n).
- [ ] **B6 (cổng + playbook + commit):** điền `02-...md` (§ nguồn: `dsa-cho-ky-su-ai.md §2, §9`) →

```bash
git add docs/python-dsa-playbook/02-list-dict-set.md NOTES.md
git commit -m "docs(playbook): 02 list-dict-set"
```

---

## Task 3: Comprehension & slicing; enumerate / zip

**Files:**
- Read: `mini_rag.py:244` (`[c["content"] for c in all_chunks]`), `mini_rag.py:336` (`scored[:k]`), `mini_rag.py:366` (`np.argsort(scores)[::-1][:k]`), `mini_rag.py:297` (`enumerate(ranked_list, start=1)`), `mini_rag.py:406` (`zip(candidates, scores)`).
- Create: `docs/python-dsa-playbook/03-comprehension-slicing.md`

**Interfaces:**
- Consumes: nhắc lại #02.
- Produces: playbook #03 + cổng 60s.

- [ ] **B1 (nhắc lại #02):** "khi nào KHÔNG dùng set?"
- [ ] **B2 (bản chất):** neo số **`[::-1]` = đảo, `[:k]` = lấy k đầu**. 3-câu: (1) không có → vòng for dài dòng, dễ sai off-by-one; (2) comprehension = "biến đổi từng phần tử thành list mới" gọn 1 dòng; (3) khi logic phức tạp/nhiều nhánh thì for tường minh dễ đọc hơn — đừng nhồi.
- [ ] **B3 (code mẫu):** dịch dòng 366 `np.argsort(scores)[::-1][:k]` ra lời ("sắp tăng dần → đảo → lấy top-k"). Hỏi: *`enumerate(..., start=1)` ở dòng 297 khác gì `start=0`, vì sao RRF cần start=1?* (pause-30s).
- [ ] **B4 (nói lại):** người học đọc dòng 244 thành câu tiếng Việt đầy đủ.
- [ ] **B5 (tự tay — KHÔNG đáp án):** viết lại comprehension dòng 244 thành for-loop tường minh, rồi ngược lại; giải thích `zip` ở dòng 406 ghép gì với gì.
- [ ] **B6 (cổng + playbook + commit):**

```bash
git add docs/python-dsa-playbook/03-comprehension-slicing.md NOTES.md
git commit -m "docs(playbook): 03 comprehension-slicing"
```

---

## Task 4: Hàm — tham số, `*args`/`**kwargs`, phạm vi biến, cạm bẫy default `[]`

**Files:**
- Read: `mini_rag.py:81` (`_merge_small_chunks(chunks, target=MERGE_TARGET_SIZE)`), `mini_rag.py:307` (`retrieve_top_k(..., k=TOP_K)`), `mini_rag.py:209` (`load_embedding_model(model_name=..., device=None)`).
- Create: `docs/python-dsa-playbook/04-functions-scope-defaults.md`

**Interfaces:**
- Consumes: nhắc lại #03.
- Produces: playbook #04 + cổng 60s.

- [ ] **B1 (nhắc lại #03):** "`[::-1]` làm gì?"
- [ ] **B2 (bản chất):** neo số **default `[]`/`{}` bị CHIA SẺ qua mọi lần gọi** (đánh giá 1 lần lúc định nghĩa). 3-câu: (1) default mutable → lần gọi sau thấy rác của lần trước; (2) dùng `None` rồi tạo mới bên trong; (3) default bất biến (số, tuple, hằng như `TOP_K`) thì an toàn. *(Phụ, không có trong code: `*args`/`**kwargs` = "gom số lượng tham số tuỳ ý thành tuple/dict" — mentor mô tả 30s, chưa cần bài tập riêng.)*
- [ ] **B3 (code mẫu):** `mini_rag.py` toàn dùng default **bất biến** (`k=TOP_K`, `device=None`, `target=MERGE_TARGET_SIZE`) — chỉ ra vì sao đây là code đúng, KHÔNG dính bẫy. Hỏi: *phạm vi biến `buf` trong `_merge_small_chunks` sống ở đâu?* (pause-30s).
- [ ] **B4 (nói lại):** người học giải thích vì sao `device=None` rồi xử lý bên trong tốt hơn `device="cpu"` cứng.
- [ ] **B5 (tự tay — KHÔNG đáp án):** cố tình viết `def f(x, acc=[])` rồi gọi 3 lần, quan sát rác dồn lại; sửa bằng `None`. Tự phát biểu quy tắc.
- [ ] **B6 (cổng + playbook + commit):**

```bash
git add docs/python-dsa-playbook/04-functions-scope-defaults.md NOTES.md
git commit -m "docs(playbook): 04 functions-scope-defaults"
```

---

## Task 5: Generator & `yield`

> ⚠️ Khái niệm này **CHƯA có trong `mini_rag.py`** (chunk_text dựng list, không yield). Dạy theo hướng
> "nó sẽ nằm ở đâu nếu thêm" — đây là điểm nâng cấp thật của chunking.

**Files:**
- Read: `mini_rag.py:183-191` (vòng dựng `final_chunks` — nơi generator sẽ thay thế).
- Create: `docs/python-dsa-playbook/05-generator-yield.md`

**Interfaces:**
- Consumes: nhắc lại #04.
- Produces: playbook #05 + cổng 60s.

- [ ] **B1 (nhắc lại #04):** "bẫy default `[]` là gì?"
- [ ] **B2 (bản chất):** neo số **generator giữ 1 phần tử trong RAM tại một thời điểm, không phải cả list**. 3-câu: (1) file khổng lồ → dựng cả list chunk ngốn RAM; (2) `yield` trả từng cái, tính tới đâu nhả tới đó (lazy); (3) cần dùng lại/đánh index nhiều lần thì generator dở (chỉ duyệt 1 lần) — lúc đó cần list.
- [ ] **B3 (code mẫu):** nhìn vòng `for chunk in chunks:` dòng 184 — mentor mô tả phiên bản `yield piece` sẽ khác gì. Hỏi: *nếu `chunk_text` thành generator thì dòng 239 `all_chunks.extend(...)` còn chạy được không?* (pause-30s).
- [ ] **B4 (nói lại):** người học phân biệt "list = nấu sẵn cả nồi" vs "generator = nấu tới đâu ăn tới đó".
- [ ] **B5 (tự tay — KHÔNG đáp án):** viết 1 generator `gen_pieces(text, size)` yield từng lát; so `sum(1 for _ in gen)` với `len(list(gen))`; giải thích vì sao chạy `list(gen)` xong thì gen "cạn".
- [ ] **B6 (cổng + playbook + commit):**

```bash
git add docs/python-dsa-playbook/05-generator-yield.md NOTES.md
git commit -m "docs(playbook): 05 generator-yield"
```

---

## Task 6: OOP tối thiểu — `class`/`self`/`__init__`; khi nào cần class vs hàm

> ⚠️ `mini_rag.py` hiện **toàn hàm module-level, KHÔNG có class**. Dạy qua bài tập gói lại — đúng gợi ý
> `class Index` trong [ke-hoach](../../ke-hoach-nen-tang-python-dsa.md).

**Files:**
- Read: `mini_rag.py:232-247` (`build_index` trả dict `{"chunks":..., "embeddings":...}`) và `mini_rag.py:307` (`retrieve_top_k(query_embedding, index, ...)`).
- Create: `docs/python-dsa-playbook/06-oop-class-vs-function.md`

**Interfaces:**
- Consumes: nhắc lại #05.
- Produces: playbook #06 + cổng 60s.

- [ ] **B1 (nhắc lại #05):** "khi nào KHÔNG dùng generator?"
- [ ] **B2 (bản chất):** neo số **class = dữ liệu (state) + hàm dùng chung state, gói làm 1**. 3-câu: (1) nhiều hàm cứ phải truyền qua lại cùng 1 `index` dict → rườm; (2) `class Index` giữ `chunks`+`embeddings` trong `self`, `self.search(q)` khỏi truyền index; (3) chỉ 1-2 hàm không chia sẻ state → class là thừa, hàm gọn hơn.
- [ ] **B3 (code mẫu):** chỉ ra `index` dict bị truyền vào `retrieve_top_k`, `build_prompt`... — đó là state đang "trôi nổi". Hỏi: *`self` thực chất là gì khi gọi `idx.search(q)`?* (pause-30s).
- [ ] **B4 (nói lại):** người học nói rõ state nào nên nằm trong `self` (chunks, embeddings, model) vs cái nào là tham số (query).
- [ ] **B5 (tự tay — KHÔNG đáp án):** viết khung `class Index` với `__init__(self, root_dir, model)` gọi `build_index`, và `search(self, question, k=TOP_K)` gọi lại logic `retrieve_top_k`. Không cần chạy hoàn hảo — cần giải thích được từng dòng.
- [ ] **B6 (cổng + playbook + commit):**

```bash
git add docs/python-dsa-playbook/06-oop-class-vs-function.md NOTES.md
git commit -m "docs(playbook): 06 oop-class-vs-function"
```

---

## Task 7: Xử lý lỗi `try/except`; context manager `with`

**Files:**
- Read: `mini_rag.py:68-74` (`with open(...)` + `except (UnicodeDecodeError, OSError): continue`), `mini_rag.py:515-521` (`call_gemini` raise `RuntimeError` với hướng dẫn).
- Create: `docs/python-dsa-playbook/07-try-except-with.md`

**Interfaces:**
- Consumes: nhắc lại #06.
- Produces: playbook #07 + cổng 60s.

- [ ] **B1 (nhắc lại #06):** "state nào nên vào `self`?"
- [ ] **B2 (bản chất):** neo số **`with` tự đóng file kể cả khi lỗi giữa chừng**. 3-câu: (1) không có → 1 file hỏng làm sập cả vòng index / file quên đóng rò tài nguyên; (2) `except (A, B)` bắt đúng loại lỗi rồi `continue` bỏ qua file rác; `with` bảo đảm đóng; (3) `except:` trần (bắt tất) che luôn bug thật — đừng nuốt lỗi mù.
- [ ] **B3 (code mẫu):** `load_files` bắt `UnicodeDecodeError, OSError` rồi `continue` (bỏ file không đọc được, không sập). `call_gemini` raise lỗi CÓ hướng dẫn set env. Hỏi: *vì sao bắt cụ thể 2 lỗi đó thay vì `except:` trần?* (pause-30s).
- [ ] **B4 (nói lại):** người học giải thích `with open(...)` khác `f=open(); f.close()` chỗ nào khi có lỗi.
- [ ] **B5 (tự tay — KHÔNG đáp án):** cho `load_files` đọc 1 file nhị phân (vd .png) → xem `except` nuốt nó; rồi đổi thành `except:` trần và tự chỉ ra vì sao nguy hiểm.
- [ ] **B6 (cổng + playbook + commit):**

```bash
git add docs/python-dsa-playbook/07-try-except-with.md NOTES.md
git commit -m "docs(playbook): 07 try-except-with"
```

---

## Task 8: Chốt Giai đoạn A — mock teach-back + trang tổng

**Files:**
- Create: `docs/python-dsa-playbook/00-INDEX-giai-doan-A.md`
- Modify: `docs/python-dsa-playbook/README.md` (tick 7 ô)

**Interfaces:**
- Consumes: cả 7 playbook entry.
- Produces: 1 trang tổng có Mermaid spine (đầu mối decision-playbook).

- [ ] **B1 (mock teach-back):** mentor đóng vai nhà tuyển dụng, bốc ngẫu nhiên 3 trong 7 khái niệm, người học chạy test 60s liên tiếp. Chỗ nào vấp → ghi ra để ôn (không sang Giai đoạn B nếu ≥2/7 vấp).
- [ ] **B2 (trang tổng):** viết `00-INDEX-...md` gồm 1 sơ đồ Mermaid nối 7 khái niệm theo "vấn đề → khái niệm giải" + bảng 1 dòng/khái niệm (số neo + link file).
- [ ] **B3 (reflex Q&A):** trả lời 2 câu phỏng vấn mentor đặt, theo công thức Cách làm + Tại sao + Đánh đổi.
- [ ] **B4 (commit):**

```bash
git add docs/python-dsa-playbook/00-INDEX-giai-doan-A.md docs/python-dsa-playbook/README.md NOTES.md
git commit -m "docs(playbook): chot Giai doan A + trang tong"
```

---

## Tiếp theo (ngoài plan này)
Qua cổng Giai đoạn A → viết plan **Giai đoạn B (DSA core)**: Big-O, array/string, hash map/set,
sort+heap/top-k, vector/dot product, đệ quy+binary search — mỗi buổi neo vào
`dsa-cho-ky-su-ai.md` (§0–§5) và `retrieve_top_k`/`rrf_fuse`.
