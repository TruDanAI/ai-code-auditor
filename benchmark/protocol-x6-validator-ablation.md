# P-X6 — Ablation `validate_report`: cổng tất định đóng góp bao nhiêu vào precision?

**Trạng thái:** đăng ký trước. **Commit file này TRƯỚC trial đầu tiên.**
**Soạn:** 21/08/2026 · **Chưa chạy trial nào tại thời điểm soạn.**

## 0. Pre-registration

Khác X5 (nơi dự đoán được chép vào protocol), lần này **dự đoán đã nằm sẵn trong git
từ trước**. `STATUS.md` tại commit `5aeb03a` (20/08/2026) ghi:

> **Phân rã giả định:** model → recall; harness → precision. Vế sau CHƯA đo được —
> cần ablation tắt `validate_report`.

Và `results-x5-model-ladder.md` cùng commit ghi rõ đó là **suy luận, chưa phải kết
luận đo được**. Git chứng minh claim này có trước thí nghiệm kiểm nó. Đây là
pre-registration mạnh hơn X5: giả thuyết được công bố trước, kèm lời tự nhận là chưa
có bằng chứng.

**Thí nghiệm này được thiết kế để có thể BÁC BỎ claim đó.** Xem H3.

## 1. Câu hỏi nghiên cứu

X5 đo được: đổi model → recall đổi (26.2 → 45.2 → 54.8). Vế còn lại chưa cô lập.

Quan sát dẫn tới giả thuyết: `agent.py` cho precision cao hơn Claude Code ở cùng
hạng model (61.1% / 53.8% vs 52.4%). Giải thích đề xuất: `validate_report` ép mỗi
finding phải trỏ vào file có thật, dòng có thật, evidence khớp **nguyên văn** — nên
finding bịa bị đội ngược trước khi ra khỏi vòng lặp.

**Nhưng đó mới là câu chuyện kể xuôi.** Precision cao có thể đến từ chỗ khác:
prompt, schema description, `max_steps`, hay đơn giản là model. X6 tắt đúng một
thứ và đo.

## 2. Biến duy nhất được đổi

`AUDITOR_NO_VALIDATOR=1` → `validate_report()` trả `""` cho mọi đầu vào.
Cổng biến mất ở **cả hai** call site (vòng lặp chính và cú chốt `mode='ANY'`) vì
guard đặt tại chính hàm, không tại nơi gọi.

**Hash `agent.py` giống hệt nhau ở cả hai arm** — arm chỉ khác một biến môi trường,
và `run_manifest.json` ghi thẳng `validator_enabled` để run tự mô tả được chính nó.

Giữ nguyên tuyệt đối: `MODEL`, `MAX_STEPS=10`, `SYSTEM_PROMPT`, 3 tool,
`SUBMIT_SCHEMA`, `MAX_REJECTIONS`, cú chốt `mode='ANY'`, 13 mục checklist, snapshot,
gold, `score_benchmark.py`, tolerance ±5, clean-majority differential.

### Kiểm chứng offline trước khi tiêu một xu nào

`test_validator.py` chạy hai chiều:

| Env | Kết quả |
|---|---|
| mặc định | **6/6 PASS** — cổng còn nguyên |
| `AUDITOR_NO_VALIDATOR=1` | **1/6** — 5 ca vi phạm lọt hết; ca duy nhất còn PASS là "báo cáo sạch", đúng như phải thế |

Công tắc là thật, không phải no-op. Đây là điều kiện tiên quyết: một ablation không
thực sự tắt thứ nó tuyên bố tắt thì mọi số sau đó là rác.

## 3. Thiết kế

| Arm | Env | Vai trò |
|---|---|---|
| **X6-on** | (mặc định) | control |
| **X6-off** | `AUDITOR_NO_VALIDATOR=1` | treatment |

3 clean + 3 spiked mỗi arm, xen kẽ — giống baseline-v01 và X5.

**Control được chạy lại, KHÔNG tái dùng số của X5-flash.** Hai lý do: (a) code đã
đổi nên hash khác, so với số cũ là so hai binary khác nhau; (b) chạy lại cho biết
biến thiên giữa các lần chạy, thứ mà so với số cũ không cho biết. Giá của sự chặt
chẽ này là ~$1.6 — rẻ hơn nhiều so với một kết luận không phòng thủ được.

**Clean consensus phải tính RIÊNG cho từng arm.** Khi tắt cổng, sàn nhiễu trên bản
sạch cũng đổi. Lấy consensus của arm này trừ cho arm kia là trừ nhầm sàn.

### Vì sao chọn `gemini-2.5-flash`

`flash` có precision **cao nhất trong cả bốn arm đã đo** (61.1%). Nó có nhiều
precision để mất nhất → hiệu ứng dễ thấy nhất nếu có. Và nó rẻ hơn `pro` 6×.

