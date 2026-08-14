# Scoring Rules — Seeded-Bug Benchmark (chốt TRƯỚC khi chạy auditor)

> **Protocol integrity note — 18/07/2026.** File này được đưa vào Git sau khi
> 7/15 mutation đã được cấy, nhưng **trước lần chạy auditor benchmark đầu tiên**.
> Vì vậy đây không phải full pre-registration trước mọi mutation. Tên trung thực:
> **protocol v0.1 freeze after 7/15 mutations, before outcome observation**.
> Không sửa luật sau khi thấy số. Nếu phát hiện luật sai, thêm một mục
> "Amendment" có ngày + lý do + ảnh hưởng dự kiến, không sửa lặng lẽ.

## Nguồn sự thật
- Repo đích: `chatbot-fanpage-spiked`, branch `spiked`, base = tag `benchmark-base` (c0fa0d6).
- Đáp án: `benchmark/golden_findings.json` (nằm ở **ai-code-auditor**, KHÔNG trong fork
  — auditor grep/read_file toàn cây repo đích nên đáp án để trong đó = data leakage).
- Mỗi lỗi cấy = 1 commit riêng trên `spiked`. `git diff benchmark-base..spiked` = đáp án
  tự sinh, file+line verify được bằng máy (không chép tay).

## 3 rổ phân loại mỗi finding auditor báo
1. **TP (Targeted True Positive)** — khớp 1 lỗi trong `golden_findings.json`. Vào công thức.
2. **FP (False Positive)** — báo lỗi ở chỗ code bình thường / hiểu sai logic / fixture test.
   Vào công thức (mẫu số FP).
3. **OOS (Out of Scope)** — lỗi bảo mật THẬT nhưng của repo gốc, không nằm trong tập cấy.
   Ghi nhận riêng, **loại khỏi** công thức TP/FP/Recall.

## Luật khớp TP (cả 3 điều kiện, AND — tinh thần `path AND keyword` Ngày 9)
Một finding = TP khi khớp một record gold thỏa **cả ba**:
1. **Đúng file** — `finding.file` == `gold.file` (so path chuẩn hoá, phân biệt hoa/thường theo repo).
2. **Đúng vị trí** — `|finding.line − gold.line| ≤ 5` (đệm lệch đếm dòng; KHÔNG cho "trúng file là ăn").
3. **Đúng bệnh** — `finding.category` cùng nhóm khung checklist với `gold.category`.
   Báo đúng dòng nhưng chẩn nhầm bệnh (vd chỗ IV-reuse mà báo "hardcode secret") = **KHÔNG** TP.

Mỗi gold record chỉ được khớp bởi **1** finding (finding gần line nhất). Nhiều finding cùng
trỏ 1 gold → 1 TP + phần dư tính FP (báo trùng cũng là nhiễu).

## Luật lên OOS (chống "rổ OOS = bãi rác giấu FP")
Mặc định mọi finding không khớp gold = **FP**. Muốn thăng lên OOS **phải qua cùng cửa
bằng chứng như auditor**: đọc code tại citation, giải thích được cơ chế gây hại thật.
Không verify được cơ chế = ở lại rổ FP. (Trách nhiệm chứng minh thuộc finding, không thuộc người chấm.)

## Caveat đã biết trước (phát hiện khi soát repo 17/7)
- **Fixture test = FP, KHÔNG phải OOS.** `tests/` chứa `EAAB-secret-page-token`,
  `password=secret` (dữ liệu test cho redaction). Auditor không mù `tests/` (quyết định Ngày 15)
  nên có thể báo chúng là "secret hardcode" → tính **FP** (không phải secret thật, không phải lỗi cấy).
- **1 đột biến = 1 lỗi cấy = 1 category.** Không đếm 1 dòng hỏng thành 2 lỗi (giữ mẫu số `TP+FN` sạch).
- **Mỗi mutation phải có "validity check".** Cấy lỗi xong PHẢI xác nhận: (a) không lỗi cú pháp, repo vẫn
  `node -c`/khởi động được; (b) tạo ĐÚNG bệnh trong gold, KHÔNG tạo lỗi ngoài ý (vd crash thay vì
  weak-crypto). Test vỡ vì mutation đảo 1 security-assertion = chấp nhận; test vỡ vì mutation làm CRASH
  luồng không liên quan = mutation SAI, phải làm lại. (Bài học 17/7: sha256→md5 làm aes-256-gcm throw
  "Invalid key length" = crash, không phải KDF yếu → mutation vô giá trị.)

## Phân loại OOS bằng DIFFERENTIAL (không chấm tay hậu kỳ)
Chạy CÙNG auditor (cùng model+prompt+tool+budget+temperature+giới hạn) trên **2 snapshot**:
- `clean` = tag `benchmark-base` (c0fa0d6), **0 lỗi cấy**.
- `spiked` = trạng thái có đủ 15 mutations.

Differential chỉ giúp xác định **nguồn gốc** finding (có sẵn ở clean hay do mutation đẻ ra),
KHÔNG tự động phán đúng/sai — vẫn phải verify code tại citation. Bảng phân loại đúng:

