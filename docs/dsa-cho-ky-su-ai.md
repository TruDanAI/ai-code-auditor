# DSA CHO KỸ SƯ AI — Cấu trúc dữ liệu & Giải thuật gắn với RAG / AI Code Auditor

> **Mục đích của tài liệu này:** Mày đang học DSA ở trường mà thấy trừu tượng, khó móc vào đâu.
> Tài liệu này lật ngược cách học: thay vì học chay để thi, mỗi khái niệm DSA ở đây được giải thích
> qua **chính project RAG / AI Code Auditor mày đang xây**. Học kiểu "DSA phục vụ project" vào đầu
> gấp nhiều lần học chay.
>
> **Cách dùng:** Đọc cột "Xuất hiện ở đâu trong project" trước. Khi thấy nó dính tới file mày đang
> code (`mini_rag.py`, `ai-workflow-engine`, `support-rag-assistant`) thì học sâu phần đó. Phần nào
> chưa đụng tới thì đọc lướt, để dành.
>
> **Mỗi mục theo quy tắc 3 câu:** (1) Vấn đề nếu không có → (2) Nguyên lý & logic → (3) Giới hạn / khi nào KHÔNG dùng.

---

## BẢN ĐỒ TỔNG QUAN — DSA nào dính tới AI ở mức nào

| Ưu tiên | Chủ đề | Bài toán AI điển hình | File trong project mày |
|---|---|---|---|
| 🔴 Nền tảng bắt buộc | **Big-O** | Hiểu vì sao brute-force chết ở triệu vector | `mini_rag.py` retrieve |
| 🔴 Phải hiểu sâu | **Array / Dynamic Array** | Ma trận embedding `(N, 384)`, batch | `mini_rag.py`, numpy |
| 🔴 Phải hiểu sâu | **Hashmap / Dict** | Cache embedding, inverted index, dedup | BM25, cache |
| 🔴 Phải hiểu sâu | **Heap / Priority Queue** | **Lấy top-k kết quả** (trái tim của retrieval) | `retrieve_top_k` |
| 🟡 Hiểu khái niệm | **Sorting** | Rank kết quả theo điểm | hybrid merger |
| 🟡 Hiểu khái niệm | **Binary Search** | Tra cứu nhanh trong mảng đã sort | nâng cao |
| 🟡 Hiểu khái niệm | **Tree (BST, B-Tree)** | Index của database, SQLite | `SQLiteDocumentStore` |
| 🟡 Hiểu khái niệm | **Graph + BFS/DFS** | **HNSW** — xương sống vector DB | Tuần 2: vector DB |
| 🟢 Biết là đủ | **Stack / Queue** | Agent loop, BFS traversal, undo | Tuần 3: agent |
| 🟢 Biết là đủ | **Trie** | Autocomplete, prefix match | (ít dùng) |
| 🟢 Biết là đủ | **Set** | Loại trùng, phép giao/hợp tập kết quả | hybrid merge dedup |

---

## 0. BIG-O NOTATION — "Cái này tốn bao nhiêu khi dữ liệu phình to?"

**Đây là thứ quan trọng nhất cả tài liệu. Nếu chỉ học 1 thứ, học cái này.**

*   **Vấn đề nếu không có:**
    Mày viết một hàm chạy ngon với 10 file. Lên production có 1 triệu file thì nó treo 3 tiếng.
    Không có Big-O thì mày **không có ngôn ngữ để nói trước "code này sẽ chết khi dữ liệu lớn"** —
    chỉ phát hiện khi đã sập.

*   **Nguyên lý & logic:**
    Big-O mô tả **tốc độ tăng của thời gian/bộ nhớ theo kích thước input n**, bỏ qua hằng số.
    Không đo giây cụ thể (giây phụ thuộc máy), mà đo **hình dạng đường cong**:
    - `O(1)` — hằng số: tra dict, truy cập `array[i]`. Dữ liệu tăng, thời gian không đổi.
    - `O(log n)` — binary search, đi sâu trong cây. Tăng triệu lần input chỉ tốn thêm ~20 bước.
    - `O(n)` — quét tuyến tính: so query với **từng** chunk (brute-force của mày).
    - `O(n log n)` — sort tốt nhất.
    - `O(n²)` — vòng lặp lồng vòng lặp. Chết nhanh.

    Ví dụ cụ thể trong `mini_rag.py`: hàm `retrieve_top_k` so query với N chunk = **O(n)**.
    Với 500 chunk thì nhanh. Với 10 triệu vector thì mỗi câu hỏi phải làm 10 triệu phép tính cosine
    → đó là lý do **NOTES.md Ngày 3 của mày** ghi "phải dùng ANN index (HNSW)".

