# Thiết Kế — Track "Python + DSA để DẠY LẠI ĐƯỢC" (Teach-back)

> **Ngày tạo:** 2026-07-01 · **Trạng thái:** đã duyệt thiết kế, chờ review spec → writing-plans
>
> **Đây là gì:** đặc tả một **hệ thống học** (phương pháp + sản phẩm), KHÔNG phải giáo trình nội dung.
> Nội dung Python/DSA sâu đã có sẵn — spec này là *lớp phương pháp dạy-lại* đặt lên trên chúng.

---

## 1. Mục tiêu & bối cảnh

Bổ sung Python + DSA tới mức **dạy lại được cho người khác** (chuẩn Feynman), phục vụ cả 3 việc:
build AI Code Auditor, đi phỏng vấn, và giải thích cho người khác hiểu. Chuẩn "dạy lại" là bậc cao
nhất trong 3 mục tiêu và là thước đo bao trùm.

**3 ràng buộc do người học chốt (2026-07-01):**

| Ràng buộc | Giá trị |
|---|---|
| Chuẩn "xong" | Dạy lại được (teach-back), không chỉ giải được bài |
| Cách ghép roadmap | Xen kẽ **~45–60 phút/ngày**, không cắt dự án AI Code Auditor |
| Nền hiện tại | Python cơ bản (hay quên cú pháp), DSA gần như chưa đụng |
| Phạm vi DSA | **Core** bám auditor + phỏng vấn; **bỏ** tree/graph/DP nặng ở track này |

**Nguyên tắc YAGNI:** chỉ lấy phần DSA (a) xuất hiện trong chính auditor và (b) hay hỏi trong phỏng vấn
AI Engineer. Dạy-lại-được trên tập nhỏ đó hơn là biết mờ mờ tất cả.

---

## 2. Quan hệ với 2 tài liệu đã có (QUAN TRỌNG — tránh trùng lặp)

Track này **không viết lại nội dung**. Nó dùng lại:

- **[`dsa-cho-ky-su-ai.md`](../../dsa-cho-ky-su-ai.md)** — *nguồn NỘI DUNG DSA*. Đã có Big-O, array,
  hashmap, heap/top-k, sort, binary search + bảng "bài toán → DSA", mỗi mục theo quy tắc 3-câu và bám
  thẳng code auditor. Track dùng file này làm giáo trình cho Giai đoạn B.
- **[`ke-hoach-nen-tang-python-dsa.md`](../../ke-hoach-nen-tang-python-dsa.md)** — *lịch & pace nền tảng*
  (chốt 29/6). Track này **điều chỉnh** file đó cho khớp ràng buộc mới (xem §6).

**Cái spec này thêm mới (chưa có trong 2 file trên):**
1. **Vòng lặp dạy-lại 5 bước** mỗi buổi, mở đầu bằng nhắc-lại-nói-thành-tiếng.
2. **Cổng "test 60 giây"** làm định nghĩa "xong" và làm bộ điều tốc độ.
3. **Playbook mỗi khái niệm** có ô **"kịch bản dạy 60s"** — phần tự-diễn-đạt-để-dạy mà 2 file cũ chưa có.
4. **Học lại Python theo bản chất** (Giai đoạn A) — 2 file cũ nghiêng về DSA, phần Python chỉ có 1 tuần sprint.

---

## 3. Định nghĩa "XONG" — Bài test 60 giây

Một khái niệm coi là **XONG** khi người học qua được **bài test 60 giây**:

> Nói lại thành tiếng cho một người không biết gì, **không nhìn note**, đủ:
> (1) vấn đề nếu không có nó → (2) cách hoạt động → (3) khi nào KHÔNG dùng → (4) 1 con số neo.

Đây vừa là chuẩn dạy-lại, vừa là khung câu trả lời phỏng vấn (Cách làm + Tại sao + Đánh đổi).

---

## 4. Vòng lặp mỗi buổi — 5 bước (45–60 phút)

| Bước | Thời gian | Việc | Ai làm |
|---|---|---|---|
| 0. Nhắc lại | ~5' | Nói lại khái niệm buổi trước; mentor đóng vai người mới hỏi | Người học nói |
| 1. Giảng bản chất | ~10–15' | Giải thích "phần sau code" TRƯỚC, theo 4 câu hỏi bản chất | Mentor |
| 2. Code mẫu | ~10' | Ví dụ **ưu tiên lấy từ auditor**, comment ở dòng quan trọng | Mentor trình, người học đọc |
| 3. Nói lại | ~5' | Người học diễn đạt bằng lời của mình (active recall) | Người học nói |
| 4. Tự tay | ~10–15' | Sửa/viết 1 mẩu nhỏ | Người học code |
| 5. Chốt playbook | ~5' | Ghi 1 trang: Mermaid + 3-câu + số neo + kịch bản 60s | Người học viết |

**4 câu hỏi bản chất (bước 1):** (1) không có nó thì khổ chỗ nào? (2) bên dưới hoạt động ra sao?
(3) khi nào KHÔNG nên dùng? (4) 1 con số neo.

---

## 5. Hai giai đoạn (tổng ~6 tuần, xen kẽ mỗi ngày)

### Giai đoạn A — Nền Python theo bản chất (~2.5 tuần)
*Làm lại nền theo bản chất, KHÔNG restart tuyến tính. Cái đã chắc thì lướt bằng 1 câu tự-kiểm-tra;
cái hổng bản chất thì đào sâu.*