| Kết quả differential | Phân loại |
|---|---|
| Có ở clean **và** spiked, verify = **lỗi thật** | **OOS** (lỗi gốc thật, ngoài tập cấy) |
| Có ở clean **và** spiked, verify = **hiểu sai code** (vd báo `SENSITIVE_KEY_PATTERN` = secret) | **Baseline FP** |
| **Chỉ** ở spiked, khớp golden | **TP** |
| **Chỉ** ở spiked, không khớp + verify không phải lỗi thật | **FP** |
| **Chỉ** ở spiked, verify = lỗi phụ THẬT do mutation đẻ ra | **Mutation side-effect** → xem lại seed (mutation bẩn) |

⚠️ SAI thường gặp: gộp "mọi finding chung clean+spiked = OOS". Một regex phòng thủ bị hiểu nhầm là secret,
xuất hiện ở cả 2 snapshot, VẪN là **baseline FP** — KHÔNG phải OOS. OOS chỉ dành cho lỗi bảo mật THẬT của repo gốc.
Vì LLM phi tất định: chạy **≥3 lượt/snapshot**, báo **trung bình + khoảng dao động**.

### Khóa cách gộp differential trước lần chạy đầu (18/07/2026)

- Chuẩn hóa một finding để so giữa trial bằng **file + category + line ±5**.
- Một finding chỉ được coi là **baseline ổn định** khi xuất hiện trong **đa số tuyệt
  đối clean trials** (3 trial → ít nhất 2). Baseline ổn định được loại khỏi seeded
  delta score và báo count riêng.
- Finding chỉ lóe lên ở 1 clean trial KHÔNG đủ để che một spiked FP. Nếu nó xuất
  hiện ở spiked nhưng không khớp gold/baseline-majority → vẫn là FP.
- `baseline` chỉ nói finding đã có ở repo clean; muốn gọi nó là lỗ hổng thật/OOS
  về ngữ nghĩa vẫn phải review evidence riêng. Báo `baseline_excluded` và
  `verified OOS` thành hai con số, không đánh tráo.
- Mỗi spiked trial được chấm **riêng**, sau đó mới báo mean + min–max. Không union
  findings từ nhiều trial thành một “super run”.

## Snapshot giao cho auditor (chống leakage đáp án qua Git)
Auditor KHÔNG được thấy lịch sử cấy lỗi. Sau khi cấy xong, xuất snapshot **không có `.git`**:
`git archive spiked | tar -x -C <thư mục audit>` (hoặc copy rồi xoá `.git`). Snapshot đưa auditor:
không `.git`, không branch/tag, không golden set, không benchmark script — chỉ trạng thái source cuối.
*(Auditor hiện chỉ có `grep`+`read_file`, chưa đọc được Git; đây là phòng thủ chiều sâu, bắt buộc-đúng bất kể tool.)*

## Công thức (Ngày 25) — tách in-scope vs coverage
14 lỗi nằm trong khung checklist + 1 lỗi (OOC-01) CỐ Ý ngoài checklist → tách 2 chỉ số để không lẫn
*checklist-gap* với *agent-miss*:
- **In-scope Recall** = TP_in / (TP_in + FN_in),  mẫu số = **14** (các lỗi checklist CÓ phủ).
- **End-to-end Coverage** = TP_all / **15** (gồm cả OOC-01).
- OOC-01 phân loại riêng `expected_outcome: checklist-gap`. Nếu Ngày sau thêm mục ReDoS vào checklist rồi
  chạy lại → đo **Recall trước/sau + chênh token** = bằng chứng ĐỊNH LƯỢNG cho phép tách 2 bệnh.
- Bộ số chính dùng cùng scope 14 seed: **In-scope Precision** = TP_in / (TP_in + FP);
  **In-scope FDR** = FP / (TP_in + FP) = 1 − Precision; **In-scope F1** =
  2·P·R / (P + R), trong đó `R` = In-scope Recall.
- OOC-01 không được dùng để làm đẹp Precision/F1 chính. Nếu bắt được nó, chỉ tăng
  **End-to-end Coverage X/15**; báo thêm all-seeded precision như số phụ nếu cần.
  ⚠️ Gọi đúng tên **FDR**, KHÔNG gọi "False Positive Rate" — FPR chuẩn = FP/(FP+TN) cần true-negative,
  mà benchmark finding-level không định nghĩa được TN.
- Báo kèm: OOS count (ngoài công thức), $/audit, latency, số lượt chạy + dao động.

## Câu CV mẫu (định dạng chốt)
> "Auditor phát hiện X/14 lỗi cấy in-scope (Recall Y%), FDR Z% (F1 = 0.NN, trung bình 3 lượt),
>  citation từng finding; +1 lỗi ngoài checklist bắt được sau khi bổ mục (chứng minh checklist-gap);
>  bóc thêm K lỗi thật ngoài lề (OOS) từ repo gốc qua differential clean-vs-spiked."
