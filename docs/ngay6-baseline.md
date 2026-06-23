# Ngày 6 — Baseline Stress-Test (chatbot-fanpage)

_Index: 3308 chunks, model = all-MiniLM-L6-v2, model LLM = gemini-3.5-flash_


## Q1. verifySignature dùng thuật toán gì?
- **Có trong code?** CÓ  |  **Kỳ vọng:** HMAC-SHA256, timingSafeEqual
- **Top-3 chunk lấy được:**
  - `0.490` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 23)
  - `0.431` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 14)
  - `0.423` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 18)
- **Auto-tag:** [TỪ CHỐI]
- **Trả lời của model:**

> Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp.
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q2. credential encryption dùng mode gì?
- **Có trong code?** CÓ  |  **Kỳ vọng:** AES-256-GCM
- **Top-3 chunk lấy được:**
  - `0.490` C:\Users\Pc\Desktop\chatbot-fanpage\.agent\skills\credential-safety.md (chunk 3)
  - `0.457` C:\Users\Pc\Desktop\chatbot-fanpage\core\credentials\page-credentials.js (chunk 7)
  - `0.452` C:\Users\Pc\Desktop\chatbot-fanpage\.agent\skills\credential-safety.md (chunk 0)
- **Auto-tag:** [CÓ TRẢ LỜI]
- **Trả lời của model:**

> Dựa vào thông tin trong context, credential encryption sử dụng mode **`aes-256-gcm`**. 
> 
> Thông tin này được tìm thấy tại:
> * **File:** `C:\Users\Pc\Desktop\chatbot-fanpage\core\credentials\page-credentials.js` | **Chunk 7** (thông qua hàm `crypto.createDecipheriv('aes-256-gcm', ...)`).
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q3. lead parser hoạt động thế nào?
- **Có trong code?** CÓ  |  **Kỳ vọng:** Trích tên/SĐT/địa chỉ từ tin nhắn
- **Top-3 chunk lấy được:**
  - `0.561` C:\Users\Pc\Desktop\chatbot-fanpage\core\admin\views.js (chunk 188)
  - `0.531` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\reviews\product-menu-ux-polish-plan.md (chunk 7)
  - `0.507` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 30)
- **Auto-tag:** [TỪ CHỐI]
- **Trả lời của model:**

> Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp.
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q4. multi-shop isolation hoạt động ra sao?
- **Có trong code?** CÓ  |  **Kỳ vọng:** Tách config theo shops/SHOP_ID
- **Top-3 chunk lấy được:**
  - `0.522` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\checkpoints\multi-shop-rollout.md (chunk 21)
  - `0.514` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\reviews\product-menu-ux-polish-plan.md (chunk 7)
  - `0.504` C:\Users\Pc\Desktop\chatbot-fanpage\core\admin\views.js (chunk 188)
- **Auto-tag:** [CÓ TRẢ LỜI]
- **Trả lời của model:**

