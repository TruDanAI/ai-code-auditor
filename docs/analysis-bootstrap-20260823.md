# Bootstrap CI + ma tran seed (A1 + A3)
Resample **1000**, RNG seed `20260823`, percentile 2.5/97.5. Khong goi LLM, khong cham lai - chi doc `score-corrected-*.json`.

## A1a. Recall in-scope, bootstrap phan tang (seed + trial)
Don vi resample **chinh** la seed: "neu chon 14 seed khac thi so ra bao nhieu".

| arm | diem | KTC 95% | be rong |
|---|---|---|---|
| baseline-v01 | 26.2% | 9.5% – 45.2% | 35.7 diem |
| x5-flash | 45.2% | 21.4% – 69.0% | 47.6 diem |
| x5-pro | 54.8% | 31.0% – 78.6% | 47.6 diem |
| x6-on | 47.6% | 23.8% – 71.4% | 47.6 diem |
| x6-off | 42.9% | 21.4% – 66.7% | 45.2 diem |
| sast-deterministic | 7.1% | 0.0% – 21.4% | 21.4 diem |

## A1b. Precision in-scope, cluster bootstrap tren trial (n=3)
⚠️ n=3 - khoang nay rong den muc gan nhu khong rang buoc gi. Bao ra de thay ro dieu do.

| arm | diem | KTC 95% |
|---|---|---|
| baseline-v01 | 24.6% | 12.5% – 36.4% |
| x5-flash | 59.3% | 50.0% – 77.8% |
| x5-pro | 50.1% | 34.8% – 61.5% |
| x6-on | 49.6% | 38.9% – 70.0% |
| x6-off | 42.1% | 24.0% – 55.6% |
| sast-deterministic | 100.0% | 100.0% – 100.0% |

## A1c. Hieu giua cac arm (recall), bootstrap **theo cap**
Cung mot lan rut seed dung cho ca hai arm -> loai bot nhieu chung.
**KTC chua 0 = khong tuyen bo duoc.**

| so sanh | hieu | KTC 95% | ket luan |
|---|---|---|---|
| baseline-v01 - x5-flash | -19.2 diem | -40.5 – +2.4 | **chua 0 → KHONG tuyen bo** |
| baseline-v01 - x5-pro | -29.2 diem | -52.4 – -7.1 | tach khoi 0 |
| baseline-v01 - x6-on | -21.6 diem | -42.9 – -2.4 | tach khoi 0 |
| baseline-v01 - x6-off | -16.8 diem | -35.7 – +2.4 | **chua 0 → KHONG tuyen bo** |
| baseline-v01 - sast-deterministic | +18.6 diem | -4.8 – +40.5 | **chua 0 → KHONG tuyen bo** |
| x5-flash - x5-pro | -9.9 diem | -28.6 – +2.4 | **chua 0 → KHONG tuyen bo** |
| x5-flash - x6-on | -2.4 diem | -16.7 – +9.5 | **chua 0 → KHONG tuyen bo** |
| x5-flash - x6-off | +2.4 diem | -7.1 – +14.3 | **chua 0 → KHONG tuyen bo** |
| x5-flash - sast-deterministic | +37.8 diem | +14.3 – +61.9 | tach khoi 0 |
| x5-pro - x6-on | +7.6 diem | -2.4 – +21.4 | **chua 0 → KHONG tuyen bo** |
| x5-pro - x6-off | +12.3 diem | -2.4 – +31.0 | **chua 0 → KHONG tuyen bo** |
| x5-pro - sast-deterministic | +47.8 diem | +23.8 – +71.4 | tach khoi 0 |
| x6-on - x6-off | +4.8 diem | -7.1 – +19.0 | **chua 0 → KHONG tuyen bo** |
| x6-on - sast-deterministic | +40.2 diem | +16.7 – +64.3 | tach khoi 0 |
| x6-off - sast-deterministic | +35.4 diem | +14.3 – +59.5 | tach khoi 0 |

## A3. Ma tran phat hien theo seed (so trial spiked bat duoc / tong)

| seed | baseline-v01 | x5-flash | x5-pro | x6-on | x6-off | sast-deterministic | tong |
|---|---|---|---|---|---|---|---|
| SEED-AUTH-01 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | **0** |
| SEED-AUTH-02 | 0/3 | 1/3 | 3/3 | 2/3 | 1/3 | 0/3 | **7** |
| SEED-CFG-01 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | **0** |
| SEED-CRY-01 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | **0** |
| SEED-CRY-02 | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | **13** |
| SEED-CRY-03 | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | **14** |
| SEED-DEP-01 | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | **16** |
| SEED-DOC-01 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | **1** |
| SEED-ERR-01 | 1/3 | 0/3 | 2/3 | 1/3 | 0/3 | 0/3 | **4** |
| SEED-INP-01 | 0/3 | 2/3 | 2/3 | 2/3 | 1/3 | 0/3 | **7** |
| SEED-INP-02 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | **0** |
| SEED-REL-01 | 0/3 | 1/3 | 1/3 | 0/3 | 1/3 | 0/3 | **3** |
| SEED-SEC-01 | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | **14** |
| SEED-SEC-02 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | **15** |

**Seed KHONG arm nao bat duoc (4/14):** `SEED-AUTH-01`, `SEED-CFG-01`, `SEED-CRY-01`, `SEED-INP-02`
