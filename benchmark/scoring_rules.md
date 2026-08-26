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

### Amendment 22/08/2026 — thêm `evidence` vào khoá so khớp baseline

Bản khoá 18/07/2026 giả định **số dòng so sánh được giữa clean và spiked**. Giả định
này SAI với mutation kiểu **chèn dòng**: mọi dòng bên dưới bị đẩy xuống, nên cùng một
số dòng ở hai snapshot có thể trỏ vào hai đoạn code khác hẳn nhau.

Ca thật đã bắt được (`SEED-DEP-01`, arm x5-pro):

| snapshot | `package.json:23` | auditor báo |
|---|---|---|
| clean | `"multer": "^2.1.1"` | dependency-confusion (2/3 clean trial → baseline ổn định) |
| spiked | `"lodash": "4.17.15"` | chính lỗi cấy — multer bị đẩy xuống dòng 24 |

Cùng file, cùng category thô `dependency`, khoảng cách dòng **0** → khoá cũ coi là một
finding và loại mất một phát hiện thật.

**Sửa (đã áp dụng):**
1. Khoá so `baseline ↔ spiked` = `file + category + line±5` **+ `evidence` đã chuẩn hoá**
   (gộp khoảng trắng, lowercase). Thiếu `evidence` một bên → rơi về so vị trí, tức
   **thiên về loại bỏ, không thiên về cho điểm**.
2. Dựng clean consensus **giữ nguyên** khoá cũ (`file + category + line±5`), vì trong
   cùng snapshot clean số dòng vốn đã so sánh được.
3. Thứ tự phân loại trong `score_trial` sửa lại cho đúng bảng ở trên: **loại baseline
   ổn định TRƯỚC**, rồi mới xét gold. Trước amendment code xét gold trước, nên một
   finding vừa khớp gold vừa thuộc clean-majority bị chấm TP — trái `TP = chỉ ở spiked`.

**Ảnh hưởng lên số đã công bố** (chấm lại offline, không chạy trial mới, raw trials giữ
nguyên; kết quả hiệu chỉnh ở `runs/<arm>/score-corrected-20260822.json`, `score.json` cũ
không xoá):

| | recall in-scope | coverage | precision in-scope |
|---|---|---|---|
| baseline-v01 | 26,2% (không đổi) | không đổi | 24,6% (không đổi) |
| x5-flash | 45,2% (không đổi) | không đổi | 61,1% → **59,3%** |
| x5-pro | 54,8% (không đổi) | không đổi | 53,8% → **50,1%** |
| x6-on | 47,6% (không đổi) | không đổi | 50,4% → **49,6%** |
| x6-off | 42,9% (không đổi) | không đổi | 43,6% → **42,1%** |

Recall và coverage **không đổi ở mọi arm**; chỉ precision/FDR/F1 giảm nhẹ (0,8–2,8 pp)
vì một số finding trước đây bị gộp nhầm vào baseline nay lộ ra là FP riêng. Hướng của
cả hai kết luận vẫn giữ: thang model (pro > flash > baseline theo recall) và validator
ON > OFF (recall +4,8 pp, precision +7,6 pp theo scorer hiện tại).

⚠️ Con số 54,8% của x5-pro **trùng nhau trước và sau khi sửa** — KHÔNG được đọc thành
"vậy là chẳng có gì sai". Có hai lỗi ngược chiều triệt tiêu nhau: thứ tự xét sai làm
số cao lên, khoá so va chạm làm số thấp xuống. Sửa cả hai thì số mới bền.

Regression test khoá ca này: `test_score_benchmark.py::BaselineBeforeGoldTests`.

### Amendment 23/08/2026 — một quan hệ đồng nhất duy nhất

Bản 22/08 để lại **bất đối xứng**: dựng consensus gom nhóm bằng khoá *lỏng*
(`file+category+line±5`) nhưng loại trừ lại kiểm bằng khoá *chặt* (thêm `evidence`).
Hệ quả: một cụm finding khác nhau nằm gần nhau bầu ra **một đại diện**, rồi chính các
thành viên còn lại của cụm bị đại diện đó từ chối.

Ca thật (arm `sast-deterministic`): ba finding `dependency` trên `package.json` dòng
16 / 18 / 23 gộp thành một đại diện dòng 18 (`"axios"`). Bốn advisory ở dòng 16 sau đó
**không khớp evidence của đại diện** → chấm FP oan, dù chúng có mặt ở **cả 3/3** clean
trial. Precision của arm này bị hạ từ 100% xuống 16,7% hoàn toàn do lỗi chấm.

**Sửa:** `build_clean_consensus` dùng đúng `same_finding` như lúc loại trừ. Một quan hệ
đồng nhất, dùng ở mọi nơi.

Ảnh hưởng: recall/coverage **không đổi ở mọi arm**; precision đổi nhẹ
(x5-pro 51,0% → **50,1%**, x6-off 42,4% → **42,1%**, các arm khác giữ nguyên).

Regression test: `test_score_benchmark.py::ConsensusClusterTests`.

**Giới hạn còn lại, ghi nhận chứ chưa sửa:** khoá so khớp ở mức *category*, không ở mức
*rule*. Nếu clean đã có một rule cùng category nổ trên đúng dòng đó, một rule MỚI ở
spiked sẽ bị che. Ca thật: `gcm-no-tag-length` nổ ở clean tại `page-credentials.js:53`,
nên `aead-no-final` (chính là hệ quả của SEED-CRY-01) ở spiked bị loại thành baseline.
Không thêm `rule_id` vào khoá vì finding của LLM không có rule_id — thêm vào sẽ tạo
bất đối xứng giữa các arm, đúng loại lỗi mà amendment này vừa xoá.

### Amendment 23/08/2026 — tái chấm toàn bộ số công bố bằng scorer hiện tại

Sau hai sửa khoá baseline ở trên, mọi metric công bố phải lấy từ **cùng scorer hiện
tại**, không lấy `score.json` lịch sử. Raw trials và `score.json` cũ được giữ nguyên;
đầu ra tái chấm là derived evidence, không phải trial mới. Lệnh tái tạo offline:

```powershell
python ..\docs\giao-trinh\checks\reproduce_auditor_claims.py --claim cv-metrics
```

| Arm | Recall | Precision | FDR | F1 |
|---|---:|---:|---:|---:|
| baseline-v01 | 26.2% | 24.6% | 75.4% | 24.2% |
| x5-flash | 45.2% | 59.3% | 40.7% | 50.8% |
| x5-pro | 54.8% | 50.1% | 49.9% | 51.5% |
| x6-on | 47.6% | 49.6% | 50.4% | 47.8% |
| x6-off | 42.9% | 42.1% | 57.9% | 40.8% |
| x4-commercial | 57.1% | 50.1% | 49.9% | 53.4% |

Derived from unrounded means: X6 precision ON−OFF = **7.6 pp**; the observed
repeated-control precision difference (x5-flash vs x6-on) = **9.6 pp**. One pair is
not a stable noise-floor estimate, but 7.6 below that observed difference is enough
to reject a strong precision-improvement interpretation at n=3.

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