- Mô hình bộ nhớ: biến = nhãn; tham chiếu vs copy; mutable vs immutable *(neo: `a=[]; b=a` → sửa `b` đổi luôn `a`)*
- `list` vs `dict` vs `set` = mảng vs hash table *(neo: dict tra cứu O(1), tìm trong list O(n))*
- Comprehension & slicing; `enumerate` / `zip`
- Hàm: tham số, `*args`/`**kwargs`, phạm vi biến, cạm bẫy default `[]`
- Generator & `yield` *(neo: xử lý file lớn không nạp hết vào RAM — dùng đúng lúc chunking)*
- OOP tối thiểu: `class` / `self` / `__init__`; khi nào cần class vs chỉ cần hàm
- Xử lý lỗi `try/except`; context manager `with`

### Giai đoạn B — DSA core bám auditor + phỏng vấn (~3.5 tuần)
*Giáo trình nội dung: dùng thẳng các mục tương ứng trong [`dsa-cho-ky-su-ai.md`](../../dsa-cho-ky-su-ai.md).*

- **Big-O** — ngôn ngữ chung để nói về chi phí *(neo: 3 mức O(1) < O(n) < O(n²))* — `dsa-cho-ky-su-ai.md` §0
- Array / String — bám `chunk_text` — §1
- Hash map / set — đếm, khử trùng lặp, tra cứu nhanh — §2, §9
- Sort + **heap / top-k** — bám thẳng `retrieve_top_k` — §3, §4
- Vector & tích vô hướng — bám `cosine_similarity` — (numpy / §1)
- Đệ quy cơ bản + binary search — §5

**Bỏ khỏi track này** (theo scope core): tree/B-Tree nặng, graph/HNSW, DP, backtracking. Chúng vẫn nằm
trong `dsa-cho-ky-su-ai.md` như tài liệu tham khảo cho track DSA dài 2–3 tháng sau này.

---

## 6. Điều chỉnh so với `ke-hoach-nen-tang-python-dsa.md` (29/6)

Spec này **thay các con số sau** trong file kế-hoạch cũ (khung học giữ nguyên):

| Điểm | File cũ (29/6) | Track này (1/7) |
|---|---|---|
| Thời gian/ngày | 1.5–2h/tối | **45–60 phút/ngày** |
| Phạm vi tháng này | DSA đầy đủ dần (tiến tới graph/DP) | **Core only**; graph/DP để track dài sau |
| Cơ chế "xong" | tick ô + đếm bài | **cổng test 60s** (bậc dạy-lại) |

→ Hành động: cập nhật header/pace của `ke-hoach-nen-tang-python-dsa.md` trỏ sang spec này, không xóa.

---

## 7. Sản phẩm: Playbook (artifact dùng cho CV)

Thư mục mới: `ai-code-auditor/docs/python-dsa-playbook/`. Mỗi khái niệm 1 file `.md` theo mẫu:

```
# <Tên khái niệm>
[Mermaid: sơ đồ bản chất]
- Vấn đề nếu không có nó:
- Cách hoạt động bên dưới:
- Khi nào KHÔNG dùng:
- 🔢 Số neo:
- 🎤 Kịch bản dạy 60s: "Nếu phải giải thích cho đồng nghiệp, tôi sẽ nói: ..."
- Bài đã tự làm: <link>
- 🔗 Nội dung nguồn: dsa-cho-ky-su-ai.md §<n> (nếu có)
```

Cuối track ghép thành 1 trang tổng **decision playbook có Mermaid spine** (đúng artifact người học muốn:
Mermaid + evidence-backed, phục vụ active-recall).

---

## 8. Nguyên tắc linh hoạt — bám cổng, không bám lịch

Tốc độ do **mức hiểu** quyết định, KHÔNG do số ngày:

- Qua bài test 60s cho khái niệm → được đẩy nhanh, gộp 2 ngày thành 1 thoải mái.
- Nói lại còn vấp → chậm lại ở đúng khái niệm đó, không ép qua.

Đây là điểm chống áp lực: gộp ngày không phải "chạy trước lịch", mà là "đã qua cổng thì đi tiếp".

---

## 9. Quy ước dạy học (bám CLAUDE.md + `prompt-bat-dau-ngay.md`)

- Quy tắc 3-câu cho mọi khái niệm.
- Không dump code; tóm tắt logic bằng lời trước, code có comment ở dòng quan trọng.
- Pause-30s: sau mỗi block code hỏi 1 câu kiểm tra trước khi chạy.
- Reflex Q&A: cuối buổi mentor đóng vai nhà tuyển dụng hỏi 1–2 câu.
- Review chứ không sửa hộ: chỉ ra lỗi + giải thích vì sao, để người học tự sửa.
- Cập nhật `NOTES.md` cuối mỗi buổi bằng định dạng 3-câu.

---

## 10. Ngoài phạm vi (Non-goals)

- Không cày LeetCode kiểu thi Big Tech (DP hóc búa, backtracking tốc độ).
- Không tạo giáo trình DSA đầy đủ mới — tái dùng `dsa-cho-ky-su-ai.md`.
- Không đụng tree/graph/DP trong track 6 tuần này.
- Không thay thế roadmap AI Code Auditor — chạy song song, ưu tiên portfolio ban ngày.
