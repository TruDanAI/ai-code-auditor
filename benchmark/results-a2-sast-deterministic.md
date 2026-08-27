# A2 — Arm tất định: Semgrep + npm audit (23/08/2026)

Mốc so sánh mà mọi bài báo agentic-security đều có và dự án này trước đó thiếu.
Chạy **offline, $0, 0 lượt gọi LLM**, chấm bằng **đúng scorer** và đúng protocol
differential như các arm LLM.

Runner: `run_deterministic_arm.py` (commit `05ce5c4`, **trước** khi chấm — git chứng
minh được thứ tự, đúng bài học rút ra từ X4).

## Cấu hình đã khai báo trước

| | |
|---|---|
| SAST | `semgrep --config p/default` (bộ rule mặc định, thứ một team thật chạy) |
| SCA | `npm audit --package-lock-only` (không cài, khớp cách gold verify DEP-01) |
| Ánh xạ | CWE → category, cố định trong code, không tinh chỉnh theo điểm |
| Trial | 3 bản sao giống hệt — công cụ tất định, **phương sai = 0 theo thiết kế** |

`p/security-audit` cũng đã chạy: **0 finding trên cả hai snapshot**. Báo ra, không
lặng lẽ bỏ.

## Kết quả

| | Semgrep + npm audit | x5-pro (LLM) |
|---|---|---|
| recall in-scope | **7,1%** (1/14) | 54,8% |
| KTC 95% recall | 0,0% – 21,4% | 31,0% – 78,6% |
| precision in-scope | **100,0%** (1 TP / 0 FP) | 50,1% |
| F1 | 13,3% | 51,5% |
| finding thô (spiked) | 39 | ~15–22 |
| bị trừ làm nền | 38 | 2–5 |
| chi phí | **$0** | ~$1,2 |

Seed duy nhất bắt được: **`SEED-DEP-01`** (lodash 4.17.15), và bắt bằng nhánh **SCA**
chứ không phải SAST. Semgrep đóng góp **0** phát hiện sau khi trừ nền.

⚠️ **"Precision 100%" ở đây nghĩa là "nộp đúng một finding và nó đúng"**, không phải
"hoàn hảo". Mẫu số bằng 1. Đừng trích câu này rời khỏi ngữ cảnh.

## Điều arm này chứng minh về chính bộ đo

1. **Phương sai bằng 0.** min = max = mean ở cả 6 chỉ số. Nếu scorer bịa ra dao động
   cho một công cụ tất định thì đó là bug — nó không bịa.
2. **Differential thật sự làm việc.** 38/39 finding bị trừ làm nền. Nếu chấm theo
   kiểu "đếm finding trên snapshot có lỗi" như phần lớn benchmark, arm này sẽ trông
   như tìm được 39 vấn đề. Con số thật là **1**.
3. **Nó bắt được một bug của scorer.** Xem `scoring_rules.md`, amendment 23/08 — arm
   này phơi ra lỗi bất đối xứng consensus/exclusion mà 5 arm LLM đều giấu được.

## Kết luận rút được (và không rút được)

Theo bootstrap có cặp, KTC 95% tách khỏi 0:

- **LLM agent > SAST+SCA tất định về recall**, ở mọi arm LLM: +35,4 đến +47,8 điểm.
  Đây là kết luận **mạnh nhất** của cả dự án tính đến nay.
- Đổi lại: agent nộp nhiều FP hơn hẳn. 100% vs 50,1% precision.

Không rút được: mọi so sánh **giữa các arm LLM với nhau** (thang model, ablation
validator) đều có KTC chứa 0 ở n=14 seed. Xem `docs/analysis-bootstrap-20260823.md`.