> Dựa trên tài liệu được cung cấp, cơ chế cô lập nhiều cửa hàng (**multi-shop isolation**) hoạt động thông qua 3 chốt chặn cô lập (isolation gates) như sau:
> 
> 1. **Cấu hình `dry_run` theo từng shop (Per-shop `dry_run`):**
>    * Biến môi trường global `MESSENGER_DRY_RUN=true` đóng vai trò là nút tắt khẩn cấp (kill switch).
>    * Cấu hình `dry_run=true` ở cấp độ shop giữ cho shop đó hoạt động trên luồng chạy thử (dry-run path).
>    * Cấu hình `dry_run=false` chỉ được áp dụng cho việc kiểm thử live có kiểm soát hoặc chuyển sang hoạt động thực tế (live switch) trên shop mục tiêu.
> 
> 2. **Cơ chế Fail-closed đối với Trang chưa ánh xạ (Unmapped Page fail-closed):**
>    * Các yêu cầu webhook được hỗ trợ bởi DB đối với một Page chưa được ánh xạ (unmapped Page) sẽ trả về mã HTTP `200`, thực hiện cơ chế đóng khi lỗi (fail closed) và hoàn toàn không tạo ra các tác động phụ như gửi tin nhắn Messenger, hiển thị trạng thái đang soạn thảo (typing) hay lưu trữ dữ liệu (storage).
> 
> 3. **Kiểm tra hồi quy cô lập hai shop (Two-shop isolation regression):**
>    * Được kiểm thử thông qua file `tests/multi-shop-isolation.test.js`, bao phủ trường hợp hai shop đã được ánh xạ có các giá trị `dry_run` khác nhau cùng với một Page chưa được ánh xạ.
> 
> Ngoài ra, khi triển khai thực tế (go-live) cho shop thứ hai, hệ thống yêu cầu: số lượng ánh xạ đang hoạt động (active mapping count) phải chính xác là `1`, số lượng thông tin xác thực hoạt động (active credential count) chính xác là `1`, shop mục tiêu là shop duy nhất có cấu hình `dry_run=false`, và tất cả các shop khác phải giữ cấu hình `dry_run=true`.
> 
> *(Nguồn: File `C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\checkpoints\multi-shop-rollout.md` | Chunk 21)*
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q5. RBAC có mấy vai trò?
- **Có trong code?** CÓ  |  **Kỳ vọng:** 4: viewer/support/maintainer/owner
- **Top-3 chunk lấy được:**
  - `0.496` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 16)
  - `0.484` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 10)
  - `0.428` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\reviews\product-menu-ux-polish-plan.md (chunk 7)
- **Auto-tag:** [TỪ CHỐI]
- **Trả lời của model:** _(re-run trên Vertex 23/6)_

> Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp.
- **Chấm tay:** ❌ MISS (recall). Model **từ chối đúng** (rào chắn ✅, không bịa) NHƯNG đây là **retrieval miss**: grep repo → `HUONG_DAN.md` **không hề chứa** vai trò (0 match `viewer/support/maintainer/owner/RBAC`); 4 vai trò thật nằm ở **code/test** (`tests/admin-routes.test.js:1830` → `['viewer','support','maintainer','owner']`, enforce `core/admin/`). ⚠️ Ghi chú cũ "retrieval đã trúng HUONG_DAN.md 16/10" là **GIẢ ĐỊNH SAI** — bài học: verify nội dung chunk, đừng đoán theo tên file.

## Q6. module thanh toán Stripe hoạt động thế nào?
- **Có trong code?** KHÔNG  |  **Kỳ vọng:** TỪ CHỐI (không có Stripe)
- **Top-3 chunk lấy được:**
  - `0.592` C:\Users\Pc\Desktop\chatbot-fanpage\core\admin\views.js (chunk 188)
  - `0.569` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 27)
  - `0.550` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\reviews\product-menu-ux-polish-plan.md (chunk 14)
- **Auto-tag:** [TỪ CHỐI]
- **Trả lời của model:**

> Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp.
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q7. hệ thống tích hợp với Zalo OA ra sao?
- **Có trong code?** KHÔNG  |  **Kỳ vọng:** TỪ CHỐI (không có Zalo)
- **Top-3 chunk lấy được:**
  - `0.580` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\reviews\product-menu-ux-polish-plan.md (chunk 8)
  - `0.496` C:\Users\Pc\Desktop\chatbot-fanpage\core\responses.js (chunk 7)
  - `0.463` C:\Users\Pc\Desktop\chatbot-fanpage\core\responses.js (chunk 6)
- **Auto-tag:** [TỪ CHỐI]
- **Trả lời của model:**

> Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp.
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q8. database dùng MongoDB phải không?
- **Có trong code?** KHÔNG  |  **Kỳ vọng:** TỪ CHỐI / là PostgreSQL
- **Top-3 chunk lấy được:**
  - `0.555` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\old-prompts\next-session-prompt.md (chunk 6)
  - `0.520` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 23)
  - `0.514` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 12)
- **Auto-tag:** [CÓ TRẢ LỜI]
- **Trả lời của model:**