*   **Giới hạn / khi nào KHÔNG quan trọng:**
    Big-O bỏ qua hằng số → đôi khi `O(n)` với hằng số nhỏ lại **nhanh hơn** `O(log n)` hằng số lớn
    ở n nhỏ. Với dữ liệu nhỏ (vài trăm phần tử) thì đừng tối ưu sớm — brute-force O(n) hoàn toàn ổn.
    "Premature optimization is the root of all evil."

> **Câu phỏng vấn kinh điển:** *"Hệ thống RAG của em có 50 chunk thì brute-force search ổn.
> Khi nào em phải đổi sang vector index, và vì sao?"* → Trả lời bằng Big-O: O(n) chết khi n lên
> hàng triệu, đổi sang ANN index O(log n).

---

## 1. ARRAY / DYNAMIC ARRAY (List, numpy array)

*   **Vấn đề nếu không có:**
    Mày cần lưu N embedding, mỗi cái 384 số, và truy cập cái thứ i tức thì. Nếu lưu rời rạc thì
    tìm phần tử thứ i phải dò từ đầu.

*   **Nguyên lý & logic:**
    Array = vùng nhớ **liên tục**. Biết địa chỉ gốc + kích thước mỗi phần tử → tính ngay địa chỉ
    phần tử thứ i bằng phép nhân → **truy cập `array[i]` là O(1)**.
    Trong AI điều này cực quan trọng: ma trận embedding `(N, 384)` mà NOTES.md Ngày 2 mày ghi
    ("encode 6 câu → ma trận (6, 384)") chính là một mảng 2 chiều liên tục. numpy nhanh vì nó
    đặt toàn bộ số **cạnh nhau trong RAM** → CPU đọc cả khối một lúc (cache-friendly), và làm phép
    tính trên cả mảng cùng lúc (vectorization) thay vì lặp Python từng phần tử.
    - Truy cập index: **O(1)**
    - Thêm vào cuối (append): **O(1)** trung bình
    - Chèn/xóa giữa: **O(n)** (phải dịch phần tử)
    - Tìm giá trị (chưa sort): **O(n)**

*   **Giới hạn / khi nào KHÔNG dùng:**
    Chèn/xóa ở giữa tốn O(n) vì phải dịch cả dãy. Nếu mày cần thêm/bớt liên tục ở giữa thì array
    tệ → dùng linked list hoặc cấu trúc khác. Và array kích thước cố định: dynamic array (Python list)
    khi đầy phải cấp vùng mới to gấp đôi rồi copy — thỉnh thoảng 1 lần append tốn O(n).

---

## 2. HASHMAP / DICT / HASH TABLE — "Tra cứu tức thì bằng khóa"

**Cấu trúc quan trọng số 2 sau Big-O. Dùng ở khắp nơi trong AI.**

*   **Vấn đề nếu không có:**
    Mỗi lần cần embedding của một câu, mày gọi model encode lại → chậm và tốn tiền. Hoặc: mày
    muốn biết "từ `signature` xuất hiện ở những document nào" mà phải quét hết mọi document mỗi lần.

*   **Nguyên lý & logic:**
    Hashmap biến **khóa (key) → một con số (hash) → vị trí ô nhớ** bằng hàm băm. Nhờ vậy tra cứu,
    thêm, xóa đều **O(1) trung bình** — không phụ thuộc số phần tử.
    Ba ứng dụng trực tiếp trong project mày:
    1. **Cache embedding:** `dict[text] → vector`. Câu đã encode rồi thì lần sau lấy ra O(1),
       khỏi gọi model. (NOTES.md Ngày 1: token tốn tiền → cache là cách tiết kiệm.)
    2. **Inverted index cho BM25 / keyword search:** `dict[từ] → danh sách document chứa từ đó`.
       Đây chính là cơ chế **Level 2 Hybrid Search** trong `ai-workflow-engine` và keyword search
       trong `support-rag-assistant`. Hỏi "signature" → tra dict 1 phát ra ngay danh sách doc, O(1),
       không quét toàn bộ.
    3. **Khử trùng lặp (dedup):** khi merge kết quả vector + keyword trong hybrid search, dùng dict/set
       để 1 chunk không bị tính 2 lần.