Nếu ablation **không** làm precision tụt ngay cả ở arm nhiều-để-mất-nhất, kết luận
"cổng tạo ra precision" yếu đi rõ rệt.

## 4. Giả thuyết đăng ký trước

| ID | Giả thuyết | Sai khi nào |
|---|---|---|
| **H1** | Hướng: precision(off) < precision(on) | precision(off) ≥ precision(on) |
| **H2** | **Độ lớn: tụt ≥ 10 điểm** → "harness → precision" thành **đo được** | tụt < 10 điểm |
| **H3** | **Tụt < 5 điểm → claim BỊ BÁC.** Precision đến từ chỗ khác (prompt/schema/model) | tụt ≥ 5 điểm |
| **H4** | recall(off) ≈ recall(on) trong ±7 điểm — cổng giúp **BÁO ĐÚNG**, không giúp **TÌM** | recall lệch > 7 điểm |
| **H5** | Tỉ lệ finding bịa > 0 ở arm off; **= 0 ở arm on theo cấu trúc** | arm off không có finding bịa nào |

Vùng xám 5–10 điểm cố ý để trống: rơi vào đó thì kết luận là **cổng đóng góp một
phần, không phải nguyên nhân chính**, và phải báo cáo đúng như vậy.

H4 quan trọng: nếu recall cũng tụt mạnh thì cổng đang làm nhiều hơn tôi nghĩ (ép
đọc file → đọc file làm agent tìm ra nhiều hơn), và câu "model→recall, harness→
precision" phải sửa lại chứ không được giữ nguyên.

## 5. Hai phép đo phụ, không tốn thêm tiền

**(a) Rule nào gánh việc.** Arm control in `[VALIDATOR] doi nguoc: <rule>` mỗi lần
từ chối. Đếm theo rule trong log là có ngay phân rã "check nào đóng góp nhiều nhất"
mà không cần thêm arm nào.

**(b) Tỉ lệ bịa, đo cơ học, KHÔNG phụ thuộc gold.** Chạy `validate_report` **offline**
trên findings của arm off, đếm số finding bị nó từ chối. Đây là con số không cần
gold, không cần scorer, không cần diễn giải: *bao nhiêu phần trăm finding trỏ vào
thứ không tồn tại.* Tái dùng đúng hàm đang bị ablate, không viết logic mới.

## 6. Ngân sách

`flash` đo được $0.26/lượt audit ở X5 → 6 trial × 2 arm ≈ **$3.12**.

**Trần cứng: $8.** Chạm trần thì dừng và báo cáo phần đã chạy.

Lưu ý: arm off có thể **rẻ hơn** arm on (không có vòng đội ngược → ít step hơn). Nếu
arm off **đắt hơn** đáng kể thì có gì đó sai, phải mở log xem trước khi chấm.

## 7. Phân loại lỗi khi chạy (giữ nguyên luật X4/X5)

- `max_steps` cạn / validator từ chối hết lượt → **dữ liệu**, tính miss.
- HTTP 429 / 503 / lỗi hạ tầng → **không phải dữ liệu**. Xoá và chạy lại.

## 8. Luật quyết định

| Kết quả | Kết luận | Việc tiếp theo |
|---|---|---|
| tụt ≥ 10 điểm | **"Harness → precision" thành đo được.** Phần tự viết tạo ra chất lượng. | Sửa STATUS.md + results-x5: bỏ chữ "suy luận". P3 đóng. |
| 5–10 điểm | Cổng đóng góp **một phần**. | Báo cáo vùng xám. Dùng phép đo phụ (a) xem rule nào gánh. |
| < 5 điểm | **Claim bị bác.** | **Sửa STATUS.md và results-x5 để rút claim.** Precision đến từ prompt/schema/model — phải nói thế. |
| precision **tăng** khi tắt cổng | Cổng đang từ chối oan finding đúng. | Kiểm log từ chối, đọc tay vài ca. Đây sẽ là phát hiện thú vị nhất. |

Dòng cuối là dòng phải chuẩn bị tinh thần nhất. Cổng có `MAX_REJECTIONS=2`; một
finding đúng nhưng evidence lệch khoảng trắng vẫn bị chặn. Không loại trừ trước.

## 9. Giới hạn

Ablation **toàn phần**, không tách từng check. Nếu hiệu ứng lớn, phân rã "check nào
gánh" đến từ phép đo phụ (a) — là quan sát từ log, **không phải arm có kiểm soát**.
Muốn chặt thì cần 4 arm; chưa đáng tiền ở giai đoạn này.

Vẫn là 15 seed, 1 repo, seed do chính tác giả viết, 3 trial/arm — đủ thấy hướng,
không đủ cho khoảng tin cậy chặt.

## 10. Đầu ra

`benchmark/results-x6-validator-ablation.md` — bảng on/off theo precision, FDR,
recall, F1, chi phí, số step; kèm bảng đếm rule và tỉ lệ bịa.