> Dựa vào thông tin được cung cấp trong context, database được sử dụng là **PostgreSQL**, không phải MongoDB.
> 
> Chi tiết này được đề cập trong:
> * **File:** `C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\old-prompts\next-session-prompt.md` | **Chunk 6**: Có nhắc đến việc *"Không ghi production PostgreSQL nếu chưa có backup mới và xác nhận riêng"* và kiểm tra schema/test SQL bằng các biến như `DATABASE_URL`, `CHATBOT_TEST_DATABASE_URL`, hoặc `CHATBOT_STAGING_DATABASE_URL`.
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q9. có dùng Redis cache không?
- **Có trong code?** KHÔNG  |  **Kỳ vọng:** TỪ CHỐI (không có Redis)
- **Top-3 chunk lấy được:**
  - `0.559` C:\Users\Pc\Desktop\chatbot-fanpage\core\admin\views.js (chunk 188)
  - `0.547` C:\Users\Pc\Desktop\chatbot-fanpage\core\responses.js (chunk 6)
  - `0.530` C:\Users\Pc\Desktop\chatbot-fanpage\HUONG_DAN.md (chunk 23)
- **Auto-tag:** [TỪ CHỐI]
- **Trả lời của model:**

> Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp.
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

## Q10. unit test framework là gì?
- **Có trong code?** CÓ  |  **Kỳ vọng:** Node test runner hoặc Jest
- **Top-3 chunk lấy được:**
  - `0.429` C:\Users\Pc\Desktop\chatbot-fanpage\docs\runbooks\runtime-change-safety-checklist.md (chunk 3)
  - `0.394` C:\Users\Pc\Desktop\chatbot-fanpage\docs\archive\old-prompts\next-session-prompt.md (chunk 14)
  - `0.393` C:\Users\Pc\Desktop\chatbot-fanpage\.agent\skills\tdd-and-review.md (chunk 4)
- **Auto-tag:** [TỪ CHỐI]
- **Trả lời của model:**

> Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp.
- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc

---

**Tự động:** 6/10 câu bị từ chối. (Kỳ vọng tối thiểu: 4 câu KHÔNG-có-trong-code phải bị từ chối.)

## BASELINE chốt (Q5 re-run trên Vertex 23/6 → đủ 10 mẫu hợp lệ)

| Chỉ số | Kết quả | Ghi chú |
|--------|---------|---------|
| **Bịa (hallucination)** | **0 / 10** | Không câu nào bịa, không citation giả. Rào chắn grounding vững (kể cả Q5). |
| **Từ chối đúng (4 câu off-topic)** | **4 / 4** | Q6/Q7/Q9 từ chối; Q8 còn *sửa* tiền-giả-định sai → "là PostgreSQL". |
| **Recall câu in-scope** | **2 / 6 (~33%)** | Trúng: Q2, Q4. Trượt: Q1, Q3, **Q5**, Q10 — đều do **retrieval**, không phải model. |

**Kết luận vàng:** generation (sinh + rào chắn) đã hoàn hảo; **nút thắt 100% ở retrieval** (4 câu miss). **Q5 (re-run 23/6) củng cố thêm:** grep verify → đáp án nằm ở file **code/test** nhưng retrieval lôi `.md` (bias docs-vs-code), khớp y 2 phát hiện vàng Ngày 5 (MiniLM yếu cross-lingual + chunking xé hàm lồng). _Bài học phụ: ghi chú baseline cũ "Q5 retrieval đã trúng" là **giả định SAI** — luôn verify nội dung chunk, đừng đoán theo tên file._

**Nhiễu phát hiện thêm:** `core/admin/views.js (chunk 188)` là "chunk nam châm" — lọt top-3 ở Q3/Q4/Q6/Q9, nghi do fallback chém 800 ký tự thành đoạn mờ nghĩa hút mọi truy vấn.

**Mục tiêu Tuần 2:** nâng MiniLM → Qwen3/BGE-M3 + sửa chunking → kỳ vọng kéo recall in-scope **33% → cao hơn**, giữ hallucination ở 0.