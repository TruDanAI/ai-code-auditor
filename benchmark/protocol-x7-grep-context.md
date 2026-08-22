# X7 — Tool ceiling vs model ceiling: thêm `context` vào `grep`

**Đăng ký trước khi chạy trial đầu tiên.** Git chứng minh thứ tự (bài học X4).

## Câu hỏi

X5 cho thấy recall tăng theo sức model (lite 26,2% → pro 54,8%), nhưng bootstrap
23/08 nói **chênh lệch pro-vs-flash không tách khỏi 0**. Vậy trần nằm ở đâu — ở
model, hay ở **harness**?

A3 chỉ đúng chỗ đau: **4/14 seed không arm nào bắt được**, và cả bốn đều là lỗi do
**THIẾU** thứ gì đó:

| seed | lỗi | vì sao grep dòng-đơn mù |
|---|---|---|
| `SEED-INP-02` | bỏ `escapeHtml` quanh `message.text` | phải nhìn ô bảng bên cạnh mới thấy cái nào lệch |
| `SEED-CRY-01` | `decipher.update()` trả về trước `final()` | phải thấy hết thân hàm mới biết `final()` vắng |
| `SEED-CFG-01` | bỏ `FB_VERIFY_TOKEN` khỏi object `required` | phải so nơi khai báo với nơi fail-fast |
| `SEED-AUTH-01` | route GHI cầm quyền `USER_DETAIL_READ` | phải thấy route↔permission của các route anh em |

Một dòng khớp đơn lẻ **không thể** chứng minh "chỗ này thiếu một bước". Phải nhìn
cạnh những chỗ giống nó.

## Biến thay đổi — đúng một

`grep(pattern, ext)` → `grep(pattern, ext, context=0)`, kiểu `grep -C`: hiện thêm
0–5 dòng trước/sau mỗi dòng khớp. Dòng khớp đánh dấu `file:line:`, dòng ngữ cảnh
đánh dấu `file:line-`, số dòng vẫn THẬT nên citation vẫn hợp lệ.

**Không đổi:** model (`gemini-2.5-pro`), `max_steps=10`, số tool (vẫn 3), snapshot,
gold, checklist, scorer, validator. So sánh trực tiếp với `x5-pro`.

## Giả thuyết đăng ký trước

| ID | Phát biểu | Ngưỡng |
|---|---|---|
| **H7.1** | recall in-scope x7 > x5-pro | KTC 95% bootstrap **có cặp** tách khỏi 0 |
| **H7.2** | recall nhóm `kho` tăng | từ 11% lên ≥ 25% |
| **H7.3** | tool mở khoá seed mù | ≥1 trong 4 seed bắt được ở ≥2/3 spiked trial |
| **H7.4** | *phản chứng* — tool đánh đổi chứ không cải thiện | precision giảm > 10 điểm |

**Cỡ hiệu ứng tối thiểu, tính TRƯỚC:** ở n=14 seed, các delta có cặp đã đo có bề
rộng KTC ~24 điểm, nên chỉ delta **≥ ~12 điểm** mới tách được khỏi 0.
→ **Nếu tool cho +5 điểm recall, chúng ta KHÔNG tuyên bố gì cả.** Ghi ra đây trước
để khỏi tự thuyết phục mình sau khi nhìn số.

## Trần chi

6 trial (3 clean + 3 spiked). Đơn giá x5-pro đo được: $1,665/trial clean,
$1,521/trial spiked → nền ≈ **$9,6**. `context` làm prompt token tăng, dự phòng
→ **trần $14. Vượt → dừng, ghi lại, không âm thầm chạy tiếp.**

## Hạn chế phải ghi vào luận văn

Cap của tool (`per_file=3`, `line_budget=160` khi `context>0`) được chọn khi tác giả
**đã biết tập seed**. Cap dựa trên nguyên tắc có sẵn trong repo ("phủ rộng hơn đào
sâu", bài học Ngày 15/16) chứ không nhắm vào seed cụ thể, nhưng việc kiểm rằng
CFG-01 sống sót qua cap là **có nhìn đáp án**. Đây là contamination nhẹ nhưng thật —
khai báo, không giấu.

Test offline: `test_grep_context.py` (7/7), `test_validator.py` (6/6).
