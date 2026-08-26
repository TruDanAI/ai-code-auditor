# X6 — Ablation `validate_report`

**Ngày chạy:** 21/08/2026 · **Protocol:** `protocol-x6-validator-ablation.md`
(commit `8792ae4`, **01:08:23 — trước trial đầu tiên**; arm ON khởi động 01:09:12)

Cùng model `gemini-2.5-flash`, cùng 15 seed, cùng gold, cùng snapshot, tolerance
±5, clean-majority differential **tính riêng từng arm**. Raw trials và historical
`score.json` được giữ nguyên; bảng metric được tái chấm bằng scorer hiện tại sau các
amendment baseline 22–23/08.

Biến duy nhất: `AUDITOR_NO_VALIDATOR`. Hash `agent.py` giống hệt hai arm;
`run_manifest.json` ghi `validator_enabled` (`true` / `false`).

## Kết quả

| Metric | ON (control) | OFF (ablation) | Δ |
|---|---|---|---|
| In-scope recall | 47.6% [42.9–50.0] | 42.9% [35.7–50.0] | −4,8 |
| **In-scope precision** | **49.6%** [38.9–70.0] | **42.1%** [24.0–55.6] | **−7,6** |
| In-scope FDR | 50.4% | 57.9% | +7,6 |
| F1 | 47.8% | 40.8% | −7,0 |
| $/lượt audit | $0.2841 | $0.2605 | −8% |
| **Tỉ lệ finding bịa (H5)** | **0.0%** (0/145) | **5.2%** (4/77) | **+5,2** |

## Phán quyết giả thuyết

| ID | Giả thuyết | Kết quả |
|---|---|---|
| **H1** | Hướng: precision(off) < precision(on) | ✅ 49.6 → 42.1 |
| **H2** | Tụt ≥ 10 điểm → claim thành **đo được** | ✗ **7,6 điểm — KHÔNG kích hoạt** |
| **H3** | Tụt < 5 điểm → claim **bị bác** | ✗ không kích hoạt |
| **H4** | recall lệch trong ±7 điểm | ✅ 4,8 điểm |
| **H5** | Bịa > 0 ở off, = 0 ở on | ✅ **5.2% vs 0.0%** |

Rơi đúng **vùng xám 5–10 điểm** đã chừa sẵn trong protocol. Luật quyết định đăng ký
trước cho ô này: *"Cổng đóng góp **một phần**, không phải nguyên nhân chính."*

## Và một điều nghiêm trọng hơn phán quyết trên

Arm control được **chạy lại** thay vì tái dùng số X5-flash. Hai lần chạy của **cùng
một hành vi code**:

| | X5-flash (20/08) | X6-on (21/08) | Δ |
|---|---|---|---|
| recall | 45.2% | 47.6% | +2,4 |
| **precision** | **59.3%** | **49.6%** | **−9,6** |

**Chênh repeated-control quan sát = 9,6 điểm. Effect ablation = 7,6 điểm.**

→ **Effect NHỎ HƠN dao động đã quan sát. Không được tuyên bố precision improvement.**

Ngưỡng H2 (≥10 điểm) được đăng ký khi chưa có repeated control; quan sát sau này cho
thấy nó gần chênh 9,6 điểm. **Đó là lỗi thiết kế trong protocol này.** Ngưỡng **không được
sửa sau khi thấy dữ liệu**; nó được giữ nguyên và giới hạn được ghi ở đây.

Nếu đã tiết kiệm $1,7 bằng cách lấy X5-flash làm control, arm OFF sẽ bị so với 59,3%
— rìa trên của phân bố — và **một hiệu ứng 17,2 điểm phần lớn là ảo** sẽ được báo cáo.
Arm control tự nó bắt được lỗi trong thí nghiệm chứa nó.

## H5 — phép đo duy nhất sạch nhiễu

Không dùng gold hay scorer. `reproduce_auditor_claims.py --claim x6-citations` tái tạo
offline invariant file/line/evidence của validator trên findings của cả hai arm, mỗi
finding một lần, đối chiếu đúng snapshot:

| Arm | Finding bịa | Lý do |
|---|---|---|
| ON | **0 / 145 (0.0%)** | — (bằng 0 theo cấu trúc) |
| OFF | **4 / 77 (5.2%)** | 4/4 là `evidence KHÔNG khớp nội dung thật của dòng` |

Đây là kết quả **cơ học** trên raw output đã quan sát: bao nhiêu phần trăm finding
trích dẫn thứ không tồn tại. Nó không là claim universal cho mọi terminal exit: sau hai
lần forced submit bị từ chối, `agent.py` vẫn trả JSON kèm warning để tránh deadlock.