*   **Giới hạn / khi nào KHÔNG dùng:**
    - Hashmap **không có thứ tự** (không hỏi được "phần tử nhỏ nhất/lớn nhất") → cần thứ hạng thì
      dùng heap/sort, không dùng dict.
    - O(1) là **trung bình**; xấu nhất O(n) khi nhiều khóa đụng hash (hash collision).
    - Key phải **hashable** (bất biến). Đặc biệt: **đừng tưởng hashmap thay được embedding search.**
      Hashmap chỉ khớp **chính xác** khóa — `dict["kiểm tra chữ ký"]` KHÁC `dict["verify signature"]`
      dù cùng nghĩa. Khớp ngữ nghĩa là việc của embedding (NOTES.md Ngày 2). Khớp chính xác (mã đơn,
      tên hàm) mới là việc của hashmap. → Đây đúng là lý do tồn tại **hybrid search**: hashmap lo
      exact-match, embedding lo ngữ nghĩa.

---

## 3. HEAP / PRIORITY QUEUE — "Lấy top-k nhanh nhất" (Trái tim của Retrieval)

**Cấu trúc DSA dính trực tiếp nhất tới hàm `retrieve_top_k` mày đang viết.**

*   **Vấn đề nếu không có:**
    Mày có 1 triệu chunk, mỗi cái 1 điểm cosine. Mày chỉ cần **5 chunk điểm cao nhất**. Cách ngây thơ:
    sort cả 1 triệu rồi lấy 5 đầu → tốn O(n log n) để rồi vứt đi 999.995 cái. Phí.

*   **Nguyên lý & logic:**
    Heap là một **cây nhị phân đặc biệt**: cha luôn ≥ (max-heap) hoặc ≤ (min-heap) con. Nhờ tính chất
    này, **phần tử lớn/nhỏ nhất luôn nằm ở gốc → lấy ra O(1)**, thêm/bớt O(log n).
    **Mẹo top-k chuẩn industry:** giữ một **min-heap kích thước k**. Duyệt qua n phần tử, mỗi cái so với
    gốc heap (phần tử nhỏ nhất trong top-k hiện tại): lớn hơn thì thay vào. Kết quả: tìm top-k trong
    **O(n log k)** thay vì O(n log n) — khi k=5 và n=1 triệu thì nhanh hơn rất nhiều.
    Trong Python: `heapq.nlargest(k, items, key=...)` làm đúng việc này. Khi mày code `retrieve_top_k`,
    nếu k nhỏ và n lớn thì đây là cách đúng thay vì `sorted(...)[:k]`.

*   **Giới hạn / khi nào KHÔNG dùng:**
    - Khi mày cần **toàn bộ danh sách đã sắp xếp** (không chỉ top-k) thì sort thẳng, heap không lợi.
    - Khi n nhỏ (vài trăm chunk như `mini_rag.py` hiện tại) thì `sorted(...)[:k]` đơn giản hơn và đủ
      nhanh — **đừng tối ưu sớm**. Heap chỉ đáng khi n rất lớn và k nhỏ.
    - Heap chỉ cho mày phần tử cực trị, **không cho tra cứu theo khóa** (đó là việc của hashmap).

> **Đây là chỗ DSA và AI gặp nhau rõ nhất:** "retrieve top-k relevant chunks" — câu cửa miệng của
> mọi hệ RAG — bản chất là một bài toán heap/priority queue.

---

## 4. SORTING — Sắp xếp kết quả theo điểm

*   **Vấn đề nếu không có:**
    Sau khi tính điểm hybrid (vector + keyword) cho mỗi chunk, mày cần đưa chunk điểm cao lên đầu để
    nhét vào prompt. Không sort thì LLM nhận chunk lộn xộn.