## Cổng thật sự nổ bao nhiêu lần?

Đếm trong log arm ON, **78 lượt audit**:

| Sự kiện | Số lần |
|---|---|
| `[VALIDATOR] đội ngược` | 5 |
| chặn "chưa read_file" | 2 |
| **Tổng can thiệp** | **7 / 78 ≈ 9%** |

Một cái cổng chỉ nổ 9% số lượt **không thể** là động lực chính của một metric tổng
hợp. Con số này giải thích vì sao hiệu ứng nhỏ, và nó nhất quán với H2 không kích hoạt.

## Trần của cổng, minh hoạ bằng số

`x6-on/clean-trial-03` nộp **75 finding**, trong đó **70 cái cùng category `auth`
trong đúng một file** `core/admin-routes.js`, 70 dòng khác nhau — **trên snapshot SẠCH**.

Cả 70 cái **qua validator**, vì mỗi dòng có thật và evidence khớp nguyên văn.

Đây chính là giới hạn đã ghi trong docstring của hàm, giờ có số minh hoạ:

> Chỉ kiểm được **HÌNH THỨC**. Bệnh **NGỮ NGHĨA** (finding rác) trị bằng schema
> description + benchmark.

Cổng kiểm được **trích dẫn có thật** trên normal accepted submissions. Nó không bảo đảm
**finding có nghĩa**, và fallback terminal nói trên không phải đảm bảo fail-closed.

Ghi nhận thêm: cơn "xả" 70 finding này nằm ở **một** trial clean nên phần lớn không
đạt đa số 2/3, và clean-majority differential hấp thụ được nó. Thiết kế differential
chịu được nhiễu loại này — một điểm cộng ngoài dự kiến.

## Đính chính claim của chính dự án

`STATUS.md` và `results-x5` ghi *"model → recall; harness → precision"*, tự nhận vế
sau là suy luận. X6 cho thấy vế sau **trộn hai claim khác nhau**:

| Claim | Trạng thái sau X6 |
|---|---|
| Validator đẩy **metric precision** lên | ❌ **Không chứng minh được ở n=3.** Hiệu ứng 7,6 < nhiễu 9,6 |
| Raw output X6 ON có citation bịa | ✅ **Đo được, cơ học.** 5.2% → 0.0% |

Đây là hai điều khác nhau và trước X6 chúng bị gộp làm một. Cách nói đúng từ đây:

> Trong X6, `validate_report` loại citation bịa khỏi raw output ON đã quan sát, không
> phải máy nâng precision. Nó kiểm một *lớp lỗi* (citation), chứ không cải thiện
> *phán đoán*; terminal fallback vẫn có thể xuất JSON lỗi kèm warning.

Vế này yếu hơn vế cũ về mặt marketing, nhưng nó **đúng** — và nó là vế phòng thủ được
trước hội đồng, vì có số cho cả hai chiều.

## Sự cố khi chạy

Arm OFF lần 1 bị **giết từ bên ngoài** lúc 03:39 (log cắt giữa lệnh `print`, không
traceback, runner không có exit code 4 nào cố ý). Theo §7: **hạ tầng ≠ dữ liệu** →
2 trial dở được **đổi tên giữ lại** (`x6-off-aborted-01`, $0.2950), **không** đưa vào
chấm, và arm OFF chạy lại từ đầu.

## Ngân sách

| | |
|---|---|
| arm ON (6 trial) | $1.7046 |
| arm OFF hỏng (2 trial, không chấm) | $0.2950 |
| arm OFF chạy lại (6 trial) | $1.5633 |
| **Tổng** | **$3.5629** / trần đăng ký trước **$8.00** |

## Giới hạn

n=3 trial mỗi arm. Một chênh repeated-control 9,6 điểm **lớn hơn** effect 7,6 điểm,
nên thí nghiệm này **thiếu lực thống kê** cho câu hỏi precision. Một cặp control chưa
ước lượng được variance hoặc noise floor vững; phải lặp control trước, rồi mới tính n
và đăng ký ablation tiếp theo.

Ablation **toàn phần**. Phân rã "check nào gánh" đến từ đếm log (5 đội ngược + 2 chặn
read_file), là **quan sát**, không phải arm có kiểm soát.

## Việc tiếp theo (chưa chạy, phải đăng ký trước)

- **X6b** — lặp control để ước lượng variance, sau đó power và đăng ký n cho ablation
  precision. Đây là thí nghiệm tiếp theo nếu vẫn muốn giữ claim precision.
- **Arm D** — Claude Code thả hết xích.