*   **Nguyên lý & logic:**
    Sort sắp các phần tử theo thứ tự. Thuật toán tốt (merge sort, quicksort, Timsort của Python) đạt
    **O(n log n)** — tối ưu cho so-sánh tổng quát. Trong `ai-workflow-engine`, bước merge hybrid score
    rồi xếp hạng chính là một lần sort theo điểm giảm dần.
    Mày cần phân biệt:
    - **Stable sort** (Timsort): giữ thứ tự tương đối của phần tử bằng điểm — quan trọng khi 2 chunk
      cùng điểm, muốn giữ thứ tự gốc.
    - **Sort key**: `sorted(chunks, key=lambda c: c.score, reverse=True)` — sort theo điểm.

*   **Giới hạn / khi nào KHÔNG dùng:**
    Nếu chỉ cần top-k (k nhỏ) thì sort cả mảng là lãng phí → dùng heap (mục 3). Sort cũng vô nghĩa
    với dữ liệu không có thứ tự tự nhiên. Và `O(n log n)` là cận của sort **dựa trên so sánh**; có sort
    đặc biệt O(n) (counting/radix) nhưng chỉ cho số nguyên giới hạn — hiếm dùng trong RAG.

---

## 5. BINARY SEARCH — Tìm trong mảng đã sắp xếp

*   **Vấn đề nếu không có:**
    Tìm một giá trị trong 1 triệu phần tử đã sort bằng cách quét tuyến tính = O(n), phí.

*   **Nguyên lý & logic:**
    Mảng **đã sort** → so với phần tử giữa, biết cần đi trái hay phải, **loại bỏ nửa còn lại mỗi bước**
    → **O(log n)**. 1 triệu phần tử chỉ cần ~20 bước.
    Tư duy "chia đôi để loại nửa" này là nền của nhiều thứ nâng cao: cách HNSW điều hướng trong đồ thị,
    cách cây index của database thu hẹp tìm kiếm, cách tìm ngưỡng (threshold) tối ưu khi tuning.

*   **Giới hạn / khi nào KHÔNG dùng:**
    Bắt buộc dữ liệu **đã sort** — chi phí sort là O(n log n), nên nếu chỉ tìm 1 lần thì quét O(n) còn
    rẻ hơn. Binary search lợi khi **sort 1 lần, tìm nhiều lần**.

---

## 6. TREE (BST, B-Tree) — Index của Database

*   **Vấn đề nếu không có:**
    `SQLiteDocumentStore` trong `support-rag-assistant` lưu document trong SQLite. Truy vấn
    "lấy document có id = X" mà quét cả bảng = O(n), chậm khi bảng lớn.

*   **Nguyên lý & logic:**
    Cây tìm kiếm giữ dữ liệu **có thứ tự phân nhánh**: bên trái nhỏ hơn, bên phải lớn hơn → tìm bằng
    cách đi xuống, mỗi tầng loại một nửa → **O(log n)**. Database thật (SQLite, Postgres) dùng **B-Tree**
    (một biến thể nhiều nhánh, tối ưu cho đọc đĩa) làm **index**. Khi mày tạo index trên cột `id`,
    database xây B-Tree → query theo id thành O(log n) thay vì O(n).
    Đây là lý do **NOTES.md của mày** nói exact-match (mã đơn, id) nên để **DB query** lo: database
    có sẵn cấu trúc cây để tra cực nhanh và chính xác — embedding không làm được việc này.

*   **Giới hạn / khi nào KHÔNG dùng:**
    Cây cân bằng cần duy trì (chèn/xóa phải tái cân bằng) → tốn hơn array cho dữ liệu tĩnh. Và B-Tree
    index tăng tốc **đọc** nhưng làm **ghi** chậm hơn (mỗi insert phải cập nhật index). Đừng index mọi cột.

---

## 7. GRAPH + BFS/DFS + HNSW — Xương sống của Vector Database

**Đây là đỉnh cao nơi DSA và AI hòa làm một. Mày sẽ đụng ở Tuần 2 khi lên vector DB thật.**

*   **Vấn đề nếu không có:**
    Brute-force search (O(n), so query với từng vector) chết ở triệu vector. Cần cách tìm "hàng xóm gần
    nhất" mà **không phải so với tất cả**.

*   **Nguyên lý & logic:**
    - **Graph** = tập **node (đỉnh)** nối nhau bằng **edge (cạnh)**. **BFS** (duyệt theo tầng, dùng
      Queue) và **DFS** (duyệt theo chiều sâu, dùng Stack) là hai cách đi thăm đồ thị.
    - **HNSW (Hierarchical Navigable Small World)** — cái mà NOTES.md Ngày 3 mày nhắc — xây một **đồ thị
      nhiều tầng** nối mỗi vector với vài hàng xóm gần. Tìm kiếm: bắt đầu ở tầng trên cùng (thưa, nhảy
      xa), "đi bộ" trên đồ thị về phía vector gần query nhất, tụt dần xuống tầng dày hơn để tinh chỉnh.
      Kết quả: tìm hàng xóm gần xấp xỉ trong **~O(log n)** thay vì O(n).
    - Đây là **ANN — Approximate Nearest Neighbor**: chữ "Approximate" rất quan trọng (xem giới hạn).
      Chroma, pgvector, FAISS, Qdrant đều dùng HNSW hoặc họ hàng. Khi mày "gọi vector DB" ở Tuần 2,
      bên dưới chính là đồ thị này đang chạy BFS-có-định-hướng.

*   **Giới hạn / khi nào KHÔNG dùng:**
    - **Approximate = có thể bỏ sót** hàng xóm gần nhất thật sự. Đánh đổi **tốc độ ↔ độ chính xác**
      (recall). Với dữ liệu nhỏ, brute-force O(n) cho kết quả **chính xác 100%** và đủ nhanh → đừng dùng
      HNSW sớm (đúng tinh thần NOTES.md: vài trăm chunk thì brute-force ổn).
    - Xây index tốn RAM và thời gian; thêm/xóa vector động phức tạp hơn array.

> **Câu chốt cho CV/phỏng vấn:** *"Vector database tìm nhanh nhờ ANN index như HNSW — bản chất là một
> đồ thị nhiều tầng, đánh đổi một chút độ chính xác (recall) để lấy tốc độ O(log n) thay vì O(n)."*
> Nói được câu này là mày đã ở trên 80% ứng viên chỉ biết "gọi `.query()`".

---

## 8. STACK & QUEUE — Agent Loop & Duyệt

*   **Vấn đề nếu không có:**
    Tuần 3 mày làm agent nhiều bước (LangGraph). Agent cần nhớ "đang làm dở việc gì, quay lại đâu",
    và xử lý hàng đợi công việc theo thứ tự.

*   **Nguyên lý & logic:**
    - **Stack (LIFO — vào sau ra trước):** nền của DFS, của lệnh gọi hàm (call stack), của undo. Trong
      agent: ngăn xếp các bước đang thực thi lồng nhau.
    - **Queue (FIFO — vào trước ra trước):** nền của BFS, của hàng đợi tác vụ. Trong agent/pipeline:
      hàng đợi document chờ xử lý, message queue.
    Cả hai chỉ thêm/bớt ở một đầu → các thao tác **O(1)**.

*   **Giới hạn / khi nào KHÔNG dùng:**
    Stack/Queue chỉ cho truy cập ở đầu, **không tra cứu giữa được** (đó là việc của array/hashmap).
    Dùng đúng vai: cần thứ tự xử lý thì queue, cần quay-lui thì stack.

---

## 9. SET — Phép tập hợp khi merge kết quả

*   **Vấn đề nếu không có:**
    Hybrid search trả về kết quả từ 2 nguồn (vector + keyword). Một chunk có thể xuất hiện ở cả hai →
    nếu không khử trùng, nó bị tính/hiển thị 2 lần.

*   **Nguyên lý & logic:**
    Set = hashmap chỉ giữ khóa, không giá trị → kiểm tra "đã có chưa" O(1), và hỗ trợ **phép giao (∩),
    hợp (∪), hiệu (−)**. Trong merger của `ai-workflow-engine`: hợp 2 tập kết quả, khử trùng bằng set
    các chunk-id đã thấy. Đây là DSA ẩn dưới một dòng `seen = set()`.

*   **Giới hạn / khi nào KHÔNG dùng:**
    Set không có thứ tự, không lưu giá trị kèm. Cần điểm số/thứ hạng đi kèm thì dùng dict (id → score).

---

## 10. TRIE — Prefix match (mục biết-là-đủ)

*   **Vấn đề nếu không có:** Autocomplete/gợi ý khi gõ, hoặc tra mọi từ bắt đầu bằng "auth" mà không quét hết từ điển.
*   **Nguyên lý & logic:** Cây ký tự, mỗi đường từ gốc là một tiền tố chung → tìm theo prefix nhanh theo độ dài chuỗi, không phụ thuộc số từ. Ít dùng trong RAG cơ bản; hữu ích nếu sau này làm search-as-you-type hay match tên hàm/biến theo tiền tố trong AI Code Auditor.
*   **Giới hạn:** Tốn bộ nhớ; với khớp ngữ nghĩa thì vô dụng (vẫn là khớp ký tự) → đó là việc của embedding.

---

## 11. KHÁI NIỆM CẦU NỐI — Hiểu "vì sao" ở tầng sâu

*Hai khái niệm CS không phải cấu trúc dữ liệu, nhưng giải thích "vì sao" ở tầng sâu hơn — giúp mày không hoảng khi gặp hành vi lạ và biết bản chất của caching.*

### 11a. Amortized Analysis — Vì sao `list.append` là O(1) dù đôi khi chậm

*   **Vấn đề nếu không có:**
    Mày thấy `list.append` thường tức thì, nhưng **thỉnh thoảng 1 lần lại khựng**. Nếu chỉ nhìn cái lần khựng đó, mày tưởng append là O(n) và hoảng — rồi đi tối ưu nhầm chỗ.

*   **Nguyên lý & logic:**
    Python list (dynamic array) đặt phần tử trong vùng nhớ liên tục có sức chứa cố định. Khi **đầy**, nó cấp một vùng mới **lớn gấp đôi** rồi **copy toàn bộ sang** — lần append đó tốn **O(n)**. Nhưng vì mỗi lần phình là gấp đôi, các lần copy thưa dần theo cấp số nhân → **chia đều chi phí ra toàn bộ N lần append, trung bình mỗi lần vẫn là O(1)**. Đây gọi là **amortized O(1)** (O(1) khấu hao): không phải "luôn O(1)", mà là "trung bình O(1) qua nhiều thao tác". Đo thật trong RAG: khi mày `all_chunks.append(...)` hàng nghìn chunk, vài lần khựng là do realloc — hoàn toàn bình thường.

*   **Giới hạn / khi nào KHÔNG dùng:**
    Amortized che cái **đỉnh chi phí tức thời** (worst-case một lần vẫn O(n)). Với hệ **real-time cần độ trễ ổn định** (không chịu được spike), phải để ý lần realloc đó — lúc này nên `list` cấp sẵn dung lượng hoặc dùng cấu trúc khác. Với RAG batch bình thường thì amortized O(1) là đủ, đừng lo.

### 11b. Time–Space Tradeoff — Bản chất của caching & index

*   **Vấn đề nếu không có:**
    Mỗi lần cần embedding của một câu, mày encode lại bằng model → **chậm và tốn tiền**. Mỗi lần cần tra vector gần nhất, mày quét hết → chậm. Không có khái niệm này, mày không thấy được **cái nút vặn** giữa nhanh và nhẹ.

*   **Nguyên lý & logic:**
    Time–Space tradeoff = **đánh đổi bộ nhớ lấy tốc độ** (hoặc ngược lại). Đây là một trong những đánh đổi nền tảng nhất của CS, và **mọi thứ "tăng tốc" mày dùng đều là nó**:
    - **Cache embedding** (dict `text → vector`): tốn thêm RAM giữ vector, đổi lại khỏi gọi model → nhanh + rẻ.
    - **Index** (B-Tree của DB, HNSW của vector DB): tốn thêm bộ nhớ + thời gian dựng index, đổi lại truy vấn O(log n) thay vì O(n).
    - **Precompute** (tính sẵn ma trận embedding lúc ingest): tốn chỗ lưu, đổi lại lúc query khỏi tính lại.
    Nhận ra đây là **cùng một nút vặn** giúp mày phán đoán: "muốn nhanh hơn → chịu tốn bộ nhớ/lưu trữ hơn; muốn nhẹ hơn → chịu chậm hơn".

*   **Giới hạn / khi nào KHÔNG dùng:**
    Đổi sang tốn bộ nhớ KHÔNG miễn phí: cache/index cần **RAM/đĩa** và phải **giữ đồng bộ** (dữ liệu đổi thì cache/index cũ thành sai — bug "stale cache" kinh điển). Khi dữ liệu **thay đổi liên tục** hoặc **bộ nhớ là nút thắt**, cache/index có thể hại nhiều hơn lợi. Đừng cache/index khi tính lại còn rẻ hơn chi phí giữ đồng bộ.

> **🔗 Nối với tài liệu khác:** 11b chính là "vì sao" đứng sau mục B1/B3 của [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) (chọn vector DB, observability) — mọi quyết định infra đều là một lần vặn nút time–space.

---

## TỔNG KẾT — Bản đồ "bài toán → DSA" để nhớ nhanh

| Bài toán mày gặp trong AI | DSA giải nó | Big-O |
|---|---|---|
| "Code này có chết khi data lớn không?" | Big-O (tư duy nền) | — |
| Lưu & truy cập N embedding | Array / numpy | O(1) truy cập |
| Cache embedding khỏi gọi lại model | Hashmap | O(1) |
| Keyword/BM25: từ → document nào | Inverted index (hashmap) | O(1) tra |
| **Lấy top-k chunk điểm cao nhất** | **Heap / Priority Queue** | O(n log k) |
| Sắp xếp kết quả theo điểm | Sorting | O(n log n) |
| Tra document theo id trong DB | B-Tree index | O(log n) |
| **Tìm vector gần nhất ở quy mô triệu** | **Graph / HNSW (ANN)** | ~O(log n) |
| Agent nhiều bước, hàng đợi tác vụ | Stack / Queue | O(1) |
| Khử trùng khi merge kết quả | Set | O(1) |

---

## CÁCH HỌC HIỆU QUẢ NHẤT CHO MÀY (chiến lược, không phải lý thuyết)

1. **70% làm project / 30% vá nền DSA.** Project là thứ nhà tuyển dụng nhìn; DSA là nền để trả lời
   phỏng vấn. Đừng đảo ngược tỉ lệ — đừng để DSA nuốt thời gian build.
2. **Mỗi chương DSA ở trường → tự hỏi "nó nằm ở đâu trong RAG của mình?"** Dùng bảng tổng kết trên
   làm điểm móc. Học có chỗ móc thì nhớ lâu gấp nhiều lần.
3. **Tự cài lại 3 thứ này bằng Python thuần, không thư viện** (giống cách mày tự viết `cosine_similarity`):
   - một hashmap mini (hiểu hash collision),
   - top-k bằng `heapq` so với `sorted(...)[:k]` (đo thời gian thật ở n lớn),
   - BFS/DFS trên một đồ thị nhỏ (để hiểu HNSW sau này).
4. **Không cày LeetCode kiểu thi Big Tech** (DP hóc búa, backtracking). Mày cần **hiểu chi phí & chọn
   đúng cấu trúc**, không cần giải đố tốc độ.

---

## CÂU HỎI PHỎNG VẤN TỰ LUYỆN (đóng vai nhà tuyển dụng AI)

1. Hệ RAG của em có 50 chunk thì brute-force search ổn. Khi nào phải đổi sang vector index, và vì sao? *(→ Big-O, mục 0 & 7)*
2. "Retrieve top-k relevant chunks" — bản chất DSA của câu này là cấu trúc dữ liệu gì? *(→ Heap, mục 3)*
3. Vì sao mã đơn hàng nên tra bằng database/keyword chứ không bằng embedding? *(→ Hashmap/B-Tree vs embedding, mục 2 & 6)*
4. Vector database tìm nhanh nhờ đâu? Đánh đổi gì? *(→ HNSW/ANN, recall vs tốc độ, mục 7)*
5. Khi merge kết quả vector + keyword, làm sao tránh tính trùng một chunk? *(→ Set, mục 9)*

> Trả lời mỗi câu theo công thức **Cách làm + Tại sao + Đánh đổi** (3 vế) thì đạt mức senior.
```
